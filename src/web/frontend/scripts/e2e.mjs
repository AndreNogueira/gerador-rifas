// Corre o e2e em 2 fases para aproveitar os núcleos sem arriscar duas chamadas ao motor ao mesmo tempo
// (playwright.config.ts): "motor" (fluxo+paginas+videos+capturas, workers:1) primeiro, depois "visual"
// (contraste+cabecalho+leve, em paralelo a sério). Cada fase arranca e fecha o seu próprio servidor, como sempre.
// Uso: `pnpm e2e` (as duas fases) ou `pnpm e2e -g contraste` (um filtro ad-hoc: 1 só trabalhador, simples e seguro
// em qualquer combinação de testes, sem ter de adivinhar a que fase cada um pertence).
import { cpus } from "node:os";
import { spawnSync } from "node:child_process";

const extra = process.argv.slice(2);

function correr(args) {
  const r = spawnSync("pnpm", ["exec", "playwright", "test", ...args], { stdio: "inherit", shell: true });
  return r.status ?? 1;
}

if (extra.length) {
  process.exit(correr(["--workers=1", ...extra]));
}

const trabalhadores = Math.max(2, Math.min(4, cpus().length));
const falhouMotor = correr(["--project=motor", "--workers=1"]);
if (falhouMotor !== 0) process.exit(falhouMotor);
process.exit(correr(["--project=visual", `--workers=${trabalhadores}`]));
