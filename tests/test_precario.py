"""O preçário (`core/precario.py`): o PDF sai em todas as línguas e temas, com os preços na moeda certa, o ajuste de letra e de páginas, e recusa o que o PDF não consegue escrever."""
import io

import core
import pytest
from core import galeria, i18n, moeda, precario, precario_catalogo as cat
from core.motor import ErroRifas
from core.precario import Linha, Precario
from pypdf import PdfReader

LINGUAS = list(i18n.LINGUAS)


def texto_do_pdf(pdf: bytes) -> str:
    return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(pdf)).pages)


def com_precos(p: Precario, base: int = 1500, passo: int = 250) -> Precario:
    return Precario(**{**p.__dict__, "linhas": tuple(Linha(artigo=ln.artigo, nome=ln.nome, categoria=ln.categoria, emoji=ln.emoji, preco=base + passo * (i % 5)) for i, ln in enumerate(p.linhas))})


def test_um_precario_simples_leva_o_titulo_os_artigos_e_os_precos():
    p = com_precos(precario.de_ocasiao("santos_populares", "pt", subtitulo="Associação Exemplo", rodape="Obrigado!"))
    pdf = precario.criar_pdf(p)
    t = texto_do_pdf(pdf)
    assert pdf.startswith(b"%PDF") and len(PdfReader(io.BytesIO(pdf)).pages) == 1
    for esperado in ("Santos Populares", "Associação Exemplo", "Obrigado!", "Bebidas", "Sardinha assada", "Caldo verde", "1,50 €", "1,75 €"):
        assert esperado in t, esperado
    assert core.png_de_pagina(pdf, 60)[:8] == b"\x89PNG\r\n\x1a\n"                    # e a pré-visualização desenha-se


@pytest.mark.parametrize("lg", LINGUAS)
def test_sai_em_todas_as_linguas_com_a_moeda_do_pais(lg):
    p = com_precos(precario.de_ocasiao("festa_popular", lg), 1500)
    pdf = precario.criar_pdf(p)
    assert len(PdfReader(io.BytesIO(pdf)).pages) == 1
    esperado = moeda.formatar(1500, p.moeda, lg).replace(" ", "").replace("\xa0", "")
    assert esperado in texto_do_pdf(pdf).replace(" ", "").replace("\xa0", ""), (lg, esperado)       # o preço escreve-se na moeda e no formato da língua


@pytest.mark.parametrize("desenho", list(precario.POR_ID))
def test_sai_com_cada_um_dos_25_desenhos(desenho):
    p = com_precos(Precario(linhas=tuple(Linha(artigo=a) for a in ("agua", "cerveja", "bolo", "pizza", "gelado", "tiro_ao_alvo")), titulo="Festa", desenho=desenho))
    assert len(PdfReader(io.BytesIO(precario.criar_pdf(p))).pages) == 1


@pytest.mark.parametrize("formato", ["A5", "A4", "A3"])
@pytest.mark.parametrize("orientacao", ["vertical", "horizontal"])
@pytest.mark.parametrize("colunas", [0, 1, 2, 3])
def test_formatos_orientacoes_e_colunas(formato, orientacao, colunas):
    p = com_precos(precario.de_ocasiao("natal", "pt", formato=formato, orientacao=orientacao, colunas=colunas))
    leitor = PdfReader(io.BytesIO(precario.criar_pdf(p)))
    larg, alt = (float(leitor.pages[0].mediabox.width), float(leitor.pages[0].mediabox.height))
    esperado = precario.FORMATOS[formato] if orientacao == "vertical" else precario.FORMATOS[formato][::-1]
    assert (round(larg), round(alt)) == (round(esperado[0]), round(esperado[1]))


def test_com_muitos_artigos_passa_a_mais_paginas_sem_perder_nenhum():
    todos = tuple(Linha(artigo=a.id, preco=1000 + i * 10) for i, a in enumerate(cat.artigos_da_lingua("pt")))[:70]
    p = Precario(linhas=todos, titulo="Tudo", rodape="rodapé", colunas=1)
    leitor = PdfReader(io.BytesIO(precario.criar_pdf(p)))
    assert 2 <= len(leitor.pages) <= precario.MAX_PAGINAS
    t = "\n".join(pg.extract_text() or "" for pg in leitor.pages)
    for ln in todos:
        assert cat.nome_imprimivel(cat.ARTIGOS[ln.artigo], "pt").split()[0] in t, ln.artigo
    assert "1/" in t and "2/" in t


def test_com_poucos_artigos_cabe_numa_so_folha():
    p = com_precos(Precario(linhas=(Linha(artigo="agua"), Linha(artigo="cerveja")), titulo="Bar"))
    assert len(PdfReader(io.BytesIO(precario.criar_pdf(p))).pages) == 1


