"""A API pública v1 (`/api/v1`): chaves, quotas, limites e a geração em lote com o motor a sério (itens em fila, descarga, cancelar, apagar)."""
import io
import time
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from fastapi.testclient import TestClient
from pypdf import PdfReader
from web import chaves_api
from web.app import criar_app
from web.trabalhos import Motor

FX = Path(__file__).resolve().parent / "fixtures"
PDF_MULTI, DIGITOS = "template_exemplo.pdf", "digitos_exemplo.png"


@pytest.fixture(autouse=True)
def _tetos(monkeypatch):
    monkeypatch.setenv("MAX_NUMEROS", "1000")
    monkeypatch.delenv("API_MAX_NUMEROS_LOTE", raising=False)
    monkeypatch.setenv("API_ESPERA_MIN", "1")


@pytest.fixture(scope="module")
def motor():
    m = Motor(tempo_maximo_s=60)
    yield m
    m.parar()


@pytest.fixture
def cliente(tmp_path, motor):
    with TestClient(criar_app(frontend=tmp_path / "sem_frontend", armazenamento=tmp_path / "dados", motor=motor)) as c:
        c.serv = c.app.state.servico
        c.chave = c.serv.chaves.criar("teste", 100)[1]
        c.h = {"X-API-Key": c.chave, "X-Lingua": "en"}
        yield c


def _itens(*intervalos, **extra):
    return {"items": [dict(name=f"Rifa {i}", first=a, last=b, digits=4, per_file=10) | extra for i, (a, b) in enumerate(intervalos)]}


def _preparar(c, corpo, template=PDF_MULTI):
    r = c.post("/api/v1/batches", json=corpo, headers=c.h)
    assert r.status_code == 201, r.text
    id_ = r.json()["id"]
    assert c.put(f"/api/v1/batches/{id_}/template", content=(FX / template).read_bytes(), headers=c.h).status_code == 200
    r = c.put(f"/api/v1/batches/{id_}/digits", content=(FX / DIGITOS).read_bytes(), headers=c.h)
    assert r.status_code == 200 and r.json()["state"] == "ready", r.text
    return id_


def _esperar(c, id_, estados=("done", "done_with_errors", "failed", "cancelled"), limite=90):
    fim = time.time() + limite
    while time.time() < fim:
        d = c.get(f"/api/v1/batches/{id_}", headers=c.h).json()
        if d["state"] in estados:
            return d
        time.sleep(0.2)
    raise AssertionError(f"o lote nao acabou a tempo: {d}")


# ------------------------------------------------------------------ chaves
def test_so_se_guarda_o_hash_da_chave(tmp_path):
    ch = chaves_api.Chaves(caminho=tmp_path / "k.sqlite3")
    info, chave = ch.criar("gráfica", 50)
    assert chave.startswith("rk_") and info.prefixo == chave[:7] and len(chave) > 30
    assert chave.encode() not in (tmp_path / "k.sqlite3").read_bytes()               # nem em claro no disco
    assert ch.autenticar(chave).id == info.id and ch.autenticar(chave + "x") is None and ch.autenticar("rk_curta") is None
    assert ch.autenticar("") is None and ch.autenticar("não-é-ascii-" + "é" * 30) is None


def test_revogar_vale_logo_e_a_quota_e_atomica(tmp_path):
    ch = chaves_api.Chaves(caminho=tmp_path / "k.sqlite3")
    info, chave = ch.criar("a", 100)
    assert ch.consumir(info, 60) and not ch.consumir(info, 41) and ch.uso_hoje(info) == (60, 1)      # passaria de 100: nada se gasta
    assert ch.consumir(info, 40) and ch.uso_hoje(info) == (100, 2) and not ch.consumir(info, 1)
    ch.devolver(info, 40)
    assert ch.uso_hoje(info) == (60, 1)
    assert not ch.consumir(info, 101)
    assert ch.revogar(info.id) and not ch.revogar(info.id)
    assert ch.autenticar(chave) is None


def test_a_quota_recomeca_no_dia_seguinte(tmp_path):
    agora = [1_800_000_000.0]
    ch = chaves_api.Chaves(caminho=tmp_path / "k.sqlite3", relogio=lambda: agora[0])
    info, _ = ch.criar("a", 10)
    assert ch.consumir(info, 10) and not ch.consumir(info, 1)
    agora[0] += 86400
    assert ch.consumir(info, 10)


