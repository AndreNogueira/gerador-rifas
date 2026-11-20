"""Janelas das funcionalidades acrescentadas depois da v2.3: séries/cor/logótipo/marcas de corte, galeria de templates, editor de templates e sorteio.

São janelas à parte (abertas pelo menu «Extras») para a janela principal ficar igual: as capturas do tutorial, e os recortes que
delas se fazem, continuam a valer. Os valores ficam em variáveis da `App` (`v_prefixos`, `v_saltar`, ...), por isso `App._trabalho()`
e a pré-visualização os usam sem saber destas janelas. A lógica (ler prefixos, sortear, desenhar a galeria) está em `core`.
"""
from __future__ import annotations

import gc
import json
import threading
import urllib.request
from tkinter import colorchooser, filedialog, messagebox
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
from PIL import Image

import ambiente          # noqa: F401  (poe ..\src no sys.path)
import core
from core import editor, editor_modelo, galeria, i18n, marca, moeda, precario, precario_catalogo, sorteio, vales
from core.i18n import t
from tema import C, FONTE

BASE = Path(__file__).resolve().parent
CANTOS = (("se", "↖"), ("sd", "↗"), ("ie", "↙"), ("id", "↘"))


class Janela(ctk.CTkToplevel):
    """Base: janela filha da principal, no mesmo estilo, que fecha com Esc."""

    def __init__(self, app, titulo: str, largura: int, altura: int):
        super().__init__(app)
        self.app = app
        self.title(titulo)
        self.geometry(f"{largura}x{altura}")
        self.minsize(largura - 80, min(altura, 420))
        self.configure(fg_color=C["fundo"])
        ico = BASE / "assets" / "icon.ico"
        if ico.exists():
            self.after(250, lambda: self._icone(ico))
        self.bind("<Escape>", lambda e=None: self.destroy())
        self.after(120, self.focus_force)

    def _icone(self, ico: Path) -> None:
        try:
            self.iconbitmap(str(ico))
        except Exception:
            pass

    def etiqueta(self, pai, texto: str, suave: bool = True, **kw) -> ctk.CTkLabel:
        return ctk.CTkLabel(pai, text=texto, anchor="w", justify="left", text_color=C["suave" if suave else "texto"],
                            font=ctk.CTkFont(FONTE, 12), **kw)

    def caixa(self, pai, texto: str, var, **kw) -> ctk.CTkCheckBox:
        return ctk.CTkCheckBox(pai, text=texto, variable=var, text_color=C["texto"], fg_color=C["acento"], hover_color=C["acento_h"],
                               border_color=C["borda"], checkmark_color=C["sobre_acento"], font=ctk.CTkFont(FONTE, 13), **kw)

    def cartao(self, titulo: str = "") -> ctk.CTkFrame:
        c = ctk.CTkFrame(self, corner_radius=14, fg_color=C["cartao"], border_width=1, border_color=C["borda"])
        c.pack(fill="x", padx=14, pady=(12, 0))
        if titulo:
            ctk.CTkLabel(c, text=titulo, anchor="w", text_color=C["texto"], font=ctk.CTkFont(FONTE, 14, "bold")).pack(
                fill="x", padx=16, pady=(11, 4))
        return c


# ------------------------------------------------------------------ séries, cor, logótipo e marcas de corte
class Opcoes(Janela):
    def __init__(self, app):
        super().__init__(app, t("win_opcoes").rstrip("…"), 560, 640)
        a = app
        c = self.cartao(t("web_prefixos"))
        a._entrada(c, a.v_prefixos, placeholder_text="A-, B-, C-").pack(fill="x", padx=16)
        self.etiqueta(c, t("web_prefixos_dica"), wraplength=500).pack(fill="x", padx=16, pady=(4, 0))
        self.caixa(c, t("web_cor_serie"), a.v_cor_serie).pack(anchor="w", padx=16, pady=(8, 0))
        self.etiqueta(c, t("web_saltar"), suave=False).pack(fill="x", padx=16, pady=(10, 2))
        a._entrada(c, a.v_saltar, placeholder_text="13, 100-110").pack(fill="x", padx=16, pady=(0, 12))

        c = self.cartao(t("web_cor_numeros"))
        linha = ctk.CTkFrame(c, fg_color="transparent")
        linha.pack(fill="x", padx=16, pady=(0, 12))
        a._entrada(linha, a.v_cor_numeros, width=120, placeholder_text="#RRGGBB").pack(side="left")
        self.amostra = ctk.CTkLabel(linha, text="", width=36, height=36, corner_radius=8, fg_color=C["campo"])
        self.amostra.pack(side="left", padx=8)
        a._botao(linha, "…", self._escolher_cor, width=44, height=36).pack(side="left")
        a._botao(linha, "", lambda: a.v_cor_numeros.set(""), icone="fechar", width=44, height=36).pack(side="left", padx=(6, 0))
        self._tr_cor = a.v_cor_numeros.trace_add("write", lambda *_: self._pintar_amostra())
        self._pintar_amostra()

        c = self.cartao(t("web_logotipo"))
        linha = ctk.CTkFrame(c, fg_color="transparent")
        linha.pack(fill="x", padx=16)
        self.l_logo = self.etiqueta(linha, "", suave=False)
        self.l_logo.pack(side="left", fill="x", expand=True)
        a._botao(linha, t("escolher"), self._escolher_logo, True, icone="pasta", width=120, height=36).pack(side="right")
        a._botao(linha, "", self._remover_logo, icone="fechar", width=44, height=36).pack(side="right", padx=(0, 6))
        linha = ctk.CTkFrame(c, fg_color="transparent")
        linha.pack(fill="x", padx=16, pady=(8, 12))
        self.etiqueta(linha, t("web_logo_posicao")).pack(side="left")
        self.seg = ctk.CTkSegmentedButton(linha, values=[s for _, s in CANTOS], corner_radius=8, height=34, width=150,
                                          selected_color=C["acento_suave"], selected_hover_color=C["acento_suave"],
                                          unselected_color=C["campo"], unselected_hover_color=C["borda"], text_color=C["texto"],
                                          fg_color=C["campo"], command=self._canto)
        self.seg.set(dict(CANTOS)[a.v_logo_pos.get()])
        self.seg.pack(side="left", padx=8)
        self.etiqueta(linha, t("web_logo_tamanho") + " (%)").pack(side="left", padx=(8, 0))
        a._entrada(linha, a.v_logo_tam, width=56).pack(side="left", padx=6)
        self._tr_logo = a.v_logo.trace_add("write", lambda *_: self._pintar_logo())
        self._pintar_logo()

        c = self.cartao()
        self.caixa(c, t("web_marcas"), a.v_marcas).pack(anchor="w", padx=16, pady=(12, 12))
        a._botao(self, t("win_fechar"), self.destroy, True, width=140, height=38).pack(pady=14)

    def _pintar_amostra(self) -> None:
        try:
            cor = core.marca.cor_de_hex(self.app.v_cor_numeros.get())
        except core.ErroRifas:
            cor = None
        hexa = "#%02x%02x%02x" % tuple(round(x * 255) for x in cor) if cor else C["campo"]
        if self.amostra.winfo_exists():
            self.amostra.configure(fg_color=hexa)

    def _pintar_logo(self) -> None:
        if self.l_logo.winfo_exists():
            self.l_logo.configure(text=Path(self.app.v_logo.get()).name if self.app.v_logo.get() else "—")

    def _escolher_cor(self) -> None:
        r = colorchooser.askcolor(title=t("web_cor_numeros"), parent=self)
        if r and r[1]:
            self.app.v_cor_numeros.set(r[1].upper())

    def _escolher_logo(self) -> None:
        p = filedialog.askopenfilename(parent=self, title=t("web_logotipo"), filetypes=[("PNG / JPG", "*.png *.jpg *.jpeg")])
        if p:
            self.app.v_logo.set(p)

    def _remover_logo(self) -> None:
        self.app.v_logo.set("")

    def _canto(self, simbolo: str) -> None:
        self.app.v_logo_pos.set(next(c for c, s in CANTOS if s == simbolo))

    def destroy(self) -> None:
        for var, tr in ((self.app.v_cor_numeros, getattr(self, "_tr_cor", None)), (self.app.v_logo, getattr(self, "_tr_logo", None))):
            if tr:
                try:
                    var.trace_remove("write", tr)
                except Exception:
                    pass
        super().destroy()


