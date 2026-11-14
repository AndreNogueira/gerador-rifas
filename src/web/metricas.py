"""Metricas de uso e de sistema, para o painel de administracao (`/admin`).

PRIVACIDADE: so se guardam agregados e contagens. Nunca IPs (so um *hash com sal aleatorio por arranque*, em memoria, para contar
enderecos distintos na ultima hora e verificar o proxy), nomes de ficheiros, conteudo, ids de sessao nem textos de erro do utilizador.
Os eventos levam apenas codigos (lingua, tema, tipo de dispositivo, estado) e numeros (quantos numeros, quanto tempo).

ARMAZENAMENTO: por omissao SQLite na pasta de armazenamento (`metricas.sqlite3`); com `DATABASE_URL` (Postgres, p.ex. Neon) usa essa base.
Os eventos e os pedidos ficam num *buffer* em memoria e so depois vao para a base, por isso um pedido nunca espera por ela: no SQLite de
30 em 30 s; no Postgres de `METRICAS_BD_MIN` em `METRICAS_BD_MIN` minutos (60 por omissao), para a computacao do Neon poder suspender
(o plano gratuito tem horas de computacao limitadas), e sempre ao terminar. Retencao: 35 dias (sistema e pedidos), 90 dias (eventos).
O disco do plano gratuito do Render e EFEMERO: com SQLite o servico perde estes dados quando adormece ou e atualizado (o painel diz
desde quando ha dados); com `DATABASE_URL` sobrevivem (ver docs/ADMIN.md e docs/BASE_DE_DADOS.md).
"""
from __future__ import annotations

import contextlib
import hashlib
import ipaddress
import json
import logging
import os
import re
import secrets
import sqlite3
import threading
import time
from collections import deque
from pathlib import Path

log = logging.getLogger(__name__)

LIMITES_MS = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000)      # +1 balde para o que passa do ultimo
RETENCAO_SISTEMA_S = 35 * 86400
RETENCAO_EVENTOS_S = 90 * 86400
# intervalo -> (janela em segundos, tamanho de cada ponto dos graficos em segundos)
INTERVALOS: dict[str, tuple[int, int]] = {"1h": (3600, 60), "6h": (21600, 60), "24h": (86400, 300), "7d": (604800, 1800), "30d": (2592000, 7200)}
SONDAGENS = {"GET /api/sessoes/{id_}/trabalho"}         # o frontend pergunta de meio em meio segundo: nao conta para «pedidos por minuto»
DURACAO_BALDES = (5, 15, 30, 60, 120, 300)              # segundos, para o histograma da duracao das geracoes
_ROBOS = re.compile(r"bot|crawl|spider|slurp|preview|facebookexternalhit|headless|curl|wget|python-requests|httpx", re.I)
_MOVEL = re.compile(r"Mobi|Android|iPhone|iPad", re.I)

# SQL que serve ao SQLite e ao Postgres (BIGINT/DOUBLE PRECISION, `?` traduzido para `%s` pelo adaptador, upsert com ON CONFLICT)
_ESQUEMA = (
    "CREATE TABLE IF NOT EXISTS sistema(ts BIGINT PRIMARY KEY, cpu DOUBLE PRECISION, mem_srv DOUBLE PRECISION, mem_motor DOUBLE PRECISION, "
    "mem_cont DOUBLE PRECISION, disco DOUBLE PRECISION, sessoes INTEGER, geracoes INTEGER)",
    "CREATE TABLE IF NOT EXISTS pedidos(ts BIGINT, grupo TEXT, n INTEGER, e4 INTEGER, e5 INTEGER, soma_ms DOUBLE PRECISION, "
    "max_ms DOUBLE PRECISION, hist TEXT, PRIMARY KEY(ts, grupo))",
    "CREATE TABLE IF NOT EXISTS eventos(ts BIGINT, tipo TEXT, a TEXT, b TEXT, c TEXT, v1 DOUBLE PRECISION, v2 DOUBLE PRECISION, v3 DOUBLE PRECISION)",
    "CREATE INDEX IF NOT EXISTS ix_eventos ON eventos(tipo, ts)",
)
_UPSERT_SISTEMA = ("INSERT INTO sistema VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(ts) DO UPDATE SET cpu=excluded.cpu, mem_srv=excluded.mem_srv, "
                   "mem_motor=excluded.mem_motor, mem_cont=excluded.mem_cont, disco=excluded.disco, sessoes=excluded.sessoes, geracoes=excluded.geracoes")
