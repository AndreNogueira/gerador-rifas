"""O português do Brasil (`pt-br`) deriva-se do de Portugal (`core/ptbr.py`): o glossário, os `{parâmetros}` intactos e nenhuma palavra de Portugal a sobrar em nenhum texto."""
import re

import pytest
from core import i18n, ptbr


@pytest.mark.parametrize("pt, br", [
    ("Descarregue o PDF", "Baixe o PDF"), ("Descarregar tudo", "Baixar tudo"), ("Carregue em «Gerar».", "Clique em «Gerar»."),
    ("Carregue os ficheiros de novo.", "Envie os arquivos de novo."), ("os ficheiros que carrega", "os arquivos que envia"),
    ("Copiar ligação", "Copiar link"), ("a ligação do sorteio", "o link do sorteio"), ("Esta ligação já não existe", "Este link já não existe"),
    ("as ligações levam", "os links levam"), ("Verifique a ligação e tente", "Verifique a conexão e tente"), ("Precisa de ligação à internet", "Precisa de conexão com a internet"),
    ("o tipo de ecrã", "o tipo de tela"), ("num ecrã grande", "numa tela grande"), ("no separador", "na aba"),
    ("A gerar «{nome}»", "Gerando «{nome}»"), ("A analisar o template…", "Analisando o template…"), ("Está a gerar PDFs", "Está gerando PDFs"),
    ("Guardar pedido", "Salvar pedido"), ("não guardamos", "não armazenamos"), ("Registe quem leva", "Registre quem leva"),
    ("confirme na câmara municipal", "confirme na prefeitura"), ("o talão e o prémio", "o canhoto e o prêmio"), ("Acerca de…", "Sobre…"),
    ("Pode contactar-nos em {email}.", "Pode nos contatar em {email}."), ("Diga-nos", "Nos diga"), ("a roda do rato", "a roda do mouse"),
    ("no telemóvel", "no celular"), ("a palavra-passe", "a senha"), ("a equipa", "a equipe"), ("a lotaria", "a loteria"),
])
def test_o_glossario(pt, br):
    assert ptbr.derivar(pt) == br


def test_os_parametros_as_etiquetas_e_os_enderecos_nao_se_mexem():
    t = "Veja {ficheiro} e <b>ficheiros</b> em https://exemplo.pt/ficheiros ou `ficheiro.py` (ficheiros)"
    assert ptbr.derivar(t) == "Veja {ficheiro} e <b>arquivos</b> em https://exemplo.pt/ficheiros ou `ficheiro.py` (arquivos)"


def test_maiusculas_e_estruturas_mantem_se():
    assert ptbr.derivar("FICHEIROS") == "ARQUIVOS" and ptbr.derivar("Ficheiro") == "Arquivo"
    assert ptbr.derivar_tudo({"a": ["ficheiro", ("ecrã", 3)], "b": 7}) == {"a": ["arquivo", ("tela", 3)], "b": 7}


def _todos_os_textos_derivados():
    """(origem, texto) de tudo o que se deriva do português: interface, SEO, guias, páginas legais e changelog."""
    from web import changelog, guias, legal_anuncios, legal_medicoes, legal_opiniao, legal_partilhas, seo_textos, textos_legais

    def folhas(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for v in o.values():
                yield from folhas(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                yield from folhas(v)

    for k, v in i18n.TEXTOS["pt-br"].items():
        yield f"interface {k}", re.sub(r"\{[^{}]*\}", " ", v)           # os {parametros} nunca se mexem (e os nomes deles ficam em portugues de Portugal)
    for k, v in seo_textos.CHAVES.items():
        yield f"seo {k}", v["pt-br"]
    for nome in guias.NOMES:
        for t in folhas(guias.DADOS[nome]["pt-br"]):
            yield f"guia {nome}", t
    for nome in textos_legais.NOMES:
        for s in textos_legais.pagina(nome, "pt-br")["seccoes"]:
            for t in [s["titulo"], *s["paragrafos"]]:
                yield f"legal {nome}", t
    for modulo in (legal_anuncios, legal_medicoes, legal_opiniao, legal_partilhas):
        for t in folhas(modulo.TEXTOS["pt-br"]):
            yield f"legal {modulo.__name__}", t
    for e in changelog.entradas("pt-br"):
        for s in e.seccoes:
            for t in [s.titulo, *s.itens]:
                yield f"changelog {e.versao}", t


def test_nenhuma_palavra_de_portugal_sobra_em_nenhum_texto_derivado():
    palavras = [re.escape(p) + ("" if p.endswith("reg") else r"\b") for p in ptbr.LISTA_NEGRA]          # «descarreg» é um radical; as outras são palavras inteiras
    pt = re.compile(r"\b(" + "|".join(palavras) + ")", re.I)
    sobras = [(origem, m.group(0), t[max(0, m.start() - 25):m.end() + 25]) for origem, t in _todos_os_textos_derivados()
              for m in [pt.search(re.sub(r"`[^`]*`", " ", t))] if m]               # o código entre crases (nomes de variáveis) não se traduz
    assert not sobras, sobras[:15]


def test_os_parametros_sao_os_mesmos_do_portugues_em_toda_a_interface():
    marca = re.compile(r"\{(\w+)\}")
    for k, v in i18n.TEXTOS["pt"].items():
        assert set(marca.findall(v)) == set(marca.findall(i18n.TEXTOS["pt-br"][k])), k
