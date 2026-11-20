"""Caracterizacao: modo «uma so rifa no template» - como a rifa enche a folha (_arrumar / disposicao_da_folha)."""
from pathlib import Path

import pytest

import core
from conftest import erro_de
from core import Ret, InfoTemplate

MM = core.MM


def _info(w_mm, h_mm, n_campos=1, celula=True):
    cel = Ret(0, 0, w_mm * MM, h_mm * MM) if celula else None
    return InfoTemplate(Path("x.pdf"), [], n_campos, [], w_mm * MM, h_mm * MM, 1, "0001", "0001", celula=cel)


def _disp(w_mm, h_mm, papel="A4", margem=5, n=None):
    return core.disposicao_da_folha(_info(w_mm, h_mm), papel, margem, n)


@pytest.mark.parametrize("w, h, papel, margem, maximo, rodadas", [
    (189, 54, "A4", 5, 5, 0),
    (54, 189, "A4", 5, 5, 0),            # em pe: a folha vira para paisagem
    (100, 100, "A4", 5, 4, 0),           # 2 x 2: a 3.a linha nao cabe
    (95, 95, "A4", 5, 6, 0),
    (216, 54, "A4", 5, 3, 0),            # 216 mm nao cabe na largura de A4 com 5 mm: a folha roda e cabem 3
    (216, 54, "Letter", 0, 3, 0),
    (216, 54, "A3", 5, 8, 1),            # no A3 uma rifa fica rodada 90 graus
    (190, 50, "A5", 0, 2, 0),
    (10, 10, "A4", 5, 560, 0),
])
def test_maximo_por_folha(w, h, papel, margem, maximo, rodadas):
    d = _disp(w, h, papel, margem)
    assert (d.maximo, d.n, d.rodadas) == (maximo, maximo, rodadas)
    assert d.papel == papel


def test_orientacao_da_folha_e_posicoes_centradas():
    d = _disp(189, 54)
    assert (round(d.largura, 2), round(d.altura, 2)) == (595.28, 841.89)      # retrato
    assert [(round(x, 2), round(y, 2), r) for x, y, r in d.posicoes] == [
        (29.76, 38.27, 0), (29.76, 191.34, 0), (29.76, 344.41, 0), (29.76, 497.48, 0), (29.76, 650.55, 0)]
    d = _disp(54, 189)
    assert (round(d.largura, 2), round(d.altura, 2)) == (841.89, 595.28)      # paisagem
    d = _disp(216, 54, "A4", 5)
    assert (round(d.largura, 2), round(d.altura, 2)) == (841.89, 595.28)


def test_posicoes_em_ordem_de_leitura_por_blocos():
    # 100 x 100 mm em A4 (2 colunas x 2 linhas): primeiro a linha de cima, da esquerda para a direita
    d = _disp(100, 100)
    assert [(round(x, 2), round(y, 2)) for x, y, _ in d.posicoes] == [
        (14.17, 137.48), (297.64, 137.48), (14.17, 420.94), (297.64, 420.94)]


def test_a3_mistura_orientacoes_e_a_numeracao_segue_os_blocos():
    d = _disp(216, 54, "A3", 5)
    assert [p[2] for p in d.posicoes].count(90) == 1
    assert d.posicoes[0][2] == 0                       # o 1.o bloco nao esta rodado
    assert [round(p[1], 2) for p in d.posicoes[:6]] == [59.53, 212.6, 365.67, 518.74, 671.81, 824.88]


def test_n_pedido_e_cortado_ao_intervalo_1_maximo():
    assert _disp(189, 54, n=3).n == 3
    d = _disp(189, 54, n=3)
    assert d.maximo == 5                               # o maximo guarda-se mesmo cortando
    assert _disp(189, 54, n=0).n == 1                  # quirk: 0 (ou negativo) vira 1
    assert _disp(189, 54, n=-4).n == 1
    assert _disp(189, 54, n=99).n == 5                 # acima do maximo: fica no maximo
    todas, cortadas = _disp(189, 54).posicoes, _disp(189, 54, n=3).posicoes
    assert [p[2] for p in cortadas] == [p[2] for p in todas[:3]]            # as primeiras, pela ordem de leitura
    dy = cortadas[0][1] - todas[0][1]
    assert dy > 0 and all(round(cx, 2) == round(ax, 2) and round(cy + dy, 2) == round(ay, 2)
                           for (cx, cy, _), (ax, ay, _) in zip(todas[:3], cortadas, strict=True))  # mesma grelha, só descida (recentrada)


