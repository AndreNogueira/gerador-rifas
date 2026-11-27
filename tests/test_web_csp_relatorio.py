"""O destino do `report-uri` da CSP (`POST /api/csp-relatorio`): conta-se o evento, nunca se guarda nem se regista o relatório."""
import json

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from web.app import CSP_RELATORIO, criar_app
from web.metricas import Metricas


@pytest.fixture
def cliente(tmp_path):
    m = Metricas(None)
    return TestClient(criar_app(frontend=tmp_path / "x", armazenamento=tmp_path / "dados", metricas=m)), m


def test_a_csp_aponta_para_o_destino_same_origin():
    assert "report-uri /api/csp-relatorio" in CSP_RELATORIO


def test_o_relatorio_conta_se_sem_guardar_o_corpo(cliente):
    c, m = cliente
    corpo = {"csp-report": {"blocked-uri": "https://exemplo-malicioso.com/x", "document-uri": "https://site/pagina-secreta"}}
    r = c.post("/api/csp-relatorio", content=json.dumps(corpo), headers={"Content-Type": "application/csp-report"})
    assert r.status_code == 204 and not r.content
    eventos = [e for e in m._eventos if e[1] == "csp_violacao"]
    assert len(eventos) == 1 and eventos[0][2:5] == ("", "", "")             # so o evento, sem nenhum dado do relatorio
    despejo = repr(m._eventos)
    assert "exemplo-malicioso" not in despejo and "pagina-secreta" not in despejo


def test_aceita_tambem_o_formato_novo_da_reporting_api(cliente):
    c, m = cliente
    corpo = [{"type": "csp-violation", "body": {"blockedURL": "https://exemplo.com/y"}}]
    r = c.post("/api/csp-relatorio", content=json.dumps(corpo), headers={"Content-Type": "application/reports+json"})
    assert r.status_code == 204
    assert len([e for e in m._eventos if e[1] == "csp_violacao"]) == 1


def test_corpo_vazio_ou_malformado_nao_rebenta(cliente):
    c, _m = cliente
    assert c.post("/api/csp-relatorio", content=b"", headers={"Content-Type": "application/csp-report"}).status_code == 204
    assert c.post("/api/csp-relatorio", content=b"{nao e json", headers={"Content-Type": "application/csp-report"}).status_code == 204
