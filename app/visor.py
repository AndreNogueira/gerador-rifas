"""Visor da pre-visualizacao: zoom, deslocamento, ajustar e expandir.

So desenha a parte visivel da imagem (recorte + redimensionamento numa so passagem), por isso o custo de cada
quadro depende do tamanho do visor e nao da ampliacao. Durante o redimensionamento e o arrastar usa uma
amostragem rapida e, passados ~140 ms sem eventos, desenha de novo com qualidade total.
"""
from __future__ import annotations

import time
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk

import icones
from tema import C, FONTE, cor_tk
from widgets import Dica


class Visor(tk.Frame):
    ZOOM_MIN, ZOOM_MAX = 0.05, 8.0
    MARGEM = 18            # folga (px do ecra) a volta da folha

    def __init__(self, master, aoexpandir):
        super().__init__(master, bg=cor_tk(C["visor"]), highlightthickness=1,
                         highlightbackground=cor_tk(C["borda"]), highlightcolor=cor_tk(C["borda"]))
        self.imagem: Image.Image | None = None
        self.zoom_fit = True
        self.zoom = 1.0
        self.cx: float | None = None          # centro da vista, em pixeis da imagem
        self.cy: float | None = None
        self.aoexpandir = aoexpandir
        self.expandido = False
        self.texto_vazio = ""
        self._foto = None
        self._drag = None
        self._ultimo = 0.0
        self._idle = None
        self._dicas: list = []

        self.barra = ctk.CTkFrame(self, corner_radius=0, fg_color=C["cartao"], height=48)
        self.barra.pack(fill="x")
        self.barra.pack_propagate(False)
        self.l_titulo = ctk.CTkLabel(self.barra, text="", font=ctk.CTkFont(FONTE, 14, "bold"),
                                     text_color=C["texto"], anchor="w")
        self.l_titulo.pack(side="left", fill="x", expand=True, padx=(16, 8))

        def botao(icone, comando, largura=34, **kw):
            return ctk.CTkButton(self.barra, text=kw.pop("text", ""), image=icones.icone(icone, 16), command=comando,
                                 width=largura, height=32, corner_radius=6, fg_color="transparent",
                                 hover_color=C["sel_menu"], text_color=C["texto"], font=ctk.CTkFont(FONTE, 12), **kw)
        self.b_expandir = botao("expandir", self._expandir)
        self.b_expandir.pack(side="right", padx=(2, 10))
        self.b_ajustar = botao("ajustar", self.ajustar, largura=96, compound="left", text="")
        self.b_ajustar.pack(side="right", padx=2)
        self.b_mais = botao("mais", lambda: self.zoom_por(1.25))
        self.b_mais.pack(side="right", padx=2)
        self.l_zoom = ctk.CTkLabel(self.barra, text="", width=46, text_color=C["suave"], font=ctk.CTkFont(FONTE, 12))
        self.l_zoom.pack(side="right")
        self.b_menos = botao("menos", lambda: self.zoom_por(1 / 1.25))
        self.b_menos.pack(side="right", padx=2)
        tk.Frame(self, height=1, bg=cor_tk(C["borda"])).pack(fill="x")

        self.tela = tk.Canvas(self, highlightthickness=0, bd=0, bg=cor_tk(C["visor"]), cursor="fleur")
        self.tela.pack(fill="both", expand=True)
        self.tela.bind("<Configure>", lambda e=None: self._agendar())
        self.tela.bind("<ButtonPress-1>", self._carregar)
        self.tela.bind("<B1-Motion>", self._arrastar)
        self.tela.bind("<MouseWheel>", self._roda)
        self.tela.bind("<Control-MouseWheel>", self._roda_zoom)
        self.tela.bind("<Shift-MouseWheel>", self._roda_horizontal)
        self.tela.bind("<Double-Button-1>", lambda e=None: self.ajustar())

    # -- API usada pela janela
    def textos(self, titulo: str, ajustar: str, vazio: str, dicas: tuple = ()) -> None:
        self.l_titulo.configure(text=titulo)
        self.b_ajustar.configure(text=ajustar)
        self.texto_vazio = vazio
        if dicas and not self._dicas:
            menos, mais, ajust, expandir, reduzir = dicas
            for w, txt in ((self.b_menos, menos), (self.b_mais, mais), (self.b_ajustar, ajust),
                           (self.b_expandir, lambda: reduzir if self.expandido else expandir)):
                self._dicas.append(Dica(w, txt))
        if self.imagem is None:
            self._render(False)

    def definir_titulo(self, titulo: str) -> None:
        self.l_titulo.configure(text=titulo)

    def definir_imagem(self, im: Image.Image, largura_papel: float = 0, manter_zoom: bool = False) -> None:
        self.imagem = im
        if not manter_zoom:
            self.zoom_fit, self.cx, self.cy = True, None, None
        self._render(False)

    def limpar(self) -> None:
        """Tira a imagem (volta ao texto «escolha o template»)."""
        self.imagem = None
        self.zoom_fit, self.cx, self.cy = True, None, None
        self._render(False)

    def estado(self) -> tuple:
        return self.imagem, self.zoom_fit, self.zoom, self.expandido, self.cx, self.cy

    def restaurar(self, estado: tuple) -> None:
        self.imagem, self.zoom_fit, self.zoom, exp, self.cx, self.cy = estado
        self.expandido = exp
        self.b_expandir.configure(image=icones.icone("reduzir" if exp else "expandir", 16))
        self.after(30, lambda: self._render(False))

    def tema(self) -> None:
        self.configure(bg=cor_tk(C["visor"]), highlightbackground=cor_tk(C["borda"]),
                       highlightcolor=cor_tk(C["borda"]))
        self.tela.configure(bg=cor_tk(C["visor"]))
        self._render(False)

    # -- zoom e deslocamento
    def ajustar(self) -> None:
        self.zoom_fit, self.cx, self.cy = True, None, None
        self._render(False)

    def zoom_por(self, fator: float, px: float | None = None, py: float | None = None, final: bool = True) -> None:
        if self.imagem is None:
            return
        W, H = self.tela.winfo_width(), self.tela.winfo_height()
        px = W / 2 if px is None else px
        py = H / 2 if py is None else py
        s0 = self._escala(W, H)
        s1 = min(self.ZOOM_MAX, max(self.ZOOM_MIN, s0 * fator))
        iw, ih = self.imagem.size
        cx = iw / 2 if self.cx is None else self.cx
        cy = ih / 2 if self.cy is None else self.cy
        ix, iy = cx - W / (2 * s0) + px / s0, cy - H / (2 * s0) + py / s0      # ponto da imagem sob o cursor
        self.zoom_fit, self.zoom = False, s1
        self.cx, self.cy = ix - px / s1 + W / (2 * s1), iy - py / s1 + H / (2 * s1)
        if final:
            self._render(False)
        else:
            self._agendar()

    def _roda(self, e) -> None:
        if self.imagem is not None:
            self._mover(0, -(e.delta / 120) * 90)

    def _roda_horizontal(self, e) -> None:
        if self.imagem is not None:
            self._mover(-(e.delta / 120) * 90, 0)

    def _roda_zoom(self, e) -> None:
        self.zoom_por(1.15 if e.delta > 0 else 1 / 1.15, e.x, e.y, final=False)

    def _mover(self, dx: float, dy: float) -> None:
        """Desloca a vista dx, dy pixeis do ecra."""
        s = max(self.zoom, 1e-6)
        iw, ih = self.imagem.size
        self.cx = (iw / 2 if self.cx is None else self.cx) + dx / s
        self.cy = (ih / 2 if self.cy is None else self.cy) + dy / s
        self._agendar()

    def _carregar(self, e) -> None:
        if self.imagem is not None:
            iw, ih = self.imagem.size
            self._drag = (e.x, e.y, iw / 2 if self.cx is None else self.cx, ih / 2 if self.cy is None else self.cy)

    def _arrastar(self, e) -> None:
        if self._drag is None or self.imagem is None:
            return
        x, y, cx, cy = self._drag
        s = max(self.zoom, 1e-6)
        self.cx, self.cy = cx - (e.x - x) / s, cy - (e.y - y) / s
        self._agendar()

    def _expandir(self) -> None:
        self.expandido = not self.expandido
        self.b_expandir.configure(image=icones.icone("reduzir" if self.expandido else "expandir", 16))
        self.aoexpandir(self.expandido)

    # -- desenho
    def _agendar(self) -> None:
        """Desenha ja (rapido, no maximo ~20x/s) e, quando os eventos param, desenha com qualidade."""
        agora = time.monotonic()
        if agora - self._ultimo >= 0.05:
            self._render(True)
        if self._idle is not None:
            self.after_cancel(self._idle)
        self._idle = self.after(140, self._final)

    def _final(self) -> None:
        self._idle = None
        if self.winfo_exists():
            self._render(False)

    def _escala(self, W: int, H: int) -> float:
        if self.imagem is None:
            return 1.0
        if not self.zoom_fit:
            return self.zoom
        m = 2 * self.MARGEM
        return min(max(W - m, 50) / self.imagem.width, max(H - m, 50) / self.imagem.height, self.ZOOM_MAX)

    def _limitar(self, c: float, tam_img: int, tam_vista: int, s: float) -> float:
        m = self.MARGEM
        if tam_img * s + 2 * m <= tam_vista:
            return tam_img / 2
        meio = tam_vista / (2 * s) - m / s
        return min(max(c, meio), tam_img - meio)

    def _render(self, rapido: bool) -> None:
        self._ultimo = time.monotonic()
        tela = self.tela
        W, H = tela.winfo_width(), tela.winfo_height()
        tela.delete("all")
        if W < 20 or H < 20:
            return
        if self.imagem is None:
            tela.create_text(W / 2, H / 2, text=self.texto_vazio, fill=cor_tk(C["suave"]), font=(FONTE, 12),
                             width=max(W - 60, 100), justify="center")
            self.l_zoom.configure(text="")
            return
        iw, ih = self.imagem.size
        s = self._escala(W, H)
        self.zoom = s
        cx = self._limitar(iw / 2 if self.cx is None else self.cx, iw, W, s)
        cy = self._limitar(ih / 2 if self.cy is None else self.cy, ih, H, s)
        self.cx, self.cy = cx, cy
        vw, vh = W / s, H / s
        x0, y0 = cx - vw / 2, cy - vh / 2
        bx0, by0, bx1, by1 = max(0.0, x0), max(0.0, y0), min(float(iw), x0 + vw), min(float(ih), y0 + vh)
        dw, dh = max(1, round((bx1 - bx0) * s)), max(1, round((by1 - by0) * s))
        dx, dy = round((bx0 - x0) * s), round((by0 - y0) * s)
        if rapido:
            im = self.imagem.resize((dw, dh), Image.BILINEAR, box=(bx0, by0, bx1, by1), reducing_gap=2.0)
        else:
            im = self.imagem.resize((dw, dh), Image.LANCZOS if s < 1 else Image.BICUBIC, box=(bx0, by0, bx1, by1))
        self._foto = ImageTk.PhotoImage(im)
        tela.create_rectangle(dx + 3, dy + 4, dx + dw + 3, dy + dh + 4, fill=cor_tk(C["borda"]), outline="")
        tela.create_image(dx, dy, image=self._foto, anchor="nw")
        self.l_zoom.configure(text=f"{round(s * 100)}%")
        # indicadores de deslocamento (finos, sobrepostos) so quando a imagem excede a vista
        m = self.MARGEM
        cor = cor_tk(C["suave"])
        tot_x, tot_y = iw + 2 * m / s, ih + 2 * m / s
        if tot_x > vw + 0.5:
            a, b = (x0 + m / s) / tot_x, (x0 + m / s + vw) / tot_x
            tela.create_rectangle(a * W, H - 7, b * W, H - 3, fill=cor, outline="", stipple="gray50")
        if tot_y > vh + 0.5:
            a, b = (y0 + m / s) / tot_y, (y0 + m / s + vh) / tot_y
            tela.create_rectangle(W - 7, a * H, W - 3, b * H, fill=cor, outline="", stipple="gray50")
