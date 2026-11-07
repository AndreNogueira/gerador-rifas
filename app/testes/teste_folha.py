"""Testa o modo «uma so rifa no template»: a app enche a folha com copias (maximo por folha, com rotacao) e escreve os numeros.

Uso: python testes/teste_folha.py <pasta_de_exemplos> <pasta_de_saida>
Cria <pasta_de_saida>/*.png com as folhas geradas (para ver a olho) e imprime OK / FALHOU.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ambiente  # noqa: F401,E402  (poe ..\src no sys.path)
import core

EX, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])
SAIDA.mkdir(parents=True, exist_ok=True)
falhas: list = []


def verifica(cond: bool, msg: str) -> None:
    print(("ok     " if cond else "FALHOU ") + msg, flush=True)
    if not cond:
        falhas.append(msg)


# 1) a arrumacao: contas feitas a mao
mm = core.MM
a4w, a4h = core.PAPEIS["A4"]


def cabem(w_mm, h_mm, papel="A4", margem=5):
    from core import Ret, InfoTemplate
    info = InfoTemplate(Path("x.pdf"), [], 1, [], w_mm * mm, h_mm * mm, 1, "0001", "0001",
                        celula=Ret(0, 0, w_mm * mm, h_mm * mm))
    return core.disposicao_da_folha(info, papel, margem)


d = cabem(189, 54)
verifica(d.maximo == 5 and d.rodadas == 0, f"189x54 mm em A4: {d.maximo} ({d.rodadas} rodadas) = 5, sem rodar")
d = cabem(54, 189)
verifica(d.maximo == 5, f"54x189 mm em A4 (em pe): {d.maximo} = 5 (a folha em largura ou rodada)")
d = cabem(100, 100)
verifica(d.maximo == 4, f"100x100 mm em A4: {d.maximo} = 4 (2 x 2: a 3.a linha nao cabe)")
d = cabem(95, 95)
verifica(d.maximo == 6, f"95x95 mm em A4: {d.maximo} = 6")
d = cabem(90, 60)
verifica(d.maximo >= 8, f"90x60 mm em A4: {d.maximo} >= 8")
d = cabem(95, 45)
um = d.maximo
verifica(um >= 12, f"95x45 mm em A4: {um} >= 12 ({d.rodadas} rodadas)")
try:
    cabem(400, 300)
    verifica(False, "rifa maior que a folha devia dar erro")
except core.ErroRifas as e:
    verifica(e.chave == "err_rifa_grande", "rifa maior que a folha -> err_rifa_grande")
d = cabem(100, 100, "A3")
verifica(d.maximo > cabem(100, 100, "A4").maximo, "A3 leva mais que A4")
# nunca saem da folha nem se sobrepoem (varias medidas)
import itertools
for w, h in itertools.product((40, 55, 70, 95, 120, 150, 189), (30, 45, 60, 80, 110, 150)):
    d = cabem(w, h)
    caixas = []
    for x, y, r in d.posicoes:
        cw, ch = (d.celula.width, d.celula.height) if r == 0 else (d.celula.height, d.celula.width)
        assert x >= d.margem - 0.01 and y >= d.margem - 0.01 and x + cw <= d.largura - d.margem + 0.01 \
            and y + ch <= d.altura - d.margem + 0.01, (w, h, x, y, r)
        caixas.append((x, y, x + cw, y + ch))
    for (a, b) in itertools.combinations(caixas, 2):
        assert a[0] >= b[2] - 0.01 or b[0] >= a[2] - 0.01 or a[1] >= b[3] - 0.01 or b[1] >= a[3] - 0.01, (w, h, a, b)
verifica(True, "nenhuma rifa sai da folha nem se sobrepoe (42 tamanhos)")

# 2) o template de 5 por pagina continua como antes
for alg in ("digitos_exemplo.pdf", "digitos_exemplo.png"):
    prep = core.preparar(EX / "template_exemplo.pdf", EX / alg)
    verifica(prep.info.n_campos == 5 and prep.disp is None and prep.por_pagina == 5, f"5 por pagina ({alg})")
    r = core.gerar(core.Trabalho(saida=SAIDA / "cinco", nome="C5-" + alg[-3:], inicio=1, fim=27, por_ficheiro=None), prep)
    verifica(all(x.ok for x in r) and r[0].paginas == 6, f"5 por pagina gerado e verificado ({alg}): {r[0].paginas} paginas")

# 3) uma rifa, pagina = rifa
for alg in ("digitos_exemplo.pdf", "digitos_exemplo.png"):
    prep = core.preparar(EX / "template_exemplo_1_rifa.pdf", EX / alg)
    verifica(prep.info.n_campos == 1 and prep.info.celula_origem == "pagina", f"1 rifa detetada ({alg}), origem {prep.info.celula_origem}")
    for papel, margem in (("A4", 5), ("A4", 12), ("A3", 5), ("Letter", 5)):
        p = prep.com_folha(papel, margem)
        r = core.gerar(core.Trabalho(saida=SAIDA / "uma", nome=f"U-{papel}-{margem}-{alg[-3:]}", inicio=1, fim=23), p)
        verifica(all(x.ok for x in r), f"1 rifa em {papel} margem {margem} ({alg}): {p.disp.n}/folha, {r[0].paginas} paginas, "
                 f"erros={r[0].erros[:1]}")
    p = prep.com_folha("A4", 5, 3)
    verifica(p.por_pagina == 3, "n pedido (3) respeitado")
    p = prep.com_folha("A4", 5, 99)
    verifica(p.por_pagina == p.disp.maximo, "n acima do maximo -> maximo")

# 4) uma rifa no meio de uma folha A4: a app recorta a zona desenhada
prep = core.preparar(EX / "template_exemplo_1_rifa_a4.pdf", EX / "digitos_exemplo.pdf")
c = prep.info.celula
verifica(prep.info.celula_origem == "conteudo" and abs(c.width / mm - 189) < 3 and abs(c.height / mm - 54) < 3,
         f"zona recortada: {prep.info.celula_origem} {c.width / mm:.0f}x{c.height / mm:.0f} mm")
p = prep.com_folha("A4", 5)
r = core.gerar(core.Trabalho(saida=SAIDA / "uma", nome="RECORTADA", inicio=1, fim=12), p)
verifica(all(x.ok for x in r) and p.disp.maximo == 5, f"rifa recortada: {p.disp.maximo}/folha, verificada")

# 4b) rifas ALEATORIAS (pagina do tamanho da rifa; letra, cores, fundo e orientacao do talao aleatorios)
import random
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_template_aleatorio as gta
rnd = random.Random(7)
tmp = Path(tempfile.mkdtemp(prefix="folha_"))
for semente in range(100, 112):
    w, h = rnd.choice((380, 450, 520, 600)), rnd.choice((110, 160, 220, 300))
    rot = (0, 90, 180, 270)[semente % 4]
    ndig = (4, 4, 6)[semente % 3]
    meta = gta.criar(tmp, semente, 1, rot, ndig, (float(w), float(h)))
    for alg in (meta["algarismos_pdf"], meta["algarismos_png"]):
        prep = core.preparar(tmp / meta["template"], tmp / alg)
        papel = rnd.choice(list(core.PAPEIS))
        p = prep.com_folha(papel, rnd.choice((0, 5, 10)))
        r = core.gerar(core.Trabalho(saida=SAIDA / "aleatorias", nome=f"A{semente}", inicio=1, fim=61, digitos=ndig), p)
        verifica(all(x.ok for x in r), f"aleatoria s{semente} {w}x{h}pt talao {rot} {ndig}dig {papel}: {p.disp.n}/folha "
                 f"({p.disp.rodadas} rodadas) [{alg[-3:]}] erros={r[0].erros[:1]}")
import shutil
shutil.rmtree(tmp, ignore_errors=True)

# 4c) muitas rifas: 5000 numeros em A3 (desempenho)
import time
prep = core.preparar(EX / "template_exemplo_1_rifa.pdf", EX / "digitos_exemplo.pdf").com_folha("A3", 5)
t0 = time.time()
r = core.gerar(core.Trabalho(saida=SAIDA / "muitas", nome="MUITAS", inicio=1, fim=5000), prep)
verifica(all(x.ok for x in r) and r[0].paginas == 500, f"5000 rifas em A3 ({prep.disp.n}/folha): {r[0].paginas} paginas em {time.time() - t0:.1f} s")

# 5) imagens das folhas (para ver)
for nome, papel in (("U-A4-5-pdf", "A4"),):
    pass
prep = core.preparar(EX / "template_exemplo_1_rifa.pdf", EX / "digitos_exemplo.pdf")
for nome, ex_tpl in (("a4_5", None),):
    (SAIDA / "folha_a4.png").write_bytes(core.pagina_previa(prep.com_folha("A4", 5), 1, 4, 5, dpi=100))
print("\nRESULTADO:", "OK" if not falhas else f"FALHOU ({len(falhas)})")
sys.exit(1 if falhas else 0)
