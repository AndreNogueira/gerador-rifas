"""Tutorial passo a passo (janela de ajuda) com imagens.

As imagens estao em assets/ajuda/: `modelo.jpg` e `digitos.png` (iguais em todas as linguas) e, para cada lingua,
`<lingua>_a.png` / `<lingua>_b.png` (capturas da janela real) + `ajuda.json` com as zonas a recortar.
Tudo isto e gerado por testes/fazer_ajuda.py a partir da propria aplicacao.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import customtkinter as ctk
from PIL import Image

import i18n
from i18n import t
from tema import C, FONTE
from widgets import Rolavel

BASE = Path(__file__).resolve().parent
PASTA = BASE / "assets" / "ajuda"
TOPICO_ALGARISMOS = 3          # posicao do topico «2 Algarismos» na lista


def _caixas() -> dict:
    try:
        return json.loads((PASTA / "ajuda.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def lista_de_topicos() -> list:
    """[(titulo no menu, titulo da pagina, texto, [imagens])]; imagem = ('fixa', ficheiro) | ('rec', estado, zona)."""
    ps = dict(previa=t("previa"), gerar=t("gerar"), ajustar=t("zoom_ajustar"), pasta=t("abrir_pasta"),
              de=t("de"), ate=t("ate"), algarismos=t("algarismos"), varios=t("modo_varios"), unico=t("modo_unico"),
              papel=t("lay_papel"), margem=t("lay_margem"), porfolha=t("lay_por_folha"),
              ajuda=t("m_ajuda"), video=t("mi_video"), limpar=t("limpar"), ficheiro=t("m_ficheiro"))

    def curto(s: str) -> str:               # "Algarismos 0-9 (obrigatorio)" -> "Algarismos 0-9"
        return re.sub(r"\s*[（(][^)）]*[)）]\s*$", "", s)
    return [
        (t("tut_t0"), t("tut_t0"), t("tut_b0", **ps) + "\n\n" + t("tut_video", **ps), [("rec", "a", "janela")]),
        ("1   " + curto(t("c1_titulo")), t("c1_titulo"), t("tut_b1"), [("fixa", "modelo.jpg"), ("rec", "a", "c1")]),
        ("      " + t("tut_t_uma"), t("tut_t_uma"), t("tut_b_uma", **ps),
         [("fixa", "modelo1.jpg"), ("rec", "c", "c1"), ("fixa", "folha.png")]),
        ("2   " + curto(t("c2_titulo")), t("ajuda_titulo"), t("ajuda_texto"), [("fixa", "digitos.png"), ("rec", "a", "c2")]),
        ("3   " + curto(t("c3_titulo")), t("c3_titulo"), t("tut_b3", **ps), [("rec", "a", "c3")]),
        ("4   " + curto(t("c4_titulo")), t("c4_titulo"), t("tut_b4"), [("rec", "a", "c4")]),
        ("5   " + t("tut_t5"), t("tut_t5"), t("tut_b5", **ps) + "\n\n" + t("tut_limpar", **ps),
         [("rec", "a", "barra"), ("rec", "b", "acoes")]),
        (t("tut_t6"), t("tut_t6"), t("tut_b6"), []),
    ]


class Tutorial(ctk.CTkToplevel):
    def __init__(self, app, topico: int = 0):
        super().__init__(app)
        self.app = app
        self.title(f"{t('tut_titulo')} – {t('app_nome')}")
        self.geometry("1060x760")
        self.minsize(780, 540)
        self.configure(fg_color=C["fundo"])
        ico = BASE / "assets" / "icon.ico"
        if ico.exists():
            self.after(250, lambda: self._icone(ico))
        self.topicos = lista_de_topicos()
        self.indice = -1
        self._larg_desenhada = 0
        self._espera = None
        self._abertas: dict = {}
        self._fotos: list = []
        self._caixas = _caixas()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        lat = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=C["cartao"])
        lat.grid(row=0, column=0, sticky="ns")
        lat.grid_propagate(False)
        ctk.CTkLabel(lat, text=t("tut_titulo"), font=ctk.CTkFont(FONTE, 20, "bold"), text_color=C["texto"]).pack(
            anchor="w", padx=22, pady=(22, 14))
        self.b_top = []
        for i, tp in enumerate(self.topicos):
            b = ctk.CTkButton(lat, text=tp[0], anchor="w", height=40, corner_radius=8, fg_color="transparent",
                              hover_color=C["sel_menu"], text_color=C["texto"], font=ctk.CTkFont(FONTE, 13),
                              command=lambda i=i: self.mostrar(i))
            b.pack(fill="x", padx=12, pady=2)
            self.b_top.append(b)

        dir_ = ctk.CTkFrame(self, fg_color="transparent")
        dir_.grid(row=0, column=1, sticky="nsew")
        dir_.grid_rowconfigure(0, weight=1)
        dir_.grid_columnconfigure(0, weight=1)
        self.rol = Rolavel(dir_)
        self.rol.grid(row=0, column=0, sticky="nsew")
        self.rol.tela.bind("<Configure>", self._ao_redimensionar, add="+")
        nav = ctk.CTkFrame(dir_, fg_color=C["cartao"], corner_radius=0, height=60)
        nav.grid(row=1, column=0, sticky="ew")
        nav.grid_propagate(False)
        kw = dict(height=36, width=130, corner_radius=8, font=ctk.CTkFont(FONTE, 13))
        self.b_ant = ctk.CTkButton(nav, text="←  " + t("tut_ant"), command=lambda: self.mostrar(self.indice - 1),
                                   fg_color=C["campo"], hover_color=C["borda"], text_color=C["texto"],
                                   border_width=1, border_color=C["borda"], **kw)
        self.b_ant.pack(side="left", padx=(24, 0), pady=12)
        self.b_seg = ctk.CTkButton(nav, text=t("tut_seg") + "  →", command=lambda: self.mostrar(self.indice + 1),
                                   fg_color=C["acento"], hover_color=C["acento_h"], text_color=C["sobre_acento"], **kw)
        self.b_seg.pack(side="right", padx=(0, 24), pady=12)
        self.bind("<MouseWheel>", self.rol.roda)
        self.bind("<Left>", lambda e=None: self.mostrar(self.indice - 1))
        self.bind("<Right>", lambda e=None: self.mostrar(self.indice + 1))
        self.bind("<Escape>", lambda e=None: self.destroy())
        self.after(60, lambda: self.mostrar(topico))
        self.after(120, self.focus_force)

    def _icone(self, ico: Path) -> None:
        try:
            self.iconbitmap(str(ico))
        except Exception:
            pass

    def tema(self) -> None:
        self.rol.tema()

    # -- imagens
    def _carregar(self, espec: tuple):
        """Devolve (imagem PIL, largura natural em unidades logicas) ou None."""
        try:
            if espec[0] == "fixa":
                im = self._abertas.get(espec[1]) or Image.open(PASTA / espec[1])
                self._abertas[espec[1]] = im
                return im.convert("RGB"), float(im.width)
            _, estado, zona = espec
            for lg in (i18n.atual(), "en", "pt"):
                info = self._caixas.get(lg, {}).get(estado)
                ficheiro = PASTA / f"{lg}_{estado}.png"
                if info and zona in info and ficheiro.exists():
                    break
            else:
                return None
            im = self._abertas.get(ficheiro.name) or Image.open(ficheiro)
            self._abertas[ficheiro.name] = im
            esc = float(info.get("escala", 1.0)) or 1.0
            rec = im.convert("RGB").crop(tuple(info[zona]))
            return rec, rec.width / esc
        except Exception:
            return None

    # -- conteudo
    def mostrar(self, i: int) -> None:
        if not 0 <= i < len(self.topicos):
            return
        self.indice = i
        for j, b in enumerate(self.b_top):
            b.configure(fg_color=C["acento_suave"] if j == i else "transparent",
                        font=ctk.CTkFont(FONTE, 13, "bold" if j == i else "normal"))
        self.b_ant.configure(state="normal" if i > 0 else "disabled")
        self.b_seg.configure(state="normal" if i < len(self.topicos) - 1 else "disabled")
        for w in self.rol.interior.winfo_children():
            w.destroy()
        self._fotos = []
        _, titulo, corpo, imagens = self.topicos[i]
        esc = self._get_window_scaling()
        self._larg_desenhada = self.rol.tela.winfo_width()
        avail = max(int(self._larg_desenhada / esc) - 88, 340)
        pai = self.rol.interior

        ctk.CTkLabel(pai, text=titulo, font=ctk.CTkFont(FONTE, 26, "bold"), text_color=C["texto"], anchor="w",
                     justify="left", wraplength=avail).pack(fill="x", padx=44, pady=(30, 12))
        for espec in imagens:
            r = self._carregar(espec)
            if r is None:
                continue
            im, natural = r
            w = int(min(avail - 14, natural))
            h = round(w * im.height / im.width)
            foto = im.resize((max(1, round(w * esc)), max(1, round(h * esc))), Image.LANCZOS)
            ci = ctk.CTkImage(light_image=foto, dark_image=foto, size=(w, h))
            self._fotos.append(ci)
            moldura = ctk.CTkFrame(pai, corner_radius=10, border_width=1, border_color=C["borda"], fg_color=C["cartao"])
            moldura.pack(anchor="w", padx=44, pady=(2, 14))
            ctk.CTkLabel(moldura, text="", image=ci).pack(padx=6, pady=6)
        fonte = ctk.CTkFont(FONTE, 14)
        for linha in corpo.split("\n"):
            if not linha.strip():
                ctk.CTkFrame(pai, height=6, fg_color="transparent").pack()
                continue
            if linha.startswith("• "):
                f = ctk.CTkFrame(pai, fg_color="transparent")
                f.pack(fill="x", padx=(52, 44), pady=3)
                ctk.CTkLabel(f, text="•", width=18, font=ctk.CTkFont(FONTE, 16, "bold"), text_color=C["link"],
                             anchor="n").pack(side="left", anchor="n")
                ctk.CTkLabel(f, text=linha[2:], font=fonte, text_color=C["texto"], anchor="w", justify="left",
                             wraplength=avail - 30).pack(side="left", fill="x", expand=True)
            else:
                ctk.CTkLabel(pai, text=linha, font=fonte, text_color=C["texto"], anchor="w", justify="left",
                             wraplength=avail).pack(fill="x", padx=44, pady=3)
        ctk.CTkFrame(pai, height=24, fg_color="transparent").pack()
        self.rol.tela.yview_moveto(0)
        self.after(30, self.rol._ajustar_regiao)

    def _ao_redimensionar(self, e) -> None:
        if abs(e.width - self._larg_desenhada) < 28 or self.indice < 0:
            return
        if self._espera is not None:
            self.after_cancel(self._espera)
        self._espera = self.after(160, self._refazer)

    def _refazer(self) -> None:
        self._espera = None
        if self.winfo_exists():
            pos = self.rol.tela.yview()[0]
            self.mostrar(self.indice)
            self.after(50, lambda: self.rol.tela.yview_moveto(pos))