def test_o_preco_em_branco_deixa_um_traco_e_com_preco_escreve_se():
    sem = texto_do_pdf(precario.criar_pdf(Precario(linhas=(Linha(artigo="agua"),), titulo="X")))
    assert "€" not in sem and "Água" in sem
    com = texto_do_pdf(precario.criar_pdf(Precario(linhas=(Linha(artigo="agua", preco=0),), titulo="X")))
    assert "0,00 €" in com


def test_moeda_inventada_e_textos_livres_com_imagem_e_categoria():
    p = Precario(linhas=(Linha(nome="Bolo da avó", preco=2000, categoria="doces", emoji="1f370"), Linha(artigo="agua", nome="Água fresca", preco=1000), Linha(nome="Sem imagem", preco=3000)),
                 titulo="Quermesse", moeda=moeda.MoedaInventada("fichas"))
    t = texto_do_pdf(precario.criar_pdf(p))
    for esperado in ("Bolo da avó", "2 fichas", "Água fresca", "1 fichas", "Sem imagem", "3 fichas", "Doces", "Outros"):
        assert esperado in t, esperado


def test_sem_imagens_nao_ha_imagens_no_pdf():
    com = precario.criar_pdf(com_precos(precario.de_ocasiao("natal", "pt", imagens=True)))
    sem = precario.criar_pdf(com_precos(precario.de_ocasiao("natal", "pt", imagens=False)))
    assert len(sem) < len(com) - 20_000
    assert not any(pg.images for pg in PdfReader(io.BytesIO(sem)).pages)


def test_o_mesmo_precario_da_os_mesmos_bytes():
    p = com_precos(precario.de_ocasiao("natal", "en"))
    assert precario.criar_pdf(p) == precario.criar_pdf(p)


@pytest.mark.parametrize("campos, chave", [
    (dict(titulo="x" * 41), "err_precario_texto"), (dict(subtitulo="y" * 71), "err_precario_texto"), (dict(rodape="z" * 121), "err_precario_texto"),
    (dict(titulo="नमस्ते"), "err_precario_texto"), (dict(titulo="emoji \U0001F600"), "err_precario_texto"),
    (dict(desenho="nao_existe"), "err_precario_texto"), (dict(formato="A0"), "err_precario_texto"), (dict(colunas=4), "err_precario_texto"), (dict(lingua="xx"), "err_precario_texto"),
    (dict(linhas=()), "err_precario_linhas"), (dict(linhas=(Linha(nome="  "),)), "err_precario_linhas"), (dict(linhas=tuple(Linha(nome=f"a{i}") for i in range(81))), "err_precario_linhas"),
    (dict(linhas=(Linha(artigo="nao_existe"),)), "err_precario_texto"), (dict(linhas=(Linha(nome="ok", preco=-1),)), "err_precario_texto"),
    (dict(linhas=(Linha(nome="ok", preco=moeda.MAX_VALOR + 1),)), "err_precario_texto"), (dict(linhas=(Linha(nome="ok", emoji="zzzz"),)), "err_precario_texto"),
    (dict(linhas=(Linha(nome="ok", categoria="nada"),)), "err_precario_texto"), (dict(linhas=(Linha(nome="चाय"),)), "err_precario_texto"),
    (dict(moeda=moeda.MoedaInventada("fichas2")), "err_precario_texto"),
])
def test_recusa_o_que_nao_serve_com_uma_mensagem_traduzida(campos, chave):
    base = dict(linhas=(Linha(artigo="agua"),), titulo="T")
    base.update(campos)
    with pytest.raises(ErroRifas) as e:
        precario.criar_pdf(Precario(**base))
    assert e.value.chave == chave
    for lg in LINGUAS:
        assert "{" not in e.value.em(lg)                                      # os {parâmetros} vieram todos preenchidos


def test_textos_com_acentos_chineses_e_cirilicos_servem():
    for titulo, nome in (("Çà é ñ", "Pão"), ("Праздник", "Пиво"), ("お祭り", "ビール"), ("축제", "맥주"), ("Φεστιβάλ", "Μπύρα"), ("Lễ hội", "Bia")):
        assert len(PdfReader(io.BytesIO(precario.criar_pdf(Precario(linhas=(Linha(nome=nome, preco=1000),), titulo=titulo)))).pages) == 1


