"""IndexNow (`web/indexnow.py`): uma vez por versão, sem segredos, sem rede nos testes e sem acordar a base depois de tratada a versão."""
import json
import urllib.error

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import indexnow, seo
from web.app import criar_app
from web.relatorio import RelatoriosEnviados

BASE = "https://rifas.exemplo.pt"
AGORA = 1_800_000_000.0


class Resposta:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class Rede:
    """Um `urlopen` falso: guarda os pedidos e falha as primeiras `falhas` vezes."""
    def __init__(self, falhas=0, estado=200):
        self.pedidos, self.falhas, self.estado = [], falhas, estado

    def __call__(self, pedido, timeout=0):
        self.pedidos.append(pedido)
        if self.falhas > 0:
            self.falhas -= 1
            raise urllib.error.HTTPError(pedido.full_url, 429, "demasiados", {}, None)
        return Resposta(self.estado)


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch):
    for nome in ("INDEXNOW", "RENDER", "PUBLIC_URL", "RENDER_EXTERNAL_URL", "DATABASE_URL"):
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.setenv("INDEXNOW", "1")


@pytest.fixture
def relatorios(tmp_path):
    return RelatoriosEnviados(caminho=tmp_path / "r.sqlite3")


def test_a_chave_e_derivada_do_endereco_e_cumpre_o_formato():
    k = indexnow.chave(BASE)
    assert k == indexnow.chave(BASE) and k != indexnow.chave("https://outro.exemplo.pt")
    assert len(k) == 32 and all(c in "0123456789abcdef" for c in k)           # 8 a 128 letras, algarismos ou «-»


def test_os_enderecos_sao_os_do_sitemap_e_nada_mais():
    lista = indexnow.urls(BASE)
    assert len(lista) == len(set(lista)) and len(lista) == sum(1 for p in seo.ROTAS.values() if p.indexavel and p.no_mapa) * len(i18n.LINGUAS)
    assert f"{BASE}/" in lista and f"{BASE}/en/tutorial" in lista and f"{BASE}/como-numerar-bilhetes-de-rifa" in lista
    assert not any("/admin" in u or "/api" in u or "/opiniao" in u or "/comentarios" in u for u in lista)       # nada fora do índice


def test_o_pedido_leva_o_endereco_a_chave_e_so_enderecos_publicos(relatorios):
    rede = Rede()
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, indexnow.EstadoIndexNow(), AGORA, rede) == "enviado"
    (pedido,) = rede.pedidos
    assert pedido.full_url == "https://api.indexnow.org/indexnow" and pedido.get_method() == "POST"
    corpo = json.loads(pedido.data)
    assert corpo["host"] == "rifas.exemplo.pt" and corpo["key"] == indexnow.chave(BASE)
    assert corpo["keyLocation"] == f"{BASE}/{indexnow.chave(BASE)}.txt" and corpo["urlList"] == indexnow.urls(BASE)
    assert set(corpo) == {"host", "key", "keyLocation", "urlList"} and all(u.startswith(BASE) for u in corpo["urlList"])


def test_uma_vez_por_versao_mesmo_com_outro_arranque_e_a_nova_versao_volta_a_avisar(relatorios):
    rede, estado = Rede(), indexnow.EstadoIndexNow()
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA, rede) == "enviado"
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA + 300, rede) == "ja_tratado"
    # um arranque novo (memória vazia) da mesma versão: a reserva na base impede o 2.º aviso
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, indexnow.EstadoIndexNow(), AGORA + 600, rede) == "reservado"
    assert len(rede.pedidos) == 1
    assert indexnow.enviar_se_devido(relatorios, "3.69.0", BASE, estado, AGORA + 900, rede) == "enviado" and len(rede.pedidos) == 2


def test_depois_de_tratada_a_versao_as_rondas_nao_tocam_na_base(relatorios):
    estado = indexnow.EstadoIndexNow()
    indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA, Rede())
    chamadas = []
    original = relatorios._executar
    relatorios._executar = lambda *a, **k: (chamadas.append(a), original(*a, **k))[1]
    for i in range(1, 300):                                                 # um dia inteiro de rondas de 5 minutos
        assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA + i * 300, Rede()) == "ja_tratado"
    assert chamadas == []


def test_a_falha_solta_a_reserva_espera_uma_hora_e_desiste_ao_fim_de_tres(relatorios):
    rede, estado = Rede(falhas=99), indexnow.EstadoIndexNow()
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA, rede) == "erro" and estado.ultimo_erro == "HTTP 429"
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA + 1800, rede) == "espera" and len(rede.pedidos) == 1
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA + 3700, rede) == "erro"
    assert relatorios.reservar("indexnow:3.68.0", AGORA)                    # a reserva foi solta: outra execução ainda podia tentar
    relatorios.libertar("indexnow:3.68.0")
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA + 8000, rede) == "erro"
    assert estado.versao_tratada == "3.68.0" and indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA + 20000, rede) == "ja_tratado"
    assert len(rede.pedidos) == 3                                           # 3 tentativas e acabou


def test_uma_resposta_inesperada_conta_como_falha(relatorios):
    estado = indexnow.EstadoIndexNow()
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA, Rede(estado=500)) == "erro" and estado.ultimo_erro == "HTTP 500"
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, estado, AGORA + 3700, Rede(estado=202)) == "enviado"          # 202 também é sucesso


@pytest.mark.parametrize("base", ["", "http://rifas.exemplo.pt", "https://localhost", "https://127.0.0.1", "https://casa.local"])
def test_nunca_envia_de_enderecos_que_nao_sao_um_site_publico(relatorios, base):
    rede = Rede()
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", base, indexnow.EstadoIndexNow(), AGORA, rede) == "desligado" and rede.pedidos == []


def test_so_liga_no_render_ou_a_pedido_e_desliga_com_zero(monkeypatch, relatorios):
    monkeypatch.delenv("INDEXNOW")
    assert not indexnow.ligado(BASE)                                        # em casa e nos testes nunca sai nada para a rede
    monkeypatch.setenv("RENDER", "true")
    assert indexnow.ligado(BASE)
    monkeypatch.setenv("INDEXNOW", "0")
    assert not indexnow.ligado(BASE)
    rede = Rede()
    assert indexnow.enviar_se_devido(relatorios, "3.68.0", BASE, indexnow.EstadoIndexNow(), AGORA, rede) == "desligado" and rede.pedidos == []


def test_o_ficheiro_da_chave_so_existe_quando_esta_ligado(tmp_path, monkeypatch):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    monkeypatch.setenv("PUBLIC_URL", BASE)
    enviados = []
    monkeypatch.setattr(indexnow, "_enviar", lambda base, abrir: enviados.append(base) or 200)      # o ciclo de fundo da app corre mesmo: nunca à rede a sério
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "d1")) as c:
        r = c.get(f"/{indexnow.chave(BASE)}.txt")
        assert r.status_code == 200 and r.text == indexnow.chave(BASE) and r.headers["content-type"].startswith("text/plain")
        assert c.get("/0123456789abcdef0123456789abcdef.txt").status_code == 404
    monkeypatch.setenv("INDEXNOW", "0")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "d2")) as c:
        assert c.get(f"/{indexnow.chave(BASE)}.txt").status_code == 404
