"""Grava o video tutorial (assets/video/tutorial_<lingua>.mp4) com a propria aplicacao.

A janela REAL e comandada passo a passo (sem abrir os dialogos de ficheiros do Windows: mostra-se o rato a clicar em
«Escolher» e passa-se ao resultado), fotografada, e cada fotograma e composto com PIL: o painel dos passos, a legenda,
o realce da zona e um cursor animado. O video segue um guiao curto, sem som (legendas grandes).

Precisa de um ffmpeg (so para gravar o video; nao vai na app): variavel FFMPEG com o caminho, ou `pip install
imageio-ffmpeg` no ambiente que corre este script.

Uso (a janela aparece no ecra durante uns minutos; nao mexer; uma lingua por execucao):
    python testes/fazer_video.py pt     (depois: python testes/fazer_video.py en)
"""
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
import ambiente  # noqa: F401,E402  (poe ..\src no sys.path)
sys.setswitchinterval(0.0005)
from tkinter import messagebox

messagebox.showwarning = messagebox.showerror = lambda *a, **k: print("MSG:", str(a[1])[:90])
messagebox.askyesno = lambda *a, **k: True
messagebox.showinfo = lambda *a, **k: None
from PIL import Image, ImageDraw, ImageFont, ImageGrab

import app as A
import core
from core import i18n
import icones

EX = BASE / "exemplos"
SAIDA_VIDEO = BASE / "assets" / "video"
MOSTRAR_PASTA = "C:\\Rifas\\Exemplo"
TPL_MOSTRAR, TPL1_MOSTRAR = MOSTRAR_PASTA + "\\rifa-exemplo.pdf", MOSTRAR_PASTA + "\\uma-rifa.pdf"
ALG_MOSTRAR = MOSTRAR_PASTA + "\\algarismos.pdf"
NOME = "RIFA EXEMPLO"

FPS = 15
LARG, ALT = 1920, 1080
APP_X, APP_Y, APP_W, APP_H = 36, 100, 1260, 900          # onde cabe a janela da app
FUNDO, PAINEL = (22, 31, 37), (34, 46, 54)
BRANCO, CINZA, VERDE, LARANJA, VERDE_OK = (255, 255, 255), (178, 192, 199), (17, 118, 122), (240, 126, 24), (96, 205, 134)
FONTES = Path(os.environ.get("RIFAS_FONTES") or Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts")   # pasta das letras do sistema

TEXTOS = {
    "pt": {
        "titulo": "Gerador de Rifas", "sub": "Tutorial em vídeo",
        "passos": ["Template", "Algarismos", "Números", "Pasta e nome", "Pré-visualizar", "Gerar", "Só uma rifa?"],
        "t": ["Escolha o template", "Escolha os algarismos 0–9", "Diga que números quer", "Pasta e nome dos ficheiros",
              "Pré-visualizar", "Gerar", "O template só tem uma rifa?"],
        "d": ["O PDF do Canva, com os números de exemplo 0001, 0002, 0003…",
              "Um ficheiro com 0123456789 na mesma letra do template (PDF, PNG ou JPG).",
              "Por exemplo de 1 a 300, em PDFs de 100 números cada um.",
              "Escolha a pasta e escreva o nome. O programa nunca escolhe o nome por si.",
              "Confira a letra, o tamanho e a posição dos números antes de gerar tudo.",
              "Cada PDF é verificado automaticamente. Já pode imprimir! «Limpar tudo» deixa tudo pronto para a próxima rifa.",
              "Basta uma rifa por página: o programa enche a folha com cópias e numera-as."],
        "fim_t": "Pronto!", "fim_d": "Mais ajuda com imagens: menu Ajuda › Tutorial passo a passo (F1)",
    },
    "en": {
        "titulo": "Raffle Generator", "sub": "Video tutorial",
        "passos": ["Template", "Digits", "Numbers", "Folder and name", "Preview", "Generate", "Only one ticket?"],
        "t": ["Choose the template", "Choose the digits 0–9", "Say which numbers you want", "Folder and file name",
              "Preview", "Generate", "Does the template have only one ticket?"],
        "d": ["The PDF from Canva, with the sample numbers 0001, 0002, 0003…",
              "A file with 0123456789 in the same font as the template (PDF, PNG or JPG).",
              "For example 1 to 300, in PDFs of 100 numbers each.",
              "Choose the folder and type the name. The program never picks a name for you.",
              "Check the font, size and position of the numbers before generating everything.",
              "Every PDF is checked automatically. Ready to print! “Clear all” gets everything ready for the next raffle.",
              "One ticket per page is enough: the program fills the sheet with copies and numbers them."],
        "fim_t": "Done!", "fim_d": "More help with pictures: Help menu › Step-by-step tutorial (F1)",
    },
}


def fonte(tam: int, negrito: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTES / ("segoeuib.ttf" if negrito else "segoeui.ttf")), tam)


