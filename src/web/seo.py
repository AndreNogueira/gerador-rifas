"""SEO: o `<head>` e um resumo estatico do conteudo de cada pagina, `robots.txt` e `sitemap.xml`.

A webapp e uma SPA: o HTML que o servidor entrega estaria vazio (`<div id="raiz">`) para quem nao corre JavaScript (redes sociais,
muitos motores de pesquisa, partilhas por mensagem). Por isso o servidor injeta no `index.html` compilado, por rota conhecida:
 - no `<head>` (marcador `<!--seo:cabecalho-->`): titulo, descricao, canonico, robots, Open Graph, Twitter e JSON-LD;
 - no corpo (marcador `<!--seo:corpo-->` dentro de `#raiz`): texto real da pagina (o React substitui-o ao arrancar; o CSS esconde-o
   visualmente: `.seo-estatico`).
Cada lingua tem o seu URL: o portugues sem prefixo (`/`, `/tutorial`) e as outras 17 com ele (`/en`, `/en/tutorial`, ...). O servidor entrega o
HTML na lingua do URL (titulo, descricao, texto, `<html lang>`, canonico, `og:locale`) com `hreflang` para as 18 e `x-default` = portugues; o sitemap
lista todas. Um URL sem prefixo e SEMPRE portugues (nao se redireciona pelo `Accept-Language`: o robo veria so uma lingua); a interface, no
browser, passa para a lingua escolhida e poe o prefixo no URL. Sem URL publico configurado (`PUBLIC_URL`) o canonico sai do pedido.
"""
from __future__ import annotations

import html
import json
import re
from collections.abc import Callable
from dataclasses import dataclass

from core import i18n, tutorial
from fastapi import Request

from . import VERSAO, changelog, config, textos_legais
from .seo_textos import LOCALE_OG, texto

NOME = "Gerador de Rifas"           # o nome em portugues; em cada lingua vem de `app_nome` (ver `_app`)
IMAGEM = "/og-imagem.png"           # 1200x630, em frontend/public
MARCADOR_CABECALHO = "<!--seo:cabecalho-->"
MARCADOR_CORPO = "<!--seo:corpo-->"
LINGUAS_URL = tuple(lg for lg in i18n.LINGUAS if lg != "pt")      # as que tem prefixo no URL (/en/..); o portugues e o URL sem prefixo


# ------------------------------------------------------------------ URLs por lingua
def caminho_na_lingua(caminho: str, lingua: str) -> str:
    """`/tutorial` -> `/en/tutorial`; a pagina inicial de uma lingua com prefixo e `/en` (sem barra final); o portugues nao leva prefixo."""
    if lingua == "pt":
        return caminho
    return f"/{lingua}" if caminho == "/" else f"/{lingua}{caminho}"


def separar_lingua(caminho: str) -> tuple[str, str]:
    """(lingua, resto) do caminho de um pedido (sem a barra inicial): `en/tutorial` -> ('en', 'tutorial'); sem prefixo -> ('pt', caminho).
    `pt/...` devolve ('pt-prefixado', resto): quem chama redireciona para o URL sem prefixo (um so URL por pagina)."""
    primeiro, _, resto = caminho.partition("/")
    if primeiro in LINGUAS_URL:
        return primeiro, resto
    if primeiro == "pt":
        return "pt-prefixado", resto
    return "pt", caminho


def _app(lingua: str) -> str:
    return i18n.traduzir("app_nome", lingua)


def _l(lingua: str, caminho: str) -> str:
    return html.escape(caminho_na_lingua(caminho, lingua), quote=True)


def _voltar(lingua: str) -> str:
    return f'<p><a href="{_l(lingua, "/")}">{html.escape(texto("voltar", lingua, app=_app(lingua)))}</a></p>'


def _paragrafos(texto_: str) -> str:
    return "".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in texto_.split("\n\n") if p.strip())


def _nome_pagina(chave: str) -> Callable[[str], str]:
    return lambda lg: i18n.traduzir(chave, lg).rstrip("…")


