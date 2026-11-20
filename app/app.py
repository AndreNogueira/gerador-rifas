"""Gerador de Rifas - interface (Windows).

Escolhe o template em PDF, o ficheiro com os algarismos 0-9, os numeros, a pasta de destino e o nome dos
ficheiros; gera os PDFs das rifas. A logica esta em core.py; os textos em idiomas/ (18 linguas).
Visor em visor.py, componentes leves em widgets.py, cores do Windows em tema.py, icones em icones.py e
tutorial em ajuda.py.
Teste automatico sem janela: GeradorRifas.exe --selftest <pasta>
"""
from __future__ import annotations

import gc
import io
import os
import shutil
import tempfile
import queue
import sys
import threading
import time
import tkinter as tk
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

import ambiente          # poe ..\src no sys.path (tem de vir antes de ajuda/core)
import ajuda
import core
import extras
import icones
import tema
from core import i18n
from core.i18n import t
from tema import C, FONTE, cor_tk
from visor import Visor
from widgets import Banda, BarraMenus, Dica, Rolavel, novo_menu, repintar_so_o_necessario

VERSAO = "2.7.0"
BASE = Path(__file__).resolve().parent            # tambem certo no .exe compilado (recursos ao lado)
DADOS = core.config.pasta_de_dados(ambiente.dados_por_defeito())     # RIFAS_DADOS, ou %APPDATA%\GeradorRifas
CONFIG = DADOS / core.config.NOME_CONFIG
NOMES_LINGUAS = list(i18n.LINGUAS.values())
CODIGO_DE_NOME = {v: k for k, v in i18n.LINGUAS.items()}
MODOS_TEMA = ("system", "light", "dark")


def ler_config() -> dict:
    return core.config.ler_config(CONFIG)


def gravar_config(d: dict) -> None:
    core.config.gravar_config(CONFIG, d)


def abrir_pasta(p: Path) -> None:
    ambiente.abrir(p)       # os.startfile (Windows) vive em ambiente.py


def verificar_traducoes() -> list:
    """Todas as linguas tem de ter as mesmas chaves e os mesmos {parametros} que o portugues."""
    return i18n.verificar_traducoes()


def verificar_ajuda() -> list:
    """As imagens do tutorial existem para todas as linguas."""
    return core.tutorial.verificar_ajuda(ajuda.PASTA, BASE / "assets" / "video", i18n.LINGUAS, ("windows",))      # os videos do site (web_*) nao vao no .exe


def selftest(destino: Path) -> int:
    """Corre sem mostrar a janela e escreve o resultado em <destino>/selftest.txt."""
    destino.mkdir(parents=True, exist_ok=True)
    linhas, codigo = [], 0
    try:
        probs = verificar_traducoes()
        linhas.append(f"traducoes ({len(i18n.LINGUAS)} linguas): {'ok' if not probs else probs}")
        codigo |= bool(probs)
        probs = verificar_ajuda()
        linhas.append(f"imagens do tutorial: {'ok' if not probs else probs}")
        codigo |= bool(probs)
        app = App(usar_config=False)       # uma janela; as linguas trocam-se pela rotina real de reconstrucao
        app.withdraw()
        for lg in i18n.LINGUAS:
            app._mudar_lingua(i18n.LINGUAS[lg])
            app.update()
            assert app.title() == i18n.t("app_nome"), lg
            tut = ajuda.Tutorial(app, 0)       # abre o tutorial e percorre todos os topicos
            tut.update()
            for i in range(len(tut.topicos)):
                tut.mostrar(i)
                tut.update()
            tut.destroy()
        app._mudar_lingua(i18n.LINGUAS["pt"])
        for classe in (extras.Opcoes, extras.Galeria, extras.Precario, extras.EditorTemplates, extras.Sorteio):       # as janelas «Extras» abrem
            j = classe(app)
            j.update()
            j.destroy()
        app.destroy()
        linhas.append(f"janela e tutorial construidos e reconstruidos em {len(i18n.LINGUAS)} linguas: ok")
        for extra, cod in (core.autoteste.gerar_exemplos(BASE / "exemplos", destino), core.autoteste.gerar_galeria(destino)):
            linhas.extend(extra)
            codigo |= cod
    except Exception:
        linhas.append("EXCECAO:\n" + traceback.format_exc())
        codigo = 1
    linhas.append("RESULTADO: " + ("OK" if codigo == 0 else "FALHOU"))
    (destino / "selftest.txt").write_text("\n".join(linhas), encoding="utf-8")
    return int(codigo)


