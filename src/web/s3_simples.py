"""Gravar um ficheiro num armazenamento S3 (o Neon Object Storage) com uma assinatura SigV4 feita à mão e só `urllib`: sem `boto3` (pesada) na imagem do serviço.

Só faz o que as cópias de segurança precisam: um `PUT` de um objeto, com endereços «path-style» (`<endpoint>/<bucket>/<chave>`), que é o que o Neon exige. A chave e o segredo nunca vão para um
log nem para uma mensagem de erro: só a classe da exceção e o código HTTP.
"""
from __future__ import annotations

import hashlib
import hmac
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

VAZIO_SHA256 = hashlib.sha256(b"").hexdigest()


class ErroS3(Exception):
    """O armazenamento recusou ou não respondeu (a mensagem tem só a classe do erro e o código HTTP)."""


def _hmac(chave: bytes, texto: str) -> bytes:
    return hmac.new(chave, texto.encode("utf-8"), hashlib.sha256).digest()


def assinar(metodo: str, host: str, caminho: str, consulta: str, extra: dict[str, str], corpo_sha256: str, regiao: str, id_chave: str, segredo: str,
            agora: datetime) -> dict[str, str]:
    """Os cabeçalhos (em minúsculas) de um pedido S3 assinado com a SigV4: `host`, `x-amz-content-sha256`, `x-amz-date`, os `extra` e `authorization`."""
    amz = agora.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dia = amz[:8]
    cab = {"host": host, "x-amz-content-sha256": corpo_sha256, "x-amz-date": amz, **{k.lower(): " ".join(v.split()) for k, v in extra.items()}}
    nomes = sorted(cab)
    assinados = ";".join(nomes)
    canonico = "\n".join([metodo, urllib.parse.quote(caminho, safe="/-_.~"), consulta, "".join(f"{k}:{cab[k]}\n" for k in nomes), assinados, corpo_sha256])
    escopo = f"{dia}/{regiao}/s3/aws4_request"
    a_assinar = "\n".join(["AWS4-HMAC-SHA256", amz, escopo, hashlib.sha256(canonico.encode("utf-8")).hexdigest()])
    k = _hmac(_hmac(_hmac(_hmac(("AWS4" + segredo).encode("utf-8"), dia), regiao), "s3"), "aws4_request")
    cab["authorization"] = f"AWS4-HMAC-SHA256 Credential={id_chave}/{escopo}, SignedHeaders={assinados}, Signature={hmac.new(k, a_assinar.encode('utf-8'), hashlib.sha256).hexdigest()}"
    return cab


def gravar(endpoint: str, regiao: str, bucket: str, chave: str, corpo: bytes, id_chave: str, segredo: str, tipo: str = "application/octet-stream",
           agora: datetime | None = None, abrir=urllib.request.urlopen) -> int:
    """Grava `corpo` em `<endpoint>/<bucket>/<chave>` e devolve o código HTTP (2xx). `abrir` só se troca nos testes."""
    url = urllib.parse.urlsplit(endpoint.rstrip("/"))
    if url.scheme != "https" or not url.netloc:
        raise ErroS3("endpoint_invalido")
    caminho = f"{url.path}/{bucket}/{chave}"
    cab = assinar("PUT", url.netloc, caminho, "", {"content-type": tipo}, hashlib.sha256(corpo).hexdigest(), regiao, id_chave, segredo, agora or datetime.now(timezone.utc))
    pedido = urllib.request.Request(f"https://{url.netloc}{urllib.parse.quote(caminho, safe='/-_.~')}", data=corpo, method="PUT",
                                    headers={k: v for k, v in cab.items() if k != "host"})
    try:
        with abrir(pedido, timeout=60) as r:
            return int(getattr(r, "status", 200))
    except urllib.error.HTTPError as e:
        raise ErroS3(f"HTTP {e.code}") from None
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise ErroS3(type(e).__name__) from None
