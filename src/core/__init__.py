"""Gerador de Rifas - logica de negocio, sem interface e sem Windows.

Usado pela app Windows (app/) e, mais tarde, pela webapp (src/web/). Nao importa Tkinter, CustomTkinter, pywin32,
ctypes nem framework web (tests/test_core_puro.py verifica-o).

`import core` continua a dar o mesmo que o antigo core.py (core.preparar, core.gerar, core.Trabalho, ...): o motor esta em
core/motor.py e este ficheiro reexporta tudo, inclusive os nomes privados que os testes usam.
"""
from .motor import *  # noqa: F401,F403
from .motor import (  # noqa: F401  (privados usados pelos testes)
    _abrir_leitor, _arrumar, _f, _matriz_texto, _mesma_letra, _origem_pdf, _rot_de, _uv, _xy,
)
from . import autoteste, config, escolha_folha, i18n, idiomas, pdftexto, pedido, tutorial  # noqa: F401
