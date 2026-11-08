"""SEO: o `<head>` e um resumo estatico do conteudo de cada pagina, `robots.txt` e `sitemap.xml`.

A webapp e uma SPA: o HTML que o servidor entrega estaria vazio (`<div id="raiz">`) para quem nao corre JavaScript (redes sociais,
muitos motores de pesquisa, partilhas por mensagem). Por isso o servidor injeta no `index.html` compilado, por rota conhecida:
 - no `<head>` (marcador `<!--seo:cabecalho-->`): titulo, descricao, canonico, robots, Open Graph, Twitter e JSON-LD;
 - no corpo (marcador `<!--seo:corpo-->` dentro de `#raiz`): texto real da pagina (o React substitui-o ao arrancar; o CSS esconde-o
   visualmente: `.seo-estatico`).
O conteudo e sempre em portugues (e o `lang` do documento): e o que um robo sem `Accept-Language` recebe. Nao ha hreflang porque
a lingua da interface nao esta no URL. Sem URL publico configurado (`PUBLIC_URL`) o canonico sai do pedido.
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

NOME = "Gerador de Rifas"
IMAGEM = "/og-imagem.png"           # 1200x630, em frontend/public
IMAGEM_ALT = "Gerador de Rifas: dois bilhetes numerados, um amarelo com o 7 da sorte"
MARCADOR_CABECALHO = "<!--seo:cabecalho-->"
MARCADOR_CORPO = "<!--seo:corpo-->"

_PASSOS = (
    ("Template", "Carregue o PDF do template exportado do Canva (com 0001, 0002, ... no lugar dos números)."),
    ("Algarismos 0–9", "Carregue um PDF, PNG ou JPG com os dez algarismos na mesma letra do template."),
    ("Números", "Escolha de que número a que número, quantos algarismos e se quer vários PDFs ou um só."),
    ("Destino", "Escreva o nome dos ficheiros, veja a pré-visualização com os números reais e gere: descarregue o PDF ou o ZIP."),
)


def _paragrafos(texto: str) -> str:
    return "".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in texto.split("\n\n") if p.strip())


def _corpo_inicio() -> str:
    passos = "".join(f"<li><strong>{html.escape(t)}.</strong> {html.escape(d)}</li>" for t, d in _PASSOS)
    return (
        f"<h1>{NOME}</h1>"
        "<p>Crie rifas numeradas em PDF a partir de um template do Canva: escolha os números, veja a pré-visualização e descarregue "
        "os PDFs prontos a imprimir. É grátis, não precisa de registo e funciona em 18 línguas.</p>"
        f"<h2>Como funciona</h2><ol>{passos}</ol>"
        f"<h2>Os seus ficheiros</h2><p>O template e os algarismos servem só para gerar as suas rifas e são apagados do servidor "
        f"passados {config.validade_min()} minutos sem atividade, ou quando carrega em «Limpar tudo».</p>"
        '<nav><a href="/tutorial">Tutorial</a> <a href="/video">Vídeo tutorial</a> <a href="/sobre">Acerca de</a></nav>'
    )


def _corpo_tutorial() -> str:
    with i18n.com_lingua("pt"):
        topicos = tutorial.lista_de_topicos()
    secoes = "".join(f"<section><h2>{html.escape(titulo)}</h2>{_paragrafos(texto)}</section>" for _, titulo, texto, _ in topicos)
    return f'<h1>Tutorial</h1><p>Passo a passo para gerar as suas rifas numeradas.</p>{secoes}<p><a href="/">Voltar ao {NOME}</a></p>'


def _corpo_video() -> str:
    return (
        "<h1>Vídeo tutorial</h1>"
        "<p>Veja em vídeo como gerar rifas numeradas em PDF, do template do Canva ao PDF pronto a imprimir.</p>"
        '<p><a href="/videos/tutorial_pt.mp4">Ver o vídeo tutorial (MP4)</a></p>'
        f'<p><a href="/">Voltar ao {NOME}</a></p>'
    )


def _corpo_sobre() -> str:
    with i18n.com_lingua("pt"):
        texto = i18n.traduzir("sobre_texto", "pt", app=NOME, versao=VERSAO)
    resumo = "\n\n".join(texto.split("\n\n")[:2])
    return f'<h1>Acerca do {NOME}</h1>{_paragrafos(resumo)}<p><a href="/">Voltar ao {NOME}</a></p>'


def _corpo_changelog() -> str:
    blocos = []
    for e in list(changelog.entradas())[:6]:
        itens = "".join(f"<h3>{html.escape(s.titulo)}</h3><ul>{''.join(f'<li>{html.escape(i)}</li>' for i in s.itens)}</ul>" for s in e.seccoes)
        blocos.append(f"<section><h2>Versão {html.escape(e.versao)} ({html.escape(e.data)})</h2>{itens}</section>")
    return f'<h1>Changelog</h1><p>O que mudou no {NOME}, versão a versão.</p>{"".join(blocos)}<p><a href="/">Voltar ao {NOME}</a></p>'


def _corpo_texto(nome: str) -> Callable[[], str]:
    def corpo() -> str:
        d = textos_legais.PAGINAS[nome]()
        aviso = f"<p><em>{html.escape(d['aviso'])}</em></p>" if d["aviso"] else ""
        secoes = "".join(f"<section><h2>{html.escape(s['titulo'])}</h2>{''.join(f'<p>{html.escape(p)}</p>' for p in s['paragrafos'])}</section>"
                         for s in d["seccoes"])
        return f'<h1>{html.escape(d["titulo"])}</h1>{aviso}{secoes}<p><a href="/">Voltar ao {NOME}</a></p>'
    return corpo


@dataclass(frozen=True)
class Pagina:
    caminho: str
    titulo: str                 # ate ~60 caracteres
    descricao: str              # ate ~155 caracteres
    corpo: Callable[[], str]
    indexavel: bool = True
    no_mapa: bool = True


ROTAS: dict[str, Pagina] = {p.caminho: p for p in (
    Pagina("/", f"{NOME}: rifas numeradas em PDF a partir do Canva",
           "Rifas numeradas em PDF a partir de um template do Canva: escolha os números, veja a pré-visualização e descarregue. Grátis e sem registo.",
           _corpo_inicio),
    Pagina("/tutorial", f"Tutorial: como criar rifas numeradas | {NOME}",
           "Passo a passo para preparar o template no Canva, criar o ficheiro dos algarismos, escolher os números e gerar os PDFs das rifas.",
           _corpo_tutorial),
    Pagina("/video", f"Vídeo tutorial | {NOME}",
           "Veja em vídeo como gerar rifas numeradas em PDF, do template do Canva ao PDF pronto a imprimir.",
           _corpo_video),
    Pagina("/sobre", f"Acerca do {NOME}",
           "O que é o Gerador de Rifas, como funciona e o que usa. O mesmo motor da aplicação para Windows, agora no browser.",
           _corpo_sobre),
    Pagina("/termos", f"Termos de utilização | {NOME}",
           "As regras de utilização do Gerador de Rifas: o que o serviço faz, o que não faz e quem é responsável pela rifa.",
           _corpo_texto("termos")),
    Pagina("/privacidade", f"Política de privacidade | {NOME}",
           "Que dados o Gerador de Rifas trata (quase nenhuns), durante quanto tempo e que direitos tem, segundo o RGPD.",
           _corpo_texto("privacidade")),
    Pagina("/contacto", f"Contacto | {NOME}",
           "Como falar com quem gere o Gerador de Rifas: dúvidas, erros e sugestões sobre as suas rifas numeradas.",
           _corpo_texto("contacto")),
    Pagina("/changelog", f"Changelog: o que mudou | {NOME}",
           "Tudo o que mudou no Gerador de Rifas, versão a versão: novas funcionalidades, melhorias e correções.",
           _corpo_changelog),
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


def _dados_estruturados(base: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": NOME,
        "url": f"{base}/",
        "description": ROTAS["/"].descricao,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Qualquer (browser)",
        "browserRequirements": "Requer JavaScript",
        "inLanguage": list(i18n.LINGUAS),
        "image": f"{base}{IMAGEM}",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        "featureList": [
            "Rifas numeradas em PDF a partir de um template do Canva",
            "Pré-visualização com os números reais",
            "Um PDF único ou vários PDFs, com download em ZIP",
            "18 línguas",
        ],
    }


def cabecalho(pagina: Pagina, base: str) -> str:
    """O bloco do `<head>` desta pagina."""
    url = f"{base}/" if pagina.caminho == "/" else f"{base}{pagina.caminho}"
    imagem = f"{base}{IMAGEM}"
    robots = "index,follow,max-image-preview:large" if pagina.indexavel else "noindex,nofollow"
    linhas = [
        f"<title>{_e(pagina.titulo)}</title>",
        f'<meta name="description" content="{_e(pagina.descricao)}" />',
        f'<meta name="robots" content="{robots}" />',
    ]
    if pagina.indexavel:
        linhas += [
            f'<link rel="canonical" href="{_e(url)}" />',
            '<meta property="og:type" content="website" />',
            f'<meta property="og:site_name" content="{NOME}" />',
            '<meta property="og:locale" content="pt_PT" />',
            f'<meta property="og:title" content="{_e(pagina.titulo)}" />',
            f'<meta property="og:description" content="{_e(pagina.descricao)}" />',
            f'<meta property="og:url" content="{_e(url)}" />',
            f'<meta property="og:image" content="{_e(imagem)}" />',
            '<meta property="og:image:width" content="1200" />',
            '<meta property="og:image:height" content="630" />',
            f'<meta property="og:image:alt" content="{_e(IMAGEM_ALT)}" />',
            '<meta name="twitter:card" content="summary_large_image" />',
            f'<meta name="twitter:title" content="{_e(pagina.titulo)}" />',
            f'<meta name="twitter:description" content="{_e(pagina.descricao)}" />',
            f'<meta name="twitter:image" content="{_e(imagem)}" />',
            f'<meta name="twitter:image:alt" content="{_e(IMAGEM_ALT)}" />',
        ]
    if pagina.caminho == "/":
        linhas.append(f'<script type="application/ld+json">{_json_ld(_dados_estruturados(base))}</script>')
    return "\n    ".join(linhas)


def renderizar(html_base: str, pagina: Pagina, base: str) -> str:
    """O `index.html` compilado com o `<head>` e o corpo estatico desta pagina."""
    cab = cabecalho(pagina, base)
    corpo = f'<div class="seo-estatico">{pagina.corpo()}</div>'
    if MARCADOR_CABECALHO in html_base:
        html_base = html_base.replace(MARCADOR_CABECALHO, cab, 1)
    else:                                                    # frontend sem marcadores (testes, desenvolvimento): antes de </head>
        html_base = re.sub(r"</head>", f"    {cab}\n  </head>", html_base, count=1)
    if MARCADOR_CORPO in html_base:
        html_base = html_base.replace(MARCADOR_CORPO, corpo, 1)
    return html_base


ADMIN = Pagina("/admin", f"Painel | {NOME}", "Painel de administração.", lambda: "<h1>Painel</h1>", indexavel=False, no_mapa=False)


def pagina_nao_encontrada() -> Pagina:
    return Pagina("/404", f"Página não encontrada | {NOME}", "Esta página não existe.",
                  lambda: f'<h1>Página não encontrada</h1><p><a href="/">Ir para o {NOME}</a></p>', indexavel=False, no_mapa=False)


def robots(base: str) -> str:
    """`robots.txt`: tudo aberto (incluindo o JS e o CSS, que os robos precisam para desenhar a pagina), menos a API e o painel."""
    return f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /admin\n\nSitemap: {base}/sitemap.xml\n"


def sitemap(base: str) -> str:
    urls = "".join(
        f"<url><loc>{_e(base + ('/' if p.caminho == '/' else p.caminho))}</loc></url>" for p in ROTAS.values() if p.indexavel and p.no_mapa
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'
