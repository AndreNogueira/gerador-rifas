"""Substitutos de «ficheiros locais» e de «abrir a pasta»: core.armazenamento (sessoes em disco configuravel) e core.saida
(descarregar um PDF ou um ZIP em streaming)."""
import io
import os
import time
import zipfile
from pathlib import Path

import pytest

import core
from core import armazenamento as arm
from core import saida
from conftest import erro_de


# ------------------------------------------------------------------ armazenamento
@pytest.fixture
def a(tmp_path):
    return arm.ArmazenamentoLocal(tmp_path / "dados")


def test_raiz_e_limite_por_variaveis_de_ambiente(monkeypatch, tmp_path):
    monkeypatch.delenv("RIFAS_ARMAZENAMENTO", raising=False)
    monkeypatch.delenv("RIFAS_LIMITE_SESSAO_MB", raising=False)
    assert arm.raiz_por_defeito().name == "gerador-rifas" and arm.limite_por_defeito() is None
    monkeypatch.setenv("RIFAS_ARMAZENAMENTO", str(tmp_path / "x"))
    monkeypatch.setenv("RIFAS_LIMITE_SESSAO_MB", "1.5")
    assert arm.raiz_por_defeito() == tmp_path / "x" and arm.limite_por_defeito() == 1572864
    s = arm.ArmazenamentoLocal()
    assert s.raiz == tmp_path / "x" and s.raiz.is_dir() and s.limite == 1572864
    for mau in ("", "abc", "0", "-3"):
        monkeypatch.setenv("RIFAS_LIMITE_SESSAO_MB", mau)
        assert arm.limite_por_defeito() is None


def test_cumpre_o_contrato(a):
    assert isinstance(a, arm.Armazenamento)


def test_sessao_nova_e_aleatoria_e_valida(a):
    ids = {a.nova_sessao() for _ in range(20)}
    assert len(ids) == 20
    for sid in ids:
        assert len(sid) >= 16 and (a.raiz / sid).is_dir()
        a._validar_sessao(sid)


@pytest.mark.parametrize("mau", ["", "abc", "../../etc", "a" * 15, "a/b" + "c" * 20, "x" * 65, "x" * 20 + "\\..", None, 5, "x" * 20 + " "])
def test_ids_de_sessao_invalidos(a, mau):
    with pytest.raises(ValueError):
        a.pasta(mau)


@pytest.mark.parametrize("mau", ["", ".", "..", "../x.pdf", "a/b.pdf", "a\\b.pdf", "C:x.pdf", "x?.pdf", "a\x00b", " x", "x.", "con|x", "n" * 201])
def test_nomes_invalidos(a, mau):
    s = a.nova_sessao()
    with pytest.raises(ValueError):
        a.guardar(s, mau, b"x")
    with pytest.raises(ValueError):
        a.ler(s, mau)


def test_guardar_ler_listar_existe(a):
    s = a.nova_sessao()
    p = a.guardar(s, "template.pdf", b"%PDF-1")
    assert p == a.raiz / s / "template.pdf" and p.read_bytes() == b"%PDF-1"
    a.guardar(s, "A.pdf", b"x" * 10, sub="saida")
    assert a.ler(s, "template.pdf") == b"%PDF-1" and a.ficheiro_local(s, "A.pdf", "saida").name == "A.pdf"
    assert a.listar(s) == ["template.pdf"] and a.listar(s, "saida") == ["A.pdf"] and a.listar(s, "nao_existe") == []
    assert a.existe(s, "template.pdf") and not a.existe(s, "outro.pdf") and not a.existe(s, "template.pdf", "saida")
    assert a.tamanho(s) == 16
    a.guardar(s, "template.pdf", b"novo")                       # substitui
    assert a.ler(s, "template.pdf") == b"novo" and a.tamanho(s) == 14


def test_ler_o_que_nao_existe(a):
    s = a.nova_sessao()
    with pytest.raises(FileNotFoundError):
        a.ler(s, "nada.pdf")
    with pytest.raises(FileNotFoundError):
        a.ficheiro_local(s, "nada.pdf", "saida")


def test_sessoes_isoladas(a):
    s1, s2 = a.nova_sessao(), a.nova_sessao()
    a.guardar(s1, "x.pdf", b"1")
    assert a.listar(s2) == [] and not a.existe(s2, "x.pdf")
    with pytest.raises(FileNotFoundError):
        a.ler(s2, "x.pdf")


