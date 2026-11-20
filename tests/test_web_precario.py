"""O gerador de preçários na webapp: o catálogo, a pré-visualização PNG, o PDF e a imagem descarregados, os erros traduzidos e a privacidade das métricas."""
import io
import json

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from pypdf import PdfReader
from web.app import criar_app
from web.trabalhos import Motor

PNG = b"\x89PNG\r\n\x1a\n"
PEDIDO = {"titulo": "Segredo da associação", "subtitulo": "Festa do bairro", "desenho": "santos", "colunas": 0,
          "linhas": [{"artigo": "sardinha", "preco": "1,5"}, {"artigo": "agua", "preco": "1"}, {"nome": "Bolo da vizinha", "categoria": "doces", "emoji": "1f370", "preco": "2.25"}]}


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


@pytest.fixture
def c(tmp_path, motor):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados", motor=motor)) as cliente:
        yield cliente


def test_o_catalogo_vem_na_lingua_do_pedido_com_desenhos_moedas_e_a_sugestao_do_mes(c):
    r = c.get("/api/precario/catalogo", params={"mes": 6}, headers={"X-Lingua": "pt-br"})
    d = r.json()
    assert r.status_code == 200 and "X-Lingua" in r.headers["vary"] and "max-age" in r.headers["cache-control"]
    ids = {a["id"] for cat in d["categorias"] for a in cat["artigos"]}
    assert "coxinha" in ids and "bifana" not in ids and d["sugerida"] == "festa_junina" and d["pais"] == "BR" and d["moeda"] == "BRL"
    assert len(d["desenhos"]) == 25 and d["desenhos"][-1] == {"id": "quadro", "nome": "Quadro negro"} and {"codigo": "BRL", "simbolo": "R$", "decimais": 2} in d["moedas"] and d["paises"]["PT"] == "EUR" and d["limites"]["linhas"] == 80
    assert d["formatos"] == ["A5", "A4", "A3", "A6x4"] and all(a["emoji"] for cat in d["categorias"] for a in cat["artigos"])
    pt = c.get("/api/precario/catalogo", headers={"X-Lingua": "pt"}).json()
    assert "bifana" in {a["id"] for cat in pt["categorias"] for a in cat["artigos"]} and pt["moeda"] == "EUR" and pt["sugerida"] == ""
    assert c.get("/api/precario/catalogo", params={"mes": 13}).status_code == 422


def test_previa_png_e_pdf_do_mesmo_pedido(c):
    r = c.post("/api/precario/previa.png", json=PEDIDO, headers={"X-Lingua": "pt"})
    assert r.status_code == 200 and r.content[:8] == PNG and r.headers["content-type"] == "image/png" and r.headers["cache-control"] == "no-store"
    r = c.post("/api/precario/pdf", json=PEDIDO, headers={"X-Lingua": "pt"})
    assert r.status_code == 200 and r.content.startswith(b"%PDF") and r.headers["content-type"] == "application/pdf" and "precario.pdf" in r.headers["content-disposition"]
    texto = PdfReader(io.BytesIO(r.content)).pages[0].extract_text()
    assert "Festa do bairro" in texto and "Sardinha assada" in texto and "1,50 €" in texto and "2,25 €" in texto and "Bolo da vizinha" in texto
    img = c.post("/api/precario/imagem.png", json=PEDIDO, params={"dpi": 100})
    assert img.status_code == 200 and img.content[:8] == PNG and "precario.png" in img.headers["content-disposition"]
    assert c.post("/api/precario/imagem.png", json=PEDIDO, params={"dpi": 400}).status_code == 422


def test_o_preco_le_se_na_lingua_do_pedido_e_a_moeda_vem_do_pedido(c):
    pedido = {"linhas": [{"artigo": "agua", "preco": "1.500"}], "titulo": "X", "moeda": {"codigo": "IDR"}}
    texto = PdfReader(io.BytesIO(c.post("/api/precario/pdf", json=pedido, headers={"X-Lingua": "id"}).content)).pages[0].extract_text()
    assert "Rp1.500" in texto
    ficha = {"linhas": [{"artigo": "agua", "preco": "3"}], "titulo": "X", "moeda": {"nome": "fichas", "decimais": 0}}
    assert "3 fichas" in PdfReader(io.BytesIO(c.post("/api/precario/pdf", json=ficha).content)).pages[0].extract_text()


@pytest.mark.parametrize("corpo", [
    {**PEDIDO, "titulo": "हिन्दी"}, {**PEDIDO, "desenho": "nao-existe"}, {**PEDIDO, "formato": "A0"}, {**PEDIDO, "linhas": []},
    {**PEDIDO, "linhas": [{"artigo": "agua", "preco": "abc"}]}, {**PEDIDO, "linhas": [{"artigo": "nao_existe"}]}, {**PEDIDO, "moeda": {"codigo": "XYZ"}},
])
def test_os_erros_sao_avisos_traduzidos_e_nada_se_desenha(c, corpo):
    for rota in ("previa.png", "pdf"):
        r = c.post(f"/api/precario/{rota}", json=corpo, headers={"X-Lingua": "en"})
        assert r.status_code == 422 and r.json()["tipo"] == "aviso" and "{" not in r.json()["detail"], (rota, r.text)
    assert "price list" in c.post("/api/precario/pdf", json={**PEDIDO, "titulo": "हिन्दी"}, headers={"X-Lingua": "en"}).json()["detail"]


