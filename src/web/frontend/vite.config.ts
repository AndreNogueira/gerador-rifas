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
    modulePreload: false, // um só JS: não há nada para pré-carregar
  },
  test: { environment: "jsdom", globals: true, setupFiles: ["./src/teste-setup.ts"] },
});
