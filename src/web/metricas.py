"""Metricas de uso e de sistema, para o painel de administracao (`/admin`).

PRIVACIDADE: so se guardam agregados e contagens. Nunca IPs (so um *hash com sal aleatorio por arranque*, em memoria, para contar
enderecos distintos na ultima hora e verificar o proxy), nomes de ficheiros, conteudo, ids de sessao nem textos de erro do utilizador.
Os eventos levam apenas codigos (lingua, tema, tipo de dispositivo, estado) e numeros (quantos numeros, quanto tempo).

ARMAZENAMENTO: SQLite na pasta de armazenamento (`metricas.sqlite3`). Os eventos e os pedidos ficam num *buffer* em memoria e vao
para o disco de 30 em 30 s, por isso um pedido nunca espera pelo disco. Retencao: 35 dias (sistema e pedidos), 90 dias (eventos).
O disco do plano gratuito do Render e EFEMERO: o servico perde estes dados quando adormece ou e atualizado (o painel diz desde quando
ha dados). Para os guardar de vez e preciso um disco persistente ou uma base externa (ver docs/ADMIN.md).
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from collections import deque
from pathlib import Path

LIMITES_MS = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000)      # +1 balde para o que passa do ultimo
RETENCAO_SISTEMA_S = 35 * 86400
RETENCAO_EVENTOS_S = 90 * 86400
# intervalo -> (janela em segundos, tamanho de cada ponto dos graficos em segundos)
INTERVALOS: dict[str, tuple[int, int]] = {"1h": (3600, 60), "6h": (21600, 60), "24h": (86400, 300), "7d": (604800, 1800), "30d": (2592000, 7200)}
SONDAGENS = {"GET /api/sessoes/{id_}/trabalho"}         # o frontend pergunta de meio em meio segundo: nao conta para «pedidos por minuto»
DURACAO_BALDES = (5, 15, 30, 60, 120, 300)              # segundos, para o histograma da duracao das geracoes
_ROBOS = re.compile(r"bot|crawl|spider|slurp|preview|facebookexternalhit|headless|curl|wget|python-requests|httpx", re.I)
_MOVEL = re.compile(r"Mobi|Android|iPhone|iPad", re.I)

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS sistema(ts INTEGER PRIMARY KEY, cpu REAL, mem_srv REAL, mem_motor REAL, mem_cont REAL, disco REAL, sessoes INTEGER, geracoes INTEGER);
CREATE TABLE IF NOT EXISTS pedidos(ts INTEGER, grupo TEXT, n INTEGER, e4 INTEGER, e5 INTEGER, soma_ms REAL, max_ms REAL, hist TEXT, PRIMARY KEY(ts, grupo));
CREATE TABLE IF NOT EXISTS eventos(ts INTEGER, tipo TEXT, a TEXT, b TEXT, c TEXT, v1 REAL, v2 REAL, v3 REAL);
CREATE INDEX IF NOT EXISTS ix_eventos ON eventos(tipo, ts);
"""


def dispositivo(user_agent: str) -> str:
    """«robo», «movel» ou «computador» (o User-Agent nao se guarda: so esta classe)."""
    if _ROBOS.search(user_agent or ""):
        return "robo"
    return "movel" if _MOVEL.search(user_agent or "") else "computador"


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


def _privado(ip: str) -> bool:
    try:
        e = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return e.is_private or e.is_loopback or e.is_link_local


