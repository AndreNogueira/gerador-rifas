import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

const t = (id: string) => screen.getByTestId(id);

beforeEach(() => {
  localStorage.clear();
  new ServidorFalso().instalar();
});
afterEach(() => vi.unstubAllGlobals());

function abrir(url = "/sorteio") {
  window.history.pushState({}, "", url);
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

const sorteados = () => Array.from(t("sorteio-resultado").querySelectorAll("li")).map((l) => l.textContent);

describe("página do sorteio (M7)", () => {
  it("sorteia com a semente e dá os números de referência; o título do separador é «Sorteio»", async () => {
    abrir();
    await userEvent.type(await screen.findByTestId("sorteio-semente"), "semente-um");
    await userEvent.clear(t("sorteio-n"));
    await userEvent.type(t("sorteio-n"), "3");
    await userEvent.click(t("sorteio-sortear"));
    expect(sorteados()).toEqual(["29", "38", "74"]); // os mesmos vetores de tests/test_sorteio.py
    await waitFor(() => expect(document.title).toBe("Sorteio | Gerador de Rifas"));
    expect(window.location.search).toContain("s=semente-um"); // o endereço repete o sorteio
  });

  it("os números a saltar não saem", async () => {
    abrir();
    await userEvent.clear(await screen.findByTestId("sorteio-ate"));
    await userEvent.type(t("sorteio-ate"), "7");
    await userEvent.type(t("sorteio-x"), "1-6");
    await userEvent.type(t("sorteio-semente"), "x");
    await userEvent.click(t("sorteio-sortear"));
    expect(sorteados()).toEqual(["7"]);
  });

  it("uma ligação partilhada repete logo o sorteio, e o resultado é o mesmo", async () => {
    abrir("/sorteio?de=1&ate=1000&n=5&s=drand%3A5000000%3Aabcdef");
    await screen.findByTestId("sorteio-resultado");
    expect(sorteados()).toEqual(["401", "161", "907", "932", "644"]);
    expect(t("sorteio-semente")).toHaveValue("drand:5000000:abcdef");
  });

  it("avisa o que falta ou não serve, sem sortear", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("sorteio-sortear"));
    expect(t("sorteio-erro")).toHaveTextContent("semente pública");
    await userEvent.type(t("sorteio-semente"), "s");
    await userEvent.clear(t("sorteio-n"));
    await userEvent.type(t("sorteio-n"), "500");
    await userEvent.click(t("sorteio-sortear"));
    expect(t("sorteio-erro")).toHaveTextContent("intervalo válido");
    await userEvent.clear(t("sorteio-n"));
    await userEvent.type(t("sorteio-n"), "1");
    await userEvent.type(t("sorteio-x"), "abc");
    await userEvent.click(t("sorteio-sortear"));
    expect(t("sorteio-erro")).toHaveTextContent("«Saltar»");
    expect(screen.queryByTestId("sorteio-resultado")).toBeNull();
  });

  it("a semente do drand preenche o campo; se falhar avisa", async () => {
    abrir();
    const fetchOriginal = globalThis.fetch;
    vi.stubGlobal("fetch", (url: string, init?: RequestInit) =>
      url === "https://api.drand.sh/public/latest"
        ? Promise.resolve(new Response(JSON.stringify({ round: 123, randomness: "abc123" }), { status: 200 }))
        : fetchOriginal(url, init),
    );
    await userEvent.click(await screen.findByTestId("sorteio-drand"));
    await waitFor(() => expect(t("sorteio-semente")).toHaveValue("drand:123:abc123"));
    vi.stubGlobal("fetch", () => Promise.reject(new TypeError("sem rede")));
    await userEvent.click(t("sorteio-drand"));
    expect(await screen.findByTestId("dialogo-texto")).toHaveTextContent("semente do drand");
  });

  it("«Copiar ligação» copia o endereço que repete o sorteio", async () => {
    const escrever = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText: escrever }, configurable: true });
    abrir("/sorteio?de=1&ate=100&n=2&s=abc&x=13");
    await userEvent.click(await screen.findByTestId("sorteio-copiar"));
    await waitFor(() => expect(escrever).toHaveBeenCalledTimes(1));
    const ligacao = new URL(escrever.mock.calls[0]?.[0] as string);
    expect(ligacao.pathname).toBe("/sorteio");
    expect(Object.fromEntries(ligacao.searchParams)).toEqual({
      de: "1",
      ate: "100",
      n: "2",
      s: "abc",
      x: "13",
    });
  });

  it("o menu leva à página do sorteio", async () => {
    window.history.pushState({}, "", "/");
    render(
      <ProvedorI18n>
        <App />
      </ProvedorI18n>,
    );
    await userEvent.click(await screen.findByTestId("nav-sorteio"));
    expect(await screen.findByTestId("sorteio-sortear")).toBeInTheDocument();
  });
});
