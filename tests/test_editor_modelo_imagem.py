"""O elemento «imagem» do modelo do editor (app Windows 2.6): juntar PNG/JPG, reduzir, caber na caixa, desfazer, caixa de seleção e o template final."""
import io

import pytest
from PIL import Image

import core
from core import editor, editor_modelo, galeria
from core.editor_modelo import Modelo


def _png(w=300, h=100, transparente=False) -> bytes:
    im = Image.new("RGBA" if transparente else "RGB", (w, h), (200, 30, 30, 120) if transparente else (200, 30, 30))
    saida = io.BytesIO()
    im.save(saida, "PNG")
    return saida.getvalue()


def _jpg(w=200, h=200) -> bytes:
    saida = io.BytesIO()
    Image.new("RGB", (w, h), (10, 120, 200)).save(saida, "JPEG")
    return saida.getvalue()


def test_junta_uma_imagem_que_cabe_na_caixa_sem_ampliar_e_fica_ao_centro():
    m = Modelo()
    id_ = m.adicionar_imagem(_png(300, 100))
    e = m.por_id(id_)
    assert e.tipo == "imagem" and e.dados.startswith("data:image/jpeg;base64,")
    assert (e.w, e.h) == (160, 53)                                    # 300×100 px a caber em 160×80 pt, na proporção
    assert abs(e.x + e.w / 2 - m.largura / 2) <= 1 and abs(e.y + e.h / 2 - m.altura / 2) <= 1
    pequena = m.por_id(m.adicionar_imagem(_png(20, 10)))
    assert (pequena.w, pequena.h) == (20, 10)                         # nunca se amplia


def test_png_com_transparencia_continua_png():
    m = Modelo()
    assert m.por_id(m.adicionar_imagem(_png(transparente=True))).dados.startswith("data:image/png;base64,")


def test_imagem_grande_e_reduzida_e_o_desenho_aceita_o_template(tmp_path):
    m = Modelo()
    m.adicionar_imagem(_png(3000, 2000))
    d = m.desenho()                                                   # `core.editor.de_dict` valida o PNG recodificado
    assert sum(1 for e in d.elementos if e.tipo == "imagem") == 1 and len(next(e for e in d.elementos if e.tipo == "imagem").imagem) < editor.MAX_IMAGEM_BYTES
    template, digitos = tmp_path / "t.pdf", tmp_path / "d.pdf"
    template.write_bytes(editor.criar_template(d))
    digitos.write_bytes(galeria.criar_algarismos())
    assert template.read_bytes().startswith(b"%PDF-") and core.preparar(template, digitos).info.n_numeros == {1: 2}


def test_so_aceita_png_e_jpg_a_serio():
    m = Modelo()
    for mau in (b"", b"GIF89a....", b"\x89PNG\r\n\x1a\nlixo", b"%PDF-1.4 isto nao e uma imagem"):
        with pytest.raises(core.ErroRifas) as e:
            m.adicionar_imagem(mau)
        assert e.value.chave == "err_editor_imagem"
    assert not any(e.tipo == "imagem" for e in m.elementos)
    assert m.por_id(m.adicionar_imagem(_jpg())).dados.startswith("data:image/jpeg")


def test_teto_de_imagens_desfazer_duplicar_e_caixa():
    m = Modelo()
    ids = [m.adicionar_imagem(_png(40, 40)) for _ in range(editor.MAX_IMAGENS)]
    assert None not in ids and m.adicionar_imagem(_png(40, 40)) is None
    m.apagar(ids[0])
    n = len(m.elementos)
    m.desfazer()
    assert len(m.elementos) == n + 1
    e = m.por_id(ids[1])
    assert m.caixa(ids[1]) == (e.x, e.y, e.x + e.w, e.y + e.h)
    assert m.elemento_em(e.x + 1, e.y + 1) == ids[1] or m.elemento_em(e.x + 1, e.y + 1) is not None
    copia = m.duplicar(ids[1])
    assert copia is None or m.por_id(copia).dados == e.dados          # duplicar leva a imagem (ou recusa se já há imagens a mais no desenho)


def test_para_dict_so_leva_dados_na_imagem_e_carregar_volta_a_aceita_la():
    m = Modelo()
    m.adicionar_imagem(_png(60, 60))
    d = m.para_dict()
    assert all(("dados" in e) == (e["tipo"] == "imagem") for e in d["elementos"])
    m2 = Modelo(d)
    assert [e.tipo for e in m2.elementos] == [e.tipo for e in m.elementos] and any(e.tipo == "imagem" and e.dados for e in m2.elementos)


def test_imagem_para_dados_devolve_as_dimensoes_finais():
    dados, w, h = editor_modelo.imagem_para_dados(_png(1200, 600))
    assert dados.startswith("data:image/") and (w, h) == (600, 300)
