import "fake-indexeddb/auto";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { camposDaLigacao, ligacaoDosCampos, PADRAO } from "./formulario";
import { ProvedorI18n } from "./i18n";
import { esquecerAlgarismos, lerAlgarismos } from "./memoria";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;
const t = (id: string) => screen.getByTestId(id);
const ficheiro = (nome: string, tipo = "application/pdf") => new File(["%PDF-1.4 x"], nome, { type: tipo });

function abrir() {
  return render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

beforeEach(async () => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  await esquecerAlgarismos();
  servidor = new ServidorFalso().instalar();
});
afterEach(() => vi.unstubAllGlobals());

async function carregarTemplate() {
  await userEvent.upload(await screen.findByTestId("upload-template"), ficheiro("Rifa Natal.pdf"));
  await waitFor(() => expect(t("estado-template")).toHaveTextContent("5 bilhetes"));
}

describe("lembrar o ficheiro dos algarismos (F4)", () => {
  it("guarda-o ao carregar e reutiliza-o na sessão seguinte, dizendo-o", async () => {
    const primeira = abrir();
    await carregarTemplate();
    await userEvent.upload(t("upload-algarismos"), ficheiro("digitos.png", "image/png"));
    await waitFor(() => expect(t("estado-algarismos")).toHaveTextContent("digitos.png"));
    await waitFor(async () => expect((await lerAlgarismos())?.name).toBe("digitos.png"));
    expect(screen.queryByTestId("algarismos-lembrados")).toBeNull(); // foi o utilizador que o escolheu

    // outro dia: sessão nova, servidor novo; só o browser se lembra
    primeira.unmount();
    localStorage.removeItem("rifas.sessao");
    servidor = new ServidorFalso().instalar();
    abrir();
    await carregarTemplate();
    await waitFor(() => expect(t("estado-algarismos")).toHaveTextContent("digitos.png"));
    expect(servidor.chamadas("PUT", /\/algarismos$/)).toHaveLength(1);
    expect(t("algarismos-lembrados")).toHaveTextContent("digitos.png");
    // escolher outro troca-o e a nota desaparece
    await userEvent.upload(t("upload-algarismos"), ficheiro("outro.png", "image/png"));
    await waitFor(() => expect(screen.queryByTestId("algarismos-lembrados")).toBeNull());
    await waitFor(async () => expect((await lerAlgarismos())?.name).toBe("outro.png"));
  });

  it("sem nada guardado não envia nada por conta própria", async () => {
    abrir();
    await carregarTemplate();
    await waitFor(() => expect(t("estado-algarismos")).toHaveTextContent("Falta o ficheiro dos algarismos."));
    expect(servidor.chamadas("PUT", /\/algarismos$/)).toHaveLength(0);
  });

  it("«Limpar tudo» apaga também o que ficou no browser", async () => {
    abrir();
    await carregarTemplate();
    await userEvent.upload(t("upload-algarismos"), ficheiro("digitos.png", "image/png"));
    await waitFor(async () => expect(await lerAlgarismos()).not.toBeNull());
    await userEvent.click(t("limpar"));
    await waitFor(async () => expect(await lerAlgarismos()).toBeNull());
  });
});

describe("partilhar a configuração por ligação (F5)", () => {
  it("a ligação leva só os campos e lê-se de volta", () => {
    const campos = {
      ...PADRAO,
      nome: "Rifa de Natal",
      inicio: "5",
      fim: "250",
      modo: "unico" as const,
      papel: "A3",
      margem: "8",
    };
    const ligacao = ligacaoDosCampos(campos, "https://rifas.exemplo/");
    expect(ligacao).toBe(
      "https://rifas.exemplo/?de=5&ate=250&modo=unico&max=300&papel=A3&margem=8&nome=Rifa+de+Natal",
    );
    expect(camposDaLigacao(new URL(ligacao).search)).toEqual({
      inicio: "5",
      fim: "250",
      modo: "unico",
      max_ficheiro: "300",
      papel: "A3",
      margem: "8",
      nome: "Rifa de Natal",
    });
  });

  it("ignora o que o formulário não aceitaria", () => {
    const mau = "?de=abc&ate=1e9&modo=hacker&papel=A0&margem=99999&nome=%3Cscript%3E&max=-1&outro=1";
    expect(camposDaLigacao(mau)).toEqual({});
    expect(camposDaLigacao(`?nome=${"x".repeat(81)}`)).toEqual({});
    expect(camposDaLigacao("?nome=a%00b")).toEqual({});
  });

  it("abre com os valores da ligação, limpa o endereço e tem prioridade sobre o que estava lembrado", async () => {
    localStorage.setItem("rifas.campos", JSON.stringify({ inicio: "9", fim: "99" }));
    window.history.pushState({}, "", "/?de=5&ate=250&modo=unico&papel=A3&nome=Natal");
    abrir();
    await waitFor(() => expect(t("de")).toHaveValue("5"));
    expect(t("ate")).toHaveValue("250");
    expect(t("nome")).toHaveValue("Natal");
    expect(window.location.search).toBe("");
  });

  it("«Copiar ligação» põe a ligação na área de transferência e avisa", async () => {
    const escrever = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText: escrever }, configurable: true });
    abrir();
    await userEvent.type(await screen.findByTestId("nome"), "Rifa");
    await userEvent.click(t("copiar-ligacao"));
    await waitFor(() => expect(escrever).toHaveBeenCalledTimes(1));
    const ligacao = new URL(escrever.mock.calls[0]?.[0] as string);
    expect(ligacao.searchParams.get("nome")).toBe("Rifa");
    expect(ligacao.searchParams.get("de")).toBe("1");
    expect(await screen.findByText("Ligação copiada.")).toBeInTheDocument();
  });
});