# ------------------------------------------------------------------ galeria de templates
class Galeria(Janela):
    """Escolhe-se um dos desenhos, escrevem-se os textos e «Usar este template» cria o template e os algarismos como se tivessem sido
    escolhidos. A pré-visualização desenha-se no worker da app (o PDFium só corre lá) e chega por `App._ev_galeria`."""

    def __init__(self, app):
        super().__init__(app, t("win_galeria").rstrip("…"), 940, 620)
        self.token = 0
        self._espera = None
        self._foto = None
        self.v = {k: tk.StringVar() for k in ("titulo", "organizacao", *(f"p{i}" for i in range(1, galeria.MAX_PREMIOS + 1)), "data")}
        self.v_n = tk.StringVar(value=str(galeria.MIN_PREMIOS))          # quantos premios (3 a 10): so os das caixas visiveis entram na rifa
        self.v_desenho = tk.StringVar(value=galeria.DESENHOS[0].id)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        esq = ctk.CTkScrollableFrame(self, fg_color="transparent", width=340)          # com 10 premios a coluna nao cabe no ecra: rola
        esq.grid(row=0, column=0, sticky="ns", padx=(14, 0), pady=12)
        self.etiqueta(esq, t("web_galeria"), wraplength=330).pack(fill="x", pady=(0, 6))
        self.seg = ctk.CTkOptionMenu(                       # 24 desenhos: uma lista suspensa (um botão segmentado não os comporta)
            esq, values=[d.nome for d in galeria.DESENHOS], corner_radius=8, height=34, fg_color=C["campo"], button_color=C["borda"],
            button_hover_color=C["acento_suave"], text_color=C["texto"], dropdown_fg_color=C["cartao"], dropdown_text_color=C["texto"],
            dropdown_hover_color=C["acento_suave"], font=ctk.CTkFont(FONTE, 13), command=self._desenho)
        self.seg.set(galeria.DESENHOS[0].nome)
        self.seg.pack(fill="x", pady=(0, 8))
        for chave, rotulo, maximo in (("titulo", t("web_galeria_titulo"), galeria.MAX_TITULO),
                                      ("organizacao", t("web_galeria_organizacao"), galeria.MAX_ORGANIZACAO)):
            self.etiqueta(esq, rotulo).pack(fill="x")
            app._entrada(esq, self.v[chave]).pack(fill="x", pady=(0, 6))
        self.etiqueta(esq, t("web_galeria_premios")).pack(fill="x")
        linha_n = ctk.CTkFrame(esq, fg_color="transparent")
        linha_n.pack(fill="x", pady=(0, 4))
        self.etiqueta(linha_n, t("web_galeria_n_premios")).pack(side="left")
        self.menu_n = ctk.CTkOptionMenu(
            linha_n, values=[str(n) for n in range(galeria.MIN_PREMIOS, galeria.MAX_PREMIOS + 1)], variable=self.v_n, width=70, height=30,
            corner_radius=8, fg_color=C["campo"], button_color=C["borda"], button_hover_color=C["acento_suave"], text_color=C["texto"],
            dropdown_fg_color=C["cartao"], dropdown_text_color=C["texto"], dropdown_hover_color=C["acento_suave"], font=ctk.CTkFont(FONTE, 13),
            command=lambda _: self._mostrar_premios())
        self.menu_n.pack(side="right")
        self.f_premios = ctk.CTkFrame(esq, fg_color="transparent")
        self.f_premios.pack(fill="x")
        self.e_premios = [app._entrada(self.f_premios, self.v[f"p{i}"]) for i in range(1, galeria.MAX_PREMIOS + 1)]
        self._mostrar_premios()
        self.etiqueta(esq, t("web_galeria_data")).pack(fill="x", pady=(4, 0))
        app._entrada(esq, self.v["data"]).pack(fill="x", pady=(0, 10))
        self.b_usar = app._botao(esq, t("web_galeria_usar"), self._usar, True, icone="gerar", height=42)
        self.b_usar.pack(fill="x")
        self.l_erro = self.etiqueta(esq, "", wraplength=330)
        self.l_erro.configure(text_color=C["erro"])
        self.l_erro.pack(fill="x", pady=(6, 0))
        self.previa = ctk.CTkLabel(self, text="…", fg_color=C["visor"], corner_radius=12, text_color=C["suave"])
        self.previa.grid(row=0, column=1, sticky="nsew", padx=14, pady=12)
        for v in self.v.values():
            v.trace_add("write", lambda *_: self._agendar())
        self._agendar(0)

    def _n_premios(self) -> int:
        try:
            return min(max(int(self.v_n.get()), galeria.MIN_PREMIOS), galeria.MAX_PREMIOS)
        except ValueError:
            return galeria.MIN_PREMIOS

    def _mostrar_premios(self) -> None:
        for e in self.e_premios:
            e.pack_forget()
        for e in self.e_premios[:self._n_premios()]:
            e.pack(fill="x", pady=(0, 4))
        self._agendar(0)

    def _desenho(self, nome: str) -> None:
        self.v_desenho.set(next(d.id for d in galeria.DESENHOS if d.nome == nome))
        self._agendar(0)

    def _textos(self) -> core.galeria.Textos:
        v = {k: x.get().strip() for k, x in self.v.items()}
        return galeria.Textos(v["titulo"][:galeria.MAX_TITULO], v["organizacao"][:galeria.MAX_ORGANIZACAO],
                              tuple(v[f"p{i}"][:galeria.MAX_PREMIO] for i in range(1, self._n_premios() + 1) if v[f"p{i}"]), v["data"][:galeria.MAX_DATA])

    def _agendar(self, atraso: int = 350) -> None:
        if self._espera:
            self.after_cancel(self._espera)
        self._espera = self.after(atraso, self._desenhar)

    def _desenhar(self) -> None:
        self._espera = None
        self.token += 1
        token, desenho, textos = self.token, self.v_desenho.get(), self._textos()
        lingua = i18n.atual()
        gc.collect()                                     # ver App._analisar: o lixo do Tk apanha-se no fio principal

        def trabalho() -> None:
            if token != self.token:                      # entretanto escreveu-se mais: este desenho ja nao interessa
                return
            try:
                with i18n.com_lingua(lingua):
                    png = core.png_de_pagina(galeria.criar_template(desenho, textos), 110)
                self.app.fila.put(("galeria", token, png, None))
            except Exception as e:                       # os textos que a letra nao tem, etc.
                self.app.fila.put(("galeria", token, None, e))
        self.app.pool.submit(trabalho)

    def resultado(self, token: int, png: bytes | None, erro: Exception | None) -> None:
        if token != self.token or not self.winfo_exists():
            return
        self.l_erro.configure(text="" if erro is None else (str(erro) if isinstance(erro, core.ErroRifas) else t("erro_inesperado", erro=erro)))
        if png is None:
            return
        import io
        im = Image.open(io.BytesIO(png))
        self.update_idletasks()
        caixa = (max(self.previa.winfo_width() - 20, 200), max(self.previa.winfo_height() - 20, 200))
        im.thumbnail(caixa, Image.LANCZOS)
        self._foto = ctk.CTkImage(light_image=im, dark_image=im, size=im.size)
        self.previa.configure(image=self._foto, text="")

    def _usar(self) -> None:
        try:
            with i18n.com_lingua(i18n.atual()):
                modelo = galeria.criar_template(self.v_desenho.get(), self._textos())
                digitos = galeria.criar_algarismos()
        except core.ErroRifas as e:
            self.l_erro.configure(text=str(e))
            return
        self.app.usar_galeria(self.v_desenho.get(), modelo, digitos)
        self.destroy()


