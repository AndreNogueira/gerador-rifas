"""IndexNow: uma vez por versão, avisa o Bing, o Yandex, o Seznam e o Naver (o Google não o usa) de que as páginas do site mudaram, para as voltarem a ler já.

- **Sem segredos e sem passos manuais.** A «chave» do IndexNow não é secreta (tem de estar num ficheiro público do próprio site, `/<chave>.txt`, que prova que o site é nosso):
  deriva-se do endereço público (`chave`), por isso não há variável nova no Render. `INDEXNOW=0` desliga; sem `INDEXNOW`, só liga no Render (`RENDER=true`) e com `PUBLIC_URL`
  ou `RENDER_EXTERNAL_URL` definidos (nos testes e em casa nunca sai nada para a rede).
- **Uma vez por versão** (`indexnow:<versao>` na tabela `relatorios`, como as outras reservas): um reinício, um acordar do Render ou dois arranques sobrepostos não repetem o aviso.
  Depois de tratada a versão a ronda de 5 minutos já não consulta a base (o Neon gratuito pode adormecer: `tests/test_web_sem_consultas.py`).
- **O que se envia:** só os endereços públicos do sitemap (cada página × cada língua) e o endereço do ficheiro da chave. Nada de visitantes, de textos nem de números.
- Se falha, solta-se a reserva e tenta-se de hora a hora, no máximo 3 vezes por versão; os erros ficam em `EstadoIndexNow` (memória) e nunca derrubam o servidor.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlsplit

from core import i18n

from . import seo
from .relatorio import RelatoriosEnviados

ENDERECO = "https://api.indexnow.org/indexnow"
MAX_TENTATIVAS = 3
ESPERA_ENTRE_TENTATIVAS_S = 3600.0
LIMITE_URLS = 10_000                                         # o máximo do protocolo por pedido


@dataclass
class EstadoIndexNow:
    """O que já se decidiu nesta execução (em memória): sem isto cada ronda de 5 minutos voltava à base."""
    versao_tratada: str = ""
    tentativas: int = 0
    proxima_tentativa: float = 0.0
    ultimo_erro: str = ""
    enviados: int = 0                                       # quantos endereços seguiram da última vez


def ligado(base: str) -> bool:
    """`INDEXNOW=0` desliga e `INDEXNOW=1` força; por omissão só no Render e com um endereço público a sério (nunca em localhost)."""
    v = os.environ.get("INDEXNOW", "").strip().lower()
    if v in ("0", "false", "nao", "não"):
        return False
    host = urlsplit(base).hostname or ""
    if not base.startswith("https://") or host in ("", "localhost") or host.endswith(".local") or host.replace(".", "").isdigit():
        return False
    return v in ("1", "true", "sim") or os.environ.get("RENDER", "").strip().lower() == "true"


def chave(base: str) -> str:
    """A chave do IndexNow (8 a 128 letras, algarismos ou «-»): 32 algarismos hexadecimais derivados do endereço público. Não é um segredo."""
    return hashlib.sha256(f"indexnow:{base}".encode()).hexdigest()[:32]


def urls(base: str) -> list[str]:
    """Os endereços do sitemap (só páginas indexáveis, em todas as línguas), sem repetições, na ordem do sitemap."""
    vistos: dict[str, None] = {}
    for p in seo.ROTAS.values():
        if p.indexavel and p.no_mapa:
            for lg in i18n.LINGUAS:
                vistos[seo._url(base, p.caminho, lg)] = None
    return list(vistos)[:LIMITE_URLS]


def corpo(base: str) -> dict:
    return {"host": urlsplit(base).netloc, "key": chave(base), "keyLocation": f"{base}/{chave(base)}.txt", "urlList": urls(base)}


def _enviar(base: str, abrir) -> int:
    pedido = urllib.request.Request(ENDERECO, data=json.dumps(corpo(base)).encode("utf-8"), method="POST",
                                    headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "gerador-rifas-indexnow"})
    with abrir(pedido, timeout=20) as r:
        return int(r.status)


def enviar_se_devido(relatorios: RelatoriosEnviados, versao: str, base: str, estado: EstadoIndexNow, agora: float | None = None, abrir=urllib.request.urlopen) -> str:
    """Uma ronda: devolve `desligado`, `ja_tratado`, `espera`, `reservado` (outro arranque já o fez), `enviado` ou `erro`."""
    agora = time.time() if agora is None else agora
    if not base or not ligado(base):
        return "desligado"
    if estado.versao_tratada == versao:
        return "ja_tratado"
    if agora < estado.proxima_tentativa:
        return "espera"
    reserva = f"indexnow:{versao}"
    if not relatorios.reservar(reserva, agora):
        estado.versao_tratada = versao                       # já avisado por outra execução desta versão: não volta a perguntar
        return "reservado"
    try:
        codigo = _enviar(base, abrir)
        if codigo not in (200, 202):
            raise RuntimeError(f"HTTP {codigo}")
    except urllib.error.HTTPError as e:
        return _falhou(relatorios, reserva, estado, agora, f"HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - uma falha de rede nunca derruba o ciclo; nova tentativa daqui a uma hora
        return _falhou(relatorios, reserva, estado, agora, type(e).__name__ if not isinstance(e, RuntimeError) else str(e))
    estado.versao_tratada, estado.enviados, estado.ultimo_erro = versao, len(urls(base)), ""
    return "enviado"


def _falhou(relatorios: RelatoriosEnviados, reserva: str, estado: EstadoIndexNow, agora: float, motivo: str) -> str:
    estado.tentativas += 1
    estado.ultimo_erro = motivo
    if estado.tentativas >= MAX_TENTATIVAS:
        estado.versao_tratada = reserva.split(":", 1)[1]    # desiste desta versão (a reserva fica: nenhuma outra execução insiste)
    else:
        relatorios.libertar(reserva)
        estado.proxima_tentativa = agora + ESPERA_ENTRE_TENTATIVAS_S
    return "erro"
