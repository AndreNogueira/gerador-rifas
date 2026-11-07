"""Interpretador minimo de PDF para texto (so usa pypdf, licenca BSD).

Percorre o conteudo de uma pagina (incluindo Form XObjects aninhados, como os que o Canva gera) e
devolve cada "corrida" de texto (operadores Tj, TJ, ' e ") com: texto, codigos dos caracteres, fonte,
tamanho efetivo, cor, posicao, direcao e avanco. Junta caracteres contiguos em tokens (o Canva desenha
cada carácter num Tj separado) e permite apagar os caracteres de tokens escolhidos.

Convencao de matrizes do PDF: ponto' = ponto x M (linha); mul(A, B) aplica A e depois B.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from pypdf.generic import ByteStringObject, ContentStream, IndirectObject

IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def mul(a: tuple, b: tuple) -> tuple:
    return (a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5])


def _trans(tx: float, ty: float) -> tuple:
    return (1.0, 0.0, 0.0, 1.0, tx, ty)


def _bytes_de(op) -> bytes:
    """Bytes originais de uma string do PDF (o pypdf pode ja a ter convertido para texto)."""
    b = getattr(op, "original_bytes", None)
    if b is not None:
        return bytes(b)
    if isinstance(op, (bytes, bytearray)):
        return bytes(op)
    return str(op).encode("latin-1", "replace")


# ------------------------------------------------------------------ fontes
_RE_CHAR = re.compile(r"beginbfchar(.*?)endbfchar", re.S)
_RE_RANGE = re.compile(r"beginbfrange(.*?)endbfrange", re.S)
_RE_PAR = re.compile(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>")
_RE_INTERV = re.compile(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]+>|\[[^\]]*\])")
_RE_HEX = re.compile(r"<([0-9A-Fa-f]*)>")


def _utf16(hexa: str) -> str:
    try:
        return bytes.fromhex(hexa if len(hexa) % 2 == 0 else hexa + "0").decode("utf-16-be")
    except Exception:
        return ""


def parse_tounicode(dados: bytes) -> dict:
    """CMap ToUnicode -> {codigo: texto}."""
    txt = dados.decode("latin-1", "replace")
    mapa: dict = {}
    for bloco in _RE_CHAR.findall(txt):
        for src, dst in _RE_PAR.findall(bloco):
            mapa[int(src, 16)] = _utf16(dst)
    for bloco in _RE_RANGE.findall(txt):
        for lo, hi, dst in _RE_INTERV.findall(bloco):
            a, b = int(lo, 16), int(hi, 16)
            if b - a > 70000:
                continue
            if dst.startswith("["):
                for k, h in enumerate(_RE_HEX.findall(dst)):
                    mapa[a + k] = _utf16(h)
            else:
                base = _utf16(dst[1:-1])
                if not base:
                    continue
                for k in range(b - a + 1):
                    mapa[a + k] = base[:-1] + chr(ord(base[-1]) + k)
    return mapa


def _num(x) -> float:
    return float(x.get_object() if hasattr(x, "get_object") else x)


class InfoFonte:
    """Dados de uma fonte do PDF: tamanho dos codigos, ToUnicode e larguras (em milesimos do corpo)."""

    def __init__(self, obj, ref=None):
        self.obj, self.ref = obj, ref
        base = str(obj.get("/BaseFont", "")).lstrip("/")
        self.nome = re.sub(r"^[A-Z]{6}\+", "", base)
        tipo0 = obj.get("/Subtype") == "/Type0"
        self.n_bytes = 2 if tipo0 else 1
        self.tounicode: dict = {}
        try:
            if "/ToUnicode" in obj:
                self.tounicode = parse_tounicode(obj["/ToUnicode"].get_object().get_data())
        except Exception:
            self.tounicode = {}
        self.larg: dict = {}
        self.dw = 1000.0
        try:
            if tipo0:
                df = obj["/DescendantFonts"][0].get_object()
                self.dw = _num(df.get("/DW", 1000))
                self._ler_w(df.get("/W"))
            else:
                first = int(obj.get("/FirstChar", 0))
                ws = obj.get("/Widths")
                if ws is not None:
                    self.larg = {first + i: _num(w) for i, w in enumerate(ws.get_object())}
                desc = obj.get("/FontDescriptor")
                self.dw = _num(desc.get_object().get("/MissingWidth", 500)) if desc is not None else 500.0
        except Exception:
            pass

    def _ler_w(self, w) -> None:
        if w is None:
            return
        w = [x.get_object() if hasattr(x, "get_object") else x for x in w.get_object()]
        i = 0
        while i < len(w):
            c = int(w[i])
            nxt = w[i + 1] if i + 1 < len(w) else None
            if isinstance(nxt, list):
                for k, v in enumerate(nxt):
                    self.larg[c + k] = _num(v)
                i += 2
            else:
                c2, v = int(nxt), _num(w[i + 2])
                for k in range(c, min(c2, c + 70000) + 1):
                    self.larg[k] = v
                i += 3

    def largura(self, codigo: int) -> float:
        return self.larg.get(codigo, self.dw)

    def decodificar(self, dados: bytes) -> list:
        """[(codigo, caractere)]"""
        n = self.n_bytes
        saida = []
        for i in range(0, len(dados) - n + 1, n):
            cod = int.from_bytes(dados[i:i + n], "big")
            ch = self.tounicode.get(cod)
            if ch is None:
                ch = chr(cod) if n == 1 else "�"
            saida.append((cod, ch))
        return saida


# ------------------------------------------------------------------ interpretador
@dataclass
class Corrida:
    texto: str
    codigos: list
    chars: list
    fonte: InfoFonte
    fonte_nome: str          # nome no dicionario de recursos (/F24)
    tamanho: float           # tamanho efetivo, em pt
    cor: tuple | None        # rgb 0..1 (None se nao foi possivel ler)
    origem: tuple            # inicio da linha de base, coordenadas do PDF (y para cima)
    direcao: tuple           # vetor unitario da escrita, coordenadas do PDF
    avanco: float            # comprimento do texto, em pt
    local: tuple             # (id do fluxo, indice do operador) - para apagar
    adv_chars: list = field(default_factory=list)   # avanco de cada caractere (pt)
    simples: bool = False    # True se o operador tem uma so string (Tj)


@dataclass
class Token:
    texto: str
    corrida: Corrida         # corrida do 1.o caractere (fonte, tamanho, cor, direcao)
    origem: tuple            # origem do 1.o caractere (PDF, y para cima)
    avanco: float            # comprimento do token (pt)
    chars: list              # [(indice da corrida, indice do caractere)]


@dataclass
class _Est:
    ctm: tuple = IDENT
    cor: tuple | None = None
    fonte_nome: str = ""
    fonte: object = None
    tam: float = 1.0
    tc: float = 0.0
    tw: float = 0.0
    th: float = 1.0
    lead: float = 0.0
    tm: tuple = IDENT
    tlm: tuple = IDENT

    def copia(self) -> "_Est":
        return _Est(**self.__dict__)


def _cmyk(c, m, y, k) -> tuple:
    return ((1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k))


class Extrator:
    """Corre o conteudo de uma pagina e junta as corridas de texto."""

    def __init__(self, leitor, pagina):
        self.leitor, self.pagina = leitor, pagina
        self.corridas: list = []
        self.fluxos: dict = {}       # id -> (objeto, ContentStream)
        self._fontes: dict = {}
        rec = pagina["/Resources"].get_object() if "/Resources" in pagina else {}
        self._correr(pagina, rec, IDENT, 0)

    # -- fontes
    def _fonte(self, recursos, nome):
        fontes = recursos.get("/Font")
        if fontes is None or nome not in fontes.get_object():
            return None
        d = fontes.get_object()
        ref = d.raw_get(nome)
        obj = ref.get_object() if isinstance(ref, IndirectObject) else ref
        chave = id(obj)
        if chave not in self._fontes:
            self._fontes[chave] = InfoFonte(obj, ref)
        return self._fontes[chave]

    # -- percurso
    def _correr(self, obj, recursos, ctm: tuple, prof: int) -> None:
        if prof > 12:
            return
        try:
            if hasattr(obj, "get_data"):                       # Form XObject
                cs = ContentStream(obj, self.leitor)
            else:                                              # pagina
                cs = obj.get_contents()
        except Exception:
            return
        if cs is None:
            return
        chave = id(obj)
        self.fluxos[chave] = (obj, cs)
        est, pilha = _Est(ctm=ctm), []
        for i, (ops, op) in enumerate(cs.operations):
            try:
                if op == b"q":
                    pilha.append(est.copia())
                elif op == b"Q":
                    if pilha:
                        est = pilha.pop()
                elif op == b"cm":
                    est.ctm = mul(tuple(float(x) for x in ops), est.ctm)
                elif op == b"BT":
                    est.tm = est.tlm = IDENT
                elif op == b"Tf":
                    est.fonte_nome, est.tam = str(ops[0]), float(ops[1])
                    est.fonte = self._fonte(recursos, est.fonte_nome)
                elif op == b"Tc":
                    est.tc = float(ops[0])
                elif op == b"Tw":
                    est.tw = float(ops[0])
                elif op == b"Tz":
                    est.th = float(ops[0]) / 100
                elif op == b"TL":
                    est.lead = float(ops[0])
                elif op == b"Tm":
                    est.tm = est.tlm = tuple(float(x) for x in ops)
                elif op in (b"Td", b"TD"):
                    tx, ty = float(ops[0]), float(ops[1])
                    if op == b"TD":
                        est.lead = -ty
                    est.tlm = mul(_trans(tx, ty), est.tlm)
                    est.tm = est.tlm
                elif op == b"T*":
                    est.tlm = mul(_trans(0, -est.lead), est.tlm)
                    est.tm = est.tlm
                elif op == b"rg":
                    est.cor = tuple(float(x) for x in ops)
                elif op == b"g":
                    est.cor = (float(ops[0]),) * 3
                elif op == b"k":
                    est.cor = _cmyk(*(float(x) for x in ops))
                elif op in (b"sc", b"scn"):
                    n = [float(x) for x in ops if isinstance(x, (int, float))]
                    if len(n) == 3:
                        est.cor = tuple(n)
                    elif len(n) == 1:
                        est.cor = (n[0],) * 3
                    elif len(n) == 4:
                        est.cor = _cmyk(*n)
                elif op in (b"Tj", b"'", b'"'):
                    if op in (b"'", b'"'):
                        est.tlm = mul(_trans(0, -est.lead), est.tlm)
                        est.tm = est.tlm
                    self._mostrar(est, [ops[-1]], (chave, i), True)
                elif op == b"TJ":
                    self._mostrar(est, list(ops[0]), (chave, i), False)
                elif op == b"Do":
                    xo = recursos.get("/XObject")
                    if xo is not None and ops[0] in xo.get_object():
                        x = xo.get_object()[ops[0]].get_object()
                        if x.get("/Subtype") == "/Form":
                            m = tuple(float(v) for v in x["/Matrix"]) if "/Matrix" in x else IDENT
                            rec = x["/Resources"].get_object() if "/Resources" in x else recursos
                            self._correr(x, rec, mul(m, est.ctm), prof + 1)
            except Exception:
                continue

    def _mostrar(self, est: _Est, itens: list, local: tuple, simples: bool) -> None:
        f = est.fonte
        if f is None:
            return
        M = mul(est.tm, est.ctm)
        escala = math.hypot(M[0], M[1]) or 1.0
        origem = (M[4], M[5])
        direcao = (M[0] / escala, M[1] / escala)
        codigos, chars, advs, adv = [], [], [], 0.0
        for it in itens:
            if isinstance(it, (int, float)):
                d = -float(it) / 1000 * est.tam * est.th
                est.tm = mul(_trans(d, 0), est.tm)
                adv += d
                if advs:
                    advs[-1] += d * escala      # o ajuste (kerning) conta para o caractere anterior
                continue
            for cod, ch in f.decodificar(_bytes_de(it)):
                w = f.largura(cod) / 1000 * est.tam * est.th + est.tc + (est.tw if ch == " " else 0.0)
                est.tm = mul(_trans(w, 0), est.tm)
                adv += w
                codigos.append(cod)
                chars.append(ch)
                advs.append(w * escala)
        if codigos:
            self.corridas.append(Corrida(
                texto="".join(chars), codigos=codigos, chars=chars, fonte=f, fonte_nome=est.fonte_nome,
                tamanho=est.tam * escala, cor=est.cor, origem=origem, direcao=direcao,
                avanco=adv * escala, local=local, adv_chars=advs, simples=simples))

    # -- tokens (numeros dentro do texto, mesmo que cada caractere venha num Tj separado)
    def tokens(self, padrao) -> list:
        """Procura `padrao` (regex) no texto, juntando caracteres contiguos da mesma linha."""
        cars = []     # (indice da corrida, k, origem do caractere)
        for ri, c in enumerate(self.corridas):
            pos = 0.0
            for k in range(len(c.chars)):
                cars.append((ri, k, (c.origem[0] + c.direcao[0] * pos, c.origem[1] + c.direcao[1] * pos)))
                pos += c.adv_chars[k]
        grupos, atual = [], []
        for ri, k, o in cars:
            c = self.corridas[ri]
            if atual:
                pri, pk, po = atual[-1]
                pc = self.corridas[pri]
                esp = (po[0] + pc.direcao[0] * pc.adv_chars[pk], po[1] + pc.direcao[1] * pc.adv_chars[pk])
                junto = (id(pc.fonte) == id(c.fonte) and abs(pc.tamanho - c.tamanho) < 0.01 * max(c.tamanho, 1)
                         and abs(pc.direcao[0] - c.direcao[0]) < 1e-3 and abs(pc.direcao[1] - c.direcao[1]) < 1e-3
                         and pc.cor == c.cor
                         and math.hypot(o[0] - esp[0], o[1] - esp[1]) < 0.35 * c.tamanho)
                if not junto:
                    grupos.append(atual)
                    atual = []
            atual.append((ri, k, o))
        if atual:
            grupos.append(atual)
        saida = []
        for g in grupos:
            texto = "".join(self.corridas[ri].chars[k] for ri, k, _ in g)
            for m in padrao.finditer(texto):
                cs = g[m.start():m.end()]
                saida.append(Token(
                    texto=m.group(0), corrida=self.corridas[cs[0][0]], origem=cs[0][2],
                    avanco=sum(self.corridas[ri].adv_chars[k] for ri, k, _ in cs),
                    chars=[(ri, k) for ri, k, _ in cs]))
        return saida

    # -- apagar
    def apagar(self, tokens: list) -> None:
        """Apaga do conteudo os caracteres dos tokens e regrava os fluxos alterados."""
        por_run: dict = {}
        for t in tokens:
            for ri, k in t.chars:
                por_run.setdefault(ri, set()).add(k)
        mudancas: dict = {}          # chave do fluxo -> {indice do operador: None | (operandos, operador)}
        for ri, ks in por_run.items():
            c = self.corridas[ri]
            chave, i = c.local
            operandos, op = self.fluxos[chave][1].operations[i]
            if len(ks) >= len(c.chars):
                mudancas.setdefault(chave, {})[i] = None                 # remove o operador todo
            elif c.simples and op in (b"Tj", b"'", b'"'):
                dados = _bytes_de(operandos[-1])
                n = c.fonte.n_bytes
                novo = b"".join(dados[j * n:(j + 1) * n] for j in range(len(c.chars)) if j not in ks)
                mudancas.setdefault(chave, {})[i] = (list(operandos[:-1]) + [ByteStringObject(novo)], op)
        for chave, mud in mudancas.items():
            obj, cs = self.fluxos[chave]
            novas = []
            for k, o in enumerate(cs.operations):
                if k in mud:
                    if mud[k] is not None:
                        novas.append(mud[k])
                else:
                    novas.append(o)
            cs.operations = novas
            if hasattr(obj, "get_data"):              # Form XObject
                obj.set_data(cs.get_data())
            else:                                     # pagina
                obj.replace_contents(cs)
