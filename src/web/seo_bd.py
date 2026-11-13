"""Os textos de SEO editáveis no painel (`/admin`), por página e por língua, guardados na base de dados.

O que se pode editar (cada texto, em cada uma das línguas): o **título** e a **descrição** de cada página (`t_inicio`, `titulo:/tutorial`, `d_*`), as frases
de apoio do SEO (`intro`, `como`...) e os **guias «como fazer»** (título, introdução, passos, dicas, fim). Tudo o que não for editado continua a vir do
código (`seo_textos.py`, `guias/`), que é também o recurso se a base estiver em baixo ou se um texto editado deixar de servir.

 - Guarda-se numa tabela `seo_textos_bd(chave, lingua, valor)` (Postgres com `DATABASE_URL`, senão SQLite local, efémero no Render: o painel avisa).
 - Lê-se **uma vez por minuto** em segundo plano para uma cache em memória (`seo_textos.SOBREPOSTOS`): nenhum pedido de página consulta a base.
 - Valida-se ao gravar **e** ao ler, com as mesmas regras dos testes de SEO: título até 66 de largura (carateres CJK contam dobro), descrição entre 50 e 158,
   os mesmos `{parâmetros}` que o texto do código, sem carateres de controlo, no máximo 1000 carateres. O HTML escapa tudo (nunca se confia no valor).
"""
from __future__ import annotations

import string
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from core import i18n

from . import guias, seo, seo_textos
from .bd_simples import BaseSql

VALOR_MAX = 1000
LARGURA_TITULO = 66
LARGURA_DESCRICAO = (50, 158)
_ESQUEMA = ("CREATE TABLE IF NOT EXISTS seo_textos_bd(chave TEXT NOT NULL, lingua TEXT NOT NULL, valor TEXT NOT NULL, atualizado BIGINT NOT NULL, "
            "PRIMARY KEY(chave, lingua))",)