@pytest.mark.parametrize("corpo", [{**PEDIDO, "colunas": 4}, {**PEDIDO, "titulo": "x" * 41}, {**PEDIDO, "linhas": [{"nome": "a"}] * 81}, {**PEDIDO, "linhas": [{"preco": "1" * 25}]},
                                   {**PEDIDO, "moeda": {"decimais": 3}}, {**PEDIDO, "rodape": "r" * 121}])
def test_os_limites_do_corpo_recusam_se_com_422(c, corpo):
    assert c.post("/api/precario/pdf", json=corpo).status_code == 422


def test_as_metricas_so_levam_o_desenho_o_formato_o_tamanho_e_a_moeda(c):
    c.post("/api/precario/pdf", json=PEDIDO)
    c.post("/api/precario/pdf", json={**PEDIDO, "moeda": {"nome": "SegredoFicha"}})
    c.post("/api/precario/previa.png", json=PEDIDO)                                  # só ver não conta
    serv = c.app.state.servico
    serv.metricas.descarregar(tudo=True)
    linhas = serv.metricas._consultar("SELECT tipo, a, b, c FROM eventos WHERE tipo IN ('precario', 'precario_moeda') ORDER BY tipo, a")
    assert set(linhas) == {("precario", "santos", "A4", "1-5"), ("precario_moeda", "inventada", "", ""), ("precario_moeda", "pais", "", "")}
    tudo = json.dumps(serv.metricas._consultar("SELECT * FROM eventos"), ensure_ascii=False)
    for segredo in ("Segredo da associação", "Festa do bairro", "Bolo da vizinha", "SegredoFicha", "sardinha", "1,5"):
        assert segredo not in tudo, segredo


def test_o_limite_de_pedidos_por_minuto_protege_o_descarregar(tmp_path, motor, monkeypatch):
    monkeypatch.setenv("RATE_PESADOS_POR_MIN", "2")
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html></html>", encoding="utf-8")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados2", motor=motor)) as cliente:
        codigos = [cliente.post("/api/precario/pdf", json=PEDIDO).status_code for _ in range(4)]
    assert codigos[:2] == [200, 200] and 429 in codigos[2:]


def test_os_cartoes_de_mesa_pelo_pdf_e_pela_previa(c):
    pedido = {"linhas": [{"artigo": "agua", "preco": "1,5"}, {"artigo": "cerveja"}], "titulo": "Festa", "formato": "A6x4"}
    r = c.post("/api/precario/pdf", json=pedido)
    assert r.status_code == 200 and r.content.startswith(b"%PDF")
    assert c.post("/api/precario/previa.png", json=pedido).status_code == 200
    muitos = {**pedido, "linhas": [{"nome": f"Artigo {i}"} for i in range(13)]}
    assert c.post("/api/precario/pdf", json=muitos, headers={"X-Lingua": "en"}).status_code == 422


def test_dois_tamanhos_pelo_pdf_e_pela_previa(c):
    pedido = {"linhas": [{"artigo": "agua", "preco": "1", "preco2": "1,8"}, {"nome": "Bolo", "preco2": "2,5"}], "tamanhos": True, "rotulos": ["Peq.", "Gde."], "titulo": "Festa"}
    r = c.post("/api/precario/pdf", json=pedido)
    assert r.status_code == 200 and r.content.startswith(b"%PDF")
    assert c.post("/api/precario/previa.png", json=pedido).status_code == 200
    assert c.post("/api/precario/pdf", json={**pedido, "rotulos": ["", "G"]}, headers={"X-Lingua": "en"}).status_code == 422
    assert c.post("/api/precario/pdf", json={**pedido, "rotulos": ["P"]}).status_code == 422
    assert c.post("/api/precario/pdf", json={**pedido, "rotulos": ["x" * 40, "G"]}).status_code == 422
    assert c.post("/api/precario/pdf", json={**pedido, "linhas": [{"artigo": "agua", "preco2": "abc"}]}).status_code == 422


def test_fotos_proprias_pelo_pdf_e_pela_previa_e_nada_fica_guardado(c):
    import base64
    import io
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGB", (300, 200), (10, 120, 60)).save(b, "JPEG")
    foto = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    pedido = {"linhas": [{"artigo": "agua", "preco": "1", "foto": foto}, {"nome": "Bolo", "foto": foto}], "titulo": "Festa"}
    assert c.post("/api/precario/pdf", json=pedido).status_code == 200
    assert c.post("/api/precario/previa.png", json=pedido).status_code == 200
    r = c.post("/api/precario/pdf", json={**pedido, "linhas": [{"artigo": "agua", "foto": "data:image/gif;base64,R0lGOD"}]}, headers={"X-Lingua": "en"})
    assert r.status_code == 422 and r.json()["tipo"] == "aviso"
    assert c.post("/api/precario/pdf", json={"linhas": [{"artigo": "agua", "foto": "x" * 200_001}]}).status_code == 422
    serv = c.app.state.servico
    serv.metricas.descarregar(tudo=True)
    assert "base64" not in str(serv.metricas._consultar("SELECT * FROM eventos"))
