"""O SEO por língua editável no painel e guardado na base de dados: validação, efeito nas páginas e no guia, recurso aos textos do código e o painel."""
import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from fastapi.testclient import TestClient
from web import guias, seo, seo_bd, seo_textos
from web.app import criar_app
from web.trabalhos import Motor

TOKEN = "uma-palavra-passe-longa-123"
DESC_OK = "Rifas numeradas em PDF a partir do Canva, com séries, talão e QR. Grátis, sem registo e sem instalar nada no computador."


@pytest.fixture(autouse=True)
def _limpo():
    seo_textos.definir_sobreposicoes({})
    yield
    seo_textos.definir_sobreposicoes({})


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    (tmp_path / "f").mkdir()
    (tmp_path / "f" / "index.html").write_text("<!doctype html><html lang=\"pt\"><head></head><body><div id=raiz><!--seo:corpo--></div></body></html>", encoding="utf-8")
    with TestClient(criar_app(frontend=tmp_path / "f", armazenamento=tmp_path / "d", motor=Motor(tempo_maximo_s=30))) as c:
        c.serv = c.app.state.servico
        yield c


def _entrar(c):
    assert c.post("/api/admin/entrar", json={"token": TOKEN}).status_code == 200


# ------------------------------------------------------------------ validacao
@pytest.mark.parametrize("chave, lingua, valor, razao", [
    ("nao_existe", "pt", "x", "desconhecido"),
    ("d_inicio", "xx", DESC_OK, "Língua"),
    ("d_inicio", "pt", "   ", "vazio"),
    ("d_inicio", "pt", "curta", "descrição deve ter"),
    ("d_inicio", "pt", "x" * 170, "descrição deve ter"),
    ("d_inicio", "pt", DESC_OK + "\nsegunda linha", "quebras"),
    ("d_inicio", "pt", DESC_OK + " {app}", "Parâmetros"),
    ("t_inicio", "pt", "Sem o parâmetro", "Parâmetros"),
    ("t_inicio", "pt", "{app}: " + "palavras " * 12, "título completo"),
    ("titulo:/tutorial", "pt", "T" * 70, "título completo"),
    ("titulo:/tutorial", "pt", "Com {app}", "Parâmetros"),
    ("guia.escolas.titulo", "pt", "T" * 66, "título completo"),
    ("guia.escolas.fim", "pt", "x" * 1001, "Máximo"),
])
def test_validacao_recusa_o_que_o_seo_nao_aceita(chave, lingua, valor, razao):
    with pytest.raises(ValueError, match=razao):
        seo_bd.validar(chave, lingua, valor)


def test_a_largura_conta_os_carateres_largos_a_dobrar():
    assert seo_bd.largura("abc") == 3 and seo_bd.largura("抽奖券") == 6
    seo_bd.validar("titulo:/tutorial", "zh", "抽" * 33)                      # 66
    with pytest.raises(ValueError):
        seo_bd.validar("titulo:/tutorial", "zh", "抽" * 34)                  # 68


def test_o_titulo_da_inicial_aceita_o_parametro_app():
    assert seo_bd.validar("t_inicio", "pt", "{app} — rifas em PDF") == "{app} — rifas em PDF"
    assert seo_bd.validar("guia.escolas.passo2.texto", "pt", "  Um texto novo.  ") == "Um texto novo."


def test_o_catalogo_cobre_titulos_descricoes_textos_e_guias_e_tem_padrao_em_todas_as_linguas():
    chaves = {c.chave for c in seo_bd.catalogo()}
    assert {"t_inicio", "d_inicio", "d_tutorial", "titulo:/tutorial", "intro", "guia.escolas.titulo", "guia.associacoes.passo5.texto", "guia.escolas.dica3"} <= chaves
    assert "titulo:/" not in chaves and not any(c.startswith("titulo:/admin") for c in chaves)
    for c in seo_bd.catalogo():
        for lg in i18n.LINGUAS:
            assert seo_bd.padrao(c.chave, lg), (c.chave, lg)


# ------------------------------------------------------------------ efeito no site
def test_um_texto_editado_aparece_na_pagina_so_nessa_lingua_e_repor_volta_ao_codigo(cliente):
    original = cliente.get("/tutorial").text
    novo = "Aprenda a fazer rifas numeradas com o Canva em quatro passos simples e sem instalar nada no computador."
    cliente.serv.seo.definir("d_tutorial", "pt", novo)
    cliente.serv.seo.definir("titulo:/tutorial", "pt", "Tutorial de rifas | Gerador de Rifas")
    pt = cliente.get("/tutorial").text
    assert f'<meta name="description" content="{novo}" />' in pt and "<title>Tutorial de rifas | Gerador de Rifas</title>" in pt
    assert novo not in cliente.get("/en/tutorial").text and "Tutorial de rifas" not in cliente.get("/en/tutorial").text
    assert f'content="{novo}"' in pt.split('property="og:description"')[1].split(">")[0]          # tambem no Open Graph
    assert cliente.serv.seo.repor("d_tutorial", "pt") and cliente.serv.seo.repor("titulo:/tutorial", "pt")
    assert cliente.get("/tutorial").text == original