def test_apagar_sessao(a):
    s = a.nova_sessao()
    a.guardar(s, "x.pdf", b"1", sub="saida")
    a.apagar_sessao(s)
    assert not (a.raiz / s).exists() and a.tamanho(s) == 0 and a.listar(s) == []
    a.apagar_sessao(s)                                          # apagar duas vezes nao rebenta


def test_limite_de_espaco_por_sessao(tmp_path):
    a = arm.ArmazenamentoLocal(tmp_path, limite_bytes=100)
    s = a.nova_sessao()
    a.guardar(s, "a.bin", b"x" * 60)
    with pytest.raises(arm.ArmazenamentoCheio):
        a.guardar(s, "b.bin", b"x" * 41)
    assert not a.existe(s, "b.bin")
    a.guardar(s, "b.bin", b"x" * 40)                            # cabe exatamente
    a.guardar(s, "a.bin", b"y" * 60)                            # substituir nao conta o antigo duas vezes
    s2 = a.nova_sessao()
    a.guardar(s2, "a.bin", b"x" * 100)                          # o limite e por sessao
    with pytest.raises(arm.ArmazenamentoCheio):
        a.guardar(s2, "c.bin", b"x")


def test_limpar_antigas(a):
    velha, nova = a.nova_sessao(), a.nova_sessao()
    a.guardar(velha, "x.pdf", b"1", sub="saida")
    a.guardar(nova, "x.pdf", b"1")
    agora = time.time()
    for p in [a.raiz / velha, *(a.raiz / velha).rglob("*")]:
        os.utime(p, (agora - 7200, agora - 7200))               # tudo na sessao velha tem 2 horas
    (a.raiz / "README.txt").write_text("nao e uma sessao")
    (a.raiz / "pasta_qualquer").mkdir()
    assert a.limpar_antigas(3600, agora) == 1
    assert not (a.raiz / velha).exists() and (a.raiz / nova).exists()
    assert (a.raiz / "README.txt").exists() and (a.raiz / "pasta_qualquer").exists()      # so apaga sessoes
    assert a.limpar_antigas(3600, agora) == 0
    assert a.limpar_antigas(3600, agora + 7200) == 1            # a nova tambem fica velha mais tarde


def test_sessao_com_ficheiro_recente_nao_e_apagada(a):
    s = a.nova_sessao()
    a.guardar(s, "velho.pdf", b"1")
    agora = time.time()
    os.utime(a.raiz / s / "velho.pdf", (agora - 7200, agora - 7200))
    os.utime(a.raiz / s, (agora - 7200, agora - 7200))
    a.guardar(s, "novo.pdf", b"2")                              # actividade recente na sessao
    assert a.limpar_antigas(3600, agora) == 0


def test_o_motor_trabalha_com_os_ficheiros_da_sessao(a, fx):
    """Fluxo da webapp: upload -> sessao -> preparar -> gerar para a pasta da sessao -> descarregar."""
    s = a.nova_sessao()
    a.guardar(s, "template.pdf", fx("template_exemplo.pdf").read_bytes())
    a.guardar(s, "algarismos.pdf", fx("digitos_exemplo.pdf").read_bytes())
    prep = core.preparar(a.ficheiro_local(s, "template.pdf"), a.ficheiro_local(s, "algarismos.pdf"))
    r = core.gerar(core.Trabalho(a.pasta(s, "saida"), "Rifa", 1, 12, por_ficheiro=5), prep)
    assert [x.ok for x in r] == [True, True, True] and a.listar(s, "saida") == [x.caminho.name for x in r]
    e = saida.entrega(r, "Rifa")
    assert e.tipo == "zip" and e.nome == "Rifa.zip"
    assert zipfile.ZipFile(io.BytesIO(b"".join(saida.conteudo_da_entrega(e)))).namelist() == a.listar(s, "saida")
    a.apagar_sessao(s)
    assert not (a.raiz / s).exists()


# ------------------------------------------------------------------ saida: ZIP em streaming
def _criar(tmp_path, nomes, tamanho=10):
    fs = []
    for n in nomes:
        p = tmp_path / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(os.urandom(tamanho))
        fs.append(p)
    return fs


def test_zip_em_streaming_le_se_com_o_zipfile(tmp_path):
    fs = _criar(tmp_path, ["A - 0001 - 0005.pdf", "A - 0006 - 0010.pdf"], 1000)
    dados = b"".join(saida.zip_em_streaming(fs))
    z = zipfile.ZipFile(io.BytesIO(dados))
    assert z.testzip() is None and z.namelist() == ["A - 0001 - 0005.pdf", "A - 0006 - 0010.pdf"]
    assert [z.read(n) for n in z.namelist()] == [f.read_bytes() for f in fs]
    assert all(i.compress_type == zipfile.ZIP_STORED for i in z.infolist())


