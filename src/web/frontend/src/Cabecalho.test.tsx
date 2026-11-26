import { join } from "node:path";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import * as sass from "sass";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { calcularOcultos, type ItemId, SAI_PRIMEIRO } from "./Cabecalho";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

const TODOS: ItemId[] = [
  "ajuda",
  "sorteio",
  "precario",
  "sobre",
  "comentarios",
  "reportar",
  "donativo",
  "partilhar",
  "lingua",
  "visual",
  "tema",
];
const LARGURAS = new Map<ItemId, number>(TODOS.map((id) => [id, 100]));
const soma = (n: number) => n * 100 + (n - 1) * 8; // n itens de 100 px com 8 px entre eles

describe("o que sai do cabeçalho para o menu «hambúrguer»", () => {
  it("não tira nada quando tudo cabe", () => {
    expect(calcularOcultos(soma(11), LARGURAS, TODOS)).toEqual([]);
    expect(calcularOcultos(5000, LARGURAS, TODOS)).toEqual([]);
  });

  it("tira primeiro o modo claro/escuro, depois o visual, e por aí fora, deixando lugar ao botão do menu", () => {
    expect(calcularOcultos(soma(11) - 1, LARGURAS, TODOS)).toEqual(["tema"]); // 10 itens + o botão do menu
    expect(calcularOcultos(soma(9) + 8 + 44, LARGURAS, TODOS)).toEqual(["tema", "visual"]);
  });

  it("quanto menos espaço, mais itens vão para o menu, sempre pela ordem de prioridade", () => {
    let anterior = 0;
    for (let largura = soma(11); largura >= 0; largura -= 20) {
      const ocultos = calcularOcultos(largura, LARGURAS, TODOS);
      expect(ocultos.length).toBeGreaterThanOrEqual(anterior);
      anterior = ocultos.length;
      expect(ocultos).toEqual(SAI_PRIMEIRO.filter((id) => ocultos.includes(id)).slice(0, ocultos.length));
    }
  });

  it("sem espaço nenhum tudo vai para o menu (o nome da app tem de caber inteiro)", () => {
    expect(calcularOcultos(-30, LARGURAS, TODOS)).toEqual([...SAI_PRIMEIRO]);
    expect(calcularOcultos(0, LARGURAS, TODOS)).toEqual([...SAI_PRIMEIRO]);
  });

  it("sem donativo configurado esse item nem conta", () => {
    const sem = TODOS.filter((id) => id !== "donativo");
    expect(calcularOcultos(soma(10), LARGURAS, sem)).toEqual([]);
    expect(calcularOcultos(0, LARGURAS, sem)).toEqual(SAI_PRIMEIRO.filter((id) => id !== "donativo"));
  });

  it("aproveita as sobras de espaço: um item pequeno volta se couber", () => {
    const larguras = new Map<ItemId, number>(TODOS.map((id) => [id, id === "lingua" ? 300 : 100]));
    // sem o seletor de língua (300 px) sobra espaço: o «sobre» ou o «sorteio» (100 px) que saíram antes voltam ao cabeçalho
    const ocultos = calcularOcultos(500, larguras, TODOS);
    expect(ocultos).toContain("lingua");
    expect(TODOS.length - ocultos.length).toBeGreaterThanOrEqual(3);
  });
});

