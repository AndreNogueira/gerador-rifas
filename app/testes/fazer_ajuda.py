"""Gera as imagens do tutorial em assets/ajuda/ a partir da propria aplicacao (capturas reais da janela).

- modelo.jpg  : o template de exemplo com os numeros de exemplo realcados (igual em todas as linguas)
- digitos.png : o ficheiro de algarismos de exemplo, recortado
- <lingua>_a.png / <lingua>_b.png : janela com tudo preenchido e pre-visualizacao / depois de gerar
- ajuda.json  : zonas a recortar de cada captura (passos 1-4, visor, acoes) e a escala do ecra

Uso (a janela aparece no ecra durante uns minutos; nao mexer): python testes/fazer_ajuda.py [c | <lingua> ...]
(`c`: so o estado C; uma ou mais linguas: so essas, sem refazer as outras nem o modelo e os algarismos)
"""
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ambiente  # noqa: F401,E402  (poe ..\src no sys.path)
sys.setswitchinterval(0.0005)
from tkinter import messagebox

messagebox.showwarning = messagebox.showerror = lambda *a, **k: print("MSG:", str(a[1])[:90])
messagebox.askyesno = lambda *a, **k: True
from PIL import Image, ImageChops, ImageDraw, ImageGrab

import ajuda
import app as A
import core
from core import i18n

BASE = Path(__file__).resolve().parent.parent
EX = BASE / "exemplos"
MOSTRAR = "C:\\Rifas\\Exemplo"       # pasta que aparece nas capturas (generica)
TPL_MOSTRAR = MOSTRAR + "\\rifa-exemplo.pdf"        # idem para os campos do template e dos algarismos
ALG_MOSTRAR = MOSTRAR + "\\algarismos.pdf"
NOME_MOSTRAR = "RIFA EXEMPLO"
PASTA = ajuda.PASTA
PASTA.mkdir(parents=True, exist_ok=True)


def _destacar(tpl: Path, nome: str, recorte) -> None:
    """Imagem do template de exemplo com os numeros de exemplo realcados (a laranja)."""
    info = core.analisar_template(tpl)
    dpi = 100
    im = Image.open(__import__("io").BytesIO(core.png_de_pagina(tpl, dpi))).convert("RGBA")
    k = dpi / 72
    sobre = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sobre)
    for s in info.slots:
        r = s.caixa(2.5)
        d.rounded_rectangle(((r.x0) * k, (r.y0) * k, (r.x1) * k, (r.y1) * k), radius=6, fill=(255, 140, 0, 60),
                            outline=(255, 120, 0, 255), width=3)
    im = Image.alpha_composite(im, sobre).convert("RGB")
    im = im.crop(recorte(im, k))
    im.save(PASTA / nome, quality=88, optimize=True)
    print(nome, im.size)


def modelo() -> None:
    # so os dois primeiros bilhetes da folha de 5
    _destacar(EX / "template_exemplo.pdf", "modelo.jpg", lambda im, k: (0, 0, im.width, int(350 * k)))
    # a pagina com uma so rifa
    _destacar(EX / "template_exemplo_1_rifa.pdf", "modelo1.jpg", lambda im, k: (0, 0, im.width, im.height))
    # o resultado: a folha A4 enchida com copias da rifa
    prep = core.preparar(EX / "template_exemplo_1_rifa.pdf", EX / "digitos_exemplo.pdf").com_folha("A4", core.MARGEM_MM)
    png = core.pagina_previa(prep, 1, 4, 5, dpi=75)
    im = Image.open(__import__("io").BytesIO(png)).convert("RGB")
    ImageDraw.Draw(im).rectangle((0, 0, im.width - 1, im.height - 1), outline=(150, 150, 150))
    im.save(PASTA / "folha.png", optimize=True)
    print("folha.png", im.size)


def digitos() -> None:
    im = Image.open(EX / "digitos_exemplo.png").convert("L")
    bbox = ImageChops.invert(im).getbbox()
    m = 60
    im = im.crop((max(bbox[0] - m, 0), max(bbox[1] - m, 0), min(bbox[2] + m, im.width), min(bbox[3] + m, im.height)))
    im = im.resize((900, round(900 * im.height / im.width)), Image.LANCZOS)
    im.save(PASTA / "digitos.png", optimize=True)
    print("digitos.png", im.size)


