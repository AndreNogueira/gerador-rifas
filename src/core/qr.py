"""M6: um QR em cada bilhete que leva a uma pagina que confirma que o codigo foi emitido por este servico, SEM base de dados.

O codigo do bilhete assina-se (HMAC-SHA256 com uma chave so do servidor, `VERIFICACAO_CHAVE`) e leva tudo o que mostra:
    https://<site>/V/<evento.serie.numero em base32>.<assinatura em base32>
Tudo em MAIUSCULAS (base32 so tem A-Z e 2-7, e o endereco aceita-se em maiusculas): o QR usa o modo alfanumerico, que e ~40 % mais
pequeno, e por isso lê-se melhor num bilhete pequeno. Verificar = recalcular a assinatura (nao ha nada guardado). Isto prova que o codigo
saiu deste servico para aquele bilhete; NAO prova que foi pago nem que ganhou.
O QR desenha-se em vetor (quadrados no PDF) num canto de cada rifa, como o logotipo: so em modo folha (template de uma rifa).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import re
from dataclasses import dataclass

POSICOES = ("se", "sd", "ie", "id")
TAMANHO_MIN, TAMANHO_MAX, TAMANHO_PADRAO = 20, 40, 28           # lado do QR em % da altura da rifa
_EVENTO_OK = re.compile(r"[A-Za-z0-9 \-]{0,16}")
_SERIE_OK = re.compile(r"[A-Za-z .\-/]{0,6}")
_NUMERO_OK = re.compile(r"[0-9]{1,12}")
_SEP = "|"


@dataclass(frozen=True)
class Qr:
    base: str                  # o endereco publico do site, sem barra final (https://...)
    chave: bytes
    evento: str = ""           # o nome curto da rifa (so letras, numeros, espacos e hifen; ate 16)
    posicao: str = "ie"
    tamanho: int = TAMANHO_PADRAO


def evento_limpo(nome: str) -> str:
    """O nome da rifa reduzido ao que o QR aceita: ASCII (letras, numeros, espaco, hifen), ate 16 caracteres."""
    ascii_ = "".join(c for c in nome if c.isascii() and (c.isalnum() or c in " -"))
    return " ".join(ascii_.split())[:16].strip()


def _b32(dados: bytes) -> str:
    return base64.b32encode(dados).decode("ascii").rstrip("=")


def _de_b32(texto: str) -> bytes:
    return base64.b32decode(texto + "=" * (-len(texto) % 8), casefold=True)


def _assinar(chave: bytes, payload: bytes) -> str:
    return _b32(hmac.new(chave, payload, hashlib.sha256).digest()[:10])           # 80 bits: de sobra para impedir falsificacoes


def codigo(chave: bytes, evento: str, serie: str, numero: str) -> str:
    """O codigo de um bilhete: «<payload em base32>.<assinatura em base32>» (so A-Z, 2-7 e o ponto)."""
    payload = _SEP.join((evento_limpo(evento), serie, numero)).encode("ascii")
    return f"{_b32(payload)}.{_assinar(chave, payload)}"


def verificar(chave: bytes, texto: str) -> tuple | None:
    """(evento, serie, numero) se o codigo foi emitido com esta chave e nao foi alterado; senao None. Nunca levanta."""
    try:
        parte, _, assinatura = texto.strip().partition(".")
        if not parte or not assinatura or len(texto) > 120:
            return None
        payload = _de_b32(parte)
        if not hmac.compare_digest(_assinar(chave, payload).encode(), assinatura.upper().encode()):
            return None
        evento, serie, numero = payload.decode("ascii").split(_SEP)
        if not (_EVENTO_OK.fullmatch(evento) and _SERIE_OK.fullmatch(serie) and _NUMERO_OK.fullmatch(numero)):
            return None
        return evento, serie, numero
    except Exception:  # noqa: BLE001 - lixo vindo de fora: simplesmente nao e valido
        return None


def url(qr: Qr, serie: str, numero: str) -> str:
    """O endereco que o QR leva, em maiusculas (modo alfanumerico do QR)."""
    return f"{qr.base}/V/{codigo(qr.chave, qr.evento, serie, numero)}".upper()


def modulos(texto: str) -> list:
    """A matriz do QR (True = quadrado escuro), correcao de erros L. O `segno` so se importa aqui."""
    import segno
    # mask fixa: sem ela o segno avalia as 8 mascaras (4,5 ms por QR; com 30 000 bilhetes sao minutos). Qualquer mascara e valida.
    return [[bool(c) for c in linha] for linha in segno.make(texto, error="l", micro=False, mask=3).matrix]


def ops_pdf(matriz: list, x: float, y: float, lado: float, silencio: int = 3) -> str:
    """Operadores PDF que desenham o QR com o canto inferior esquerdo em (x, y) e `lado` pt de lado: um fundo branco (a zona de
    silencio, para ler-se sobre qualquer template) e os quadrados escuros em faixas horizontais."""
    n = len(matriz)
    m = lado / (n + 2 * silencio)
    f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".") if v else "0"       # noqa: E731
    ops = [f"q 1 g {f(x)} {f(y)} {f(lado)} {f(lado)} re f 0 g"]
    for r, linha in enumerate(matriz):
        yy = y + lado - (silencio + r + 1) * m
        c = 0
        while c < n:
            if linha[c]:
                fim = c
                while fim + 1 < n and linha[fim + 1]:
                    fim += 1
                ops.append(f"{f(x + (silencio + c) * m)} {f(yy)} {f((fim - c + 1) * m)} {f(m)} re")
                c = fim + 1
            else:
                c += 1
    ops.append("f Q\n")
    return "\n".join(ops)
