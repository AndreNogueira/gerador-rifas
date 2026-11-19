"""Moedas do preçário (`docs/PLANO_PRECARIO.md`): a moeda do **país** (não só da língua), a formatação como se escreve nessa língua e a **moeda inventada** («fichas», «tostões»).

- **Valores em inteiros**, em milésimos da unidade (`1500` = 1,500): nunca `float` (0,10 + 0,20 tem de dar 0,30). `valor_de_texto` lê o que o utilizador escreve («1,5», «1.50», «€ 1 234,50») e `formatar` escreve-o
  com as casas da moeda, o separador decimal e de milhares **da língua** e o símbolo antes ou depois (`1,50 €`, `€1.50`, `R$ 1,50`, `1,50 zł`, `Rp1.500`).
- **País → moeda** (`moeda_do_pais`): o país de omissão de cada língua (`pais_por_omissao`: `pt`→PT, `pt-br`→BR, `en`→US…) e o do browser (região do `navigator.language`, calculada no browser) só sugerem; o utilizador escolhe.
- Os símbolos usados têm todos letra nas famílias que o PDF embebe (`core/letras.py`): o teste confere. O ฿ (tailandês) não está: não há tailandês.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

MAX_VALOR = 9_999_999_999           # milésimos: quase dez milhões de unidades; acima disto o preço não cabe numa linha do cartaz nem faz sentido
MAX_NOME_INVENTADA = 14


@dataclass(frozen=True)
class Moeda:
    codigo: str                     # ISO 4217 («EUR»)
    simbolo: str                    # como se escreve no sítio («€», «R$», «zł»)
    decimais: int                   # 0 (iene, won, dong) ou 2


@dataclass(frozen=True)
class MoedaInventada:
    """Fichas, tostões, bolotas…: o nome que a pessoa escolhe, antes ou depois do número, com 0, 1 ou 2 casas decimais."""
    nome: str
    antes: bool = False
    decimais: int = 0


def _m(codigo: str, simbolo: str, decimais: int = 2) -> Moeda:
    return Moeda(codigo, simbolo, decimais)


MOEDAS: dict[str, Moeda] = {m.codigo: m for m in (
    _m("EUR", "€"), _m("USD", "$"), _m("GBP", "£"), _m("BRL", "R$"), _m("CAD", "$"), _m("AUD", "$"), _m("NZD", "$"), _m("CHF", "CHF"),
    _m("SEK", "kr"), _m("NOK", "kr"), _m("DKK", "kr"), _m("ISK", "kr", 0), _m("PLN", "zł"), _m("CZK", "Kč"), _m("HUF", "Ft", 0), _m("RON", "lei"),
    _m("RUB", "₽"), _m("UAH", "₴"), _m("TRY", "₺"), _m("CNY", "¥"), _m("JPY", "¥", 0), _m("KRW", "₩", 0), _m("INR", "₹"), _m("IDR", "Rp", 0), _m("VND", "₫", 0),
    _m("MXN", "$"), _m("ARS", "$"), _m("COP", "$", 0), _m("CLP", "$", 0), _m("PEN", "S/"), _m("UYU", "$"), _m("BOB", "Bs"),
    _m("AOA", "Kz"), _m("MZN", "MT"), _m("CVE", "CVE"), _m("STN", "Db"), _m("MOP", "MOP$"),
    _m("ZAR", "R"), _m("ILS", "₪"), _m("AED", "AED"), _m("HKD", "HK$"), _m("TWD", "NT$"), _m("SGD", "S$"), _m("MYR", "RM"), _m("PHP", "₱"),
)}

# País (ISO 3166-1 alfa-2) -> moeda. Os que não estão aqui ficam sem moeda sugerida (o utilizador escolhe da lista ou inventa uma).
PAIS_MOEDA: dict[str, str] = {
    **dict.fromkeys(("PT", "ES", "FR", "DE", "IT", "NL", "BE", "AT", "IE", "FI", "GR", "LU", "SK", "SI", "EE", "LV", "LT", "MT", "CY", "HR", "AD", "MC", "SM", "VA", "ME"), "EUR"),
    **dict.fromkeys(("US", "EC", "SV", "PR", "TL", "PA", "GU"), "USD"),
    "GB": "GBP", "BR": "BRL", "CA": "CAD", "AU": "AUD", "NZ": "NZD", "CH": "CHF", "LI": "CHF", "SE": "SEK", "NO": "NOK", "DK": "DKK", "IS": "ISK",
    "PL": "PLN", "CZ": "CZK", "HU": "HUF", "RO": "RON", "RU": "RUB", "UA": "UAH", "TR": "TRY", "CN": "CNY", "JP": "JPY", "KR": "KRW", "IN": "INR",
    "ID": "IDR", "VN": "VND", "MX": "MXN", "AR": "ARS", "CO": "COP", "CL": "CLP", "PE": "PEN", "UY": "UYU", "BO": "BOB",
    "AO": "AOA", "MZ": "MZN", "CV": "CVE", "ST": "STN", "MO": "MOP", "ZA": "ZAR", "IL": "ILS", "AE": "AED", "HK": "HKD", "TW": "TWD", "SG": "SGD", "MY": "MYR", "PH": "PHP",
}

# O país que cada língua do site sugere quando não há melhor (o browser afina com a região de `navigator.language`)
PAIS_DA_LINGUA = {
    "pt": "PT", "pt-br": "BR", "en": "US", "es": "ES", "fr": "FR", "de": "DE", "it": "IT", "nl": "NL", "pl": "PL", "sv": "SE", "cs": "CZ", "ro": "RO",
    "el": "GR", "ru": "RU", "tr": "TR", "zh": "CN", "ja": "JP", "ko": "KR", "hi": "IN", "ca": "ES", "uk": "UA", "id": "ID", "vi": "VN",
}


@dataclass(frozen=True)
class Convencao:
    """Como uma língua escreve um preço: separador decimal e de milhares, símbolo antes ou depois, e a partir de quantos algarismos se agrupam os milhares."""
    decimal: str
    milhares: str
    antes: bool
    espaco: bool
    agrupar_a_partir_de: int = 4


CONVENCOES: dict[str, Convencao] = {
    "pt": Convencao(",", " ", False, True, 5), "pt-br": Convencao(",", ".", True, True), "en": Convencao(".", ",", True, False),
    "es": Convencao(",", ".", False, True, 5), "fr": Convencao(",", " ", False, True), "de": Convencao(",", ".", False, True), "it": Convencao(",", ".", False, True),
    "nl": Convencao(",", ".", True, True), "pl": Convencao(",", " ", False, True, 5), "sv": Convencao(",", " ", False, True), "cs": Convencao(",", " ", False, True),
    "ro": Convencao(",", ".", False, True), "el": Convencao(",", ".", False, True), "ru": Convencao(",", " ", False, True), "tr": Convencao(",", ".", True, False),
    "zh": Convencao(".", ",", True, False), "ja": Convencao(".", ",", True, False), "ko": Convencao(".", ",", True, False), "hi": Convencao(".", ",", True, False),
    "ca": Convencao(",", ".", False, True), "uk": Convencao(",", " ", False, True), "id": Convencao(",", ".", True, False), "vi": Convencao(",", ".", False, True),
}
_PADRAO = CONVENCOES["en"]
_SO_O_PONTO_E_DECIMAL = {lg for lg, c in CONVENCOES.items() if c.decimal == "."}


class ErroMoeda(ValueError):
    """Um valor, uma moeda ou uma moeda inventada inválidos (a interface mostra `err_precario_*`)."""


def moeda_do_pais(pais: str) -> Moeda | None:
    """A moeda de um país (código de duas letras, em qualquer caixa); `None` se não a conhecemos."""
    codigo = PAIS_MOEDA.get((pais or "").strip().upper())
    return MOEDAS[codigo] if codigo else None


def pais_por_omissao(lingua: str) -> str:
    """O país que a língua sugere («pt-br» → «BR»); o inglês, se a língua for desconhecida."""
    return PAIS_DA_LINGUA.get(lingua, "US")


def moeda_por_omissao(lingua: str) -> Moeda:
    return moeda_do_pais(pais_por_omissao(lingua)) or MOEDAS["USD"]


def moeda_de_codigo(codigo: str) -> Moeda:
    try:
        return MOEDAS[(codigo or "").strip().upper()]
    except KeyError:
        raise ErroMoeda(f"moeda desconhecida: {codigo!r}") from None


def validar_inventada(m: MoedaInventada) -> MoedaInventada:
    """O nome tem de ter 1 a 14 letras (as do PDF, ver `core.letras`), sem algarismos nem controlos, e 0 a 2 casas."""
    from . import letras
    nome = " ".join(m.nome.split())
    if not nome or len(nome) > MAX_NOME_INVENTADA or any(c.isdigit() or ord(c) < 32 for c in nome) or m.decimais not in (0, 1, 2):
        raise ErroMoeda("moeda inventada inválida")
    if letras.em_falta(nome):
        raise ErroMoeda(f"sem letra para: {letras.em_falta(nome)}")
    return MoedaInventada(nome, bool(m.antes), m.decimais)


# ------------------------------------------------------------------ valores
def valor_de_texto(texto: str, lingua: str = "en") -> int | None:
    """O que a pessoa escreveu → milésimos («1,5» → 1500; «€ 1 234,50» → 1234500); `None` se não é um preço (vazio, letras, negativo).

    Com os dois separadores, o último é o decimal; só com um, depende da língua: «1.500» é 1500 em português e 1,5 em inglês.
    """
    t = re.sub(r"[^\d.,\s  '’-]", "", texto or "").replace(" ", " ").replace(" ", " ").strip()
    if not t or "-" in t or not re.search(r"\d", t):
        return None
    t = t.replace("'", "").replace("’", "").replace(" ", "")
    convencao = CONVENCOES.get(lingua, _PADRAO)
    if "," in t and "." in t:                              # os dois: o ultimo e o decimal, o outro agrupa os milhares
        ultimo = max(t.rfind(","), t.rfind("."))
        parte_inteira, fracao = re.sub(r"[.,]", "", t[:ultimo]), t[ultimo + 1:]
    elif "," in t or "." in t:
        sep = "," if "," in t else "."
        antes, _, depois = t.rpartition(sep)
        if t.count(sep) > 1 or (len(depois) == 3 and sep != convencao.decimal):     # «1.234.567» ou «1.500» (em português): milhares
            parte_inteira, fracao = t.replace(sep, ""), ""
        else:
            parte_inteira, fracao = antes, depois
    else:
        parte_inteira, fracao = t, ""
    if not parte_inteira.isdigit() and not (parte_inteira == "" and fracao.isdigit()):
        return None
    try:
        d = Decimal(f"{parte_inteira or '0'}.{fracao or '0'}")
    except InvalidOperation:
        return None
    mil = int((d * 1000).to_integral_value(ROUND_HALF_UP))
    return mil if 0 <= mil <= MAX_VALOR else None


def _arredondar(milesimos: int, decimais: int) -> int:
    """Em unidades da menor casa da moeda (centimos): meio para cima."""
    return int((Decimal(milesimos) / Decimal(10 ** (3 - decimais))).to_integral_value(ROUND_HALF_UP))


def numero(milesimos: int, decimais: int, lingua: str) -> str:
    """Só o número, como a língua o escreve («1 234,50», «1,234.50»)."""
    if not 0 <= milesimos <= MAX_VALOR:
        raise ErroMoeda("valor fora dos limites")
    c = CONVENCOES.get(lingua, _PADRAO)
    unidades = _arredondar(milesimos, decimais)
    inteira, fracao = divmod(unidades, 10 ** decimais) if decimais else (unidades, 0)
    texto = str(inteira)
    if len(texto) >= c.agrupar_a_partir_de:
        grupos = []
        while texto:
            grupos.insert(0, texto[-3:])
            texto = texto[:-3]
        texto = c.milhares.join(grupos)
    return texto + (c.decimal + str(fracao).zfill(decimais) if decimais else "")


def formatar(milesimos: int, moeda: Moeda | MoedaInventada, lingua: str) -> str:
    """O preço como se escreve na `lingua`: «1,50 €», «€1.50», «R$ 1,50», «1,50 zł», «3 fichas», «Rp1.500»."""
    c = CONVENCOES.get(lingua, _PADRAO)
    n = numero(milesimos, moeda.decimais, lingua)
    if isinstance(moeda, MoedaInventada):
        return f"{moeda.nome} {n}" if moeda.antes else f"{n} {moeda.nome}"
    if c.antes:
        return f"{moeda.simbolo}{' ' if c.espaco or len(moeda.simbolo) > 2 else ''}{n}"      # «R$ 1,50», «CHF 1.50», mas «€1.50» e «Rp1.500»
    return f"{n} {moeda.simbolo}"
