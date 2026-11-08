"""Converte as gravacoes do Playwright (src/web/frontend/videos-gravados/*.webm) nos videos das funcionalidades (app/assets/video/*.mp4).

Corta o inicio (a preparacao: carregar os ficheiros) com o instante que a gravacao guardou, reduz para 1280x720 a 15 fps (H.264, sem som,
`+faststart`) e escreve `web_<id>_<lingua>.mp4`. Precisa de um ffmpeg (so para fazer os videos; nao vai na app): `uv run --with imageio-ffmpeg python
scripts/videos_para_mp4.py`, ou a variavel FFMPEG com o caminho de um ffmpeg. Os videos da app Windows (`windows_*`) vem de app/testes/fazer_videos_windows.py.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "src" / "web" / "frontend" / "videos-gravados"
DESTINO = RAIZ / "app" / "assets" / "video"


def ffmpeg() -> str:
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("falta o ffmpeg: uv run --with imageio-ffmpeg python scripts/videos_para_mp4.py (ou defina FFMPEG)")


def converter(webm: Path, exe: str) -> Path:
    meta = webm.with_suffix(".json")
    corte = json.loads(meta.read_text())["corte"] if meta.exists() else 0.0
    saida = DESTINO / (webm.stem + ".mp4")
    cmd = [exe, "-y", "-loglevel", "error", "-ss", f"{corte:.2f}", "-i", str(webm), "-an", "-r", "15",
           "-vf", "scale=1280:720:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "30",
           "-movflags", "+faststart", str(saida)]
    subprocess.run(cmd, check=True)
    return saida


def main() -> int:
    ficheiros = sorted(ORIGEM.glob("web_*.webm"))
    if not ficheiros:
        print("nada para converter: corra primeiro `pnpm videos` em src/web/frontend")
        return 1
    DESTINO.mkdir(parents=True, exist_ok=True)
    exe = ffmpeg()
    for f in ficheiros:
        s = converter(f, exe)
        print(f"{s.name}: {s.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
