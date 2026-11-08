// Grava os vídeos das funcionalidades (e2e/videos.spec.ts) com o browser a sério. Uso: `pnpm videos` (todos) ou `pnpm videos series qr` (só esses).
// Precisa de `pnpm build` feito e do Chromium do Playwright. Depois: `uv run --with imageio-ffmpeg python scripts/videos_para_mp4.py` (na raiz).
import { spawnSync } from "node:child_process";

const so = process.argv.slice(2);
const r = spawnSync("pnpm", ["exec", "playwright", "test", "e2e/videos.spec.ts"], {
  stdio: "inherit",
  shell: true,
  env: { ...process.env, GRAVAR_VIDEOS: so.length ? so.join(",") : "1" },
});
process.exit(r.status ?? 1);
