"""Imprime «tcl;tk» com as pastas que o Nuitka precisa (`--tcl-library-dir` e `--tk-library-dir`), ou nada se não for preciso.

O plugin `tk-inter` do Nuitka (4.3.x) procura a pasta `tcl8.6` do Python. No Python 3.15 o Tcl/Tk é o 9.0, que traz as bibliotecas dentro da própria
DLL (sistema de ficheiros «zipfs»), por isso essa pasta não existe e o Nuitka pára com «Could not find Tcl». Basta dar-lhe duas pastas que existam
(a do Tk 9 e outra qualquer ao lado): as bibliotecas que o programa usa vêm da DLL. Verificado com o .exe da 2.5 (`--selftest` igual ao da 3.13).
Com o Tcl 8.6 (Python 3.13) não imprime nada e o Nuitka encontra tudo sozinho.
"""
import os
import sys

base = os.path.join(getattr(sys, "base_prefix", sys.prefix), "tcl")
if os.path.isdir(base) and not any(n.startswith("tcl8") for n in os.listdir(base)):
    tk = next((n for n in sorted(os.listdir(base)) if n.startswith("tk9")), None)
    outra = next((n for n in sorted(os.listdir(base)) if n != tk and os.path.isdir(os.path.join(base, n))), None)
    if tk and outra:
        print(f"{os.path.join(base, outra)};{os.path.join(base, tk)}")
