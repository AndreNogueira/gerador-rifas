import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ESPERA_PREVIA_MS } from "./Gerador";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;
const t = (id: string) => screen.getByTestId(id);
const ficheiro = (nome: string, tipo = "application/pdf") => new File(["%PDF-1.4 x"], nome, { type: tipo });
const previas = () => servidor.chamadas("POST", /\/previa$/);
const ESPERA = { timeout: ESPERA_PREVIA_MS * 5 + 1000 };

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  servidor = new ServidorFalso().instalar();
});
afterEach(() => vi.unstubAllGlobals());

async function abrirComTemplateEAlgarismos() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
  await userEvent.upload(await screen.findByTestId("upload-template"), ficheiro("Rifa Natal.pdf"));
  await waitFor(() => expect(t("estado-template")).toHaveTextContent("5 bilhetes"));
  await userEvent.upload(t("upload-algarismos"), ficheiro("digitos.png", "image/png"));
  await waitFor(() => expect(t("estado-algarismos")).toHaveTextContent("digitos.png"));
}

describe("pré-visualização automática", () => {
  it("aparece sozinha quando o template e os algarismos ficam prontos, sem carregar no botão", async () => {
    await abrirComTemplateEAlgarismos();
    expect(previas()).toHaveLength(0); // ainda dentro da espera
    await waitFor(() => expect(previas()).toHaveLength(1), ESPERA);
    await waitFor(() => expect(t("visor").getAttribute("src")).toContain("/previa.pdf?n=1"), ESPERA);
    expect(t("titulo-visor")).toHaveTextContent("Pré-visualização");
  });

  it("refaz-se quando se muda um campo que altera a página, mas não quando se muda só o nome do ficheiro", async () => {
    await abrirComTemplateEAlgarismos();
    await waitFor(() => expect(previas()).toHaveLength(1), ESPERA);
    fireEvent.change(t("nome"), { target: { value: "Rifa de Verão" } });
    await new Promise((r) => setTimeout(r, ESPERA_PREVIA_MS + 400));
    expect(previas()).toHaveLength(1); // o nome do ficheiro não muda a página
    fireEvent.change(t("algarismos"), { target: { value: "5" } });
    await waitFor(() => expect(previas()).toHaveLength(2), ESPERA);
    expect(previas()[1]?.corpo).toMatchObject({ digitos: "5" });
  });

  it("várias teclas seguidas dão um só pedido (a espera recomeça a cada alteração)", async () => {
    await abrirComTemplateEAlgarismos();
    await waitFor(() => expect(previas()).toHaveLength(1), ESPERA);
    for (const d of ["5", "6", "7"]) {
      fireEvent.change(t("algarismos"), { target: { value: d } });
      await new Promise((r) => setTimeout(r, 100));
    }
    await waitFor(() => expect(previas()).toHaveLength(2), ESPERA);
    await new Promise((r) => setTimeout(r, ESPERA_PREVIA_MS + 300));
    expect(previas()).toHaveLength(2);
    expect(previas()[1]?.corpo).toMatchObject({ digitos: "7" });
  });

  it("depois de «Pré-visualizar» à mão não faz outro pedido igual", async () => {
    await abrirComTemplateEAlgarismos();
    await userEvent.click(t("previa"));
    await waitFor(() => expect(previas().length).toBeGreaterThanOrEqual(1));
    const antes = previas().length;
    await new Promise((r) => setTimeout(r, ESPERA_PREVIA_MS + 400));
    expect(previas()).toHaveLength(antes);
  });

  it("um erro da pré-visualização automática aparece junto ao visor, sem janela, e não se repete sozinho", async () => {
    servidor.previaErro = "O número final tem de ser maior que o inicial.";
    await abrirComTemplateEAlgarismos();
    expect(await screen.findByTestId("previa-erro", {}, ESPERA)).toHaveTextContent("O número final");
    expect(screen.queryByRole("dialog")).toBeNull();
    const pedidos = previas().length;
    await new Promise((r) => setTimeout(r, ESPERA_PREVIA_MS + 400));
    expect(previas()).toHaveLength(pedidos); // não insiste até algo mudar
    servidor.previaErro = "";
    fireEvent.change(t("algarismos"), { target: { value: "6" } });
    await waitFor(() => expect(screen.queryByTestId("previa-erro")).toBeNull(), ESPERA);
  });

  it("não pede nada sem template e algarismos", async () => {
    render(
      <ProvedorI18n>
        <App />
      </ProvedorI18n>,
    );
    await screen.findByTestId("upload-template");
    fireEvent.change(t("algarismos"), { target: { value: "6" } });
    await new Promise((r) => setTimeout(r, ESPERA_PREVIA_MS + 400));
    expect(previas()).toHaveLength(0);
  });
});
