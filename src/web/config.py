"""Configuracao da webapp: tudo por variaveis de ambiente (nada de caminhos nem segredos no codigo).

O servico e PUBLICO e sem palavra-passe: os limites abaixo sao a defesa contra abuso (a instancia gratuita do Render tem 512 MB).
"""
from __future__ import annotations

import os
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]            # raiz do repositorio (ou /repo no contentor)


def _inteiro(nome: str, por_defeito: int) -> int:
    try:
        v = int(os.environ.get(nome, "").strip())
        return v if v > 0 else por_defeito
    except ValueError:
        return por_defeito


def porta() -> int:
    """Porta onde ouvir: variavel PORT (por omissao 8080; o Render define-a)."""
    return _inteiro("PORT", 8080)


def host() -> str:
    """127.0.0.1 por omissao (so este computador); num contentor define-se HOST=0.0.0.0."""
    return os.environ.get("HOST", "").strip() or "127.0.0.1"


def pasta_frontend() -> Path:
    """Onde esta o frontend compilado (`pnpm build` -> src/web/frontend/dist). RIFAS_FRONTEND troca-o."""
    env = os.environ.get("RIFAS_FRONTEND", "").strip()
    return Path(env) if env else Path(__file__).resolve().parent / "frontend" / "dist"


def pasta_assets() -> Path:
    """Imagens do tutorial e videos (por omissao app/assets, que a app Windows tambem usa). RIFAS_ASSETS troca-a."""
    env = os.environ.get("RIFAS_ASSETS", "").strip()
    return Path(env) if env else RAIZ / "app" / "assets"


def limite_upload_mb() -> int:
    """Tamanho maximo de cada ficheiro carregado (template, algarismos). MAX_UPLOAD_MB."""
    return _inteiro("MAX_UPLOAD_MB", 25)


def max_numeros() -> int:
    """Quantos numeros, no maximo, num pedido de geracao. MAX_NUMEROS. Medido com 512 MB e 0.1 CPU (a instancia gratuita do Render):
    5 000 numeros ~ 25 s, 20 000 ~ 85 s, 100 000 varios minutos a ocupar o unico motor; por isso 30 000 por defeito."""
    return _inteiro("MAX_NUMEROS", 30_000)


def validade_min() -> int:
    """Minutos sem atividade ate uma sessao e os seus ficheiros serem apagados. JOB_TTL_MIN."""
    return _inteiro("JOB_TTL_MIN", 30)


def tempo_maximo_geracao_min() -> int:
    """Passado este tempo a geracao e interrompida (o processo do motor e morto e recriado). JOB_MAX_MIN."""
    return _inteiro("JOB_MAX_MIN", 10)


def max_sessoes() -> int:
    """Sessoes ativas ao mesmo tempo (cada uma tem uma pasta em disco). MAX_SESSOES."""
    return _inteiro("MAX_SESSOES", 200)


def limite_sessao_mb() -> int:
    """Espaco maximo em disco por sessao (uploads + PDFs gerados). RIFAS_LIMITE_SESSAO_MB."""
    return _inteiro("RIFAS_LIMITE_SESSAO_MB", 300)


def pedidos_pesados_por_min() -> int:
    """Uploads, pre-visualizacoes e geracoes por minuto e por IP. RATE_PESADOS_POR_MIN."""
    return _inteiro("RATE_PESADOS_POR_MIN", 30)


def pedidos_leves_por_min() -> int:
    """Os restantes pedidos que alteram estado (calculos do formulario, cancelar...) por minuto e por IP. RATE_LEVES_POR_MIN."""
    return _inteiro("RATE_LEVES_POR_MIN", 300)


def proxies_de_confianca() -> str:
    """De onde se aceita o cabecalho X-Forwarded-For (IPs ou redes, separados por virgulas). FORWARDED_ALLOW_IPS."""
    return os.environ.get("FORWARDED_ALLOW_IPS", "").strip() or "127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"


