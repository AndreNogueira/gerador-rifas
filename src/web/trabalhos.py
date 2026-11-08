"""O motor (`core`, sincrono e com o PDFium) num PROCESSO de trabalho isolado.

Porque um processo e nao um *thread*: o PDFium nao e thread-safe; a instancia gratuita do Render tem 512 MB; um PDF mal feito
pode rebentar a memoria ou nao acabar. O processo e unico (1 PDFium), recria-se se morrer (OOM) ou passar do tempo, e tem uma
pequena cache do ultimo `Preparado` (reconstrui-lo custa ~1 s no PC e muito mais na CPU do Render).

Fronteira entre processos: so entram/saem dados simples (caminhos, texto, `InfoTemplate`, `Resultado`). Os erros viajam como
tuplos (`ErroRifas` com parametros nao sobrevive ao pickle). O progresso e o cancelar passam por ficheiros na pasta da sessao:
`progresso.json` (o worker escreve, o servidor le) e `cancelar` (o servidor cria; o motor so chama `.is_set()`).

As funcoes `analisar`, `previa` e `gerar` correm no worker (nao as chame diretamente no servidor); `Motor` e o que o servidor usa.
"""
from __future__ import annotations

import asyncio
import json
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from pathlib import Path

import core
from core import entradas, escolha_folha, i18n


class Ocupado(Exception):
    """O motor esta a gerar para alguem (ou ha pedidos a mais em fila): tentar de novo daqui a pouco."""


PROGRESSO = "progresso.json"
CANCELAR = "cancelar"
_CACHE: dict = {"chave": None, "prep": None}          # SO existe dentro do processo de trabalho


# ====================================================================== dentro do processo de trabalho
def _erro(e: BaseException) -> tuple:
    """Uma excecao como tuplo simples (viaja pelo pickle): ("cancelado",) | ("alg", chave, params, info) | ("erro", chave, params) | ("exc", texto)."""
    if isinstance(e, core.Cancelado):
        return ("cancelado",)
    if isinstance(e, core.ErroAlgarismos):
        return ("alg", e.chave, dict(e.params), e.info)
    if isinstance(e, core.ErroRifas):
        return ("erro", e.chave, dict(e.params))
    return ("exc", f"{type(e).__name__}: {e}")


def _assinatura(pasta: Path) -> tuple:
    fs = [f for f in sorted(pasta.iterdir()) if f.is_file() and f.name.startswith(("template.", "algarismos."))]
    return tuple((f.name, f.stat().st_mtime_ns, f.stat().st_size) for f in fs)


def _preparado(pasta: str, tpl_nome: str, alg_nome: str, log=None):
    """O `Preparado` desta sessao: o da cache se os ficheiros nao mudaram, senao reconstroi-se."""
    p = Path(pasta)
    chave = (pasta, _assinatura(p))
    if _CACHE["chave"] == chave and _CACHE["prep"] is not None:
        return _CACHE["prep"]
    _CACHE.update(chave=None, prep=None)                 # liberta o anterior antes de construir o novo (memoria)
    algs = sorted(f for f in p.iterdir() if f.name.startswith("algarismos."))
    prep = entradas.preparar_de_bytes((p / "template.pdf").read_bytes(), algs[0].read_bytes() if algs else None,
                                      tpl_nome or "template.pdf", alg_nome or "algarismos", log or (lambda m: None))
    _CACHE.update(chave=chave, prep=prep)
    return prep


def _com_folha(prep, papel: str, margem: str, porfolha: str, marcas: bool = False):
    """Template de uma so rifa: aplica a folha escolhida (recalculada aqui, nao atravessa o pickle)."""
    if not escolha_folha.tem_folha(prep.info):
        return prep
    esc = escolha_folha.escolher_folha(prep.info, papel, margem, porfolha, marcas)
    return escolha_folha.preparado_com_folha(prep, esc.disp)


