"""Guardar e abrir o pedido num ficheiro (app Windows 2.6; no site é «Copiar ligação»): os valores do formulário e das opções «Extras», em JSON.

Nunca leva o template, o ficheiro dos algarismos, a pasta de destino nem o logótipo (são caminhos do computador de quem guarda e o template nunca se
guarda); leva o resto: números, modo, papel, margem, nome dos ficheiros, séries, números a saltar, cores, marcas de corte e canto/tamanho do logótipo.
Ao abrir, o que não se conhece ignora-se e cada valor é validado (tipo, tamanho, forma), de modo que um ficheiro alterado à mão não estraga a app.
"""
from __future__ import annotations

import json
import re

from . import marca
from .motor import PAPEIS, ErroRifas

FORMATO = "gerador-de-rifas-pedido"
VERSAO = 1
MAX_BYTES = 20_000
EXTENSAO = ".rifas"

_NUM = re.compile(r"\d{1,9}")
_COR = re.compile(r"#[0-9a-fA-F]{6}")
_MODOS = ("varios", "unico")
_PAPEIS = tuple(PAPEIS)


def _texto(maximo: int):
    return lambda v: isinstance(v, str) and len(v) <= maximo and "\x00" not in v


CAMPOS = {                       # campo -> validação (True se o valor serve)
    "inicio": lambda v: isinstance(v, str) and bool(_NUM.fullmatch(v)),
    "fim": lambda v: isinstance(v, str) and bool(_NUM.fullmatch(v)),
    "digitos": lambda v: isinstance(v, str) and bool(_NUM.fullmatch(v)),
    "max_ficheiro": lambda v: isinstance(v, str) and bool(_NUM.fullmatch(v)),
    "modo": lambda v: v in _MODOS,
    "papel": lambda v: v in _PAPEIS,
    "margem": lambda v: isinstance(v, str) and bool(re.fullmatch(r"\d{1,3}([.,]\d{1,2})?", v)),
    "porfolha": lambda v: isinstance(v, str) and (v == "" or bool(_NUM.fullmatch(v))),
    "nome": _texto(120),
    "prefixos": _texto(80),
    "saltar": _texto(400),
    "cor_serie": lambda v: isinstance(v, bool),
    "marcas": lambda v: isinstance(v, bool),
    "cor_numeros": lambda v: isinstance(v, str) and (v == "" or bool(_COR.fullmatch(v))),
    "logo_pos": lambda v: v in marca.POSICOES,
    "logo_tam": lambda v: isinstance(v, str) and bool(_NUM.fullmatch(v)),
}


def para_bytes(campos: dict) -> bytes:
    """O ficheiro (UTF-8) com os `campos` que se conhecem e servem; o resto fica de fora."""
    uteis = {k: v for k, v in campos.items() if k in CAMPOS and CAMPOS[k](v)}
    return (json.dumps({"formato": FORMATO, "versao": VERSAO, "campos": uteis}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def de_bytes(dados: bytes) -> dict:
    """Os campos de um ficheiro de pedido. `err_pedido_ficheiro` se não é um ficheiro nosso (ou é grande demais ou está estragado)."""
    if not isinstance(dados, (bytes, bytearray)) or len(dados) > MAX_BYTES:
        raise ErroRifas("err_pedido_ficheiro")
    try:
        d = json.loads(bytes(dados).decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        raise ErroRifas("err_pedido_ficheiro") from None
    if not isinstance(d, dict) or d.get("formato") != FORMATO or not isinstance(d.get("campos"), dict):
        raise ErroRifas("err_pedido_ficheiro")
    campos = {k: v for k, v in d["campos"].items() if k in CAMPOS and CAMPOS[k](v)}
    if not campos:
        raise ErroRifas("err_pedido_ficheiro")
    if "margem" in campos:
        campos["margem"] = campos["margem"].replace(",", ".")
    return campos