def espera_cancelar_s() -> float:
    """Segundos que o motor tem para parar sozinho depois de «Cancelar»; passados eles, o processo do motor e morto e recriado
    (as fases de gravar e verificar o PDF nao consultam o cancelamento). CANCELAR_ESPERA_S (0 = matar logo)."""
    try:
        return max(0.0, float(os.environ.get("CANCELAR_ESPERA_S", "3")))
    except ValueError:
        return 3.0


def url_publica() -> str:
    """O URL publico do site (sem barra final), para o canonico, o Open Graph e o sitemap. PUBLIC_URL; no Render, o RENDER_EXTERNAL_URL
    que o proprio Render define serve de reserva. Vazio = usar o do pedido (so em desenvolvimento)."""
    for nome in ("PUBLIC_URL", "RENDER_EXTERNAL_URL"):
        v = os.environ.get(nome, "").strip().rstrip("/")
        if re.fullmatch(r"https?://[A-Za-z0-9.\-]+(:\d+)?", v):
            return v
    return ""


def donativo_url() -> str:
    """Ligacao para donativos (MB Way, PayPal, Ko-fi...): DONATIVO_URL. So `https://` (outra coisa ignora-se); vazio = sem botao."""
    v = os.environ.get("DONATIVO_URL", "").strip()
    return v if re.fullmatch(r"https://[^\s<>\"']{4,300}", v) else ""


def contacto_email() -> str:
    """E-mail publico de contacto: CONTACTO_EMAIL (nada no repositorio). Invalido ou vazio = sem contacto publico."""
    v = os.environ.get("CONTACTO_EMAIL", "").strip()
    return v if re.fullmatch(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,24}", v) else ""


def responsavel() -> str:
    """Nome de quem responde pelo servico (nas paginas Termos e Privacidade): RESPONSAVEL. Sem texto HTML nem quebras de linha."""
    return re.sub(r"[<>\r\n]", "", os.environ.get("RESPONSAVEL", "")).strip()[:100]


def admin_token() -> str:
    """A palavra-passe do painel de administracao (variavel ADMIN_TOKEN, no Render em Environment; NUNCA no repositorio). Vazia, ou com
    menos de 12 caracteres, o painel nao existe (404)."""
    t = os.environ.get("ADMIN_TOKEN", "").strip()
    return t if len(t) >= 12 else ""


def metricas_efemeras() -> bool:
    """Se as metricas se perdem quando o servico reinicia: no Render (variavel RENDER) o disco e efemero, a menos que o dono diga onde
    fica um disco persistente (RIFAS_METRICAS)."""
    return bool(os.environ.get("RENDER")) and not os.environ.get("RIFAS_METRICAS", "").strip()


def manter_acordado() -> tuple[str, float]:
    """(URL a chamar, segundos entre chamadas) para o servico nao adormecer por inatividade; ("", 0) se desligado.
    No Render gratuito o servico adormece apos 15 min sem pedidos que venham de fora: o proprio servico chama-se a si (pelo URL
    publico, que passa pelo proxy do Render) de 10 em 10 min. KEEPALIVE=0 desliga; KEEPALIVE_URL define outro URL;
    KEEPALIVE_MIN muda o intervalo (1 a 14). Fora do Render nao faz nada, a nao ser que se defina KEEPALIVE_URL."""
    if os.environ.get("KEEPALIVE", "").strip().lower() in ("0", "nao", "não", "false", "off"):
        return "", 0.0
    url = ""
    for nome in ("KEEPALIVE_URL", "RENDER_EXTERNAL_URL"):
        v = os.environ.get(nome, "").strip().rstrip("/")
        if re.fullmatch(r"https?://[A-Za-z0-9.\-]+(:\d+)?", v):
            url = v
            break
    if not url:
        return "", 0.0
    try:
        minutos = min(14.0, max(1.0, float(os.environ.get("KEEPALIVE_MIN", "10"))))
    except ValueError:
        minutos = 10.0
    return url, minutos * 60
