#!/bin/sh
# Corre todos os testes do motor num contentor Linux (chamado por docker/testes_linux.ps1; /repo = a raiz do repositorio).
# Falha (codigo != 0) se qualquer teste falhar.
set -u
cd /repo
pip install -q uv 2>&1 | grep -v notice
uv sync -q || exit 1
PY=/opt/venv/bin/python
echo "== Python $($PY -c 'import sys,platform;print(sys.version.split()[0], platform.system())')"
falhas=0
echo "== pytest"
$PY -m pytest -q -p no:cacheprovider || falhas=$((falhas + 1))
cd app
export PYTHONIOENCODING=utf-8
correr() {
    echo "== $*"
    $PY "$@" > /tmp/saida.txt 2>&1
    codigo=$?
    tail -3 /tmp/saida.txt
    [ "$codigo" -eq 0 ] || { echo "FALHOU (codigo $codigo)"; falhas=$((falhas + 1)); }
}
correr testes/teste_folha.py exemplos /tmp/o_folha
correr testes/teste_canva.py /tmp/o_canva
correr testes/teste_5000.py testes/templates_aleatorios /tmp/o_5000_pdf pdf 600
correr testes/teste_5000.py testes/templates_aleatorios /tmp/o_5000_png png 600
correr testes/teste_digitos.py testes/templates_aleatorios /tmp/o_digitos
echo "== RESULTADO: $([ "$falhas" -eq 0 ] && echo OK || echo "FALHOU ($falhas)")"
[ "$falhas" -eq 0 ]
