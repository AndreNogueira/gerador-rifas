#!/bin/sh
# Corre em local o mesmo que o CI: ruff, pytest, e no frontend Biome, tsc, Vitest e build.
# Uso (a partir da raiz): sh scripts/verificar.sh [--docker]
cd "$(dirname "$0")/.." || exit 1
raiz=$(pwd)
falhas=""

passo() {
  nome=$1; pasta=$2; shift 2
  printf '\n==> %s\n' "$nome"
  if ! (cd "$pasta" && "$@"); then
    falhas="$falhas
  - $nome"
    printf 'FALHOU: %s\n' "$nome"
  fi
}

passo "ruff"             "$raiz" uv run ruff check .
passo "pytest"           "$raiz" uv run pytest -q
passo "frontend: Biome"  "$raiz/src/web/frontend" pnpm run lint
passo "frontend: tsc"    "$raiz/src/web/frontend" pnpm run tipos
passo "frontend: Vitest" "$raiz/src/web/frontend" pnpm run teste
passo "frontend: build"  "$raiz/src/web/frontend" pnpm run build

if [ "$1" = "--docker" ]; then
  passo "docker: testes" "$raiz" docker build --target testes -t gerador-rifas-testes .
  passo "docker: web"    "$raiz" docker build --target web -t gerador-rifas .
fi

if [ -z "$falhas" ]; then
  printf '\nTudo verde. Podes abrir o PR.\n'
  exit 0
fi
printf '\nFalhou:%s\n' "$falhas"
exit 1