def _corpo_inicio(lg: str) -> str:
    with i18n.com_lingua(lg):
        topicos = tutorial.lista_de_topicos("web")
    passos = "".join(f"<li><strong>{html.escape(topicos[i][1])}.</strong> {html.escape(topicos[i][2].split(chr(10) * 2)[0])}</li>" for i in (1, 3, 4, 5))
    return (
        f"<h1>{html.escape(_app(lg))}</h1><p>{html.escape(texto('intro', lg))}</p>"
        f"<h2>{html.escape(texto('como', lg))}</h2><ol>{passos}</ol>"
        f"<p>{html.escape(texto('ficheiros', lg, min=config.validade_min()))}</p>"
        f'<nav><a href="{_l(lg, "/tutorial")}">{html.escape(_nome_pagina("tut_titulo")(lg))}</a> '
        f'<a href="{_l(lg, "/video")}">{html.escape(_nome_pagina("mi_video")(lg))}</a> '
        f'<a href="{_l(lg, "/sobre")}">{html.escape(_nome_pagina("mi_sobre")(lg))}</a></nav>'
    )


def _corpo_tutorial(lg: str) -> str:
    with i18n.com_lingua(lg):
        topicos = tutorial.lista_de_topicos("web")
    secoes = "".join(f"<section><h2>{html.escape(titulo)}</h2>{_paragrafos(txt)}</section>" for _, titulo, txt, _ in topicos)
    return f"<h1>{html.escape(_nome_pagina('tut_titulo')(lg))}</h1><p>{html.escape(texto('d_tutorial', lg))}</p>{secoes}{_voltar(lg)}"


def _corpo_video(lg: str) -> str:
    video = "tutorial_pt.mp4" if lg == "pt" else "tutorial_en.mp4"
    return (
        f"<h1>{html.escape(_nome_pagina('mi_video')(lg))}</h1><p>{html.escape(texto('d_video', lg))}</p>"
        f'<p><a href="/videos/{video}">{html.escape(_nome_pagina("mi_video")(lg))} (MP4)</a></p>{_voltar(lg)}'
    )


def _corpo_sobre(lg: str) -> str:
    resumo = "\n\n".join(i18n.traduzir("sobre_texto", lg, app=_app(lg), versao=VERSAO).split("\n\n")[:2])
    return f"<h1>{html.escape(_nome_pagina('mi_sobre')(lg))}</h1>{_paragrafos(resumo)}{_voltar(lg)}"


def _corpo_sorteio(lg: str) -> str:
    return f"<h1>{html.escape(_nome_pagina('web_sorteio')(lg))}</h1><p>{html.escape(texto('d_sorteio', lg))}</p>{_voltar(lg)}"


def _corpo_editor(lg: str) -> str:
    return f"<h1>{html.escape(_nome_pagina('web_editor')(lg))}</h1><p>{html.escape(texto('d_editor', lg))}</p>{_voltar(lg)}"


def _corpo_changelog(lg: str) -> str:
    blocos = []
    for e in list(changelog.entradas(lg))[:6]:
        itens = "".join(f"<h3>{html.escape(s.titulo)}</h3><ul>{''.join(f'<li>{html.escape(i)}</li>' for i in s.itens)}</ul>" for s in e.seccoes)
        blocos.append(f"<section><h2>{html.escape(e.versao)} ({html.escape(e.data)})</h2>{itens}</section>")
    return f"<h1>Changelog</h1><p>{html.escape(texto('d_changelog', lg))}</p>{''.join(blocos)}{_voltar(lg)}"


def _corpo_texto(nome: str) -> Callable[[str], str]:
    def corpo(lg: str) -> str:
        d = textos_legais.pagina(nome, lg)
        aviso = f"<p><em>{html.escape(d['aviso'])}</em></p>" if d["aviso"] else ""
        secoes = "".join(f"<section><h2>{html.escape(s['titulo'])}</h2>{''.join(f'<p>{html.escape(p)}</p>' for p in s['paragrafos'])}</section>"
                         for s in d["seccoes"])
        return f'<h1>{html.escape(d["titulo"])}</h1>{aviso}{secoes}{_voltar(lg)}'
    return corpo


