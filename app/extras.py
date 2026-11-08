"""Janelas das funcionalidades acrescentadas depois da v2.3: séries/cor/logótipo/marcas de corte, galeria de templates e sorteio.

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
from core import galeria, i18n, marca, sorteio
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
        self.v = {k: tk.StringVar() for k in ("titulo", "organizacao", "p1", "p2", "p3", "data")}
        self.v_desenho = tk.StringVar(value=galeria.DESENHOS[0].id)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        esq = ctk.CTkFrame(self, fg_color="transparent", width=360)
        esq.grid(row=0, column=0, sticky="ns", padx=(14, 0), pady=12)
        self.etiqueta(esq, t("web_galeria"), wraplength=330).pack(fill="x", pady=(0, 6))
        self.seg = ctk.CTkSegmentedButton(
            esq, values=[d.nome for d in galeria.DESENHOS], corner_radius=8, height=34, selected_color=C["acento_suave"],
            selected_hover_color=C["acento_suave"], unselected_color=C["campo"], unselected_hover_color=C["borda"],
            text_color=C["texto"], fg_color=C["campo"], command=self._desenho)
        self.seg.set(galeria.DESENHOS[0].nome)
        self.seg.pack(fill="x", pady=(0, 8))
        for chave, rotulo, maximo in (("titulo", t("web_galeria_titulo"), galeria.MAX_TITULO),
                                      ("organizacao", t("web_galeria_organizacao"), galeria.MAX_ORGANIZACAO)):
            self.etiqueta(esq, rotulo).pack(fill="x")
            app._entrada(esq, self.v[chave]).pack(fill="x", pady=(0, 6))
        self.etiqueta(esq, t("web_galeria_premios")).pack(fill="x")
        for chave in ("p1", "p2", "p3"):
            app._entrada(esq, self.v[chave]).pack(fill="x", pady=(0, 4))
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

    def _desenho(self, nome: str) -> None:
        self.v_desenho.set(next(d.id for d in galeria.DESENHOS if d.nome == nome))
        self._agendar(0)

    def _textos(self) -> core.galeria.Textos:
        v = {k: x.get().strip() for k, x in self.v.items()}
        return galeria.Textos(v["titulo"][:galeria.MAX_TITULO], v["organizacao"][:galeria.MAX_ORGANIZACAO],
                              tuple(v[k][:galeria.MAX_PREMIO] for k in ("p1", "p2", "p3") if v[k]), v["data"][:galeria.MAX_DATA])

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