# ------------------------------------------------------------------ de e para dicionários
def test_de_dict_le_precos_escritos_na_lingua_e_milesimos_e_da_o_mesmo_de_volta():
    d = {"titulo": "Festa", "desenho": "natal", "colunas": 2, "moeda": {"codigo": "BRL"}, "lingua": "pt-br",
         "linhas": [{"artigo": "coxinha", "preco": "5,50"}, {"nome": "Bolo", "categoria": "doces", "emoji": "1f370", "preco": 3000}, {"artigo": "agua"}]}
    p = precario.de_dict(d)
    assert [ln.preco for ln in p.linhas] == [5500, 3000, None] and p.moeda.codigo == "BRL" and p.colunas == 2 and p.lingua == "pt-br"
    assert precario.de_dict(precario.para_dict(p)) == p and precario.para_dict(p)["linhas"][0]["preco"] == 5500
    assert "R$ 5,50" in texto_do_pdf(precario.criar_pdf(p))


def test_de_dict_moeda_por_omissao_inventada_e_a_lingua_do_pedido_ganha():
    base = {"linhas": [{"artigo": "agua", "preco": "1"}]}
    assert precario.de_dict(base, "pt-br").moeda.codigo == "BRL" and precario.de_dict(base, "ja").moeda.codigo == "JPY" and precario.de_dict(base).moeda.codigo == "EUR"
    ficha = precario.de_dict({**base, "moeda": {"nome": "fichas", "antes": True, "decimais": 1}})
    assert ficha.moeda == moeda.MoedaInventada("fichas", True, 1) and precario.de_dict(precario.para_dict(ficha)) == ficha
    assert precario.de_dict({**base, "lingua": "en"}, "pt").lingua == "pt"


@pytest.mark.parametrize("d", [None, [], "x", {"titulo": 3}, {"linhas": "x"}, {"linhas": [1]}, {"linhas": [{"preco": True}]}, {"linhas": [{"preco": "abc"}]}, {"linhas": [{"preco": 1.5}]},
                               {"moeda": "EUR"}, {"moeda": {"codigo": "XXX"}}, {"moeda": {"nome": "f", "decimais": "2"}}, {"colunas": "2"}, {"colunas": True}, {"linhas": [{"artigo": 5}]}])
def test_de_dict_recusa_tipos_errados_com_erro_traduzido(d):
    with pytest.raises(ErroRifas) as e:
        precario.de_dict(d)
    assert e.value.chave in ("err_precario_texto", "err_precario_linhas")


# ------------------------------------------------------------------ ficheiro .precario
def _exemplo() -> Precario:
    return Precario(linhas=[Linha("agua", "Água", 1500), Linha("", "Bolo da avó", None)], titulo="Festa", lingua="pt")


def test_o_ficheiro_do_precario_ida_e_volta():
    p = _exemplo()
    outro = precario.de_bytes(precario.para_bytes(p))
    assert precario.para_dict(outro) == precario.para_dict(p)


@pytest.mark.parametrize("dados", [b"", b"nao e json", b"[]", b'{"formato": "outro", "precario": {}}', b"x" * (precario.MAX_BYTES + 1)])
def test_ficheiro_estragado_ou_alheio_e_recusado(dados):
    with pytest.raises(ErroRifas) as e:
        precario.de_bytes(dados)
    assert e.value.chave == "err_pedido_ficheiro"


# ------------------------------------------------------------------ o quadro negro
def test_o_quadro_negro_e_um_desenho_so_do_preçário_com_papel_escuro_e_texto_a_giz():
    assert "quadro" in precario.POR_ID and "quadro" not in galeria.POR_ID                 # a galeria de rifas fica como estava
    d = precario.POR_ID["quadro"]
    assert precario._escuro(d) and not precario._escuro(galeria.POR_ID["quermesse"])
    assert precario._cor_texto(d)[0] > 0.9 and precario._cor_texto(galeria.POR_ID["quermesse"])[0] < 0.2     # giz claro num, quase preto noutro
    assert precario._cor_realce(d) == d.destaque and precario._cor_realce(galeria.POR_ID["quermesse"]) == galeria.POR_ID["quermesse"].principal


