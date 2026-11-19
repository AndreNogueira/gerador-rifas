"""Enviar um e-mail por uma API HTTPS (Resend): o relatório diário (`relatorio.py`).

Porquê HTTPS e não SMTP: o Render gratuito bloqueia as portas de saída do SMTP (25, 465 e 587).

SEGURANÇA
 - A chave (`RESEND_API_KEY`) vive só nas variáveis do Render: nunca no código, num log nem numa resposta.
 - Um erro da API nunca sai tal e qual (pode trazer o endereço do destinatário): só a classe da exceção e o código HTTP.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

API = "https://api.resend.com/emails"


class ErroEmail(Exception):
    """O envio falhou (a mensagem tem só a classe do erro e o código HTTP, nunca a chave nem os endereços)."""


def enviar(chave: str, de: str, para: list[str], assunto: str, html: str, texto: str, abrir=urllib.request.urlopen) -> str:
    """Envia o e-mail (HTML + texto simples) e devolve o id que a API deu. `abrir` só se troca nos testes."""
    if not chave or not para:
        raise ErroEmail("sem_configuracao")
    pedido = urllib.request.Request(
        API, method="POST",
        data=json.dumps({"from": de, "to": para, "subject": assunto, "html": html, "text": texto}).encode("utf-8"),
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json", "User-Agent": "gerador-rifas-relatorio"})
    try:
        with abrir(pedido, timeout=20) as r:
            return str(json.loads(r.read().decode("utf-8")).get("id", ""))
    except urllib.error.HTTPError as e:
        raise ErroEmail(f"HTTP {e.code}") from None
    except (urllib.error.URLError, OSError, ValueError, TypeError, AttributeError) as e:
        raise ErroEmail(type(e).__name__) from None
