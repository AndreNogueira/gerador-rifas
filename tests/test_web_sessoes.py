"""A API das sessoes (src/web/rotas.py) com o processo do motor a sério: analisar, pre-visualizar, gerar, descarregar, cancelar,
limpar, recuperar de um motor morto e as defesas de um servico publico (tamanho, IPs, uma geracao de cada vez)."""
import io
import time
import urllib.parse
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from pypdf import PdfReader

from web import config
from web.app import criar_app
from web.trabalhos import Motor

FX = Path(__file__).resolve().parent / "fixtures"
PDF_MULTI, PDF_UMA = "template_exemplo.pdf", "template_exemplo_1_rifa.pdf"
DIGITOS = "digitos_exemplo.png"


def _ler(nome):
    return (FX / nome).read_bytes()


@pytest.fixture(autouse=True)
def _teto_alto(monkeypatch):
    """Os testes que precisam de um trabalho demorado pedem 100 000 numeros: o teto por defeito (30 000) nao se aplica a eles.
    Os testes do proprio teto fixam o seu valor."""
    monkeypatch.setenv("MAX_NUMEROS", "1000000")


@pytest.fixture(scope="module")
def motor():
    """Um unico processo do motor para o modulo (arrancar custa ~1 s)."""
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


@pytest.fixture
def cliente(tmp_path, motor):
    with TestClient(criar_app(frontend=tmp_path / "sem_frontend", armazenamento=tmp_path / "dados", motor=motor)) as c:
        c.dados = tmp_path / "dados"
        yield c


def _nova(c, lingua="pt"):
    r = c.post("/api/sessoes", headers={"X-Lingua": lingua})
    assert r.status_code == 201, r.text
    return r.json()["sessao"]


def _enviar(c, sessao, o_que, nome_no_disco, nome="meu ficheiro.pdf", lingua="pt"):
    return c.put(f"/api/sessoes/{sessao}/{o_que}", content=_ler(nome_no_disco),
                 headers={"X-Nome": urllib.parse.quote(nome), "X-Lingua": lingua, "Content-Type": "application/octet-stream"})


def _pronta(c, template=PDF_MULTI, lingua="pt"):
    s = _nova(c, lingua)
    assert _enviar(c, s, "template", template, "Rifa São João.pdf", lingua).status_code == 200
    r = _enviar(c, s, "algarismos", DIGITOS, "digitos.png", lingua)
    assert r.status_code == 200 and r.json()["pronto"], r.text
    return s


def _campos(**kw):
    base = dict(nome="Rifa São João", inicio="1", fim="20", digitos="4", modo="varios", max_ficheiro="10", papel="A4", margem="5", porfolha="")
    base.update(kw)
    return base


def _esperar(c, s, estados=("ok", "erros", "cancelado", "falhou"), limite=60, lingua="pt"):
    fim = time.time() + limite
    while time.time() < fim:
        t = c.get(f"/api/sessoes/{s}/trabalho", headers={"X-Lingua": lingua}).json()
        if t["estado"] in estados:
            return t
        time.sleep(0.1)
    raise AssertionError("a geracao nao acabou a tempo")


# ------------------------------------------------------------------ sessao e uploads
def test_nova_sessao_esta_vazia_e_traduzida(cliente):
    d = cliente.post("/api/sessoes", headers={"X-Lingua": "en"}).json()
    assert d["template"]["estado"] == "vazio" and d["template"]["texto"] == "Choose the template PDF."
    assert d["algarismos"]["estado"] == "vazio" and d["pronto"] is False and d["info"] is None and d["trabalho"]["estado"] == "livre"
    assert cliente.get(f"/api/sessoes/{d['sessao']}", headers={"X-Lingua": "pt"}).json()["template"]["texto"] == "Escolha o PDF do template."


def test_lingua_do_pedido_vem_do_cabecalho_ou_do_browser(cliente):
    s = _nova(cliente)
    de = cliente.get(f"/api/sessoes/{s}", headers={"X-Lingua": "de"}).json()["template"]["texto"]
    assert de != cliente.get(f"/api/sessoes/{s}", headers={"X-Lingua": "pt"}).json()["template"]["texto"]
    ja = cliente.get(f"/api/sessoes/{s}", headers={"Accept-Language": "ja-JP,ja;q=0.9"}).json()["template"]["texto"]
    assert ja == cliente.get(f"/api/sessoes/{s}", headers={"X-Lingua": "ja"}).json()["template"]["texto"]
    assert cliente.get(f"/api/sessoes/{s}", headers={"X-Lingua": "klingon"}).json()["template"]["texto"]  # lingua invalida: ingles


