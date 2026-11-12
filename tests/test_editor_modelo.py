"""O modelo de edição do editor (a app Windows usa-o; o site tem o equivalente em TypeScript): histórico, duplicar, ordem, geometria e o que fica debaixo do rato.
Tudo sem janelas; o que se valida e desenha é `core.editor`."""
import pytest

import core
from core import editor, editor_modelo, galeria
from core.editor_modelo import Modelo


class Relogio:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


@pytest.fixture
def m():
    r = Relogio()
    modelo = Modelo(relogio=r)
    modelo.r = r
    return modelo


def tipos(m: Modelo) -> list:
    return [e.tipo for e in m.elementos]


def test_o_modelo_de_partida_e_valido_e_o_motor_aceita_o_template(tmp_path):
    m = Modelo()
    assert m.sem_problemas() and tipos(m).count("numero") == 2
    algarismos = tmp_path / "a.pdf"
    algarismos.write_bytes(galeria.criar_algarismos())
    pdf = tmp_path / "t.pdf"
    pdf.write_bytes(editor.criar_template(m.desenho()))
    assert core.preparar(pdf, algarismos).info.n_numeros == {1: 2}


def test_desfazer_e_refazer_repoem_o_estado_e_um_novo_passo_apaga_o_refazer(m):
    n = len(m.elementos)
    assert not m.pode_desfazer() and not m.pode_refazer()
    a = m.adicionar("retangulo")
    assert len(m.elementos) == n + 1 and m.pode_desfazer()
    assert m.desfazer() and len(m.elementos) == n and m.pode_refazer()
    assert m.refazer() and m.por_id(a) is not None and not m.pode_refazer()
    m.desfazer()
    m.adicionar("linha")                                         # um passo novo: o «refazer» antigo deixa de existir
    assert not m.pode_refazer()
    assert not Modelo().desfazer() and not Modelo().refazer()


def test_alteracoes_seguidas_ao_mesmo_campo_sao_um_so_passo_mas_depois_de_uma_pausa_sao_outro(m):
    t = m.adicionar("texto")
    for letra in ("N", "No", "Nov", "Novo"):
        m.definir(t, texto=letra)
        m.r.t += 0.2
    assert m.por_id(t).texto == "Novo"
    m.desfazer()
    assert m.por_id(t).texto == "Texto"                          # o gesto inteiro de escrever
    m.refazer()
    m.r.t += 5                                                   # pausa: uma alteração nova
    m.definir(t, texto="Outro")
    m.desfazer()
    assert m.por_id(t).texto == "Novo"
    m.mover(t, 5, 0)
    m.mover(t, 5, 0)
    m.mover(t, 5, 0)
    m.desfazer()
    assert m.por_id(t).x == round(m.largura / 2) - 40            # arrastar (vários movimentos) desfaz-se de uma vez


def test_o_historico_tem_um_teto(m):
    for i in range(80):
        m.definir(m.elementos[0].id, espessura=float(i % 7))
        m.r.t += 10
    assert len(m.passado) == editor_modelo.MAX_HISTORICO


def test_apagar_duplicar_e_ordem(m):
    titulo = next(e for e in m.elementos if e.texto == "TÍTULO DA RIFA")
    n = len(m.elementos)
    copia = m.duplicar(titulo.id)
    c = m.por_id(copia)
    assert len(m.elementos) == n + 1 and (c.x, c.y) == (titulo.x + 10, titulo.y + 10) and c.id != titulo.id and m.elementos[-1] is c
    assert m.ordem(copia, 1) is False                             # já está por cima de tudo
    assert m.ordem(copia, -1) and m.elementos[-2] is c
    assert m.ordem(copia, 1) and m.elementos[-1] is c
    assert m.apagar(copia) and m.por_id(copia) is None and not m.apagar(copia)
    m.desfazer()
    assert m.por_id(copia) is not None                           # o desfazer repõe-no com o mesmo id (a seleção sobrevive)


def test_o_teto_de_elementos(m):
    while len(m.elementos) < editor.MAX_ELEMENTOS:
        assert m.adicionar("linha") is not None
    assert m.adicionar("linha") is None and m.duplicar(m.elementos[0].id) is None
    assert m.problemas()["elementos"] is False
    assert m.adicionar("imagem") is None                          # a app Windows não tem imagens (o logótipo vai em «Extras»)


