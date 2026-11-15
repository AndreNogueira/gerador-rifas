import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ProvedorI18n } from "./i18n";
import { SeletorData } from "./SeletorData";
import { ServidorFalso } from "./servidor-falso";

beforeEach(() => {
  localStorage.clear();
  new ServidorFalso().instalar();
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(new Date("2026-11-15T12:00:00Z"));
});
afterEach(() => vi.useRealTimers());

function mostrar(valor: string, aoMudar = vi.fn()) {
  render(
    <ProvedorI18n>
      <SeletorData valor={valor} aoMudar={aoMudar} rotulo="Data do sorteio" testid="data" />
    </ProvedorI18n>,
  );
  return aoMudar;
}
const calendario = () => screen.getByRole("dialog", { name: "Data do sorteio" });
const dia = (iso: string) => calendario().querySelector(`[data-iso="${iso}"]`) as HTMLElement;

describe("o calendário da data do sorteio", () => {
  it("sem data mostra o convite traduzido; com data, escrita como a língua a escreve", async () => {
    mostrar("");
    expect(await screen.findByText("Escolher a data")).toBeInTheDocument();
  });

  it("com data mostra-a em dd/mm/aaaa (português) e abre no mês dela, com os nomes na língua", async () => {
    mostrar("2026-12-31");
    const botao = await screen.findByTestId("data");
    expect(botao).toHaveTextContent("31/12/2026");
    expect(botao).toHaveAccessibleName("Data do sorteio: 31/12/2026");
    expect(botao).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(botao);
    expect(botao).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByTestId("data-mes")).toHaveTextContent(/dezembro de 2026/i);
    const cabecalhos = within(calendario()).getAllByRole("columnheader");
    expect(cabecalhos).toHaveLength(7);
    expect(cabecalhos[0]).toHaveTextContent(/^seg/i); // a semana começa à segunda-feira em português
    expect(dia("2026-12-31")).toHaveAttribute("aria-pressed", "true");
    expect(dia("2026-12-31")).toHaveAccessibleName(/quinta-feira, 31 de dezembro de 2026/i);
    expect(dia("2026-12-31")).toHaveFocus();
    expect(calendario().parentElement).toBe(document.body); // fora dos cartões, que têm máscara
  });

  it("escolher um dia fecha o calendário e devolve aaaa-mm-dd", async () => {
    const aoMudar = mostrar("2026-12-31");
    await userEvent.click(await screen.findByTestId("data"));
    await userEvent.click(dia("2026-12-25"));
    expect(aoMudar).toHaveBeenCalledWith("2026-12-25");
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(screen.getByTestId("data")).toHaveFocus();
  });

  it("as setas do mês, «Hoje» e «Limpar» usam os textos traduzidos", async () => {
    const aoMudar = mostrar("2026-12-31");
    await userEvent.click(await screen.findByTestId("data"));
    await userEvent.click(screen.getByRole("button", { name: "Mês seguinte" }));
    expect(screen.getByTestId("data-mes")).toHaveTextContent(/janeiro de 2027/i);
    await userEvent.click(screen.getByRole("button", { name: "Mês anterior" }));
    await userEvent.click(screen.getByRole("button", { name: "Mês anterior" }));
    expect(screen.getByTestId("data-mes")).toHaveTextContent(/novembro de 2026/i);
    await userEvent.click(screen.getByRole("button", { name: "Hoje" }));
    expect(aoMudar).toHaveBeenLastCalledWith("2026-11-15");
    await userEvent.click(screen.getByTestId("data"));
    await userEvent.click(screen.getByRole("button", { name: "Limpar" }));
    expect(aoMudar).toHaveBeenLastCalledWith("");
  });

  it("teclado: setas movem o dia (e o mês), Enter escolhe, Esc fecha", async () => {
    const aoMudar = mostrar("2026-12-31");
    await userEvent.click(await screen.findByTestId("data"));
    await userEvent.keyboard("{ArrowRight}");
    expect(dia("2027-01-01")).toHaveFocus();
    expect(screen.getByTestId("data-mes")).toHaveTextContent(/janeiro de 2027/i);
    await userEvent.keyboard("{ArrowDown}");
    expect(dia("2027-01-08")).toHaveFocus();
    await userEvent.keyboard("{PageUp}");
    expect(dia("2026-12-08")).toHaveFocus();
    await userEvent.keyboard("{Enter}");
    expect(aoMudar).toHaveBeenCalledWith("2026-12-08");
    await userEvent.click(screen.getByTestId("data"));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    await userEvent.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).toBeNull();
  });
});
