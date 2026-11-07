"""O que a app precisa de saber do sistema onde corre - atras de uma interface, para nao depender do Windows.

`Sistema` e o contrato. Cada ambiente tem a sua implementacao:
  - `SistemaNeutro` (aqui, funciona em Linux/macOS/Windows e num servidor): so usa variaveis de ambiente;
  - `SistemaWindows` (app/ambiente.py): registo do Windows, kernel32 e os.startfile.
Numa webapp quase tudo isto vem do browser (Accept-Language, CSS `prefers-color-scheme`/`accent-color`, descarregar em vez de
abrir): o `SistemaNeutro` so serve para o dono fixar valores por defeito.

  | necessidade              | Windows (app)                  | servidor Linux (web)                                   |
  |--------------------------|--------------------------------|--------------------------------------------------------|
  | lingua                   | kernel32 GetUserDefaultLocale  | cabecalho Accept-Language (i18n.lingua_de_accept_language) |
  | pasta de dados           | %APPDATA%\\GeradorRifas        | RIFAS_DADOS (config.pasta_de_dados) / armazenamento     |
  | modo claro/escuro        | registo AppsUseLightTheme      | CSS prefers-color-scheme; ou RIFAS_TEMA                |
  | cor de destaque          | registo Accent / DWM           | CSS accent-color; ou RIFAS_COR_DESTAQUE                |
  | abrir pasta/ficheiro     | os.startfile                   | nao existe: descarregar (core.saida)                   |
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol, runtime_checkable

from . import config, i18n
from .tema import cor_valida

ENV_TEMA = "RIFAS_TEMA"                  # claro | escuro | (outro valor ou vazio = o browser/sistema decide)
ENV_COR_DESTAQUE = "RIFAS_COR_DESTAQUE"  # #RRGGBB


@runtime_checkable
class Sistema(Protocol):
    def codigo_de_lingua(self) -> str:
        """Codigo da lingua do sistema (p.ex. «pt-PT»), ou «» se nao se sabe."""

    def pasta_de_dados(self) -> Path:
        """Onde guardar o config.json."""

    def modo_escuro(self) -> bool | None:
        """True/False se o sistema o define; None se nao se sabe (o browser decide)."""

    def cor_destaque(self) -> tuple | None:
        """Cor de destaque (R, G, B) do sistema, ou None."""

    def abrir(self, caminho: Path) -> bool:
        """Abre uma pasta/ficheiro com o programa predefinido do sistema. False se nao e possivel (servidor)."""


class SistemaNeutro:
    """Sem dependencias de plataforma: tudo vem de variaveis de ambiente. Num servidor `abrir` nao faz nada."""

    def __init__(self, ambiente=None):
        self.env = os.environ if ambiente is None else ambiente

    def codigo_de_lingua(self) -> str:
        return self.env.get(i18n.ENV_LINGUA, "").strip()

    def pasta_de_dados(self) -> Path:
        env = self.env.get(config.ENV_DADOS, "").strip()
        return Path(env) if env else Path.home() / ".gerador-rifas"

    def modo_escuro(self) -> bool | None:
        return {"escuro": True, "claro": False}.get(self.env.get(ENV_TEMA, "").strip().lower())

    def cor_destaque(self) -> tuple | None:
        return cor_valida(self.env.get(ENV_COR_DESTAQUE))

    def abrir(self, caminho: Path) -> bool:
        return False
