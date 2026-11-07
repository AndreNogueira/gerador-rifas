import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ProvedorI18n, traduzir } from "./i18n";

describe("traduzir", () => {
  const textos = { ola: "Olá {nome}, tem {n} novas", simples: "sem parâmetros" };

  it("troca os parâmetros", () => {
    expect(traduzir(textos, "ola", { nome: "Ana", n: 3 })).toBe("Olá Ana, tem 3 novas");
  });
  it("deixa o que não foi dado, como o str.format do motor", () => {
    expect(traduzir(textos, "ola", { nome: "Ana" })).toBe("Olá Ana, tem {n} novas");
  });
  it("sem parâmetros devolve o texto tal e qual", () => {
    expect(traduzir(textos, "ola")).toBe("Olá {nome}, tem {n} novas");
    expect(traduzir(textos, "simples")).toBe("sem parâmetros");
  });
  it("chave desconhecida devolve a própria chave", () => {
    expect(traduzir(textos, "nao_existe")).toBe("nao_existe");
  });
});

const TEXTOS: Record<string, Record<string, string>> = {
  pt: {
    app_nome: "Gerador de Rifas",
    m_idioma: "Idioma",
    c1_titulo: "Template (PDF)",
    c2_titulo: "Algarismos",
    c3_titulo: "Números",
    c4_titulo: "Destino",
    previa_titulo: "Pré-visualização",
    previa_vazio: "vazio",
    previa: "Pré-visualizar",
    gerar: "Gerar PDFs",
  },
  en: {
    app_nome: "Raffle Generator",
    m_idioma: "Language",
    c1_titulo: "Template (PDF)",
    c2_titulo: "Digits",
    c3_titulo: "Numbers",
    c4_titulo: "Destination",
    previa_titulo: "Preview",
    previa_vazio: "empty",
    previa: "Preview",
    gerar: "Generate PDFs",
  },
};

function resposta(corpo: unknown, estado = 200) {
  return Promise.resolve(new Response(JSON.stringify(corpo), { status: estado }));
}

function comApi() {
  vi.stubGlobal(
    "fetch",
    vi.fn((url: string) => {
      if (url === "/health") return resposta({ estado: "ok", versao: "3.0.0" });
      if (url === "/api/linguas")
        return resposta({
          por_defeito: "pt",
          linguas: [
            { codigo: "pt", nome: "Português" },
            { codigo: "en", nome: "English" },
          ],
        });
      const m = /^\/api\/textos\/(\w+)$/.exec(url);
      if (m?.[1] && TEXTOS[m[1]]) return resposta({ lingua: m[1], textos: TEXTOS[m[1]] });
      return resposta({ detail: "não" }, 404);
    }),
  );
}

function renderApp() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

beforeEach(() => {
  localStorage.clear();
  comApi();
});
afterEach(() => vi.unstubAllGlobals());

describe("App", () => {
  it("mostra os 4 passos na língua do browser e a versão da API", async () => {
    renderApp();
    expect(await screen.findByRole("heading", { name: "Gerador de Rifas" })).toBeInTheDocument();
    for (const t of ["Template (PDF)", "Algarismos", "Números", "Destino"])
      expect(screen.getByText(t)).toBeInTheDocument();
    expect(await screen.findByText("v3.0.0")).toBeInTheDocument();
  });

  it("muda de língua e lembra-se dela", async () => {
    renderApp();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await userEvent.selectOptions(screen.getByTestId("lingua"), "en");
    expect(await screen.findByRole("heading", { name: "Raffle Generator" })).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("en");
    await waitFor(() => expect(localStorage.getItem("rifas.lingua")).toBe("en"));
  });

  it("usa a língua guardada em vez da do browser", async () => {
    localStorage.setItem("rifas.lingua", "en");
    renderApp();
    expect(await screen.findByRole("heading", { name: "Raffle Generator" })).toBeInTheDocument();
  });

  it("mostra o erro se a API falhar", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => resposta({ detail: "servidor em baixo" }, 503)),
    );
    renderApp();
    expect(await screen.findByRole("alert")).toHaveTextContent("servidor em baixo");
  });
});