def test_zip_em_streaming_e_mesmo_aos_bocados(tmp_path):
    """Um ficheiro de 3 MB nao e emitido de uma vez (memoria limitada): sai em varios pedacos."""
    fs = _criar(tmp_path, ["grande.bin"], 3 * 1024 * 1024)
    pedacos = list(saida.zip_em_streaming(fs))
    assert len(pedacos) >= 10 and max(len(p) for p in pedacos) <= saida.BOCADO + 4096
    assert zipfile.ZipFile(io.BytesIO(b"".join(pedacos))).read("grande.bin") == fs[0].read_bytes()


def test_zip_com_compressao_e_nomes_repetidos(tmp_path):
    (tmp_path / "a").mkdir(); (tmp_path / "b").mkdir()
    f1, f2, f3 = tmp_path / "a" / "x.pdf", tmp_path / "b" / "x.pdf", tmp_path / "c.txt"
    f1.write_bytes(b"A" * 5000); f2.write_bytes(b"B" * 5000); f3.write_bytes(b"C" * 5000)
    dados = b"".join(saida.zip_em_streaming([f1, f2, f3], comprimir=True))
    z = zipfile.ZipFile(io.BytesIO(dados))
    assert z.namelist() == ["x.pdf", "x (2).pdf", "c.txt"]
    assert z.read("x.pdf") == b"A" * 5000 and z.read("x (2).pdf") == b"B" * 5000
    assert all(i.compress_type == zipfile.ZIP_DEFLATED for i in z.infolist()) and len(dados) < 3000


def test_zip_sem_ficheiros_e_valido(tmp_path):
    z = zipfile.ZipFile(io.BytesIO(b"".join(saida.zip_em_streaming([]))))
    assert z.namelist() == []


def test_zip_ficheiro_vazio_e_nome_com_acentos(tmp_path):
    f = tmp_path / "Ação ñ.pdf"
    f.write_bytes(b"")
    z = zipfile.ZipFile(io.BytesIO(b"".join(saida.zip_em_streaming([f]))))
    assert z.namelist() == ["Ação ñ.pdf"] and z.read("Ação ñ.pdf") == b""


# ------------------------------------------------------------------ saida: entrega
def _res(p, ok=True):
    return core.Resultado(p, 1, [] if ok else ["erro"])


def test_entrega_um_pdf_e_pdf(tmp_path):
    f, = _criar(tmp_path, ["Rifa - 0001 - 0005.pdf"], 100)
    e = saida.entrega([_res(f)], "Rifa")
    assert (e.tipo, e.nome, e.media_type, e.ficheiros) == ("pdf", f.name, "application/pdf", [f])
    assert b"".join(saida.conteudo_da_entrega(e)) == f.read_bytes()


def test_entrega_varios_e_zip_com_nome_seguro(tmp_path):
    fs = _criar(tmp_path, ["a.pdf", "b.pdf"])
    e = saida.entrega([_res(f) for f in fs], 'Rifa/Natal: "2026"?')
    assert (e.tipo, e.nome, e.media_type) == ("zip", "RifaNatal 2026.zip", "application/zip")
    assert saida.entrega([_res(f) for f in fs], "///").nome == "rifas.zip"


def test_entrega_so_com_os_verificados(tmp_path):
    fs = _criar(tmp_path, ["a.pdf", "b.pdf", "c.pdf"])
    e = saida.entrega([_res(fs[0]), _res(fs[1], ok=False), _res(fs[2])], "R")
    assert e.tipo == "zip" and e.ficheiros == [fs[0], fs[2]]
    e = saida.entrega([_res(fs[0]), _res(fs[1], ok=False)], "R")
    assert e.tipo == "pdf" and e.ficheiros == [fs[0]]


def test_entrega_sem_nada_para_entregar(tmp_path):
    f, = _criar(tmp_path, ["a.pdf"])
    with pytest.raises(ValueError):
        saida.entrega([], "R")
    with pytest.raises(ValueError):
        saida.entrega([_res(f, ok=False)], "R")


def test_conteudo_de_um_pdf_grande_sai_aos_bocados(tmp_path):
    f, = _criar(tmp_path, ["g.pdf"], 1_000_000)
    pedacos = list(saida.conteudo_da_entrega(saida.entrega([_res(f)], "R")))
    assert len(pedacos) == 4 and b"".join(pedacos) == f.read_bytes()
