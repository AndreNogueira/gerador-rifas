"""As sessoes dos utilizadores (sem contas): um id aleatorio, uma pasta em disco e o estado da analise e da geracao.

Tudo o que o utilizador le sai daqui ja traduzido na lingua do pedido, com os textos e as regras do `core`
(`pedido`, `escolha_folha`, `i18n`). Em memoria: um reinicio (deploy, adormecer no Render) apaga as sessoes e os ficheiros;
o frontend cria uma sessao nova quando recebe 404.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import core
from core import escolha_folha, i18n, pedido, saida
from core.armazenamento import ArmazenamentoLocal

from . import config
from .modelos import (Calculo, Campos, EntregaInfo, Ficheiro, FolhaInfo, InfoTemplate, PreviaInfo, Resumo, Sessao, TrabalhoEstado)
from .trabalhos import PROGRESSO

A_CORRER = ("a_gerar", "a_cancelar")


def primeira_linha(txt: str) -> str:
    return txt.strip().splitlines()[0] if txt.strip() else ""


def texto_de_erro(r: tuple, lg: str) -> str:
    """Um erro do worker (`trabalhos._erro`) como mensagem na lingua `lg`."""
    if r[0] in ("erro", "alg"):
        return i18n.traduzir(r[1], lg, **r[2])
    if r[0] == "cancelado":
        return i18n.traduzir("cancelado", lg)
    return i18n.traduzir("erro_inesperado", lg, erro=r[1])


def texto_de_linha(linha: dict, lg: str) -> str:
    """Uma linha do registo (`{chave, params, texto}`) na lingua `lg` (as sem chave ficam como estao)."""
    if linha.get("chave"):
        try:
            return i18n.traduzir(linha["chave"], lg, **linha.get("params", {}))
        except (KeyError, IndexError, ValueError):
            pass
    return linha.get("texto", "")


@dataclass
class Geracao:
    estado: str = "livre"          # livre | a_gerar | a_cancelar | ok | erros | cancelado | falhou
    feitas: int = 0
    total: int = 0
    registo: list = field(default_factory=list)       # [{chave, params, texto}]
    erro: tuple | None = None      # com «falhou»: ("erro", chave, params) | ("exc", texto)
    resultados: list = field(default_factory=list)
    entrega: saida.Entrega | None = None
    nome: str = ""


@dataclass
class SessaoEstado:
    id: str
    ultimo: float = field(default_factory=time.time)
    tpl_nome: str = ""
    alg_nome: str = ""
    analise: tuple | None = None      # a resposta de `trabalhos.analisar`
    alg_erro: tuple | None = None     # um ficheiro de algarismos recusado pelo tipo (nao chegou a ser guardado)
    previa_n: int = 0
    previa_titulo: tuple | None = None
    gerar: Geracao = field(default_factory=Geracao)
    tarefa: asyncio.Task | None = None

    def tocar(self) -> None:
        self.ultimo = time.time()

    @property
    def info(self):
        a = self.analise
        if a is None:
            return None
        return a[1] if a[0] == "ok" else (a[3] if a[0] == "alg" else None)

    @property
    def a_correr(self) -> bool:
        return self.gerar.estado in A_CORRER


class Sessoes:
    """O registo das sessoes e a sua pasta em disco (`ArmazenamentoLocal`)."""

    def __init__(self, armazem: ArmazenamentoLocal, maximo: int | None = None, validade_s: float | None = None):
        self.armazem = armazem
        self.maximo = maximo if maximo is not None else config.max_sessoes()
        self.validade_s = validade_s if validade_s is not None else config.validade_min() * 60
        self._todas: dict = {}

    def __len__(self) -> int:
        return len(self._todas)

    def criar(self) -> SessaoEstado | None:
        """Uma sessao nova, ou None se ha demasiadas (depois de apagar as inativas)."""
        if len(self._todas) >= self.maximo:
            self.limpar()
        if len(self._todas) >= self.maximo:
            return None
        s = SessaoEstado(self.armazem.nova_sessao())
        self._todas[s.id] = s
        return s

    def obter(self, id_: str) -> SessaoEstado | None:
        s = self._todas.get(id_)
        if s is not None:
            s.tocar()
        return s

    def apagar(self, id_: str) -> None:
        s = self._todas.pop(id_, None)
        if s is not None:
            if s.tarefa is not None and not s.tarefa.done():
                s.tarefa.cancel()
            self.armazem.apagar_sessao(id_)

    def pasta(self, s: SessaoEstado) -> Path:
        return self.armazem.pasta(s.id)

    def limpar(self, agora: float | None = None) -> int:
        """Apaga as sessoes inativas (menos as que estao a gerar) e as pastas orfas. Devolve quantas sessoes."""
        agora = time.time() if agora is None else agora
        velhas = [i for i, s in self._todas.items() if not s.a_correr and agora - s.ultimo > self.validade_s]
        for i in velhas:
            self.apagar(i)
        self.armazem.limpar_antigas(self.validade_s, agora)
        return len(velhas)


# ====================================================================== a vista da sessao em JSON (traduzida)
def _ficheiros(s: SessaoEstado, lg: str) -> tuple:
    """(Ficheiro do template, Ficheiro dos algarismos, avisos)."""
    a = s.analise
    tr = lambda chave, **kw: i18n.traduzir(chave, lg, **kw)  # noqa: E731
    if not s.tpl_nome or a is None:
        tpl = Ficheiro(nome=s.tpl_nome, estado="vazio", texto=tr("c1_vazio"))
    elif a[0] in ("ok", "alg"):
        info = a[1] if a[0] == "ok" else a[3]
        ok = tr("c1_ok_uma", primeiro=info.primeiro) if info.n_campos == 1 else tr("c1_ok", n=info.n_campos, primeiro=info.primeiro, ultimo=info.ultimo)
        tpl = Ficheiro(nome=s.tpl_nome, estado="ok", texto=f"{ok} · {', '.join(info.fontes)}\n{s.tpl_nome}")
    else:
        msg = texto_de_erro(a, lg)
        tpl = Ficheiro(nome=s.tpl_nome, estado="erro", texto="✖ " + primeira_linha(msg), detalhe=msg)

    if s.alg_erro is not None:
        msg = texto_de_erro(s.alg_erro, lg)
        alg = Ficheiro(nome=s.alg_nome, estado="erro", texto="✖ " + primeira_linha(msg), detalhe=msg)
    elif a is not None and a[0] == "ok":
        alg = Ficheiro(nome=s.alg_nome, estado="ok", texto="✔ " + "; ".join(a[2].get(lg) or a[2]["pt"]))
    elif a is not None and a[0] == "alg":
        if s.alg_nome:
            msg = texto_de_erro(a, lg)
            alg = Ficheiro(nome=s.alg_nome, estado="erro", texto="✖ " + primeira_linha(msg), detalhe=msg)
        else:
            alg = Ficheiro(estado="precisa", texto=tr("c2_precisa"))
    else:
        alg = Ficheiro(nome=s.alg_nome, estado="vazio", texto=("— " + s.alg_nome) if s.alg_nome else "—")

    avisos = []
    if a is not None and a[0] == "ok":
        avisos = [texto_de_linha(m, lg) for m in a[3] if str(m.get("texto", "")).startswith("⚠")]
    return tpl, alg, avisos


def ler_progresso(g: Geracao, pasta: Path) -> None:
    """Atualiza `g` com o `progresso.json` que o worker escreve (o progresso e o registo vivem nesse ficheiro)."""
    try:
        d = json.loads((pasta / PROGRESSO).read_text(encoding="utf-8"))
        g.feitas, g.total, g.registo = int(d["feitas"]), int(d["total"]), list(d["registo"])
    except (OSError, ValueError, KeyError):
        pass                                               # ainda nao existe, ou estava a ser trocado: fica o anterior


def _trabalho(s: SessaoEstado, lg: str, desde: int, pasta: Path) -> TrabalhoEstado:
    g = s.gerar
    if g.estado in A_CORRER:
        ler_progresso(g, pasta)
    tr = lambda chave, **kw: i18n.traduzir(chave, lg, **kw)  # noqa: E731
    texto, cor, erro = "", "suave", ""
    if g.estado == "a_gerar":
        texto = tr("est_progresso", a=g.feitas, b=g.total) if g.total else tr("est_a_gerar")
    elif g.estado == "a_cancelar":
        texto = tr("est_a_cancelar")
    elif g.estado == "ok":
        texto, cor = tr("est_ok", n=len(g.resultados)), "ok"
    elif g.estado == "erros":
        texto, cor = tr("est_erros", n=sum(1 for r in g.resultados if not r.ok)), "aviso"
    elif g.estado == "cancelado":
        texto, cor = tr("cancelado"), "aviso"
    elif g.estado == "falhou":
        texto, cor = tr("est_falhou"), "erro"
        erro = texto_de_erro(g.erro, lg) if g.erro else ""
    linhas = [texto_de_linha(m, lg) for m in g.registo[desde:]]
    entrega = None
    if g.entrega is not None and g.estado in ("ok", "erros"):
        e = g.entrega
        entrega = EntregaInfo(tipo=e.tipo, nome=e.nome, ficheiros=[f.name for f in e.ficheiros[:8]], total=len(e.ficheiros),
                              url=f"/api/sessoes/{s.id}/descarregar")
    return TrabalhoEstado(estado=g.estado, texto=texto, cor=cor, feitas=g.feitas, total=g.total, registo=linhas,
                          proximo=max(desde, len(g.registo)), erro=erro, entrega=entrega)


def vista(s: SessaoEstado, lg: str, pasta: Path, desde: int = 0) -> Sessao:
    """A sessao como o frontend a le (tudo traduzido em `lg`)."""
    tpl, alg, avisos = _ficheiros(s, lg)
    info = s.info
    tem_modelo = (pasta / "template.pdf").is_file() and s.tpl_nome != ""
    return Sessao(
        sessao=s.id, template=tpl, algarismos=alg,
        info=InfoTemplate(n_campos=info.n_campos, primeiro=info.primeiro, ultimo=info.ultimo, digitos=len(info.primeiro),
                          tem_folha=escolha_folha.tem_folha(info)) if info is not None else None,
        pronto=s.analise is not None and s.analise[0] == "ok",
        tem_modelo=tem_modelo, modelo_url=f"/api/sessoes/{s.id}/modelo.pdf" if tem_modelo else "",
        previa=PreviaInfo(n=s.previa_n, titulo=i18n.traduzir(s.previa_titulo[0], lg, **s.previa_titulo[1]),
                          url=f"/api/sessoes/{s.id}/previa.pdf?n={s.previa_n}") if s.previa_titulo else None,
        avisos=avisos, trabalho=_trabalho(s, lg, desde, pasta))


# ====================================================================== o formulario: folha, resumo, confirmacao
def trabalho_dos_campos(c: Campos) -> core.Trabalho:
    """Os campos de texto -> `core.Trabalho` (levanta ErroRifas; chamar dentro de `i18n.com_lingua`)."""
    return pedido.trabalho_de_campos("", c.nome, c.inicio, c.fim, c.max_ficheiro, c.digitos, c.modo)


def folha_dos_campos(info, c: Campos):
    """(Disposicao | None, EscolhaFolha | None) da folha escolhida; levanta ErroRifas se nao cabe. Chamar dentro de com_lingua."""
    if not escolha_folha.tem_folha(info):
        return None, None
    esc = escolha_folha.escolher_folha(info, c.papel, c.margem, c.porfolha)
    return esc.disp, esc


def calcular(info, c: Campos, lg: str) -> Calculo:
    """O painel da folha e o resumo do pedido para o que esta escrito (o que a app Windows mostrava a cada tecla)."""
    folha, disp = None, None
    with i18n.com_lingua(lg):
        if escolha_folha.tem_folha(info):
            try:
                esc = escolha_folha.escolher_folha(info, c.papel, c.margem, c.porfolha)
                disp = esc.disp
                texto, aviso = escolha_folha.texto_da_folha(disp, esc.acima)
                folha = FolhaInfo(texto=texto, aviso=aviso, n=disp.n, maximo=disp.maximo)
            except core.ErroRifas as e:
                folha = FolhaInfo(texto="✖ " + primeira_linha(e.em(lg)), erro=True)
        try:
            tr_ = trabalho_dos_campos(c)
            n = pedido.rifas_por_pagina(disp, info)
            texto, aviso = pedido.resumo_do_pedido(tr_, n, tem_template=info is not None)
            if tr_.fim - tr_.inicio + 1 > config.max_numeros():          # avisa-se logo, nao so ao carregar em «Gerar»
                texto, aviso = i18n.traduzir("web_demasiados", lg, max=config.max_numeros()), True
            resumo = Resumo(texto=texto, aviso=aviso, max_ativo=c.modo == "varios")
        except core.ErroRifas as e:
            resumo = Resumo(texto=e.em(lg), aviso=True, max_ativo=c.modo == "varios")
    confirmar = ""
    if disp is not None and disp.n > core.AVISO_POR_PAGINA:
        confirmar = i18n.traduzir("conf_muitas", lg, n=disp.n, w=f"{disp.celula.width / core.MM:.0f}", h=f"{disp.celula.height / core.MM:.0f}")
    return Calculo(folha=folha, resumo=resumo, confirmar=confirmar)
