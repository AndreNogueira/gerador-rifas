import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
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
    await userEvent.click(screen.getByLabelText("Natal"));
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
    await userEvent.click(screen.getByLabelText("Gala"));
    await userEvent.type(t("galeria-titulo"), "Rifa");
    const premios = screen.getAllByLabelText("Prémios (uma linha cada, até 3)");
    await userEvent.type(premios[0] as Element, "1.º Cabaz");
    await userEvent.type(premios[2] as Element, "3.º Livro");
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

  it("textos que a letra não tem dão um aviso em vez da imagem e desativam «Usar»", async () => {
    servidor.galeriaErro = "O texto não pode ser usado no template da galeria («系»).";
    abrir();
    await userEvent.click((await screen.findByTestId("galeria")).querySelector("summary") as Element);
    expect(await screen.findByTestId("galeria-erro")).toHaveTextContent("«系»");
    expect(screen.queryByTestId("galeria-previa")).toBeNull();
    expect(t("galeria-usar")).toBeDisabled();
  });
});