class Metricas:
    def __init__(self, caminho: Path | None = None, relogio=time.time):
        self.caminho = caminho
        self._agora = relogio
        self.arranque = int(relogio())
        self._trava = threading.Lock()
        self._ligacao: sqlite3.Connection | None = None
        self._eventos: list[tuple] = []
        self._amostras: list[tuple] = []
        self._pedidos: dict[tuple[int, str], list] = {}
        self._cliente: deque = deque(maxlen=5000)          # (ts, privado, xff, hash do ip)
        self._sal = secrets.token_bytes(16)                # muda a cada arranque: nao da para ligar hashes entre arranques
        self.evento("arranque")

    # ------------------------------------------------------------------ registo (rapido, sem disco)
    def evento(self, tipo: str, a: str = "", b: str = "", c: str = "", v1: float = 0.0, v2: float = 0.0, v3: float = 0.0) -> None:
        with self._trava:
            self._eventos.append((int(self._agora()), tipo, str(a)[:40], str(b)[:40], str(c)[:40], float(v1), float(v2), float(v3)))

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

    def cliente(self, ip: str, tem_xff: bool) -> None:
        """Para verificar o proxy: o IP vira um hash com sal (em memoria, ultima hora) e guarda-se se era privado e se vinha X-Forwarded-For."""
        h = hashlib.sha256(self._sal + ip.encode()).hexdigest()[:10]
        with self._trava:
            self._cliente.append((self._agora(), _privado(ip), bool(tem_xff), h))

    def amostrar(self, cpu: float, mem_srv: float, mem_motor: float, mem_cont: float | None, disco: float, sessoes: int, geracoes: int) -> None:
        with self._trava:
            self._amostras.append((int(self._agora()), cpu, mem_srv, mem_motor, mem_cont, disco, sessoes, geracoes))

    # ------------------------------------------------------------------ disco
    def _db(self) -> sqlite3.Connection:
        if self._ligacao is None:
            if self.caminho is not None:
                Path(self.caminho).parent.mkdir(parents=True, exist_ok=True)
            self._ligacao = sqlite3.connect(str(self.caminho) if self.caminho else ":memory:", check_same_thread=False)
            self._ligacao.execute("PRAGMA journal_mode=WAL")
            self._ligacao.execute("PRAGMA synchronous=NORMAL")
            self._ligacao.executescript(_ESQUEMA)
        return self._ligacao

    def descarregar(self, tudo: bool = False) -> None:
        """Passa o buffer para o SQLite (os minutos de pedidos ja fechados; todos se `tudo`) e apaga o que passou da retencao."""
        agora = int(self._agora())
        with self._trava:
            eventos, self._eventos = self._eventos, []
            amostras, self._amostras = self._amostras, []
            minuto = agora // 60 * 60
            fechados = {k: v for k, v in self._pedidos.items() if tudo or k[0] < minuto}
            for k in fechados:
                del self._pedidos[k]
            db = self._db()
            db.executemany("INSERT INTO eventos VALUES (?,?,?,?,?,?,?,?)", eventos)
            db.executemany("INSERT OR REPLACE INTO sistema VALUES (?,?,?,?,?,?,?,?)", amostras)
            for (ts, grupo), (n, e4, e5, soma, mx, hist) in fechados.items():
                antigo = db.execute("SELECT n,e4,e5,soma_ms,max_ms,hist FROM pedidos WHERE ts=? AND grupo=?", (ts, grupo)).fetchone()
                if antigo:
                    n, e4, e5, soma, mx = n + antigo[0], e4 + antigo[1], e5 + antigo[2], soma + antigo[3], max(mx, antigo[4])
                    hist = _somar(hist, json.loads(antigo[5]))
                db.execute("INSERT OR REPLACE INTO pedidos VALUES (?,?,?,?,?,?,?,?)", (ts, grupo, n, e4, e5, soma, mx, json.dumps(hist)))
            db.execute("DELETE FROM sistema WHERE ts < ?", (agora - RETENCAO_SISTEMA_S,))
            db.execute("DELETE FROM pedidos WHERE ts < ?", (agora - RETENCAO_SISTEMA_S,))
            db.execute("DELETE FROM eventos WHERE ts < ?", (agora - RETENCAO_EVENTOS_S,))
            db.commit()

    def fechar(self) -> None:
        self.descarregar(tudo=True)
        with self._trava:
            if self._ligacao is not None:
                self._ligacao.close()
                self._ligacao = None

    # ------------------------------------------------------------------ consultas (para o painel)
    def _consultar(self, sql: str, args: tuple = ()) -> list[tuple]:
        self.descarregar(tudo=True)                         # o painel ve sempre o que ja aconteceu (ate o minuto em curso)
        with self._trava:
            return self._db().execute(sql, args).fetchall()

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
            return self._consultar(f"SELECT COUNT(*) FROM eventos WHERE tipo=? AND ts>=? {onde}", (tipo, desde, *args))[0][0]  # noqa: S608
        gens = self._consultar("SELECT a, COUNT(*), SUM(v2), SUM(v3) FROM eventos WHERE tipo='geracao' AND ts>=? GROUP BY a", (desde,))
        duracoes = sorted(r[0] for r in self._consultar("SELECT v1 FROM eventos WHERE tipo='geracao' AND a='ok' AND ts>=?", (desde,)))
        hist = [0] * (len(DURACAO_BALDES) + 1)
        for d in duracoes:
            hist[next((i for i, lim in enumerate(DURACAO_BALDES) if d <= lim), len(DURACAO_BALDES))] += 1
        rotulos = [f"até {lim} s" if lim < 60 else f"até {lim // 60} min" for lim in DURACAO_BALDES] + [f"mais de {DURACAO_BALDES[-1] // 60} min"]
        def pct(p: float) -> float | None:
            return round(duracoes[min(len(duracoes) - 1, int(p * len(duracoes)))], 1) if duracoes else None
        return {
            "sessoes": n("sessao"),
            "previas": {"ok": n("previa", "AND a='ok'"), "erro": n("previa", "AND a<>'ok'")},
            "templates": {"ok": n("template", "AND a='ok'"), "erro": n("template", "AND a<>'ok'")},
            "algarismos": {"ok": n("algarismos", "AND a='ok'"), "erro": n("algarismos", "AND a<>'ok'")},
            "geracoes": {r[0]: r[1] for r in gens},
            "numeros": int(sum(r[2] or 0 for r in gens if r[0] in ("ok", "erros"))),
            "paginas": int(sum(r[3] or 0 for r in gens if r[0] in ("ok", "erros"))),
            "descargas": self._contar("descarga", "a", desde),
            "duracao": {"mediana_s": pct(0.5), "p95_s": pct(0.95), "max_s": round(duracoes[-1], 1) if duracoes else None,
                        "histograma": [{"chave": k, "n": v} for k, v in zip(rotulos, hist, strict=True)]},
            "linguas": self._contar("sessao", "a", desde),
            "temas": self._contar("sessao", "b", desde),
            "dispositivos": self._contar("sessao", "c", desde),
            "paginas_vistas": self._contar("pagina", "a", desde, "AND c<>'robo'"),
            "robos": n("pagina", "AND c='robo'"),
            "erros_http": self._contar("erro_http", "a", desde),
            "falhas": self._contar("geracao", "b", desde, "AND a='falhou'"),
            "reinicios_motor": n("motor_reiniciado"),
            "arranques": n("arranque"),
        }

    def proxy(self) -> dict:
        """O que o servidor ve dos clientes: se os IPs reais chegam (`FORWARDED_ALLOW_IPS`) ou se tudo parece vir do proxy do Render."""
        limite = self._agora() - 3600
        with self._trava:
            amostra = [c for c in self._cliente if c[0] >= limite]
        n = len(amostra)
        if n == 0:
            return {"pedidos": 0, "ips_distintos": 0, "privados_pct": None, "xff_pct": None, "veredicto": "sem_dados"}
        privados = sum(1 for c in amostra if c[1]) / n * 100
        xff = sum(1 for c in amostra if c[2]) / n * 100
        distintos = len({c[3] for c in amostra})
        if n < 20:
            veredicto = "poucos_pedidos"
        elif privados > 80 and xff == 0:
            veredicto = "sem_proxy"                          # tudo interno e sem X-Forwarded-For: desenvolvimento local
        elif privados > 80 and distintos <= 2:
            veredicto = "problema"                           # os clientes aparecem todos com o IP do proxy: o limite por IP e global
        else:
            veredicto = "ok"
        return {"pedidos": n, "ips_distintos": distintos, "privados_pct": round(privados), "xff_pct": round(xff), "veredicto": veredicto}


def caminho_por_defeito(raiz: Path) -> Path:
    return Path(os.environ.get("RIFAS_METRICAS", "").strip() or raiz / "metricas.sqlite3")