def test_sessao_inexistente_da_404(cliente):
    for id_ in ("naoexisteaaaaaaaaaaaa", "x", "!!!!!!!!!!!!!!!!!!!!!!!!", "%2e%2e" * 10):
        r = cliente.get(f"/api/sessoes/{id_}")
        assert r.status_code == 404 and r.json()["tipo"] == "erro", id_


def test_template_com_varios_bilhetes(cliente):
    s = _nova(cliente)
    d = _enviar(cliente, s, "template", PDF_MULTI, "Rifa São João.pdf").json()
    assert d["template"]["estado"] == "ok" and d["template"]["nome"] == "Rifa São João.pdf"
    assert d["info"]["n_campos"] > 1 and d["info"]["tem_folha"] is False and d["info"]["digitos"] == len(d["info"]["primeiro"])
    assert d["algarismos"]["estado"] == "precisa" and d["pronto"] is False
    assert d["tem_modelo"] and cliente.get(d["modelo_url"]).content.startswith(b"%PDF-")


def test_template_de_uma_rifa_tem_painel_da_folha(cliente):
    s = _nova(cliente)
    d = _enviar(cliente, s, "template", PDF_UMA).json()
    assert d["info"]["n_campos"] == 1 and d["info"]["tem_folha"] is True


def test_algarismos_ok_e_descricao_na_lingua(cliente):
    s = _nova(cliente)
    _enviar(cliente, s, "template", PDF_MULTI)
    pt = _enviar(cliente, s, "algarismos", DIGITOS, "d.png").json()
    assert pt["pronto"] and pt["algarismos"]["estado"] == "ok" and pt["algarismos"]["texto"].startswith("✔ ")
    en = cliente.get(f"/api/sessoes/{s}", headers={"X-Lingua": "en"}).json()
    assert en["algarismos"]["texto"] != pt["algarismos"]["texto"] and "d.png" in en["algarismos"]["texto"]


def test_algarismos_antes_do_template_so_ficam_a_espera(cliente):
    s = _nova(cliente)
    d = _enviar(cliente, s, "algarismos", DIGITOS, "d.png").json()
    assert d["algarismos"]["estado"] == "vazio" and "d.png" in d["algarismos"]["texto"] and d["pronto"] is False
    d = _enviar(cliente, s, "template", PDF_MULTI).json()
    assert d["pronto"] is True


def test_template_que_nao_e_pdf_da_erro_claro_sem_guardar(cliente):
    s = _nova(cliente)
    r = cliente.put(f"/api/sessoes/{s}/template", content=b"MZ\x90\x00 isto e um .exe", headers={"X-Nome": "rifa.pdf"})
    d = r.json()
    assert r.status_code == 200 and d["template"]["estado"] == "erro" and "«rifa.pdf»" in d["template"]["detalhe"] and not d["tem_modelo"]
    assert d["template"]["texto"].startswith("✖ ") and "\n" not in d["template"]["texto"]


def test_template_pdf_sem_numeros_da_erro(cliente):
    s = _nova(cliente)
    d = _enviar(cliente, s, "template", "digitos_exemplo.pdf").json()          # um PDF valido, mas sem os numeros de exemplo
    assert d["template"]["estado"] == "erro" and d["template"]["detalhe"] and d["pronto"] is False


def test_algarismos_de_tipo_errado_sao_recusados(cliente):
    s = _nova(cliente)
    _enviar(cliente, s, "template", PDF_MULTI)
    r = cliente.put(f"/api/sessoes/{s}/algarismos", content=b"GIF89a....", headers={"X-Nome": "x.gif"})
    d = r.json()
    assert r.status_code == 200 and d["algarismos"]["estado"] == "erro" and d["algarismos"]["detalhe"] and d["pronto"] is False
    assert _enviar(cliente, s, "algarismos", DIGITOS, "d.png").json()["pronto"]                  # e corrige-se com um bom


