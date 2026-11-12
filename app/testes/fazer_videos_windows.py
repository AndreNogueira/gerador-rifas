"""Grava os videos das funcionalidades da app Windows (assets/video/windows_<id>_<lingua>.mp4) com a propria aplicacao.

Como `fazer_video.py`: a janela REAL e comandada passo a passo, fotografada e cada fotograma leva uma legenda grande (sem som). Aqui os passos sao
os de cada funcionalidade (series, lista, marcas de corte, galeria, marca propria, sorteio, visual); as outras (QR, guardar, instalar) so existem no site.
A preparacao (carregar o template) nao se grava. Precisa de um ffmpeg (so para gravar; nao vai na app): `uv pip install --python .venv\\Scripts\\python.exe
imageio-ffmpeg`, ou a variavel FFMPEG.

Uso (a janela aparece no ecra durante uns minutos; nao mexer):
    python testes/fazer_videos_windows.py [id ...]       (sem ids: todos; ex.: python testes/fazer_videos_windows.py series galeria)
"""
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
from tkinter import filedialog, messagebox

messagebox.showwarning = messagebox.showerror = lambda *a, **k: print("MSG:", str(a[1])[:90])
messagebox.askyesno = lambda *a, **k: True
messagebox.showinfo = lambda *a, **k: None
from PIL import Image, ImageDraw, ImageFont, ImageGrab

import app as A
import extras
import core
from core import i18n

EX = BASE / "exemplos"
SAIDA = BASE / "assets" / "video"
FPS = 8
LARG, ALT = 1280, 720
FUNDO = (22, 31, 37)
FONTES = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
POS_APP = "1240x880+20+20"
UMA_RIFA = (EX / "template_exemplo_1_rifa.pdf", EX / "digitos_exemplo.png")
VARIAS = (EX / "template_exemplo.pdf", EX / "digitos_exemplo.pdf")


def ffmpeg() -> str:
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("falta o ffmpeg: uv pip install --python .venv\\Scripts\\python.exe imageio-ffmpeg (ou defina FFMPEG)")


