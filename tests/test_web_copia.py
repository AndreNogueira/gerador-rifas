"""A cópia de segurança semanal (`web/copia.py`, `web/s3_simples.py`): a assinatura SigV4, o agendamento sem duplicados, a rotação de 8 semanas, o restauro e a privacidade."""
import gzip
import json
import os
import urllib.error
from datetime import date, datetime, timezone

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from test_web_relatorio import INDEX, LEITURA, TOKEN, ts
from web import config, copia, s3_simples
from web.app import criar_app
from web.copia import EstadoCopia, ErroCopia
from web.relatorio import RelatoriosEnviados

ID, SEGREDO = "NEONKEYID1234567", "segredo-do-s3-muito-secreto-9876543210"
ENDPOINT = "https://c-7.eu-central-1.aws.neon.tech"
PG_FALSO = "postgresql://utilizador:palavra@servidor-falso.exemplo:5432/base"


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("ADMIN_TOKEN", "CLAUDE_TOKEN", "DATABASE_URL", "RESEND_API_KEY", "RELATORIO_EMAIL_PARA", "RELATORIO_FUSO") + tuple(f"BACKUP_S3_{n}" for n in ("ENDPOINT", "BUCKET", "REGION", "ACCESS_KEY_ID", "SECRET_ACCESS_KEY")):
        monkeypatch.delenv(nome, raising=False)


