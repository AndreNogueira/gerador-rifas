import { render, screen, waitFor, within } from "@testing-library/react";
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
    await within(guia).findByTestId("outros-guias"); // já chegou a lista dos outros guias: a contagem seguinte tem de a ignorar
    expect(guia.querySelectorAll("ol > li")).toHaveLength(5);
    // as dicas, sem a lista «Outros guias» (que aparece quando o servidor responde: contá-la fazia o teste depender de quem chegava primeiro)
    expect(guia.querySelectorAll("ul:not(.lista-guias) > li")).toHaveLength(3);
    expect(within(guia).getByTestId("guia-gerador")).toHaveAttribute("href", "/");
    // o título do separador põe-se num efeito, depois de desenhar o guia: esperar por ele em vez de o ler logo (era a causa de um teste instável)
    await waitFor(() => expect(document.title).toContain("Como fazer uma rifa para a escola"));
  });

  it("os guias por tema (não por público) têm o seu endereço e o mesmo desenho", async () => {
    abrir("/como-numerar-bilhetes-de-rifa");
    const guia = await screen.findByTestId("guia-numerar");
    expect(
      await within(guia).findByRole("heading", { level: 1, name: "Como numerar os bilhetes de uma rifa" }),
    ).toBeInTheDocument();
    expect(guia.querySelectorAll("ol > li")).toHaveLength(5);
  });

  it("o guia do preçário (por tema, não por público) também tem a sua página", async () => {
    abrir("/como-fazer-o-precario-de-uma-festa");
    expect(await screen.findByTestId("guia-precario")).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { level: 1, name: "Como fazer o preçário de uma festa" }),
    ).toBeInTheDocument();
  });

  it("a das associações é outra página, com o seu próprio guia", async () => {
    abrir("/rifas-para-associacoes");
    expect(await screen.findByTestId("guia-associacoes")).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { level: 1, name: "Como fazer uma rifa para a associação" }),
    ).toBeInTheDocument();
  });

  it("o guia do sorteio liga à sua própria ferramenta (/sorteio), não ao gerador", async () => {
    abrir("/sorteio-de-rifa-verificavel");
    const guia = await screen.findByTestId("guia-sorteio");
    expect(await within(guia).findByTestId("guia-ferramenta")).toHaveAttribute("href", "/sorteio");
    expect(within(guia).queryByTestId("guia-gerador")).not.toBeInTheDocument();
  });

  it("o guia do preçário liga à sua própria ferramenta (/precario), não ao gerador", async () => {
    abrir("/como-fazer-o-precario-de-uma-festa");
    const guia = await screen.findByTestId("guia-precario");
    expect(await within(guia).findByTestId("guia-ferramenta")).toHaveAttribute("href", "/precario");
    expect(within(guia).queryByTestId("guia-gerador")).not.toBeInTheDocument();
  });
});
