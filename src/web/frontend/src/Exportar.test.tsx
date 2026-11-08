import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { nomeSeguro } from "./Gerador";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;
let descargas: string[];

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  servidor = new ServidorFalso().instalar();
  descargas = [];
  URL.createObjectURL = vi.fn(() => "blob:falso");
  URL.revokeObjectURL = vi.fn();
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (this: HTMLAnchorElement) {
    descargas.push(this.download);
  });
});
afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

describe("exportar a lista e a folha de controlo (M2)", () => {
  it("o CSV e a folha pedem o que está no formulário e descarregam com o nome da rifa", async () => {
    abrir();
    await userEvent.type(await screen.findByTestId("nome"), "Rifa de Natal");
    await userEvent.type(screen.getByTestId("prefixos"), "A-");
    await userEvent.click(screen.getByTestId("exportar-csv"));
    await waitFor(() => expect(descargas).toEqual(["Rifa de Natal.csv"]));
    const csv = servidor.chamadas("POST", /\/api\/exportar\/lista\.csv$/)[0];
    expect(csv?.corpo).toMatchObject({ nome: "Rifa de Natal", prefixos: "A-", inicio: "1", fim: "1000" });
    await userEvent.click(screen.getByTestId("exportar-controlo"));
    await waitFor(() => expect(descargas).toEqual(["Rifa de Natal.csv", "Controlo - Rifa de Natal.pdf"]));
    expect(servidor.chamadas("POST", /\/api\/exportar\/controlo\.pdf$/)).toHaveLength(1);
  });

  it("sem nome o ficheiro chama-se «rifas»", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("exportar-csv"));
    await waitFor(() => expect(descargas).toEqual(["rifas.csv"]));
  });

  it("se o servidor recusar mostra o aviso e não descarrega nada", async () => {
    servidor.exportarErro = "No máximo 30 000 números por pedido.";
    abrir();
    await userEvent.click(await screen.findByTestId("exportar-csv"));
    expect(await screen.findByText("No máximo 30 000 números por pedido.")).toBeInTheDocument();
    expect(descargas).toEqual([]);
  });

  it("nomeSeguro tira o que o Windows não aceita e os pontos e espaços das pontas", () => {
    expect(nomeSeguro('  Rifa: "Natal" <2026>/a\\b|c?d*  ')).toBe("Rifa Natal 2026abcd");
    expect(nomeSeguro("..")).toBe("");
    expect(nomeSeguro("x".repeat(200))).toHaveLength(80);
  });
});
