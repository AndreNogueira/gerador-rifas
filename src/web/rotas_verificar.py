"""M6: a pagina a que o QR de cada bilhete leva: confirma que o codigo foi emitido por este servico (assinatura HMAC), sem base de dados.

Uma pagina minima, sem JavaScript, na lingua do browser, que nunca se indexa nem se guarda em cache. Prova so a origem do codigo:
nao diz se o bilhete foi pago nem se ganhou (isso e de quem organiza a rifa). O endereco aceita `/V/` e `/v/`: o QR leva-o em maiusculas.
"""
from __future__ import annotations

import html

from core import i18n, qr
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from . import config
from .rotas import Servico, leve, servico

router = APIRouter(tags=["verificar"])

_CSS = ("body{font:16px/1.5 system-ui,sans-serif;margin:0;display:grid;place-items:center;min-height:100vh;background:#f3effe;color:#1d1240}"
        "main{max-width:30rem;margin:1rem;padding:1.5rem;border-radius:14px;background:#fff;box-shadow:0 6px 24px #0002}"
        "h1{margin:0 0 .5rem;font-size:1.3rem}.ok{color:#0a7a45}.mau{color:#b3261e}.suave{color:#6b6482;font-size:.9rem}p{margin:.5rem 0}")


def _pagina(lg: str, estado: str, linhas: list[str], aviso: str) -> HTMLResponse:
    cor = {"ok": "ok", "invalido": "mau", "indisponivel": "mau"}[estado]
    titulo = html.escape(i18n.traduzir("web_qr_titulo", lg))
    saida = (f'<!doctype html><html lang="{html.escape(lg)}"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">'
             '<meta name="referrer" content="no-referrer">'
             f"<title>{titulo}</title><style>{_CSS}</style></head><body><main><h1>{titulo}</h1>"
             f'<p class="{cor}"><strong>{html.escape(linhas[0])}</strong></p>{"".join(f"<p>{html.escape(x)}</p>" for x in linhas[1:])}'
             f'<p class="suave">{html.escape(aviso)}</p></main></body></html>')
    return HTMLResponse(saida, status_code=200 if estado == "ok" else 404,
                        headers={"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow", "Referrer-Policy": "no-referrer",
                                 "X-Content-Type-Options": "nosniff"})


@router.get("/v/{codigo}", include_in_schema=False, dependencies=[Depends(leve)])
@router.get("/V/{codigo}", include_in_schema=False, dependencies=[Depends(leve)])
def verificar(codigo: str, request: Request, serv: Servico = Depends(servico)) -> HTMLResponse:
    lg = i18n.lingua_de_accept_language(request.headers.get("accept-language"))
    chave = config.verificacao_chave()
    if not chave:
        serv.metricas.evento("verificacao", "indisponivel")
        return _pagina(lg, "indisponivel", [i18n.traduzir("err_qr_indisponivel", lg)], "")
    r = qr.verificar(chave.encode(), codigo)
    serv.metricas.evento("verificacao", "ok" if r else "invalido")
    aviso = i18n.traduzir("web_qr_aviso", lg)
    if r is None:
        return _pagina(lg, "invalido", [i18n.traduzir("web_qr_invalido", lg)], aviso)
    evento, serie, numero = r
    linhas = [i18n.traduzir("web_qr_valido", lg), i18n.traduzir("web_qr_bilhete", lg, numero=f"{serie}{numero}")]
    if evento:
        linhas.append(i18n.traduzir("web_qr_rifa", lg, evento=evento))
    return _pagina(lg, "ok", linhas, aviso)