# ------------------------------------------------------------------ sorteio verificável
class Sorteio(Janela):
    def __init__(self, app):
        super().__init__(app, t("web_sorteio"), 640, 700)
        self.v_de, self.v_ate = tk.StringVar(value=app.v_inicio.get()), tk.StringVar(value=app.v_fim.get())
        self.v_quantos, self.v_saltar = tk.StringVar(value="1"), tk.StringVar(value=app.v_saltar.get())
        self.v_semente = tk.StringVar()
        self.etiqueta(self, t("web_sorteio_intro"), wraplength=590).pack(fill="x", padx=18, pady=(14, 0))
        c = self.cartao()
        g = ctk.CTkFrame(c, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=12)
        for i, (rotulo, var, larg) in enumerate(((t("de"), self.v_de, 110), (t("ate"), self.v_ate, 110),
                                                  (t("web_sorteio_quantos"), self.v_quantos, 110))):
            self.etiqueta(g, rotulo).grid(row=0, column=i, sticky="w", padx=(0 if i == 0 else 12, 0))
            app._entrada(g, var, width=larg).grid(row=1, column=i, sticky="w", padx=(0 if i == 0 else 12, 0))
        self.etiqueta(c, t("web_saltar")).pack(fill="x", padx=16)
        app._entrada(c, self.v_saltar, placeholder_text="13, 100-110").pack(fill="x", padx=16, pady=(0, 8))
        self.etiqueta(c, t("web_sorteio_semente")).pack(fill="x", padx=16)
        app._entrada(c, self.v_semente).pack(fill="x", padx=16)
        self.etiqueta(c, t("web_sorteio_semente_dica"), wraplength=560).pack(fill="x", padx=16, pady=(4, 0))
        app._botao(c, t("web_sorteio_drand"), self._drand, width=220, height=34).pack(anchor="w", padx=16, pady=(8, 12))
        linha = ctk.CTkFrame(self, fg_color="transparent")
        linha.pack(fill="x", padx=14, pady=(10, 0))
        self.b_sortear = app._botao(linha, t("web_sorteio_sortear"), self.sortear, True, height=42)
        self.b_sortear.pack(side="left", fill="x", expand=True)
        self.l_estado = self.etiqueta(self, "", wraplength=590)
        self.l_estado.pack(fill="x", padx=18, pady=(8, 0))
        self.etiqueta(self, t("web_sorteio_resultado"), suave=False).pack(fill="x", padx=18, pady=(8, 2))
        self.saida = ctk.CTkTextbox(self, height=130, corner_radius=8, fg_color=C["cartao"], text_color=C["texto"], border_width=1,
                                    border_color=C["borda"], font=ctk.CTkFont("Consolas", 14), state="disabled")
        self.saida.pack(fill="x", padx=14)
        self.etiqueta(self, t("web_sorteio_como"), wraplength=590).pack(fill="x", padx=18, pady=(8, 0))
        self.numeros: list[int] = []

    def sortear(self) -> list[int] | None:
        """Sorteia com o que está escrito; mostra o resultado ou o erro. Devolve os números (None se houve erro)."""
        try:
            self.numeros = core.sorteio.pedido(self.v_de.get(), self.v_ate.get(), self.v_quantos.get(), self.v_semente.get(), self.v_saltar.get())
        except core.ErroRifas as e:
            self.numeros = []
            self.l_estado.configure(text=str(e), text_color=C["erro"])
            self._mostrar("")
            return None
        self.l_estado.configure(text="", text_color=C["suave"])
        self._mostrar("\n".join(f"{i}.º  {n}" for i, n in enumerate(self.numeros, 1)))
        return self.numeros

    def _mostrar(self, texto: str) -> None:
        self.saida.configure(state="normal")
        self.saida.delete("1.0", "end")
        self.saida.insert("1.0", texto)
        self.saida.configure(state="disabled")

    def _drand(self) -> None:
        """A aleatoriedade pública do drand (a mesma que o site vai buscar): numa thread, para não prender a janela."""
        def trabalho() -> None:
            try:
                with urllib.request.urlopen("https://api.drand.sh/public/latest", timeout=8) as r:  # noqa: S310
                    d = json.loads(r.read(4096))
                semente = f"drand:{int(d['round'])}:{str(d['randomness'])[:64]}"
                self.after(0, lambda: self.winfo_exists() and self.v_semente.set(semente))
            except Exception:
                self.after(0, lambda: self.winfo_exists() and self.l_estado.configure(text=t("web_sorteio_drand_erro"), text_color=C["aviso"]))
        threading.Thread(target=trabalho, daemon=True).start()