# ------------------------------------------------------------------ autenticacao e documentacao
def test_sem_chave_ou_com_chave_errada_e_401(cliente):
    assert cliente.post("/api/v1/batches", json=_itens((1, 10))).status_code == 401
    assert cliente.get("/api/v1/usage", headers={"X-API-Key": "rk_" + "x" * 40}).status_code == 401
    assert cliente.get("/api/v1/usage", headers=cliente.h).status_code == 200


def test_muitas_falhas_do_mesmo_ip_dao_429(cliente):
    codigos = [cliente.get("/api/v1/usage", headers={"X-API-Key": "rk_" + "y" * 40}).status_code for _ in range(25)]
    assert codigos[0] == 401 and codigos[-1] == 429


def test_swagger_e_openapi_da_v1_com_o_esquema_de_seguranca(cliente):
    assert cliente.get("/api/v1/docs").status_code == 200
    d = cliente.get("/api/v1/openapi.json").json()
    assert d["components"]["securitySchemes"]["APIKeyHeader"] == {"type": "apiKey", "in": "header", "name": "X-API-Key", "description": d["components"]["securitySchemes"]["APIKeyHeader"]["description"]}
    assert {"/batches", "/batches/{id_}", "/batches/{id_}/template", "/batches/{id_}/digits", "/batches/{id_}/start", "/batches/{id_}/cancel",
            "/batches/{id_}/download", "/batches/{id_}/items/{n}/download", "/usage"} <= set(d["paths"])
    assert cliente.get("/api/docs").status_code == 200                                # o Swagger interno continua
    assert cliente.get("/api/v1/usage", headers=cliente.h).headers["x-robots-tag"].startswith("noindex")


def test_admin_cria_lista_e_revoga_chaves(tmp_path, motor, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "uma-palavra-passe-longa-123")
    with TestClient(criar_app(frontend=tmp_path / "f", armazenamento=tmp_path / "d", motor=motor)) as c:
        assert c.get("/api/admin/chaves").status_code == 404 and c.post("/api/admin/chaves", json={"nome": "x"}).status_code == 404
        assert c.post("/api/admin/entrar", json={"token": "uma-palavra-passe-longa-123"}).status_code == 200
        criada = c.post("/api/admin/chaves", json={"nome": "Associação X", "quota_dia": 500}).json()
        assert criada["chave"].startswith("rk_") and criada["quota_dia"] == 500
        lista = c.get("/api/admin/chaves").json()
        assert [x["nome"] for x in lista] == ["Associação X"] and "chave" not in lista[0] and lista[0]["usados_hoje"] == 0
        assert c.get("/api/v1/usage", headers={"X-API-Key": criada["chave"]}).json()["daily_quota_numbers"] == 500
        assert c.delete(f"/api/admin/chaves/{criada['id']}").status_code == 204
        assert c.get("/api/v1/usage", headers={"X-API-Key": criada["chave"]}).status_code == 401
        assert c.delete(f"/api/admin/chaves/{criada['id']}").status_code == 404


# ------------------------------------------------------------------ o lote de ponta a ponta
def test_lote_de_ponta_a_ponta(cliente):
    id_ = _preparar(cliente, _itens((1, 20), (101, 125)))
    r = cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h)
    assert r.status_code == 202 and r.json()["state"] in ("running",)
    d = _esperar(cliente, id_)
    assert d["state"] == "done" and [i["state"] for i in d["items"]] == ["done", "done"], d
    assert d["numbers_total"] == 45 and d["download_url"].endswith(f"/batches/{id_}/download")
    assert d["items"][0]["files"] == ["Rifa 0_0001-0010.pdf", "Rifa 0_0011-0020.pdf"] or len(d["items"][0]["files"]) == 2
    # cada item: 20 numeros em ficheiros de 10 -> ZIP; 25 em ficheiros de 10 -> 3 PDFs
    z0 = cliente.get(f"/api/v1/batches/{id_}/items/0/download", headers=cliente.h)
    assert z0.status_code == 200 and z0.headers["content-type"] == "application/zip"
    assert len(zipfile.ZipFile(io.BytesIO(z0.content)).namelist()) == 2
    tudo = cliente.get(f"/api/v1/batches/{id_}/download", headers=cliente.h)
    nomes = zipfile.ZipFile(io.BytesIO(tudo.content)).namelist()
    assert tudo.status_code == 200 and len(nomes) == 5 and all(n.endswith(".pdf") for n in nomes)
    pdf = zipfile.ZipFile(io.BytesIO(tudo.content)).read(nomes[0])
    assert len(PdfReader(io.BytesIO(pdf)).pages) >= 1
    u = cliente.get("/api/v1/usage", headers=cliente.h).json()
    assert u["used_today_numbers"] == 45 and u["remaining_today_numbers"] == 55 and u["active_batches"] == 1
    assert cliente.delete(f"/api/v1/batches/{id_}", headers=cliente.h).status_code == 204
    assert cliente.get(f"/api/v1/batches/{id_}", headers=cliente.h).status_code == 404
    assert cliente.get("/api/v1/usage", headers=cliente.h).json()["active_batches"] == 0


