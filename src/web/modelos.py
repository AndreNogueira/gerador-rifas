"""Os JSON da API (modelos Pydantic) e o erro HTTP com texto pronto a mostrar. O frontend (src/api.ts) espelha estes tipos.

Todos os textos que o utilizador le vem ja traduzidos na lingua do pedido (cabecalho `X-Lingua`), a partir dos textos do `core`.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ErroApi(Exception):
    """Erro com texto traduzido para o utilizador. `tipo`: «aviso» (ele pode corrigir) ou «erro»."""

    def __init__(self, estado: int, texto: str, tipo: Literal["aviso", "erro"] = "erro"):
        super().__init__(texto)
        self.estado, self.texto, self.tipo = estado, texto, tipo


class Erro(BaseModel):
    detail: str
    tipo: Literal["aviso", "erro"] = "erro"


# ------------------------------------------------------------------ sessao
class Ficheiro(BaseModel):
    """O estado de um dos dois ficheiros carregados (template, algarismos)."""
    nome: str = ""
    estado: Literal["vazio", "precisa", "ok", "erro"] = "vazio"
    texto: str = ""
    detalhe: str = ""              # com estado «erro»: a mensagem completa (o `texto` e so a 1.a linha)


class InfoTemplate(BaseModel):
    n_campos: int                  # bilhetes por pagina
    primeiro: str
    ultimo: str
    digitos: int                   # algarismos do desenho (0001 -> 4): o valor sugerido
    tem_folha: bool                # template de uma so rifa: aparece o painel da folha


class PreviaInfo(BaseModel):
    n: int                         # muda a cada pre-visualizacao (evita a cache do visor)
    titulo: str
    url: str


class EntregaInfo(BaseModel):
    tipo: Literal["pdf", "zip"]
    nome: str
    ficheiros: list[str]
    total: int
    url: str


class TrabalhoEstado(BaseModel):
    estado: Literal["livre", "a_gerar", "a_cancelar", "ok", "erros", "cancelado", "falhou"] = "livre"
    texto: str = ""                # a linha de estado ja traduzida
    cor: Literal["suave", "ok", "aviso", "erro"] = "suave"
    feitas: int = 0
    total: int = 0
    registo: list[str] = []        # linhas novas do registo desde `desde`
    proximo: int = 0               # passar como `desde` no pedido seguinte
    erro: str = ""                 # com estado «falhou»: a mensagem
    entrega: EntregaInfo | None = None


class Sessao(BaseModel):
    sessao: str
    template: Ficheiro
    algarismos: Ficheiro
    info: InfoTemplate | None = None
    pronto: bool = False           # template e algarismos validos: pode pre-visualizar e gerar
    tem_modelo: bool = False       # ha template para mostrar no visor
    modelo_url: str = ""
    previa: PreviaInfo | None = None
    avisos: list[str] = []         # avisos da analise do template (letras diferentes, DPI baixo...)
    trabalho: TrabalhoEstado


# ------------------------------------------------------------------ formulario
class Campos(BaseModel):
    """O que o utilizador escreveu nos cartoes 3 e 4 e no painel da folha (texto, como na app Windows)."""
    nome: str = Field("", max_length=200)
    inicio: str = Field("1", max_length=20)
    fim: str = Field("1000", max_length=20)
    digitos: str = Field("4", max_length=20)
    modo: Literal["varios", "unico"] = "varios"
    max_ficheiro: str = Field("300", max_length=20)
    papel: str = Field("A4", max_length=20)
    margem: str = Field("5", max_length=20)
    porfolha: str = Field("", max_length=20)


class FolhaInfo(BaseModel):
    ativa: bool = True
    texto: str = ""
    aviso: bool = False
    erro: bool = False
    n: int = 0                     # rifas por folha escolhidas
    maximo: int = 0


class Resumo(BaseModel):
    texto: str
    aviso: bool = False
    max_ativo: bool = True         # o campo «maximo por ficheiro» so conta no modo «varios»


class Calculo(BaseModel):
    folha: FolhaInfo | None = None   # None: o template nao e de uma so rifa
    resumo: Resumo
    confirmar: str = ""            # texto a confirmar antes de gerar (muitas rifas por folha), vazio se nao e preciso