def test_o_titulo_da_inicial_usa_o_parametro_app(cliente):
    cliente.serv.seo.definir("t_inicio", "en", "{app} - fast raffle tickets from Canva")
    assert "<title>Raffle Generator - fast raffle tickets from Canva</title>" in cliente.get("/en").text or "<title>" in cliente.get("/en").text
    assert seo_textos.texto("t_inicio", "en", app="X") == "X - fast raffle tickets from Canva"


def test_o_guia_editado_chega_a_api_e_ao_html(cliente):
    cliente.serv.seo.definir("guia.escolas.passo1.titulo", "pt", "Primeiro passo novo")
    cliente.serv.seo.definir("guia.escolas.dica2", "pt", "Uma dica nova e útil.")
    g = cliente.get("/api/guia/escolas", headers={"X-Lingua": "pt"}).json()
    assert g["passos"][0]["titulo"] == "Primeiro passo novo" and g["dicas"][1] == "Uma dica nova e útil."
    assert g["passos"][1]["titulo"] == guias.padrao("escolas", "pt")["passos"][1]["titulo"]       # o resto fica como no codigo
    html = cliente.get("/rifas-para-escolas").text
    assert "Primeiro passo novo" in html and "Uma dica nova e útil." in html
    assert cliente.get("/api/guia/escolas", headers={"X-Lingua": "en"}).json()["passos"][0]["titulo"] == guias.padrao("escolas", "en")["passos"][0]["titulo"]


def test_html_perigoso_num_texto_editado_sai_escapado(cliente):
    cliente.serv.seo.definir("guia.escolas.fim", "pt", '<script>alert(1)</script> fim')
    html = cliente.get("/rifas-para-escolas").text
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_a_base_em_baixo_mantem_os_textos_de_antes(cliente, monkeypatch):
    cliente.serv.seo.definir("d_tutorial", "pt", DESC_OK)
    monkeypatch.setattr(cliente.serv.seo, "lidos", lambda: (_ for _ in ()).throw(RuntimeError("base em baixo")))
    assert cliente.serv.seo.atualizar() == 1 and cliente.serv.seo.erro
    assert DESC_OK in cliente.get("/tutorial").text


def test_um_valor_estragado_a_mao_na_base_ignora_se(cliente):
    cliente.serv.seo.definir("d_tutorial", "pt", DESC_OK)
    cliente.serv.seo._executar("INSERT INTO seo_textos_bd(chave, lingua, valor, atualizado) VALUES (%s, %s, %s, 0)", ("d_video", "pt", "curto"))
    cliente.serv.seo._executar("INSERT INTO seo_textos_bd(chave, lingua, valor, atualizado) VALUES (%s, %s, %s, 0)", ("t_inicio", "pt", "sem parametro"))
    assert cliente.serv.seo.atualizar() == 1
    assert set(seo_textos.SOBREPOSTOS) == {("d_tutorial", "pt")}


def test_um_texto_editado_com_parametros_a_mais_nunca_parte_a_pagina(cliente):
    seo_textos.definir_sobreposicoes({("t_inicio", "pt"): "{app} e {outro}", ("voltar", "pt"): "{xpto}"})
    assert cliente.get("/").status_code == 200 and cliente.get("/tutorial").status_code == 200


# ------------------------------------------------------------------ o painel
def test_o_painel_do_seo_so_existe_com_sessao(cliente):
    assert cliente.get("/api/admin/seo").status_code == 404
    assert cliente.put("/api/admin/seo", json={"chave": "d_inicio", "lingua": "pt", "valor": DESC_OK}).status_code == 404
    assert cliente.delete("/api/admin/seo", params={"chave": "d_inicio", "lingua": "pt"}).status_code == 404


def test_o_painel_lista_edita_e_repoe(cliente):
    _entrar(cliente)
    d = cliente.get("/api/admin/seo", params={"lingua": "ja"}).json()
    assert d["lingua"] == "ja" and len(d["linguas"]) == len(i18n.LINGUAS) and d["limites"]["titulo"] == 66 and d["persistente"] is False
    item = next(i for i in d["itens"] if i["chave"] == "d_inicio")
    assert item["padrao"] and item["valor"] is None and item["tipo"] == "descricao"
    assert cliente.put("/api/admin/seo", json={"chave": "d_inicio", "lingua": "pt", "valor": "curto"}).status_code == 422
    r = cliente.put("/api/admin/seo", json={"chave": "d_inicio", "lingua": "pt", "valor": "  " + DESC_OK + " "})
    assert r.status_code == 200 and r.json()["valor"] == DESC_OK
    novo = cliente.get("/api/admin/seo", params={"lingua": "pt"}).json()
    assert next(i for i in novo["itens"] if i["chave"] == "d_inicio")["valor"] == DESC_OK
    assert DESC_OK in cliente.get("/").text
    assert cliente.delete("/api/admin/seo", params={"chave": "d_inicio", "lingua": "pt"}).status_code == 204
    assert next(i for i in cliente.get("/api/admin/seo", params={"lingua": "pt"}).json()["itens"] if i["chave"] == "d_inicio")["valor"] is None
    assert cliente.get("/api/admin/seo", params={"lingua": "xx"}).status_code == 422


def test_o_titulo_dos_robos_e_dos_paineis_nao_se_edita(cliente):
    assert seo.ADMIN.titulo("pt").startswith("Painel")
    with pytest.raises(ValueError):
        seo_bd.validar("titulo:/admin", "pt", "x")
