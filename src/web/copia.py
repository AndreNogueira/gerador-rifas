"""A cópia de segurança semanal dos dados que NÃO se refazem, para o armazenamento de objetos do Neon (S3), e o restauro.

O QUE VAI NA CÓPIA (só com `DATABASE_URL`, tudo na mesma base): `historico_diario` (o único registo que não se refaz: os eventos brutos duram 90 dias), `objetivos`, `auditoria`,
`comentarios`, `seo_textos_bd` (os textos de SEO editados) e `api_chaves` (só os SHA-256 das chaves da API, nunca as chaves). Cada tabela leva as colunas e as linhas. Fica num ficheiro
`.json.gz`; os eventos, pedidos e amostras do sistema ficam de fora (são volumosos e já têm o seu prazo).

QUANDO: na segunda-feira depois das 00:05 (hora do `RELATORIO_FUSO`), ou quando o serviço acordar se dormia; a reserva da semana (`backup:<segunda-feira>`) está na tabela `relatorios`, por
isso um arranque novo não a repete. Cada cópia vai para uma de **8 posições rotativas** (`backups/rifas-semana-N.json.gz`, N = a semana do ano módulo 8): guardam-se as últimas 8 semanas e
o serviço só usa o `PUT` (nunca lista nem apaga). ATENÇÃO: a credencial do Neon `storage:write` **também lê e apaga** e vale para TODOS os buckets do ramo (o Neon não a limita a um bucket nem a só escrever),
por isso uma fuga dela deixa ler e apagar as cópias: guarda-se só no Render, como a `DATABASE_URL` (que já dá acesso a tudo o que está nas cópias).

LIGAR: as variáveis `BACKUP_S3_ENDPOINT`, `BACKUP_S3_BUCKET`, `BACKUP_S3_REGION`, `BACKUP_S3_ACCESS_KEY_ID` e `BACKUP_S3_SECRET_ACCESS_KEY` (as últimas duas são palavras-passe: só no Render).
RESTAURAR: `scripts/restaurar_copia.py` (ver `docs/ADMIN.md`). Nada de dados de visitantes sai do Neon: é o mesmo fornecedor da base.
"""
from __future__ import annotations

import gzip
import json
import logging
import re
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from . import config, s3_simples
from .relatorio import DEPOIS_DAS

log = logging.getLogger("rifas.copia")

TABELAS = ("historico_diario", "objetivos", "auditoria", "comentarios", "seo_textos_bd", "api_chaves")
POSICOES = 8
ESPERA_APOS_FALHA_S = 3600.0


class ErroCopia(Exception):
    """Não foi possível fazer a cópia (a mensagem não leva a chave nem o segredo)."""


@dataclass
class EstadoCopia:
    """O que o painel mostra da cópia (em memória; a última verdadeira está na base, `relatorios`)."""
    tratadas: set[str] = field(default_factory=set)          # semanas já decididas: sem consultas à base até à segunda-feira seguinte (o Neon pode adormecer)
    proxima_tentativa: float = 0.0
    ultimo_erro: str = ""
    ultimo_erro_em: float = 0.0
    ultimo_tamanho: int = 0


def ativa() -> bool:
    """Há destino configurado e uma base Postgres (as cópias só fazem sentido com a base externa)."""
    return config.backup_s3() is not None and bool(config.database_url())


# ------------------------------------------------------------------ exportar e restaurar
def exportar(url_bd: str, tabelas: tuple[str, ...] = TABELAS) -> dict:
    """Todas as linhas das `tabelas` que existem: `{versao, criado, tabelas: {nome: {colunas, linhas}}}`. Valores que o JSON não tem viram texto."""
    import psycopg

    saida: dict[str, dict] = {}
    with psycopg.connect(url_bd, connect_timeout=15) as lig:
        for nome in tabelas:
            if lig.execute("SELECT to_regclass(%s)", (f"public.{nome}",)).fetchone()[0] is None:
                continue                                              # a tabela só existe depois de usada a 1.ª vez
            cur = lig.execute(f"SELECT * FROM {nome}")  # noqa: S608 - `nome` vem da lista fixa TABELAS
            saida[nome] = {"colunas": [c.name for c in cur.description], "linhas": [list(r) for r in cur.fetchall()]}
        lig.rollback()
    return {"versao": 1, "criado": datetime.now(timezone.utc).isoformat(timespec="seconds"), "tabelas": saida}


def comprimir(dados: dict) -> bytes:
    return gzip.compress(json.dumps(dados, ensure_ascii=False, default=str, separators=(",", ":")).encode("utf-8"), mtime=0)


def descomprimir(corpo: bytes) -> dict:
    dados = json.loads(gzip.decompress(corpo).decode("utf-8"))
    if not isinstance(dados, dict) or dados.get("versao") != 1 or not isinstance(dados.get("tabelas"), dict):
        raise ErroCopia("formato_desconhecido")
    return dados


def _garantir_tabelas(url_bd: str) -> None:
    """Cria (se faltarem) as tabelas da app numa base nova, como a app faz ao usá-las pela 1.ª vez."""
    from pathlib import Path

    from .chaves_api import Chaves
    from .historico import HistoricoDiario
    from .objetivos import Objetivos
    from .opiniao import Comentarios
    from .seo_bd import SeoBd

    nada = Path("/nao-usado")
    Chaves(url_bd, nada).listar()
    SeoBd(url_bd, nada).lidos()
    HistoricoDiario(url_bd).total()
    Objetivos(url_bd).todos()
    Comentarios(url_bd).total()
    from .auditoria import Auditoria

    Auditoria(url_bd).total()