def test_item_unico_descarrega_o_pdf_direto(cliente):
    id_ = _preparar(cliente, {"items": [dict(name="Só um", first=1, last=8, digits=4)]})
    cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h)
    d = _esperar(cliente, id_)
    r = cliente.get(d["items"][0]["download_url"], headers=cliente.h)
    assert d["state"] == "done" and r.headers["content-type"] == "application/pdf" and r.content.startswith(b"%PDF-")


def test_o_lote_so_e_visto_pela_chave_que_o_criou(cliente):
    id_ = _preparar(cliente, _itens((1, 5)))
    outra = cliente.serv.chaves.criar("outra", 100)[1]
    assert cliente.get(f"/api/v1/batches/{id_}", headers={"X-API-Key": outra}).status_code == 404
    assert cliente.delete(f"/api/v1/batches/{id_}", headers={"X-API-Key": outra}).status_code == 204       # nao apaga o de outra chave
    assert cliente.get(f"/api/v1/batches/{id_}", headers=cliente.h).status_code == 200


# ------------------------------------------------------------------ limites
def test_limites_do_lote(cliente, monkeypatch):
    monkeypatch.setenv("API_MAX_ITENS", "2")
    assert cliente.post("/api/v1/batches", json=_itens((1, 5), (1, 5), (1, 5)), headers=cliente.h).status_code == 422
    assert cliente.post("/api/v1/batches", json=_itens((1, 2000)), headers=cliente.h).status_code == 422          # MAX_NUMEROS=1000
    assert cliente.post("/api/v1/batches", json={"items": []}, headers=cliente.h).status_code == 422
    monkeypatch.setenv("API_MAX_NUMEROS_LOTE", "30")
    assert cliente.post("/api/v1/batches", json=_itens((1, 20), (1, 20)), headers=cliente.h).status_code == 422
    r = cliente.post("/api/v1/batches", json={"items": [dict(name="x", first=10, last=1)]}, headers=cliente.h)
    assert r.status_code == 422 and r.json()["detail"].startswith("[items/0]")


def test_a_quota_diaria_recusa_o_arranque_sem_gastar(cliente):
    id_ = _preparar(cliente, _itens((1, 60), (1, 60)))                                # 120 > quota 100
    r = cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h)
    assert r.status_code == 429 and "Daily quota" in r.json()["detail"]
    assert cliente.get("/api/v1/usage", headers=cliente.h).json()["used_today_numbers"] == 0
    assert cliente.get(f"/api/v1/batches/{id_}", headers=cliente.h).json()["state"] == "ready"


def test_lotes_ativos_por_chave(cliente, monkeypatch):
    monkeypatch.setenv("API_LOTES_ATIVOS", "2")
    ids = [cliente.post("/api/v1/batches", json=_itens((1, 5)), headers=cliente.h) for _ in range(3)]
    assert [r.status_code for r in ids] == [201, 201, 429]
    cliente.delete(f"/api/v1/batches/{ids[0].json()['id']}", headers=cliente.h)
    assert cliente.post("/api/v1/batches", json=_itens((1, 5)), headers=cliente.h).status_code == 201


