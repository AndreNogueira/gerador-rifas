import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { defineConfig, devices } from "@playwright/test";

// Os testes e2e correm num browser a sério contra a app compilada (`pnpm build`) servida pelo FastAPI (`python -m src.web`).
// 2 projetos, corridos em 2 fases por `scripts/e2e.mjs` (`pnpm e2e`): "motor" (fluxo.spec.ts + paginas.spec.ts —
// geração a sério, pré-visualização do preçário/vales: tudo isto partilha o único processo de trabalho do motor,
// `trabalhos.Motor.pool`/`.curto`, por isso workers:1) e "visual" (contraste.spec.ts + cabecalho.spec.ts +
// leve.spec.ts — só navegação e amostragem de pixéis, nunca chamam o motor: seguro com vários trabalhadores a
// sério). Um ficheiro novo entra num dos dois `testMatch` abaixo (se chamar o motor, em "motor"; senão, em
// "visual"); `scripts/e2e.mjs` corre sempre "motor" primeiro, por segurança.
const PORTA = 8123;
const URL = `http://127.0.0.1:${PORTA}`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 120_000,
  expect: { timeout: 30_000 },
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  outputDir: "./test-results",
  use: { baseURL: URL, locale: "pt-PT", trace: "retain-on-failure" },
  projects: [
    {
      name: "motor",
      testMatch: /(fluxo|paginas|videos|capturas)\.spec\.ts$/,
      fullyParallel: false,
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "visual",
      testMatch: /(contraste|cabecalho|leve)\.spec\.ts$/,
      fullyParallel: true,
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "uv run python -m src.web",
    cwd: "../../..",
    url: `${URL}/health`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      PORT: String(PORTA),
      HOST: "127.0.0.1",
      PUBLIC_URL: URL,
      VERIFICACAO_CHAVE: "chave-so-para-os-testes-e2e-1234567890", // o QR de verificação só existe com chave
      KEEPALIVE: "0",
      RIFAS_ARMAZENAMENTO: mkdtempSync(join(tmpdir(), "rifas-e2e-")), // uma pasta nova a cada corrida: os comentários e o resto não se acumulam (há 3 comentários por IP e hora)
    },
  },
});
