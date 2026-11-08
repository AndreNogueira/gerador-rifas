// Tira as capturas do tutorial do site (e2e/capturas.spec.ts) para app/assets/ajuda. Uso: `pnpm capturas` (todas as línguas) ou `pnpm capturas pt en`.
// Precisa de `pnpm build` feito e do Chromium do Playwright.
import { spawnSync } from "node:child_process";

const so = process.argv.slice(2);
const r = spawnSync("pnpm", ["exec", "playwright", "test", "e2e/capturas.spec.ts"], {
  stdio: "inherit",
  shell: true,
  env: { ...process.env, GRAVAR_CAPTURAS: so.length ? so.join(",") : "1" },
});
if (r.status === 0) {
  // 28 MB de PNG de 24 bits -> ~6 MB de paleta (scripts/otimizar_capturas.py, na raiz do repositório)
  const o = spawnSync("uv", ["run", "python", "scripts/otimizar_capturas.py"], { stdio: "inherit", shell: true, cwd: "../../.." });
  process.exit(o.status ?? 1);
}
process.exit(r.status ?? 1);