# ------------------------------------------------------------------ editor de templates
class EditorTemplates(Janela):
    """Desenha-se UMA rifa (retângulos, linhas, textos e o número 0001, uma ou duas vezes) em vez de usar um template do Canva; «Usar este template»
    cria o template e os algarismos como a galeria. Os elementos, o histórico e o que está debaixo do rato vivem em `core.editor_modelo` (testável sem
    janelas); o que se vê é o PDF a sério (letra Vera) desenhado no worker da app e mostrado como imagem, e por cima desenham-se só a seleção e a pega.
    Arrastar mostra uma caixa tracejada e a imagem refaz-se ao largar."""

    MARGEM = 10

    def __init__(self, app):
        super().__init__(app, t("web_editor").rstrip("…"), 1180, 740)
        self.minsize(940, 580)
        self.m = editor_modelo.Modelo()
        self.sel: int | None = None
        self.token = 0
        self._espera = None
        self._foto = None
        self._arrasto = None
        self.escala = 1.0
        self.botoes: dict[str, ctk.CTkButton] = {}
        self.etiqueta(self, t("web_editor_intro"), wraplength=1180).pack(fill="x", padx=16, pady=(12, 0))
        self._barra((("texto", "web_editor_texto"), ("retangulo", "web_editor_retangulo"), ("linha", "web_editor_linha"),
                     ("numero", "web_editor_numero"), ("imagem", "web_editor_imagem")), lambda tipo: (lambda: self.acrescentar(tipo)), "+ ")
        self._barra((("desfazer", "web_editor_desfazer"), ("refazer", "web_editor_refazer"), ("duplicar", "web_editor_duplicar"),
                     ("frente", "web_editor_frente"), ("tras", "web_editor_tras"), ("apagar", "web_editor_apagar"),
                     ("modelo", "web_editor_modelo")), lambda nome: getattr(self, "_a_" + nome), "")
        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=14, pady=(8, 0))
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_rowconfigure(0, weight=1)
        self.tela = tk.Canvas(corpo, bg=self._cor("visor"), highlightthickness=0, takefocus=True)
        self.tela.grid(row=0, column=0, sticky="nsew")
        self.insp = ctk.CTkScrollableFrame(corpo, width=330, fg_color=C["cartao"], corner_radius=12, border_width=1, border_color=C["borda"])
        self.insp.grid(row=0, column=1, sticky="ns", padx=(12, 0))
        baixo = ctk.CTkFrame(self, fg_color="transparent")
        baixo.pack(fill="x", padx=14, pady=(8, 12))
        self.l_erro = self.etiqueta(baixo, "", wraplength=900)
        self.l_erro.configure(text_color=C["erro"])
        self.l_erro.pack(side="left", fill="x", expand=True)
        self.b_usar = app._botao(baixo, t("web_galeria_usar"), self._usar, True, icone="gerar", height=42, width=260)
        self.b_usar.pack(side="right")
        self.tela.bind("<ButtonPress-1>", self._clicar)
        self.tela.bind("<B1-Motion>", self._arrastar)
        self.tela.bind("<ButtonRelease-1>", self._largar)
        self.tela.bind("<Configure>", lambda e: self._ajustar())
        for seq, f in (("<Delete>", self._a_apagar), ("<Left>", lambda: self._seta(-1, 0)), ("<Right>", lambda: self._seta(1, 0)),
                       ("<Up>", lambda: self._seta(0, -1)), ("<Down>", lambda: self._seta(0, 1)),
                       ("<Shift-Left>", lambda: self._seta(-10, 0)), ("<Shift-Right>", lambda: self._seta(10, 0)),
                       ("<Shift-Up>", lambda: self._seta(0, -10)), ("<Shift-Down>", lambda: self._seta(0, 10))):
            self.tela.bind(seq, lambda e, f=f: f())
        for seq, f in (("<Control-z>", self._a_desfazer), ("<Control-y>", self._a_refazer), ("<Control-d>", self._a_duplicar)):
            self.bind(seq, lambda e, f=f: None if isinstance(self.focus_get(), tk.Entry) else f())
        self._inspetor()
        self._estado_botoes()
        self.after(60, self._ajustar)

    def _cor(self, chave: str) -> str:
        """Uma cor da paleta para o `tk.Canvas`, que (ao contrário dos widgets do CustomTkinter) não aceita o par «claro escuro»."""
        return self._apply_appearance_mode(C[chave])

    # ------------------------------------------------------------------ construção
    def _barra(self, itens, comando, prefixo: str) -> None:
        linha = ctk.CTkFrame(self, fg_color="transparent")
        linha.pack(fill="x", padx=14, pady=(8, 0))
        for chave, texto in itens:
            b = self.app._botao(linha, prefixo + t(texto), comando(chave), height=32)
            b.pack(side="left", padx=(0, 6))
            self.botoes[chave] = b

    def _campo_num(self, pai, rotulo: str, valor: float, aplicar, largura: int = 76) -> None:
        caixa = ctk.CTkFrame(pai, fg_color="transparent")
        caixa.pack(side="left", padx=(0, 8))
        self.etiqueta(caixa, rotulo).pack(anchor="w")
        var = tk.StringVar(value=f"{valor:g}")
        e = self.app._entrada(caixa, var, width=largura)
        e.pack()

        def aplicar_campo(_=None) -> None:
            try:
                v = float(var.get().replace(",", "."))
            except ValueError:
                var.set(f"{valor:g}")
                return
            if v != valor:
                aplicar(v)
        e.bind("<Return>", aplicar_campo)
        e.bind("<FocusOut>", aplicar_campo)

    def _botao_cor(self, pai, rotulo: str, cor: str, aplicar) -> None:
        caixa = ctk.CTkFrame(pai, fg_color="transparent")
        caixa.pack(side="left", padx=(0, 8))
        self.etiqueta(caixa, rotulo).pack(anchor="w")

        def escolher() -> None:
            nova = colorchooser.askcolor(color=cor or "#000000", parent=self)[1]
            if nova:
                aplicar(nova)
        ctk.CTkButton(caixa, text="", width=52, height=32, fg_color=cor or "#000000", hover_color=cor or "#000000", border_width=1,
                      border_color=C["borda"], command=escolher).pack()

    def _inspetor(self) -> None:
        for filho in self.insp.winfo_children():
            filho.destroy()
        m = self.m
        self.etiqueta(self.insp, t("web_editor_pagina"), wraplength=290, suave=False).pack(fill="x", pady=(4, 2))
        linha = ctk.CTkFrame(self.insp, fg_color="transparent")
        linha.pack(fill="x")
        self._campo_num(linha, "W", m.largura, lambda v: self._pagina(largura=v))
        self._campo_num(linha, "H", m.altura, lambda v: self._pagina(altura=v))
        self._botao_cor(linha, t("web_editor_fundo"), m.fundo, lambda c: self._pagina(fundo=c))
        e = m.por_id(self.sel) if self.sel is not None else None
        if e is None:
            return
        nomes = {"texto": "web_editor_texto", "retangulo": "web_editor_retangulo", "linha": "web_editor_linha", "numero": "web_editor_numero",
                 "imagem": "web_editor_imagem"}
        self.etiqueta(self.insp, t(nomes[e.tipo]), wraplength=290, suave=False).pack(fill="x", pady=(14, 2))
        linha = ctk.CTkFrame(self.insp, fg_color="transparent")
        linha.pack(fill="x")
        self._campo_num(linha, "X", e.x, lambda v: self._definir(x=v))
        self._campo_num(linha, "Y", e.y, lambda v: self._definir(y=v))
        if e.tipo in ("retangulo", "linha", "imagem"):
            linha = ctk.CTkFrame(self.insp, fg_color="transparent")
            linha.pack(fill="x", pady=(6, 0))
            self._campo_num(linha, "W", e.w, lambda v: self._definir(w=v))
            self._campo_num(linha, "H", e.h, lambda v: self._definir(h=v))
        if e.tipo == "texto":
            self.etiqueta(self.insp, t("web_editor_texto")).pack(fill="x", pady=(8, 0))
            var = tk.StringVar(value=e.texto)
            self.var_texto = var
            self.entrada_texto = self.app._entrada(self.insp, var)
            self.entrada_texto.pack(fill="x")
            var.trace_add("write", lambda *_: self._definir(texto=var.get()[:editor.MAX_TEXTO]))
        linha = ctk.CTkFrame(self.insp, fg_color="transparent")
        linha.pack(fill="x", pady=(8, 0))
        if e.tipo in ("texto", "numero"):
            self._campo_num(linha, t("web_editor_tamanho"), e.tamanho,
                            lambda v: self._definir(tamanho=min(max(v, editor.TAMANHO_MIN), editor.TAMANHO_MAX)))
            self._botao_cor(linha, t("web_editor_cor"), e.cor, lambda c: self._definir(cor=c))
        if e.tipo == "retangulo":
            self._botao_cor(linha, t("web_editor_cor"), e.cor, lambda c: self._definir(cor=c))
        if e.tipo in ("retangulo", "linha"):
            self._botao_cor(linha, t("web_editor_contorno"), e.contorno or "#000000",
                            lambda c: self._definir(contorno=c, espessura=e.espessura or 1.0))
            self._campo_num(linha, "pt", e.espessura, lambda v: self._definir(espessura=min(max(v, 0.0), 20.0)))
        if e.tipo == "texto":
            v_neg = tk.BooleanVar(value=e.negrito)
            self.caixa(self.insp, t("web_editor_negrito"), v_neg, command=lambda: self._definir(negrito=v_neg.get())).pack(anchor="w", pady=(8, 0))
        if e.tipo in ("texto", "numero"):
            v_rot = tk.BooleanVar(value=e.rot == 90)
            self.caixa(self.insp, t("web_editor_rodar"), v_rot, command=lambda: self._definir(rot=90 if v_rot.get() else 0)).pack(anchor="w", pady=(6, 0))

    # ------------------------------------------------------------------ ações (também usadas pelos testes)
    def _estado_botoes(self) -> None:
        m = self.m
        tem = self.sel is not None and m.por_id(self.sel) is not None
        for chave, ativo in (("desfazer", m.pode_desfazer()), ("refazer", m.pode_refazer()), ("duplicar", tem), ("frente", tem), ("tras", tem),
                             ("apagar", tem)):
            self.botoes[chave].configure(state="normal" if ativo else "disabled")
        p = m.problemas()
        texto = t("err_editor_numero") if p["numero"] else t("err_editor_digitos", texto=p["digitos"]) if p["digitos"] else ""
        self.l_erro.configure(text=texto)
        self.b_usar.configure(state="normal" if m.sem_problemas() and not self.app.a_gerar else "disabled")

    def _mudou(self, inspetor: bool = False, render: bool = True) -> None:
        if self.sel is not None and self.m.por_id(self.sel) is None:
            self.sel = None
            inspetor = True
        if inspetor:
            self._inspetor()
        self._estado_botoes()
        self._pintar_selecao()
        if render:
            self._agendar(120)

    def acrescentar(self, tipo: str, ficheiro: str | None = None) -> None:
        """Junta um elemento; a imagem pede o ficheiro (PNG ou JPG) numa janela, ou recebe-o já em `ficheiro` (os testes)."""
        if tipo == "imagem":
            self._juntar_imagem(ficheiro)
            return
        novo = self.m.adicionar(tipo)
        if novo is not None:
            self.sel = novo
            self._mudou(inspetor=True)

    def _juntar_imagem(self, ficheiro: str | None = None) -> None:
        ficheiro = ficheiro or filedialog.askopenfilename(parent=self, title=t("web_editor_imagem"), filetypes=[("PNG / JPG", "*.png *.jpg *.jpeg")])
        if not ficheiro:
            return
        try:
            novo = self.m.adicionar_imagem(Path(ficheiro).read_bytes())
        except (core.ErroRifas, OSError) as e:
            self.l_erro.configure(text=t("web_editor_imagem_invalida") if isinstance(e, OSError) else str(e))
            return
        if novo is not None:
            self.sel = novo
            self._mudou(inspetor=True)

    def _a_desfazer(self) -> None:
        if self.m.desfazer():
            self._ajustar(forcar=True)
            self._mudou(inspetor=True)

    def _a_refazer(self) -> None:
        if self.m.refazer():
            self._ajustar(forcar=True)
            self._mudou(inspetor=True)

    def _a_duplicar(self) -> None:
        if self.sel is not None:
            novo = self.m.duplicar(self.sel)
            if novo is not None:
                self.sel = novo
                self._mudou(inspetor=True)

    def _a_frente(self) -> None:
        if self.sel is not None and self.m.ordem(self.sel, 1):
            self._mudou()

    def _a_tras(self) -> None:
        if self.sel is not None and self.m.ordem(self.sel, -1):
            self._mudou()

    def _a_apagar(self) -> None:
        if self.sel is not None and self.m.apagar(self.sel):
            self.sel = None
            self._mudou(inspetor=True)

    def _a_modelo(self) -> None:
        """«Começar com um modelo»: também se desfaz."""
        passado = [*self.m.passado, self.m._snapshot()]
        self.m.carregar(editor_modelo.modelo_com_talao())
        self.m.passado = passado[-editor_modelo.MAX_HISTORICO:]
        self.sel = None
        self._ajustar(forcar=True)
        self._mudou(inspetor=True)

    def _seta(self, dx: float, dy: float) -> None:
        if self.sel is not None:
            self.m.mover(self.sel, dx, dy, "seta")
            self._mudou()

    def _definir(self, **campos) -> None:
        if self.sel is not None and self.m.definir(self.sel, **campos):
            self._mudou(inspetor=set(campos) != {"texto"})

    def _pagina(self, **kw) -> None:
        self.m.pagina(**kw)
        self._ajustar(forcar=True)
        self._mudou(inspetor=True)

    # ------------------------------------------------------------------ o ecrã
    def _ajustar(self, forcar: bool = False) -> None:
        """A escala (px por pt): a rifa inteira cabe na tela. Se mudou, refaz-se a imagem."""
        if not self.winfo_exists():
            return
        larg = max(self.tela.winfo_width() - 2 * self.MARGEM, 240)
        alt = max(self.tela.winfo_height() - 2 * self.MARGEM, 120)
        nova = round(min(larg / self.m.largura, alt / self.m.altura, 2.5), 3)
        if forcar or abs(nova - self.escala) > 0.005:
            self.escala = nova
            self._agendar(0)
        self._pintar_selecao()

    def _px(self, x: float, y: float) -> tuple[float, float]:
        return self.MARGEM + x * self.escala, self.MARGEM + y * self.escala

    def _pt(self, px: float, py: float) -> tuple[float, float]:
        return (px - self.MARGEM) / self.escala, (py - self.MARGEM) / self.escala

    def _pintar_selecao(self) -> None:
        self.tela.delete("sel")
        if self.sel is None:
            return
        c = self.m.caixa(self.sel)
        if c is None:
            return
        x0, y0 = self._px(c[0] - 2, c[1] - 2)
        x1, y1 = self._px(c[2] + 2, c[3] + 2)
        self.tela.create_rectangle(x0, y0, x1, y1, outline=self._cor("acento"), dash=(4, 3), width=2, tags="sel")
        e = self.m.por_id(self.sel)
        if e is not None and e.tipo in ("retangulo", "linha"):
            hx, hy = self._px(e.x + e.w, e.y + e.h)
            self.tela.create_rectangle(hx - 5, hy - 5, hx + 5, hy + 5, fill=self._cor("acento"), outline=self._cor("sobre_acento"), tags="sel")

    def _agendar(self, atraso: int = 120) -> None:
        if self._espera:
            self.after_cancel(self._espera)
        self._espera = self.after(atraso, self._desenhar)

    def _desenhar(self) -> None:
        self._espera = None
        if not self.winfo_exists():
            return
        self.token += 1
        token, escala, lingua = self.token, self.escala, i18n.atual()
        try:
            desenho = self.m.desenho()
        except core.ErroRifas:
            return                                                # um desenho que ainda não serve (p.ex. sem número): a imagem velha fica
        gc.collect()                                              # ver App._analisar: o lixo do Tk apanha-se no fio principal

        def trabalho() -> None:
            if token != self.token:
                return
            try:
                with i18n.com_lingua(lingua):
                    png = core.png_de_pagina(editor.criar_template(desenho), max(round(72 * escala), 24))
                self.app.fila.put(("editor", token, png, None))
            except Exception as e:                                # noqa: BLE001
                self.app.fila.put(("editor", token, None, e))
        self.app.pool.submit(trabalho)

    def resultado(self, token: int, png: bytes | None, erro: Exception | None) -> None:
        if token != self.token or not self.winfo_exists():
            return
        if erro is not None:
            self.l_erro.configure(text=str(erro) if isinstance(erro, core.ErroRifas) else t("erro_inesperado", erro=erro))
            return
        if png is None:
            return
        import io

        from PIL import ImageTk
        self._foto = ImageTk.PhotoImage(Image.open(io.BytesIO(png)))
        self.tela.delete("pagina")
        self.tela.create_image(self.MARGEM, self.MARGEM, image=self._foto, anchor="nw", tags="pagina")
        self.tela.tag_lower("pagina")
        self._estado_botoes()

    # ------------------------------------------------------------------ o rato
    def _clicar(self, ev) -> None:
        self.tela.focus_set()
        x, y = self._pt(ev.x, ev.y)
        e = self.m.por_id(self.sel) if self.sel is not None else None
        if e is not None and e.tipo in ("retangulo", "linha"):
            hx, hy = self._px(e.x + e.w, e.y + e.h)
            if abs(ev.x - hx) <= 8 and abs(ev.y - hy) <= 8:       # a pega do canto: redimensionar
                self._arrasto = ("tamanho", e.id, x, y, e.w, e.h)
                return
        novo = self.m.elemento_em(x, y)
        if novo != self.sel:
            self.sel = novo
            self._inspetor()
            self._estado_botoes()
        self._pintar_selecao()
        e = self.m.por_id(novo) if novo is not None else None
        self._arrasto = ("mover", e.id, x, y, e.x, e.y) if e is not None else None

    def _arrastar(self, ev) -> None:
        if self._arrasto is None:
            return
        modo, id_, x0, y0, a, b = self._arrasto
        x, y = self._pt(ev.x, ev.y)
        dx, dy = x - x0, y - y0
        if modo == "mover":
            self.m.definir(id_, x=round(a + dx), y=round(b + dy))
        else:
            self.m.definir(id_, w=round(a + dx), h=round(b + dy))
        self._pintar_selecao()                                    # só a caixa tracejada: a imagem refaz-se ao largar

    def _largar(self, ev) -> None:
        if self._arrasto is not None:
            self._arrasto = None
            self._mudou(inspetor=True)

    # ------------------------------------------------------------------ usar
    def _usar(self) -> None:
        try:
            with i18n.com_lingua(i18n.atual()):
                modelo = editor.criar_template(self.m.desenho())
                digitos = galeria.criar_algarismos()
        except core.ErroRifas as e:
            self.l_erro.configure(text=str(e))
            return
        self.app.usar_galeria("editor", modelo, digitos)
        self.destroy()

    def destroy(self) -> None:
        if self._espera:
            try:
                self.after_cancel(self._espera)
            except Exception:
                pass
        super().destroy()