def main() -> None:
    so_c = "c" in sys.argv[1:]          # `python testes/fazer_ajuda.py c`: so refaz as capturas do estado C
    pedidas = [x for x in sys.argv[1:] if x in i18n.LINGUAS]       # `python testes/fazer_ajuda.py ca uk`: so estas linguas (junta ao ajuda.json existente)
    linguas = pedidas or list(i18n.LINGUAS)
    if not so_c and not pedidas:
        modelo()
        digitos()
    saida = Path(tempfile.mkdtemp(prefix="ajuda_"))
    a = A.App(usar_config=False)
    altura = min(a.winfo_screenheight() - 80, 1000)
    a.geometry(f"1240x{altura}+20+5")
    a.attributes("-topmost", True)

    def pump(seg, ate=None):
        t0 = time.time()
        while time.time() - t0 < seg:
            a.update()
            time.sleep(0.03)
            if ate and ate():
                break

    def zona(w, margem=4):
        a.update_idletasks()
        x0 = w.winfo_rootx() - a.winfo_rootx() - margem
        y0 = w.winfo_rooty() - a.winfo_rooty() - margem
        x1 = x0 + w.winfo_width() + 2 * margem
        y1 = y0 + w.winfo_height() + 2 * margem
        return [max(x0, 0), max(y0, 0), min(x1, a.winfo_width()), min(y1, a.winfo_height())]

    def captura(nome):
        a.update()
        assert i18n.atual() == lg_atual[0], (lg_atual[0], i18n.atual())      # a lingua nao mudou por si
        assert a.m_lingua.get() == i18n.LINGUAS[lg_atual[0]], "o seletor de lingua mudou"
        x, y, w, h = a.winfo_rootx(), a.winfo_rooty(), a.winfo_width(), a.winfo_height()
        im = ImageGrab.grab((x, y, x + w, y + h)).convert("RGB")
        im.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(PASTA / nome, optimize=True)

    lg_atual = [""]
    try:                      # rato fora da janela (a roda do rato sobre o seletor de lingua pode mudar a lingua)
        import ctypes
        ctypes.windll.user32.SetCursorPos(a.winfo_screenwidth() - 5, a.winfo_screenheight() // 2)
    except Exception:
        pass
    pump(1.5)
    caixas: dict = json.loads((PASTA / "ajuda.json").read_text(encoding="utf-8")) if (so_c or pedidas) else {}
    if not so_c:
        a.v_template.set(str(EX / "template_exemplo.pdf"))
        a.v_alg.set(str(EX / "digitos_exemplo.pdf"))
        a.v_fim.set("300")
        a.v_max.set("100")
        a.v_nome.set(NOME_MOSTRAR)
        a._analisar()
        pump(15, lambda: a.prep is not None)
        assert a.prep is not None, "o template de exemplo nao carregou"
        a.v_template.set(TPL_MOSTRAR)       # so para a captura: o motor ja leu os ficheiros
        a.v_alg.set(ALG_MOSTRAR)
        a._previa()
        pump(8, lambda: a.st_titulo[0] == "previa_titulo_n")
    escala = a._get_window_scaling()
    for lg in ([] if so_c else linguas):
        lg_atual[0] = lg
        a._mudar_lingua(i18n.LINGUAS[lg])
        a.e_nome.focus_set()
        a.focus_force()
        a.visor.ajustar()
        a.log_linhas.clear()
        a.st_estado = None
        a.prog = 0.0
        a.mostrar_pasta = False
        a._reconstruir()
        a.v_saida.set(MOSTRAR)
        pump(1.2)
        a.focus_set()
        # estado A: tudo preenchido + pre-visualizacao
        a.rolavel.tela.yview_moveto(0)
        pump(0.4)
        alvo = {"janela": [0, 0, a.winfo_width(), a.winfo_height()]}
        for k in ("c1", "c2", "c3", "c4", "visor"):
            alvo[k] = zona(a.w_ajuda[k])
        alvo["barra"] = zona(a.visor.barra, 0)
        captura(f"{lg}_a.png")
        estado_a = dict(alvo, escala=escala)
        # estado B: depois de gerar (aqui 1 PDF pequeno, so para mostrar progresso, estado e registo)
        a.v_fim.set("20")
        a._set_modo("unico")
        a.seg_modo.set(i18n.t("modo_unico"))
        a.v_saida.set(str(saida / lg))
        a._gerar()
        pump(30, lambda: not a.a_gerar)
        a.v_saida.set(MOSTRAR)
        pump(0.6)
        a.rolavel.tela.yview_moveto(1.0)
        pump(0.4)
        estado_b = {"janela": [0, 0, a.winfo_width(), a.winfo_height()], "acoes": zona(a.w_ajuda["acoes"]),
                    "escala": escala}
        captura(f"{lg}_b.png")
        a.v_fim.set("300")
        a._set_modo("varios")
        caixas.setdefault(lg, {}).update({"a": estado_a, "b": estado_b})       # junta (as zonas do site, `wa`/`wb`/`wc`, vivem no mesmo ficheiro)
        print(f"  {lg}: ok  A={PASTA / (lg + '_a.png')}", (PASTA / f"{lg}_a.png").stat().st_size // 1024, "KB",
              (PASTA / f"{lg}_b.png").stat().st_size // 1024, "KB", flush=True)
    # estado C: template com UMA so rifa (aparecem o papel, a margem e as rifas por folha); so se guarda o cartao 1
    a.v_template.set(str(EX / "template_exemplo_1_rifa.pdf"))
    a.v_alg.set(str(EX / "digitos_exemplo.pdf"))
    a.v_fim.set("300")
    a._set_modo("varios")
    a._analisar()
    pump(15, lambda: a.prep is not None)
    assert a.prep is not None and a.prep.info.n_campos == 1, "o template de 1 rifa nao carregou"
    a.v_template.set(TPL_MOSTRAR)
    a.v_alg.set(ALG_MOSTRAR)
    a.v_porfolha.set("")
    for lg in linguas:
        lg_atual[0] = lg
        a._mudar_lingua(i18n.LINGUAS[lg])
        a.focus_set()
        a.rolavel.tela.yview_moveto(0)
        pump(1.6)
        esperado = i18n.t("c1_ok_uma", primeiro="0001")[:10]
        assert i18n.atual() == lg and esperado in a.l_template.cget("text"), (lg, i18n.atual(), a.l_template.cget("text"))
        x0, y0, x1, y1 = zona(a.w_ajuda["c1"])
        a.update()
        ax, ay = a.winfo_rootx(), a.winfo_rooty()
        im = ImageGrab.grab((ax + x0, ay + y0, ax + x1, ay + y1)).convert("RGB")
        im.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(PASTA / f"{lg}_c.png", optimize=True)
        caixas[lg]["c"] = {"c1": [0, 0, im.width, im.height], "escala": escala}
        print(f"  {lg}: c ok", im.size, flush=True)
    (PASTA / "ajuda.json").write_text(json.dumps(caixas, ensure_ascii=False), encoding="utf-8")
    a.destroy()
    shutil.rmtree(saida, ignore_errors=True)
    print("tutorial: imagens geradas em", PASTA)


if __name__ == "__main__":
    main()