@dataclass(frozen=True)
class Pagina:
    caminho: str
    descricao_chave: str                       # a chave de `seo_textos` (d_<...>)
    corpo: Callable[[str], str]                # (lingua) -> HTML
    nome: Callable[[str], str] | None = None   # o nome da pagina na lingua, para o titulo «<nome> | <app>» (None: usa `t_inicio`)
    indexavel: bool = True
    no_mapa: bool = True
    titulo_fixo: str = ""                      # paginas sem texto proprio (painel, 404): titulo e descricao fixos
    descricao_fixa: str = ""

    def titulo(self, lg: str = "pt") -> str:                 # ate ~65 caracteres
        if self.titulo_fixo:
            return self.titulo_fixo
        if self.nome is None:
            return texto("t_inicio", lg, app=_app(lg))
        return f"{self.nome(lg)} | {_app(lg)}"

    def descricao(self, lg: str = "pt") -> str:              # ate ~160 caracteres
        return self.descricao_fixa or texto(self.descricao_chave, lg)


ROTAS: dict[str, Pagina] = {p.caminho: p for p in (
    Pagina("/", "d_inicio", _corpo_inicio),
    Pagina("/tutorial", "d_tutorial", _corpo_tutorial, _nome_pagina("tut_titulo")),
    Pagina("/video", "d_video", _corpo_video, _nome_pagina("mi_video")),
    Pagina("/sobre", "d_sobre", _corpo_sobre, _nome_pagina("mi_sobre")),
    Pagina("/sorteio", "d_sorteio", _corpo_sorteio, _nome_pagina("web_sorteio")),
    Pagina("/editor", "d_editor", _corpo_editor, _nome_pagina("web_editor")),
    Pagina("/termos", "d_termos", _corpo_texto("termos"), lambda lg: textos_legais.pagina("termos", lg)["titulo"]),
    Pagina("/privacidade", "d_privacidade", _corpo_texto("privacidade"), lambda lg: textos_legais.pagina("privacidade", lg)["titulo"]),
    Pagina("/contacto", "d_contacto", _corpo_texto("contacto"), lambda lg: textos_legais.pagina("contacto", lg)["titulo"]),
    Pagina("/changelog", "d_changelog", _corpo_changelog, lambda lg: "Changelog"),
)}


def url_publica(request: Request) -> str:
    """O URL publico do site, sem barra final. `PUBLIC_URL` (ou o `RENDER_EXTERNAL_URL` do Render) manda; sem eles usa o do pedido
    (so serve em desenvolvimento: o cabecalho `Host` e do cliente e nao se deve confiar nele para um canonico em producao)."""
    configurado = config.url_publica()
    return configurado or str(request.base_url).rstrip("/")


def _e(texto: str) -> str:
    return html.escape(texto, quote=True)


def _json_ld(dados: dict) -> str:
    # `</` dentro de um <script> fecharia-o: escapa-se
    return json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _dados_estruturados(base: str, lg: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": _app(lg),
        "url": f"{base}{caminho_na_lingua('/', lg)}",
        "description": ROTAS["/"].descricao(lg),
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Any (browser)",
        "browserRequirements": "Requires JavaScript",
        "inLanguage": list(i18n.LINGUAS),
        "image": f"{base}{IMAGEM}",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
    }


def _url(base: str, caminho: str, lg: str) -> str:
    c = caminho_na_lingua(caminho, lg)
    return f"{base}/" if c == "/" else f"{base}{c}"