def test_o_tipo_decide_se_pelos_bytes_nao_pelo_nome(cliente):
    s = _nova(cliente)
    _enviar(cliente, s, "template", PDF_MULTI)
    assert _enviar(cliente, s, "algarismos", DIGITOS, "isto_e_png.pdf").json()["pronto"]
    assert not any(n.endswith(".pdf") and n.startswith("algarismos") for n in cliente.get(f"/api/sessoes/{s}").json() and
                   [p.name for p in (cliente.dados / s).iterdir()])


def test_nomes_perigosos_nunca_chegam_ao_disco(cliente):
    s = _nova(cliente)
    d = cliente.put(f"/api/sessoes/{s}/template", content=_ler(PDF_MULTI), headers={"X-Nome": urllib.parse.quote("../../etc/passwd.pdf")}).json()
    assert d["template"]["estado"] == "ok"
    assert sorted(p.name for p in (cliente.dados / s).iterdir() if p.is_file()) == ["template.pdf"]
    assert not (cliente.dados.parent / "etc").exists()


def test_upload_demasiado_grande_e_cortado_sem_ler_tudo(cliente, monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_MB", "1")
    s = _nova(cliente)
    grande = b"%PDF-1.4\n" + b"0" * (1024 * 1024 + 10)
    r = cliente.put(f"/api/sessoes/{s}/template", content=grande, headers={"X-Lingua": "pt"})
    assert r.status_code == 413 and "1 MB" in r.json()["detail"] and r.json()["tipo"] == "aviso"

    def em_pedacos():                                           # sem Content-Length (chunked): o teto aplica-se ao fluxo
        for i in range(0, len(grande), 65536):
            yield grande[i:i + 65536]
    assert cliente.put(f"/api/sessoes/{s}/template", content=em_pedacos()).status_code == 413
    assert not (cliente.dados / s / "template.pdf").exists()


# ------------------------------------------------------------------ calcular (folha e resumo)
def test_calcular_resumo_varios_e_unico(cliente):
    s = _pronta(cliente)
    r = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(), headers={"X-Lingua": "pt"}).json()
    assert r["folha"] is None and r["resumo"]["aviso"] is False and "20" in r["resumo"]["texto"] and r["confirmar"] == ""
    u = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(modo="unico"), headers={"X-Lingua": "pt"}).json()
    assert u["resumo"]["max_ativo"] is False and u["resumo"]["texto"] != r["resumo"]["texto"]


def test_calcular_erros_viram_avisos_no_resumo(cliente):
    s = _pronta(cliente)
    assert cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(fim="abc")).json()["resumo"]["aviso"] is True
    assert cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(inicio="5", fim="1")).json()["resumo"]["aviso"] is True


def test_calcular_avisa_logo_se_passa_do_teto_de_numeros(cliente, monkeypatch):
    monkeypatch.setenv("MAX_NUMEROS", "50")
    s = _pronta(cliente)
    r = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(fim="51"), headers={"X-Lingua": "pt"}).json()
    assert r["resumo"]["aviso"] is True and "50" in r["resumo"]["texto"]
    assert cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(fim="50")).json()["resumo"]["aviso"] is False


def test_calcular_maximo_nao_multiplo_avisa(cliente):
    s = _pronta(cliente)
    n = cliente.get(f"/api/sessoes/{s}").json()["info"]["n_campos"]
    r = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(max_ficheiro=str(n * 3 + 1))).json()
    assert r["resumo"]["aviso"] is True


def test_calcular_folha_de_uma_rifa(cliente):
    s = _pronta(cliente, PDF_UMA)
    r = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(), headers={"X-Lingua": "pt"}).json()
    f = r["folha"]
    assert f["erro"] is False and f["maximo"] >= 1 and f["n"] == f["maximo"] and "A4" in f["texto"]
    a3 = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(papel="A3")).json()["folha"]
    assert a3["maximo"] > f["maximo"]
    pouco = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(porfolha="2")).json()["folha"]
    assert pouco["n"] == 2
    muito = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(porfolha="9999")).json()["folha"]
    assert muito["n"] == muito["maximo"] and muito["aviso"] is True
    mau = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(margem="999")).json()["folha"]
    assert mau["erro"] is True and mau["texto"].startswith("✖ ")