_NOME = re.compile(r"[a-z_][a-z0-9_]{0,62}")


def restaurar(url_bd: str, dados: dict, forcar: bool = False) -> dict[str, int | None]:
    """Põe as linhas da cópia na base `url_bd`. Por omissão só preenche tabelas VAZIAS (não duplica nem mistura com dados que já lá estão): uma tabela com linhas fica
    como está (`None` no resultado); `forcar` junta as linhas que faltam (`ON CONFLICT DO NOTHING`). Devolve quantas linhas entraram por tabela."""
    import psycopg

    for nome, t in dados["tabelas"].items():
        if nome in TABELAS and (not all(_NOME.fullmatch(c) for c in t["colunas"]) or any(len(l) != len(t["colunas"]) for l in t["linhas"])):
            raise ErroCopia("tabela_invalida")                        # um ficheiro estragado ou adulterado não escreve onde quiser
    _garantir_tabelas(url_bd)
    entraram: dict[str, int | None] = {}
    with psycopg.connect(url_bd, connect_timeout=15) as lig:
        for nome, t in dados["tabelas"].items():
            if nome not in TABELAS:
                continue                                              # só as tabelas conhecidas
            if not forcar and lig.execute(f"SELECT count(*) FROM {nome}").fetchone()[0]:  # noqa: S608 - `nome` esta em TABELAS
                entraram[nome] = None
                continue
            cols = ", ".join(t["colunas"])
            marcas = ", ".join(["%s"] * len(t["colunas"]))
            entraram[nome] = sum(lig.execute(f"INSERT INTO {nome} ({cols}) VALUES ({marcas}) ON CONFLICT DO NOTHING", linha).rowcount for linha in t["linhas"])  # noqa: S608
        lig.commit()
    return entraram


# ------------------------------------------------------------------ fazer a cópia
def posicao(segunda: date) -> int:
    return segunda.isocalendar().week % POSICOES


def chave_do_objeto(segunda: date | None = None, manual: bool = False) -> str:
    return "backups/rifas-manual.json.gz" if manual else f"backups/rifas-semana-{posicao(segunda)}.json.gz"


def fazer(segunda: date | None = None, manual: bool = False, abrir=urllib.request.urlopen, agora: datetime | None = None) -> dict:
    """Exporta, comprime e grava a cópia no S3. Devolve `{chave, bytes, linhas: {tabela: n}}`. Qualquer falha vira `ErroCopia` só com a classe e o código."""
    s3 = config.backup_s3()
    if s3 is None or not config.database_url():
        raise ErroCopia("sem_configuracao")
    try:
        dados = exportar(config.database_url())
    except Exception as e:  # noqa: BLE001 - a mensagem pode ter o endereço da base
        raise ErroCopia(f"base: {type(e).__name__}") from None
    corpo = comprimir(dados)
    chave = chave_do_objeto(segunda, manual)
    try:
        s3_simples.gravar(s3["endpoint"], s3["regiao"], s3["bucket"], chave, corpo, s3["id"], s3["segredo"], "application/gzip", agora, abrir)
    except s3_simples.ErroS3 as e:
        raise ErroCopia(f"armazenamento: {e}") from None
    return {"chave": chave, "bytes": len(corpo), "linhas": {n: len(t["linhas"]) for n, t in dados["tabelas"].items()}}


def fazer_se_devido(relatorios, estado: EstadoCopia, agora: float | None = None, abrir=urllib.request.urlopen) -> str:
    """Chamado de poucos em poucos minutos. Devolve `desligada`, `cedo` (antes das 00:05 de segunda-feira), `espera`, `tratada`, `ja_feita`, `feita` ou `falhou`."""
    if relatorios is None or not ativa():
        return "desligada"
    agora = time.time() if agora is None else agora
    local = datetime.fromtimestamp(agora, ZoneInfo(config.relatorio_fuso()))
    segunda = local.date() - timedelta(days=local.weekday())
    if local.date() == segunda and local.time() < DEPOIS_DAS:
        return "cedo"
    chave = f"backup:{segunda.isoformat()}"
    if chave in estado.tratadas:
        return "tratada"
    if agora < estado.proxima_tentativa:
        return "espera"
    try:
        if not relatorios.reservar(chave, agora):
            estado.tratadas.add(chave)
            return "ja_feita"
    except Exception:  # noqa: BLE001 - a base em baixo: tenta-se daqui a pouco
        estado.proxima_tentativa = agora + 300
        return "falhou"
    try:
        r = fazer(segunda, False, abrir)
    except ErroCopia as e:
        motivo = str(e)
    except Exception as e:  # noqa: BLE001 - nada derruba o ciclo do serviço
        motivo = type(e).__name__
    else:
        estado.tratadas.add(chave)
        estado.ultimo_erro, estado.ultimo_tamanho = "", r["bytes"]
        log.info("copia de seguranca feita: %s (%d bytes)", r["chave"], r["bytes"])
        return "feita"
    try:
        relatorios.libertar(chave)                                    # desfaz a reserva: a próxima tentativa volta a fazer a cópia
    except Exception:  # noqa: BLE001
        log.warning("copia: nao consegui desfazer a reserva de %s", chave)
    estado.ultimo_erro, estado.ultimo_erro_em = motivo, agora
    estado.proxima_tentativa = agora + ESPERA_APOS_FALHA_S
    log.warning("copia de seguranca falhou (%s)", motivo)
    return "falhou"