describe("o menu «hambúrguer» no cabeçalho", () => {
  beforeEach(() => {
    localStorage.clear();
    window.history.pushState({}, "", "/");
    new ServidorFalso().instalar();
  });
  afterEach(() => vi.restoreAllMocks());

  function abrir() {
    render(
      <ProvedorI18n>
        <App />
      </ProvedorI18n>,
    );
  }

  it("com espaço para tudo não há menu", async () => {
    abrir();
    await screen.findByTestId("nav-ajuda");
    expect(screen.queryByTestId("nav-burger")).toBeNull();
    for (const id of ["nav-sorteio", "nav-sobre", "lingua", "visual", "tema", "partilhar-abrir-topo"])
      expect(screen.getByTestId(id)).toBeInTheDocument();
  });

  it("sem espaço, o que não cabe passa para o menu e continua a funcionar", async () => {
    // 520 px de cabeçalho, 200 do nome e 100 por item: só cabem 2 itens e o botão do menu
    vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(520);
    vi.spyOn(HTMLElement.prototype, "offsetWidth", "get").mockImplementation(function (this: HTMLElement) {
      return this.classList.contains("marca") ? 200 : this.dataset.item ? 100 : 0;
    });
    abrir();
    const botao = await screen.findByTestId("nav-burger");
    expect(botao).toHaveAttribute("aria-label", "Menu");
    expect(botao).toHaveAttribute("aria-expanded", "false");
    // «Comentários» e «Reportar problema» são os últimos a sair: ficam à vista
    expect(screen.getByTestId("nav-comentarios")).toBeInTheDocument();
    expect(screen.getByTestId("nav-reportar-problema")).toBeInTheDocument();
    for (const id of [
      "nav-ajuda",
      "nav-sorteio",
      "nav-sobre",
      "partilhar-abrir-topo",
      "lingua",
      "visual",
      "tema",
    ])
      expect(screen.queryByTestId(id)).toBeNull();
    await userEvent.click(botao);
    const menu = screen.getByRole("list", { name: "Menu" });
    const dentro = within(menu);
    expect(dentro.getByTestId("burger-tutorial")).toBeInTheDocument(); // a Ajuda
    expect(dentro.getByTestId("burger-sorteio")).toBeInTheDocument();
    expect(dentro.getByTestId("burger-sobre")).toBeInTheDocument();
    expect(dentro.getByTestId("burger-lingua")).toHaveValue("pt");
    expect(dentro.getByTestId("burger-visual")).toBeInTheDocument();
    expect(dentro.getByTestId("burger-tema")).toBeInTheDocument();
    await userEvent.selectOptions(dentro.getByTestId("burger-tema"), "escuro");
    expect(localStorage.getItem("rifas.tema")).toBe("escuro");
    await userEvent.click(screen.getByTestId("nav-burger"));
    await userEvent.click(screen.getByTestId("nav-burger"));
    await userEvent.click(screen.getByTestId("burger-sorteio"));
    await waitFor(() => expect(window.location.pathname).toBe("/sorteio"));
    await waitFor(() => expect(screen.queryByRole("list", { name: "Menu" })).toBeNull()); // escolher fecha o menu
  });

  it("com o ecrã minúsculo tudo vai para o menu, até as ajudas, com os guias à vista", async () => {
    vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(300);
    vi.spyOn(HTMLElement.prototype, "offsetWidth", "get").mockImplementation(function (this: HTMLElement) {
      return this.classList.contains("marca") ? 250 : this.dataset.item ? 100 : 0;
    });
    abrir();
    await userEvent.click(await screen.findByTestId("nav-burger"));
    const menu = within(screen.getByRole("list", { name: "Menu" }));
    expect(menu.getByTestId("burger-tutorial")).toBeInTheDocument();
    expect(menu.getByTestId("burger-video")).toBeInTheDocument();
    expect(menu.getByTestId("guia-rifas-para-escolas")).toBeInTheDocument();
    expect(menu.getByTestId("partilhar-whatsapp")).toBeInTheDocument(); // as redes de «Partilhar», já abertas
    expect(menu.getByTestId("burger-comentarios")).toHaveAttribute("href", "/comentarios");
    expect(menu.getByTestId("burger-reportar")).toHaveAttribute("href", "/reportar-problema");
    expect(screen.queryByTestId("nav-ajuda")).toBeNull();
    expect(screen.queryByTestId("partilhar-abrir-topo")).toBeNull();
  });
});

describe("letra do seletor de língua", () => {
  it("usa a letra do sistema, não a da marca (evita descarregar glifos extra só para os nomes nativos)", () => {
    const css = sass.compile(join(__dirname, "estilos/_cabecalho.scss"), { style: "expanded" }).css;
    const bloco = css.match(/([^{}]+)\{\s*font-family:\s*system-ui[^}]*\}/);
    expect(bloco, "falta a regra do seletor de língua com a letra do sistema").toBeTruthy();
    const seletor = bloco?.[1] ?? "";
    for (const testid of ["lingua", "burger-lingua"]) {
      expect(seletor, `falta select[data-testid="${testid}"] nessa regra`).toContain(
        `[data-testid=${testid}]`,
      );
    }
  });
});