def test_calcular_pede_confirmacao_com_muitas_rifas_por_folha(cliente):
    s = _pronta(cliente, PDF_UMA)
    maximo = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(papel="A3", margem="0")).json()["folha"]["maximo"]
    r = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(papel="A3", margem="0", porfolha=str(maximo))).json()
    assert (r["confirmar"] != "") == (maximo > 24)


def test_calcular_valida_o_tamanho_dos_campos(cliente):
    s = _pronta(cliente)
    assert cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(nome="x" * 201)).status_code == 422
    assert cliente.post(f"/api/sessoes/{s}/calcular", json=_campos(modo="outro")).status_code == 422


# ------------------------------------------------------------------ pre-visualizar
def test_previa_devolve_um_pdf_de_uma_pagina_com_os_numeros(cliente):
    s = _pronta(cliente)
    d = cliente.post(f"/api/sessoes/{s}/previa", json=_campos(inicio="7", fim="30"), headers={"X-Lingua": "pt"}).json()
    assert d["previa"]["n"] == 1 and "7" in d["previa"]["titulo"]
    pdf = cliente.get(d["previa"]["url"])
    assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf"
    assert pdf.headers["cache-control"] == "no-store" and pdf.headers["content-disposition"] == "inline"
    leitor = PdfReader(io.BytesIO(pdf.content))
    assert len(leitor.pages) == 1
    d2 = cliente.post(f"/api/sessoes/{s}/previa", json=_campos(inicio="9"), headers={"X-Lingua": "pt"}).json()
    assert d2["previa"]["n"] == 2 and d2["previa"]["url"] != d["previa"]["url"]


def test_previa_com_folha_de_uma_rifa(cliente):
    s = _pronta(cliente, PDF_UMA)
    d = cliente.post(f"/api/sessoes/{s}/previa", json=_campos(porfolha="2")).json()
    assert d["previa"]["n"] == 1 and cliente.get(d["previa"]["url"]).content.startswith(b"%PDF-")


def test_previa_com_campos_invalidos_da_aviso_claro(cliente):
    s = _pronta(cliente)
    for kw in (dict(fim="0"), dict(digitos="0"), dict(digitos="99"), dict(inicio="x"), dict(inicio="5", fim="1")):
        r = cliente.post(f"/api/sessoes/{s}/previa", json=_campos(**kw), headers={"X-Lingua": "pt"})
        assert r.status_code == 422 and r.json()["tipo"] == "aviso" and r.json()["detail"], kw


def test_previa_sem_template_nem_algarismos(cliente):
    s = _nova(cliente)
    assert cliente.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 409
    _enviar(cliente, s, "template", PDF_MULTI)
    assert cliente.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 409


def test_novo_ficheiro_apaga_a_previa(cliente):
    s = _pronta(cliente)
    cliente.post(f"/api/sessoes/{s}/previa", json=_campos())
    assert cliente.get(f"/api/sessoes/{s}/previa.pdf").status_code == 200
    d = _enviar(cliente, s, "template", PDF_MULTI).json()
    assert d["previa"] is None and cliente.get(f"/api/sessoes/{s}/previa.pdf").status_code == 404


# ------------------------------------------------------------------ gerar e descarregar
def test_gerar_varios_ficheiros_da_um_zip_com_as_paginas_certas(cliente):
    s = _pronta(cliente)
    n = cliente.get(f"/api/sessoes/{s}").json()["info"]["n_campos"]
    r = cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(inicio="1", fim=str(n * 6), max_ficheiro=str(n * 2)), headers={"X-Lingua": "pt"})
    assert r.status_code == 202 and r.json()["trabalho"]["estado"] in ("a_gerar", "ok")
    t = _esperar(cliente, s)
    assert t["estado"] == "ok" and t["entrega"]["tipo"] == "zip" and t["entrega"]["total"] == 3 and t["feitas"] == t["total"] == 6
    assert any("0001" in linha or "1" in linha for linha in t["registo"]) and t["texto"]
    z = cliente.get(t["entrega"]["url"])
    assert z.status_code == 200 and z.headers["content-type"] == "application/zip"
    assert "filename*=UTF-8''" in z.headers["content-disposition"] and "S%C3%A3o" in z.headers["content-disposition"]
    with zipfile.ZipFile(io.BytesIO(z.content)) as zf:
        nomes = sorted(zf.namelist())
        assert len(nomes) == 3 and all(n_.endswith(".pdf") and "Rifa São João" in n_ for n_ in nomes)
        assert [len(PdfReader(io.BytesIO(zf.read(n_))).pages) for n_ in nomes] == [2, 2, 2]


