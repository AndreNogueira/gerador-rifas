"""Testa templates REAIS exportados do Canva (com as letras reais) que estao em testes/.

Uso: python testes/teste_canva.py <pasta_de_saida> [pasta_dos_pdfs]

- «... Letras.pdf»            ficheiro dos algarismos (letra do Canva);
- «teste - 00001 - 30000.pdf» PDF gerado pela app (so se confirma que os numeros estao certos);
- os outros .pdf              templates: 5 por pagina (n_campos 5) ou uma rifa (n_campos 1; enche-se A4 e A3).
Gera e verifica cada um; sai com codigo 1 se algum falhar.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ambiente  # noqa: F401,E402  (poe ..\src no sys.path)
import core
import pypdfium2 as pdfium

SAIDA = Path(sys.argv[1])
PASTA = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent
SAIDA.mkdir(parents=True, exist_ok=True)
falhas: list = []


def verifica(cond: bool, msg: str) -> None:
    print(("ok     " if cond else "FALHOU ") + msg, flush=True)
    if not cond:
        falhas.append(msg)


pdfs = sorted(PASTA.glob("*.pdf"))
letras = [p for p in pdfs if "letras" in p.name.lower()]
gerados = [p for p in pdfs if re.search(r" - \d+ - \d+\.pdf$", p.name)]
templates = [p for p in pdfs if p not in letras and p not in gerados]
if not letras or not templates:
    print("nao ha templates do Canva + ficheiro de letras em", PASTA)
    sys.exit(0)

for t in templates:
    prep = core.preparar(t, letras[0])
    i = prep.info
    ok_letra = "Letras" in prep.descricoes[0] or letras[0].name in prep.descricoes[0]
    verifica(ok_letra and prep.escritores[i.fontes[0]].vetorial, f"{t.name}: {i.n_campos} rifa(s), letra {i.fontes[0]} do ficheiro de letras (vetorial)")
    variantes = [("", prep)] if i.n_campos > 1 else [(f" {p}", prep.com_folha(p, 5)) for p in ("A4", "A3", "Letter")]
    for suf, p in variantes:
        r = core.gerar(core.Trabalho(saida=SAIDA, nome=(t.stem + suf).replace(" ", "_"), inicio=1, fim=1203, digitos=4), p)
        verifica(all(x.ok for x in r) and r[0].paginas == -(-1203 // p.por_pagina),
                 f"{t.name}{suf}: {p.por_pagina}/pagina, {r[0].paginas} paginas, verificado {r[0].erros[:1]}")
    # tambem com 5 digitos e varios PDFs
    n = p.por_pagina
    r = core.gerar(core.Trabalho(saida=SAIDA, nome=(t.stem + "_5dig").replace(" ", "_"), inicio=1, fim=30 * n, por_ficheiro=10 * n,
                                 digitos=5), p)
    verifica(len(r) == 3 and all(x.ok for x in r), f"{t.name}: 5 algarismos em 3 PDFs ({n}/pagina)")

for g in gerados:      # PDF que a app ja gerou: numeros seguidos, 2x cada (talao + principal)
    d = pdfium.PdfDocument(str(g))
    m = re.search(r" - (\d+) - (\d+)\.pdf$", g.name)
    a, b = int(m.group(1)), int(m.group(2))
    larg = len(m.group(1))
    esperado = []
    for k in range(len(d)):
        tp = d[k].get_textpage()
        achados = re.findall(rf"(?<!\d)\d{{{larg}}}(?!\d)", tp.get_text_range())
        tp.close()
        nums = sorted({int(x) for x in achados})
        esperado.extend(nums)
        if k >= 3 and k < len(d) - 3:       # nas paginas do meio basta confirmar a 1.a e as ultimas (rapido)
            continue
    verifica(esperado[0] == a and esperado[-1] == b and len(esperado) == b - a + 1,
             f"{g.name}: {len(d)} paginas, numeros {esperado[0]}..{esperado[-1]} ({len(esperado)} distintos)")
    d.close()

print("\nRESULTADO:", "OK" if not falhas else f"FALHOU ({len(falhas)})")
sys.exit(1 if falhas else 0)
