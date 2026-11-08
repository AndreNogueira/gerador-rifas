"""M3: marcas de corte nas margens da folha (templates de uma rifa) e o talao (numero duplicado) que o motor ja escrevia."""
import re
from dataclasses import replace

import pytest
from pypdf import PdfReader

import core
from core import escolha_folha
from conftest import erro_de, numeros_pdf

MM = core.MM


@pytest.fixture(scope="module")
def prep1(fx):
    return core.preparar(fx("template_exemplo_1_rifa.pdf"), fx("digitos_exemplo.pdf"))


def _folha(prep, marcas: bool, margem=5):
    p = prep.com_folha("A4", margem)
    return replace(p, disp=replace(p.disp, marcas=marcas))


def _gerar(tmp_path, prep, n=5):
    r = core.gerar(core.Trabalho(tmp_path, "R", 1, n), prep)
    assert r[0].ok
    return r[0].caminho


def _tracos(caminho) -> list:
    conteudo = PdfReader(str(caminho)).pages[0].get_contents().get_data().decode("latin-1")
    return [tuple(float(v) for v in m) for m in re.findall(r"(\S+) (\S+) m (\S+) (\S+) l S", conteudo)]


def test_com_marcas_ha_tracos_so_nas_margens_a_prolongar_os_cortes(tmp_path, prep1):
    p = _folha(prep1, True)
    d = p.disp
    tracos = _tracos(_gerar(tmp_path, p))
    assert len(tracos) == 2 * 2 + 2 * 6                                   # 1 coluna x 5 linhas: 2 cortes verticais (em cima e em baixo) e 6 horizontais (esq. e dir.)
    cw, ch = d.celula.width, d.celula.height
    x0, y0 = d.posicoes[0][0], d.posicoes[0][1]
    x1, y1 = x0 + cw, d.posicoes[-1][1] + ch
    topo, fundo = d.altura - y0, d.altura - y1                            # em coordenadas do PDF (y para cima)
    for ax, ay, bx, by in tracos:
        comprimento = abs(bx - ax) + abs(by - ay)
        assert 1 <= comprimento <= 3.5 * MM + 0.01
        if ax == bx:                                                      # traco vertical: acima ou abaixo da grelha, a prolongar x0 ou x1
            assert min(ay, by) >= topo + 0.99 * MM or max(ay, by) <= fundo - 0.99 * MM
            assert round(ax, 1) in (round(x0, 1), round(x1, 1))
        else:                                                             # horizontal: a esquerda ou a direita
            assert max(ax, bx) <= x0 - 0.99 * MM or min(ax, bx) >= x1 + 0.99 * MM
        assert 0 <= min(ax, bx) and max(ax, bx) <= d.largura and 0 <= min(ay, by) and max(ay, by) <= d.altura     # dentro da folha


def test_sem_marcas_o_pdf_e_igual_ao_de_sempre(tmp_path, prep1):
    a = _gerar(tmp_path / "a", _folha(prep1, False))
    b = _gerar(tmp_path / "b", prep1.com_folha("A4", 5))
    assert _tracos(a) == [] and PdfReader(str(a)).pages[0].get_contents().get_data() == PdfReader(str(b)).pages[0].get_contents().get_data()


def test_marcas_pedem_pelo_menos_3_mm_de_margem(prep1):
    f = lambda m, marcas=True: escolha_folha.escolher_folha(prep1.info, "A4", m, "", marcas)    # noqa: E731
    assert erro_de(f, "2") == ("ErroRifas", "err_marcas", {"min": 3})
    assert f("3").disp.marcas is True and f("0", marcas=False).disp.marcas is False            # sem marcas qualquer margem serve


def test_o_talao_e_o_canhoto_ja_levam_o_mesmo_numero_duas_vezes(tmp_path, prep1):
    assert prep1.info.n_numeros == {1: 2}                                 # o template tem o numero no canhoto e na parte principal
    pagina = numeros_pdf(_gerar(tmp_path, _folha(prep1, True)), 4)[0]
    assert pagina == sorted(f"{n:04d}" for n in range(1, 6) for _ in range(2))


def test_o_template_de_varias_rifas_nao_tem_folha_nem_marcas(fx):
    prep5 = core.preparar(fx("template_exemplo.pdf"), fx("digitos_exemplo.pdf"))
    assert prep5.disp is None and not escolha_folha.tem_folha(prep5.info)
