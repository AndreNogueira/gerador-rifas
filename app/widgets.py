"""Componentes leves (em tk puro, rapidos ao redimensionar): painel deslocavel, barra de menus, dicas."""
from __future__ import annotations

import sys
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk

from tema import C, FONTE, cor_tk
from tema import _rgb


def repintar_so_o_necessario(janela) -> None:
    """Windows: as classes de janela do Tk (TkTopLevel/TkChild) tem CS_HREDRAW|CS_VREDRAW, o que obriga a repintar
    TODOS os widgets (centenas de canvas do CustomTkinter) a cada passo ao redimensionar. Sem esses bits so se
    repintam os widgets cujo tamanho muda: ~7x mais rapido. Os widgets continuam a redesenhar-se quando o seu
    tamanho muda (o Tk trata o ConfigureNotify)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        u = ctypes.windll.user32
        u.GetClassLongPtrW.restype = ctypes.c_size_t
        u.GetClassLongPtrW.argtypes = [ctypes.c_void_p, ctypes.c_int]
        u.SetClassLongPtrW.restype = ctypes.c_size_t
        u.SetClassLongPtrW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
        u.GetParent.restype = ctypes.c_void_p
        u.GetParent.argtypes = [ctypes.c_void_p]
        filho = janela.winfo_id()
        for hwnd in (filho, u.GetParent(filho)):            # TkChild e TkTopLevel
            if hwnd:
                estilo = u.GetClassLongPtrW(hwnd, -26)       # GCL_STYLE
                u.SetClassLongPtrW(hwnd, -26, estilo & ~0x3)  # sem CS_HREDRAW (1) nem CS_VREDRAW (2)
    except Exception:
        pass


def repintar_tudo(janela) -> None:
    """Forca a repintura completa (so para testes de comparacao)."""
    import ctypes
    u = ctypes.windll.user32
    u.GetParent.restype = ctypes.c_void_p
    u.GetParent.argtypes = [ctypes.c_void_p]
    u.RedrawWindow.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
    u.RedrawWindow(u.GetParent(janela.winfo_id()), None, None, 0x1 | 0x4 | 0x80 | 0x100)   # INVALIDATE|ERASE|ALLCHILDREN|UPDATENOW


class Dica:
    """Balao de ajuda que aparece ao parar o rato sobre um widget."""

    def __init__(self, widget, texto: str, atraso: int = 550):
        self.w, self.texto, self.atraso = widget, texto, atraso
        self._id = None
        self._tw = None
        widget.bind("<Enter>", self._entrar, add="+")
        widget.bind("<Leave>", self._sair, add="+")
        widget.bind("<ButtonPress>", self._sair, add="+")

    def _entrar(self, _=None):
        self._sair()
        self._id = self.w.after(self.atraso, self._mostrar)

    def _mostrar(self):
        texto = self.texto() if callable(self.texto) else self.texto
        if not texto or not self.w.winfo_exists():
            return
        x, y = self.w.winfo_rootx() + 8, self.w.winfo_rooty() + self.w.winfo_height() + 6
        self._tw = tw = tk.Toplevel(self.w)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        borda = tk.Frame(tw, bg=cor_tk(C["borda"]), padx=1, pady=1)
        borda.pack()
        tk.Label(borda, text=texto, bg=cor_tk(C["cartao"]), fg=cor_tk(C["texto"]), font=(FONTE, 9),
                 padx=8, pady=4).pack()

    def _sair(self, _=None):
        if self._id is not None:
            try:
                self.w.after_cancel(self._id)
            except Exception:
                pass
            self._id = None
        if self._tw is not None:
            try:
                self._tw.destroy()
            except Exception:
                pass
            self._tw = None


class Rolavel(tk.Frame):
    """Painel com deslocamento vertical (roda do rato) e indicador fino sobreposto.

    Mais rapido que o CTkScrollableFrame: so reajusta a largura quando ela muda e nao redesenha barras.
    Os widgets vao para `self.interior`.
    """

    def __init__(self, master):
        super().__init__(master, bg=cor_tk(C["fundo"]), highlightthickness=0, bd=0)
        self.tela = tk.Canvas(self, highlightthickness=0, bd=0, bg=cor_tk(C["fundo"]))
        self.tela.pack(fill="both", expand=True)
        self.interior = ctk.CTkFrame(self.tela, fg_color="transparent", corner_radius=0)
        self._jan = self.tela.create_window(0, 0, window=self.interior, anchor="nw")
        self._larg = 0
        self.interior.bind("<Configure>", lambda e=None: self._ajustar_regiao())
        self.tela.bind("<Configure>", self._ao_mudar_tela)
        self.tela.configure(yscrollcommand=self._ao_rolar)
        # a roda do rato e ligada uma unica vez pela janela principal (que chama `roda`)

    def tema(self) -> None:
        self.configure(bg=cor_tk(C["fundo"]))
        self.tela.configure(bg=cor_tk(C["fundo"]))
        self._ao_rolar(*self.tela.yview())

    def _ao_mudar_tela(self, e) -> None:
        if e.width != self._larg:                  # so mexe no interior quando a largura muda
            self._larg = e.width
            self.tela.itemconfigure(self._jan, width=e.width)
        self._ajustar_regiao()

    def _ajustar_regiao(self) -> None:
        h = max(self.interior.winfo_reqheight(), self.tela.winfo_height())
        self.tela.configure(scrollregion=(0, 0, self._larg, h))
        if self.interior.winfo_reqheight() <= self.tela.winfo_height():
            self.tela.yview_moveto(0)
        self._ao_rolar(*self.tela.yview())

    def _ao_rolar(self, lo, hi) -> None:
        self.tela.delete("ind")
        lo, hi = float(lo), float(hi)
        if hi - lo >= 0.999:
            return
        h, w = self.tela.winfo_height(), self.tela.winfo_width()
        y0 = self.tela.canvasy(0)
        self.tela.create_rectangle(w - 6, y0 + lo * h + 2, w - 2, y0 + hi * h - 2, fill=cor_tk(C["suave"]),
                                   outline="", tags="ind", stipple="gray50")

    def roda(self, e) -> None:
        try:
            alvo = self.winfo_containing(e.x_root, e.y_root)
        except Exception:
            return
        if alvo is None or not str(alvo).startswith(str(self) + ".") or isinstance(alvo, tk.Text):
            return
        if self.interior.winfo_reqheight() > self.tela.winfo_height():
            self.tela.yview_scroll(-1 * (e.delta // 120) * 3, "units")


class BarraMenus(tk.Frame):
    """Barra de menus propria (segue o tema claro/escuro); cada titulo abre um tk.Menu."""

    def __init__(self, master):
        super().__init__(master, bg=cor_tk(C["barra"]), highlightthickness=0)
        self._itens: list = []

    def adicionar(self, titulo: str, preencher) -> None:
        """`preencher(menu)` acrescenta os itens; e chamado em cada abertura, por isso reflete o estado atual."""
        lb = tk.Label(self, text=titulo, bg=cor_tk(C["barra"]), fg=cor_tk(C["texto"]), font=(FONTE, 10),
                      padx=11, pady=6, cursor="arrow")
        lb.pack(side="left")
        menu = novo_menu(self)
        lb.bind("<Enter>", lambda e=None, w=lb: w.configure(bg=cor_tk(C["sel_menu"])))
        lb.bind("<Leave>", lambda e=None, w=lb: w.configure(bg=cor_tk(C["barra"])))
        lb.bind("<Button-1>", lambda e=None, w=lb, m=menu, p=preencher: self._abrir(w, m, p))
        self._itens.append(lb)

    def _abrir(self, lb, menu, preencher) -> None:
        lb.configure(bg=cor_tk(C["sel_menu"]))
        menu.delete(0, "end")
        preencher(menu)
        try:
            menu.tk_popup(lb.winfo_rootx(), lb.winfo_rooty() + lb.winfo_height())
        finally:
            menu.grab_release()
            lb.configure(bg=cor_tk(C["barra"]))


def novo_menu(pai) -> tk.Menu:
    """tk.Menu com as cores do tema (no Windows os menus pendentes respeitam estas cores)."""
    return tk.Menu(pai, tearoff=0, bg=cor_tk(C["cartao"]), fg=cor_tk(C["texto"]),
                   activebackground=cor_tk(C["sel_menu"]), activeforeground=cor_tk(C["texto"]),
                   disabledforeground=cor_tk(C["suave"]), selectcolor=cor_tk(C["texto"]), relief="flat", bd=1,
                   font=(FONTE, 10), activeborderwidth=0)


class Banda(tk.Canvas):
    """A faixa de cor do topo: gradiente violeta -> magenta (as cores da marca), o logotipo e o nome da aplicacao.

    Desenha-se de novo quando a largura muda (a imagem do gradiente e gerada com essa largura: sem degraus)."""

    def __init__(self, master, titulo: str, versao: str, logo: Image.Image | None, altura: int = 58, escala: float = 1.0):
        self._altura = max(40, int(altura * escala))
        super().__init__(master, height=self._altura, highlightthickness=0, bd=0, bg=cor_tk(C["banda_a"]))
        self._titulo, self._versao, self._escala = titulo, versao, escala
        self._logo = logo.resize((int(self._altura * 0.74),) * 2, Image.LANCZOS) if logo is not None else None
        self._logo_tk = ImageTk.PhotoImage(self._logo) if self._logo is not None else None
        self._fundo = None
        self._larg = 0
        self.bind("<Configure>", self._desenhar)

    def _gradiente(self, w: int) -> Image.Image:
        a, b = _rgb(cor_tk(C["banda_a"])), _rgb(cor_tk(C["banda_b"]))
        faixa = Image.new("RGB", (w, 1))
        px = faixa.load()
        for x in range(w):
            t = x / max(1, w - 1)
            px[x, 0] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
        return faixa.resize((w, self._altura))

    def _desenhar(self, e=None) -> None:
        w = self.winfo_width()
        if w < 20:
            return
        if w != self._larg:
            self._fundo, self._larg = ImageTk.PhotoImage(self._gradiente(w)), w
        self.delete("all")
        self.create_image(0, 0, image=self._fundo, anchor="nw")
        x = int(16 * self._escala)
        if self._logo_tk is not None:
            self.create_image(x, self._altura // 2, image=self._logo_tk, anchor="w")
            x += self._logo_tk.width() + int(12 * self._escala)
        self.create_text(x + 1, self._altura // 2 + 1, text=self._titulo, anchor="w", fill="#2A0F6B", font=(FONTE, 17, "bold"))
        self.create_text(x, self._altura // 2, text=self._titulo, anchor="w", fill="#FFFFFF", font=(FONTE, 17, "bold"))
        self.create_text(w - int(16 * self._escala), self._altura // 2, text=f"v{self._versao}", anchor="e", fill="#E9E0FF",
                         font=(FONTE, 10))
