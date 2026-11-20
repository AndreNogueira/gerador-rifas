import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { App } from "./App";
import { MENU_COMO_FAZER } from "./Cabecalho";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  new ServidorFalso().instalar();
});

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

describe("o menu «Ajuda» no cabeçalho (tutorial, vídeo e «como fazer» num só separador)", () => {
  it("abre uma lista com o tutorial, o vídeo e todos os guias", async () => {
    abrir();
    const botao = await screen.findByTestId("nav-ajuda");
    expect(botao).toHaveTextContent("Ajuda");
    expect(botao).toHaveAttribute("aria-expanded", "false");
    const nav = botao.closest("nav") as HTMLElement;
    // o cabeçalho só tem o menu e as páginas soltas (com os comentários e o reportar problema): o tutorial e o vídeo já não são separadores à parte
    expect([...nav.querySelectorAll("a, button")].map((e) => e.getAttribute("data-testid"))).toEqual([
      "nav-ajuda",
      "nav-sorteio",
      "nav-precario",
      "nav-sobre",
      "nav-comentarios",
      "nav-reportar-problema",
    ]);
    expect(screen.queryByTestId("guia-rifas-para-escolas")).toBeNull();
    await userEvent.click(botao);
    expect(botao).toHaveAttribute("aria-expanded", "true");
    const lista = document.getElementById("menu-ajuda") as HTMLElement;
    const ligacoes = within(lista).getAllByRole("link");
    expect(ligacoes.map((a) => a.getAttribute("href"))).toEqual([
      "/tutorial",
      "/video",
      "/como-fazer", // o índice de todos os guias, à frente de cada um
      ...MENU_COMO_FAZER.map((g) => g.para),
    ]);
    expect(ligacoes.map((a) => a.textContent)).toEqual([
      "Tutorial",
      "Vídeo tutorial",
      "Todos os guias",
      "Para escolas",
      "Para associações",
      "Para clubes",
      "Para bombeiros",
      "Para festas de bairro",
      "Para paróquias",
    ]);
    expect(within(lista).getByText("Como fazer")).toBeInTheDocument(); // o título do segundo grupo
  });

  it("escolher um guia navega para ele, fecha a lista e marca o menu como página atual", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("nav-ajuda"));
    await userEvent.click(screen.getByTestId("guia-rifas-para-clubes"));
    await waitFor(() => expect(window.location.pathname).toBe("/rifas-para-clubes"));
    await waitFor(() => expect(document.getElementById("menu-ajuda")).toBeNull());
    expect(screen.getByTestId("nav-ajuda")).toHaveAttribute("aria-current", "page");
  });

  it("o tutorial e o vídeo também marcam o menu como página atual", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("nav-ajuda"));
    await userEvent.click(screen.getByTestId("nav-video"));
    await waitFor(() => expect(window.location.pathname).toBe("/video"));
    expect(screen.getByTestId("nav-ajuda")).toHaveAttribute("aria-current", "page");
  });

  it("fecha com Esc (e devolve o foco ao botão) e ao tocar fora", async () => {
    abrir();
    const botao = await screen.findByTestId("nav-ajuda");
    await userEvent.click(botao);
    expect(document.getElementById("menu-ajuda")).not.toBeNull();
    await userEvent.keyboard("{Escape}");
    expect(document.getElementById("menu-ajuda")).toBeNull();
    expect(botao).toHaveFocus();
    await userEvent.click(botao);
    await userEvent.click(document.body);
    expect(document.getElementById("menu-ajuda")).toBeNull();
  });

  it("o rodapé já não repete os guias (vivem só neste menu)", async () => {
    abrir();
    const rodape = await screen.findByRole("navigation", { name: "Informação" });
    for (const g of MENU_COMO_FAZER) expect(rodape.querySelector(`a[href="${g.para}"]`)).toBeNull();
  });
});

describe("o botão Partilhar no cabeçalho", () => {
  it("está no cabeçalho, não no rodapé, e abre um painel com as redes", async () => {
    abrir();
    const botao = await screen.findByTestId("partilhar-abrir-topo");
    expect(botao.closest("header")).not.toBeNull();
    expect(document.querySelector("footer [data-testid^='partilhar-']")).toBeNull();
    await userEvent.click(botao);
    const lista = screen.getByRole("list", { name: "Partilhar" });
    for (const id of ["whatsapp", "telegram", "facebook", "email"]) {
      const ligacao = within(lista).getByTestId(`partilhar-${id}`);
      expect(ligacao.querySelector("svg")).not.toBeNull(); // cada rede tem o seu ícone
    }
    await userEvent.keyboard("{Escape}");
    expect(screen.queryByRole("list", { name: "Partilhar" })).toBeNull();
  });
});