def _logs(lista: list) -> list:
    return [{"chave": getattr(m, "chave", ""), "params": dict(getattr(m, "params", {}) or {}), "texto": str(m)} for m in lista]


def _descricoes(prep) -> dict:
    """«letra X» / «imagem Y» como o motor as descreve, em CADA lingua (a descricao e calculada com a lingua em vigor)."""
    saida = {}
    for lg in i18n.LINGUAS:
        with i18n.com_lingua(lg):
            saida[lg] = list(prep.descricoes)
    return saida


def analisar(pasta: str, tpl_nome: str, alg_nome: str) -> tuple:
    """Le o template (e os algarismos, se ja ha). ("ok", info, {lingua: descricoes}, logs) | ("alg"|"erro"|"exc", ...)."""
    logs: list = []
    try:
        prep = _preparado(pasta, tpl_nome, alg_nome, logs.append)
        return ("ok", prep.info, _descricoes(prep), _logs(logs))
    except Exception as e:  # noqa: BLE001 - tudo volta como dados
        r = _erro(e)
        return (*r, _logs(logs))


def previa(pasta: str, tpl_nome: str, alg_nome: str, papel: str, margem: str, porfolha: str,
           inicio: int, fim: int, digitos: int, prefixo: str = "", cor: tuple | None = None, saltar: tuple = (),
           marcas: bool = False) -> tuple:
    """PDF de 1 pagina com os primeiros numeros: ("ok", bytes, por_pagina) | erro. `prefixo`, `cor` e `saltar`: ver core.series."""
    try:
        prep = _com_folha(_preparado(pasta, tpl_nome, alg_nome), papel, margem, porfolha, marcas)
        return ("ok", core.pdf_da_previa(prep, inicio, digitos, fim, prefixo, cor, saltar), prep.por_pagina)
    except Exception as e:  # noqa: BLE001
        return _erro(e)


def png(pdf: str, dpi: int = 150) -> tuple:
    """A 1.a pagina de um PDF como PNG (para os browsers que nao mostram PDFs, como o Chrome do Android): (\"ok\", bytes) | erro."""
    try:
        return ("ok", core.motor.png_de_pagina(Path(pdf), dpi))
    except Exception as e:  # noqa: BLE001
        return _erro(e)


class Bandeira:
    """Imita threading.Event para o motor (que so usa `is_set`): ha uma bandeira se o ficheiro existe."""

    def __init__(self, caminho: Path):
        self.caminho = caminho

    def is_set(self) -> bool:
        return self.caminho.exists()


class _Progresso:
    """Escreve `progresso.json` (feitas, total, registo) no maximo 4 vezes por segundo, de forma atomica."""

    def __init__(self, caminho: Path):
        self.caminho, self.feitas, self.total, self.linhas, self._ultimo = caminho, 0, 0, [], 0.0

    def _escrever(self) -> None:
        self._ultimo = time.monotonic()
        tmp = self.caminho.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps({"feitas": self.feitas, "total": self.total, "registo": self.linhas}, ensure_ascii=False), encoding="utf-8")
        except OSError:
            return                                       # o progresso e so informativo: nunca derruba a geracao
        for _ in range(5):
            try:
                os.replace(tmp, self.caminho)
                return
            except OSError:                              # Windows: o servidor esta a ler o ficheiro nesse instante
                time.sleep(0.02)

    def passo(self, feitas: int, total: int) -> None:
        self.feitas, self.total = feitas, total
        if time.monotonic() - self._ultimo >= 0.25:
            self._escrever()

    def log(self, m) -> None:
        self.linhas.extend(_logs([m]))
        self._escrever()

    def fechar(self) -> None:
        self._escrever()


