import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { defineConfig, devices } from "@playwright/test";

// Os testes e2e correm num browser a sério contra a app compilada (`pnpm build`) servida pelo FastAPI (`python -m src.web`).
// Um trabalhador só: o servidor gera um PDF de cada vez e as sessões partilham o motor.
const PORTA = 8123;
const URL = `http://127.0.0.1:${PORTA}`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 120_000,
  expect: { timeout: 30_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  outputDir: "./test-results",
  use: { baseURL: URL, locale: "pt-PT", trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
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
