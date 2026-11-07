"""Testes com mais algarismos e intervalos grandes (procura problemas de espaco, memoria e tempo).

Uso: python teste_digitos.py <pasta_templates_aleatorios> <pasta_saida>
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import core  # noqa: E402

try:
    import psutil
    proc = psutil.Process()
except Exception:      # psutil so e usado nos testes
    proc = None

pasta, saida = Path(sys.argv[1]), Path(sys.argv[2])
log = lambda m: print("   |", m[:200], flush=True)


def mem() -> str:
    return f"{proc.memory_info().rss / 1e6:.0f} MB" if proc else "?"


def correr(titulo, tpl, alg, **kw):
    t0 = time.time()
    prep = core.preparar(pasta / tpl, pasta / alg, log)
    tr = core.Trabalho(saida=saida / titulo, nome="X", **kw)
    res = core.gerar(tr, prep, log)
    r = res[0]
    print(f"{titulo}: {sum(x.paginas for x in res)} paginas, {r.caminho.stat().st_size / 1e6:.1f} MB, "
          f"{time.time() - t0:.1f}s, memoria {mem()}, {'OK' if all(x.ok for x in res) else 'FALHOU ' + str(r.erros[:1])}",
          flush=True)
    return res


# 1. desenho de 4 algarismos com numeros de 8 algarismos (tem de encolher, nao transbordar)
for rota, alg in (("pdf", "algarismos_s4.pdf"), ("png", "algarismos_s4.png")):
    correr(f"mais_algarismos_{rota}", "template_14_por_pagina_4dig_s4.pdf", alg, inicio=1, fim=5000, digitos=8)

# 2. 6 e 8 algarismos nos desenhos feitos para 6 e 8
correr("seis_dig", "template_5_por_pagina_6dig_s8.pdf", "algarismos_s8.pdf", inicio=1, fim=100000, digitos=6)
correr("oito_dig", "template_12_por_pagina_8dig_s9.pdf", "algarismos_s9.pdf", inicio=99990000, fim=99999999, digitos=8)

# 3. numero com mais algarismos que o pedido (fim = 123456 com digitos=4 -> largura 6)
correr("auto_largura", "template_24_por_pagina_4dig_s5.pdf", "algarismos_s5.pdf", inicio=1, fim=123456, digitos=4)

# 4. intervalo enorme: 1 milhao de numeros num unico PDF
if len(sys.argv) > 3 and sys.argv[3] == "grande":
    correr("um_milhao", "template_24_por_pagina_4dig_s5.pdf", "algarismos_s5.pdf", inicio=1, fim=1_000_000, digitos=7)