# ------------------------------------------------------------------ preçário (gerador de preçários para festas)
def _com_lingua(lingua: str, fn, *a):
    with i18n.com_lingua(lingua):
        return fn(*a)


def _hoje() -> int:
    import datetime
    return datetime.date.today().month


class Precario(Janela):
    """O preçário na app Windows: a mesma lógica do site (`core.precario`, `core.precario_catalogo`, `core.moeda`) numa janela: ocasião e tema, artigos (caixas por categoria), preços,
    moeda (a do país da língua ou uma inventada) e aspeto, com a pré-visualização desenhada no worker da app (o PDFium só corre lá; chega por `App._ev_precario`) e «Guardar PDF»,
    «Guardar imagem» e o ficheiro `.precario` (só os campos). Diferença para o site: a moeda escolhe-se numa lista de moedas (o Tk não tem os nomes dos países)."""

    def __init__(self, app):
        super().__init__(app, t("web_precario"), 1120, 760)
        self.lingua = i18n.atual()
        self.token = 0
        self._espera = None
        self._foto = None
        self._a_aplicar = False                        # ao abrir um ficheiro as variáveis mudam todas de seguida: só se desenha no fim
        self._ocasiao_anterior = ""
        self.artigos = {a.id: a for a in precario_catalogo.artigos_da_lingua(self.lingua)}
        self.ocasioes = precario_catalogo.ocasioes_da_lingua(self.lingua)
        self.sugerida = precario_catalogo.ocasiao_da_epoca(_hoje(), self.lingua)
        self.linhas: list[dict] = []                   # {chave, artigo, nome, categoria, emoji}
        self.v_preco: dict[str, tk.StringVar] = {}
        self.v_preco2: dict[str, tk.StringVar] = {}           # o segundo preço (só com «dois tamanhos»)
        self.v_tamanhos = tk.BooleanVar()
        self.v_rotulo1, self.v_rotulo2 = tk.StringVar(), tk.StringVar()
        self.v_artigo = {a: tk.BooleanVar() for a in self.artigos}
        self.v_titulo, self.v_subtitulo, self.v_rodape, self.v_meu = (tk.StringVar() for _ in range(4))
        self.v_moeda = tk.StringVar()
        self.v_inventada, self.v_inv_antes, self.v_imagens = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(value=True)
        self.v_inv_nome, self.v_inv_casas = tk.StringVar(), tk.StringVar(value="0")
        self.v_formato, self.v_orientacao, self.v_colunas = tk.StringVar(value="A4"), tk.StringVar(), tk.StringVar()
        self.v_desenho, self.v_ocasiao = tk.StringVar(value="quermesse"), tk.StringVar()
        self._orientacoes = {"vertical": t("web_precario_vertical"), "horizontal": t("web_precario_horizontal")}
        self._colunas = {0: t("web_precario_auto"), 1: "1", 2: "2", 3: "3"}
        self._formatos = {f: (t("web_precario_cartoes") if f == precario.CARTOES else f) for f in precario.FORMATOS}
        self.v_orientacao.set(self._orientacoes["vertical"])
        self.v_colunas.set(self._colunas[0])
        self.v_formato.set(self._formatos["A4"])
        self._moedas = {f"{m.codigo} ({m.simbolo})": m.codigo for m in moeda.MOEDAS.values()}
        padrao = moeda.moeda_por_omissao(self.lingua)
        self.v_moeda.set(f"{padrao.codigo} ({padrao.simbolo})")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        esq = ctk.CTkScrollableFrame(self, fg_color="transparent", width=420)
        esq.grid(row=0, column=0, sticky="ns", padx=(14, 0), pady=12)
        self.etiqueta(esq, t("web_precario_intro"), wraplength=400).pack(fill="x", pady=(0, 6))
        self.etiqueta(esq, t("web_precario_ocasiao")).pack(fill="x")
        self.m_ocasiao = self._menu(esq, [self._nome_ocasiao(o) for o in self.ocasioes], self._escolher_ocasiao)
        self.m_ocasiao.pack(fill="x", pady=(0, 6))
        self.etiqueta(esq, t("web_precario_aspeto")).pack(fill="x")
        self.m_desenho = self._menu(esq, [d.nome for d in precario.DESENHOS], self._mudar_desenho)
        self.m_desenho.pack(fill="x", pady=(0, 8))
        self.etiqueta(esq, t("web_precario_artigos")).pack(fill="x", pady=(4, 0))
        self.f_artigos = ctk.CTkFrame(esq, fg_color="transparent")
        self.f_artigos.pack(fill="x")
        for c in precario_catalogo.CATEGORIAS.values():
            itens = [a for a in self.artigos.values() if a.categoria == c.id]
            if not itens:
                continue
            ctk.CTkLabel(self.f_artigos, text=precario_catalogo.nome(c, self.lingua), anchor="w", text_color=C["texto"], font=ctk.CTkFont(FONTE, 13, "bold")).pack(fill="x", pady=(8, 2))
            for a in itens:
                self.caixa(self.f_artigos, precario_catalogo.nome(a, self.lingua), self.v_artigo[a.id], command=lambda i=a.id: self._alternar(i)).pack(anchor="w", pady=1)
        meu = ctk.CTkFrame(esq, fg_color="transparent")
        meu.pack(fill="x", pady=(10, 0))
        self.e_meu = app._entrada(meu, self.v_meu, placeholder_text=t("web_precario_nome_artigo"))
        self.e_meu.pack(side="left", fill="x", expand=True)
        app._botao(meu, "+", self._juntar, width=36).pack(side="left", padx=(6, 0))
        self.etiqueta(esq, t("web_precario_dica_preco"), wraplength=400).pack(fill="x", pady=(10, 0))
        self.f_precos = ctk.CTkFrame(esq, fg_color="transparent")
        self.f_precos.pack(fill="x")
        self.etiqueta(esq, t("web_precario_moeda")).pack(fill="x", pady=(12, 0))
        self.m_moeda = self._menu(esq, list(self._moedas), lambda _: self._agendar(0), variavel=self.v_moeda)
        self.m_moeda.pack(fill="x", pady=(0, 4))
        self.caixa(esq, t("web_precario_moeda_inventada"), self.v_inventada, command=lambda: self._agendar(0)).pack(anchor="w", pady=2)
        inv = ctk.CTkFrame(esq, fg_color="transparent")
        inv.pack(fill="x")
        self.etiqueta(inv, t("web_precario_inventada_nome")).pack(fill="x")
        app._entrada(inv, self.v_inv_nome).pack(fill="x", pady=(0, 4))
        self.caixa(inv, t("web_precario_inventada_antes"), self.v_inv_antes, command=lambda: self._agendar(0)).pack(anchor="w")
        linha_c = ctk.CTkFrame(inv, fg_color="transparent")
        linha_c.pack(fill="x", pady=(4, 0))
        self.etiqueta(linha_c, t("web_precario_inventada_casas")).pack(side="left")
        self._menu(linha_c, ["0", "1", "2"], lambda _: self._agendar(0), variavel=self.v_inv_casas, largura=70).pack(side="right")
        for rotulo, var in ((t("web_precario_campo_titulo"), self.v_titulo), (t("web_precario_campo_subtitulo"), self.v_subtitulo), (t("web_precario_campo_rodape"), self.v_rodape)):
            self.etiqueta(esq, rotulo).pack(fill="x", pady=(8, 0))
            app._entrada(esq, var).pack(fill="x")
        opcoes = ctk.CTkFrame(esq, fg_color="transparent")
        opcoes.pack(fill="x", pady=(8, 0))
        for rotulo, valores, var in ((t("web_precario_formato"), list(self._formatos.values()), self.v_formato),
                                     (t("web_precario_vertical") + " / " + t("web_precario_horizontal"), list(self._orientacoes.values()), self.v_orientacao),
                                     (t("web_precario_colunas"), list(self._colunas.values()), self.v_colunas)):
            col = ctk.CTkFrame(opcoes, fg_color="transparent")
            col.pack(side="left", expand=True, fill="x", padx=2)
            self.etiqueta(col, rotulo, wraplength=120).pack(fill="x")
            self._menu(col, valores, lambda _: self._agendar(0), variavel=var).pack(fill="x")
        self.caixa(esq, t("web_precario_imagens"), self.v_imagens, command=lambda: self._agendar(0)).pack(anchor="w", pady=(8, 4))
        self.caixa(esq, t("web_precario_tamanhos"), self.v_tamanhos, command=self._precos).pack(anchor="w", pady=(0, 2))
        self.f_rotulos = ctk.CTkFrame(esq, fg_color="transparent")                # os nomes das duas colunas: só com «dois tamanhos»
        self.etiqueta(self.f_rotulos, t("web_precario_rotulos")).pack(fill="x")
        linha_r = ctk.CTkFrame(self.f_rotulos, fg_color="transparent")
        linha_r.pack(fill="x")
        for var, padrao in ((self.v_rotulo1, t("web_precario_tamanho_1")), (self.v_rotulo2, t("web_precario_tamanho_2"))):
            app._entrada(linha_r, var, width=120, placeholder_text=padrao).pack(side="left", padx=(0, 6))
            var.trace_add("write", lambda *_: self._agendar())
        self.b_pdf = app._botao(esq, t("win_precario_pdf"), self._guardar_pdf, True, icone="gerar", height=40)
        self.b_pdf.pack(fill="x", pady=(8, 4))
        app._botao(esq, t("win_precario_imagem"), self._guardar_imagem, height=34).pack(fill="x", pady=2)
        app._botao(esq, t("web_vales_titulo") + "…", self._vales, height=34).pack(fill="x", pady=2)
        app._botao(esq, t("win_precario_guardar"), self._guardar_ficheiro, height=34).pack(fill="x", pady=2)
        app._botao(esq, t("win_precario_abrir"), self._abrir_ficheiro, height=34).pack(fill="x", pady=2)
        self.l_erro = self.etiqueta(esq, "", wraplength=400)
        self.l_erro.configure(text_color=C["erro"])
        self.l_erro.pack(fill="x", pady=(6, 0))
        self.previa = ctk.CTkLabel(self, text=t("web_precario_vazio"), fg_color=C["visor"], corner_radius=12, text_color=C["suave"], wraplength=420)
        self.previa.grid(row=0, column=1, sticky="nsew", padx=14, pady=12)
        for v in (self.v_titulo, self.v_subtitulo, self.v_rodape, self.v_inv_nome):
            v.trace_add("write", lambda *_: self._agendar())
        inicial = self.sugerida or (self.ocasioes[0] if self.ocasioes else None)
        if inicial is not None:
            self._escolher_ocasiao(self._nome_ocasiao(inicial))
        self._agendar(0)

    # -- widgets
    def _menu(self, pai, valores, comando, variavel=None, largura=None) -> ctk.CTkOptionMenu:
        kw = {"width": largura} if largura else {}
        if variavel is not None:
            kw["variable"] = variavel
        return ctk.CTkOptionMenu(pai, values=valores, corner_radius=8, height=32, fg_color=C["campo"], button_color=C["borda"], button_hover_color=C["acento_suave"],
                                 text_color=C["texto"], dropdown_fg_color=C["cartao"], dropdown_text_color=C["texto"], dropdown_hover_color=C["acento_suave"],
                                 font=ctk.CTkFont(FONTE, 13), command=comando, **kw)

    def _nome_ocasiao(self, o) -> str:
        return ("★ " if self.sugerida is not None and self.sugerida.id == o.id else "") + precario_catalogo.nome(o, self.lingua)

    # -- escolhas
    def _escolher_ocasiao(self, nome: str) -> None:
        o = next((x for x in self.ocasioes if self._nome_ocasiao(x) == nome), None)
        if o is None:
            return
        anterior = precario_catalogo.nome(precario_catalogo.OCASIOES[self._ocasiao_anterior], self.lingua) if self._ocasiao_anterior else ""
        self.v_ocasiao.set(o.id)
        self.m_ocasiao.set(nome)
        self.v_desenho.set(o.desenho)
        self.m_desenho.set(precario.POR_ID[o.desenho].nome)
        if not self.v_titulo.get().strip() or self.v_titulo.get() == anterior:
            self.v_titulo.set(precario_catalogo.nome(o, self.lingua)[:precario.MAX_TITULO])
        self._ocasiao_anterior = o.id
        for a, v in self.v_artigo.items():
            v.set(a in o.artigos)
        livres = [ln for ln in self.linhas if not ln["artigo"]]
        self.linhas = [{"chave": a, "artigo": a, "nome": "", "categoria": "", "emoji": ""} for a in o.artigos if a in self.artigos] + livres
        self._precos()

    def _mudar_desenho(self, nome: str) -> None:
        self.v_desenho.set(next(d.id for d in precario.DESENHOS if d.nome == nome))
        self._agendar(0)

    def _alternar(self, artigo: str) -> None:
        if self.v_artigo[artigo].get():
            if not any(ln["artigo"] == artigo for ln in self.linhas) and len(self.linhas) < precario.MAX_LINHAS:
                self.linhas.append({"chave": artigo, "artigo": artigo, "nome": "", "categoria": "", "emoji": ""})
            else:
                self.v_artigo[artigo].set(any(ln["artigo"] == artigo for ln in self.linhas))
        else:
            self.linhas = [ln for ln in self.linhas if ln["artigo"] != artigo]
        self._precos()

    def _juntar(self) -> None:
        nome = self.v_meu.get().strip()[:precario.MAX_NOME]
        if not nome or len(self.linhas) >= precario.MAX_LINHAS:
            return
        self.linhas.append({"chave": f"c{len(self.linhas)}-{nome}", "artigo": "", "nome": nome, "categoria": "extras", "emoji": ""})
        self.v_meu.set("")
        self._precos()

    def _tirar(self, chave: str) -> None:
        ln = next((x for x in self.linhas if x["chave"] == chave), None)
        if ln is None:
            return
        if ln["artigo"]:
            self.v_artigo[ln["artigo"]].set(False)
        self.linhas.remove(ln)
        self._precos()

    def _nome_da_linha(self, ln: dict) -> str:
        return ln["nome"] or precario_catalogo.nome(self.artigos[ln["artigo"]], self.lingua)

    def _precos(self) -> None:
        """Refaz as linhas de preço (uma por artigo escolhido); o que já se escreveu fica (as variáveis vivem em `v_preco`)."""
        for w in self.f_precos.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.f_precos, text=t("web_precario_escolhidos", n=len(self.linhas)), anchor="w", text_color=C["texto"], font=ctk.CTkFont(FONTE, 13, "bold")).pack(fill="x", pady=(8, 2))
        for ln in self.linhas:
            v = self.v_preco.get(ln["chave"])
            if v is None:
                v = self.v_preco[ln["chave"]] = tk.StringVar()
                v.trace_add("write", lambda *_: self._agendar())
            linha = ctk.CTkFrame(self.f_precos, fg_color="transparent")
            linha.pack(fill="x", pady=1)
            ctk.CTkLabel(linha, text=self._nome_da_linha(ln), anchor="w", text_color=C["texto"], font=ctk.CTkFont(FONTE, 12), width=190).pack(side="left")
            ctk.CTkEntry(linha, textvariable=v, width=100 if not self.v_tamanhos.get() else 70, height=28, corner_radius=8, fg_color=C["campo"], border_color=C["borda"], text_color=C["texto"],
                         font=ctk.CTkFont(FONTE, 12), placeholder_text=self.v_rotulo1.get().strip() or t("web_precario_tamanho_1") if self.v_tamanhos.get() else t("web_precario_preco"),
                         placeholder_text_color=C["suave"]).pack(side="left", padx=4)
            if self.v_tamanhos.get():
                v2 = self.v_preco2.get(ln["chave"])
                if v2 is None:
                    v2 = self.v_preco2[ln["chave"]] = tk.StringVar()
                    v2.trace_add("write", lambda *_: self._agendar())
                ctk.CTkEntry(linha, textvariable=v2, width=70, height=28, corner_radius=8, fg_color=C["campo"], border_color=C["borda"], text_color=C["texto"],
                             font=ctk.CTkFont(FONTE, 12), placeholder_text=self.v_rotulo2.get().strip() or t("web_precario_tamanho_2"), placeholder_text_color=C["suave"]).pack(side="left", padx=(0, 4))
            ctk.CTkButton(linha, text="×", width=28, height=28, corner_radius=8, fg_color=C["campo"], hover_color=C["borda"], text_color=C["texto"], border_width=1,
                          border_color=C["borda"], command=lambda c=ln["chave"]: self._tirar(c)).pack(side="left")
        if self.v_tamanhos.get():
            self.f_rotulos.pack(fill="x", before=self.b_pdf)
        else:
            self.f_rotulos.pack_forget()
        self._agendar(0)

    # -- o preçário e a pré-visualização
    def precario(self) -> "precario.Precario":
        """O `core.precario.Precario` do que está na janela (levanta `ErroRifas` se um preço não se lê)."""
        linhas = []
        for ln in self.linhas:
            texto = self.v_preco[ln["chave"]].get().strip() if ln["chave"] in self.v_preco else ""
            preco = None
            if texto:
                preco = moeda.valor_de_texto(texto, self.lingua)
                if preco is None:
                    raise core.ErroRifas("err_precario_texto", car=texto[:14])
            texto2 = self.v_preco2[ln["chave"]].get().strip() if self.v_tamanhos.get() and ln["chave"] in self.v_preco2 else ""
            preco2 = None
            if texto2:
                preco2 = moeda.valor_de_texto(texto2, self.lingua)
                if preco2 is None:
                    raise core.ErroRifas("err_precario_texto", car=texto2[:14])
            linhas.append(precario.Linha(ln["artigo"], ln["nome"], preco, ln["categoria"], ln["emoji"], preco2))
        nome = " ".join(self.v_inv_nome.get().split())
        if self.v_inventada.get() and nome:
            m = moeda.MoedaInventada(nome, self.v_inv_antes.get(), int(self.v_inv_casas.get() or 0))
        else:
            m = moeda.MOEDAS[self._moedas.get(self.v_moeda.get(), "EUR")]
        orientacao = next((k for k, v in self._orientacoes.items() if v == self.v_orientacao.get()), "vertical")
        colunas = next((k for k, v in self._colunas.items() if v == self.v_colunas.get()), 0)
        formato = next((k for k, v in self._formatos.items() if v == self.v_formato.get()), "A4")
        return precario.Precario(linhas=tuple(linhas), titulo=self.v_titulo.get().strip()[:precario.MAX_TITULO], subtitulo=self.v_subtitulo.get().strip()[:precario.MAX_SUBTITULO],
                                 rodape=self.v_rodape.get().strip()[:precario.MAX_RODAPE], desenho=self.v_desenho.get() or "quermesse", formato=formato,
                                 orientacao=orientacao, colunas=colunas, imagens=self.v_imagens.get(), moeda=m, lingua=self.lingua,
                                 tamanhos=self.v_tamanhos.get(), rotulos=(self.v_rotulo1.get().strip() or t("web_precario_tamanho_1"), self.v_rotulo2.get().strip() or t("web_precario_tamanho_2")))

    def _agendar(self, atraso: int = 350) -> None:
        if self._a_aplicar or not self.winfo_exists():
            return
        if self._espera:
            self.after_cancel(self._espera)
        self._espera = self.after(atraso, self._desenhar)

    def _desenhar(self) -> None:
        self._espera = None
        self.token += 1
        token = self.token
        try:
            p = self.precario()
        except core.ErroRifas as e:
            self.l_erro.configure(text=str(e))
            return
        if not p.linhas:
            self.l_erro.configure(text="")
            self._foto = None
            self.previa.configure(image="", text=t("web_precario_vazio"))
            return
        gc.collect()                                     # ver App._analisar: o lixo do Tk apanha-se no fio principal

        def trabalho() -> None:
            if token != self.token:
                return
            try:
                with i18n.com_lingua(p.lingua):
                    png = core.png_de_pagina(precario.criar_pdf(p), 110)
                self.app.fila.put(("precario", token, png, None))
            except Exception as e:                       # os textos que a letra nao tem, etc.
                self.app.fila.put(("precario", token, None, e))
        self.app.pool.submit(trabalho)

    def resultado(self, token: int, png: bytes | None, erro: Exception | None) -> None:
        if token != self.token or not self.winfo_exists():
            return
        self.l_erro.configure(text="" if erro is None else (str(erro) if isinstance(erro, core.ErroRifas) else t("erro_inesperado", erro=erro)))
        if png is None:
            return
        import io
        im = Image.open(io.BytesIO(png))
        self.update_idletasks()
        im.thumbnail((max(self.previa.winfo_width() - 20, 200), max(self.previa.winfo_height() - 20, 200)), Image.LANCZOS)
        self._foto = ctk.CTkImage(light_image=im, dark_image=im, size=im.size)
        self.previa.configure(image=self._foto, text="")

    # -- guardar e abrir
    def _guardar(self, titulo: str, extensao: str, tipo: str, dados, destino: str | None = None) -> Path | None:
        try:
            conteudo = dados(self.precario())
        except core.ErroRifas as e:
            self.l_erro.configure(text=str(e))
            return None
        destino = destino or filedialog.asksaveasfilename(parent=self, title=titulo.rstrip("…"), initialdir=self.app._dir_de(self.app.v_saida), initialfile="precario" + extensao,
                                                          defaultextension=extensao, filetypes=[(tipo, "*" + extensao), (t("dlg_tipo_todos"), "*.*")])
        if not destino:
            return None
        try:
            Path(destino).write_bytes(conteudo)
        except OSError as e:
            messagebox.showerror(t("app_nome"), t("erro_inesperado", erro=e))
            return None
        self.l_erro.configure(text="")
        return Path(destino)

    def _vales(self) -> None:
        """«Vales numerados…»: só com uma moeda inventada com nome (o aviso diz como); abre a janela dos vales com o desenho e a moeda deste preçário."""
        nome = self.v_inv_nome.get().strip()
        if not self.v_inventada.get() or not nome:
            self.l_erro.configure(text=t("web_vales_intro"))
            return
        self.l_erro.configure(text="")
        antiga = self.app.w_extras.get("vales")
        if antiga is not None and antiga.winfo_exists():
            antiga.destroy()
        self.app.w_extras["vales"] = Vales(self.app, nome, vales.desenho_do_vale(self.v_desenho.get()), self.v_subtitulo.get())

    def _guardar_pdf(self, destino: str | None = None) -> Path | None:
        return self._guardar(t("win_precario_pdf"), ".pdf", "PDF", lambda p: _com_lingua(p.lingua, precario.criar_pdf, p), destino)

    def _guardar_imagem(self, destino: str | None = None) -> Path | None:
        return self._guardar(t("win_precario_imagem"), ".png", "PNG", lambda p: core.png_de_pagina(_com_lingua(p.lingua, precario.criar_pdf, p), 150), destino)

    def _guardar_ficheiro(self, destino: str | None = None) -> Path | None:
        return self._guardar(t("win_precario_guardar"), precario.EXTENSAO, "Preçário", precario.para_bytes, destino)

    def _abrir_ficheiro(self, ficheiro: str | None = None) -> bool:
        """Pergunta que preçário abrir (ou recebe o `ficheiro`, nos testes) e repõe a janela. False se desistiu ou o ficheiro não serve."""
        destino = ficheiro or filedialog.askopenfilename(parent=self, title=t("win_precario_abrir").rstrip("…"), initialdir=self.app._dir_de(self.app.v_saida),
                                                         filetypes=[("Preçário", "*" + precario.EXTENSAO), (t("dlg_tipo_todos"), "*.*")])
        if not destino:
            return False
        try:
            with open(destino, "rb") as f:
                p = precario.de_bytes(f.read(precario.MAX_BYTES + 1), self.lingua)
        except (OSError, core.ErroRifas) as e:
            messagebox.showwarning(t("app_nome"), str(e) if isinstance(e, core.ErroRifas) else t("erro_inesperado", erro=e))
            return False
        self.aplicar(p)
        return True

    def aplicar(self, p: "precario.Precario") -> None:
        """Repõe a janela com o preçário `p`: os artigos que a língua vê voltam a ser caixas; os outros (de uma região que esta língua não vê, ou textos livres) ficam como linhas livres."""
        self._a_aplicar = True
        try:
            self.v_titulo.set(p.titulo)
            self.v_subtitulo.set(p.subtitulo)
            self.v_rodape.set(p.rodape)
            self.v_desenho.set(p.desenho)
            self.m_desenho.set(precario.POR_ID[p.desenho].nome)
            self.v_formato.set(self._formatos[p.formato])
            self.v_orientacao.set(self._orientacoes[p.orientacao])
            self.v_colunas.set(self._colunas[p.colunas])
            self.v_imagens.set(p.imagens)
            self.v_tamanhos.set(p.tamanhos)
            self.v_rotulo1.set(p.rotulos[0])
            self.v_rotulo2.set(p.rotulos[1])
            if isinstance(p.moeda, moeda.MoedaInventada):
                self.v_inventada.set(True)
                self.v_inv_nome.set(p.moeda.nome)
                self.v_inv_antes.set(p.moeda.antes)
                self.v_inv_casas.set(str(p.moeda.decimais))
            else:
                self.v_inventada.set(False)
                self.v_moeda.set(f"{p.moeda.codigo} ({p.moeda.simbolo})")
            for v in self.v_artigo.values():
                v.set(False)
            self.linhas, self.v_preco, self.v_preco2 = [], {}, {}
            for i, ln in enumerate(p.linhas):
                original = precario_catalogo.ARTIGOS.get(ln.artigo)
                if ln.artigo in self.artigos:
                    chave = ln.artigo
                    self.v_artigo[ln.artigo].set(True)
                    self.linhas.append({"chave": chave, "artigo": ln.artigo, "nome": ln.nome, "categoria": "", "emoji": ""})
                else:
                    nome = ln.nome or (precario_catalogo.nome(original, self.lingua) if original else "?")
                    chave = f"c{i}-{nome}"
                    self.linhas.append({"chave": chave, "artigo": "", "nome": nome, "categoria": ln.categoria or (original.categoria if original else "extras"), "emoji": ln.emoji or (original.emoji if original else "")})
                texto = moeda.numero(ln.preco, p.moeda.decimais, self.lingua) if ln.preco is not None else ""
                var = self.v_preco[chave] = tk.StringVar(value=texto)
                var.trace_add("write", lambda *_: self._agendar())
                if ln.preco2 is not None:
                    var2 = self.v_preco2[chave] = tk.StringVar(value=moeda.numero(ln.preco2, p.moeda.decimais, self.lingua))
                    var2.trace_add("write", lambda *_: self._agendar())
        finally:
            self._a_aplicar = False
        self._precos()