def test_gerar_um_so_pdf_descarrega_o_pdf(cliente):
    s = _pronta(cliente)
    n = cliente.get(f"/api/sessoes/{s}").json()["info"]["n_campos"]
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim=str(n * 3), modo="unico"))
    t = _esperar(cliente, s)
    assert t["estado"] == "ok" and t["entrega"]["tipo"] == "pdf" and t["entrega"]["total"] == 1
    r = cliente.get(t["entrega"]["url"])
    assert r.headers["content-type"] == "application/pdf" and int(r.headers["content-length"]) == len(r.content)
    assert len(PdfReader(io.BytesIO(r.content)).pages) == 3


def test_gerar_com_folha_de_uma_rifa(cliente):
    s = _pronta(cliente, PDF_UMA)
    maximo = cliente.post(f"/api/sessoes/{s}/calcular", json=_campos()).json()["folha"]["maximo"]
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim=str(maximo * 2), modo="unico"))
    t = _esperar(cliente, s)
    assert t["estado"] == "ok"
    assert len(PdfReader(io.BytesIO(cliente.get(t["entrega"]["url"]).content)).pages) == 2


def test_gerar_mensagens_na_lingua_do_utilizador(cliente):
    s = _pronta(cliente, lingua="en")
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(), headers={"X-Lingua": "en"})
    en = _esperar(cliente, s, lingua="en")
    pt = cliente.get(f"/api/sessoes/{s}/trabalho", headers={"X-Lingua": "pt"}).json()
    assert en["texto"] != pt["texto"] and en["registo"] != pt["registo"] and len(en["registo"]) == len(pt["registo"]) > 0


def test_o_registo_le_se_desde_um_ponto(cliente):
    s = _pronta(cliente)
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos())
    t = _esperar(cliente, s)
    todas = len(t["registo"])
    assert todas > 1 and t["proximo"] == todas
    resto = cliente.get(f"/api/sessoes/{s}/trabalho?desde=1", headers={"X-Lingua": "pt"}).json()
    assert resto["registo"] == t["registo"][1:] and resto["proximo"] == todas
    assert cliente.get(f"/api/sessoes/{s}/trabalho?desde=999", headers={"X-Lingua": "pt"}).json()["registo"] == []


@pytest.mark.parametrize("kw, chave_do_texto", [
    (dict(nome=""), "err_nome"),
    (dict(nome="   "), "err_nome"),
    (dict(inicio="5", fim="1"), "err_intervalo"),
    (dict(max_ficheiro="0"), "err_max"),
    (dict(digitos="13"), "err_digitos"),
    (dict(fim="1000000"), "web_demasiados"),
])
def test_gerar_recusa_pedidos_invalidos_com_aviso_na_lingua(cliente, monkeypatch, kw, chave_do_texto):
    monkeypatch.setenv("MAX_NUMEROS", "30000")                 # o teto por defeito: 1 000 000 de numeros passa-o
    s = _pronta(cliente)
    r = cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(**kw), headers={"X-Lingua": "en"})
    assert r.status_code == 422 and r.json()["tipo"] == "aviso"
    from core import i18n
    esperado = i18n.TEXTOS["en"][chave_do_texto].split("{")[0].strip()
    assert esperado in r.json()["detail"]
    assert cliente.get(f"/api/sessoes/{s}").json()["trabalho"]["estado"] == "livre"


def test_gerar_maximo_nao_multiplo_e_recusado(cliente):
    s = _pronta(cliente)
    n = cliente.get(f"/api/sessoes/{s}").json()["info"]["n_campos"]
    r = cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(max_ficheiro=str(n + 1)))
    assert r.status_code == 422 and r.json()["tipo"] == "aviso"


def test_o_teto_de_numeros_configuravel(cliente, monkeypatch):
    monkeypatch.setenv("MAX_NUMEROS", "10")
    s = _pronta(cliente)
    r = cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim="11"))
    assert r.status_code == 422 and "10" in r.json()["detail"]


