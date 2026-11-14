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

describe("o grupo «Como fazer» no cabeçalho", () => {
  it("fica ao lado do tutorial e abre uma lista com todos os guias", async () => {
    abrir();
    const botao = await screen.findByTestId("nav-como-fazer");
    expect(botao).toHaveTextContent("Como fazer");
    expect(botao).toHaveAttribute("aria-expanded", "false");
    const nav = botao.closest("nav") as HTMLElement;
    const ordem = [...nav.querySelectorAll("a, button")].map((e) => e.getAttribute("data-testid"));
    expect(ordem.slice(0, 2)).toEqual(["nav-tutorial", "nav-como-fazer"]); // logo a seguir ao tutorial
    expect(screen.queryByTestId("guia-rifas-para-escolas")).toBeNull();
    await userEvent.click(botao);
    expect(botao).toHaveAttribute("aria-expanded", "true");
    const lista = document.getElementById("menu-como-fazer") as HTMLElement;
    const ligacoes = within(lista).getAllByRole("link");
    expect(ligacoes).toHaveLength(MENU_COMO_FAZER.length);
    expect(ligacoes.map((a) => a.getAttribute("href"))).toEqual(MENU_COMO_FAZER.map((g) => g.para));
    expect(ligacoes.map((a) => a.textContent)).toEqual([
      "Para escolas",
      "Para associações",
      "Para clubes",
      "Para bombeiros",
      "Para festas de bairro",
      "Para paróquias",
    ]);
  });

  it("escolher um guia navega para ele, fecha a lista e marca o grupo como página atual", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("nav-como-fazer"));
    await userEvent.click(screen.getByTestId("guia-rifas-para-clubes"));
    await waitFor(() => expect(window.location.pathname).toBe("/rifas-para-clubes"));
    await waitFor(() => expect(document.getElementById("menu-como-fazer")).toBeNull());
    expect(screen.getByTestId("nav-como-fazer")).toHaveAttribute("aria-current", "page");
  });

  it("fecha com Esc (e devolve o foco ao botão) e ao tocar fora", async () => {
    abrir();
    const botao = await screen.findByTestId("nav-como-fazer");
    await userEvent.click(botao);
    expect(document.getElementById("menu-como-fazer")).not.toBeNull();
    await userEvent.keyboard("{Escape}");
    expect(document.getElementById("menu-como-fazer")).toBeNull();
    expect(botao).toHaveFocus();
    await userEvent.click(botao);
    await userEvent.click(document.body);
    expect(document.getElementById("menu-como-fazer")).toBeNull();
  });

  it("o rodapé já não repete os guias (vivem só neste grupo)", async () => {
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