def test_n_pedido_abaixo_do_maximo_fica_recentrado_margens_iguais():
    # truncar sem recentrar (bug corrigido) deixava toda a folga do lado de baixo/direito: a guilhotina a direito
    # deixava de servir para separar cada rifa (o espaço no topo e no fundo da folha tinham de ficar iguais)
    for n in (1, 2, 3, 4, 5):
        d = _disp(189, 54, n=n)
        cw, ch = d.celula.width, d.celula.height
        caixas = [(x, y, x + (cw if r == 0 else ch), y + (ch if r == 0 else cw)) for x, y, r in d.posicoes]
        x0, y0 = min(c[0] for c in caixas), min(c[1] for c in caixas)
        x1, y1 = max(c[2] for c in caixas), max(c[3] for c in caixas)
        assert round(y0, 2) == round(d.altura - y1, 2), f"n={n}: margem de cima e de baixo diferentes"
        assert round(x0, 2) == round(d.largura - x1, 2), f"n={n}: margem da esquerda e da direita diferentes"


def test_margem_negativa_vale_zero_e_margem_em_pontos():
    d = _disp(189, 54, margem=-5)
    assert d.margem == 0.0 and d.maximo == 5
    assert _disp(189, 54, margem=5).margem == pytest.approx(5 * MM)
    assert _disp(190, 50, "A5", 0).margem == 0.0


def test_a_margem_muda_o_maximo():
    assert _disp(216, 54, "A4", 0).maximo == 3          # sem margem tambem 3 (rodada) em A4
    assert _disp(189, 54, "A4", 5).maximo == 5
    assert _disp(189, 54, "A4", 12).maximo == 3         # com margem 12 mm ja nao cabem 5 (a folha passa a paisagem)


def test_erros_da_folha():
    assert erro_de(core.disposicao_da_folha, _info(300, 300), "A4", 5) == (
        "ErroRifas", "err_rifa_grande", {"w": "300", "h": "300", "papel": "A4", "margem": "5"})
    assert erro_de(core.disposicao_da_folha, _info(189, 54, n_campos=5), "A4", 5) == ("ErroRifas", "err_folha_varias", {})
    assert erro_de(core.disposicao_da_folha, _info(189, 54, celula=False), "A4", 5) == ("ErroRifas", "err_folha_varias", {})
    # margem enorme: nao sobra area
    assert erro_de(core.disposicao_da_folha, _info(10, 10), "A4", 200)[1] == "err_rifa_grande"
    # papel desconhecido: quirk, rebenta com KeyError (a interface so deixa escolher os 5 papeis)
    with pytest.raises(KeyError):
        core.disposicao_da_folha(_info(189, 54), "B5", 5)


def test_arrumar_dois_blocos():
    assert core._arrumar(100, 100, 60, 40) == [(0, 0, 0), (0, 40, 0), (60, 0, 90)]
    assert core._arrumar(10, 10, 60, 40) == []
    assert core._arrumar(60, 40, 60, 40) == [(0, 0, 0)]


def test_disposicao_com_o_template_de_exemplo(fx):
    info = core.analisar_template(fx("template_exemplo_1_rifa.pdf"))
    resultado = {}
    for papel, margem in (("A4", 5), ("A3", 5), ("Letter", 0), ("A4", 12)):
        d = core.disposicao_da_folha(info, papel, margem)
        resultado[(papel, margem)] = (d.maximo, d.rodadas, round(d.largura, 2), round(d.altura, 2))
    assert resultado == {("A4", 5): (5, 0, 595.28, 841.89), ("A3", 5): (10, 0, 1190.55, 841.89),
                         ("Letter", 0): (5, 0, 612.0, 792.0), ("A4", 12): (3, 0, 841.89, 595.28)}
    d = core.disposicao_da_folha(info, "A4", 5)
    assert d.origem == "pagina" and d.celula == info.celula
