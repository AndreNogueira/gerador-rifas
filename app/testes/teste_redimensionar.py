"""Mede o redimensionamento da janela e da divisoria e confirma que nao ficam artefactos visuais.

Para cada cenario (encolher/alargar a janela, arrastar a divisoria, expandir o visor, tema escuro) compara a
captura logo a seguir com a captura depois de forcar a repintura completa do Windows: tem de ser igual.
Uso: python teste_redimensionar.py <pasta_saida>
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.setswitchinterval(0.0005)
from tkinter import messagebox

messagebox.showwarning = messagebox.showerror = lambda *a, **k: print("MSG:", str(a[1])[:90])
from PIL import ImageChops, ImageGrab

import app as A
import widgets

T = Path(sys.argv[1])
T.mkdir(parents=True, exist_ok=True)
ex = Path(__file__).resolve().parent.parent / "exemplos"
a = A.App(usar_config=False)
a.geometry("1240x880+30+10")
a.attributes("-topmost", True)


def pump(sec, until=None):
    t0 = time.time()
    while time.time() - t0 < sec:
        a.update()
        time.sleep(0.03)
        if until and until():
            break


def captura():
    a.update()
    x, y, w, h = a.winfo_rootx(), a.winfo_rooty(), a.winfo_width(), a.winfo_height()
    return ImageGrab.grab((x, y, x + w, y + h)).convert("RGB")


def comparar(nome):
    pump(0.35)                                   # deixa passar os redesenhos "finais" (140 ms)
    antes = captura()
    widgets.repintar_tudo(a)
    pump(0.35)
    depois = captura()
    if antes.size != depois.size:
        print(f"  {nome}: tamanhos diferentes")
        return False
    h = ImageChops.difference(antes, depois).convert("L").histogram()
    dif = sum(h[24:])
    ok = dif < antes.width * antes.height * 0.0005
    print(f"  {nome}: {'ok' if ok else 'ARTEFACTOS'} ({dif} px diferentes)")
    if not ok:
        antes.save(T / f"art_{nome}_antes.png")
        depois.save(T / f"art_{nome}_depois.png")
    return ok


pump(1.5)
a.v_template.set(str(ex / "template_exemplo.pdf"))
a.v_alg.set(str(ex / "digitos_exemplo.pdf"))
a._analisar()
pump(10, lambda: a.prep is not None)
a._previa()
pump(6, lambda: a.st_titulo[0] == "previa_titulo_n")
pump(0.5)

tudo = []
t0 = time.perf_counter()
for w in list(range(1240, 1000, -16)) + list(range(1000, 1240, 16)):
    a.geometry(f"{w}x880")
    a.update()
print(f"janela (largura): {(time.perf_counter() - t0) / 30 * 1000:.0f} ms/passo")
tudo.append(comparar("largura"))
t0 = time.perf_counter()
for h in list(range(880, 700, -12)) + list(range(700, 880, 12)):
    a.geometry(f"1240x{h}")
    a.update()
print(f"janela (altura): {(time.perf_counter() - t0) / 30 * 1000:.0f} ms/passo")
tudo.append(comparar("altura"))
a.geometry("1000x700")
tudo.append(comparar("encolhida"))
a.geometry("1500x900+10+10")
tudo.append(comparar("grande"))
a.geometry("1240x880+30+10")
pump(0.4)


class E:
    def __init__(self, x):
        self.x_root = x


x0 = a.divisoria.winfo_rootx()
a._div_carregar(E(x0))
t0 = time.perf_counter()
passos = list(range(x0, x0 - 100, -10)) + list(range(x0 - 100, x0 + 150, 10))
for x in passos:
    a._div_mover(E(x))
    a.update()
print(f"divisoria (arrastar): {(time.perf_counter() - t0) / len(passos) * 1000:.0f} ms/passo")
a._div_largar(E(x0 + 150))
tudo.append(comparar("divisoria"))
a.visor._expandir()
pump(0.5)
tudo.append(comparar("expandido"))
a.visor._expandir()
pump(0.5)
tudo.append(comparar("reduzido"))
a.visor.zoom_por(2.5)
tudo.append(comparar("zoom"))
a._definir_tema("dark")
a.geometry("1240x880+30+10")
pump(1.0)
tudo.append(comparar("escuro"))
a._alternar_tema()
pump(0.8)
tudo.append(comparar("claro_de_novo"))
print("RESULTADO:", "OK" if all(tudo) else "FALHOU")
a.destroy()
