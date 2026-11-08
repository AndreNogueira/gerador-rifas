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
const imagem = (nome = "logo.png") => new File(["\x89PNG"], nome, { type: "image/png" });

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

function umaRifa() {
  servidor.respostaTemplate = (s, nome) => ({
    ...s,
    template: { nome, estado: "ok", texto: "✔ Template com 1 rifa", detalhe: "" },
    info: { n_campos: 1, primeiro: "0001", ultimo: "0001", digitos: 4, tem_folha: true },
  });
}

describe("marca própria (M5)", () => {
  it("a cor dos números vai nos pedidos, em qualquer template, e limpa-se", async () => {
    abrir();
    const cor = await screen.findByTestId("cor-numeros");
    expect(screen.queryByTestId("cor-numeros-limpar")).toBeNull();
    fireEvent.change(cor, { target: { value: "#1e88e5" } });
    await waitFor(() => {
      const pedidos = servidor.chamadas("POST", /\/calcular$/);
      expect((pedidos[pedidos.length - 1]?.corpo as Campos | undefined)?.cor_numeros).toBe("#1E88E5");
    });
    await userEvent.click(t("cor-numeros-limpar"));
    await waitFor(() => {
      const pedidos = servidor.chamadas("POST", /\/calcular$/);
      expect((pedidos[pedidos.length - 1]?.corpo as Campos | undefined)?.cor_numeros).toBe("");
    });
  });

  it("o logótipo só se pede com um template de uma rifa; carrega-se, mostra o nome e remove-se", async () => {
    umaRifa();
    abrir();
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    expect(screen.queryByTestId("upload-logotipo")).toBeNull();
    await userEvent.upload(
      t("upload-template"),
      new File(["%PDF-1.4 x"], "uma.pdf", { type: "application/pdf" }),
    );
    await userEvent.upload(await screen.findByTestId("upload-logotipo"), imagem("minha associacao.png"));
    await waitFor(() => expect(t("logotipo-nome")).toHaveTextContent("minha associacao.png"));
    expect(servidor.chamadas("PUT", /\/logotipo$/)).toHaveLength(1);
    await userEvent.selectOptions(t("logo-posicao"), "ie");
    fireEvent.change(t("logo-tamanho"), { target: { value: "35" } });
    await waitFor(() => {
      const pedidos = servidor.chamadas("POST", /\/calcular$/);
      expect(pedidos[pedidos.length - 1]?.corpo).toMatchObject({ logo_posicao: "ie", logo_tamanho: "35" });
    });
    await userEvent.click(t("remover-logotipo"));
    await waitFor(() => expect(screen.queryByTestId("logotipo-nome")).toBeNull());
    expect(servidor.chamadas("DELETE", /\/logotipo$/)).toHaveLength(1);
  });

  it("um logótipo recusado mostra o aviso do servidor e não fica", async () => {
    umaRifa();
    servidor.logotipoErro = "O logótipo tem de ser uma imagem PNG ou JPG com no máximo 2 MB.";
    abrir();
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await userEvent.upload(
      t("upload-template"),
      new File(["%PDF-1.4 x"], "uma.pdf", { type: "application/pdf" }),
    );
    await userEvent.upload(await screen.findByTestId("upload-logotipo"), imagem("mau.png"));
    expect(await screen.findByTestId("dialogo-texto")).toHaveTextContent("PNG ou JPG");
    expect(screen.queryByTestId("logotipo-nome")).toBeNull();
  });

  it("a cor vai na ligação partilhada (e só se for válida)", () => {
    const ligacao = ligacaoDosCampos({ ...PADRAO, cor_numeros: "#1E88E5" }, "https://x/");
    expect(new URL(ligacao).searchParams.get("cn")).toBe("#1E88E5");
    expect(camposDaLigacao(new URL(ligacao).search).cor_numeros).toBe("#1E88E5");
    expect(ligacaoDosCampos(PADRAO, "https://x/")).not.toMatch(/cn=|logo/);
    expect(camposDaLigacao("?cn=azul")).toEqual({});
    expect(camposDaLigacao("?cn=%23GGGGGG")).toEqual({});
  });
});