def largura(texto: str) -> int:
    """Largura de um texto nos resultados de pesquisa: os carateres largos (chinês, japonês, coreano) contam dobro."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in texto)


def _parametros(texto: str) -> set:
    return {nome for _, nome, _, _ in string.Formatter().parse(texto) if nome}


@dataclass(frozen=True)
class Campo:
    chave: str
    tipo: str          # titulo | descricao | texto
    rotulo: str


def catalogo() -> list[Campo]:
    """Tudo o que se pode editar, pela ordem em que o painel mostra."""
    campos = [Campo("t_inicio", "titulo", "Título da página inicial")]
    for p in seo.ROTAS.values():
        if p.indexavel and p.caminho != "/" and not p.titulo_fixo:
            campos.append(Campo(f"titulo:{p.caminho}", "titulo", f"Título de {p.caminho} (inteiro, com «| nome»)"))
        if p.indexavel and p.descricao_chave:
            campos.append(Campo(p.descricao_chave, "descricao", f"Descrição de {p.caminho}"))
    campos += [Campo(c, "texto", f"Texto de apoio «{c}»") for c in seo_textos.CHAVES if c != "t_inicio" and not c.startswith("d_")]
    for nome in guias.NOMES:
        for c in guias.chaves_editaveis(nome):
            tipo = "titulo" if c.endswith(".titulo") and ".passo" not in c else "texto"
            campos.append(Campo(c, tipo, f"Guia «{nome}»: {c.split('.', 2)[2]}"))
    return campos


def _por_chave() -> dict:
    return {c.chave: c for c in catalogo()}


def padrao(chave: str, lingua: str) -> str:
    """O texto do codigo para `chave` na `lingua` (vazio nos titulos de pagina, que o codigo compoe, e entao mostra-se o composto)."""
    if chave.startswith("guia."):
        _, nome, resto = chave.split(".", 2)
        g = guias.padrao(nome, lingua)
        if resto in ("titulo", "intro", "fim"):
            return g[resto]
        if resto.startswith("passo"):
            n, campo = resto[5:].split(".")
            return g["passos"][int(n) - 1][campo]
        return g["dicas"][int(resto[4:]) - 1]
    if chave.startswith("titulo:"):
        return seo.ROTAS[chave[7:]].titulo_padrao(lingua)
    return seo_textos.padrao(chave, lingua)


def validar(chave: str, lingua: str, valor: str) -> str:
    """O valor limpo, ou `ValueError` com a razao (em portugues: e para o dono, no painel)."""
    campo = _por_chave().get(chave)
    if campo is None:
        raise ValueError("Texto desconhecido.")
    if lingua not in i18n.LINGUAS:
        raise ValueError("Língua desconhecida.")
    valor = valor.strip()
    if not valor:
        raise ValueError("O texto está vazio (para voltar ao original use «repor»).")
    if len(valor) > VALOR_MAX:
        raise ValueError(f"Máximo de {VALOR_MAX} carateres.")
    if any(unicodedata.category(c) == "Cc" and c not in "\n" for c in valor) or (campo.tipo != "texto" and "\n" in valor):
        raise ValueError("Sem quebras de linha nem carateres de controlo.")
    esperados = _parametros(padrao(chave, "pt")) if not chave.startswith("titulo:") else set()
    if _parametros(valor) != esperados:
        raise ValueError("Parâmetros diferentes dos do original: " + (", ".join("{" + p + "}" for p in sorted(esperados)) or "nenhum") + ".")
    app = i18n.traduzir("app_nome", lingua)
    if campo.tipo == "descricao":
        n = largura(valor)
        if not LARGURA_DESCRICAO[0] <= n <= LARGURA_DESCRICAO[1] or len(valor) > 160:
            raise ValueError(f"A descrição deve ter entre {LARGURA_DESCRICAO[0]} e {LARGURA_DESCRICAO[1]} de largura (tem {n}).")
    elif campo.tipo == "titulo":
        final = valor.format(app=app) if chave == "t_inicio" else f"{valor} | {app}" if chave.startswith("guia.") else valor
        if largura(final) > LARGURA_TITULO:
            raise ValueError(f"O título completo («{final}») tem largura {largura(final)}; o máximo é {LARGURA_TITULO}.")
    return valor


class SeoBd(BaseSql):
    ESQUEMA = _ESQUEMA

    def __init__(self, url_bd: str = "", caminho: Path | None = None, relogio=time.time):
        super().__init__(url_bd, caminho)
        self._relogio = relogio
        self.erro = False                                  # a ultima leitura falhou (ficam os textos de antes)
        self.ultima_leitura = 0

    def lidos(self) -> dict[tuple[str, str], str]:
        """Todos os textos editados que continuam validos (um valor estragado a mao na base ignora-se)."""
        saida = {}
        for chave, lingua, valor in self._executar("SELECT chave, lingua, valor FROM seo_textos_bd"):
            try:
                saida[(chave, lingua)] = validar(chave, lingua, valor)
            except ValueError:
                continue
        return saida

    def atualizar(self) -> int:
        """Le a base e publica os textos para o resto da app. Se falhar, mantem os de antes. Devolve quantos textos estao em vigor."""
        try:
            novos = self.lidos()
        except Exception:  # noqa: BLE001 - a base em baixo nunca derruba as paginas: ficam os textos de antes (ou os do codigo)
            self.erro = True
            return len(seo_textos.SOBREPOSTOS)
        self.erro = False
        self.ultima_leitura = int(self._relogio())
        seo_textos.definir_sobreposicoes(novos)
        return len(novos)

    def definir(self, chave: str, lingua: str, valor: str) -> str:
        valor = validar(chave, lingua, valor)
        self._executar("INSERT INTO seo_textos_bd(chave, lingua, valor, atualizado) VALUES (%s, %s, %s, %s) "
                       "ON CONFLICT (chave, lingua) DO UPDATE SET valor = EXCLUDED.valor, atualizado = EXCLUDED.atualizado",
                       (chave, lingua, valor, int(self._relogio())))
        self.atualizar()
        return valor

    def repor(self, chave: str, lingua: str) -> bool:
        linhas = self._executar("DELETE FROM seo_textos_bd WHERE chave = %s AND lingua = %s RETURNING chave", (chave, lingua))
        self.atualizar()
        return bool(linhas)

    def vista(self, lingua: str) -> list[dict]:
        """Para o painel: cada texto editavel nesta lingua com o do codigo e o editado (ou None)."""
        editados = {c: v for (c, lg), v in seo_textos.SOBREPOSTOS.items() if lg == lingua}
        return [{"chave": c.chave, "tipo": c.tipo, "rotulo": c.rotulo, "padrao": padrao(c.chave, lingua), "valor": editados.get(c.chave)} for c in catalogo()]