def test_gerar_outra_vez_substitui_os_pdfs_anteriores(cliente):
    s = _pronta(cliente)
    n = cliente.get(f"/api/sessoes/{s}").json()["info"]["n_campos"]
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim=str(n * 4), max_ficheiro=str(n)))
    assert _esperar(cliente, s)["entrega"]["total"] == 4
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim=str(n * 2), max_ficheiro=str(n)))
    assert _esperar(cliente, s)["entrega"]["total"] == 2
    assert len(list((cliente.dados / s / "saida").glob("*.pdf"))) == 2


def test_nao_se_pode_mexer_nos_ficheiros_durante_a_geracao(cliente, motor):
    s = _pronta(cliente)
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim="100000", modo="unico"))        # demora
    try:
        assert _enviar(cliente, s, "template", PDF_MULTI).status_code == 503
        assert cliente.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 503
        assert cliente.post(f"/api/sessoes/{s}/gerar", json=_campos()).status_code == 503
    finally:
        cliente.post(f"/api/sessoes/{s}/cancelar")
        _esperar(cliente, s)


def test_cancelar_a_meio(cliente):
    s = _pronta(cliente, PDF_UMA)
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim="100000", modo="unico", porfolha="1"))
    fim = time.time() + 30
    while cliente.get(f"/api/sessoes/{s}/trabalho").json()["feitas"] < 5:                    # espera que comece a montar paginas
        assert time.time() < fim
        time.sleep(0.05)
    c = cliente.post(f"/api/sessoes/{s}/cancelar", headers={"X-Lingua": "pt"}).json()
    assert c["estado"] == "a_cancelar"
    t = _esperar(cliente, s)
    assert t["estado"] == "cancelado" and t["entrega"] is None
    assert cliente.get(f"/api/sessoes/{s}/descarregar").status_code == 404


def test_cancelar_mata_o_motor_se_nao_parar_a_tempo(cliente, monkeypatch):
    """Gravar e verificar o PDF nao consultam o cancelamento: passada a espera, o processo do motor e morto e o estado e «cancelado»."""
    monkeypatch.setenv("CANCELAR_ESPERA_S", "0")
    s = _pronta(cliente, PDF_UMA)
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim="100000", modo="unico", porfolha="1"))
    time.sleep(0.5)
    assert cliente.post(f"/api/sessoes/{s}/cancelar").json()["estado"] == "a_cancelar"
    t = _esperar(cliente, s, limite=20)
    assert t["estado"] == "cancelado" and t["entrega"] is None and t["erro"] == ""
    assert cliente.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 200          # o motor recriou-se e esta livre


def test_o_tempo_de_espera_do_cancelamento_e_configuravel(monkeypatch):
    monkeypatch.delenv("CANCELAR_ESPERA_S", raising=False)
    assert config.espera_cancelar_s() == 3.0
    monkeypatch.setenv("CANCELAR_ESPERA_S", "0.5")
    assert config.espera_cancelar_s() == 0.5
    monkeypatch.setenv("CANCELAR_ESPERA_S", "abc")
    assert config.espera_cancelar_s() == 3.0


def test_uma_so_geracao_de_cada_vez_em_todo_o_servidor(cliente, motor):
    a, b = _pronta(cliente), _pronta(cliente)
    cliente.post(f"/api/sessoes/{a}/gerar", json=_campos(fim="100000", modo="unico"))
    try:
        r = cliente.post(f"/api/sessoes/{b}/gerar", json=_campos())
        assert r.status_code == 503 and r.json()["tipo"] == "aviso"
        assert cliente.post(f"/api/sessoes/{b}/previa", json=_campos()).status_code == 503       # outra sessao: ocupado, nao fica presa
    finally:
        cliente.post(f"/api/sessoes/{a}/cancelar")
        _esperar(cliente, a)
    assert cliente.post(f"/api/sessoes/{b}/previa", json=_campos()).status_code == 200            # libertou-se


def test_descarregar_sem_nada_gerado(cliente):
    s = _pronta(cliente)
    assert cliente.get(f"/api/sessoes/{s}/descarregar").status_code == 404


def test_o_nome_do_download_aguenta_acentos_e_aspas(cliente):
    s = _pronta(cliente)
    n = cliente.get(f"/api/sessoes/{s}").json()["info"]["n_campos"]
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(nome='Rifa "Ação" ç', fim=str(n), modo="unico"))
    t = _esperar(cliente, s)
    cab = cliente.get(t["entrega"]["url"]).headers["content-disposition"]
    assert cab.startswith('attachment; filename="') and "filename*=UTF-8''" in cab and '""' not in cab