@pytest.fixture
def ligada(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", PG_FALSO)
    monkeypatch.setenv("BACKUP_S3_ENDPOINT", ENDPOINT)
    monkeypatch.setenv("BACKUP_S3_BUCKET", "rifas-backups")
    monkeypatch.setenv("BACKUP_S3_REGION", "eu-central-1")
    monkeypatch.setenv("BACKUP_S3_ACCESS_KEY_ID", ID)
    monkeypatch.setenv("BACKUP_S3_SECRET_ACCESS_KEY", SEGREDO)


DADOS = {"versao": 1, "criado": "2026-11-16T00:10:00+00:00", "tabelas": {
    "historico_diario": {"colunas": ["dia", "dados", "criado"], "linhas": [["2026-11-15", '{"sessoes":{"Sessões":9}}', 1800000000]]},
    "objetivos": {"colunas": ["chave", "meta"], "linhas": [["sessoes", 30.0]]}}}


# ------------------------------------------------------------------ a assinatura e o PUT
def test_a_assinatura_reproduz_o_exemplo_oficial_da_aws():
    c = s3_simples.assinar("GET", "examplebucket.s3.amazonaws.com", "/test.txt", "", {"range": "bytes=0-9"}, s3_simples.VAZIO_SHA256, "us-east-1",
                           "AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", datetime(2013, 5, 24, tzinfo=timezone.utc))
    assert c["authorization"] == ("AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20130524/us-east-1/s3/aws4_request, SignedHeaders=host;range;x-amz-content-sha256;x-amz-date, "
                                  "Signature=f0e8bdb87c964420e857bd35b5d6ed310bd44f0170aba48dd91039c6036bdb41")


class Resposta:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class Rede:
    def __init__(self, falhas=0, erro=None):
        self.pedidos, self.falhas = [], falhas
        self.erro = erro or urllib.error.HTTPError(ENDPOINT, 403, "proibido", {}, None)

    def __call__(self, pedido, timeout=0):
        self.pedidos.append(pedido)
        if self.falhas > 0:
            self.falhas -= 1
            raise self.erro
        return Resposta()


def test_o_put_vai_para_o_endereco_path_style_com_o_corpo_e_a_assinatura():
    rede = Rede()
    assert s3_simples.gravar(ENDPOINT, "eu-central-1", "rifas-backups", "backups/rifas-semana-7.json.gz", b"conteudo", ID, SEGREDO, "application/gzip",
                             datetime(2026, 11, 16, tzinfo=timezone.utc), rede) == 200
    p = rede.pedidos[0]
    assert p.get_method() == "PUT" and p.full_url == "https://c-7.eu-central-1.aws.neon.tech/rifas-backups/backups/rifas-semana-7.json.gz" and p.data == b"conteudo"
    cab = {k.lower(): v for k, v in p.header_items()}
    assert cab["authorization"].startswith(f"AWS4-HMAC-SHA256 Credential={ID}/20261116/eu-central-1/s3/aws4_request") and cab["content-type"] == "application/gzip"
    assert cab["x-amz-content-sha256"] == __import__("hashlib").sha256(b"conteudo").hexdigest() and SEGREDO not in json.dumps(cab)


def test_os_erros_do_s3_nao_levam_nem_a_chave_nem_o_segredo_nem_o_endereco():
    for erro, esperado in ((urllib.error.HTTPError(ENDPOINT, 403, "x", {}, None), "HTTP 403"), (urllib.error.URLError(f"{ENDPOINT} {SEGREDO} {ID}"), "URLError")):
        with pytest.raises(s3_simples.ErroS3) as e:
            s3_simples.gravar(ENDPOINT, "eu-central-1", "b", "k", b"x", ID, SEGREDO, abrir=Rede(1, erro))
        assert str(e.value) == esperado
    with pytest.raises(s3_simples.ErroS3):
        s3_simples.gravar("http://inseguro.exemplo", "r", "b", "k", b"x", ID, SEGREDO, abrir=Rede())                  # só https


# ------------------------------------------------------------------ a configuração e a cópia
def test_a_configuracao_exige_tudo_e_https(monkeypatch, ligada):
    assert config.backup_s3() == {"endpoint": ENDPOINT, "bucket": "rifas-backups", "regiao": "eu-central-1", "id": ID, "segredo": SEGREDO}
    monkeypatch.setenv("BACKUP_S3_ENDPOINT", ENDPOINT + "/")
    assert config.backup_s3()["endpoint"] == ENDPOINT                                                          # a barra final tira-se
    for nome, mau in (("ENDPOINT", "http://x.exemplo"), ("ENDPOINT", "https://x.exemplo/../y"), ("BUCKET", "../fora"), ("BUCKET", "A"), ("SECRET_ACCESS_KEY", ""), ("REGION", "")):
        monkeypatch.setenv(f"BACKUP_S3_{nome}", mau)
        assert config.backup_s3() is None, nome
        monkeypatch.undo()
        monkeypatch.setenv("DATABASE_URL", PG_FALSO)
        for n, v in (("ENDPOINT", ENDPOINT), ("BUCKET", "rifas-backups"), ("REGION", "eu-central-1"), ("ACCESS_KEY_ID", ID), ("SECRET_ACCESS_KEY", SEGREDO)):
            monkeypatch.setenv(f"BACKUP_S3_{n}", v)


def test_so_esta_ativa_com_destino_e_base_postgres(monkeypatch, ligada):
    assert copia.ativa() is True
    monkeypatch.delenv("DATABASE_URL")
    assert copia.ativa() is False                                                                              # sem Postgres não há nada a guardar à parte


def test_comprimir_e_descomprimir_e_formatos_estragados():
    assert copia.descomprimir(copia.comprimir(DADOS)) == DADOS
    assert copia.comprimir(DADOS) == copia.comprimir(DADOS)                                                    # determinística
    for mau in (gzip.compress(b"[1]"), gzip.compress(b'{"versao": 2, "tabelas": {}}'), gzip.compress(b'{"versao": 1, "tabelas": []}')):
        with pytest.raises(ErroCopia):
            copia.descomprimir(mau)


def test_as_8_posicoes_rodam_e_a_manual_nao_mexe_nelas():
    assert [copia.chave_do_objeto(date(2026, 1, 5) + __import__("datetime").timedelta(weeks=i)) for i in (0, 1)] == ["backups/rifas-semana-2.json.gz", "backups/rifas-semana-3.json.gz"]
    assert copia.chave_do_objeto(date(2026, 11, 16)) == "backups/rifas-semana-7.json.gz" and copia.chave_do_objeto(date(2026, 11, 16)) != copia.chave_do_objeto(date(2026, 11, 23))
    assert copia.chave_do_objeto(date(2026, 9, 21)) == copia.chave_do_objeto(date(2026, 11, 16))                  # 8 semanas depois: a mesma posição (a antiga é substituída)
    assert copia.chave_do_objeto(manual=True) == "backups/rifas-manual.json.gz"


# ------------------------------------------------------------------ o agendamento
@pytest.fixture
def exporta(monkeypatch):
    monkeypatch.setattr(copia, "exportar", lambda url, tabelas=copia.TABELAS: DADOS)


class Contador:
    def __init__(self, tabela):
        self.n = 0
        original = tabela._executar

        def contado(*a, **k):
            self.n += 1
            return original(*a, **k)
        tabela._executar = contado


def test_desligada_sem_configuracao(tmp_path):
    assert copia.fazer_se_devido(RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoCopia(), ts(2026, 11, 16, 1), Rede()) == "desligada"


def test_na_segunda_depois_das_zero_e_cinco_faz_uma_so_vez_e_nao_volta_a_consultar_a_base(tmp_path, ligada, exporta):
    r, est, rede = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoCopia(), Rede()
    assert copia.fazer_se_devido(r, est, ts(2026, 11, 16, 0, 2), rede) == "cedo" and rede.pedidos == []
    assert copia.fazer_se_devido(r, est, ts(2026, 11, 16, 0, 10), rede) == "feita" and len(rede.pedidos) == 1
    c = Contador(r)
    for h in range(1, 20):
        assert copia.fazer_se_devido(r, est, ts(2026, 11, 16, h), rede) == "tratada"
    assert c.n == 0 and len(rede.pedidos) == 1                                                                 # nada de consultas até à segunda seguinte
    p = rede.pedidos[0]
    assert p.full_url == "https://c-7.eu-central-1.aws.neon.tech/rifas-backups/backups/rifas-semana-7.json.gz"
    assert copia.descomprimir(p.data) == DADOS and r.ultimo("backup")["dia"] == "backup:2026-11-16" and r.ultimo("dia") is None and est.ultimo_tamanho == len(p.data)


def test_um_arranque_novo_pergunta_uma_vez_e_nao_repete(tmp_path, ligada, exporta):
    r, rede = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), Rede()
    copia.fazer_se_devido(r, EstadoCopia(), ts(2026, 11, 16, 1), rede)
    outro = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3")
    assert copia.fazer_se_devido(outro, EstadoCopia(), ts(2026, 11, 17, 9), rede) == "ja_feita" and len(rede.pedidos) == 1


