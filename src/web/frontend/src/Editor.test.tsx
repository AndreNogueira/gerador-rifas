import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { lerGuardado, modeloComTalao, PADRAO_NUMERO, paraEnviar, problemas } from "./editor-modelo";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/editor");
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

describe("o desenho (editor-modelo)", () => {
  it("o modelo é uma rifa com talão: o número duas vezes, sem texto que o motor confunda", () => {
    const d = modeloComTalao();
    expect(d.elementos.filter((e) => e.tipo === "numero")).toHaveLength(2);
    expect(problemas(d)).toEqual({ numero: false, digitos: "", elementos: false });
  });

  it("o padrão dos algarismos é o do motor: 0 e, pelo menos, mais dois algarismos", () => {
    for (const s of ["0123", "Ref. 0001", "(007)", "a 00000 b"]) expect(PADRAO_NUMERO.test(s), s).toBe(true);
    for (const s of ["2026", "10/01", "910000000", "100€", "01", "Nº 5"])
      expect(PADRAO_NUMERO.test(s), s).toBe(false);
  });

  it("paraEnviar tira os ids e o contorno de um retângulo sem espessura", () => {
    const d = modeloComTalao();
    const envio = paraEnviar({
      ...d,
      elementos: d.elementos.slice(0, 1).map((e) => ({ ...e, contorno: "#112233", espessura: 0 })),
    });
    expect(envio.elementos[0]).not.toHaveProperty("id");
    expect(envio.elementos[0]?.contorno).toBe("");
  });

  it("um rascunho estragado não é aceite", () => {
    expect(lerGuardado("não é json")).toBeNull();
    expect(lerGuardado(JSON.stringify({ fundo: "x", elementos: [] }))).toBeNull();
    expect(
      lerGuardado(
        JSON.stringify({ largura: 535, altura: 152, fundo: "#ffffff", elementos: [{ tipo: "foto" }] }),
      ),
    ).toBeNull();
    const bom = lerGuardado(JSON.stringify(paraEnviar(modeloComTalao())));
    expect(bom?.elementos).toHaveLength(11);
  });
});

describe("página do editor", () => {
  it("arranca com o modelo, acrescenta e apaga elementos e avisa quando falta o número", async () => {
    abrir();
    const tela = await screen.findByTestId("editor-tela");
    expect(within(tela).getAllByTestId("el-numero")).toHaveLength(2);
    await userEvent.click(screen.getByTestId("add-retangulo"));
    expect(within(tela).getAllByTestId("el-retangulo")).toHaveLength(3);
    expect(screen.getByTestId("editor-inspetor")).toBeInTheDocument();
    await userEvent.click(screen.getByTestId("editor-apagar"));
    expect(within(tela).getAllByTestId("el-retangulo")).toHaveLength(2);
    for (const n of within(tela).getAllByTestId("el-numero")) {
      fireEvent.focus(n);
      await userEvent.click(screen.getByTestId("editor-apagar"));
    }
    expect(await screen.findByTestId("editor-erro-numero")).toHaveTextContent("0001");
    expect(screen.getByTestId("editor-usar")).toBeDisabled();
  });

  it("um texto com algo que parece o número é recusado já no ecrã", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("add-texto"));
    const campo = screen.getByTestId("editor-texto");
    await userEvent.clear(campo);
    await userEvent.type(campo, "Ref 0123");
    expect(await screen.findByTestId("editor-erro-digitos")).toHaveTextContent("Ref 0123");
    expect(screen.getByTestId("editor-usar")).toBeDisabled();
  });

  it("as setas movem o elemento escolhido e o rascunho fica guardado no browser", async () => {
    abrir();
    const tela = await screen.findByTestId("editor-tela");
    const texto = within(tela).getAllByTestId("el-texto")[0] as HTMLElement;
    const x = Number(texto.querySelector("text")?.getAttribute("x"));
    texto.focus();
    fireEvent.keyDown(texto, { key: "ArrowRight", shiftKey: true });
    await waitFor(() =>
      expect(
        Number(within(tela).getAllByTestId("el-texto")[0]?.querySelector("text")?.getAttribute("x")),
      ).toBe(x + 10),
    );
    const guardado = JSON.parse(localStorage.getItem("rifas.editor") ?? "{}") as {
      elementos: { x: number; tipo: string }[];
    };
    expect(guardado.elementos.find((e) => e.tipo === "texto")?.x).toBe(x + 10);
  });

  it("«Usar este template» envia o desenho, deixa o template na sessão e volta ao ecrã principal", async () => {
    abrir();
    await screen.findByTestId("editor-tela");
    await waitFor(() => expect(screen.getByTestId("editor-usar")).toBeEnabled());
    await userEvent.click(screen.getByTestId("editor-usar"));
    await waitFor(() => expect(window.location.pathname).toBe("/"));
    const envio = servidor.chamadas("POST", /\/editor$/);
    expect(envio).toHaveLength(1);
    const corpo = envio[0]?.corpo as { elementos: { id?: string; tipo: string }[] };
    expect(corpo.elementos.some((e) => "id" in e)).toBe(false);
    expect(corpo.elementos.filter((e) => e.tipo === "numero")).toHaveLength(2);
    expect(await screen.findByTestId("estado-template")).toHaveTextContent("editor");
  });
});