def test_uploads_invalidos_e_fora_de_ordem(cliente):
    id_ = cliente.post("/api/v1/batches", json=_itens((1, 5)), headers=cliente.h).json()["id"]
    assert cliente.put(f"/api/v1/batches/{id_}/template", content=b"nao e um pdf", headers=cliente.h).status_code == 422
    assert cliente.put(f"/api/v1/batches/{id_}/digits", content=b"nem uma imagem", headers=cliente.h).status_code == 422
    assert cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h).status_code == 409           # sem ficheiros
    assert cliente.get(f"/api/v1/batches/{id_}", headers=cliente.h).json()["state"] == "waiting_files"
    assert cliente.get(f"/api/v1/batches/{id_}/download", headers=cliente.h).status_code == 404
    assert cliente.get("/api/v1/batches/inexistente", headers=cliente.h).status_code == 404


def test_um_lote_nao_arranca_duas_vezes(cliente):
    id_ = _preparar(cliente, _itens((1, 5)))
    assert cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h).status_code == 202
    assert cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h).status_code == 409
    assert cliente.put(f"/api/v1/batches/{id_}/template", content=(FX / PDF_MULTI).read_bytes(), headers=cliente.h).status_code == 409
    _esperar(cliente, id_)


# ------------------------------------------------------------------ fila atras do site, cancelar, apagar
def test_o_lote_espera_pela_vez_do_motor(cliente):
    id_ = _preparar(cliente, _itens((1, 5)))
    assert cliente.serv.motor.reservar("alguem-do-site")                              # o site esta a gerar
    try:
        cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h)
        time.sleep(0.8)
        d = cliente.get(f"/api/v1/batches/{id_}", headers=cliente.h).json()
        assert d["state"] == "running" and d["items"][0]["state"] == "queued"
    finally:
        cliente.serv.motor.geracao = None
    assert _esperar(cliente, id_)["state"] == "done"


def test_cancelar_um_lote_em_fila_nao_gera_nada(cliente):
    id_ = _preparar(cliente, _itens((1, 5), (6, 10)))
    assert cliente.serv.motor.reservar("alguem-do-site")
    try:
        cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h)
        time.sleep(0.5)
        assert cliente.post(f"/api/v1/batches/{id_}/cancel", headers=cliente.h).json()["state"] in ("cancelling", "cancelled")
        d = _esperar(cliente, id_, ("cancelled",))
    finally:
        cliente.serv.motor.geracao = None
    assert [i["state"] for i in d["items"]] == ["cancelled", "cancelled"] and d["download_url"] == ""


def test_a_espera_pelo_motor_tem_limite(cliente, monkeypatch):
    import web.api_v1 as v1
    monkeypatch.setattr(v1.config, "api_espera_motor_min", lambda: 0)               # desiste logo
    id_ = _preparar(cliente, _itens((1, 5)))
    assert cliente.serv.motor.reservar("alguem-do-site")
    try:
        cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h)
        d = _esperar(cliente, id_, ("failed",))
    finally:
        cliente.serv.motor.geracao = None
    assert d["items"][0]["state"] == "failed" and "busy" in d["items"][0]["error"]


def test_apagar_um_lote_a_correr_liberta_o_motor(cliente):
    id_ = _preparar(cliente, _itens((1, 900)))                                         # demora o suficiente
    cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h)
    for _ in range(50):
        if cliente.get(f"/api/v1/batches/{id_}", headers=cliente.h).json()["items"][0]["state"] == "running":
            break
        time.sleep(0.1)
    assert cliente.delete(f"/api/v1/batches/{id_}", headers=cliente.h).status_code == 204
    time.sleep(0.5)
    assert cliente.serv.motor.geracao is None
    nova = _preparar(cliente, _itens((1, 5)))                                          # o servidor continua a gerar
    cliente.post(f"/api/v1/batches/{nova}/start", headers=cliente.h)
    assert _esperar(cliente, nova)["state"] == "done"


def test_as_metricas_da_api_nao_levam_a_chave(cliente):
    id_ = _preparar(cliente, _itens((1, 5)))
    cliente.post(f"/api/v1/batches/{id_}/start", headers=cliente.h)
    _esperar(cliente, id_)
    texto = repr(cliente.serv.metricas._eventos)
    assert cliente.chave not in texto and cliente.chave[:7] not in texto.replace("api_v1", "") and "Rifa 0" not in texto
    assert "lote_arrancado" in texto and "api_geracao" in texto
