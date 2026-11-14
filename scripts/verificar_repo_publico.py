"""Confirma que o repositório PÚBLICO da app Windows (`AndreNogueira/gerador-rifas-windows`) só distribui o programa e nunca tem código-fonte.

Corre-se antes de cada release (precisa do `gh` autenticado): `uv run python scripts/verificar_repo_publico.py`. Sai com código 1 se algo falhar.
O que verifica: é público; só tem o ramo `main`; todos os commits, em todo o histórico, só tocam no `README.md`; a árvore só tem o `README.md`; nenhuma
etiqueta ou release leva outra coisa além do `GeradorRifas.exe` e do `.sha256`; o `README.md` não tem blocos de código nem ligações para o repositório privado.
Os arquivos «Source code» que o GitHub junta a cada release são o conteúdo da árvore (só o README), por isso também ficam limpos.
"""
from __future__ import annotations

import base64
import json
import re
import subprocess
import sys

REPO = "AndreNogueira/gerador-rifas-windows"
PRIVADO = "AndreNogueira/gerador-rifas"
PERMITIDOS_NA_RELEASE = {"GeradorRifas.exe", "GeradorRifas.exe.sha256"}


def gh(*args: str):
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout) if r.stdout.strip() else None


def verificar() -> list[str]:
    problemas = []
    repo = gh(f"repos/{REPO}")
    if repo["private"] or repo["visibility"] != "public":
        problemas.append("o repositório deixou de ser público (o link de descarga deixa de funcionar)")
    ramos = [b["name"] for b in gh(f"repos/{REPO}/branches", "--paginate")]
    if ramos != ["main"]:
        problemas.append(f"ramos a mais: {ramos}")
    for c in gh(f"repos/{REPO}/commits", "--paginate"):
        ficheiros = [f["filename"] for f in gh(f"repos/{REPO}/commits/{c['sha']}").get("files", [])]
        if set(ficheiros) - {"README.md"}:
            problemas.append(f"o commit {c['sha'][:8]} toca em {ficheiros}")
    arvore = gh(f"repos/{REPO}/git/trees/main?recursive=1")
    ficheiros = [(n["type"], n["path"]) for n in arvore["tree"]]
    if ficheiros != [("blob", "README.md")]:
        problemas.append(f"a árvore tem mais do que o README.md: {ficheiros}")
    for r in gh(f"repos/{REPO}/releases", "--paginate"):
        extra = {a["name"] for a in r["assets"]} - PERMITIDOS_NA_RELEASE
        if extra:
            problemas.append(f"a release {r['tag_name']} tem ficheiros a mais: {sorted(extra)}")
    readme = base64.b64decode(gh(f"repos/{REPO}/contents/README.md")["content"]).decode("utf-8")
    if "```" in readme:
        problemas.append("o README tem blocos de código")
    if re.search(rf"github\.com/{re.escape(PRIVADO)}(?![-\w])", readme):
        problemas.append("o README liga ao repositório privado")
    return problemas


if __name__ == "__main__":
    try:
        mau = verificar()
    except subprocess.CalledProcessError as e:
        print("não consegui falar com o GitHub (gh autenticado?):", e.stderr[:200])
        sys.exit(2)
    print("\n".join(f"FALHA {p}" for p in mau) if mau else f"ok: {REPO} só distribui o programa (README.md e releases com o .exe), sem código-fonte")
    sys.exit(1 if mau else 0)