# ------------------------------------------------------------------ limpar tudo, sessoes, limpeza
def test_limpar_tudo_apaga_ficheiros_e_estado(cliente):
    s = _pronta(cliente)
    cliente.post(f"/api/sessoes/{s}/previa", json=_campos())
    assert (cliente.dados / s).is_dir()
    assert cliente.delete(f"/api/sessoes/{s}").status_code == 204
    assert not (cliente.dados / s).exists() and cliente.get(f"/api/sessoes/{s}").status_code == 404
    assert cliente.delete(f"/api/sessoes/{s}").status_code == 204                      # idempotente


def test_limpar_tudo_durante_a_geracao_liberta_o_motor(cliente, motor):
    s = _pronta(cliente)
    cliente.post(f"/api/sessoes/{s}/gerar", json=_campos(fim="100000", modo="unico"))
    assert cliente.delete(f"/api/sessoes/{s}").status_code == 204
    outra = _pronta(cliente)                                                            # o motor foi reiniciado e esta livre
    assert cliente.post(f"/api/sessoes/{outra}/previa", json=_campos()).status_code == 200


def test_sessoes_inativas_sao_apagadas(cliente):
    sessoes = cliente.app.state.servico.sessoes
    a, b = _nova(cliente), _nova(cliente)
    sessoes._todas[a].ultimo -= 10_000
    assert sessoes.limpar() == 1
    assert cliente.get(f"/api/sessoes/{a}").status_code == 404 and cliente.get(f"/api/sessoes/{b}").status_code == 200
    assert not (cliente.dados / a).exists()


def test_sessoes_a_gerar_nao_sao_apagadas_por_inatividade(cliente):
    sessoes = cliente.app.state.servico.sessoes
    s = _nova(cliente)
    sessoes._todas[s].gerar.estado = "a_gerar"
    sessoes._todas[s].ultimo -= 10_000
    assert sessoes.limpar() == 0 and s in sessoes._todas


def test_limite_de_sessoes(cliente):
    sessoes = cliente.app.state.servico.sessoes
    sessoes.maximo = 2
    _nova(cliente), _nova(cliente)
    r = cliente.post("/api/sessoes", headers={"X-Lingua": "pt"})
    assert r.status_code == 503 and r.json()["tipo"] == "aviso"


def test_arranque_apaga_pastas_antigas(tmp_path, motor):
    dados = tmp_path / "dados"
    (dados / ("A" * 24)).mkdir(parents=True)
    (dados / ("A" * 24) / "template.pdf").write_bytes(b"x")
    with TestClient(criar_app(frontend=tmp_path, armazenamento=dados, motor=motor)):
        assert not (dados / ("A" * 24)).exists()


def test_limite_de_espaco_por_sessao(cliente, monkeypatch):
    monkeypatch.setattr(cliente.app.state.servico.sessoes.armazem, "limite", 1000)
    s = _nova(cliente)
    r = _enviar(cliente, s, "template", PDF_MULTI)
    assert r.status_code == 413 and r.json()["tipo"] == "aviso"


# ------------------------------------------------------------------ pedidos por IP
def test_limite_de_pedidos_pesados_por_ip(cliente, monkeypatch):
    monkeypatch.setenv("RATE_PESADOS_POR_MIN", "3")
    s = _nova(cliente)
    codigos = [cliente.put(f"/api/sessoes/{s}/algarismos", content=b"GIF89a", headers={"X-Lingua": "pt"}).status_code for _ in range(5)]
    assert codigos[:3] == [200] * 3 and codigos[3:] == [429, 429]
    r = cliente.put(f"/api/sessoes/{s}/algarismos", content=b"GIF89a", headers={"X-Lingua": "en"})
    assert r.status_code == 429 and r.json()["tipo"] == "aviso"


def test_limite_de_pedidos_leves_por_ip(cliente, monkeypatch):
    monkeypatch.setenv("RATE_LEVES_POR_MIN", "4")
    codigos = [cliente.post("/api/sessoes").status_code for _ in range(6)]
    assert codigos == [201] * 4 + [429] * 2