def gerar(pasta: str, tpl_nome: str, alg_nome: str, nome: str, inicio: int, fim: int, por_ficheiro: int | None,
          digitos: int, papel: str, margem: str, porfolha: str, prefixos: tuple = (), saltar: tuple = (),
          cor_por_serie: bool = False, marcas: bool = False) -> tuple:
    """Gera os PDFs para `<pasta>/saida`. ("ok", [Resultado]) | ("cancelado",) | erro. O registo vai para `progresso.json`."""
    p = Path(pasta)
    prog = _Progresso(p / PROGRESSO)
    try:
        prep = _com_folha(_preparado(pasta, tpl_nome, alg_nome), papel, margem, porfolha, marcas)
        tr = core.Trabalho(saida=p / "saida", nome=nome, inicio=inicio, fim=fim, por_ficheiro=por_ficheiro, digitos=digitos,
                           prefixos=prefixos, saltar=saltar, cor_por_serie=cor_por_serie)
        res = core.gerar(tr, prep, prog.log, prog.passo, Bandeira(p / CANCELAR))
        return ("ok", res)
    except Exception as e:  # noqa: BLE001
        return _erro(e)
    finally:
        prog.fechar()


def _iniciar() -> None:
    """Corre uma vez ao arrancar o processo: o resto das importacoes (PIL, pypdfium2) faz-se ja aqui, nao no 1.o pedido."""
    from core import motor  # noqa: F401


def aquecer() -> str:
    return "pronto"


# ====================================================================== no servidor
class Motor:
    """O processo de trabalho visto do servidor (asyncio). Uma geracao de cada vez; analisar/pre-visualizar de outra sessao
    enquanto se gera recebem logo `web_ocupado` em vez de ficarem presos atras dela."""

    MAX_PENDENTES = 4                 # pedidos curtos em fila para o motor (acima disto: ocupado)

    def __init__(self, tempo_maximo_s: float | None = None):
        self._pool: ProcessPoolExecutor | None = None
        self.geracao: str | None = None            # sessao que esta a gerar
        self.tempo_maximo_s = tempo_maximo_s
        self._pendentes = 0
        self.reinicios = 0                        # quantas vezes o processo foi morto e recriado (painel de administracao)

    # -- processo
    def _novo(self) -> ProcessPoolExecutor:
        return ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn"), initializer=_iniciar)

    @property
    def pool(self) -> ProcessPoolExecutor:
        if self._pool is None:
            self._pool = self._novo()
        return self._pool

    def reiniciar(self) -> None:
        """Mata o processo (OOM, tempo excedido, bloqueado) e deixa que o proximo pedido crie outro."""
        pool, self._pool = self._pool, None
        if pool is None:
            return
        self.reinicios += 1
        for proc in list(getattr(pool, "_processes", {}).values()):
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
        pool.shutdown(wait=False, cancel_futures=True)

    def parar(self) -> None:
        self.reiniciar()

    async def aquecer(self) -> None:
        await asyncio.get_running_loop().run_in_executor(self.pool, aquecer)

    async def _correr(self, fn, *args, tempo: float | None = None):
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(loop.run_in_executor(self.pool, fn, *args), tempo)
        except asyncio.TimeoutError:
            self.reiniciar()
            raise
        except BrokenProcessPool:
            self.reiniciar()
            raise

    # -- pedidos curtos
    async def curto(self, fn, *args):
        """Analisar/pre-visualizar: nao se espera atras de uma geracao nem de uma fila grande."""
        if self.geracao is not None or self._pendentes >= self.MAX_PENDENTES:
            raise Ocupado()
        self._pendentes += 1
        try:
            return await self._correr(fn, *args, tempo=120)
        finally:
            self._pendentes -= 1

    # -- geracao
    def reservar(self, sessao: str) -> bool:
        """Fica com a vez de gerar (sincrono: duas pessoas nunca passam ao mesmo tempo). False se ja ha uma geracao."""
        if self.geracao is not None:
            return False
        self.geracao = sessao
        return True

    async def gerar(self, sessao: str, *args):
        """Corre a geracao de quem a reservou e liberta a vez no fim."""
        try:
            return await self._correr(gerar, *args, tempo=self.tempo_maximo_s)
        finally:
            self.geracao = None
