import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// Em desenvolvimento o Vite (5173) reencaminha a API para o FastAPI (python -m src.web, porta 8080).
const api = process.env.API_URL ?? "http://127.0.0.1:8080";

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": api, "/health": api } },
  build: { outDir: "dist", sourcemap: true },
  test: { environment: "jsdom", globals: true, setupFiles: ["./src/teste-setup.ts"] },
});