def test_problemas_o_numero_e_os_algarismos_a_mais(m):
    for e in [e for e in m.elementos if e.tipo == "numero"]:
        m.apagar(e.id)
    assert m.problemas()["numero"] and not m.sem_problemas()
    m.adicionar("numero")
    assert m.sem_problemas()
    t = m.adicionar("texto")
    m.definir(t, texto="Tel 0123")
    assert m.problemas()["digitos"] == "Tel 0123" and not m.sem_problemas()


def test_caixa_do_texto_usa_a_largura_exata_na_vera_e_acompanha_o_alinhamento_e_a_rotacao(m):
    t = m.adicionar("texto")
    m.definir(t, texto="Rifa", tamanho=20, x=100, y=50, negrito=True)
    x0, y0, x1, y1 = m.caixa(t)
    largura = editor.largura_do_texto("Rifa", True, 20)
    assert (x0, x1) == pytest.approx((100, 100 + largura)) and y0 == pytest.approx(50 - 16) and y1 == pytest.approx(50 + 4)
    m.definir(t, alinhamento="d")
    assert m.caixa(t)[2] == pytest.approx(100)
    m.definir(t, alinhamento="c", rot=90)
    x0, y0, x1, y1 = m.caixa(t)
    assert (y1 - y0) == pytest.approx(largura) and x0 == pytest.approx(100 - 16) and (y0 + y1) / 2 == pytest.approx(50)


def test_o_que_esta_debaixo_do_rato(m):
    titulo = next(e for e in m.elementos if e.texto == "TÍTULO DA RIFA")
    x0, y0, x1, y1 = m.caixa(titulo.id)
    assert m.elemento_em((x0 + x1) / 2, (y0 + y1) / 2) == titulo.id            # o texto, por cima da moldura
    moldura = m.elementos[0]
    assert m.elemento_em(300, 120) == moldura.id                                # só a moldura (o talão acaba em x=63)
    assert m.elemento_em(-50, -50) is None
    linha = next(e for e in m.elementos if e.tipo == "linha")
    assert m.elemento_em(linha.x + 2, linha.y + 50) == linha.id                  # a linha apanha-se a poucos pt
    assert m.elemento_em(linha.x + 30, linha.y + 50) != linha.id
    por_cima = m.adicionar("retangulo")
    c = m.por_id(por_cima)
    assert m.elemento_em(c.x + 5, c.y + 5) == por_cima                          # o de cima ganha ao de baixo
    for _ in range(len(m.elementos)):                                           # mandado para trás de tudo, a moldura fica por cima dele
        m.ordem(por_cima, -1)
    assert m.elemento_em(c.x + 5, c.y + 5) != por_cima


def test_carregar_um_desenho_do_site_ignora_o_que_nao_conhece_e_apaga_o_historico(m):
    m.adicionar("linha")
    m.carregar({"largura": 300, "altura": 100, "fundo": "#fafafa", "elementos": [
        {"tipo": "numero", "x": 5, "y": 50, "tamanho": 12, "cor": "#000000", "campo_novo": 1},
        {"tipo": "imagem", "x": 0, "y": 0, "w": 5, "h": 5, "dados": "data:..."},          # imagens só existem no site
        {"tipo": "outra-coisa"}]})
    assert tipos(m) == ["numero"] and (m.largura, m.altura) == (300, 100) and not m.pode_desfazer()
    assert m.desenho().largura == 300


def test_pagina_respeita_os_limites_e_entra_no_historico(m):
    m.pagina(largura=5000, altura=1)
    assert (m.largura, m.altura) == (editor.LARGURA_MAX, editor.ALTURA_MIN)
    m.desfazer()
    assert (m.largura, m.altura) == (535, 152)


def test_campos_que_nao_existem_ou_sao_do_sistema_nao_se_mudam(m):
    e = m.elementos[0]
    assert m.definir(e.id, id=999) is False and m.definir(e.id, tipo="texto") is False and m.definir(e.id, nao_existe=1) is False
    assert m.definir(12345, texto="x") is False and m.mover(12345, 1, 1) is False
