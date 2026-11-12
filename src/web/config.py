"""Configuracao da webapp: tudo por variaveis de ambiente (nada de caminhos nem segredos no codigo).

O servico e PUBLICO e sem palavra-passe: os limites abaixo sao a defesa contra abuso (a instancia gratuita do Render tem 512 MB).
"""
from __future__ import annotations

import os
import re
import tempfile
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


def assets_zip_url() -> str:
    """O `.zip` com as imagens e os videos do site, no armazenamento de objetos (`scripts/publicar_assets.py`): ASSETS_URL. So https e a acabar em `.zip`.
    Com ele a imagem Docker nao leva os ficheiros: o servidor descarrega-os no arranque (`assets_remotos.py`). Sem ele usa os de `app/assets`."""
    v = os.environ.get("ASSETS_URL", "").strip()
    return v if re.fullmatch(r"https://[^\s<>\"']{8,400}\.zip", v) else ""


def assets_sha256() -> str:
    """O SHA-256 do `.zip` (ASSETS_SHA256), para o servidor so aceitar exatamente esse ficheiro. Vazio = nao verifica (so se confia no URL)."""
    v = os.environ.get("ASSETS_SHA256", "").strip().lower()
    return v if re.fullmatch(r"[0-9a-f]{64}", v) else ""


def pasta_assets() -> Path:
    """Imagens do tutorial e videos: `RIFAS_ASSETS` se estiver definida; senao, com `ASSETS_URL`, a pasta temporaria onde o servidor as extrai
    (`assets_remotos.py`); senao `app/assets`, que a app Windows tambem usa."""
    env = os.environ.get("RIFAS_ASSETS", "").strip()
    if env:
        return Path(env)
    if assets_zip_url():
        return Path(tempfile.gettempdir()) / "rifas-assets"
    return RAIZ / "app" / "assets"


def limite_upload_mb() -> int:
    """Tamanho maximo de cada ficheiro carregado (template, algarismos). MAX_UPLOAD_MB."""
    return _inteiro("MAX_UPLOAD_MB", 25)


def max_numeros() -> int:
    """Quantos numeros, no maximo, num pedido de geracao. MAX_NUMEROS. Medido com 512 MB e 0.1 CPU (a instancia gratuita do Render):
    5 000 numeros ~ 25 s, 20 000 ~ 85 s, 100 000 varios minutos a ocupar o unico motor; por isso 30 000 por defeito."""
    return _inteiro("MAX_NUMEROS", 30_000)


def max_numeros_qr() -> int:
    """Quantos numeros, no maximo, num pedido COM QR (MAX_NUMEROS_QR): cada QR custa ~1 ms de CPU e ~600 bytes de PDF, o que num pedido de
    30 000 numeros na instancia gratuita passaria o tempo maximo da geracao. 10 000 por defeito."""
    return _inteiro("MAX_NUMEROS_QR", 10_000)


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


def adsense_cliente() -> str:
    """O identificador de editor da Google AdSense (`ca-pub-` e 10 a 20 algarismos): ADSENSE_CLIENTE. Publico por natureza (vai no HTML e no `ads.txt`),
    mas nao se poe no repositorio. Vazio ou invalido = **sem anuncios** (nada se carrega da Google). Ver `docs/ADSENSE.md`."""
    v = os.environ.get("ADSENSE_CLIENTE", "").strip()
    return v if re.fullmatch(r"ca-pub-\d{10,20}", v) else ""


def adsense_slot() -> str:
    """O bloco de anuncios (so os algarismos do `data-ad-slot`): ADSENSE_SLOT. Sem ele a pagina carrega o script da Google (verificacao do site e mensagem de
    consentimento) mas nao mostra nenhum bloco. Sem `ADSENSE_CLIENTE` nao vale."""
    v = os.environ.get("ADSENSE_SLOT", "").strip()
    return v if adsense_cliente() and re.fullmatch(r"\d{6,20}", v) else ""


def google_verificacao() -> str:
    """O codigo de verificacao do Google Search Console (so o valor do `content` da etiqueta `google-site-verification`): GOOGLE_VERIFICACAO.
    E publico por natureza (vai no HTML da pagina inicial), mas nao se poe no repositorio. Invalido ou vazio = sem etiqueta."""
    v = os.environ.get("GOOGLE_VERIFICACAO", "").strip()
    return v if re.fullmatch(r"[A-Za-z0-9_\-]{20,120}", v) else ""


def contacto_email() -> str:
    """E-mail publico de contacto: CONTACTO_EMAIL (nada no repositorio). Invalido ou vazio = sem contacto publico."""
    v = os.environ.get("CONTACTO_EMAIL", "").strip()
    return v if re.fullmatch(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,24}", v) else ""


def verificacao_chave() -> str:
    """A chave que assina os codigos dos QR dos bilhetes: VERIFICACAO_CHAVE (so no Render; pelo menos 16 caracteres). Sem ela nao ha QR
    (nao se assinaria nada) e a pagina de verificacao diz que nao esta disponivel. NUNCA no repositorio."""
    v = os.environ.get("VERIFICACAO_CHAVE", "").strip()
    return v if len(v) >= 16 else ""


def responsavel() -> str:
    """Nome de quem responde pelo servico (nas paginas Termos e Privacidade): RESPONSAVEL. Sem texto HTML nem quebras de linha."""
    return re.sub(r"[<>\r\n]", "", os.environ.get("RESPONSAVEL", "")).strip()[:100]


def admin_token() -> str:
    """A palavra-passe do painel de administracao (variavel ADMIN_TOKEN, no Render em Environment; NUNCA no repositorio). Vazia, ou com
    menos de 12 caracteres, o painel nao existe (404)."""
    t = os.environ.get("ADMIN_TOKEN", "").strip()
    return t if len(t) >= 12 else ""


def database_url() -> str:
    """O endereco da base Postgres (Neon, Supabase...): DATABASE_URL, so no Render (leva a palavra-passe: NUNCA no repositorio, num log ou no
    painel). So `postgres://` ou `postgresql://`; outra coisa ignora-se. Vazio = SQLite local, como sempre."""
    v = os.environ.get("DATABASE_URL", "").strip()
    return v if re.fullmatch(r"postgres(ql)?://[^\s]{6,500}", v) else ""


def metricas_bd_min() -> float:
    """De quantos em quantos minutos as metricas vao para a base Postgres (METRICAS_BD_MIN, 1 a 720; 60 por omissao). Quanto mais perto de 5,
    menos a computacao do Neon suspende (o plano gratuito tem horas limitadas); quanto maior, mais se perde se o servico for morto sem avisar."""
    try:
        return min(720.0, max(1.0, float(os.environ.get("METRICAS_BD_MIN", "60"))))
    except ValueError:
        return 60.0


def metricas_efemeras() -> bool:
    """Se as metricas se perdem quando o servico reinicia: no Render (variavel RENDER) o disco e efemero, a menos que o dono diga onde
    fica um disco persistente (RIFAS_METRICAS)."""
    return bool(os.environ.get("RENDER")) and not os.environ.get("RIFAS_METRICAS", "").strip() and not database_url()


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
