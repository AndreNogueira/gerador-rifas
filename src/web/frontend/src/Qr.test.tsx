import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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
  servidor.respostaTemplate = (s, nome) => ({
    ...s,
    template: { nome, estado: "ok", texto: "✔ Template com 1 rifa", detalhe: "" },
    info: { n_campos: 1, primeiro: "0001", ultimo: "0001", digitos: 4, tem_folha: true },
  });
});
afterEach(() => vi.unstubAllGlobals());

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

async function comTemplate() {
  await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
  await userEvent.upload(
    t("upload-template"),
    new File(["%PDF-1.4 x"], "uma.pdf", { type: "application/pdf" }),
  );
  await screen.findByTestId("papel");
}

describe("QR de verificação (M6)", () => {
  it("sem a chave no servidor a opção nem aparece", async () => {
    servidor.temQr = false;
    abrir();
    await comTemplate();
    await waitFor(() => expect(servidor.chamadas("GET", /\/api\/publico$/).length).toBeGreaterThan(0));
    expect(screen.queryByTestId("qr")).toBeNull();
  });

  it("com a chave aparece só num template de uma rifa; mostra o canto e o tamanho ao ligar e vai nos pedidos", async () => {
    servidor.temQr = true;
    abrir();
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    expect(screen.queryByTestId("qr")).toBeNull(); // ainda sem template de uma rifa
    await userEvent.upload(
      t("upload-template"),
      new File(["%PDF-1.4 x"], "uma.pdf", { type: "application/pdf" }),
    );
    const caixa = await screen.findByTestId("qr");
    expect(screen.queryByTestId("qr-posicao")).toBeNull();
    await userEvent.click(caixa);
    await userEvent.selectOptions(t("qr-posicao"), "sd");
    fireEvent.change(t("qr-tamanho"), { target: { value: "34" } });
    await waitFor(() => {
      const pedidos = servidor.chamadas("POST", /\/calcular$/);
      expect(pedidos[pedidos.length - 1]?.corpo).toMatchObject({
        qr: "1",
        qr_posicao: "sd",
        qr_tamanho: "34",
      });
    });
  });

  it("vai na ligação partilhada", () => {
    const ligacao = ligacaoDosCampos({ ...PADRAO, qr: "1" } as Campos, "https://x/");
    expect(new URL(ligacao).searchParams.get("qr")).toBe("1");
    expect(camposDaLigacao(new URL(ligacao).search).qr).toBe("1");
    expect(ligacaoDosCampos(PADRAO, "https://x/")).not.toMatch(/qr=/);
    expect(camposDaLigacao("?qr=2")).toEqual({});
  });
});
