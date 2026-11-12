"""O modelo de edição do editor de templates, sem janelas nem browser: os elementos, o histórico (desfazer e refazer), duplicar, ordem de desenho,
caixas e «o que está debaixo do rato». É o que a app Windows (`app/extras.py`) usa para editar; o site tem o equivalente em TypeScript
(`editor-modelo.ts`, `editor-historico.ts`) porque o ecrã dele é um SVG. O que se desenha e se valida é sempre `core.editor` (`de_dict`, `criar_template`).

Coordenadas em pt, origem em cima à esquerda, como em `core.editor`; um texto ancora-se na linha de base (`ASCENTE` × tamanho abaixo do topo).
"""
from __future__ import annotations

import copy
import itertools
import time
from dataclasses import asdict, dataclass, field

from . import editor

MAX_HISTORICO = 50
JUNTAR_S = 1.2                                   # alterações seguidas ao mesmo valor, a menos de 1,2 s, são um só passo
TOLERANCIA = 4.0                                 # pt à volta de uma linha ou de um contorno para a apanhar com o rato
_ids = itertools.count(1)


@dataclass
class El:
    tipo: str
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    cor: str = "#000000"
    contorno: str = ""
    espessura: float = 1.0
    raio: float = 0.0
    tracejado: bool = False
    texto: str = ""
    tamanho: float = 12.0
    negrito: bool = False
    alinhamento: str = "e"
    rot: int = 0
    id: int = field(default_factory=lambda: next(_ids))

    def para_dict(self) -> dict:
        d = asdict(self)
        d.pop("id")
        if self.tipo == "retangulo" and self.espessura <= 0:
            d["contorno"] = ""
        return d


def _el(tipo: str, **kw) -> El:
    return El(tipo=tipo, **kw)


def modelo_com_talao() -> dict:
    """A rifa com talão com que o editor começa (a mesma do site): moldura, talão com o número rodado, título, prémios, data e o número principal."""
    return {"largura": 535, "altura": 152, "fundo": "#ffffff", "elementos": [
        _el("retangulo", x=2, y=2, w=531, h=148, cor="#fffdf5", contorno="#0f6e73", espessura=2, raio=10).para_dict(),
        _el("retangulo", x=3, y=3, w=60, h=146, cor="#e6f4f1", raio=9).para_dict(),
        _el("linha", x=64, y=8, w=0, h=136, contorno="#0f6e73", espessura=1, tracejado=True).para_dict(),
        _el("texto", x=84, y=40, texto="TÍTULO DA RIFA", tamanho=21, cor="#0f6e73", negrito=True).para_dict(),
        _el("texto", x=84, y=56, texto="Associação · Local do evento", tamanho=9, cor="#555555").para_dict(),
        _el("texto", x=84, y=84, texto="1.º Prémio: …", tamanho=10, cor="#222222").para_dict(),
        _el("texto", x=84, y=98, texto="2.º Prémio: …", tamanho=10, cor="#222222").para_dict(),
        _el("texto", x=84, y=138, texto="Sorteio: dd/mm/aaaa", tamanho=10, cor="#0f6e73", negrito=True).para_dict(),
        _el("texto", x=392, y=54, texto="Nº", tamanho=11, cor="#555555").para_dict(),
        _el("numero", x=412, y=56, tamanho=20, cor="#c2410c", negrito=True, texto=editor.NUMERO).para_dict(),
        _el("numero", x=42, y=112, tamanho=19, cor="#c2410c", negrito=True, texto=editor.NUMERO, rot=90).para_dict(),
    ]}