def test_o_quadro_negro_pinta_o_fundo_escuro_e_escreve_o_texto_claro():
    import pypdfium2 as pdfium
    p = com_precos(Precario(linhas=tuple(Linha(artigo=a) for a in ("agua", "cerveja")), titulo="Festa", desenho="quadro", imagens=False))
    doc = pdfium.PdfDocument(io.BytesIO(precario.criar_pdf(p)))
    try:
        im = doc[0].render(scale=0.3).to_pil().convert("RGB")
    finally:
        doc.close()
    w, h = im.size
    r, g, b = im.getpixel((w // 2, int(h * 0.62)))                                         # o miolo do quadro, longe do texto
    assert max(r, g, b) < 80, (r, g, b)


# ------------------------------------------------------------------ cartões de mesa (A6, 4 por folha A4)
def _cartoes(n: int = 6, **kw) -> Precario:
    return com_precos(Precario(linhas=tuple(Linha(artigo=a) for a in list(cat.ARTIGOS)[:n]),
                               titulo="Festa", formato=precario.CARTOES, **kw))


def test_os_cartoes_de_mesa_sao_uma_folha_a4_com_quatro_cartoes_e_guias_de_corte():
    leitor = PdfReader(io.BytesIO(precario.criar_pdf(_cartoes())))
    assert len(leitor.pages) == 1 and [round(float(x)) for x in leitor.pages[0].mediabox[2:]] == [595, 842]
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(io.BytesIO(precario.criar_pdf(_cartoes())))
    try:
        tp = doc[0].get_textpage()
        texto = tp.get_text_range()
        tp.close()
    finally:
        doc.close()
    assert texto.count("Festa") == 4                                                       # o titulo do cartao aparece quatro vezes


def test_o_cartao_e_sempre_de_pe_e_de_uma_so_face_e_aceita_ate_12_artigos():
    assert len(PdfReader(io.BytesIO(precario.criar_pdf(_cartoes(12, orientacao="horizontal")))).pages) == 1
    with pytest.raises(ErroRifas) as e:
        precario.criar_pdf(Precario(linhas=tuple(Linha(nome=f"Artigo {i}") for i in range(precario.MAX_CARTOES + 1)), formato=precario.CARTOES))
    assert e.value.chave == "err_precario_linhas" and e.value.params["max"] == precario.MAX_CARTOES


def test_o_formato_dos_cartoes_viaja_na_api_e_no_ficheiro():
    p = _cartoes()
    assert precario.de_dict(precario.para_dict(p)).formato == precario.CARTOES
    assert precario.de_bytes(precario.para_bytes(p)).formato == precario.CARTOES
    assert precario.CARTOES in precario.FORMATOS and list(precario.FORMATOS)[-1] == precario.CARTOES      # no fim da lista: A5, A4, A3 primeiro


# ------------------------------------------------------------------ dois tamanhos (dois preços por artigo)
def _tamanhos(**kw) -> Precario:
    linhas = (Linha("agua", preco=1000, preco2=1800), Linha("cerveja", preco=1500), Linha("", "Bolo da avó", preco2=2500))
    return Precario(linhas=linhas, titulo="Festa", tamanhos=True, rotulos=("Pequena", "Grande"), **kw)


def test_com_dois_tamanhos_saem_os_rotulos_e_os_dois_precos():
    texto = texto_do_pdf(precario.criar_pdf(_tamanhos())).replace("\xa0", " ")
    assert "Pequena" in texto and "Grande" in texto
    for esperado in ("1,00", "1,80", "1,50", "2,50"):
        assert esperado in texto, esperado
    sem = texto_do_pdf(precario.criar_pdf(Precario(linhas=_tamanhos().linhas, titulo="Festa")))
    assert "Pequena" not in sem and "Grande" not in sem and "1,80" not in sem.replace("\xa0", " ")     # sem `tamanhos` o segundo preço nem aparece


@pytest.mark.parametrize("formato", ["A5", "A4", "A3", "A6x4"])
def test_os_dois_tamanhos_cabem_em_todos_os_formatos_e_com_a_moeda_inventada(formato):
    p = _tamanhos(formato=formato, moeda=moeda.MoedaInventada("fichas", False, 0))
    assert len(PdfReader(io.BytesIO(precario.criar_pdf(p))).pages) >= 1


def test_os_tamanhos_viajam_no_dicionario_e_no_ficheiro():
    p = _tamanhos()
    assert precario.de_dict(precario.para_dict(p)) == p
    assert precario.de_bytes(precario.para_bytes(p)) == p
    assert precario.de_dict({"linhas": [{"artigo": "agua", "preco": "1,5", "preco2": "2,5"}], "tamanhos": True}, "pt").linhas[0].preco2 == 2500
    assert precario.de_dict({"linhas": []}, "pt").rotulos == ("P", "G") and precario.de_dict({"linhas": []}, "pt").tamanhos is False


@pytest.mark.parametrize("rotulos", [("", "G"), ("P", "   "), ("x" * 11, "G"), ("P",), ("P", "G", "M")])
def test_rotulos_invalidos_so_importam_com_tamanhos(rotulos):
    base = {"linhas": [{"artigo": "agua"}], "rotulos": list(rotulos)}
    if len(rotulos) != 2 or len(rotulos[0]) > 10:
        with pytest.raises(ErroRifas):
            precario.criar_pdf(precario.de_dict({**base, "tamanhos": True}, "pt"))
        return
    with pytest.raises(ErroRifas):
        precario.criar_pdf(precario.de_dict({**base, "tamanhos": True}, "pt"))                 # vazio com tamanhos: recusado
    assert precario.criar_pdf(precario.de_dict({**base, "tamanhos": False}, "pt")).startswith(b"%PDF")    # sem tamanhos os rótulos nem se usam
