"""Gera N rifas (por defeito 5000) em cada template aleatorio e confirma o resultado.

Uso:  python teste_5000.py <pasta_com_templates> <pasta_saida> <rota: pdf|png> [N]
Cada template: 1 PDF com tudo + varios PDFs (Z = 50 paginas), verificacao automatica incluida.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ambiente  # noqa: F401,E402  (poe ..\src no sys.path)
import core  # noqa: E402

pasta, saida, rota = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 5000
def _meta(p: Path) -> dict:
    m = json.loads(p.read_text(encoding="utf-8"))
    for k in ("template", "algarismos_pdf", "algarismos_png"):    # caminhos relativos a esta pasta
        m[k] = str(p.parent / Path(m[k]).name)
    return m


metas = sorted((_meta(p) for p in pasta.glob("meta_s*.json")), key=lambda m: m["n"])
falhou = False
for m in metas:
    n = m["n"]
    dig = Path(m["algarismos_pdf" if rota == "pdf" else "algarismos_png"])
    t0 = time.time()
    prep = core.preparar(Path(m["template"]), dig, lambda s: None)
    assert prep.info.n_campos == n, (prep.info.n_campos, n)
    esc = "vetorial" if prep.escritores[prep.info.fontes[0]].vetorial else "imagem"
    t1 = time.time()
    res = core.gerar(core.Trabalho(saida=saida / f"n{n}_{rota}_unico", nome="RIFA", inicio=1, fim=N, digitos=m.get("ndig", 4)), prep)
    r = res[0]
    paginas_esp = math.ceil(N / n)
    ok1 = r.ok and r.paginas == paginas_esp
    t2 = time.time()
    z = 50 * n
    res2 = core.gerar(core.Trabalho(saida=saida / f"n{n}_{rota}_varios", nome="RIFA", inicio=1, fim=N, por_ficheiro=z, digitos=m.get("ndig", 4)), prep)
    ok2 = all(x.ok for x in res2) and sum(x.paginas for x in res2) == paginas_esp and len(res2) == math.ceil(N / z)
    t3 = time.time()
    falhou |= not (ok1 and ok2)
    print(f"n={n:2d} {m['pagina']:<18} {m['grelha']:<5} {m['fonte']:<12} {m['talao']:<12} [{esc}] "
          f"prep {t1 - t0:4.1f}s | 1 PDF: {r.paginas}p {r.caminho.stat().st_size / 1e6:5.1f}MB {t2 - t1:6.1f}s "
          f"{'OK' if ok1 else 'FALHOU ' + str(r.erros[:1])} | {len(res2)} PDFs {t3 - t2:6.1f}s {'OK' if ok2 else 'FALHOU'}",
          flush=True)
sys.exit(1 if falhou else 0)
