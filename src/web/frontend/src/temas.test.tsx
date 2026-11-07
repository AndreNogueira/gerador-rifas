import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";
import { VISUAIS, VISUAL_POR_OMISSAO, visualValido } from "./temas";

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}
const raiz = document.documentElement;

beforeEach(() => {
  localStorage.clear();
  raiz.removeAttribute("data-visual");
  new ServidorFalso().instalar();
});
afterEach(() => vi.unstubAllGlobals());

describe("temas visuais", () => {
  it("arranca no tema por omissão e não guarda nada", async () => {
    abrir();
    await screen.findByTestId("visual");
    expect(raiz.getAttribute("data-visual")).toBe(VISUAL_POR_OMISSAO);
    expect(localStorage.getItem("rifas.visual")).toBeNull();
  });

  it("muda de tema, lembra-se dele e volta ao tema por omissão sem deixar rasto", async () => {
    abrir();
    const seletor = await screen.findByTestId("visual");
    await userEvent.selectOptions(seletor, "gala");
    expect(raiz.getAttribute("data-visual")).toBe("gala");
    expect(localStorage.getItem("rifas.visual")).toBe("gala");
    await userEvent.selectOptions(seletor, VISUAL_POR_OMISSAO);
    expect(raiz.getAttribute("data-visual")).toBe(VISUAL_POR_OMISSAO);
    expect(localStorage.getItem("rifas.visual")).toBeNull();
  });

  it("retoma o tema guardado e ignora valores desconhecidos", async () => {
    localStorage.setItem("rifas.visual", "arcade");
    abrir();
    await waitFor(() => expect(raiz.getAttribute("data-visual")).toBe("arcade"));
    expect(screen.getByTestId("visual")).toHaveValue("arcade");
    document.body.innerHTML = "";
    localStorage.setItem("rifas.visual", "nao-existe");
    abrir();
    await waitFor(() => expect(raiz.getAttribute("data-visual")).toBe(VISUAL_POR_OMISSAO));
  });

  it("o tema é independente de claro/escuro", async () => {
    abrir();
    await userEvent.selectOptions(await screen.findByTestId("tema"), "escuro");
    await userEvent.selectOptions(screen.getByTestId("visual"), "natal");
    expect(raiz.getAttribute("data-tema")).toBe("dark");
    expect(raiz.getAttribute("data-visual")).toBe("natal");
  });
});

/** Separa «a, b» nas vírgulas de topo (as de dentro de `:not(a, b)` não contam). */
function listaDeSeletores(texto: string): string[] {
  const partes: string[] = [];
  let nivel = 0;
  let atual = "";
  for (const c of texto) {
    if (c === "(") nivel++;
    if (c === ")") nivel--;
    if (c === "," && nivel === 0) {
      partes.push(atual);
      atual = "";
    } else atual += c;
  }
  partes.push(atual);
  return partes;
}

describe("registo dos temas", () => {
  const pasta = join(process.cwd(), "src", "temas");
  const ficheiros = readdirSync(pasta).filter((f) => f.endsWith(".css"));
  const principal = readFileSync(join(process.cwd(), "src", "main.tsx"), "utf8");

  it("tem ids únicos e válidos", () => {
    const ids = VISUAIS.map((v) => v.id);
    expect(new Set(ids).size).toBe(ids.length);
    for (const id of ids) expect(visualValido(id)).toBe(true);
    expect(visualValido("xpto")).toBe(false);
  });

  it("cada tema (menos o de omissão, que vive em estilos.css) tem a sua folha, importada em main.tsx", () => {
    for (const v of VISUAIS) {
      if (v.id === VISUAL_POR_OMISSAO) continue;
      expect(ficheiros, `falta temas/${v.id}.css`).toContain(`${v.id}.css`);
      expect(principal, `main.tsx não importa temas/${v.id}.css`).toContain(`./temas/${v.id}.css`);
    }
  });

  it("não há folhas de temas por registar", () => {
    const ids: string[] = VISUAIS.map((v) => v.id);
    for (const f of ficheiros)
      expect(ids, `temas/${f} não está em temas.ts`).toContain(f.replace(/\.css$/, ""));
  });

  it("cada folha só mexe no seu tema (nada de seletores soltos)", () => {
    for (const f of ficheiros) {
      const css = readFileSync(join(pasta, f), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
      const id = f.replace(/\.css$/, "");
      const seletores = [...css.matchAll(/(^|\})\s*([^{}@\s][^{}]*)\{/g)].map((m) => (m[2] ?? "").trim());
      for (const s of seletores) {
        if (/^(from|to|\d+%)$/.test(s)) continue; // passos de @keyframes
        for (const parte of listaDeSeletores(s)) {
          expect(parte.trim(), `${f}: «${parte.trim()}» não começa por :root[data-visual="${id}"]`).toMatch(
            new RegExp(`^:root\\[data-visual="${id}"\\]`),
          );
        }
      }
    }
  });
});