class Gravador:
    """Fotografa a janela e escreve o video (H.264, 1280x720) por um pipe para o ffmpeg."""

    def __init__(self, app, destino: Path):
        self.app, self.destino = app, destino
        self.legenda = ""
        self.fonte = ImageFont.truetype(str(FONTES / "segoeuib.ttf"), 26)
        self.p = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{LARG}x{ALT}", "-r", str(FPS),
                                   "-i", "-", "-an", "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "30",
                                   "-movflags", "+faststart", str(destino)], stdin=subprocess.PIPE)

    def quadro(self) -> None:
        a = self.app
        a.update()
        x, y, w, h = a.winfo_rootx(), a.winfo_rooty(), a.winfo_width(), a.winfo_height()
        im = ImageGrab.grab(bbox=(x, y, x + w, y + h)).convert("RGB")
        esc = ALT / im.height
        im = im.resize((round(im.width * esc), ALT), Image.LANCZOS)
        tela = Image.new("RGB", (LARG, ALT), FUNDO)
        tela.paste(im, ((LARG - im.width) // 2, 0))
        if self.legenda:
            d = ImageDraw.Draw(tela)
            linhas = self._quebrar(self.legenda, LARG - 160, d)
            alt = 18 + 36 * len(linhas)
            d.rounded_rectangle((60, ALT - alt - 24, LARG - 60, ALT - 14), 14, fill=(20, 16, 40))
            for i, l in enumerate(linhas):
                d.text((LARG // 2, ALT - alt - 14 + 8 + 36 * i), l, font=self.fonte, fill=(255, 255, 255), anchor="ma")
        self.p.stdin.write(tela.tobytes())

    def _quebrar(self, texto: str, largura: int, d) -> list:
        linhas, atual = [], ""
        for palavra in texto.split():
            tentativa = (atual + " " + palavra).strip()
            if d.textlength(tentativa, font=self.fonte) > largura and atual:
                linhas.append(atual)
                atual = palavra
            else:
                atual = tentativa
        return linhas + [atual]

    def segundos(self, s: float, texto: str | None = None) -> None:
        if texto is not None:
            self.legenda = texto
        t0 = time.time()
        n = max(1, round(s * FPS))
        for i in range(n):
            self.quadro()
            resto = (t0 + (i + 1) / FPS) - time.time()
            if resto > 0:
                time.sleep(resto)

    def escrever(self, var, texto: str, passo: int = 1) -> None:
        """Escreve `texto` na variavel como se fosse digitado, um fotograma por letra."""
        var.set("")
        for i in range(1, len(texto) + 1):
            var.set(texto[:i])
            if i % passo == 0 or i == len(texto):
                self.quadro()
                time.sleep(0.07)

    def fim(self) -> None:
        self.p.stdin.close()
        self.p.wait()


def esperar(app, ate, limite=60.0):
    t0 = time.time()
    while time.time() - t0 < limite:
        app.update()
        time.sleep(0.03)
        if ate():
            return True
    return False


def preparar(app, ficheiros) -> None:
    app._limpar_tudo()
    app.update()
    if ficheiros is None:
        return
    app.v_template.set(str(ficheiros[0]))
    app.v_alg.set(str(ficheiros[1]))
    app._analisar()
    esperar(app, lambda: app.prep is not None)
    app.v_nome.set("")
    app.update()


def abrir(app, nome: str, classe, geometria: str):
    app._abrir_extra(nome, classe)
    j = app.w_extras[nome]
    j.geometry(geometria)
    esperar(app, lambda: False, 0.9)          # o fade-in das janelas do customtkinter
    return j


# ------------------------------------------------------------------ as cenas: (id, ficheiros, funcao(app, gravador, T))
def cena_series(a, g, T):
    g.segundos(1.8, T("Séries, prefixos e números a saltar", "Series, prefixes and skipped numbers"))
    a.v_fim.set("30")
    g.segundos(1.2, T("Menu «Extras» → «Séries, cor e logótipo…»", "Menu “Extras” → “Series, color and logo…”"))
    j = abrir(a, "opcoes", extras.Opcoes, "+660+60")
    g.segundos(1.0, T("Escreva os prefixos separados por vírgulas: cada um é uma série", "Type the prefixes separated by commas: each one is a series"))
    g.escrever(a.v_prefixos, "A-, B-", 1)
    g.segundos(1.2)
    g.legenda = T("Números que não se imprimem: 13 e de 20 a 22", "Numbers that are not printed: 13 and 20 to 22")
    g.escrever(a.v_saltar, "13, 20-22", 2)
    g.segundos(1.4)
    g.segundos(1.6, T("Cada série pode ter a sua cor", "Each series can have its own color"))
    a.v_cor_serie.set(True)
    g.segundos(1.4)
    j.destroy()
    g.segundos(3.0, T("O resumo conta só o que se imprime, série a série", "The summary counts only what gets printed, series by series"))
    a._previa()
    esperar(a, lambda: a.st_titulo[0] == "previa_titulo_n")
    g.segundos(3.6, T("A pré-visualização mostra o prefixo A- e a cor da série", "The preview shows the A- prefix and the series color"))
    g.segundos(2.4, T("Cada série sai nos seus próprios PDFs", "Each series comes out in its own PDFs"))


def cena_lista(a, g, T):
    g.segundos(1.8, T("Lista de bilhetes e folha de controlo", "Ticket list and control sheet"))
    a.v_fim.set("120")
    a.v_nome.set("")
    a.e_nome.delete(0, "end")
    a.e_nome.insert(0, T("Rifa de Natal", "Christmas raffle"))
    a.v_nome.set(a.e_nome.get())
    g.segundos(2.4, T("Não precisa de template: usa só o intervalo e o nome", "No template needed: it only uses the range and the name"))
    pasta = Path(tempfile.mkdtemp(prefix="rifas-video-"))
    filedialog.asksaveasfilename = lambda **k: str(pasta / k["initialfile"])
    g.segundos(1.6, T("Menu «Extras» → «Exportar lista (CSV)…»", "Menu “Extras” → “Export list (CSV)…”"))
    a._exportar_csv()
    g.segundos(3.0, T("Um bilhete por linha, com Nome, Contacto e Pago para preencher", "One ticket per row, with Name, Contact and Paid to fill in"))
    g.segundos(1.6, T("Menu «Extras» → «Folha de controlo (PDF)»", "Menu “Extras” → “Control sheet (PDF)”"))
    a._exportar_folha()
    g.segundos(3.4, T("A folha de controlo é um PDF para imprimir e ir marcando quem pagou", "The control sheet is a PDF to print and tick off who paid"))


def cena_marcas(a, g, T):
    g.segundos(1.8, T("Marcas de corte", "Crop marks"))
    g.segundos(3.0, T("Com uma só rifa repetida na folha, a margem deve ter 3 mm ou mais", "With a single ticket repeated on the sheet, the margin must be 3 mm or more"))
    a.v_fim.set("20")
    j = abrir(a, "opcoes", extras.Opcoes, "+660+60")
    g.segundos(1.4, T("Menu «Extras» → «Séries, cor e logótipo…» → «Marcas de corte»", "Menu “Extras” → “Series, color and logo…” → “Crop marks”"))
    a.v_marcas.set(True)
    g.segundos(1.6)
    j.destroy()
    a._previa()
    esperar(a, lambda: a.st_titulo[0] == "previa_titulo_n")
    g.segundos(4.2, T("Os traços nas margens prolongam as linhas de corte", "The marks in the margins extend the cutting lines"))


def cena_galeria(a, g, T):
    g.segundos(2.0, T("Sem template do Canva? Use a galeria", "No Canva template? Use the gallery"))
    g.segundos(1.2, T("Menu «Extras» → «Galeria de templates…»", "Menu “Extras” → “Template gallery…”"))
    j = abrir(a, "galeria", extras.Galeria, "+160+110")
    esperar(a, lambda: j._foto is not None, 8)
    j.seg.set("Natal")
    j._desenho("Natal")
    g.segundos(2.0, T("Escolha um dos quatro desenhos", "Pick one of the four designs"))
    g.legenda = T("Escreva o título, a organização, os prémios e a data", "Write the title, the organization, the prizes and the date")
    g.escrever(j.v["titulo"], T("Rifa de Natal", "Christmas raffle"), 2)
    j.v["organizacao"].set(T("Associação Exemplo", "Example Association"))
    j.v["p1"].set(T("1.º Prémio: Cabaz", "1st Prize: Hamper"))
    esperar(a, lambda: False, 1.6)
    g.segundos(3.0)
    g.segundos(1.2, T("«Usar este template»: o template e os algarismos ficam prontos", "“Use this template”: the template and the digits are ready"))
    j._usar()
    esperar(a, lambda: a.prep is not None)
    g.segundos(3.4)
    g.segundos(2.4, T("Só falta escolher os números e gerar", "All that is left is choosing the numbers and generating"))


def cena_editor(a, g, T):
    g.segundos(2.0, T("Sem Canva? Desenhe a sua rifa no editor", "No Canva? Design your ticket in the editor"))
    g.segundos(1.2, T("Menu «Extras» → «Editor de templates…»", "Menu “Extras” → “Template editor…”"))
    j = abrir(a, "editor", extras.EditorTemplates, "+120+60")
    esperar(a, lambda: j._foto is not None, 8)
    g.segundos(2.4, T("Começa com um modelo de rifa com talão", "It starts with a sample ticket with a stub"))
    titulo = next(e for e in j.m.elementos if e.texto == "TÍTULO DA RIFA")
    x0, y0, x1, y1 = j.m.caixa(titulo.id)
    px, py = j._px((x0 + x1) / 2, (y0 + y1) / 2)
    j.tela.event_generate("<ButtonPress-1>", x=int(px), y=int(py))
    a.update()
    esperar(a, lambda: False, 0.5)
    g.legenda = T("Escolha um elemento e mude o texto", "Pick an element and change its text")
    g.escrever(j.var_texto, T("RIFA DE NATAL", "CHRISTMAS RAFFLE"), 2)
    esperar(a, lambda: not j._espera, 4)
    g.segundos(1.6)
    g.legenda = T("Arraste os elementos para o sítio (ou use as setas)", "Drag the elements into place (or use the arrow keys)")
    for i in range(1, 13):
        j.tela.event_generate("<B1-Motion>", x=int(px) + i * 8, y=int(py) + i)
        a.update()
        g.quadro()
        time.sleep(0.04)
    j.tela.event_generate("<ButtonRelease-1>", x=int(px) + 96, y=int(py) + 12)
    esperar(a, lambda: not j._espera, 4)
    g.segundos(2.0)
    g.legenda = T("Desfazer, refazer e duplicar", "Undo, redo and duplicate")
    j._a_desfazer()
    esperar(a, lambda: not j._espera, 4)
    g.segundos(1.4)
    j._a_refazer()
    j._a_duplicar()
    esperar(a, lambda: not j._espera, 4)
    g.segundos(2.0)
    j._a_apagar()
    j.acrescentar("retangulo")
    esperar(a, lambda: not j._espera, 4)
    g.segundos(2.0, T("Junte textos, retângulos, linhas e o número 0001 (uma ou duas vezes)",
                      "Add texts, rectangles, lines and the number 0001 (once or twice)"))
    j._a_apagar()
    g.segundos(1.0, T("«Usar este template»: o template e os algarismos ficam prontos", "“Use this template”: the template and the digits are ready"))
    j._usar()
    esperar(a, lambda: a.prep is not None)
    g.segundos(3.0)
    g.segundos(2.4, T("Só falta escolher os números e gerar", "All that is left is choosing the numbers and generating"))


def cena_marca(a, g, T):
    g.segundos(1.8, T("Marca própria: cor e logótipo", "Your brand: color and logo"))
    logo = Path(tempfile.mkdtemp(prefix="rifas-video-")) / "logotipo.png"
    Image.open(BASE.parent / "src" / "web" / "frontend" / "e2e" / "ficheiros" / "logotipo.png").save(logo)
    a.v_fim.set("20")
    j = abrir(a, "opcoes", extras.Opcoes, "+660+60")
    g.segundos(1.4, T("Menu «Extras» → «Séries, cor e logótipo…»", "Menu “Extras” → “Series, color and logo…”"))
    g.segundos(1.2, T("Escolha a cor dos números", "Choose the color of the numbers"))
    g.escrever(a.v_cor_numeros, "#C1121F", 2)
    g.segundos(1.4)
    g.segundos(1.2, T("Escolha o logótipo da associação (PNG ou JPG)", "Choose the association's logo (PNG or JPG)"))
    a.v_logo.set(str(logo))
    g.segundos(1.6)
    g.segundos(1.2, T("Escolha o canto e o tamanho", "Choose the corner and the size"))
    a.v_logo_pos.set("se")
    j.seg.set("↖")
    a.v_logo_tam.set("30")
    g.segundos(1.6)
    j.destroy()
    a._previa()
    esperar(a, lambda: a.st_titulo[0] == "previa_titulo_n")
    g.segundos(4.0, T("O logótipo e a cor aparecem em cada rifa", "The logo and the color appear on every ticket"))


def cena_sorteio(a, g, T):
    g.segundos(1.8, T("Sorteio verificável", "Verifiable draw"))
    g.segundos(1.2, T("Menu «Extras» → «Sorteio…»", "Menu “Extras” → “Draw…”"))
    j = abrir(a, "sorteio", extras.Sorteio, "+300+60")
    j.v_de.set("1")
    j.v_ate.set("500")
    j.v_quantos.set("3")
    g.segundos(2.4, T("O intervalo de números e quantos sortear", "The range of numbers and how many to draw"))
    g.legenda = T("A semente pública: algo que ninguém controla, como o resultado de uma lotaria", "The public seed: something nobody controls, like a lottery result")
    g.escrever(j.v_semente, T("lotaria-2026-12-22", "lottery-2026-12-22"), 2)
    g.segundos(1.0)
    j.sortear()
    g.segundos(3.2, T("Os números saem pela ordem do sorteio", "The numbers come out in draw order"))
    g.segundos(3.6, T("Quem repetir com os mesmos dados obtém sempre o mesmo resultado", "Anyone repeating it with the same data always gets the same result"))
    j.destroy()


def cena_visual(a, g, T):
    g.segundos(2.0, T("Temas visuais e Natal automático", "Visual themes and automatic Christmas"))
    g.segundos(1.4, T("Menu «Ver» → «Visual»", "Menu “View” → “Visual”"))
    for v in ("natal", "premiado", "natal"):
        a._definir_visual(v)
        esperar(a, lambda: False, 0.6)
        g.segundos(2.0, T("Premiado e Natal: a estrutura é a mesma, só mudam as cores", "Premiado and Natal: the layout is the same, only the colors change"))
    g.segundos(2.0, T("O claro e o escuro são independentes do tema", "Light and dark are independent of the theme"))
    a._definir_tema("dark")
    esperar(a, lambda: False, 0.6)
    g.segundos(2.0)
    a._definir_tema("light")
    esperar(a, lambda: False, 0.6)
    g.segundos(3.0, T("Em dezembro o Natal é o tema automático", "In December, Christmas is the automatic theme"))
    a._definir_visual("auto")


CENAS = {"series": (VARIAS, cena_series), "lista": (None, cena_lista), "marcas": (UMA_RIFA, cena_marcas), "galeria": (None, cena_galeria), "editor": (None, cena_editor),
         "marca": (UMA_RIFA, cena_marca), "sorteio": (VARIAS, cena_sorteio), "visual": (VARIAS, cena_visual)}


def main() -> int:
    ids = sys.argv[1:] or list(CENAS)
    app = A.App(usar_config=False)
    app.geometry(POS_APP)
    esperar(app, lambda: False, 0.6)
    SAIDA.mkdir(parents=True, exist_ok=True)
    for lg in ("pt", "en"):
        app._mudar_lingua(i18n.LINGUAS[lg])
        esperar(app, lambda: False, 0.6)
        app.geometry(POS_APP)
        for id_ in ids:
            ficheiros, cena = CENAS[id_]
            preparar(app, ficheiros)
            g = Gravador(app, SAIDA / f"windows_{id_}_{lg}.mp4")
            try:
                cena(app, g, lambda pt, en, lg=lg: pt if lg == "pt" else en)
                g.segundos(0.6, "")
            finally:
                g.fim()
            for j in list(app.w_extras.values()):
                try:
                    j.destroy()
                except Exception:
                    pass
            app.w_extras.clear()
            print(f"windows_{id_}_{lg}.mp4: {(SAIDA / f'windows_{id_}_{lg}.mp4').stat().st_size // 1024} KB", flush=True)
    app._definir_visual("auto")
    app.destroy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
