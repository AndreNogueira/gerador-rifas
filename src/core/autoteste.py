"""A parte do auto-teste (app --selftest) que nao precisa de janela: gerar os PDFs de exemplo e confirma-los.

Extraido de app.py::selftest. As linhas de resultado e a ordem sao exatamente as do auto-teste original.
"""
from __future__ import annotations

from pathlib import Path

from .motor import Trabalho, gerar, preparar


def gerar_exemplos(exemplos: Path, destino: Path) -> tuple:
    """Gera os exemplos com os dois ficheiros de algarismos (imagem e PDF): template de 5 rifas por pagina e, com uma so rifa,
    folha A4 (margem 5 e 12) e A3. Devolve (linhas de resultado, codigo) com codigo 0 = tudo ok, 1 = alguma falha."""
    exemplos, destino = Path(exemplos), Path(destino)
    linhas, codigo = [], 0
    tpl = exemplos / "template_exemplo.pdf"
    for nome in ("digitos_exemplo.png", "digitos_exemplo.pdf"):
        prep = preparar(tpl, exemplos / nome)
        res = gerar(Trabalho(saida=destino / nome.split(".")[0], nome="TESTE", inicio=1, fim=65), prep)
        ok = all(r.ok for r in res)
        linhas.append(f"{nome}: {'ok' if ok else 'ERRO'} ({sum(r.paginas for r in res)} paginas)")
        codigo |= 0 if ok else 1
    # uma so rifa no template: a folha A4 e enchida com copias (PDF e imagem de algarismos; 0, 90 graus e A3)
    for nome in ("digitos_exemplo.png", "digitos_exemplo.pdf"):
        prep = preparar(exemplos / "template_exemplo_1_rifa.pdf", exemplos / nome)
        for papel, margem in (("A4", 5), ("A3", 5), ("A4", 12)):
            p = prep.com_folha(papel, margem)
            res = gerar(Trabalho(saida=destino / "folha", nome=f"UMA-{papel}-{margem}-{nome[-3:]}", inicio=1, fim=23), p)
            ok = all(r.ok for r in res) and p.disp.n >= 3
            linhas.append(f"1 rifa, {papel}, margem {margem}, {nome}: {'ok' if ok else 'ERRO'} "
                          f"({p.disp.n} por folha, {sum(r.paginas for r in res)} paginas)")
            codigo |= 0 if ok else 1
    return linhas, codigo
