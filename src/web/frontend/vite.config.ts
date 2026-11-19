import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";
import { ofuscar } from "./ofuscar";

// Em desenvolvimento o Vite (5173) reencaminha a API para o FastAPI (python -m src.web, porta 8080).
const api = process.env.API_URL ?? "http://127.0.0.1:8080";

export default defineConfig({
  plugins: [react(), ofuscar()],
  server: { proxy: { "/api": api, "/health": api } },
  build: {
    outDir: "dist",
    sourcemap: false, // um mapa publicado desfaria a ofuscação (e pesa mais de 1 MB)
    cssCodeSplit: false, // UM só CSS
    // as partes preguiçosas (Admin, Editor, Sorteio) são ficheiros à parte e partilham com o principal um pedaço pequeno (o runtime do JSX): o Vite liga-o no
    // index.html com `modulepreload` para o browser o pedir JÁ, em paralelo com o principal (senão só o descobria depois de o carregar: uma viagem a mais à rede)
    modulePreload: { polyfill: false },
  },
  // 20 s: os testes dos temas compilam os 14 temas com o Sass, o que numa máquina ocupada passa dos 5 s por omissão
  test: {
    environment: "jsdom",
    globals: true,
    exclude: ["e2e/**", "node_modules/**", "dist/**"],
    setupFiles: ["./src/teste-setup.ts"],
    testTimeout: 20000,
  },
});
