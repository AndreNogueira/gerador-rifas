import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

beforeEach(() => {
  localStorage.clear();
  new ServidorFalso().instalar();
});

function abrir(caminho: string) {
  window.history.pushState({}, "", caminho);
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

describe("o índice dos guias «como fazer»", () => {
  it("/como-fazer lista todos os guias com título e resumo, e liga a cada um", async () => {
    abrir("/como-fazer");
    const indice = await screen.findByTestId("indice-guias");
    expect(within(indice).getByRole("heading", { level: 1 })).toHaveTextContent(
      "Como fazer uma rifa: guias passo a passo",
    );
    const escolas = await within(indice).findByTestId("indice-escolas");
    expect(escolas).toHaveAttribute("href", "/rifas-para-escolas");
    expect(escolas).toHaveTextContent("Como fazer uma rifa para a escola");
    expect(indice).toHaveTextContent("Uma forma simples de angariar fundos."); // o resumo ao lado da ligação
    expect(within(indice).getByTestId("indice-associacoes")).toHaveAttribute(
      "href",
      "/rifas-para-associacoes",
    );
    expect(document.title).toBe("Como fazer uma rifa: guias passo a passo | Gerador de Rifas");
  });

  it("no fim de cada guia há ligações para os outros guias (nunca para si próprio) e para o índice", async () => {
    abrir("/rifas-para-escolas");
    const outros = await screen.findByTestId("outros-guias");
    expect(within(outros).getByRole("heading", { level: 2 })).toHaveTextContent("Outros guias");
    expect(await within(outros).findByTestId("indice-associacoes")).toHaveAttribute(
      "href",
      "/rifas-para-associacoes",
    );
    expect(within(outros).queryByTestId("indice-escolas")).toBeNull();
    expect(within(outros).getByTestId("outros-guias-todos")).toHaveAttribute("href", "/como-fazer");
  });
});
