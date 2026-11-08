import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import type { Campos } from "./api";
import { camposDaLigacao, ligacaoDosCampos, PADRAO } from "./formulario";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;
const t = (id: string) => screen.getByTestId(id);

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  servidor = new ServidorFalso().instalar();
});
afterEach(() => vi.unstubAllGlobals());

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

describe("marcas de corte", () => {
  it("só aparecem com um template de uma rifa e vão nos pedidos", async () => {
    servidor.respostaTemplate = (s, nome) => ({
      ...s,
      template: { nome, estado: "ok", texto: "✔ Template com 1 rifa", detalhe: "" },
      info: { n_campos: 1, primeiro: "0001", ultimo: "0001", digitos: 4, tem_folha: true },
    });
    abrir();
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    expect(screen.queryByTestId("marcas")).not.toBeInTheDocument();
    await userEvent.upload(
      t("upload-template"),
      new File(["%PDF-1.4 x"], "uma.pdf", { type: "application/pdf" }),
    );
    const caixa = await screen.findByTestId("marcas");
    expect(caixa).not.toBeChecked();
    await userEvent.click(caixa);
    expect(caixa).toBeChecked();
    await waitFor(() => {
      const pedidos = servidor.chamadas("POST", /\/calcular$/);
      expect((pedidos[pedidos.length - 1]?.corpo as Campos | undefined)?.marcas).toBe("1");
    });
  });

  it("vão na ligação partilhada e lêem-se de volta", () => {
    const ligacao = ligacaoDosCampos({ ...PADRAO, marcas: "1" }, "https://x/");
    expect(new URL(ligacao).searchParams.get("mc")).toBe("1");
    expect(camposDaLigacao(new URL(ligacao).search).marcas).toBe("1");
    expect(ligacaoDosCampos(PADRAO, "https://x/")).not.toMatch(/mc=/);
    expect(camposDaLigacao("?mc=2")).toEqual({});
  });
});