def test_o_servico_que_dormiu_na_segunda_faz_a_cópia_quando_acorda(tmp_path, ligada, exporta):
    r, rede = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), Rede()
    assert copia.fazer_se_devido(r, EstadoCopia(), ts(2026, 11, 19, 9), rede) == "feita"                       # quinta-feira: a semana de 16 de novembro
    assert r.ultimo("backup")["dia"] == "backup:2026-11-16"


def test_a_semana_seguinte_faz_outra_numa_posicao_diferente(tmp_path, ligada, exporta):
    r, est, rede = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoCopia(), Rede()
    copia.fazer_se_devido(r, est, ts(2026, 11, 16, 1), rede)
    assert copia.fazer_se_devido(r, est, ts(2026, 11, 23, 1), rede) == "feita"
    assert [p.full_url.rsplit("/", 1)[1] for p in rede.pedidos] == ["rifas-semana-7.json.gz", "rifas-semana-0.json.gz"]


def test_uma_falha_desfaz_a_reserva_espera_uma_hora_e_repete_sem_vazar_nada(tmp_path, ligada, exporta, caplog):
    r, est = RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), EstadoCopia()
    rede = Rede(1, urllib.error.URLError(f"{ENDPOINT} {SEGREDO} {ID} {PG_FALSO}"))
    with caplog.at_level("DEBUG"):
        assert copia.fazer_se_devido(r, est, ts(2026, 11, 16, 1), rede) == "falhou" and r.ultimo("backup") is None
        assert est.ultimo_erro == "armazenamento: URLError"
        assert copia.fazer_se_devido(r, est, ts(2026, 11, 16, 1, 30), rede) == "espera" and len(rede.pedidos) == 1
        assert copia.fazer_se_devido(r, est, ts(2026, 11, 16, 2, 5), rede) == "feita" and est.ultimo_erro == ""
    visivel = caplog.text + est.ultimo_erro
    for segredo in (SEGREDO, ID, "palavra", "servidor-falso", "c-7.eu-central-1"):
        assert segredo not in visivel


def test_a_base_em_baixo_tambem_vira_um_erro_sem_o_endereco(tmp_path, ligada, monkeypatch):
    def avaria(*a, **k):
        raise RuntimeError(f"nao liga a {PG_FALSO}")
    monkeypatch.setattr(copia, "exportar", avaria)
    est = EstadoCopia()
    assert copia.fazer_se_devido(RelatoriosEnviados(caminho=tmp_path / "r.sqlite3"), est, ts(2026, 11, 16, 1), Rede()) == "falhou"
    assert est.ultimo_erro == "base: RuntimeError" and "palavra" not in est.ultimo_erro


# ------------------------------------------------------------------ o restauro (validação; a base a sério está no teste de Postgres)
def test_o_restauro_recusa_colunas_e_linhas_suspeitas_antes_de_tocar_na_base():
    for mau in ({"historico_diario": {"colunas": ["dia; DROP TABLE x"], "linhas": [["a"]]}}, {"objetivos": {"colunas": ["chave", "meta"], "linhas": [["so-uma"]]}},
                {"comentarios": {"colunas": ["Texto"], "linhas": []}}):
        with pytest.raises(ErroCopia):
            copia.restaurar("postgresql://nunca-se-liga.exemplo/x", {"versao": 1, "tabelas": mau})


