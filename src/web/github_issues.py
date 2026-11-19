"""Criar um *issue* no GitHub do projeto a partir de um problema reportado no site (`POST /api/problemas`).

SEGURANÇA
 - O token (`GITHUB_ISSUES_TOKEN`, um *fine-grained token* só com «Issues: read and write» NESTE repositório) vive só nas variáveis do Render: nunca no código, num log
   nem numa resposta. Sem token (ou sem `GITHUB_REPO`) a função fica desligada e o site diz-o.
 - O texto vem de um visitante: vai SEMPRE dentro de blocos de código, para o GitHub não o interpretar (nada de @menções que notificam gente, #referências,
   imagens nem ligações). O título é uma linha de texto limpa. O IP do visitante nunca é enviado.
 - Um erro do GitHub nunca chega ao visitante tal e qual (pode ter detalhes internos): vira «não foi possível registar agora».
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

from .opiniao import limpar_texto

API = "https://api.github.com"
ETIQUETA = "bug-do-site"
TITULO_MAX = 100
CAMPO_MAX = 4000
TECNICA_MAX = 600


class ErroGithub(Exception):
    """O GitHub recusou ou não respondeu (a mensagem não vai para o visitante)."""


def neutralizar_titulo(t: str) -> str:
    """Uma linha, sem @menções nem #referências (um espaço invisível desfaz-as) e sem sintaxe de markdown no início."""
    t = limpar_texto(t, TITULO_MAX, uma_linha=True)
    t = t.replace("@", "@​").replace("#", "#​")
    return re.sub(r"^[>#\-*+=\s]+", "", t) or "Problema reportado no site"


def bloco(texto: str) -> str:
    """O texto dentro de um bloco de código com uma vedação mais comprida do que qualquer sequência de crases que ele contenha."""
    maior = max((len(m) for m in re.findall(r"`+", texto)), default=0)
    vedacao = "`" * max(3, maior + 1)
    return f"{vedacao}text\n{texto}\n{vedacao}"


def corpo_do_issue(descricao: str, passos: str, tecnica: str, versao: str, lingua: str, pagina: str) -> str:
    partes = ["_Reportado pelo formulário do site (sem conta, sem IP)._", "", "### O que aconteceu", bloco(limpar_texto(descricao, CAMPO_MAX))]
    if passos.strip():
        partes += ["", "### Como repetir", bloco(limpar_texto(passos, CAMPO_MAX))]
    ficha = [f"Versão: {versao}", f"Língua: {lingua}", f"Página: {pagina}"]
    if tecnica.strip():
        ficha.append(f"Navegador e ecrã: {limpar_texto(tecnica, TECNICA_MAX, uma_linha=True)}")
    partes += ["", "### Informação técnica", bloco("\n".join(ficha))]
    return "\n".join(partes)


def criar_issue(token: str, repo: str, titulo: str, corpo: str, abrir=urllib.request.urlopen) -> int:
    """Cria o issue e devolve o número. `abrir` só se troca nos testes."""
    pedido = urllib.request.Request(
        f"{API}/repos/{repo}/issues", method="POST",
        data=json.dumps({"title": titulo, "body": corpo, "labels": [ETIQUETA]}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
                 "Content-Type": "application/json", "User-Agent": "gerador-rifas-site"})
    try:
        with abrir(pedido, timeout=10) as r:
            dados = json.loads(r.read().decode("utf-8"))
        numero = int(dados["number"])
    except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError) as e:
        raise ErroGithub(type(e).__name__) from None          # só a classe: a mensagem pode trazer o endereço ou o token
    return numero
