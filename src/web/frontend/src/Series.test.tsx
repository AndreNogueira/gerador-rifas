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
const ficheiro = (nome: string, tipo = "application/pdf") => new File(["%PDF-1.4 x"], nome, { type: tipo });

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

describe("séries, prefixos e saltos (formulário)", () => {
  it("os campos vão no pedido de pré-visualização e de geração", async () => {
    abrir();
    await userEvent.upload(await screen.findByTestId("upload-template"), ficheiro("Rifa.pdf"));
    await waitFor(() => expect(t("estado-template")).toHaveTextContent("5 bilhetes"));
    await userEvent.upload(t("upload-algarismos"), ficheiro("d.png", "image/png"));
    await waitFor(() => expect(t("estado-algarismos")).toHaveTextContent("d.png"));
    await userEvent.type(t("prefixos"), "A-, B-");
    await userEvent.type(t("saltar"), "13, 100-110");
    await userEvent.click(t("cor-serie"));
    await userEvent.type(t("nome"), "Rifa");
    await userEvent.click(t("previa"));
    await waitFor(() => expect(servidor.chamadas("POST", /\/previa$/)).toHaveLength(1));
    const enviado = servidor.chamadas("POST", /\/previa$/)[0]?.corpo as Campos;
    expect(enviado).toMatchObject({ prefixos: "A-, B-", saltar: "13, 100-110", cor_serie: "1" });
    expect(t("cor-serie")).toBeChecked();
    await userEvent.click(t("cor-serie"));
    expect(t("cor-serie")).not.toBeChecked();
  });
});

describe("séries, prefixos e saltos (ligação)", () => {
  const campos: Campos = {
    ...PADRAO,
    nome: "Rifa",
    prefixos: "A-, B-",
    saltar: "13, 100-110",
    cor_serie: "1",
  };

  it("vão na ligação e lêem-se de volta", () => {
    const ligacao = ligacaoDosCampos(campos, "https://rifas.exemplo/");
    const p = new URL(ligacao).searchParams;
    expect(p.get("pre")).toBe("A-, B-");
    expect(p.get("saltar")).toBe("13, 100-110");
    expect(p.get("cor")).toBe("1");
    expect(camposDaLigacao(new URL(ligacao).search)).toMatchObject({
      prefixos: "A-, B-",
      saltar: "13, 100-110",
      cor_serie: "1",
    });
  });

  it("um campo vazio não vai na ligação e o que não se aceitaria ignora-se", () => {
    expect(ligacaoDosCampos(PADRAO, "https://x/")).not.toMatch(/pre=|saltar=|cor=/);
    expect(camposDaLigacao("?pre=A1&saltar=abc&cor=2")).toEqual({});
    expect(camposDaLigacao(`?pre=${"A".repeat(121)}`)).toEqual({});
    expect(camposDaLigacao("?pre=%3Cscript%3E")).toEqual({});
  });
});