# ------------------------------------------------------------------ o painel
@pytest.fixture
def admin(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    monkeypatch.setenv("CLAUDE_TOKEN", LEITURA)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(INDEX, encoding="utf-8")
    return TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados"), headers={"X-Lingua": "pt"})


def test_o_estado_diz_se_esta_ligada_sem_mostrar_credenciais(admin):
    assert admin.get("/api/admin/copia").status_code == 404
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    d = admin.get("/api/admin/copia").json()
    assert d["ativa"] is False and d["tem_s3"] is False and d["bucket"] == "" and d["ultimo"] is None and d["posicoes"] == 8 and "historico_diario" in d["tabelas"]


def test_ligada_mostra_o_bucket_e_nunca_as_credenciais(admin, ligada):
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    d = admin.get("/api/admin/copia").json()
    assert d["ativa"] is True and d["bucket"] == "rifas-backups"
    texto = json.dumps(d)
    for segredo in (SEGREDO, ID, PG_FALSO, "palavra", ENDPOINT):
        assert segredo not in texto


def test_so_o_dono_faz_a_copia_manual_e_fica_no_registo(admin, ligada, exporta, monkeypatch):
    gravados = []
    monkeypatch.setattr(s3_simples, "gravar", lambda *a, **k: gravados.append(a) or 200)
    admin.post("/api/admin/entrar", json={"token": LEITURA})
    assert admin.post("/api/admin/copia/fazer").status_code == 403 and gravados == []
    admin.post("/api/admin/sair")
    admin.post("/api/admin/entrar", json={"token": TOKEN})
    r = admin.post("/api/admin/copia/fazer")
    assert r.status_code == 200 and r.json()["chave"] == "backups/rifas-manual.json.gz" and r.json()["linhas"] == {"historico_diario": 1, "objetivos": 1} and len(gravados) == 1
    assert admin.get("/api/admin/auditoria").json()["itens"][0]["acao"] == "copia_manual"


def test_a_copia_manual_desligada_da_409_e_um_erro_do_s3_da_502(admin, ligada, exporta, monkeypatch):
    admin.post("/api/admin/entrar", json={"token": TOKEN})

    def recusa(*a, **k):
        raise s3_simples.ErroS3("HTTP 403")
    monkeypatch.setattr(s3_simples, "gravar", recusa)
    r = admin.post("/api/admin/copia/fazer")
    assert r.status_code == 502 and "HTTP 403" in r.json()["detail"] and SEGREDO not in r.text and ENDPOINT not in r.text
    monkeypatch.delenv("DATABASE_URL")
    assert admin.post("/api/admin/copia/fazer").status_code == 409


# ------------------------------------------------------------------ a base a sério, no Postgres (TEST_DATABASE_URL: um Postgres descartável)
URL_PG = os.environ.get("TEST_DATABASE_URL", "")


@pytest.mark.skipif(not URL_PG, reason="sem TEST_DATABASE_URL")
def test_postgres_exportar_e_restaurar_ida_e_volta():
    import psycopg
    from web.historico import HistoricoDiario
    from web.objetivos import Objetivos
    from web.opiniao import Comentarios

    with psycopg.connect(URL_PG, autocommit=True) as lig:
        for t in copia.TABELAS:
            lig.execute(f"DROP TABLE IF EXISTS {t}")
    h, o, c = HistoricoDiario(url_bd=URL_PG), Objetivos(url_bd=URL_PG), Comentarios(url_bd=URL_PG)
    h.gravar("2026-11-15", {"sessoes": {"Sessões": 9}}, 1_800_000_000)
    o.definir("sessoes", 30.5)
    c.criar("Um comentário que tem de sobreviver à cópia", False, "Rui", "PT")
    dados = copia.descomprimir(copia.comprimir(copia.exportar(URL_PG)))
    assert dados["tabelas"]["historico_diario"]["linhas"][0][0] == "2026-11-15" and dados["tabelas"]["objetivos"]["linhas"] == [["sessoes", 30.5]]
    assert "Um comentário que tem de sobreviver" in json.dumps(dados, ensure_ascii=False)
    with psycopg.connect(URL_PG, autocommit=True) as lig:
        for t in ("historico_diario", "objetivos", "comentarios"):
            lig.execute(f"DELETE FROM {t}")
    r1 = copia.restaurar(URL_PG, dados)
    assert r1["historico_diario"] == 1 and r1["objetivos"] == 1 and r1["comentarios"] == 1
    assert h.ler("2026-11-15", "2026-11-15") == [("2026-11-15", {"sessoes": {"Sessões": 9}})] and o.todos() == {"sessoes": 30.5} and c.total() == 1
    r2 = copia.restaurar(URL_PG, dados)                                                                        # outra vez: tabelas com dados ficam como estão
    assert r2["historico_diario"] is None and r2["objetivos"] is None and o.todos() == {"sessoes": 30.5}
    r3 = copia.restaurar(URL_PG, dados, forcar=True)                                                           # --juntar: só as que faltam
    assert r3["historico_diario"] == 0 and r3["objetivos"] == 0 and h.total() == 1