# ------------------------------------------------------------------ interface
class App(ctk.CTk):
    def __init__(self, usar_config: bool = True) -> None:
        super().__init__()
        self.usar_config = usar_config
        self.cfg = ler_config() if usar_config else {}
        modo = self.cfg.get("tema") if usar_config else "light"
        self.modo_tema = modo if modo in MODOS_TEMA else "system"
        self.visual = core.config.preferencias(self.cfg).get("visual", "auto") if usar_config else "auto"
        tema.definir_visual(self.visual)
        self._assin = tema.assinatura()
        tema.atualizar()
        tema.aplicar_modo(self.modo_tema)
        self.configure(fg_color=C["fundo"])
        self.geometry(f"1240x{min(900, max(self.winfo_screenheight() - 90, 640))}")
        self.minsize(1000, 640)
        ico = BASE / "assets" / "icon.ico"
        if ico.exists():
            self.after(250, lambda: self._icone(ico))

        if usar_config:
            i18n.definir(self.cfg.get("lingua") or i18n.detetar(ambiente.codigo_de_lingua_do_windows()))
        self.fila: queue.Queue = queue.Queue()
        # o PDFium nao e thread-safe: TODAS as chamadas ao motor passam por este unico worker
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.prep: core.Preparado | None = None
        self.info: core.InfoTemplate | None = None
        self._info_template_anterior = None
        self.token = 0
        self.a_gerar = False
        self._a_fechar = False
        self.cancelar = threading.Event()
        self.ultima_pasta: Path | None = None
        self.b_escolher: list = []
        self.log_linhas: list = []
        self.prog = 0.0
        self.mostrar_pasta = False
        self._estado_visor = None
        self._largura_esq = 560
        self.tut: ajuda.Tutorial | None = None
        self.w_ajuda: dict = {}
        self._sub_tema = None
        self._sub_visual = None
        self._arrasto = (0, 0)
        self._nova_larg = None
        # estados dinamicos (re-desenhados ao mudar de lingua)
        self.st_tpl: tuple = ("vazio",)
        self.st_alg: tuple = ("vazio",)
        self.st_estado: tuple | None = None
        self.st_titulo: tuple = ("previa_titulo", {})
        self.disp: core.Disposicao | None = None       # so com 1 rifa no template: como as copias enchem a folha
        self.st_folha: tuple | None = None
        # variaveis (persistem quando a interface e reconstruida). O template e o nome dos ficheiros NAO sao
        # pre-escritos nem guardados entre sessoes.
        self.v_template, self.v_alg = ctk.StringVar(), ctk.StringVar()
        self.v_saida, self.v_nome = ctk.StringVar(), ctk.StringVar()
        self.v_inicio, self.v_fim = ctk.StringVar(value="1"), ctk.StringVar(value="1000")
        self.v_digitos, self.v_max = ctk.StringVar(value="4"), ctk.StringVar(value="300")
        self.v_papel, self.v_margem = ctk.StringVar(value="A4"), ctk.StringVar(value=str(core.MARGEM_MM))
        self.v_porfolha = ctk.StringVar(value="")          # vazio = o maximo que couber
        # opcoes das janelas «Extras» (so da sessao; ver extras.py): series, cor, logotipo e marcas de corte
        self.v_prefixos, self.v_saltar = ctk.StringVar(), ctk.StringVar()
        self.v_cor_serie, self.v_marcas = tk.BooleanVar(value=False), tk.BooleanVar(value=False)
        self.v_cor_numeros, self.v_logo = ctk.StringVar(), ctk.StringVar()
        self.v_logo_pos, self.v_logo_tam = ctk.StringVar(value="sd"), ctk.StringVar(value=str(core.marca.TAMANHO_PADRAO))
        self._pasta_galeria: Path | None = None            # onde estao o template e os algarismos da galeria (temporaria)
        self.w_extras: dict = {}
        self.v_tema = tk.StringVar(value=self.modo_tema)
        self.v_visual = tk.StringVar(value=self.visual)
        self.v_lingua = tk.StringVar(value=i18n.atual())
        self.modo = "varios"       # "varios" | "unico"

        self._carregar_config()
        self._ligar_atalhos()
        self._construir()
        self._render_tudo()
        self.update_idletasks()
        repintar_so_o_necessario(self)     # redimensionar a janela fica ~7x mais rapido
        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self.after(100, self._ler_fila)
        self.after(2000, self._vigiar_windows)

    def _icone(self, ico: Path) -> None:
        try:
            self.iconbitmap(str(ico))
        except Exception:
            pass

    def destroy(self) -> None:
        self._a_fechar = True          # pára os ciclos "after" e evita callbacks pendentes
        self._apagar_pasta_galeria()
        try:
            self.pool.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        super().destroy()

    # -- atalhos de teclado (ligados uma unica vez; usam sempre os widgets atuais)
    def _ligar_atalhos(self) -> None:
        def livre(fn):
            return lambda e=None: None if self.a_gerar else fn()

        def pronto(fn):
            return lambda e=None: fn() if (self.prep is not None and not self.a_gerar) else None
        self.bind("<Control-o>", livre(self._escolher_template))
        self.bind("<Control-l>", livre(self._escolher_saida))
        self.bind("<Control-p>", pronto(self._previa))
        self.bind("<Control-g>", lambda e=None: self._gerar() if (self.prep is not None or self.a_gerar) else None)
        self.bind("<F5>", lambda e=None: self._gerar() if (self.prep is not None or self.a_gerar) else None)
        self.bind("<F1>", lambda e=None: self._tutorial())
        self.bind("<F11>", lambda e=None: self.visor._expandir())
        for tecla in ("<Control-plus>", "<Control-equal>", "<Control-KP_Add>"):
            self.bind(tecla, lambda e=None: self.visor.zoom_por(1.25))
        for tecla in ("<Control-minus>", "<Control-KP_Subtract>"):
            self.bind(tecla, lambda e=None: self.visor.zoom_por(1 / 1.25))
        self.bind("<Control-Key-0>", lambda e=None: self.visor.ajustar())
        self.bind_all("<MouseWheel>", self._roda)

    def _roda(self, e) -> None:
        try:
            self.rolavel.roda(e)
        except (tk.TclError, AttributeError):
            pass

    # -- construcao
    def _cartao(self, pai, passo: int, titulo: str) -> ctk.CTkFrame:
        c = ctk.CTkFrame(pai, corner_radius=14, fg_color=C["cartao"], border_width=1, border_color=C["borda"])
        c.pack(fill="x", padx=2, pady=(0, 9))
        self.w_ajuda[f"c{passo}"] = c
        topo = ctk.CTkFrame(c, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(11, 4))
        ctk.CTkLabel(topo, text=str(passo), width=30, height=30, corner_radius=15, fg_color=C[f"passo{passo}"],
                     text_color=C[f"sobre_passo{passo}"], font=ctk.CTkFont(FONTE, 14, "bold")).pack(side="left")
        ctk.CTkLabel(topo, text=titulo, font=ctk.CTkFont(FONTE, 15, "bold"), text_color=C["texto"]).pack(
            side="left", padx=(10, 0))
        return c

    def _entrada(self, pai, var, **kw) -> ctk.CTkEntry:
        return ctk.CTkEntry(pai, textvariable=var, corner_radius=8, height=36, fg_color=C["campo"],
                            border_color=C["borda"], text_color=C["texto"], font=ctk.CTkFont(FONTE, 13),
                            placeholder_text_color=C["suave"], **kw)

    def _botao(self, pai, texto, comando, primario=False, icone=None, **kw) -> ctk.CTkButton:
        if icone:
            cor_ic = C["sobre_acento"] if primario else C["texto"]
            kw.update(image=icones.icone(icone, 16, cor_ic), compound="left")
        if primario:
            return ctk.CTkButton(pai, text=texto, command=comando, corner_radius=8, fg_color=C["acento"],
                                 hover_color=C["acento_h"], text_color=C["sobre_acento"],
                                 font=ctk.CTkFont(FONTE, 13, "bold"), **kw)
        return ctk.CTkButton(pai, text=texto, command=comando, corner_radius=8, fg_color=C["campo"],
                             hover_color=C["borda"], text_color=C["texto"], border_width=1, border_color=C["borda"],
                             font=ctk.CTkFont(FONTE, 13), **kw)

    def _linha_ficheiro(self, pai, var, comando, placeholder=""):
        f = ctk.CTkFrame(pai, fg_color="transparent")
        f.pack(fill="x", padx=16, pady=(0, 4))
        # sem textvariable: com ele o CTkEntry nao mostra o texto indicativo quando esta vazio
        e = self._entrada(f, None, placeholder_text=placeholder)

        def sincronizar(*_):
            e.configure(state="normal")
            e.delete(0, "end")
            e.insert(0, var.get())
            e.configure(state="readonly")
        sincronizar()
        var.trace_add("write", lambda *_: e.winfo_exists() and sincronizar())
        e.pack(side="left", fill="x", expand=True)
        b = self._botao(f, t("escolher"), comando, True, icone="pasta", width=118, height=36)
        b.pack(side="left", padx=(8, 0))
        self.b_escolher.append(b)
        return f

    def _etiqueta(self, pai, **kw) -> ctk.CTkLabel:
        return ctk.CTkLabel(pai, text="", justify="left", anchor="w", wraplength=kw.pop("wraplength", 470),
                            font=ctk.CTkFont(FONTE, 12), **kw)

    def _construir(self) -> None:
        self.title(t("app_nome"))
        self.configure(fg_color=C["fundo"])
        self.b_escolher = []
        self.w_ajuda = {"janela": self}
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # a faixa da marca (gradiente violeta -> magenta, logotipo e nome)
        logo = None
        try:
            logo = Image.open(BASE / "assets" / "icon.png").convert("RGBA")
        except Exception:
            pass
        self.banda = Banda(self, t("app_nome"), VERSAO, logo, escala=self._px(1))
        self.banda.grid(row=0, column=0, sticky="ew")

        # barra superior: logotipo, menus, idioma e tema
        topo = tk.Frame(self, bg=cor_tk(C["barra"]), highlightthickness=0)
        topo.grid(row=1, column=0, sticky="ew")
        self.menus = BarraMenus(topo)
        self.menus.pack(side="left")
        self.menus.adicionar(t("m_ficheiro"), self._preencher_ficheiro)
        self.menus.adicionar(t("m_ver"), self._preencher_ver)
        self.menus.adicionar(t("win_m_extras"), self._preencher_extras)
        self.menus.adicionar(t("m_idioma"), self._preencher_idioma)
        self.menus.adicionar(t("m_ajuda"), self._preencher_ajuda)
        escuro = ctk.get_appearance_mode() == "Dark"
        self.b_tema = ctk.CTkButton(topo, text="", image=icones.icone("sol" if escuro else "lua", 18), width=36,
                                    height=30, corner_radius=6, fg_color="transparent", hover_color=C["sel_menu"],
                                    command=self._alternar_tema)
        self.b_tema.pack(side="right", padx=(2, 12))
        Dica(self.b_tema, t("tip_tema"))
        self.m_lingua = ctk.CTkOptionMenu(topo, values=NOMES_LINGUAS, width=150, height=30, corner_radius=6,
                                          command=self._mudar_lingua, fg_color=C["campo"], button_color=C["borda"],
                                          button_hover_color=C["suave"], text_color=C["texto"],
                                          dropdown_fg_color=C["cartao"], dropdown_text_color=C["texto"],
                                          dropdown_hover_color=C["sel_menu"], font=ctk.CTkFont(FONTE, 12),
                                          dropdown_font=ctk.CTkFont(FONTE, 13))
        self.m_lingua.set(i18n.LINGUAS[i18n.atual()])
        self.m_lingua.pack(side="right", padx=(0, 4))
        ctk.CTkLabel(topo, text="", image=icones.icone("globo", 18), width=24).pack(side="right")
        tk.Frame(self, height=1, bg=cor_tk(C["borda"])).grid(row=2, column=0, sticky="ew")

        # corpo: definicoes | divisoria | pre-visualizacao. A divisoria propria so desenha uma linha fina enquanto
        # se arrasta e aplica a nova largura ao largar (muito mais rapido do que redesenhar tudo a cada pixel).
        self.painel = tk.Frame(self, bg=cor_tk(C["fundo"]), highlightthickness=0)
        self.painel.grid(row=3, column=0, sticky="nsew", padx=14, pady=(12, 14))
        self.painel.grid_rowconfigure(0, weight=1)
        self.painel.grid_columnconfigure(0, weight=0, minsize=self._px(self._largura_esq))
        self.painel.grid_columnconfigure(1, weight=0, minsize=12)
        self.painel.grid_columnconfigure(2, weight=1, minsize=self._px(self.LARGURA_MIN_VISOR))
        self.rolavel = Rolavel(self.painel)
        self.rolavel.grid(row=0, column=0, sticky="nsew")
        self.esq = self.rolavel.interior
        self.divisoria = tk.Frame(self.painel, bg=cor_tk(C["fundo"]), width=12, cursor="sb_h_double_arrow",
                                  highlightthickness=0)
        self.divisoria.grid(row=0, column=1, sticky="ns")
        self._pega = tk.Frame(self.divisoria, bg=cor_tk(C["borda"]), width=3, height=44)
        self._pega.place(relx=0.5, rely=0.5, anchor="center")
        self._marca = tk.Frame(self.painel, bg=cor_tk(C["acento"]), width=3)
        for w in (self.divisoria, self._pega):
            w.bind("<ButtonPress-1>", self._div_carregar)
            w.bind("<B1-Motion>", self._div_mover)
            w.bind("<ButtonRelease-1>", self._div_largar)
            w.bind("<Enter>", lambda e=None: self._pega.configure(bg=cor_tk(C["acento"])))
            w.bind("<Leave>", lambda e=None: self._pega.configure(bg=cor_tk(C["borda"])))
        self.painel.bind("<Configure>", self._div_limitar)
        self.visor = Visor(self.painel, self._ao_expandir)
        self.visor.grid(row=0, column=2, sticky="nsew")
        self.w_ajuda["visor"] = self.visor
        esq = self.esq

        # 1. template
        c = self._cartao(esq, 1, t("c1_titulo"))
        self._linha_ficheiro(c, self.v_template, self._escolher_template, t("c1_placeholder"))
        self.l_template = self._etiqueta(c)
        self.l_template.pack(fill="x", padx=16, pady=(2, 11))
        self._construir_folha(c)

        # 2. algarismos
        c = self._cartao(esq, 2, t("c2_titulo"))
        f = self._linha_ficheiro(c, self.v_alg, self._escolher_alg, t("c2_placeholder"))
        b = self._botao(f, "", self._limpar_alg, icone="fechar", width=36, height=36)
        b.pack(side="left", padx=(6, 0))
        self.b_escolher.append(b)
        self.l_alg = self._etiqueta(c)
        self.l_alg.pack(fill="x", padx=16, pady=(2, 0))
        ctk.CTkButton(c, text=t("c2_ajuda"), fg_color="transparent", text_color=C["link"], hover=False, anchor="w",
                      width=10, font=ctk.CTkFont(FONTE, 12, underline=True), command=lambda: self._tutorial(ajuda.TOPICO_ALGARISMOS)).pack(
            anchor="w", padx=12, pady=(0, 7))

        # 3. numeros
        c = self._cartao(esq, 3, t("c3_titulo"))
        g = ctk.CTkFrame(c, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=(0, 8))
        self.e_numeros = []                  # De, Ate, Algarismos (o video do tutorial aponta para eles)
        for i, (txt, var, larg) in enumerate(((t("de"), self.v_inicio, 110), (t("ate"), self.v_fim, 110),
                                              (t("algarismos"), self.v_digitos, 80))):
            ctk.CTkLabel(g, text=txt, text_color=C["suave"], font=ctk.CTkFont(FONTE, 12)).grid(
                row=0, column=i, sticky="w", padx=(0 if i == 0 else 12, 0))
            e = self._entrada(g, var, width=larg)
            e.grid(row=1, column=i, sticky="w", padx=(0 if i == 0 else 12, 0))
            self.e_numeros.append(e)
        etiquetas = [t("modo_varios"), t("modo_unico")]
        self.seg_modo = ctk.CTkSegmentedButton(
            c, values=etiquetas, corner_radius=8, height=34, selected_color=C["acento_suave"],
            selected_hover_color=C["acento_suave"], unselected_color=C["campo"], unselected_hover_color=C["borda"],
            text_color=C["texto"], font=ctk.CTkFont(FONTE, 13), fg_color=C["campo"],
            command=lambda v: self._set_modo("varios" if v == etiquetas[0] else "unico"))
        self.seg_modo.set(etiquetas[0] if self.modo == "varios" else etiquetas[1])
        self.seg_modo.pack(fill="x", padx=16, pady=(4, 8))
        f_max = ctk.CTkFrame(c, fg_color="transparent")
        f_max.pack(fill="x", padx=16)
        ctk.CTkLabel(f_max, text=t("max_ficheiro"), text_color=C["texto"], font=ctk.CTkFont(FONTE, 13)).pack(side="left")
        self.e_max = self._entrada(f_max, self.v_max, width=90)
        self.e_max.pack(side="left", padx=10)
        self.l_resumo = self._etiqueta(c)
        self.l_resumo.pack(fill="x", padx=16, pady=(5, 11))
        for v in (self.v_inicio, self.v_fim, self.v_digitos, self.v_max, self.v_prefixos, self.v_saltar):
            v.trace_add("write", lambda *_: self._resumo())

        # 4. destino
        c = self._cartao(esq, 4, t("c4_titulo"))
        self._linha_ficheiro(c, self.v_saida, self._escolher_saida, t("c4_placeholder"))
        n = ctk.CTkFrame(c, fg_color="transparent")
        n.pack(fill="x", padx=16, pady=(4, 13))
        ctk.CTkLabel(n, text=t("nome_ficheiros"), text_color=C["texto"], font=ctk.CTkFont(FONTE, 13)).pack(side="left")
        self.e_nome = self._entrada(n, None, placeholder_text=t("nome_placeholder"))
        self.e_nome.pack(side="left", fill="x", expand=True, padx=(10, 0))
        if self.v_nome.get():
            self.e_nome.insert(0, self.v_nome.get())

        def ao_escrever(_=None):
            self.v_nome.set(self.e_nome.get())
            self.e_nome.configure(border_color=C["borda"])
        self.e_nome.bind("<KeyRelease>", ao_escrever)

        # acoes (botoes, progresso, estado e registo)
        self.f_acoes = ctk.CTkFrame(esq, fg_color="transparent")
        self.f_acoes.pack(fill="x")
        self.w_ajuda["acoes"] = self.f_acoes
        a = ctk.CTkFrame(self.f_acoes, fg_color="transparent")
        a.pack(fill="x", padx=2, pady=(0, 6))
        self.b_previa = self._botao(a, t("previa"), self._previa, False, icone="olho", width=160, height=46)
        self.b_previa.pack(side="left")
        self.b_gerar = ctk.CTkButton(a, text=t("gerar"), height=46, corner_radius=8, command=self._gerar,
                                     fg_color=C["acento2"], hover_color=C["acento2_h"], text_color=C["sobre_acento2"],
                                     font=ctk.CTkFont(FONTE, 16, "bold"), compound="left",
                                     image=icones.icone("gerar", 18, C["sobre_acento2"]))
        self.b_gerar.pack(side="left", fill="x", expand=True, padx=(10, 0))

        self.barra = ctk.CTkProgressBar(self.f_acoes, height=8, corner_radius=4, progress_color=C["acento2"],
                                        fg_color=C["borda"])
        self.barra.set(self.prog)
        self.barra.pack(fill="x", padx=4, pady=(6, 4))
        self.l_estado = ctk.CTkLabel(self.f_acoes, text="", anchor="w", font=ctk.CTkFont(FONTE, 13),
                                     text_color=C["suave"])
        self.l_estado.pack(fill="x", padx=4)
        # no fim da geracao: abrir a pasta e limpar tudo para recomecar
        self.f_pos = ctk.CTkFrame(self.f_acoes, fg_color="transparent")
        self.b_pasta = self._botao(self.f_pos, t("abrir_pasta"),
                                   lambda: self.ultima_pasta and abrir_pasta(self.ultima_pasta), True,
                                   icone="pasta", height=38)
        self.b_pasta.pack(side="left", fill="x", expand=True)
        self.b_limpar = self._botao(self.f_pos, t("limpar"), self._limpar_tudo, False, icone="fechar", height=38,
                                    width=150)
        self.b_limpar.pack(side="left", padx=(8, 0))
        self.log = ctk.CTkTextbox(self.f_acoes, height=92, corner_radius=8, fg_color=C["cartao"],
                                  text_color=C["suave"], border_width=1, border_color=C["borda"],
                                  font=ctk.CTkFont("Consolas", 11), wrap="word",
                                  scrollbar_button_color=C["borda"], scrollbar_button_hover_color=C["suave"])
        self.log.pack(fill="x", padx=2, pady=(8, 0))
        self.log.insert("1.0", "".join(m + "\n" for m in self.log_linhas))
        self.log.see("end")
        self.log.configure(state="disabled")

        if self._estado_visor is not None:
            self.visor.restaurar(self._estado_visor)
            if self.visor.expandido:
                self._ao_expandir(True)

    # -- folha: com 1 rifa no template o programa enche a folha com copias
    def _construir_folha(self, cartao) -> None:
        f = ctk.CTkFrame(cartao, fg_color="transparent")
        self.f_folha = f                     # so aparece quando o template tem uma unica rifa
        ctk.CTkLabel(f, text=t("lay_info"), justify="left", anchor="w", wraplength=470, text_color=C["suave"],
                     font=ctk.CTkFont(FONTE, 12)).pack(fill="x", pady=(0, 6))
        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x")
        rot = ((t("lay_papel"), None), (t("lay_margem"), self.v_margem), (t("lay_por_folha"), self.v_porfolha))
        for i, (txt, var) in enumerate(rot):
            ctk.CTkLabel(g, text=txt, text_color=C["suave"], font=ctk.CTkFont(FONTE, 12)).grid(
                row=0, column=i, sticky="w", padx=(0 if i == 0 else 12, 0))
            if var is None:
                self.m_papel = ctk.CTkOptionMenu(
                    g, values=list(core.PAPEIS), width=100, height=36, corner_radius=8, fg_color=C["campo"],
                    button_color=C["borda"], button_hover_color=C["suave"], text_color=C["texto"],
                    dropdown_fg_color=C["cartao"], dropdown_text_color=C["texto"], dropdown_hover_color=C["sel_menu"],
                    font=ctk.CTkFont(FONTE, 13), dropdown_font=ctk.CTkFont(FONTE, 13),
                    command=lambda v: (self.v_papel.set(v), self._recalcular_folha()))
                self.m_papel.set(self.v_papel.get())
                self.m_papel.grid(row=1, column=i, sticky="w")
            else:
                self._entrada(g, var, width=96 if i == 2 else 84).grid(
                    row=1, column=i, sticky="w", padx=(12, 0))
        self.l_folha = self._etiqueta(f)
        self.l_folha.pack(fill="x", pady=(6, 0))
        for v in (self.v_margem, self.v_porfolha, self.v_marcas):
            v.trace_add("write", lambda *_: self._recalcular_folha())
        self.b_escolher_folha = [self.m_papel]

    def _recalcular_folha(self) -> None:
        """(Re)calcula como a rifa enche a folha com o papel, a margem e o numero por folha escolhidos."""
        info = self.info
        if not (hasattr(self, "f_folha") and self.f_folha.winfo_exists()):
            return
        if not core.escolha_folha.tem_folha(info):
            self.disp, self.st_folha = None, None
            self.f_folha.pack_forget()
            self._resumo()
            return
        if not self.f_folha.winfo_ismapped():
            self.f_folha.pack(fill="x", padx=16, pady=(0, 11), after=self.l_template)
        try:
            esc = core.escolha_folha.escolher_folha(info, self.v_papel.get(), self.v_margem.get(), self.v_porfolha.get(), self.v_marcas.get())
            self.disp = esc.disp
            self.st_folha = ("ok", self.disp, esc.acima)
        except core.ErroRifas as e:
            self.disp, self.st_folha = None, ("erro", e)
        self._render_folha()
        self._resumo()

    def _render_folha(self) -> None:
        if not (hasattr(self, "l_folha") and self.l_folha.winfo_exists()):
            return
        k = self.st_folha
        if k is None:
            return
        if k[0] == "erro":
            self.l_folha.configure(text="✖ " + self._primeira_linha(k[1]), text_color=C["erro"])
            return
        txt, aviso = core.escolha_folha.texto_da_folha(k[1], k[2])
        self.l_folha.configure(text=txt, text_color=C["aviso"] if aviso else C["suave"])

    def _prep_atual(self) -> core.Preparado | None:
        """O template preparado, com a folha escolhida quando o template tem uma so rifa. None (e aviso ao utilizador)
        se a folha nao e valida."""
        erro = self.st_folha[1] if (self.st_folha and self.st_folha[0] == "erro") else None
        try:
            return core.escolha_folha.preparado_com_folha(self.prep, self.disp, erro)
        except core.ErroRifas as e:
            messagebox.showwarning(t("app_nome"), str(e))
            return None

    # -- divisoria entre as definicoes e a pre-visualizacao
    LARGURA_MIN_ESQ, LARGURA_MIN_VISOR = 430, 300

    def _px(self, v: float) -> int:
        """Unidades logicas -> pixeis do ecra (a escala do Windows, p.ex. 150%)."""
        return int(round(v * self._get_window_scaling()))

    def _div_maximo(self) -> float:
        """Largura maxima (logica) das definicoes: o visor guarda sempre o seu minimo."""
        s = self._get_window_scaling()
        return max(self.LARGURA_MIN_ESQ, (self.painel.winfo_width() - 12) / s - self.LARGURA_MIN_VISOR)

    def _div_carregar(self, e) -> None:
        self._arrasto = (e.x_root, self._largura_esq)
        self._nova_larg = None
        self._marca.place(x=self._px(self._largura_esq) + 4, y=0, relheight=1, width=3)
        self._marca.lift()

    def _div_mover(self, e) -> None:
        x0, larg0 = self._arrasto
        nova = min(max(larg0 + (e.x_root - x0) / self._get_window_scaling(), self.LARGURA_MIN_ESQ),
                   self._div_maximo())
        self._nova_larg = nova
        self._marca.place(x=self._px(nova) + 4, y=0, relheight=1, width=3)

    def _div_largar(self, e) -> None:
        self._marca.place_forget()
        nova = self._nova_larg
        if nova is not None and abs(nova - self._largura_esq) > 0.5:
            self._largura_esq = nova
            self.painel.grid_columnconfigure(0, minsize=self._px(nova))
        self._nova_larg = None

    def _div_limitar(self, e) -> None:
        """Ao encolher a janela, a coluna das definicoes nao pode comer o espaco do visor. A largura escolhida pelo
        utilizador (`_largura_esq`) nao se perde: so a largura efetiva e limitada."""
        if self.visor.expandido or e.width < 200:         # ainda sem tamanho valido
            return
        efetiva = min(self._largura_esq, self._div_maximo())
        self.painel.grid_columnconfigure(0, minsize=self._px(efetiva))

    def _ao_expandir(self, expandir: bool) -> None:
        """Expandir: o visor ocupa toda a janela (as definicoes escondem-se). Reduzir: volta ao normal."""
        if expandir:
            self.rolavel.grid_remove()
            self.divisoria.grid_remove()
            self.painel.grid_columnconfigure(0, minsize=0)
            self.painel.grid_columnconfigure(1, minsize=0)
        else:
            self.painel.grid_columnconfigure(0, minsize=self._px(self._largura_esq))
            self.painel.grid_columnconfigure(1, minsize=12)
            self.rolavel.grid()
            self.divisoria.grid()

    # -- menus
    def _preencher_ficheiro(self, m: tk.Menu) -> None:
        livre = "disabled" if self.a_gerar else "normal"
        pronto = "normal" if (self.prep is not None and not self.a_gerar) else "disabled"
        m.add_command(label=t("mi_abrir_template"), accelerator="Ctrl+O", command=self._escolher_template, state=livre)
        m.add_command(label=t("mi_abrir_alg"), command=self._escolher_alg, state=livre)
        m.add_command(label=t("mi_destino"), accelerator="Ctrl+L", command=self._escolher_saida, state=livre)
        m.add_separator()
        m.add_command(label=t("previa"), accelerator="Ctrl+P", command=self._previa, state=pronto)
        m.add_command(label=t("cancelar") if self.a_gerar else t("gerar"), accelerator="Ctrl+G", command=self._gerar,
                      state="normal" if (self.prep is not None or self.a_gerar) else "disabled")
        m.add_command(label=t("abrir_pasta"), state="normal" if self.ultima_pasta else "disabled",
                      command=lambda: self.ultima_pasta and abrir_pasta(self.ultima_pasta))
        m.add_command(label=t("limpar"), command=self._limpar_tudo, state=livre)
        m.add_separator()
        m.add_command(label=t("mi_sair"), accelerator="Alt+F4", command=self._fechar)

    def _preencher_ver(self, m: tk.Menu) -> None:
        m.add_command(label=t("mi_zoom_mais"), accelerator="Ctrl++", command=lambda: self.visor.zoom_por(1.25))
        m.add_command(label=t("mi_zoom_menos"), accelerator="Ctrl+−", command=lambda: self.visor.zoom_por(1 / 1.25))
        m.add_command(label=t("mi_ajustar"), accelerator="Ctrl+0", command=self.visor.ajustar)
        m.add_command(label=t("mi_reduzir") if self.visor.expandido else t("mi_expandir"), accelerator="F11",
                      command=self.visor._expandir)
        m.add_separator()
        if self._sub_visual is None or not self._sub_visual.winfo_exists():
            self._sub_visual = novo_menu(m)
        self._sub_visual.delete(0, "end")
        for valor, rotulo in (("auto", t("win_visual_auto")), *core.tema.NOMES_VISUAIS.items()):
            self._sub_visual.add_radiobutton(label=rotulo, variable=self.v_visual, value=valor,
                                             command=lambda v=valor: self._definir_visual(v))
        m.add_cascade(label=t("web_visual"), menu=self._sub_visual)
        if self._sub_tema is None or not self._sub_tema.winfo_exists():
            self._sub_tema = novo_menu(m)
        sub = self._sub_tema
        sub.delete(0, "end")
        for valor, chave in (("system", "mi_tema_sistema"), ("light", "mi_tema_claro"), ("dark", "mi_tema_escuro")):
            sub.add_radiobutton(label=t(chave), variable=self.v_tema, value=valor,
                                command=lambda v=valor: self._definir_tema(v))
        m.add_cascade(label=t("mi_tema"), menu=sub)

    def _preencher_extras(self, m: tk.Menu) -> None:
        livre = "disabled" if self.a_gerar else "normal"
        m.add_command(label=t("win_opcoes"), command=lambda: self._abrir_extra("opcoes", extras.Opcoes), state=livre)
        m.add_command(label=t("win_galeria"), command=lambda: self._abrir_extra("galeria", extras.Galeria), state=livre)
        m.add_command(label=t("web_precario") + "…", command=lambda: self._abrir_extra("precario", extras.Precario), state=livre)
        m.add_command(label=t("web_editor") + "…", command=lambda: self._abrir_extra("editor", extras.EditorTemplates), state=livre)
        m.add_command(label=t("web_sorteio") + "…", command=lambda: self._abrir_extra("sorteio", extras.Sorteio))
        m.add_separator()
        m.add_command(label=t("web_exportar_csv") + "…", command=self._exportar_csv)
        m.add_command(label=t("web_folha_controlo"), command=self._exportar_folha)
        m.add_separator()
        m.add_command(label=t("win_guardar_pedido"), command=self._guardar_pedido)
        m.add_command(label=t("win_abrir_pedido"), command=self._abrir_pedido, state=livre)

    def _preencher_idioma(self, m: tk.Menu) -> None:
        self.v_lingua.set(i18n.atual())
        for codigo, nome in i18n.LINGUAS.items():
            m.add_radiobutton(label=nome, variable=self.v_lingua, value=codigo,
                              command=lambda n=nome: self._mudar_lingua(n),
                              state="disabled" if self.a_gerar else "normal")

    def _preencher_ajuda(self, m: tk.Menu) -> None:
        m.add_command(label=t("mi_tutorial"), accelerator="F1", command=lambda: self._tutorial())
        m.add_command(label=t("mi_video"), command=self._video)
        m.add_command(label=t("ajuda_titulo"), command=lambda: self._tutorial(ajuda.TOPICO_ALGARISMOS))
        m.add_separator()
        m.add_command(label=t("mi_sobre"), command=self._sobre)

    @staticmethod
    def ficheiro_video() -> Path | None:
        """O video tutorial na lingua atual (ou em ingles / portugues, se nao houver nessa lingua)."""
        return core.tutorial.ficheiro_video(BASE / "assets" / "video", i18n.atual())

    def _video(self) -> None:
        f = self.ficheiro_video()
        if f is None:
            messagebox.showinfo(t("app_nome"), t("video_falta", nome="tutorial_pt.mp4"))
        else:
            abrir_pasta(f)          # abre com o leitor de video predefinido do Windows

    def _sobre(self) -> None:
        messagebox.showinfo(t("mi_sobre").rstrip("…"), t("sobre_texto", app=t("app_nome"), versao=VERSAO))

    def _tutorial(self, topico: int | None = None) -> None:
        if self.tut is not None and self.tut.winfo_exists():
            self.tut.deiconify()
            self.tut.lift()
            self.tut.focus_force()
            if topico is not None:
                self.tut.mostrar(topico)
            return
        self.tut = ajuda.Tutorial(self, topico if topico is not None else 0)

    # -- re-desenho dos textos dinamicos
    def _render_tudo(self) -> None:
        self._render_tpl()
        self._render_alg()
        self._render_estado()
        self._render_titulo()
        self.visor.textos(t(self.st_titulo[0], **self.st_titulo[1]), t("zoom_ajustar"), t("previa_vazio"),
                          (t("mi_zoom_menos"), t("mi_zoom_mais"), t("mi_ajustar"), t("mi_expandir"), t("mi_reduzir")))
        self._recalcular_folha()
        self._set_modo(self.modo)
        if self.mostrar_pasta:
            self.f_pos.pack(fill="x", padx=2, pady=(8, 0), before=self.log)
        self._estado_botoes()

    @staticmethod
    def _primeira_linha(e: Exception) -> str:
        return str(e).split("\n")[0]

    def _render_tpl(self) -> None:
        k = self.st_tpl
        if k[0] == "vazio":
            self.l_template.configure(text=t("c1_vazio"), text_color=C["suave"])
        elif k[0] == "analisar":
            self.l_template.configure(text=t("c1_analisar"), text_color=C["suave"])
        elif k[0] == "ok":
            i: core.InfoTemplate = k[1]
            ok = (t("c1_ok_uma", primeiro=i.primeiro) if i.n_campos == 1
                  else t("c1_ok", n=i.n_campos, primeiro=i.primeiro, ultimo=i.ultimo))
            self.l_template.configure(text=ok + " · " + ", ".join(i.fontes), text_color=C["ok"])
        else:   # erro
            self.l_template.configure(text="✖ " + self._primeira_linha(k[1]), text_color=C["erro"])

    def _render_alg(self) -> None:
        k = self.st_alg
        if k[0] == "vazio":
            self.l_alg.configure(text="—", text_color=C["suave"])
        elif k[0] == "precisa":
            self.l_alg.configure(text=t("c2_precisa"), text_color=C["erro"])
        elif k[0] == "analisar":
            self.l_alg.configure(text=t("c2_analisar"), text_color=C["suave"])
        elif k[0] == "ok":
            self.l_alg.configure(text="✔ " + "; ".join(k[1].descricoes), text_color=C["ok"])
        else:   # erro no ficheiro escolhido
            self.l_alg.configure(text="✖ " + str(k[1]), text_color=C["erro"])

    def _render_estado(self) -> None:
        if self.st_estado is None:
            self.l_estado.configure(text="")
        else:
            chave, params, cor = self.st_estado
            self.l_estado.configure(text=t(chave, **params), text_color=cor)

    def _set_estado(self, chave: str | None, cor=None, **params) -> None:
        self.st_estado = None if chave is None else (chave, params, cor or C["suave"])
        self._render_estado()

    def _render_titulo(self) -> None:
        self.visor.definir_titulo(t(self.st_titulo[0], **self.st_titulo[1]))

    # -- reconstrucao da janela (lingua, tema, cor de destaque do Windows)
    def _reconstruir(self) -> None:
        topico = self.tut.indice if (self.tut is not None and self.tut.winfo_exists()) else None
        self._estado_visor = self.visor.estado()
        for w in self.winfo_children():
            w.destroy()
        self.tut = None
        self._sub_tema = None
        self._sub_visual = None
        self._construir()
        self._render_tudo()
        # Os widgets destruidos deixam lixo ciclico do Tk. Se fosse o fio de trabalho a apanha-lo (o pypdf aloca
        # muito), cada finalizador do Tk esperaria pelo fio principal e a geracao ficava ~100x mais lenta.
        self.update_idletasks()
        gc.collect()
        if topico is not None:
            self._tutorial(topico)

    def _mudar_lingua(self, nome: str) -> None:
        if self.a_gerar:
            self.m_lingua.set(i18n.LINGUAS[i18n.atual()])
            return
        i18n.definir(CODIGO_DE_NOME[nome])
        self.v_lingua.set(i18n.atual())
        self._reconstruir()
        self._guardar_config()

    def _alternar_tema(self) -> None:
        self._definir_tema("light" if ctk.get_appearance_mode() == "Dark" else "dark")

    def _definir_tema(self, modo: str) -> None:
        self.modo_tema = modo
        self.v_tema.set(modo)
        tema.aplicar_modo(modo)
        self._reconstruir()
        self._guardar_config()

    def _definir_visual(self, valor: str) -> None:
        """«auto» (por época) ou um dos 14 visuais de `core.tema.VISUAIS`: refaz as cores e a janela."""
        if self.a_gerar:
            self.v_visual.set(self.visual)
            return
        self.visual = valor
        tema.definir_visual(valor)
        self._assin = tema.assinatura()
        tema.atualizar()
        self._reconstruir()
        self._guardar_config()

    def _vigiar_windows(self) -> None:
        """Acompanha o Windows: cor de destaque e (no modo 'Igual ao Windows') claro/escuro."""
        if self._a_fechar:
            return
        try:
            assin, escuro = tema.assinatura(), tema.windows_escuro()
            acento_mudou = assin != self._assin
            modo_mudou = self.modo_tema == "system" and escuro != (ctk.get_appearance_mode() == "Dark")
            if (acento_mudou or modo_mudou) and not self.a_gerar:
                self._assin = assin
                tema.atualizar()
                tema.aplicar_modo(self.modo_tema)
                self._reconstruir()
        except Exception:
            pass
        self.after(2000, self._vigiar_windows)

    # -- config (o template e o nome dos ficheiros nunca sao guardados)
    def _carregar_config(self) -> None:
        pref = core.config.preferencias(self.cfg)
        for chave, var in (("algarismos", self.v_alg), ("saida", self.v_saida), ("inicio", self.v_inicio),
                           ("fim", self.v_fim), ("digitos", self.v_digitos), ("max", self.v_max),
                           ("margem", self.v_margem)):
            if chave in pref:
                var.set(pref[chave])
        if "papel" in pref:
            self.v_papel.set(pref["papel"])
        if "modo" in pref:
            self.modo = pref["modo"]

    def _guardar_config(self) -> None:
        if not self.usar_config:
            return
        gravar_config(core.config.para_gravar(
            lingua=i18n.atual(), tema=self.modo_tema, algarismos=self.v_alg.get(), saida=self.v_saida.get(),
            inicio=self.v_inicio.get(), fim=self.v_fim.get(), digitos=self.v_digitos.get(), max_ficheiro=self.v_max.get(),
            modo=self.modo, papel=self.v_papel.get(), margem=self.v_margem.get(),
            visual=self.visual if self.visual != "auto" else ""))

    def _fechar(self) -> None:
        if self.a_gerar and not messagebox.askyesno(t("app_nome"), t("sair_a_gerar")):
            return
        self.cancelar.set()
        self._guardar_config()
        self.destroy()

    # -- escolhas
    @staticmethod
    def _dir_de(var) -> str | None:
        v = var.get()
        if v:
            p = Path(v)
            return str(p if p.is_dir() else p.parent)
        return None

    def _escolher_template(self) -> None:
        p = filedialog.askopenfilename(title=t("dlg_template"), filetypes=[(t("dlg_tipo_pdf"), "*.pdf")],
                                       initialdir=self._dir_de(self.v_template))
        if p:
            self.v_template.set(p)
            self._analisar()

    def _escolher_alg(self) -> None:
        p = filedialog.askopenfilename(
            title=t("dlg_algarismos"), initialdir=self._dir_de(self.v_alg),
            filetypes=[(t("dlg_tipo_alg"), "*.pdf *.png *.jpg *.jpeg"), (t("dlg_tipo_todos"), "*.*")])
        if p:
            self.v_alg.set(p)
            self._analisar()

    def _limpar_alg(self) -> None:
        self.v_alg.set("")
        if self.v_template.get():
            self._analisar()

    def _escolher_saida(self) -> None:
        p = filedialog.askdirectory(title=t("dlg_destino"), initialdir=self._dir_de(self.v_saida), mustexist=False)
        if p:
            self.v_saida.set(str(Path(p)))

    def _set_modo(self, modo: str) -> None:
        self.modo = modo
        self.e_max.configure(state="normal" if modo == "varios" else "disabled")
        self._resumo()

    # -- resumo
    def _trabalho(self, com_logotipo: bool = False) -> core.Trabalho:
        """O pedido dos campos. O logotipo (um ficheiro a ler e validar) so entra quando se pede: o resumo, que corre a cada tecla, nao o le."""
        tr = core.pedido.trabalho_de_campos(
            self.v_saida.get(), self.v_nome.get(), self.v_inicio.get(), self.v_fim.get(), self.v_max.get(),
            self.v_digitos.get(), self.modo, self.v_prefixos.get(), self.v_saltar.get(), self.v_cor_serie.get(), self.v_cor_numeros.get())
        if com_logotipo and self.v_logo.get():
            tam = self.v_logo_tam.get().strip()
            tr.marca = core.marca.ler_ficheiro(self.v_logo.get(), self.v_logo_pos.get(),
                                               int(tam) if tam.isdigit() else core.marca.TAMANHO_PADRAO)
        return tr

    def _resumo(self) -> None:
        try:
            tr = self._trabalho()
            n = core.pedido.rifas_por_pagina(self.disp, self.info)
            txt, aviso = core.pedido.resumo_do_pedido(tr, n, tem_template=self.info is not None)
            self.l_resumo.configure(text=txt, text_color=C["aviso"] if aviso else C["suave"])
        except core.ErroRifas as e:
            self.l_resumo.configure(text=str(e), text_color=C["aviso"])

    # -- analise do template + algarismos (worker)
    def _analisar(self) -> None:
        tpl = self.v_template.get()
        if not tpl:
            return
        self.token += 1
        token = self.token
        gc.collect()          # o lixo do Tk (fontes) apanha-se aqui, no fio principal: no worker cada __del__ esperava pelo ciclo da interface
        alg = Path(self.v_alg.get()) if self.v_alg.get() else None
        self.prep = None
        self.st_tpl = ("analisar",)
        self.st_alg = ("analisar",) if alg else ("vazio",)
        self._render_tpl()
        self._render_alg()
        self._estado_botoes()

        def trabalho() -> None:
            logs: list = []
            try:
                self.fila.put(("miniatura", token, core.pagina_template(Path(tpl), 200)))
            except Exception:
                pass
            try:
                prep = core.preparar(Path(tpl), alg, logs.append)
                self.fila.put(("prep", token, prep, logs))
            except core.ErroAlgarismos as e:
                self.fila.put(("prep_alg", token, e, logs))
            except Exception as e:
                self.fila.put(("prep_erro", token, e, logs))
        self.pool.submit(trabalho)

    def _estado_botoes(self) -> None:
        pronto = self.prep is not None and not self.a_gerar
        self.b_gerar.configure(state="normal" if (pronto or self.a_gerar) else "disabled",
                               text=t("cancelar") if self.a_gerar else t("gerar"),
                               image=icones.icone("fechar" if self.a_gerar else "gerar", 18, C["sobre_acento"]))
        self.b_previa.configure(state="normal" if pronto else "disabled")
        livre = "disabled" if self.a_gerar else "normal"
        for b in self.b_escolher:
            b.configure(state=livre)
        self.m_lingua.configure(state=livre)

    # -- pre-visualizacao
    def _mostrar_pil(self, im: Image.Image, titulo: tuple, manter_zoom: bool = False) -> None:
        self.st_titulo = titulo
        self._render_titulo()
        self.visor.definir_imagem(im, manter_zoom=manter_zoom)

    def _previa(self) -> None:
        if not self.prep:
            return
        try:
            tr = self._trabalho(com_logotipo=True)
            if tr.fim < tr.inicio or not 1 <= tr.digitos <= core.MAX_DIGITOS:
                raise core.ErroRifas("conf_numeros")
            core.series.validar_extras(tr)
        except core.ErroRifas as e:
            messagebox.showwarning(t("app_nome"), str(e))
            return
        prep = self._prep_atual()
        if prep is None:
            return
        self.b_previa.configure(state="disabled")

        def trabalho() -> None:
            try:
                png = core.pedido.previa_png(prep, tr, dpi=200)
                self.fila.put(("previa", png, tr, prep.por_pagina))
            except Exception as e:
                self.fila.put(("previa_erro", e))
        self.pool.submit(trabalho)

    # -- gerar
    def _gerar(self) -> None:
        if self.a_gerar:
            self.cancelar.set()
            self._set_estado("est_a_cancelar")
            return
        if not self.prep:
            return
        try:
            tr = self._trabalho(com_logotipo=True)
            if not tr.nome:
                self.e_nome.configure(border_color=C["erro"])
                self.e_nome.focus_set()
                raise core.ErroRifas("err_nome")
            if not tr.saida.parts:
                raise core.ErroRifas("falta_pasta")
        except core.ErroRifas as e:
            messagebox.showwarning(t("app_nome"), str(e))
            return
        prep = self._prep_atual()
        if prep is None:
            return
        try:
            plano = core.planear(tr, prep.por_pagina)
        except core.ErroRifas as e:
            messagebox.showwarning(t("app_nome"), str(e))
            return
        d = prep.disp
        if d is not None and d.n > core.AVISO_POR_PAGINA and not messagebox.askyesno(
                t("app_nome"), t("conf_muitas", n=d.n, w=f"{d.celula.width / core.MM:.0f}",
                                 h=f"{d.celula.height / core.MM:.0f}")):
            return
        existentes = [p.name for p, _, _ in plano if p.exists()]
        if existentes:
            lista = "\n".join(existentes[:6]) + ("\n…" if len(existentes) > 6 else "")
            if not messagebox.askyesno(t("app_nome"), t("existem", n=len(existentes), lista=lista)):
                return
        self._guardar_config()
        gc.collect()          # lixo do Tk apanhado aqui (fio principal) e nao durante a geracao
        self.cancelar.clear()
        self.a_gerar = True
        self.ultima_pasta = tr.saida
        self.mostrar_pasta = False
        self.f_pos.pack_forget()
        self.prog = 0.0
        self.barra.set(0)
        self._set_estado("est_a_gerar")
        self._estado_botoes()

        def trabalho() -> None:
            try:
                ultimo = [0.0]

                def progresso(a: int, b: int) -> None:     # no maximo ~4 atualizacoes por segundo
                    agora = time.monotonic()
                    if a == b or agora - ultimo[0] > 0.25:
                        ultimo[0] = agora
                        self.fila.put(("prog", a, b))
                res = core.gerar(tr, prep, lambda m: self.fila.put(("log", m)), progresso, self.cancelar)
                self.fila.put(("fim", res))
            except core.Cancelado:
                self.fila.put(("cancelado",))
            except Exception as e:
                self.fila.put(("erro", e, traceback.format_exc()))
        self.pool.submit(trabalho)

    # -- janelas «Extras» (series/cor/logotipo, galeria, sorteio) e exportar a lista
    def _abrir_extra(self, nome: str, classe) -> None:
        j = self.w_extras.get(nome)
        if j is not None and j.winfo_exists():
            j.deiconify()
            j.lift()
            j.focus_force()
            return
        self.w_extras[nome] = classe(self)

    def _bilhetes_do_pedido(self):
        """(Trabalho, [(serie, numero)]) dos campos, ou None (e aviso) se o pedido nao serve. Nao precisa de template."""
        try:
            tr = self._trabalho()
            if not 1 <= tr.digitos <= core.MAX_DIGITOS or tr.inicio < 0 or tr.fim < tr.inicio:
                raise core.ErroRifas("conf_numeros")
            core.series.validar_extras(tr)
            return tr, core.series.bilhetes(tr)
        except core.ErroRifas as e:
            messagebox.showwarning(t("app_nome"), str(e))
            return None

    def _exportar(self, exportar, tipo: tuple) -> Path | None:
        """Pergunta onde guardar e escreve o ficheiro que `exportar(tr, bilhetes, lingua)` devolve. O caminho, ou None se desistiu/falhou."""
        r = self._bilhetes_do_pedido()
        if r is None:
            return None
        tr, bilhetes = r
        nome, dados = exportar(tr, bilhetes, i18n.atual())
        p = filedialog.asksaveasfilename(title=t("win_guardar"), initialdir=self._dir_de(self.v_saida), initialfile=nome,
                                         defaultextension=tipo[1][1:], filetypes=[tipo, (t("dlg_tipo_todos"), "*.*")])
        if not p:
            return None
        try:
            Path(p).write_bytes(dados)
        except OSError as e:
            messagebox.showerror(t("app_nome"), t("erro_inesperado", erro=e))
            return None
        self._set_estado("win_guardado", C["ok"], nome=Path(p).name)
        return Path(p)

    def _exportar_csv(self) -> Path | None:
        return self._exportar(core.controlo.exportar_csv, ("CSV", "*.csv"))

    def _exportar_folha(self) -> Path | None:
        return self._exportar(core.controlo.exportar_folha, (t("dlg_tipo_pdf"), "*.pdf"))

    # -- guardar e abrir o pedido (ficheiro .rifas; o site tem «Copiar ligação»): so os campos, nunca o template, os algarismos, a pasta nem o logotipo
    def _campos_do_pedido(self) -> dict:
        return {"inicio": self.v_inicio.get(), "fim": self.v_fim.get(), "digitos": self.v_digitos.get(), "max_ficheiro": self.v_max.get(), "modo": self.modo,
                "papel": self.v_papel.get(), "margem": self.v_margem.get(), "porfolha": self.v_porfolha.get(), "nome": self.v_nome.get(),
                "prefixos": self.v_prefixos.get(), "saltar": self.v_saltar.get(), "cor_serie": bool(self.v_cor_serie.get()), "marcas": bool(self.v_marcas.get()),
                "cor_numeros": self.v_cor_numeros.get(), "logo_pos": self.v_logo_pos.get(), "logo_tam": self.v_logo_tam.get()}

    def _guardar_pedido(self) -> Path | None:
        """Pergunta onde guardar e escreve o pedido. O caminho, ou None se desistiu/falhou."""
        base = core.nome_seguro(self.v_nome.get()) or "pedido"
        p = filedialog.asksaveasfilename(title=t("win_guardar_pedido").rstrip("…"), initialdir=self._dir_de(self.v_saida), initialfile=base + core.pedido_ficheiro.EXTENSAO,
                                         defaultextension=core.pedido_ficheiro.EXTENSAO,
                                         filetypes=[("Rifas", "*" + core.pedido_ficheiro.EXTENSAO), (t("dlg_tipo_todos"), "*.*")])
        if not p:
            return None
        try:
            Path(p).write_bytes(core.pedido_ficheiro.para_bytes(self._campos_do_pedido()))
        except OSError as e:
            messagebox.showerror(t("app_nome"), t("erro_inesperado", erro=e))
            return None
        self._set_estado("win_guardado", C["ok"], nome=Path(p).name)
        return Path(p)

    def _abrir_pedido(self, ficheiro: str | None = None) -> bool:
        """Pergunta que pedido abrir (ou recebe o `ficheiro`, nos testes) e repõe os campos. False se desistiu ou o ficheiro não serve."""
        p = ficheiro or filedialog.askopenfilename(title=t("win_abrir_pedido").rstrip("…"), initialdir=self._dir_de(self.v_saida),
                                                   filetypes=[("Rifas", "*" + core.pedido_ficheiro.EXTENSAO), (t("dlg_tipo_todos"), "*.*")])
        if not p:
            return False
        try:
            with open(p, "rb") as f:
                campos = core.pedido_ficheiro.de_bytes(f.read(core.pedido_ficheiro.MAX_BYTES + 1))
        except OSError as e:
            messagebox.showerror(t("app_nome"), t("erro_inesperado", erro=e))
            return False
        except core.ErroRifas as e:
            messagebox.showwarning(t("app_nome"), str(e))
            return False
        self._aplicar_pedido(campos)
        self._set_estado("win_guardado", C["ok"], nome=Path(p).name)
        return True

    def _aplicar_pedido(self, c: dict) -> None:
        for chave, var in (("inicio", self.v_inicio), ("fim", self.v_fim), ("digitos", self.v_digitos), ("max_ficheiro", self.v_max), ("margem", self.v_margem),
                           ("porfolha", self.v_porfolha), ("prefixos", self.v_prefixos), ("saltar", self.v_saltar), ("cor_numeros", self.v_cor_numeros),
                           ("logo_pos", self.v_logo_pos), ("logo_tam", self.v_logo_tam), ("cor_serie", self.v_cor_serie), ("marcas", self.v_marcas)):
            if chave in c:
                var.set(c[chave])
        if "papel" in c:
            self.v_papel.set(c["papel"])
            if hasattr(self, "m_papel") and self.m_papel.winfo_exists():
                self.m_papel.set(c["papel"])
        if "nome" in c:
            self.v_nome.set(c["nome"])
            self.e_nome.delete(0, "end")
            self.e_nome.insert(0, c["nome"])
            self.e_nome.configure(border_color=C["borda"])
        if "modo" in c:
            self._set_modo(c["modo"])
            self.seg_modo.set(t("modo_varios") if c["modo"] == "varios" else t("modo_unico"))
        if self.info is not None:
            self._recalcular_folha()
        self._resumo()
        self._guardar_config()

    def usar_galeria(self, desenho: str, modelo: bytes, algarismos: bytes) -> None:
        """«Usar este template» da galeria: guarda o template e os algarismos numa pasta temporaria e continua como se os tivesse escolhido."""
        if self._pasta_galeria is None or not self._pasta_galeria.exists():
            self._pasta_galeria = Path(tempfile.mkdtemp(prefix="rifas-galeria-"))
        tpl, alg = self._pasta_galeria / f"galeria-{desenho}.pdf", self._pasta_galeria / "algarismos.pdf"
        tpl.write_bytes(modelo)
        alg.write_bytes(algarismos)
        self.v_template.set(str(tpl))
        self.v_alg.set(str(alg))
        self._analisar()

    def _apagar_pasta_galeria(self) -> None:
        if self._pasta_galeria is not None:
            shutil.rmtree(self._pasta_galeria, ignore_errors=True)
            self._pasta_galeria = None

    def _ev_editor(self, token: int, png: bytes | None, erro: Exception | None) -> None:
        j = self.w_extras.get("editor")
        if j is not None and j.winfo_exists():
            j.resultado(token, png, erro)

    def _ev_galeria(self, token: int, png: bytes | None, erro: Exception | None) -> None:
        j = self.w_extras.get("galeria")
        if j is not None and j.winfo_exists():
            j.resultado(token, png, erro)

    def _ev_precario(self, token: int, png: bytes | None, erro: Exception | None) -> None:
        j = self.w_extras.get("precario")
        if j is not None and j.winfo_exists():
            j.resultado(token, png, erro)

    # -- fila (worker -> interface)
    def _escrever_log(self, m: str) -> None:
        self.log_linhas.append(m)
        self.log.configure(state="normal")
        self.log.insert("end", m + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _ler_fila(self) -> None:
        limite = time.monotonic() + 0.03       # nunca prende a interface mais de ~30 ms por ciclo
        try:
            while time.monotonic() < limite:
                ev = self.fila.get_nowait()
                getattr(self, "_ev_" + ev[0])(*ev[1:])
        except queue.Empty:
            pass
        if not self._a_fechar:
            self.after(50, self._ler_fila)

    def _ev_log(self, m: str) -> None:
        self._escrever_log(m)

    def _ev_prog(self, feitas: int, total: int) -> None:
        self.prog = feitas / max(total, 1)
        self.barra.set(self.prog)
        self._set_estado("est_progresso", a=feitas, b=total)

    def _ev_miniatura(self, token: int, png: bytes) -> None:
        if token == self.token and self.prep is None:
            self._mostrar_pil(Image.open(io.BytesIO(png)), ("template_titulo", {}))

    def _avisos(self, logs: list) -> None:
        for m in logs:
            if m.startswith("⚠"):
                self._escrever_log(m)

    def _novo_template(self, info: core.InfoTemplate) -> None:
        """Ao carregar um template novo, os algarismos passam a ser os do desenho (ex.: 0001 -> 4)."""
        if self._info_template_anterior != str(info.caminho):
            self._info_template_anterior = str(info.caminho)
            self.v_digitos.set(str(len(info.primeiro)))
            self.v_porfolha.set("")          # novo template: volta ao maximo que couber na folha

    def _ev_prep(self, token: int, prep: core.Preparado, logs: list) -> None:
        if token != self.token:
            return
        self.prep, self.info = prep, prep.info
        self._novo_template(prep.info)
        self.st_tpl, self.st_alg = ("ok", prep.info), ("ok", prep)
        self._render_tpl()
        self._render_alg()
        self._avisos(logs)
        self._estado_botoes()
        self._recalcular_folha()

    def _ev_prep_alg(self, token: int, e: core.ErroAlgarismos, logs: list) -> None:
        if token != self.token:
            return
        self.info = e.info
        self._novo_template(e.info)
        self.st_tpl = ("ok", e.info)
        if self.v_alg.get():       # o ficheiro escolhido tem problemas
            self.st_alg = ("erro", e)
            messagebox.showwarning(t("app_nome"), str(e))
        else:                      # ainda nao escolheu o ficheiro
            self.st_alg = ("precisa",)
        self._render_tpl()
        self._render_alg()
        self._estado_botoes()
        self._recalcular_folha()

    def _ev_prep_erro(self, token: int, e: Exception, logs: list) -> None:
        if token != self.token:
            return
        self.info = None
        err = e if isinstance(e, core.ErroRifas) else core.ErroRifas("erro_inesperado", erro=str(e))
        self.st_tpl, self.st_alg = ("erro", err), ("vazio",)
        self._render_tpl()
        self._render_alg()
        self._estado_botoes()
        self._recalcular_folha()
        messagebox.showerror(t("app_nome"), str(err))

    def _ev_previa(self, png: bytes, tr: core.Trabalho, n: int) -> None:
        if self.prep is None:              # entretanto limpou-se tudo
            self._estado_botoes()
            return
        self._mostrar_pil(Image.open(io.BytesIO(png)),
                          ("previa_titulo_n", {"de": tr.inicio, "ate": min(tr.fim, tr.inicio + n - 1)}),
                          manter_zoom=True)
        self._estado_botoes()

    def _ev_previa_erro(self, e: Exception) -> None:
        self._estado_botoes()
        messagebox.showerror(t("app_nome"), str(e) if isinstance(e, core.ErroRifas) else t("erro_inesperado", erro=e))

    def _limpar_tudo(self) -> None:
        """Volta ao estado de um arranque novo: sem template, algarismos, pasta nem nome, numeros por defeito,
        pre-visualizacao, progresso e registo vazios. A lingua, o tema e o papel/margem das folhas mantem-se."""
        if self.a_gerar:
            return
        self.token += 1                      # uma analise ainda a decorrer deixa de contar
        self.prep = self.info = self.disp = None
        self.st_folha = None
        self._info_template_anterior = None
        for v, valor in ((self.v_template, ""), (self.v_alg, ""), (self.v_saida, ""), (self.v_nome, ""),
                         (self.v_inicio, "1"), (self.v_fim, "1000"), (self.v_digitos, "4"), (self.v_max, "300"),
                         (self.v_porfolha, "")):
            v.set(valor)
        for v, valor in ((self.v_prefixos, ""), (self.v_saltar, ""), (self.v_cor_serie, False), (self.v_marcas, False),
                         (self.v_cor_numeros, ""), (self.v_logo, ""), (self.v_logo_pos, "sd"),
                         (self.v_logo_tam, str(core.marca.TAMANHO_PADRAO))):
            v.set(valor)
        self._apagar_pasta_galeria()
        self.e_nome.delete(0, "end")
        self.e_nome.configure(border_color=C["borda"])
        self.st_tpl, self.st_alg = ("vazio",), ("vazio",)
        self.st_titulo = ("previa_titulo", {})
        self.st_estado = None
        self.log_linhas.clear()
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.prog = 0.0
        self.barra.set(0)
        self.ultima_pasta = None
        self.mostrar_pasta = False
        self.f_pos.pack_forget()
        self.visor.limpar()
        self.modo = "varios"
        self.seg_modo.set(t("modo_varios"))
        self._render_tudo()                   # textos, resumo e botoes (inclui esconder o painel da folha)
        self.rolavel.tela.yview_moveto(0)
        self._guardar_config()

    def _fim(self, mostrar_pasta: bool = True) -> None:
        self.a_gerar = False
        self.mostrar_pasta = mostrar_pasta
        if mostrar_pasta:
            self.f_pos.pack(fill="x", padx=2, pady=(8, 0), before=self.log)
        self._estado_botoes()

    def _ev_fim(self, res: list) -> None:
        self._fim()
        self.prog = 1.0
        self.barra.set(1)
        mau = [r for r in res if not r.ok]
        if mau:
            self._set_estado("est_erros", C["erro"], n=len(mau))
        else:
            self._set_estado("est_ok", C["ok"], n=len(res))

    def _ev_cancelado(self) -> None:
        self._fim()
        self.prog = 0.0
        self.barra.set(0)
        self._set_estado("est_cancelado", C["aviso"])

    def _ev_erro(self, e: Exception, tb: str) -> None:
        self._fim(mostrar_pasta=False)
        self._set_estado("est_falhou", C["erro"])
        self._escrever_log(tb if not isinstance(e, core.ErroRifas) else str(e))
        messagebox.showerror(t("app_nome"), str(e) if isinstance(e, core.ErroRifas) else t("erro_inesperado", erro=e))


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "--selftest":
        sys.exit(selftest(Path(sys.argv[2])))
    # o motor de PDF corre noutro fio e e quase todo Python: sem isto a interface fica "agarrada" ao GIL
    sys.setswitchinterval(0.0005)
    App().mainloop()


if __name__ == "__main__":
    main()
