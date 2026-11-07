"""Testa o botao «Limpar tudo» (fim da geracao): gera, limpa e confirma que tudo voltou ao estado inicial.
Uso: python testes/teste_limpar.py <pasta_de_saida>   (a janela aparece no ecra durante um minuto)"""
import sys, time
from pathlib import Path
sys.path.insert(0, r"Z:\projects\rifas\app")
sys.setswitchinterval(0.0005)
from tkinter import messagebox
messagebox.showwarning = messagebox.showerror = lambda *a, **k: print("MSG", a[1][:80])
messagebox.askyesno = lambda *a, **k: True
from PIL import ImageGrab
import app as A, core, i18n

EX = Path(r"Z:\projects\rifas\app\exemplos")
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
a = A.App(usar_config=False)
a.geometry("1240x900+20+5"); a.attributes("-topmost", True)

def pump(seg, ate=None):
    t0 = time.time()
    while time.time() - t0 < seg:
        a.update(); time.sleep(0.03)
        if ate and ate(): break

def shot(n):
    a.update(); x, y, w, h = a.winfo_rootx(), a.winfo_rooty(), a.winfo_width(), a.winfo_height()
    ImageGrab.grab((x, y, x + w, y + h)).save(OUT / n)

def estado():
    return dict(tpl=a.v_template.get(), alg=a.v_alg.get(), saida=a.v_saida.get(), nome=a.v_nome.get(), nome_entry=a.e_nome.get(),
                de=a.v_inicio.get(), ate=a.v_fim.get(), dig=a.v_digitos.get(), mx=a.v_max.get(), modo=a.modo,
                prep=a.prep is not None, info=a.info is not None, visor_img=a.visor.imagem is not None,
                log=len(a.log_linhas), prog=a.prog, estado=a.st_estado, pos_visivel=a.f_pos.winfo_ismapped(),
                folha_vis=a.f_folha.winfo_ismapped(), gerar=a.b_gerar.cget("state"), previa=a.b_previa.cget("state"))

for tpl in ("template_exemplo.pdf", "template_exemplo_1_rifa.pdf"):
    a.v_template.set(str(EX / tpl)); a.v_alg.set(str(EX / "digitos_exemplo.pdf"))
    a.v_nome.set("TESTE"); a.e_nome.insert(0, "TESTE"); a.v_saida.set(str(OUT / "pdfs")); a.v_fim.set("23"); a.v_max.set("10")
    a._set_modo("unico"); a.seg_modo.set(i18n.t("modo_unico"))
    a._analisar(); pump(15, lambda: a.prep is not None)
    a._previa(); pump(8, lambda: a.st_titulo[0] == "previa_titulo_n")
    a._gerar(); pump(30, lambda: not a.a_gerar and a.st_estado and a.st_estado[0] == "est_ok"); pump(0.5)
    print(tpl, "antes:", {k: v for k, v in estado().items() if k in ("prep", "visor_img", "log", "pos_visivel", "folha_vis")})
    shot(f"antes_{tpl[:-4]}.png")
    a.b_limpar.invoke(); pump(0.8)
    e = estado(); print("depois:", e); shot(f"depois_{tpl[:-4]}.png")
    assert e["tpl"] == e["alg"] == e["saida"] == e["nome"] == e["nome_entry"] == "", e
    assert (e["de"], e["ate"], e["dig"], e["mx"], e["modo"]) == ("1", "1000", "4", "300", "varios"), e
    assert not e["prep"] and not e["info"] and not e["visor_img"] and e["log"] == 0 and e["prog"] == 0 and e["estado"] is None, e
    assert not e["pos_visivel"] and not e["folha_vis"] and e["gerar"] == "disabled" and e["previa"] == "disabled", e
# recomeca do zero: uma nova geracao tem de funcionar
a.v_template.set(str(EX / "template_exemplo.pdf")); a.v_alg.set(str(EX / "digitos_exemplo.pdf"))
a.v_nome.set("OUTRA"); a.v_saida.set(str(OUT / "pdfs2")); a.v_fim.set("12")
a._analisar(); pump(15, lambda: a.prep is not None)
a._gerar(); pump(30, lambda: not a.a_gerar and a.st_estado and a.st_estado[0] == "est_ok")
print("nova geracao:", a.st_estado[0], [p.name for p in (OUT / "pdfs2").glob("*.pdf")], "limpar visivel:", a.f_pos.winfo_ismapped())
# durante a geracao o botao nao aparece e _limpar_tudo e ignorado
a._limpar_tudo(); pump(0.3)
a.destroy()
print("OK")
