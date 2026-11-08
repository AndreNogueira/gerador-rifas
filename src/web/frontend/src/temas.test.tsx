import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import * as sass from "sass";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";
import { visualPorEpoca } from "./tema";
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
  vi.useFakeTimers({ toFake: ["Date"] }); // o tema automático depende do mês: os testes fixam-no em junho
  vi.setSystemTime(new Date(2026, 5, 10));
  new ServidorFalso().instalar();
});
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("tema por época", () => {
  it("em dezembro o tema automático é o Natal; nos outros meses o Premiado", () => {
    expect(visualPorEpoca(new Date(2026, 11, 1))).toBe("natal");
    expect(visualPorEpoca(new Date(2026, 11, 31))).toBe("natal");
    expect(visualPorEpoca(new Date(2026, 10, 30))).toBe(VISUAL_POR_OMISSAO);
    expect(visualPorEpoca(new Date(2027, 0, 1))).toBe(VISUAL_POR_OMISSAO);
  });

  it("em dezembro arranca em Natal sem guardar nada, e escolher o Premiado fica guardado", async () => {
    vi.setSystemTime(new Date(2026, 11, 20));
    abrir();
    const seletor = await screen.findByTestId("visual");
    expect(raiz.getAttribute("data-visual")).toBe("natal");
    expect(localStorage.getItem("rifas.visual")).toBeNull();
    await userEvent.selectOptions(seletor, "premiado");
    expect(localStorage.getItem("rifas.visual")).toBe("premiado");
    await userEvent.selectOptions(seletor, "natal"); // voltar ao automático não deixa rasto
    expect(localStorage.getItem("rifas.visual")).toBeNull();
  });
});

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

/** Declarações de um bloco CSS, separadas por «;» fora de parênteses. */
function declaracoes(corpo: string): [string, string][] {
  const saida: [string, string][] = [];
  let nivel = 0;
  let atual = "";
  const fechar = () => {
    const i = atual.indexOf(":");
    if (i > 0) saida.push([atual.slice(0, i).trim(), atual.slice(i + 1).trim()]);
    atual = "";
  };
  for (const c of corpo) {
    if (c === "(") nivel++;
    if (c === ")") nivel--;
    if (c === ";" && nivel === 0) fechar();
    else atual += c;
  }
  if (atual.trim()) fechar();
  return saida;
}

const raizSrc = join(process.cwd(), "src");
const pastaTemas = join(raizSrc, "estilos", "temas");
const nomesDe = (ficheiro: string) =>
  new Set(
    [...readFileSync(join(raizSrc, "estilos", ficheiro), "utf8").matchAll(/^\s*(--[a-z0-9-]+)\s*:/gm)].map(
      (m) => m[1] as string,
    ),
  );
const PERMITIDAS = nomesDe("_tokens.scss"); // o que um tema pode mudar
const GEOMETRIA = nomesDe("_geometria.scss"); // o que NUNCA muda com o tema

describe("registo dos temas", () => {
  const ficheiros = readdirSync(pastaTemas).filter((f) => f.endsWith(".scss") && f !== "_index.scss");
  const indice = readFileSync(join(pastaTemas, "_index.scss"), "utf8");
  const idDe = (f: string) => f.replace(/^_/, "").replace(/\.scss$/, "");

  it("tem ids únicos e válidos", () => {
    const ids = VISUAIS.map((v) => v.id);
    expect(new Set(ids).size).toBe(ids.length);
    for (const id of ids) expect(visualValido(id)).toBe(true);
    expect(visualValido("xpto")).toBe(false);
  });

  it("cada tema (menos o de omissão, que vive em _tokens.scss) tem a sua folha, juntada em _index.scss", () => {
    for (const v of VISUAIS) {
      if (v.id === VISUAL_POR_OMISSAO) continue;
      expect(ficheiros, `falta estilos/temas/_${v.id}.scss`).toContain(`_${v.id}.scss`);
      expect(indice, `_index.scss não faz @forward "${v.id}"`).toContain(`@forward "${v.id}";`);
    }
  });

  it("não há folhas de temas por registar", () => {
    const ids: string[] = VISUAIS.map((v) => v.id);
    for (const f of ficheiros) expect(ids, `${f} não está em temas.ts`).toContain(idDe(f));
  });
});

describe("a estrutura não muda com o tema", () => {
  const ficheiros = readdirSync(pastaTemas).filter((f) => f.endsWith(".scss") && f !== "_index.scss");

  it("os ficheiros de tokens e de geometria declaram variáveis (senão este teste não protegia nada)", () => {
    expect(PERMITIDAS.size).toBeGreaterThan(60);
    expect(GEOMETRIA.has("--corte")).toBe(true);
  });

  for (const f of ficheiros) {
    const id = f.replace(/^_/, "").replace(/\.scss$/, "");
    it(`${id}: um só bloco :root[data-visual="${id}"], só com variáveis permitidas`, () => {
      const css = sass
        .compile(join(pastaTemas, f), { style: "expanded" })
        .css.replace(/\/\*[\s\S]*?\*\//g, "");
      expect(css, "um tema não pode ter @-regras (@media, @keyframes…)").not.toMatch(/@/);
      const blocos = [...css.matchAll(/([^{}]+)\{([^{}]*)\}/g)];
      expect(blocos, "um tema é UM bloco").toHaveLength(1);
      const [, seletor, corpo] = blocos[0] as RegExpMatchArray;
      // o Sass tira as aspas do atributo ([data-visual=natal]): é o mesmo seletor
      expect((seletor ?? "").trim().replaceAll('"', "")).toBe(`:root[data-visual=${id}]`);
      for (const [nome] of declaracoes(corpo ?? "")) {
        expect(nome.startsWith("--"), `${id}: «${nome}» não é uma variável (só se mudam variáveis)`).toBe(
          true,
        );
        expect(GEOMETRIA.has(nome), `${id}: «${nome}» é geometria (fixa em todos os temas)`).toBe(false);
        expect(
          PERMITIDAS.has(nome) || nome.startsWith("--t-"),
          `${id}: «${nome}» não está em _tokens.scss (junta-a lá, com o valor do Premiado, antes de a usar)`,
        ).toBe(true);
      }
    });
  }

  it("a app só tem um ponto de entrada de estilos (main.scss) e nenhum CSS solto", () => {
    const entradas: string[] = [];
    const ver = (pasta: string) => {
      for (const e of readdirSync(pasta, { withFileTypes: true })) {
        const caminho = join(pasta, e.name);
        if (e.isDirectory()) ver(caminho);
        else if (/\.(css|scss)$/.test(e.name) && !caminho.includes(join("src", "estilos")))
          entradas.push(caminho);
        else if (/\.tsx?$/.test(e.name) && !e.name.endsWith(".test.tsx")) {
          for (const m of readFileSync(caminho, "utf8").matchAll(/^import\s+"([^"]+\.s?css)"/gm))
            entradas.push(`${e.name}: ${m[1]}`);
        }
      }
    };
    ver(raizSrc);
    expect(entradas).toEqual(["main.tsx: ./estilos/main.scss"]);
  });
});
