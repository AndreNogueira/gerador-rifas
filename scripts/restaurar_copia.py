"""Restaura uma cópia de segurança do site (`src/web/copia.py`) para uma base Postgres.

    uv run python scripts/restaurar_copia.py copia.json.gz --url "postgresql://..."            # preenche só as tabelas VAZIAS
    uv run python scripts/restaurar_copia.py copia.json.gz --url "postgresql://..." --juntar   # junta as linhas que faltam (ON CONFLICT DO NOTHING)

Como obter a cópia: o ficheiro está no bucket das cópias (`backups/rifas-semana-N.json.gz`, 8 semanas rotativas, ou `backups/rifas-manual.json.gz`); descarrega-se com um URL pré-assinado
(`presign_storage_object` do MCP do Neon, operação `download`) ou com qualquer cliente S3 com uma credencial `storage:read`. `--url` pode vir de `DATABASE_URL`.
Sem `--url` e sem `DATABASE_URL` não faz nada. Cria as tabelas que faltem (como a app) e nunca apaga linhas. `--ver` só diz o que a cópia tem.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ficheiro", type=Path, help="a cópia (.json.gz)")
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""), help="a base Postgres de destino (por omissão DATABASE_URL)")
    ap.add_argument("--juntar", action="store_true", help="junta as linhas que faltam mesmo em tabelas que já têm dados")
    ap.add_argument("--ver", action="store_true", help="só mostra o conteúdo da cópia")
    a = ap.parse_args()

    from web import copia

    dados = copia.descomprimir(a.ficheiro.read_bytes())
    print(f"Cópia de {dados.get('criado', '?')}:")
    for nome, t in dados["tabelas"].items():
        print(f"  {nome}: {len(t['linhas'])} linhas")
    if a.ver:
        return 0
    if not a.url:
        print("Falta o destino: --url ou DATABASE_URL.", file=sys.stderr)
        return 2
    try:
        entraram = copia.restaurar(a.url, dados, forcar=a.juntar)
    except copia.ErroCopia as e:
        print(f"Cópia inválida ({e}).", file=sys.stderr)
        return 1
    print("Restauro:")
    for nome, n in entraram.items():
        print(f"  {nome}: " + ("já tinha dados, ficou como estava (use --juntar)" if n is None else f"{n} linhas novas"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
