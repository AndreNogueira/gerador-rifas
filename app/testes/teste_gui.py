"""Percorre a interface real: template + algarismos, pre-visualizacao com zoom/expansao, 18 linguas,
nome obrigatorio e geracao.
Uso: python teste_gui.py <pasta_saida> <template.pdf> <algarismos.pdf|png> [fim=5000] [unico|<max por ficheiro>]
(capturas de ecra em <pasta_saida>)"""
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.setswitchinterval(0.0005)
from tkinter import messagebox

mensagens = []
messagebox.showwarning = messagebox.showerror = lambda *a, **k: mensagens.append(str(a[1]).replace("\n", " / ")[:90])
messagebox.askyesno = lambda *a, **k: True
from PIL import ImageGrab

import app as A
import i18n

T, tpl, alg = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
FIM = sys.argv[4] if len(sys.argv) > 4 else "5000"
MAXF = sys.argv[5] if len(sys.argv) > 5 else "unico"
T.mkdir(parents=True, exist_ok=True)
shutil.rmtree(T / "gui_pdfs", ignore_errors=True)
a = A.App(usar_config=False)
a.geometry("1240x880+30+10")


def pump(sec, until=None):
    t0 = time.time()
    while time.time() - t0 < sec:
        a.update()
        time.sleep(0.03)
        if until and until():
            break


def shot(n):
    a.update_idletasks()
    x, y, w, h = a.winfo_rootx(), a.winfo_rooty(), a.winfo_width(), a.winfo_height()
    ImageGrab.grab((x, y, x + w, y + h)).save(T / f"{n}.png")


pump(1)
print("nome inicial vazio:", repr(a.v_nome.get()))
a.v_template.set(tpl)
a.v_saida.set(str(T / "gui_pdfs"))
a.v_fim.set(FIM)
a._analisar()
pump(8, lambda: a.info is not None)
print("sem algarismos ->", a.l_alg.cget("text")[:50], "| gerar:", a.b_gerar.cget("state"), "| digitos auto:", a.v_digitos.get())
a.v_alg.set(alg)
a._analisar()
pump(10, lambda: a.prep is not None)
print("com algarismos ->", a.l_alg.cget("text")[:60], "| gerar:", a.b_gerar.cget("state"))
a._previa()
pump(5, lambda: a.visor.imagem is not None and "previa" in a.st_titulo[0] and a.st_titulo[0] == "previa_titulo_n")
print("visor:", a.visor.imagem.size if a.visor.imagem else None, "zoom", round(a.visor.zoom, 2), "fit", a.visor.zoom_fit)
shot("gui_pt")
# zoom
a.visor.zoom_por(2.0); pump(0.5)
z2 = a.visor.zoom
a.visor.zoom_por(1 / 4); pump(0.3)
print("zoom: x2 ->", round(z2, 2), "depois /4 ->", round(a.visor.zoom, 2), "| fit:", a.visor.zoom_fit)
a.visor.zoom_por(3.0); pump(0.5); shot("gui_zoom")
a.visor.ajustar(); pump(0.3)
print("ajustar -> fit:", a.visor.zoom_fit)
# expandir / reduzir
a.visor._expandir(); pump(0.6); shot("gui_expandido")
print("expandido: definicoes visiveis =", a.rolavel.winfo_ismapped(), "| largura do visor =", a.visor.winfo_width())
a.visor._expandir(); pump(0.8)
print("reduzido: definicoes visiveis =", a.rolavel.winfo_ismapped(), "| largura das definicoes =", a.rolavel.winfo_width())
# 18 linguas
for lg in i18n.LINGUAS:
    a._mudar_lingua(i18n.LINGUAS[lg])
    pump(0.6)
    ok = a.title() == i18n.t("app_nome")
    print(f"  {lg}: {a.title()!r:34} {a.b_gerar.cget('text')!r:22} {'ok' if ok else 'ERRO'}")
    if lg in ("ja", "hi", "zh", "ru", "el", "de"):
        shot(f"gui_{lg}")
a._mudar_lingua(i18n.LINGUAS["pt"])
pump(0.5)
# tema escuro
a._definir_tema("dark")
pump(0.6)
shot("gui_escuro")
a._definir_tema("light")
# nome obrigatorio
mensagens.clear()
a._gerar()
pump(0.3)
print("sem nome -> gerar bloqueado:", not a.a_gerar, "| aviso:", mensagens[-1:] )
# gerar
a.v_nome.set("Rifa Teste")
if MAXF == "unico":
    a._set_modo("unico")
else:
    a.v_max.set(MAXF)
t_gerar = time.time()
a._gerar()
pump(0.5)
print("durante:", a.b_gerar.cget("text"), "| menu lingua:", a.m_lingua.cget("state"))
a._mudar_lingua("English")
print("lingua apos tentativa durante a geracao:", i18n.atual())
pump(280, lambda: not a.a_gerar)
print(f"tempo de geracao: {time.time() - t_gerar:.1f}s")
print("fim:", a.l_estado.cget("text"), "| pasta visivel:", a.b_pasta.winfo_ismapped(),
      "|", sorted(p.name for p in (T / "gui_pdfs").glob("*"))[:6])
shot("gui_fim")
a.destroy()