def cabecalho(pagina: Pagina, base: str, lg: str = "pt") -> str:
    """O bloco do `<head>` desta pagina na lingua `lg` (o canonico e o hreflang apontam para o URL de cada lingua)."""
    url = _url(base, pagina.caminho, lg)
    imagem = f"{base}{IMAGEM}"
    titulo, descricao = pagina.titulo(lg), pagina.descricao(lg)
    alt = texto("og_alt", lg, app=_app(lg))
    robots = "index,follow,max-image-preview:large" if pagina.indexavel else "noindex,nofollow"
    linhas = [
        f"<title>{_e(titulo)}</title>",
        f'<meta name="description" content="{_e(descricao)}" />',
        f'<meta name="robots" content="{robots}" />',
    ]
    if pagina.indexavel:
        linhas.append(f'<link rel="canonical" href="{_e(url)}" />')
        linhas += [f'<link rel="alternate" hreflang="{outra}" href="{_e(_url(base, pagina.caminho, outra))}" />' for outra in i18n.LINGUAS]
        linhas.append(f'<link rel="alternate" hreflang="x-default" href="{_e(_url(base, pagina.caminho, "pt"))}" />')
        linhas += [
            '<meta property="og:type" content="website" />',
            f'<meta property="og:site_name" content="{_e(_app(lg))}" />',
            f'<meta property="og:locale" content="{LOCALE_OG[lg]}" />',
            f'<meta property="og:title" content="{_e(titulo)}" />',
            f'<meta property="og:description" content="{_e(descricao)}" />',
            f'<meta property="og:url" content="{_e(url)}" />',
            f'<meta property="og:image" content="{_e(imagem)}" />',
            '<meta property="og:image:width" content="1200" />',
            '<meta property="og:image:height" content="630" />',
            f'<meta property="og:image:alt" content="{_e(alt)}" />',
            '<meta name="twitter:card" content="summary_large_image" />',
            f'<meta name="twitter:title" content="{_e(titulo)}" />',
            f'<meta name="twitter:description" content="{_e(descricao)}" />',
            f'<meta name="twitter:image" content="{_e(imagem)}" />',
            f'<meta name="twitter:image:alt" content="{_e(alt)}" />',
        ]
    if pagina.caminho == "/":
        verificacao = config.google_verificacao()
        if verificacao:                                      # Search Console: o Google procura-a na pagina inicial
            linhas.append(f'<meta name="google-site-verification" content="{_e(verificacao)}" />')
        linhas.append(f'<script type="application/ld+json">{_json_ld(_dados_estruturados(base, lg))}</script>')
    return "\n    ".join(linhas)


def renderizar(html_base: str, pagina: Pagina, base: str, lg: str = "pt") -> str:
    """O `index.html` compilado com o `<head>` e o corpo estatico desta pagina, na lingua `lg` (tambem o `<html lang>`)."""
    cab = cabecalho(pagina, base, lg)
    corpo = f'<div class="seo-estatico">{pagina.corpo(lg)}</div>'
    html_base = re.sub(r'<html lang="[^"]*"', f'<html lang="{lg}"', html_base, count=1)
    if MARCADOR_CABECALHO in html_base:
        html_base = html_base.replace(MARCADOR_CABECALHO, cab, 1)
    else:                                                    # frontend sem marcadores (testes, desenvolvimento): antes de </head>
        html_base = re.sub(r"</head>", f"    {cab}\n  </head>", html_base, count=1)
    if MARCADOR_CORPO in html_base:
        html_base = html_base.replace(MARCADOR_CORPO, corpo, 1)
    return html_base


ADMIN = Pagina("/admin", "", lambda lg: "<h1>Painel</h1>", indexavel=False, no_mapa=False,
               titulo_fixo=f"Painel | {NOME}", descricao_fixa="Painel de administração.")


def pagina_nao_encontrada() -> Pagina:
    return Pagina("/404", "", lambda lg: f'<h1>Página não encontrada</h1><p><a href="/">Ir para o {NOME}</a></p>', indexavel=False, no_mapa=False,
                  titulo_fixo=f"Página não encontrada | {NOME}", descricao_fixa="Esta página não existe.")


def robots(base: str) -> str:
    """`robots.txt`: tudo aberto (incluindo o JS e o CSS, que os robos precisam para desenhar a pagina), menos a API e o painel."""
    return f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /admin\nDisallow: /v/\nDisallow: /V/\n\nSitemap: {base}/sitemap.xml\n"


def sitemap(base: str) -> str:
    """Uma `<url>` por pagina e lingua, cada uma com as alternativas (`xhtml:link`, o formato que o Google pede para varias linguas)."""
    urls = []
    for p in ROTAS.values():
        if not (p.indexavel and p.no_mapa):
            continue
        alternativas = "".join(f'<xhtml:link rel="alternate" hreflang="{lg}" href="{_e(_url(base, p.caminho, lg))}"/>' for lg in i18n.LINGUAS)
        alternativas += f'<xhtml:link rel="alternate" hreflang="x-default" href="{_e(_url(base, p.caminho, "pt"))}"/>'
        urls += [f"<url><loc>{_e(_url(base, p.caminho, lg))}</loc>{alternativas}</url>" for lg in i18n.LINGUAS]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            f'xmlns:xhtml="http://www.w3.org/1999/xhtml">{"".join(urls)}</urlset>\n')
