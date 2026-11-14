import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { lerGuardado, modeloComTalao, PADRAO_NUMERO, paraEnviar, problemas } from "./editor-modelo";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

vi.mock("./imagem", () => ({
  prepararImagem: vi.fn(async (f: File) => {
    if (f.type !== "image/png") throw new Error("tipo");
    return { dados: "data:image/png;base64,iVBORw0KGgo=", largura: 200, altura: 100 };
  }),
}));

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

const contar = (tipo: string) =>
  within(screen.getByTestId("editor-tela")).queryAllByTestId(`el-${tipo}`).length;

describe("editor v2: histórico, duplicar, ordem, imagem e partilha", () => {
  it("desfazer e refazer repõem os elementos, e os botões só funcionam quando há o que desfazer", async () => {
    abrir();
    await screen.findByTestId("editor-tela");
    expect(screen.getByTestId("editor-desfazer")).toBeDisabled();
    expect(screen.getByTestId("editor-refazer")).toBeDisabled();
    await userEvent.click(screen.getByTestId("add-retangulo"));
    expect(contar("retangulo")).toBe(3);
    await userEvent.click(screen.getByTestId("editor-desfazer"));
    expect(contar("retangulo")).toBe(2);
    expect(screen.getByTestId("editor-refazer")).toBeEnabled();
    await userEvent.click(screen.getByTestId("editor-refazer"));
    expect(contar("retangulo")).toBe(3);
  });

  it("escrever num texto é um só passo do histórico; Ctrl+Z desfaz tudo o que se escreveu", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("add-texto"));
    const campo = screen.getByTestId("editor-texto");
    await userEvent.clear(campo);
    await userEvent.type(campo, "Novo texto");
    await userEvent.click(screen.getByTestId("editor-desfazer"));
    expect((screen.getByTestId("editor-texto") as HTMLInputElement).value).toBe("Texto"); // voltou ao valor de antes de começar a escrever
    await userEvent.click(screen.getByTestId("editor-desfazer"));
    expect(contar("texto")).toBe(6); // desfez o «+ Texto»
  });

  it("Ctrl+Z, Ctrl+Y e Ctrl+D funcionam fora dos campos de escrita", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("add-linha"));
    expect(contar("linha")).toBe(2);
    fireEvent.keyDown(document.body, { key: "d", ctrlKey: true });
    expect(contar("linha")).toBe(3);
    fireEvent.keyDown(document.body, { key: "z", ctrlKey: true });
    expect(contar("linha")).toBe(2);
    fireEvent.keyDown(document.body, { key: "y", ctrlKey: true });
    expect(contar("linha")).toBe(3);
  });

  it("duplicar copia o elemento um pouco ao lado; para a frente e para trás mudam a ordem de desenho", async () => {
    abrir();
    const tela = await screen.findByTestId("editor-tela");
    const primeiro = within(tela).getAllByTestId("el-texto")[0] as HTMLElement;
    fireEvent.focus(primeiro);
    const x = Number(primeiro.querySelector("text")?.getAttribute("x"));
    await userEvent.click(screen.getByTestId("editor-duplicar"));
    expect(contar("texto")).toBe(7);
    // a ordem de desenho é a dos filhos do SVG: a cópia (com x + 10) entra por último (por cima de tudo)
    const posicao = () =>
      Array.from(tela.querySelectorAll("g.editor-el")).findIndex(
        (g) =>
          Number(g.querySelector("text")?.getAttribute("x")) === x + 10 &&
          g.getAttribute("data-testid") === "el-texto",
      );
    const total = tela.querySelectorAll("g.editor-el").length;
    expect(posicao()).toBe(total - 1);
    await userEvent.click(screen.getByTestId("editor-tras"));
    expect(posicao()).toBe(total - 2);
    await userEvent.click(screen.getByTestId("editor-frente"));
    expect(posicao()).toBe(total - 1);
    await userEvent.click(screen.getByTestId("editor-frente")); // já está por cima de tudo: não muda
    expect(posicao()).toBe(total - 1);
  });

  it("junta uma imagem (o logótipo) e envia-a ao servidor; um ficheiro que não presta dá o aviso", async () => {
    abrir();
    await screen.findByTestId("editor-tela");
    const envio = new File(["x"], "logo.png", { type: "image/png" });
    await userEvent.upload(screen.getByTestId("editor-ficheiro"), envio);
    await waitFor(() => expect(contar("imagem")).toBe(1));
    const im = within(screen.getByTestId("editor-tela")).getByTestId("el-imagem").querySelector("image");
    expect(im).toHaveAttribute("href", "data:image/png;base64,iVBORw0KGgo=");
    expect(Number(im?.getAttribute("width"))).toBe(160); // 200 × 100 px cabe em 160 × 80 pt
    await userEvent.click(screen.getByTestId("editor-usar"));
    await waitFor(() => expect(servidor.chamadas("POST", /\/editor$/)).toHaveLength(1));
    const corpo = servidor.chamadas("POST", /\/editor$/)[0]?.corpo as {
      elementos: { tipo: string; dados?: string; id?: string }[];
    };
    expect(corpo.elementos.find((e) => e.tipo === "imagem")?.dados).toBe(
      "data:image/png;base64,iVBORw0KGgo=",
    );
    expect(corpo.elementos.filter((e) => e.tipo !== "imagem").every((e) => !("dados" in e))).toBe(true);
  });

  it("uma imagem inválida mostra o aviso e não entra no desenho", async () => {
    abrir();
    await screen.findByTestId("editor-tela");
    fireEvent.change(screen.getByTestId("editor-ficheiro"), {
      target: { files: [new File(["x"], "x.gif", { type: "image/gif" })] },
    });
    expect(await screen.findByTestId("editor-aviso")).toHaveTextContent("PNG ou JPG");
    expect(contar("imagem")).toBe(0);
  });

  it("só mostra «Partilhar por ligação» com base de dados; partilha sem imagens e mostra a ligação", async () => {
    abrir();
    await screen.findByTestId("editor-tela");
    expect(screen.queryByTestId("editor-partilhar")).toBeNull();
    cleanup();
    servidor.partilhaEditor = true;
    abrir();
    await userEvent.upload(
      await screen.findByTestId("editor-ficheiro"),
      new File(["x"], "logo.png", { type: "image/png" }),
    );
    await waitFor(() => expect(contar("imagem")).toBe(1));
    await userEvent.click(await screen.findByTestId("editor-partilhar"));
    expect(await screen.findByTestId("editor-ligacao")).toHaveTextContent("/editor?d=abc0xyzxyz");
    const enviado = servidor.partilhados.get("abc0xyzxyz") as { elementos: { tipo: string }[] };
    expect(enviado.elementos.some((e) => e.tipo === "imagem")).toBe(false);
  });

  it("abre um desenho partilhado a partir do endereço; um endereço que já não existe avisa", async () => {
    servidor.partilhaEditor = true;
    const base = modeloComTalao();
    servidor.partilhados.set("umidvalido1", {
      ...paraEnviar(base),
      elementos: paraEnviar(base)
        .elementos.slice(0, 5)
        .concat(paraEnviar(base).elementos.filter((e) => e.tipo === "numero")),
    });
    window.history.pushState({}, "", "/editor?d=umidvalido1");
    render(
      <ProvedorI18n>
        <App />
      </ProvedorI18n>,
    );
    await waitFor(() => expect(contar("texto")).toBe(2)); // o que veio da ligação (o modelo tem 6 textos)
    expect(contar("numero")).toBe(2);
    cleanup();
    window.history.pushState({}, "", "/editor?d=nao-existe-123");
    render(
      <ProvedorI18n>
        <App />
      </ProvedorI18n>,
    );
    expect(await screen.findByTestId("editor-aviso")).toHaveTextContent("expirou");
  });
});