# ------------------------------------------------------------------ vales de fichas numerados (fase 7 do preçário)
class Vales(Janela):
    """«Vales numerados»: com uma moeda inventada no preçário, desenha o vale (o mesmo desenho do preçário, o valor em grande) e «Criar vales numerados»
    põe o template e os algarismos na janela principal (como a galeria): o resto (séries, QR de verificação, folhas) é o gerador de rifas.
    A pré-visualização desenha-se no worker da app e chega por `App._ev_vales`. Aberta pela janela do preçário, que lhe passa o desenho, o nome e a organização."""

    def __init__(self, app, moeda_plural: str, desenho: str, organizacao: str = ""):
        super().__init__(app, t("web_vales_titulo"), 860, 520)
        self.token = 0
        self._espera = None
        self._foto = None
        self.desenho, self.moeda_plural, self.organizacao = desenho, moeda_plural.strip(), organizacao
        self.v = {k: tk.StringVar() for k in ("titulo", "singular", "quantidade", "organizacao", "nota")}
        self.v["titulo"].set(t("web_vales_cabecalho_padrao"))
        self.v["quantidade"].set("1")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        esq = ctk.CTkFrame(self, fg_color="transparent", width=340)
        esq.grid(row=0, column=0, sticky="ns", padx=(14, 0), pady=12)
        self.etiqueta(esq, t("web_vales_intro"), wraplength=330).pack(fill="x", pady=(0, 8))
        for chave, rotulo in (("titulo", t("web_vales_cabecalho")), ("singular", t("web_vales_singular")), ("quantidade", t("web_vales_quantidade")),
                              ("organizacao", t("web_galeria_organizacao")), ("nota", t("web_vales_nota"))):
            self.etiqueta(esq, rotulo, wraplength=330).pack(fill="x")
            app._entrada(esq, self.v[chave]).pack(fill="x", pady=(0, 6))
        self.b_usar = app._botao(esq, t("web_vales_criar"), self._usar, True, icone="gerar", height=42)
        self.b_usar.pack(fill="x", pady=(6, 0))
        self.l_erro = self.etiqueta(esq, "", wraplength=330)
        self.l_erro.configure(text_color=C["erro"])
        self.l_erro.pack(fill="x", pady=(6, 0))
        self.previa = ctk.CTkLabel(self, text="…", fg_color=C["visor"], corner_radius=12, text_color=C["suave"])
        self.previa.grid(row=0, column=1, sticky="nsew", padx=14, pady=12)
        for v in self.v.values():
            v.trace_add("write", lambda *_: self._agendar())
        self._agendar(0)

    @staticmethod
    def singular_de(plural: str) -> str:
        p = plural.strip()
        return p[:-1] if len(p) > 2 and p.lower().endswith("s") else p

    def vale(self) -> vales.Vale:
        """O vale com o que está nas caixas (a quantidade que não é um número fica 0: o `core` recusa-a com a mensagem certa)."""
        try:
            q = int(self.v["quantidade"].get().strip())
        except ValueError:
            q = 0
        return vales.Vale(self.desenho, self.v["titulo"].get(), self.v["organizacao"].get() or self.organizacao,
                          self.v["singular"].get() or self.singular_de(self.moeda_plural), self.moeda_plural, q, self.v["nota"].get())

    def _agendar(self, atraso: int = 350) -> None:
        if self._espera:
            self.after_cancel(self._espera)
        self._espera = self.after(atraso, self._desenhar)

    def _desenhar(self) -> None:
        self._espera = None
        self.token += 1
        token, v, lingua = self.token, self.vale(), i18n.atual()
        gc.collect()                                     # ver App._analisar: o lixo do Tk apanha-se no fio principal

        def trabalho() -> None:
            if token != self.token:
                return
            try:
                with i18n.com_lingua(lingua):
                    png = core.png_de_pagina(vales.criar_template(v), 110)
                self.app.fila.put(("vales", token, png, None))
            except Exception as e:                       # noqa: BLE001 - quantidade fora dos limites, letras que faltam, etc.
                self.app.fila.put(("vales", token, None, e))
        self.app.pool.submit(trabalho)

    def resultado(self, token: int, png: bytes | None, erro: Exception | None) -> None:
        if token != self.token or not self.winfo_exists():
            return
        self.l_erro.configure(text="" if erro is None else (str(erro) if isinstance(erro, core.ErroRifas) else t("erro_inesperado", erro=erro)))
        if png is None:
            return
        import io
        im = Image.open(io.BytesIO(png))
        self.update_idletasks()
        im.thumbnail((max(self.previa.winfo_width() - 20, 200), max(self.previa.winfo_height() - 20, 200)), Image.LANCZOS)
        self._foto = ctk.CTkImage(light_image=im, dark_image=im, size=im.size)
        self.previa.configure(image=self._foto, text="")

    def _usar(self) -> None:
        try:
            with i18n.com_lingua(i18n.atual()):
                v = self.vale()
                modelo = vales.criar_template(v)
                digitos = vales.criar_algarismos()
        except core.ErroRifas as e:
            self.l_erro.configure(text=str(e))
            return
        self.app.usar_galeria(f"vales-{v.desenho}", modelo, digitos)
        self.destroy()

    def destroy(self) -> None:
        if self._espera:
            self.after_cancel(self._espera)
            self._espera = None
        self.token += 1
        super().destroy()
