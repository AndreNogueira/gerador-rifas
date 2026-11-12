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

describe("guias «como fazer»", () => {
  it("a página das escolas mostra título, 5 passos, 3 dicas e as ligações", async () => {
    abrir("/rifas-para-escolas");
    const guia = await screen.findByTestId("guia-escolas");
    expect(
      await within(guia).findByRole("heading", { level: 1, name: "Como fazer uma rifa para a escola" }),
    ).toBeInTheDocument();
    expect(guia.querySelectorAll("ol > li")).toHaveLength(5);
    expect(guia.querySelectorAll("ul > li")).toHaveLength(3);
    expect(within(guia).getByTestId("guia-gerador")).toHaveAttribute("href", "/");
    expect(document.title).toContain("Como fazer uma rifa para a escola");
  });

  it("a das associações é outra página, com o seu próprio guia", async () => {
    abrir("/rifas-para-associacoes");
    expect(await screen.findByTestId("guia-associacoes")).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { level: 1, name: "Como fazer uma rifa para a associação" }),
    ).toBeInTheDocument();
  });

  it("o rodapé liga aos dois guias", async () => {
    abrir("/");
    const rodape = await screen.findByRole("navigation", { name: "Informação" });
    expect(within(rodape).getByRole("link", { name: "Para escolas" })).toHaveAttribute(
      "href",
      "/rifas-para-escolas",
    );
    expect(within(rodape).getByRole("link", { name: "Para associações" })).toHaveAttribute(
      "href",
      "/rifas-para-associacoes",
    );
  });
});