def test_o_limitador_esquece_com_o_tempo():
    from web.limites import Limitador
    lim = Limitador()
    assert [lim.permitir("1.1.1.1", "x", 2, agora=t) for t in (0, 1, 2)] == [True, True, False]
    assert lim.permitir("2.2.2.2", "x", 2, agora=2)                                     # outro IP tem a sua conta
    assert lim.permitir("1.1.1.1", "x", 2, agora=61.5)                                  # passou a janela


# ------------------------------------------------------------------ o processo do motor
def test_motor_recupera_se_o_processo_morrer(cliente, motor):
    s = _pronta(cliente)
    assert cliente.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 200
    for p in list(motor.pool._processes.values()):                                      # simula um OOM kill
        p.kill()
    time.sleep(0.5)
    r = cliente.post(f"/api/sessoes/{s}/previa", json=_campos(), headers={"X-Lingua": "pt"})
    assert r.status_code == 500 and r.json()["tipo"] == "erro" and r.json()["detail"]    # um erro limpo, nao um traceback
    assert cliente.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 200  # o seguinte ja funciona


def test_geracao_que_passa_do_tempo_e_interrompida(tmp_path):
    motor = Motor(tempo_maximo_s=1.0)
    try:
        with TestClient(criar_app(frontend=tmp_path, armazenamento=tmp_path / "dados", motor=motor)) as c:
            s = _pronta(c, PDF_UMA)
            c.post(f"/api/sessoes/{s}/gerar", json=_campos(fim="100000", modo="unico", porfolha="1"))
            t = _esperar(c, s, limite=30)
            assert t["estado"] == "falhou" and t["erro"] and t["entrega"] is None
            assert c.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 200   # o motor foi recriado e esta livre
    finally:
        motor.parar()


def test_o_worker_reutiliza_o_preparado_da_cache(cliente):
    s = _pronta(cliente)
    t0 = time.time()
    for _ in range(3):
        assert cliente.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 200
    assert time.time() - t0 < 10


def test_config_dos_limites_por_defeito(monkeypatch):
    for v in ("MAX_UPLOAD_MB", "MAX_NUMEROS", "JOB_TTL_MIN", "JOB_MAX_MIN", "MAX_SESSOES", "RIFAS_LIMITE_SESSAO_MB", "RATE_PESADOS_POR_MIN", "RATE_LEVES_POR_MIN"):
        monkeypatch.delenv(v, raising=False)
    assert (config.limite_upload_mb(), config.max_numeros(), config.validade_min(), config.tempo_maximo_geracao_min()) == (25, 30_000, 30, 10)
    assert (config.max_sessoes(), config.limite_sessao_mb(), config.pedidos_pesados_por_min(), config.pedidos_leves_por_min()) == (200, 300, 30, 300)


# ------------------------------------------------------------------ PNG da pre-visualizacao (browsers sem visor de PDF, como o Chrome do Android)
def test_a_previa_e_o_template_tambem_saem_em_png(cliente):
    s = _pronta(cliente)
    assert cliente.get(f"/api/sessoes/{s}/previa.png").status_code == 404                 # ainda nao ha pre-visualizacao
    assert cliente.post(f"/api/sessoes/{s}/previa", json=_campos()).status_code == 200
    for nome in ("previa", "modelo"):
        r = cliente.get(f"/api/sessoes/{s}/{nome}.png")
        assert r.status_code == 200 and r.headers["content-type"] == "image/png" and r.headers["cache-control"] == "no-store"
        assert r.content.startswith(b"\x89PNG") and len(r.content) > 5_000
    assert (cliente.dados / s / "previa.png").is_file()                                   # fica em cache ao lado do PDF
    assert cliente.get("/api/sessoes/naoexiste12345678901/previa.png").status_code == 404


def test_o_png_refaz_se_a_previa_mudar(cliente):
    s = _pronta(cliente)
    cliente.post(f"/api/sessoes/{s}/previa", json=_campos(inicio="1"))
    a = cliente.get(f"/api/sessoes/{s}/previa.png").content
    time.sleep(0.05)
    cliente.post(f"/api/sessoes/{s}/previa", json=_campos(inicio="5000", fim="5004"))
    b = cliente.get(f"/api/sessoes/{s}/previa.png").content
    assert a != b