class Modelo:
    def __init__(self, desenho: dict | None = None, relogio=time.monotonic):
        self._relogio = relogio
        self.passado: list[dict] = []
        self.futuro: list[dict] = []
        self._grupo: tuple[str, float] | None = None
        self.carregar(desenho or modelo_com_talao())

    # ------------------------------------------------------------------ o desenho
    def carregar(self, desenho: dict) -> None:
        """Substitui o desenho (e apaga o histórico). Os campos que faltam ficam com os valores por omissão; o que não se conhece, deita-se fora."""
        self.largura = float(desenho.get("largura", 535))
        self.altura = float(desenho.get("altura", 152))
        self.fundo = str(desenho.get("fundo", "#ffffff"))
        campos = set(El.__dataclass_fields__) - {"id"}
        self.elementos = [El(**{k: v for k, v in e.items() if k in campos}) for e in desenho.get("elementos", []) if e.get("tipo") in editor.TIPOS and e.get("tipo") != "imagem"]
        self.passado, self.futuro, self._grupo = [], [], None

    def para_dict(self) -> dict:
        return {"largura": self.largura, "altura": self.altura, "fundo": self.fundo, "elementos": [e.para_dict() for e in self.elementos]}

    def desenho(self) -> editor.Desenho:
        """O desenho validado (`ErroRifas` se algo não presta); com ele se cria o template."""
        return editor.de_dict(self.para_dict())

    def problemas(self) -> dict:
        n = sum(1 for e in self.elementos if e.tipo == "numero")
        mau = next((e.texto for e in self.elementos if e.tipo == "texto" and editor.PADRAO_EXEMPLO.search(e.texto)), "")
        return {"numero": n < 1 or n > 2, "digitos": mau, "elementos": len(self.elementos) > editor.MAX_ELEMENTOS}

    def sem_problemas(self) -> bool:
        p = self.problemas()
        return not (p["numero"] or p["digitos"] or p["elementos"])

    # ------------------------------------------------------------------ histórico
    def _snapshot(self) -> dict:
        return copy.deepcopy({"largura": self.largura, "altura": self.altura, "fundo": self.fundo, "elementos": [asdict(e) for e in self.elementos]})

    def _repor(self, s: dict) -> None:
        self.largura, self.altura, self.fundo = s["largura"], s["altura"], s["fundo"]
        self.elementos = [El(**e) for e in s["elementos"]]                  # os ids mantêm-se: a seleção sobrevive ao desfazer

    def _antes(self, grupo: str | None) -> None:
        """Chamar antes de mudar: guarda o estado para o «desfazer», exceto se continua o mesmo gesto (mesmo `grupo`, a menos de 1,2 s)."""
        agora = self._relogio()
        junta = grupo is not None and self._grupo is not None and self._grupo[0] == grupo and agora - self._grupo[1] < JUNTAR_S
        self._grupo = (grupo, agora) if grupo else None
        if not junta:
            self.passado = [*self.passado[-(MAX_HISTORICO - 1):], self._snapshot()]
        self.futuro = []

    def pode_desfazer(self) -> bool:
        return bool(self.passado)

    def pode_refazer(self) -> bool:
        return bool(self.futuro)

    def desfazer(self) -> bool:
        if not self.passado:
            return False
        self._grupo = None
        self.futuro = [self._snapshot(), *self.futuro]
        self._repor(self.passado.pop())
        return True

    def refazer(self) -> bool:
        if not self.futuro:
            return False
        self._grupo = None
        self.passado = [*self.passado, self._snapshot()]
        self._repor(self.futuro.pop(0))
        return True

    # ------------------------------------------------------------------ edição
    def por_id(self, id_: int) -> El | None:
        return next((e for e in self.elementos if e.id == id_), None)

    def adicionar(self, tipo: str) -> int | None:
        """Um elemento novo no meio do desenho (None se já há elementos a mais). Devolve o id."""
        if len(self.elementos) >= editor.MAX_ELEMENTOS or tipo not in ("texto", "retangulo", "linha", "numero"):
            return None
        cx, cy = round(self.largura / 2), round(self.altura / 2)
        novo = {
            "texto": lambda: _el("texto", x=cx - 40, y=cy, texto="Texto", tamanho=16),
            "retangulo": lambda: _el("retangulo", x=cx - 40, y=cy - 20, w=80, h=40, cor="#dbeafe", contorno="#1e3a8a", espessura=1.5),
            "linha": lambda: _el("linha", x=cx - 50, y=cy, w=100, h=0, contorno="#555555", espessura=1.5),
            "numero": lambda: _el("numero", x=cx - 30, y=cy, tamanho=20, cor="#c2410c", negrito=True, texto=editor.NUMERO),
        }[tipo]()
        self._antes(None)
        self.elementos.append(novo)
        return novo.id

    def apagar(self, id_: int) -> bool:
        if self.por_id(id_) is None:
            return False
        self._antes(None)
        self.elementos = [e for e in self.elementos if e.id != id_]
        return True

    def duplicar(self, id_: int) -> int | None:
        e = self.por_id(id_)
        if e is None or len(self.elementos) >= editor.MAX_ELEMENTOS:
            return None
        self._antes(None)
        copia = copy.copy(e)
        copia.id, copia.x, copia.y = next(_ids), e.x + 10, e.y + 10
        self.elementos.append(copia)
        return copia.id

    def ordem(self, id_: int, para: int) -> bool:
        """+1 = para a frente (desenha-se mais tarde, por cima), -1 = para trás. False se já está na ponta."""
        i = next((k for k, e in enumerate(self.elementos) if e.id == id_), -1)
        j = i + para
        if i < 0 or not 0 <= j < len(self.elementos):
            return False
        self._antes(None)
        self.elementos.insert(j, self.elementos.pop(i))
        return True

    def definir(self, id_: int, **campos) -> bool:
        """Muda campos de um elemento (texto, cor, tamanho, …). Valores seguidos ao mesmo campo contam como um só passo do histórico."""
        e = self.por_id(id_)
        if e is None or any(k not in El.__dataclass_fields__ or k in ("id", "tipo") for k in campos):
            return False
        self._antes(f"{id_}:{','.join(sorted(campos))}")
        for k, v in campos.items():
            setattr(e, k, v)
        return True

    def mover(self, id_: int, dx: float, dy: float, gesto: str = "mover") -> bool:
        e = self.por_id(id_)
        if e is None:
            return False
        self._antes(f"{id_}:{gesto}")
        e.x, e.y = round(e.x + dx), round(e.y + dy)
        return True

    def pagina(self, largura: float | None = None, altura: float | None = None, fundo: str | None = None) -> None:
        self._antes("pagina")
        if largura is not None:
            self.largura = min(max(largura, editor.LARGURA_MIN), editor.LARGURA_MAX)
        if altura is not None:
            self.altura = min(max(altura, editor.ALTURA_MIN), editor.ALTURA_MAX)
        if fundo is not None:
            self.fundo = fundo

    # ------------------------------------------------------------------ geometria
    def caixa(self, id_: int) -> tuple[float, float, float, float] | None:
        """(x0, y0, x1, y1) do elemento, em pt (y para baixo). O texto usa a largura exata na Vera."""
        e = self.por_id(id_)
        if e is None:
            return None
        if e.tipo in ("retangulo", "linha"):
            return (min(e.x, e.x + e.w), min(e.y, e.y + e.h), max(e.x, e.x + e.w), max(e.y, e.y + e.h))
        texto = editor.NUMERO if e.tipo == "numero" else e.texto
        largura = editor.largura_do_texto(texto, e.negrito or e.tipo == "numero", e.tamanho) if texto else e.tamanho * 0.5
        sobe, desce = e.tamanho * editor.ASCENTE, e.tamanho * (1 - editor.ASCENTE)
        if e.rot == 90:                                   # o texto sobe a partir do ponto de ancoragem
            if e.alinhamento == "c":
                y0, y1 = e.y - largura / 2, e.y + largura / 2
            elif e.alinhamento == "d":
                y0, y1 = e.y, e.y + largura
            else:
                y0, y1 = e.y - largura, e.y
            return (e.x - sobe, y0, e.x + desce, y1)
        x0 = e.x - largura / 2 if e.alinhamento == "c" else e.x - largura if e.alinhamento == "d" else e.x
        return (x0, e.y - sobe, x0 + largura, e.y + desce)

    def elemento_em(self, x: float, y: float) -> int | None:
        """O id do elemento de cima que está debaixo do ponto (x, y) (em pt), ou None. As linhas apanham-se a `TOLERANCIA` pt; os retângulos pelo
        interior; o texto pela caixa."""
        for e in reversed(self.elementos):
            if e.tipo == "linha":
                if _distancia_ao_segmento(x, y, e.x, e.y, e.x + e.w, e.y + e.h) <= max(TOLERANCIA, e.espessura):
                    return e.id
                continue
            c = self.caixa(e.id)
            if c and c[0] - 1 <= x <= c[2] + 1 and c[1] - 1 <= y <= c[3] + 1:
                return e.id
        return None


def _distancia_ao_segmento(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx, dy = bx - ax, by - ay
    comprimento2 = dx * dx + dy * dy
    t = 0.0 if comprimento2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / comprimento2))
    return ((px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2) ** 0.5