_UPSERT_PEDIDOS = ("INSERT INTO pedidos VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(ts, grupo) DO UPDATE SET n=excluded.n, e4=excluded.e4, "
                   "e5=excluded.e5, soma_ms=excluded.soma_ms, max_ms=excluded.max_ms, hist=excluded.hist")
INTERVALO_BD_PADRAO_MIN = 60                  # Postgres: de quanto em quanto tempo o buffer vai para a base (a computacao do Neon suspende aos 5 min)
BUFFER_MAXIMO = 5000                          # ... ou logo que haja tantos registos por gravar
PAUSA_APOS_FALHA_S = 30                       # sem tentar a base depois de uma falha
BUFFER_LIMITE_FALHAS = 50_000                 # se a base estiver em baixo, o buffer nao cresce sem fim: deita fora o mais antigo


class _Sqlite:
    """O armazenamento local (por omissao): um ficheiro, ou memoria se `caminho` for None."""
    tipo = "sqlite"

    def __init__(self, caminho: Path | None):
        self.caminho = caminho
        self._lig: sqlite3.Connection | None = None

    def _ligacao(self) -> sqlite3.Connection:
        if self._lig is None:
            if self.caminho is not None:
                Path(self.caminho).parent.mkdir(parents=True, exist_ok=True)
            self._lig = sqlite3.connect(str(self.caminho) if self.caminho else ":memory:", check_same_thread=False)
            self._lig.execute("PRAGMA journal_mode=WAL")
            self._lig.execute("PRAGMA synchronous=NORMAL")
            for instrucao in _ESQUEMA:
                self._lig.execute(instrucao)
        return self._lig

    @property
    def ligado(self) -> bool:
        return self._lig is not None

    def executar(self, sql: str, args: tuple = ()) -> list[tuple]:
        return self._ligacao().execute(sql, args).fetchall()

    def muitos(self, sql: str, linhas: list[tuple]) -> None:
        if linhas:
            self._ligacao().executemany(sql, linhas)

    def confirmar(self) -> None:
        self._ligacao().commit()

    def anular(self) -> None:
        if self._lig is not None:
            self._lig.rollback()

    def fechar(self) -> None:
        if self._lig is not None:
            self._lig.close()
            self._lig = None


class _Postgres:
    """O armazenamento persistente (`DATABASE_URL`). Liga-se so quando e preciso e volta a ligar-se se a base a tiver fechado
    (o Neon suspende a computacao e corta as ligacoes inativas). O URL leva a palavra-passe: nunca vai para um log nem para o painel."""
    tipo = "postgres"

    def __init__(self, url: str):
        self._url = url
        self._lig = None

    def _ligacao(self):
        if self._lig is None or self._lig.closed:
            import psycopg                                   # so quando ha DATABASE_URL: sem ele a app nem precisa do driver

            self._lig = psycopg.connect(self._url, connect_timeout=10)
            for instrucao in _ESQUEMA:
                self._lig.execute(instrucao)
            self._lig.commit()
        return self._lig

    @property
    def ligado(self) -> bool:
        return self._lig is not None and not self._lig.closed

    def executar(self, sql: str, args: tuple = ()) -> list[tuple]:
        cur = self._ligacao().execute(sql.replace("?", "%s"), args)
        return cur.fetchall() if cur.description else []

    def muitos(self, sql: str, linhas: list[tuple]) -> None:
        if linhas:
            with self._ligacao().cursor() as cur:
                cur.executemany(sql.replace("?", "%s"), linhas)

    def confirmar(self) -> None:
        self._ligacao().commit()

    def anular(self) -> None:
        if self._lig is not None and not self._lig.closed:
            self._lig.rollback()

    def fechar(self) -> None:
        if self._lig is not None:
            try:
                self._lig.close()
            finally:
                self._lig = None


