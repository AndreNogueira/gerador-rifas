import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { DESENHOS } from "./Galeria";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;
const t = (id: string) => screen.getByTestId(id);

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  servidor = new ServidorFalso().instalar();
  URL.createObjectURL = vi.fn(() => "blob:previa");
  URL.revokeObjectURL = vi.fn();
});
afterEach(() => vi.unstubAllGlobals());

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

const previas = () => servidor.chamadas("GET", /\/api\/galeria\/previa\.png/);

describe("galeria de templates (M4)", () => {
  it("só pede a pré-visualização com a galeria aberta e com os textos escritos", async () => {
    abrir();
    const galeria = await screen.findByTestId("galeria");
    expect(previas()).toHaveLength(0);
    await userEvent.click(galeria.querySelector("summary") as Element);
    await waitFor(() => expect(previas()).toHaveLength(1));
    expect(previas()[0]?.url).toContain("desenho=bosque");
    await userEvent.type(t("galeria-titulo"), "Rifa de Natal");
    await userEvent.click(t("galeria-desenho"));
    await userEvent.click(within(screen.getByRole("listbox")).getByRole("option", { name: "Natal" }));
    await waitFor(() =>
      expect(
        previas().some((p) => p.url.includes("desenho=natal") && p.url.includes("t=Rifa+de+Natal")),
      ).toBe(true),
    );
    expect(await screen.findByTestId("galeria-previa")).toHaveAttribute("src", "blob:previa");
  });

  it("«Usar este template» envia os textos e o template da galeria fica na sessão", async () => {
    abrir();
    await userEvent.click((await screen.findByTestId("galeria")).querySelector("summary") as Element);
    await userEvent.click(t("galeria-desenho"));
    await userEvent.click(within(screen.getByRole("listbox")).getByRole("option", { name: "Gala" }));
    await userEvent.type(t("galeria-titulo"), "Rifa");
    await userEvent.type(t("galeria-premio-1"), "1.º Cabaz");
    await userEvent.type(t("galeria-premio-3"), "3.º Livro");
    await userEvent.click(t("galeria-usar"));
    await waitFor(() => expect(t("estado-template")).toHaveTextContent("galeria"));
    const pedido = servidor.chamadas("POST", /\/galeria$/)[0]?.corpo;
    expect(pedido).toEqual({
      desenho: "gala",
      titulo: "Rifa",
      organizacao: "",
      premios: ["1.º Cabaz", "3.º Livro"],
      data: "",
    });
    expect(t("estado-algarismos")).toHaveTextContent("Vera");
    expect(await screen.findByTestId("papel")).toBeInTheDocument(); // uma rifa: aparece o painel da folha
  });

  it("o desenho escolhe-se numa caixa de uma linha, com um mini desenho em cada uma das 24 opções", async () => {
    abrir();
    await userEvent.click((await screen.findByTestId("galeria")).querySelector("summary") as Element);
    const botao = t("galeria-desenho");
    expect(botao).toHaveAttribute("role", "combobox");
    expect(botao).toHaveAttribute("aria-expanded", "false");
    expect(botao).toHaveTextContent("Bosque");
    expect(botao.querySelector("img")?.getAttribute("src")).toBe("/galeria/bosque.webp");
    expect(screen.queryByRole("listbox")).toBeNull();
    await userEvent.click(botao);
    expect(botao).toHaveAttribute("aria-expanded", "true");
    const opcoes = within(screen.getByRole("listbox")).getAllByRole("option");
    expect(opcoes).toHaveLength(DESENHOS.length);
    expect(opcoes.map((o) => o.textContent)).toEqual(DESENHOS.map((d) => d.nome));
    for (const [i, d] of DESENHOS.entries()) {
      expect(opcoes[i]?.querySelector("img")?.getAttribute("src")).toBe(`/galeria/${d.id}.webp`);
      expect(opcoes[i]).toHaveAttribute("aria-selected", String(d.id === "bosque"));
    }
    await userEvent.click(within(screen.getByRole("listbox")).getByRole("option", { name: "Praia" }));
    expect(screen.queryByRole("listbox")).toBeNull(); // fecha ao escolher
    expect(botao).toHaveTextContent("Praia");
    expect(botao.querySelector("img")?.getAttribute("src")).toBe("/galeria/praia.webp");
    await waitFor(() => expect(previas().some((p) => p.url.includes("desenho=praia"))).toBe(true));
  });

  it("o seletor do desenho funciona só com o teclado: setas, Home/End, letra, Enter e Esc", async () => {
    abrir();
    await userEvent.click((await screen.findByTestId("galeria")).querySelector("summary") as Element);
    const botao = t("galeria-desenho");
    botao.focus();
    await userEvent.keyboard("{ArrowDown}"); // abre
    expect(botao).toHaveAttribute("aria-expanded", "true");
    expect(botao).toHaveAttribute("aria-activedescendant", "galeria-desenho-bosque");
    await userEvent.keyboard("{ArrowDown}{ArrowDown}");
    expect(botao).toHaveAttribute("aria-activedescendant", "galeria-desenho-natal");
    await userEvent.keyboard("{End}");
    expect(botao).toHaveAttribute("aria-activedescendant", `galeria-desenho-${DESENHOS.at(-1)?.id}`);
    await userEvent.keyboard("{Home}{ArrowUp}"); // não passa do princípio
    expect(botao).toHaveAttribute("aria-activedescendant", "galeria-desenho-bosque");
    await userEvent.keyboard("m"); // o primeiro nome que começa por «m»
    expect(botao).toHaveAttribute("aria-activedescendant", "galeria-desenho-magusto");
    await userEvent.keyboard("{Enter}");
    expect(screen.queryByRole("listbox")).toBeNull();
    expect(botao).toHaveTextContent("Magusto");
    expect(botao).toHaveFocus();
    await userEvent.keyboard("{ArrowDown}{ArrowDown}{Escape}"); // Esc fecha sem escolher
    expect(screen.queryByRole("listbox")).toBeNull();
    expect(botao).toHaveTextContent("Magusto");
  });

  it("a pessoa escolhe quantos prémios quer: de 3 (o mínimo) a 10 (o máximo)", async () => {
    abrir();
    await userEvent.click((await screen.findByTestId("galeria")).querySelector("summary") as Element);
    const escolha = t("galeria-n-premios") as HTMLSelectElement;
    expect([...escolha.options].map((o) => o.value)).toEqual(["3", "4", "5", "6", "7", "8", "9", "10"]);
    expect(escolha.value).toBe("3");
    expect(screen.queryByTestId("galeria-premio-4")).toBeNull();
    await userEvent.selectOptions(escolha, "10");
    for (let i = 1; i <= 10; i++) await userEvent.type(t(`galeria-premio-${i}`), `${i}.º Prémio`);
    expect(screen.queryByTestId("galeria-premio-11")).toBeNull();
    await waitFor(() => expect(previas().some((p) => p.url.includes("p=10.%C2%BA+Pr%C3%A9mio"))).toBe(true));
    await userEvent.selectOptions(escolha, "4"); // menos caixas: os prémios escondidos não vão na rifa
    await userEvent.click(t("galeria-usar"));
    await waitFor(() => expect(servidor.chamadas("POST", /\/galeria$/)).toHaveLength(1));
    const corpo = servidor.chamadas("POST", /\/galeria$/)[0]?.corpo as { premios: string[] } | undefined;
    const premios = corpo?.premios;
    expect(premios).toEqual(["1.º Prémio", "2.º Prémio", "3.º Prémio", "4.º Prémio"]);
  });

  it("a data escolhe-se no calendário e depois escolhe-se como aparece na rifa", async () => {
    abrir();
    await userEvent.click((await screen.findByTestId("galeria")).querySelector("summary") as Element);
    expect(t("galeria-data")).toHaveAttribute("type", "date");
    fireEvent.change(t("galeria-data"), { target: { value: "2026-12-31" } });
    await userEvent.type(t("galeria-data-antes"), "Sorteio:");
    const formato = t("galeria-data-formato") as HTMLSelectElement;
    expect([...formato.options].map((o) => o.value)).toEqual([
      "curto",
      "medio",
      "longo",
      "completo",
      "livre",
    ]);
    expect(formato.options[2]?.textContent).toBe("31 de dezembro de 2026"); // as opções mostram a data escolhida já escrita
    const pediu = (d: string) =>
      previas().some((p) => p.url.includes(`d=${encodeURIComponent(d).replaceAll("%20", "+")}`));
    await waitFor(() => expect(pediu("Sorteio: 31 de dezembro de 2026")).toBe(true));
    await userEvent.selectOptions(formato, "curto");
    await waitFor(() => expect(pediu("Sorteio: 31/12/2026")).toBe(true));
    await userEvent.click(t("galeria-usar"));
    await waitFor(() => expect(servidor.chamadas("POST", /\/galeria$/)).toHaveLength(1));
    expect(servidor.chamadas("POST", /\/galeria$/)[0]?.corpo).toMatchObject({ data: "Sorteio: 31/12/2026" });
  });

  it("«Escrever à mão» troca o calendário por uma caixa de texto livre", async () => {
    abrir();
    await userEvent.click((await screen.findByTestId("galeria")).querySelector("summary") as Element);
    await userEvent.selectOptions(t("galeria-data-formato"), "livre");
    expect(screen.queryByTestId("galeria-data")).toBeNull();
    await userEvent.type(t("galeria-data-livre"), "No dia da festa");
    await userEvent.click(t("galeria-usar"));
    await waitFor(() => expect(servidor.chamadas("POST", /\/galeria$/)).toHaveLength(1));
    expect(servidor.chamadas("POST", /\/galeria$/)[0]?.corpo).toMatchObject({ data: "No dia da festa" });
  });

  it("textos que a letra não tem dão um aviso em vez da imagem e desativam «Usar»", async () => {
    servidor.galeriaErro = "O texto não pode ser usado no template da galeria («系»).";
    abrir();
    await userEvent.click((await screen.findByTestId("galeria")).querySelector("summary") as Element);
    expect(await screen.findByTestId("galeria-erro")).toHaveTextContent("«系»");
    expect(screen.queryByTestId("galeria-previa")).toBeNull();
    expect(t("galeria-usar")).toBeDisabled();
  });
});
