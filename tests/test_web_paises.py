"""O país das visitas nas métricas: só o código ISO de duas letras que a rede do alojamento põe em `CF-IPCountry`; nunca o IP nem o valor bruto do cabeçalho."""
import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import criar_app
from web.metricas import Metricas, pais_do_cabecalho


@pytest.mark.parametrize("bruto,esperado", [
    ("PT", "PT"), ("pt", "PT"), (" br ", "BR"), ("US", "US"),
    ("XX", "??"), ("T1", "??"), ("", "??"), (None, "??"), ("PRT", "??"), ("P", "??"), ("P1", "??"), ("1.2.3.4", "??"),
    ("PT; drop table eventos", "??"), ("<script>", "??"), ("é", "??"),
])
def test_pais_do_cabecalho(bruto, esperado):
    assert pais_do_cabecalho(bruto) == esperado


@pytest.fixture
def cliente(tmp_path):
    m = Metricas(None)
    return TestClient(criar_app(frontend=tmp_path / "x", armazenamento=tmp_path / "dados", metricas=m)), m


def test_cada_sessao_conta_o_pais_que_o_cabecalho_diz(cliente):
    c, m = cliente
    for cc in ("PT", "PT", "pt", "BR", "FR"):
        assert c.post("/api/sessoes", headers={"CF-IPCountry": cc}).status_code == 201
    c.post("/api/sessoes")                                                    # sem cabeçalho (desenvolvimento local)
    c.post("/api/sessoes", headers={"CF-IPCountry": "XX"})                    # desconhecido
    paises = {d["chave"]: d["n"] for d in m.resumo(0)["paises"]}
    assert paises == {"PT": 3, "BR": 1, "FR": 1, "??": 2}


def test_so_o_codigo_chega_as_metricas_nunca_o_valor_bruto_nem_o_ip(cliente):
    c, m = cliente
    c.post("/api/sessoes", headers={"CF-IPCountry": "203.0.113.7", "X-Forwarded-For": "203.0.113.7"})
    c.post("/api/sessoes", headers={"CF-IPCountry": "Portugal, Lisboa"})
    with m._trava:
        guardados = [e for e in m._eventos if e[1] == "pais"]
    assert [e[2] for e in guardados] == ["??", "??"]
    for e in m._eventos:                                                     # nenhum evento tem o IP, e o país não viaja nas outras colunas
        assert "203.0.113" not in "".join(str(x) for x in e) and "Portugal" not in "".join(str(x) for x in e)
        if e[1] == "pais":
            assert e[3] == e[4] == ""


def test_o_painel_sabe_se_o_cabecalho_do_pais_chega(cliente):
    c, m = cliente
    assert m.proxy()["pais_pct"] is None
    for _ in range(3):
        c.get("/api/linguas", headers={"CF-IPCountry": "PT"})
    c.get("/api/linguas")
    assert m.proxy()["pais_pct"] == 75