def _erro_de_ligacao(e: Exception) -> bool:
    """Ligacao cortada ou impossivel (a base suspendeu, rede): vale a pena voltar a ligar e repetir uma vez."""
    try:
        import psycopg
    except ImportError:
        return False
    return isinstance(e, psycopg.OperationalError | psycopg.InterfaceError)


def dispositivo(user_agent: str) -> str:
    """«robo», «movel» ou «computador» (o User-Agent nao se guarda: so esta classe)."""
    if _ROBOS.search(user_agent or ""):
        return "robo"
    return "movel" if _MOVEL.search(user_agent or "") else "computador"


def familia(user_agent: str, toque: bool = False, largura_ecra: int = 0) -> str:
    """A familia do dispositivo pelo User-Agent: iPhone, iPad, Android (telemovel/tablet), Windows, Mac, Linux, ChromeOS ou Outro.
    O iPad moderno diz que e um Mac: distingue-se por ter toque e um ecra grande."""
    ua = user_agent or ""
    if "iPhone" in ua:
        return "iPhone"
    if "iPad" in ua or ("Macintosh" in ua and toque and largura_ecra >= 700):
        return "iPad"
    if "Android" in ua:
        return "Android (telemóvel)" if "Mobile" in ua else "Android (tablet)"
    if "CrOS" in ua:
        return "ChromeOS"
    for chave, nome in (("Windows", "Windows"), ("Macintosh", "Mac"), ("Linux", "Linux")):
        if chave in ua:
            return nome
    return "Outro"


def classe_do_ecra(largura: int, altura: int, toque: bool) -> str:
    """«telemovel», «tablet» ou o tamanho do ecra de um computador, pelo lado MAIOR e MENOR do ecra em pixeis CSS e por ter toque."""
    curto, longo = min(largura, altura), max(largura, altura)
    if toque and curto < 600:
        return "telemóvel"
    if toque and curto < 1100 and longo < 1500:
        return "tablet"
    fisico = f"{largura}×{altura}"
    if longo >= 2000 and longo / max(curto, 1) > 2.1:                  # ultra-wide: um monitor largo (nao um ecra vertical pequeno)
        return f"computador ultra-wide ({fisico})" if longo >= 2400 else "computador ultra-wide"
    if longo < 1400:
        return "computador pequeno (< 1400 px)"
    if longo < 1800:
        return "computador médio (1400–1799 px)"
    if longo < 2400:
        return "computador Full HD (1800–2399 px)"
    if longo < 3200:
        return "computador QHD/2K (2400–3199 px)"
    return "computador 4K ou maior (≥ 3200 px)"


def modelo_limpo(modelo: str) -> str:
    """O modelo do telemovel (de `userAgentData`), sem controlos e sem os valores «vazios» do Chrome com UA reduzido."""
    m = "".join(c for c in (modelo or "") if c.isprintable()).strip()[:40]
    return "" if m.upper() in ("", "K", "UNKNOWN", "ANDROID") else m


def _balde(ms: float) -> int:
    for i, limite in enumerate(LIMITES_MS):
        if ms <= limite:
            return i
    return len(LIMITES_MS)


def percentil(hist: list[int], p: float) -> float | None:
    """O percentil `p` (0-1) de um histograma por baldes: o limite superior do balde onde se atinge `p` (aproximado; None se vazio)."""
    total = sum(hist)
    if not total:
        return None
    alvo, acumulado = p * total, 0
    for i, n in enumerate(hist):
        acumulado += n
        if acumulado >= alvo:
            return float(LIMITES_MS[min(i, len(LIMITES_MS) - 1)])
    return float(LIMITES_MS[-1])


def _somar(a: list[int], b: list[int]) -> list[int]:
    return [x + y for x, y in zip(a, b, strict=True)]


def pais_do_cabecalho(valor: str | None) -> str:
    """O país (ISO 3166, duas letras maiúsculas) que a rede do alojamento põe em `CF-IPCountry`; qualquer outra coisa (em falta, `XX` = desconhecido,
    `T1` = Tor, texto livre) é «??». Só esta forma fechada chega às métricas: o valor bruto de um cabeçalho nunca é guardado."""
    v = (valor or "").strip().upper()
    return v if re.fullmatch(r"[A-Z]{2}", v) and v not in ("XX", "T1") else "??"


