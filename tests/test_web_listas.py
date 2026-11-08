"""M2 na webapp: exportar a lista (CSV) e a folha de controlo (PDF) do pedido do formulario."""
import io
import urllib.parse

import pypdfium2 as pdfium
import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app

CAMPOS = dict(nome="Rifa de Natal", inicio="1", fim="40", digitos="4", modo="varios", max_ficheiro="5", papel="A4", margem="5", porfolha="")


@pytest.fixture
def c(tmp_path, monkeypatch):
    monkeypatch.setenv("MAX_NUMEROS", "100")
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text('<html><head><!--seo:cabecalho--></head><body><div id="raiz"><!--seo:corpo--></div></body></html>', encoding="utf-8")
    with TestClient(criar_app(frontend=dist, armazenamento=tmp_path / "dados")) as cliente:
        yield cliente


def _csv(r) -> list:
    return r.content.decode("utf-8-sig").split("\r\n")


def test_csv_com_series_saltos_e_cabecalhos_na_lingua(c):
    r = c.post("/api/exportar/lista.csv", json={**CAMPOS, "fim": "4", "prefixos": "A-, B-", "saltar": "2"}, headers={"X-Lingua": "en"})
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    assert _csv(r) == ["Series;Number;Name;Contact;Paid", "A;A-0001;;;", "A;A-0003;;;", "A;A-0004;;;", "B;B-0001;;;", "B;B-0003;;;", "B;B-0004;;;", ""]
    assert r.headers["cache-control"] == "no-store" and r.headers["x-content-type-options"] == "nosniff"
    assert urllib.parse.unquote(r.headers["content-disposition"]) == "attachment; filename*=UTF-8''Rifa de Natal.csv"


def test_csv_em_outras_linguas_e_sem_nome_o_ficheiro_chama_se_rifas(c):
    r = c.post("/api/exportar/lista.csv", json={**CAMPOS, "nome": "", "fim": "1"}, headers={"X-Lingua": "zh"})
    assert _csv(r)[0] == "系列;号码;姓名;联系方式;已付款" and "rifas.csv" in r.headers["content-disposition"]
    assert _csv(c.post("/api/exportar/lista.csv", json={**CAMPOS, "fim": "1"}, headers={"X-Lingua": "pt"}))[0] == "Série;Número;Nome;Contacto;Pago"


def test_folha_de_controlo_em_pdf_com_titulo_e_numeros(c):
    r = c.post("/api/exportar/controlo.pdf", json={**CAMPOS, "prefixos": "A-"}, headers={"X-Lingua": "pt"})
    assert r.status_code == 200 and r.headers["content-type"] == "application/pdf" and r.content[:5] == b"%PDF-"
    doc = pdfium.PdfDocument(io.BytesIO(r.content))
    try:
        assert len(doc) == 2                                                              # 40 bilhetes: 36 + 4
        tp = doc[0].get_textpage()
        texto = tp.get_text_range()
        tp.close()
    finally:
        doc.close()
    assert "Rifa de Natal: Controlo de vendas" in texto and "A-0001" in texto and "Contacto" in texto
    assert "Controlo - Rifa de Natal.pdf" in urllib.parse.unquote(r.headers["content-disposition"])


def test_folha_de_controlo_numa_lingua_que_a_helvetica_nao_escreve_sai_em_ingles(c):
    r = c.post("/api/exportar/controlo.pdf", json={**CAMPOS, "fim": "3"}, headers={"X-Lingua": "el"})
    doc = pdfium.PdfDocument(io.BytesIO(r.content))
    try:
        tp = doc[0].get_textpage()
        texto = tp.get_text_range()
        tp.close()
    finally:
        doc.close()
    assert "Sales control sheet" in texto and "Contact" in texto and "0001" in texto


@pytest.mark.parametrize("campos,fragmento", [
    ({"fim": "500"}, "100"),                                  # acima do teto de numeros
    ({"fim": "3", "prefixos": "A1"}, "prefix"),
    ({"fim": "3", "saltar": "x"}, "Skip"),
    ({"inicio": "5", "fim": "3"}, ""),
    ({"inicio": "x"}, ""),
    ({"fim": "3", "saltar": "1-3"}, ""),                      # os saltos comem tudo
])
def test_pedidos_invalidos_dao_aviso_422_traduzido(c, campos, fragmento):
    for rota in ("lista.csv", "controlo.pdf"):
        r = c.post(f"/api/exportar/{rota}", json={**CAMPOS, **campos}, headers={"X-Lingua": "en"})
        assert r.status_code == 422 and r.json()["tipo"] == "aviso" and fragmento.lower() in r.json()["detail"].lower()


def test_o_teto_conta_as_series(c):
    assert c.post("/api/exportar/lista.csv", json={**CAMPOS, "fim": "60", "prefixos": "A,B"}).status_code == 422       # 120 > 100
