"""Junta num `.zip` os ficheiros que o SITE mostra (os vídeos e as imagens do tutorial) para os publicar no armazenamento de objetos (Neon Object
Storage, S3) em vez de irem na imagem Docker. O serviço descarrega-o no arranque (`src/web/assets_remotos.py`, variáveis `ASSETS_URL` e `ASSETS_SHA256`).

A app Windows continua a usar `app/assets` inteira; o site só precisa do subconjunto web: ficam de fora os `windows_*.mp4` e as capturas `<lg>_a|b|c.png`.

    uv run python scripts/publicar_assets.py                 # cria saida/assets-web-<sha>.zip e diz que variáveis pôr
    uv run --with boto3 python scripts/publicar_assets.py --enviar   # e envia-o (credenciais AWS-padrão do Neon: `neon env pull` ou uma com `storage:write`)

O `.zip` é determinístico (mesmos ficheiros = mesmos bytes = mesmo SHA-256; um teste compara-o com o do Dockerfile) e o nome leva o SHA-256, por isso cada versão
tem o seu URL e nada fica em cache velha. O bucket (`public_read`) é o `ASSETS_BUCKET` (por omissão `site-assets`). Sem credenciais o ficheiro também se pode enviar por um URL pré-assinado
(`presign_storage_object` do MCP do Neon). Ver `docs/ASSETS.md`.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "app" / "assets"
SAIDA = RAIZ / "saida"
CAPTURA_WINDOWS = re.compile(r"^[a-z]{2}_[abc]\.png$")          # as capturas da app Windows (as do site são `<lg>_wa|wb|wc.png`)
DATA = (2026, 1, 1, 0, 0, 0)                                    # data fixa: o mesmo conteúdo dá os mesmos bytes


def do_site() -> list:
    """Os ficheiros que o site usa, como `[(nome no zip, caminho)]`, ordenados."""
    ficheiros = [(f"video/{f.name}", f) for f in (ASSETS / "video").glob("*.mp4") if not f.name.startswith("windows_")]
    ficheiros += [(f"ajuda/{f.name}", f) for f in (ASSETS / "ajuda").iterdir()
                  if f.is_file() and f.suffix in (".png", ".jpg", ".json") and not CAPTURA_WINDOWS.match(f.name)]
    return sorted(ficheiros)


def zip_bytes() -> bytes:
    """O .zip em memoria: determinístico em qualquer sistema (ordem e data fixas, sem compressão, e o `ajuda.json` canónico: o fim de linha não conta)."""
    import io
    import json
    saida = io.BytesIO()
    with zipfile.ZipFile(saida, "w", zipfile.ZIP_STORED) as z:
        for nome, caminho in do_site():
            dados = caminho.read_bytes()
            if caminho.suffix == ".json":
                dados = json.dumps(json.loads(dados), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            info = zipfile.ZipInfo(nome, DATA)
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            info.create_system = 3                                  # o `zipfile` poe 0 no Windows e 3 em Linux no cabecalho: fixo-o para o SHA-256 ser igual em qualquer sistema
            z.writestr(info, dados)
    return saida.getvalue()


def criar_zip(destino: Path) -> str:
    destino.parent.mkdir(parents=True, exist_ok=True)
    dados = zip_bytes()
    destino.write_bytes(dados)
    return hashlib.sha256(dados).hexdigest()


def main(enviar: bool) -> int:
    provisorio = SAIDA / "assets-web.zip"
    sha = criar_zip(provisorio)
    final = SAIDA / f"assets-web-{sha[:12]}.zip"
    final.unlink(missing_ok=True)
    provisorio.rename(final)
    print(f"{len(do_site())} ficheiros, {final.stat().st_size / 1e6:.1f} MB -> {final}\nSHA-256 {sha}")
    bucket = os.environ.get("ASSETS_BUCKET", "site-assets")
    chave = final.name
    if enviar:
        import boto3
        from botocore.config import Config
        s3 = boto3.client("s3", config=Config(s3={"addressing_style": "path"}))
        s3.upload_file(str(final), bucket, chave, ExtraArgs={"ContentType": "application/zip", "CacheControl": "public, max-age=31536000, immutable"})
        print("enviado")
    endpoint = os.environ.get("AWS_ENDPOINT_URL_S3", "https://<o-endpoint-do-neon>")
    print(f"\nNo Render (Environment):\n  ASSETS_URL    = {endpoint.rstrip('/')}/{bucket}/{chave}\n  ASSETS_SHA256 = {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--enviar" in sys.argv))