def _privado(ip: str) -> bool:
    try:
        e = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return e.is_private or e.is_loopback or e.is_link_local


class Metricas:
    def __init__(self, caminho: Path | None = None, relogio=time.time, url_bd: str = "", intervalo_bd_min: float = INTERVALO_BD_PADRAO_MIN):
        self.caminho = caminho
        self._agora = relogio
        self.arranque = int(relogio())
        self._trava = threading.Lock()                     # os buffers em memoria (nunca se espera pela base com ela tomada)
        self.observar = None                               # gancho de cada evento (observabilidade.Observabilidade.evento)
        self._trava_bd = threading.Lock()                  # a base (uma operacao de cada vez)
        self._armazem = _Postgres(url_bd) if url_bd else _Sqlite(caminho)
        self._intervalo_bd_s = max(60.0, float(intervalo_bd_min) * 60)
        self._ultimo_descarrego = float(relogio())
        self.erro_bd = False                               # a ultima operacao na base falhou (o painel avisa)
        self._bloqueado_ate = 0.0                          # depois de uma falha, nao se volta a tentar durante um bocado (nem cada consulta do painel espera)
        self._eventos: list[tuple] = []
        self._amostras: list[tuple] = []
        self._pedidos: dict[tuple[int, str], list] = {}
        self._cliente: deque = deque(maxlen=5000)          # (ts, privado, xff, hash do ip, o cabecalho do pais veio)
        self._sal = secrets.token_bytes(16)                # muda a cada arranque: nao da para ligar hashes entre arranques
        self.evento("arranque")

    # ------------------------------------------------------------------ registo (rapido, sem disco)
    def evento(self, tipo: str, a: str = "", b: str = "", c: str = "", v1: float = 0.0, v2: float = 0.0, v3: float = 0.0) -> None:
        linha = (int(self._agora()), tipo, str(a)[:40], str(b)[:40], str(c)[:40], float(v1), float(v2), float(v3))
        with self._trava:
            self._eventos.append(linha)
        if self.observar is not None:                        # o registo estruturado e o livro de erros (observabilidade.py): nunca partem um evento
            with contextlib.suppress(Exception):
                self.observar(*linha[1:])

    def pedido(self, grupo: str, estado: int, ms: float) -> None:
        minuto = int(self._agora()) // 60 * 60
        with self._trava:
            linha = self._pedidos.setdefault((minuto, grupo[:80]), [0, 0, 0, 0.0, 0.0, [0] * (len(LIMITES_MS) + 1)])
            linha[0] += 1
            linha[1] += 400 <= estado < 500
            linha[2] += estado >= 500
            linha[3] += ms
            linha[4] = max(linha[4], ms)
            linha[5][_balde(ms)] += 1

    def cliente(self, ip: str, tem_xff: bool, tem_pais: bool = False) -> None:
        """Para verificar o proxy: o IP vira um hash com sal (em memoria, ultima hora) e guarda-se se era privado, se vinha X-Forwarded-For e se
        a rede do alojamento disse o pais (`CF-IPCountry`: so se o cabecalho existe, nunca o seu valor)."""
        h = hashlib.sha256(self._sal + ip.encode()).hexdigest()[:10]
        with self._trava:
            self._cliente.append((self._agora(), _privado(ip), bool(tem_xff), h, bool(tem_pais)))

    def amostrar(self, cpu: float, mem_srv: float, mem_motor: float, mem_cont: float | None, disco: float, sessoes: int, geracoes: int) -> None:
        with self._trava:
            self._amostras.append((int(self._agora()), cpu, mem_srv, mem_motor, mem_cont, disco, sessoes, geracoes))

    # ------------------------------------------------------------------ base de dados
    @property
    def persistente(self) -> bool:
        """Se os dados sobrevivem a um reinicio do servico (base externa): o painel deixa de avisar que se perdem."""
        return self._armazem.tipo == "postgres"

    def estado_bd(self) -> dict:
        return {"tipo": self._armazem.tipo, "erro": self.erro_bd, "intervalo_min": round(self._intervalo_bd_s / 60) if self.persistente else 0}

    def _com_nova_tentativa(self, operacao):
        """Corre `operacao()`; se uma ligacao que existia tiver sido cortada (Neon suspenso), fecha-a e tenta mais uma vez.
        Se nem sequer foi possivel ligar, nao se insiste: a base esta em baixo."""
        tinha_ligacao = self._armazem.ligado
        try:
            return operacao()
        except Exception as e:  # noqa: BLE001 - so se repete o que parece uma ligacao cortada
            if not tinha_ligacao or not _erro_de_ligacao(e):
                raise
            self._armazem.fechar()
            return operacao()

    def descarregar_periodico(self) -> None:
        """Chamado de 30 em 30 s. No SQLite grava sempre; no Postgres so de `METRICAS_BD_MIN` em `METRICAS_BD_MIN` minutos (ou com muitos
        registos por gravar), para a base poder suspender entre gravacoes. Uma falha nao perde nada: o buffer fica para a vez seguinte."""
        if self.persistente:
            with self._trava:
                pendentes = len(self._eventos) + len(self._amostras) + len(self._pedidos)
                devido = self._agora() - self._ultimo_descarrego >= self._intervalo_bd_s or pendentes >= BUFFER_MAXIMO
            if not devido:
                return
        self.descarregar()

    def _repor(self, eventos: list, amostras: list, fechados: dict) -> None:
        """Devolve ao buffer o que nao chegou a ser gravado (a base falhou)."""
        with self._trava:
            self._eventos = (eventos + self._eventos)[-BUFFER_LIMITE_FALHAS:]
            self._amostras = (amostras + self._amostras)[-BUFFER_LIMITE_FALHAS:]
            for chave, v in fechados.items():
                atual = self._pedidos.get(chave)
                if atual is None:
                    self._pedidos[chave] = v
                else:
                    atual[0] += v[0]
                    atual[1] += v[1]
                    atual[2] += v[2]
                    atual[3] += v[3]
                    atual[4] = max(atual[4], v[4])
                    atual[5] = _somar(atual[5], v[5])

    def descarregar(self, tudo: bool = False) -> None:
        """Passa o buffer para a base (os minutos de pedidos ja fechados; todos se `tudo`) e apaga o que passou da retencao."""
        agora = int(self._agora())
        if agora < self._bloqueado_ate:
            return                                          # a base falhou ha pouco: o buffer fica como esta ate a pausa acabar
        with self._trava:
            eventos, self._eventos = self._eventos, []
            amostras, self._amostras = self._amostras, []
            minuto = agora // 60 * 60
            fechados = {k: v for k, v in self._pedidos.items() if tudo or k[0] < minuto}
            for k in fechados:
                del self._pedidos[k]
            self._ultimo_descarrego = float(self._agora())
        with self._trava_bd:
            try:
                self._com_nova_tentativa(lambda: self._gravar(agora, eventos, amostras, fechados))
                self.erro_bd = False
            except Exception as e:
                self._armazem.anular()
                self.erro_bd = True
                self._bloqueado_ate = self._agora() + PAUSA_APOS_FALHA_S
                self._repor(eventos, amostras, fechados)
                log.warning("metricas: nao foi possivel gravar (%s); fica no buffer", type(e).__name__)     # nunca a mensagem: pode ter o endereco da base
                raise

    def _gravar(self, agora: int, eventos: list, amostras: list, fechados: dict) -> None:
        db = self._armazem
        db.muitos("INSERT INTO eventos VALUES (?,?,?,?,?,?,?,?)", eventos)
        db.muitos(_UPSERT_SISTEMA, amostras)
        for (ts, grupo), (n, e4, e5, soma, mx, hist) in fechados.items():
            antigo = db.executar("SELECT n,e4,e5,soma_ms,max_ms,hist FROM pedidos WHERE ts=? AND grupo=?", (ts, grupo))
            if antigo:
                a = antigo[0]
                n, e4, e5, soma, mx = n + a[0], e4 + a[1], e5 + a[2], soma + a[3], max(mx, a[4])
                hist = _somar(hist, json.loads(a[5]))
            db.executar(_UPSERT_PEDIDOS, (ts, grupo, n, e4, e5, soma, mx, json.dumps(hist)))
        db.executar("DELETE FROM sistema WHERE ts < ?", (agora - RETENCAO_SISTEMA_S,))
        db.executar("DELETE FROM pedidos WHERE ts < ?", (agora - RETENCAO_SISTEMA_S,))
        db.executar("DELETE FROM eventos WHERE ts < ?", (agora - RETENCAO_EVENTOS_S,))
        db.confirmar()

    def fechar(self) -> None:
        with contextlib.suppress(Exception):               # a base em baixo nao pode impedir o servico de terminar
            self.descarregar(tudo=True)
        with self._trava_bd:
            self._armazem.fechar()

    # ------------------------------------------------------------------ consultas (para o painel)
    def _consultar(self, sql: str, args: tuple = ()) -> list[tuple]:
        if self._agora() < self._bloqueado_ate:
            return []                                       # a base esta em baixo: o painel mostra o aviso sem esperar por cada consulta
        with contextlib.suppress(Exception):
            self.descarregar(tudo=True)                     # o painel ve sempre o que ja aconteceu (ate o minuto em curso)
        with self._trava_bd:
            try:
                resultado = self._com_nova_tentativa(lambda: self._armazem.executar(sql, args))
                self._armazem.confirmar()                   # fecha a transacao de leitura (o Postgres abre uma a cada consulta)
                self.erro_bd = False
                return resultado
            except Exception as e:
                self._armazem.anular()
                self.erro_bd = True
                self._bloqueado_ate = self._agora() + PAUSA_APOS_FALHA_S
                log.warning("metricas: consulta falhou (%s)", type(e).__name__)
                return []                                   # o painel mostra o aviso em vez de partir

    def dados_desde(self) -> int:
        """O instante do dado mais antigo (ou o arranque): o painel diz «dados desde…» por causa do disco efemero."""
        r = self._consultar("SELECT MIN(ts) FROM eventos")
        return int(r[0][0]) if r and r[0][0] is not None else self.arranque

    def serie_sistema(self, desde: int, passo: int) -> list[dict]:
        linhas = self._consultar(
            "SELECT ts/?*? AS t, AVG(cpu), MAX(mem_srv), MAX(mem_motor), MAX(mem_cont), MAX(disco), MAX(sessoes), MAX(geracoes) "
            "FROM sistema WHERE ts >= ? GROUP BY t ORDER BY t", (passo, passo, desde))
        chaves = ("cpu", "mem_servidor", "mem_motor", "mem_contentor", "disco", "sessoes", "geracoes")
        return [{"t": r[0], **{k: (round(v, 1) if isinstance(v, float) else v) for k, v in zip(chaves, r[1:], strict=True)}} for r in linhas]

    def serie_pedidos(self, desde: int, passo: int) -> list[dict]:
        """Pedidos, erros e latencia (p50, p95) por ponto; sem as sondagens do progresso."""
        linhas = self._consultar("SELECT ts, grupo, n, e4, e5, hist FROM pedidos WHERE ts >= ?", (desde,))
        baldes: dict[int, list] = {}
        for ts, grupo, n, e4, e5, hist in linhas:
            if grupo in SONDAGENS:
                continue
            b = baldes.setdefault(ts // passo * passo, [0, 0, 0, [0] * (len(LIMITES_MS) + 1)])
            b[0] += n
            b[1] += e4
            b[2] += e5
            b[3] = _somar(b[3], json.loads(hist))
        return [{"t": t, "n": b[0], "e4": b[1], "e5": b[2], "p50": percentil(b[3], 0.5), "p95": percentil(b[3], 0.95)} for t, b in sorted(baldes.items())]

    def tabela_pedidos(self, desde: int) -> list[dict]:
        """Por tipo de pedido (metodo + rota): quantos, erros e latencia."""
        linhas = self._consultar("SELECT grupo, n, e4, e5, soma_ms, max_ms, hist FROM pedidos WHERE ts >= ?", (desde,))
        por_grupo: dict[str, list] = {}
        for grupo, n, e4, e5, soma, mx, hist in linhas:
            g = por_grupo.setdefault(grupo, [0, 0, 0, 0.0, 0.0, [0] * (len(LIMITES_MS) + 1)])
            g[0] += n
            g[1] += e4
            g[2] += e5
            g[3] += soma
            g[4] = max(g[4], mx)
            g[5] = _somar(g[5], json.loads(hist))
        saida = [{"pedido": k, "n": g[0], "e4": g[1], "e5": g[2], "medio_ms": round(g[3] / g[0], 1), "p50": percentil(g[5], 0.5),
                  "p95": percentil(g[5], 0.95), "max_ms": round(g[4], 1), "sondagem": k in SONDAGENS} for k, g in por_grupo.items() if g[0]]
        return sorted(saida, key=lambda d: -d["n"])

    def serie_eventos(self, desde: int, passo: int) -> list[dict]:
        linhas = self._consultar(
            "SELECT ts/?*? AS t, tipo, COUNT(*), SUM(v2) FROM eventos WHERE ts >= ? AND tipo IN ('sessao','previa','geracao','pagina') GROUP BY t, tipo ORDER BY t",
            (passo, passo, desde))
        por_t: dict[int, dict] = {}
        for t, tipo, n, soma in linhas:
            d = por_t.setdefault(t, {"t": t, "sessoes": 0, "previas": 0, "geracoes": 0, "paginas": 0, "numeros": 0})
            d[{"sessao": "sessoes", "previa": "previas", "geracao": "geracoes", "pagina": "paginas"}[tipo]] += n
            if tipo == "geracao":
                d["numeros"] += int(soma or 0)
        return [por_t[t] for t in sorted(por_t)]

    def _contar(self, tipo: str, coluna: str, desde: int, onde: str = "", args: tuple = ()) -> list[dict]:
        linhas = self._consultar(f"SELECT {coluna}, COUNT(*) FROM eventos WHERE tipo=? AND ts>=? {onde} GROUP BY {coluna} ORDER BY 2 DESC", (tipo, desde, *args))  # noqa: S608 - `coluna`/`onde` sao constantes do codigo
        return [{"chave": r[0] or "(sem dados)", "n": r[1]} for r in linhas]

    def resumo(self, desde: int) -> dict:
        """Totais e distribuicoes do intervalo."""
        def n(tipo: str, onde: str = "", args: tuple = ()) -> int:
            linhas = self._consultar(f"SELECT COUNT(*) FROM eventos WHERE tipo=? AND ts>=? {onde}", (tipo, desde, *args))  # noqa: S608
            return linhas[0][0] if linhas else 0                  # sem linhas = a base esta em baixo
        gens = self._consultar("SELECT a, COUNT(*), SUM(v2), SUM(v3) FROM eventos WHERE tipo='geracao' AND ts>=? GROUP BY a", (desde,))
        duracoes = sorted(r[0] for r in self._consultar("SELECT v1 FROM eventos WHERE tipo='geracao' AND a='ok' AND ts>=?", (desde,)))
        hist = [0] * (len(DURACAO_BALDES) + 1)
        for d in duracoes:
            hist[next((i for i, lim in enumerate(DURACAO_BALDES) if d <= lim), len(DURACAO_BALDES))] += 1
        rotulos = [f"até {lim} s" if lim < 60 else f"até {lim // 60} min" for lim in DURACAO_BALDES] + [f"mais de {DURACAO_BALDES[-1] // 60} min"]
        def pct(p: float) -> float | None:
            return round(duracoes[min(len(duracoes) - 1, int(p * len(duracoes)))], 1) if duracoes else None
        # funil: quantos EVENTOS de cada etapa (nao pessoas: nao se guarda nada que as identifique); cada passo e a etapa seguinte da vida de uma geracao
        funil = [("Sessões abertas", n("sessao")), ("Template carregado", n("template", "AND a IN ('ok','alg')")),
                 ("Algarismos prontos", n("algarismos", "AND a='ok'")), ("Pré-visualização", n("previa", "AND a='ok'")),
                 ("Geração concluída", sum(r[1] for r in gens if r[0] in ("ok", "erros"))), ("Descarga", n("descarga"))]
        return {
            "sessoes": n("sessao"),
            "previas": {"ok": n("previa", "AND a='ok'"), "erro": n("previa", "AND a<>'ok'")},
            "templates": {"ok": n("template", "AND a='ok'"), "erro": n("template", "AND a<>'ok'")},
            "algarismos": {"ok": n("algarismos", "AND a='ok'"), "erro": n("algarismos", "AND a<>'ok'")},
            "geracoes": {r[0]: r[1] for r in gens},
            "numeros": int(sum(r[2] or 0 for r in gens if r[0] in ("ok", "erros"))),
            "paginas": int(sum(r[3] or 0 for r in gens if r[0] in ("ok", "erros"))),
            "descargas": self._contar("descarga", "a", desde),
            "funil": [{"chave": k, "n": v} for k, v in funil],
            "duracao": {"mediana_s": pct(0.5), "p95_s": pct(0.95), "max_s": round(duracoes[-1], 1) if duracoes else None,
                        "histograma": [{"chave": k, "n": v} for k, v in zip(rotulos, hist, strict=True)]},
            "linguas": self._contar("sessao", "a", desde),
            "temas": self._contar("sessao", "b", desde),
            "dispositivos": self._contar("sessao", "c", desde),
            "paises": self._contar("pais", "a", desde),
            "paginas_vistas": self._contar("pagina", "a", desde, "AND c<>'robo'"),
            "robos": n("pagina", "AND c='robo'"),
            "erros_http": self._contar("erro_http", "a", desde),
            "falhas": self._contar("geracao", "b", desde, "AND a='falhou'"),
            "classes_de_ecra": self._contar("ecra", "a", desde),
            "ecras": self._contar("ecra", "b", desde),
            "dispositivos_detalhe": self._contar("ecra", "c", desde),
            "janelas": self._janelas(desde),
            "toque": self._contar("ecra", "CASE WHEN v3 > 0 THEN 'com toque' ELSE 'sem toque' END", desde),
            "reinicios_motor": n("motor_reiniciado"),
            "arranques": n("arranque"),
        }

    def _janelas(self, desde: int) -> list[dict]:
        """A largura da JANELA do browser (nao do ecra) por escaloes: mostra quem usa janelas pequenas num ecra grande."""
        linhas = self._consultar(
            "SELECT CASE WHEN v1 < 360 THEN '< 360 px' WHEN v1 < 414 THEN '360–413 px (telemóvel)' WHEN v1 < 768 THEN '414–767 px (telemóvel grande)' "
            "WHEN v1 < 1024 THEN '768–1023 px (tablet)' WHEN v1 < 1440 THEN '1024–1439 px' WHEN v1 < 1920 THEN '1440–1919 px' "
            "WHEN v1 < 2560 THEN '1920–2559 px' ELSE '≥ 2560 px' END AS e, COUNT(*) FROM eventos WHERE tipo='ecra' AND ts>=? GROUP BY e ORDER BY 2 DESC",
            (desde,))
        return [{"chave": r[0], "n": r[1]} for r in linhas]

    def proxy(self) -> dict:
        """O que o servidor ve dos clientes: se os IPs reais chegam (`FORWARDED_ALLOW_IPS`) ou se tudo parece vir do proxy do Render."""
        limite = self._agora() - 3600
        with self._trava:
            amostra = [c for c in self._cliente if c[0] >= limite]
        n = len(amostra)
        if n == 0:
            return {"pedidos": 0, "ips_distintos": 0, "privados_pct": None, "xff_pct": None, "pais_pct": None, "veredicto": "sem_dados"}
        privados = sum(1 for c in amostra if c[1]) / n * 100
        xff = sum(1 for c in amostra if c[2]) / n * 100
        pais = sum(1 for c in amostra if c[4]) / n * 100
        distintos = len({c[3] for c in amostra})
        if n < 20:
            veredicto = "poucos_pedidos"
        elif privados > 80 and xff == 0:
            veredicto = "sem_proxy"                          # tudo interno e sem X-Forwarded-For: desenvolvimento local
        elif privados > 80 and distintos <= 2:
            veredicto = "problema"                           # os clientes aparecem todos com o IP do proxy: o limite por IP e global
        else:
            veredicto = "ok"
        return {"pedidos": n, "ips_distintos": distintos, "privados_pct": round(privados), "xff_pct": round(xff),
                "pais_pct": round(pais), "veredicto": veredicto}


def caminho_por_defeito(raiz: Path) -> Path:
    return Path(os.environ.get("RIFAS_METRICAS", "").strip() or raiz / "metricas.sqlite3")