def quebrar(d: ImageDraw.ImageDraw, texto: str, f, largura: int) -> list:
    linhas, atual = [], ""
    for p in texto.split():
        teste = (atual + " " + p).strip()
        if d.textlength(teste, font=f) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    return linhas + [atual] if atual else linhas


def ffmpeg_exe() -> str:
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


class Gravador:
    def __init__(self, lg: str, destino: Path) -> None:
        self.lg, self.tx = lg, TEXTOS[lg]
        i18n.definir(lg)
        self.tmp = Path(tempfile.mkdtemp(prefix="video_"))
        self.a = A.App(usar_config=False)
        a = self.a
        a.geometry("1240x900+20+5")
        a.attributes("-topmost", True)
        orig = a._trabalho
        tmp = self.tmp / "pdfs"

        def trabalho_tmp():                 # os PDFs vao para uma pasta temporaria; o ecra mostra a pasta de exemplo
            tr = orig()
            tr.saida = tmp
            return tr
        a._trabalho = trabalho_tmp
        adicionar = core.Documento.adicionar_linha

        def devagar(self_, linha):          # so no video: a barra de progresso demora o suficiente para se ver
            adicionar(self_, linha)
            time.sleep(0.03)
        core.Documento.adicionar_linha = devagar
        self._adicionar = adicionar
        destino.parent.mkdir(parents=True, exist_ok=True)
        self.proc = subprocess.Popen(
            [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{LARG}x{ALT}",
             "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", str(destino)], stdin=subprocess.PIPE)
        self.passo, self.feitos = -1, set()
        self.cur = (APP_X + APP_W / 2, APP_Y + APP_H / 2)
        self.img, self.esc = None, 1.0
        self._painel: dict = {}
        self.fundo = Image.new("RGB", (LARG, ALT), FUNDO)
        d = ImageDraw.Draw(self.fundo)
        d.text((APP_X, 28), self.tx["titulo"], font=fonte(40, True), fill=BRANCO)
        d.text((APP_X + d.textlength(self.tx["titulo"], font=fonte(40, True)) + 22, 38), "· " + self.tx["sub"],
               font=fonte(30), fill=CINZA)

    # -- fotografar e compor
    def bombear(self, seg: float) -> None:
        t0 = time.time()
        while time.time() - t0 < seg:
            self.a.update()
            time.sleep(0.02)

    def capturar(self) -> None:
        a = self.a
        a.update()
        x, y, w, h = a.winfo_rootx(), a.winfo_rooty(), a.winfo_width(), a.winfo_height()
        im = ImageGrab.grab((x, y, x + w, y + h)).convert("RGB")
        self.esc = min(APP_W / w, APP_H / h, 1.0)
        if self.esc < 1:
            im = im.resize((round(w * self.esc), round(h * self.esc)), Image.LANCZOS)
        self.img = im

    def caixa(self, w, margem: int = 6) -> tuple:
        """Retangulo de um widget no ecra do video."""
        a, e = self.a, self.esc
        x0 = (w.winfo_rootx() - a.winfo_rootx()) * e + APP_X
        y0 = (w.winfo_rooty() - a.winfo_rooty()) * e + APP_Y
        return (x0 - margem, y0 - margem, x0 + w.winfo_width() * e + margem, y0 + w.winfo_height() * e + margem)

    def centro(self, w) -> tuple:
        c = self.caixa(w, 0)
        return ((c[0] + c[2]) / 2, (c[1] + c[3]) / 2)

    def painel(self) -> Image.Image:
        chave = (self.passo, frozenset(self.feitos))
        if chave in self._painel:
            return self._painel[chave]
        px, py, pw = 1330, 100, LARG - 1330 - 36
        im = Image.new("RGB", (pw, 900), PAINEL)
        d = ImageDraw.Draw(im)
        y = 28
        for i, nome in enumerate(self.tx["passos"]):
            atual = i == self.passo
            if atual:
                d.rounded_rectangle((12, y - 6, pw - 12, y + 50), radius=14, fill=VERDE)
            cor_circ = VERDE_OK if i in self.feitos else (LARANJA if atual else (84, 100, 110))
            d.ellipse((26, y, 70, y + 44), fill=cor_circ)
            marca = "✓" if i in self.feitos else str(i + 1)
            f = fonte(26, True)
            d.text((48, y + 22), marca, font=f, fill=BRANCO if i not in self.feitos else FUNDO, anchor="mm")
            d.text((88, y + 22), nome, font=fonte(29, atual), fill=BRANCO if (atual or i in self.feitos) else CINZA,
                   anchor="lm")
            y += 66
        if self.passo >= 0:
            y += 20
            d.line((24, y, pw - 24, y), fill=(70, 86, 96), width=2)
            y += 24
            fb = fonte(38, True)
            for linha in quebrar(d, self.tx["t"][self.passo], fb, pw - 56):
                d.text((28, y), linha, font=fb, fill=LARANJA)
                y += 48
            y += 8
            fd = fonte(30)
            for linha in quebrar(d, self.tx["d"][self.passo], fd, pw - 56):
                d.text((28, y), linha, font=fd, fill=BRANCO)
                y += 42
        self._painel[chave] = im
        return im

    def compor(self, cursor=None, ripple: int = 0, destaque=None) -> Image.Image:
        f = self.fundo.copy()
        d = ImageDraw.Draw(f)
        w, h = self.img.size
        d.rounded_rectangle((APP_X + 6, APP_Y + 8, APP_X + w + 6, APP_Y + h + 8), radius=6, fill=(12, 17, 20))
        f.paste(self.img, (APP_X, APP_Y))
        f.paste(self.painel(), (1330, 100))
        d = ImageDraw.Draw(f)
        if destaque:        # nunca fora da janela da app
            x0, y0, x1, y1 = destaque
            destaque = (max(x0, APP_X), max(y0, APP_Y), min(x1, APP_X + w), min(y1, APP_Y + h))
            d.rounded_rectangle(destaque, radius=10, outline=LARANJA, width=5)
        if ripple:
            cx, cy = cursor
            r = 8 + ripple * 6
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=LARANJA, width=5)
        if cursor:
            x, y = cursor
            seta = [(0, 0), (0, 30), (8, 23), (14, 36), (20, 33), (14, 21), (24, 21)]
            seta = [(x + 1.15 * px_, y + 1.15 * py_) for px_, py_ in seta]
            d.polygon([(px_ + 2, py_ + 3) for px_, py_ in seta], fill=(0, 0, 0))
            d.polygon(seta, fill=BRANCO, outline=(0, 0, 0))
        return f

    def emitir(self, frame: Image.Image, seg: float) -> None:
        b = frame.tobytes()
        for _ in range(max(1, round(seg * FPS))):
            self.proc.stdin.write(b)

    def mostrar(self, seg: float, cursor=None, destaque=None, ripple: int = 0) -> None:
        self.capturar()
        self.emitir(self.compor(cursor or self.cur, ripple, destaque), seg)

    # -- gestos
    def mover(self, alvo: tuple, seg: float = 0.7, destaque=None) -> None:
        x0, y0 = self.cur
        n = max(2, round(seg * FPS))
        for i in range(1, n + 1):
            u = i / n
            e = u * u * (3 - 2 * u)
            self.cur = (x0 + (alvo[0] - x0) * e, y0 + (alvo[1] - y0) * e)
            self.emitir(self.compor(self.cur, 0, destaque), 1 / FPS)

    def clicar(self, w, depois=None, destaque=None, espera: float = 0.5) -> None:
        self.capturar()
        self.mover(self.centro(w), 0.8, destaque)
        for r in range(1, 7):
            self.emitir(self.compor(self.cur, r, destaque), 1 / FPS)
        if depois:
            depois()
        self.bombear(0.05)
        self.mostrar(espera, destaque=destaque)

    def escrever(self, var, texto: str, entry=None, destaque=None) -> None:
        for i in range(1, len(texto) + 1):
            var.set(texto[:i])
            if entry is not None and not entry.get() == texto[:i]:      # entradas sem variavel (nome dos ficheiros)
                entry.delete(0, "end")
                entry.insert(0, texto[:i])
            self.bombear(0.02)
            self.mostrar(0.11, destaque=destaque)

    def esperar(self, cond, destaque=None, max_video: float = 1.6, max_real: float = 30.0) -> None:
        t0, gravado = time.time(), 0.0
        while not cond() and time.time() - t0 < max_real:
            self.bombear(0.2)
            if gravado < max_video:
                self.mostrar(0.2, destaque=destaque)
                gravado += 0.2
        self.bombear(0.2)

    def novo_passo(self, i: int) -> None:
        if self.passo >= 0:
            self.feitos.add(self.passo)
        self.passo = i

    def cartao_titulo(self, titulo: str, sub: str, seg: float, icone: bool = True) -> None:
        f = Image.new("RGB", (LARG, ALT), FUNDO)
        d = ImageDraw.Draw(f)
        if icone:
            ic = icones.bilhete(220, (255, 255, 255), VERDE)
            f.paste(ic, ((LARG - ic.width) // 2, 250), ic if ic.mode == "RGBA" else None)
        d.text((LARG / 2, 560), titulo, font=fonte(92, True), fill=BRANCO, anchor="mm")
        for k, linha in enumerate(quebrar(d, sub, fonte(44), 1500)):
            d.text((LARG / 2, 660 + 56 * k), linha, font=fonte(44), fill=LARANJA if k == 0 else CINZA, anchor="mm")
        self.emitir(f, seg)

    # -- o guiao
    def gravar(self) -> None:
        a, tx = self.a, self.tx
        self.bombear(1.2)
        self.img = None
        self.cartao_titulo(tx["titulo"], tx["sub"], 3.0)
        a.v_fim.set("1000")
        self.capturar()
        self.emitir(self.compor(), 1.0)

        # 1. template
        self.novo_passo(0)
        card = lambda k: self.caixa(a.w_ajuda[k], 4)
        self.mostrar(2.0, destaque=card("c1"))

        def analisar(tpl, alg, tpl_ecra, alg_ecra):
            """Analisa os ficheiros verdadeiros mas o ecra mostra caminhos genericos (o motor ja leu os verdadeiros)."""
            a.v_template.set(str(tpl) if tpl else "")
            a.v_alg.set(str(alg) if alg else "")
            a._analisar()
            a.v_template.set(tpl_ecra)
            a.v_alg.set(alg_ecra)

        def escolher_template():
            analisar(EX / "template_exemplo.pdf", None, TPL_MOSTRAR, "")
        self.clicar(a.b_escolher[0], escolher_template, destaque=card("c1"))
        self.esperar(lambda: a.info is not None, card("c1"))
        self.mostrar(3.5, destaque=card("c1"))

        # 2. algarismos
        self.novo_passo(1)
        self.mostrar(2.0, destaque=card("c2"))

        def escolher_alg():
            analisar(EX / "template_exemplo.pdf", EX / "digitos_exemplo.pdf", TPL_MOSTRAR, ALG_MOSTRAR)
        self.clicar(a.b_escolher[1], escolher_alg, destaque=card("c2"))
        self.esperar(lambda: a.prep is not None, card("c2"))
        self.mostrar(3.5, destaque=card("c2"))

        # 3. numeros
        self.novo_passo(2)
        self.mostrar(1.5, destaque=card("c3"))
        a.v_fim.set("")
        self.clicar(a.e_numeros[1], destaque=card("c3"), espera=0.2)
        self.escrever(a.v_fim, "300", destaque=card("c3"))
        a.v_max.set("")
        self.clicar(a.e_max, destaque=card("c3"), espera=0.2)
        self.escrever(a.v_max, "100", destaque=card("c3"))
        self.mostrar(3.5, destaque=card("c3"))

        # 4. destino
        self.novo_passo(3)
        self.mostrar(1.5, destaque=card("c4"))
        self.clicar(a.b_escolher[3], lambda: a.v_saida.set(MOSTRAR_PASTA), destaque=card("c4"))
        self.mostrar(1.2, destaque=card("c4"))
        self.clicar(a.e_nome, destaque=card("c4"), espera=0.2)
        self.escrever(a.v_nome, NOME, entry=a.e_nome, destaque=card("c4"))
        self.mostrar(2.5, destaque=card("c4"))

        # 5. pre-visualizar
        self.novo_passo(4)
        self.mostrar(1.5, destaque=self.caixa(a.b_previa, 6))
        self.clicar(a.b_previa, a._previa, destaque=self.caixa(a.b_previa, 6), espera=0.3)
        self.esperar(lambda: a.st_titulo[0] == "previa_titulo_n", self.caixa(a.visor, 2))
        self.mostrar(3.0, destaque=self.caixa(a.visor, 2))
        # zoom no numero do primeiro bilhete
        v = a.visor
        s = next(sl for sl in a.prep.info.slots if sl.campo == 1 and sl.rot == 0)
        k = 200 / 72                                         # a pre-visualizacao e desenhada a 200 dpi
        W, H = v.tela.winfo_width(), v.tela.winfo_height()
        px = (s.origem[0] + s.avanco / 2) * k
        py = (s.origem[1] - s.tamanho * 0.35) * k
        z0 = v.zoom
        cx = (px - (v.cx or 0)) * z0 + W / 2
        cy = (py - (v.cy or 0)) * z0 + H / 2
        alvo = (v.tela.winfo_rootx() - a.winfo_rootx() + cx, v.tela.winfo_rooty() - a.winfo_rooty() + cy)
        alvo = (APP_X + alvo[0] * self.esc, APP_Y + alvo[1] * self.esc)
        self.mover(alvo, 0.9, self.caixa(v, 2))
        for _ in range(5):
            v.zoom_por(1.45, cx, cy)
            self.bombear(0.05)
            self.mostrar(0.35, cursor=alvo, destaque=self.caixa(v, 2))
        self.mostrar(2.5, cursor=alvo, destaque=self.caixa(v, 2))
        v.ajustar()
        self.bombear(0.2)
        self.mostrar(1.0, cursor=alvo, destaque=self.caixa(v, 2))

        # 6. gerar
        a.rolavel.tela.yview_moveto(1.0)       # mostra o botao, a barra de progresso e o registo
        self.bombear(0.4)
        self.novo_passo(5)
        self.mostrar(1.0, destaque=self.caixa(a.b_gerar, 6))
        self.clicar(a.b_gerar, a._gerar, destaque=self.caixa(a.b_gerar, 6), espera=0.1)
        t0 = time.time()
        while a.a_gerar and time.time() - t0 < 60:
            self.bombear(0.05)
            self.mostrar(0.15, destaque=self.caixa(a.f_acoes, 4))
        self.bombear(0.3)
        self.mostrar(3.5, destaque=self.caixa(a.f_acoes, 4))
        self.clicar(a.b_pasta, lambda: None, destaque=self.caixa(a.f_acoes, 4), espera=1.0)
        self.clicar(a.b_limpar, a._limpar_tudo, destaque=self.caixa(a.f_acoes, 4), espera=0.3)
        self.bombear(0.4)
        self.mostrar(3.0)

        # 7. so uma rifa
        a.rolavel.tela.yview_moveto(0)
        self.bombear(0.4)
        self.novo_passo(6)
        self.mostrar(1.5, destaque=card("c1"))

        def escolher_uma():
            a.v_porfolha.set("")
            analisar(EX / "template_exemplo_1_rifa.pdf", EX / "digitos_exemplo.pdf", TPL1_MOSTRAR, ALG_MOSTRAR)
        self.clicar(a.b_escolher[0], escolher_uma, destaque=card("c1"))
        self.esperar(lambda: a.prep is not None and a.prep.info.n_campos == 1, card("c1"))
        self.bombear(0.4)
        self.mostrar(4.0, destaque=card("c1"))
        a.rolavel.tela.yview_moveto(1.0)
        self.bombear(0.4)
        self.clicar(a.b_previa, a._previa, destaque=self.caixa(a.b_previa, 6), espera=0.2)
        self.esperar(lambda: a.b_previa.cget("state") == "normal", self.caixa(a.visor, 2))
        self.mostrar(3.5, destaque=self.caixa(a.visor, 2))
        # papel A3: cabem mais
        a.rolavel.tela.yview_moveto(0)
        self.bombear(0.4)
        self.clicar(a.m_papel, lambda: (a.v_papel.set("A3"), a.m_papel.set("A3"), a._recalcular_folha()),
                    destaque=card("c1"), espera=2.0)
        a.rolavel.tela.yview_moveto(1.0)
        self.bombear(0.4)
        self.clicar(a.b_previa, a._previa, destaque=self.caixa(a.b_previa, 6), espera=0.2)
        self.esperar(lambda: a.st_titulo[0] == "previa_titulo_n" and a.b_previa.cget("state") == "normal",
                     self.caixa(a.visor, 2))
        self.mostrar(4.0, destaque=self.caixa(a.visor, 2))
        self.feitos.add(6)
        self.mostrar(1.0)

        # fim
        self.cartao_titulo(tx["fim_t"], tx["fim_d"], 5.0)

    def fechar(self) -> None:
        core.Documento.adicionar_linha = self._adicionar
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=600)
        finally:
            self.a.destroy()
            import shutil
            shutil.rmtree(self.tmp, ignore_errors=True)


def main() -> None:
    langs = sys.argv[1:] or ["pt", "en"]
    for lg in langs:
        destino = SAIDA_VIDEO / f"tutorial_{lg}.mp4"
        g = Gravador(lg, destino)
        t0 = time.time()
        try:
            g.gravar()
        finally:
            g.fechar()
        print(f"{lg}: {destino} {destino.stat().st_size / 1e6:.1f} MB em {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
