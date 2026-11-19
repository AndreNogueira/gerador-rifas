import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminComentarios } from "./AdminComentarios";

let lista: { id: string; pais: string; texto: string }[];
let pedidos: { metodo: string; url: string }[];

function json(corpo: unknown, estado = 200) {
  return Promise.resolve(new Response(estado === 204 ? null : JSON.stringify(corpo), { status: estado }));
}

beforeEach(() => {
  pedidos = [];
  lista = [
    { id: "a", pais: "PT", texto: "Muito bom, obrigado!" },
    { id: "b", pais: "??", texto: "Um comentário vindo de um país desconhecido" },
  ];
  vi.stubGlobal(
    "fetch",
    vi.fn((entrada: RequestInfo | URL, init?: RequestInit) => {
      const url = String(entrada);
      const metodo = init?.method ?? "GET";
      pedidos.push({ metodo, url });
      if (metodo === "DELETE") {
        lista = lista.filter((c) => url !== `/api/admin/comentarios/${c.id}`);
        return json(null, 204);
      }
      return json({ total: lista.length, itens: lista });
    }),
  );
  vi.spyOn(window, "confirm").mockReturnValue(true);
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("os comentários no painel do dono", () => {
  it("mostra só o país e o texto de cada um", async () => {
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    const linhas = await screen.findAllByTestId("admin-comentario");
    expect(linhas).toHaveLength(2);
    expect(within(linhas[0] as HTMLElement).getByText("Portugal (PT)")).toBeInTheDocument();
    expect(within(linhas[0] as HTMLElement).getByText("Muito bom, obrigado!")).toBeInTheDocument();
    expect(within(linhas[1] as HTMLElement).getByText("Desconhecido")).toBeInTheDocument();
    const cabecalhos = within(screen.getByTestId("admin-tabela-comentarios"))
      .getAllByRole("columnheader")
      .map((c) => c.textContent);
    expect(cabecalhos).toEqual(["País", "Texto", "Apagar"]); // nada sobre quem escreveu, nem IP
  });

  it("apagar pede confirmação, apaga e atualiza a lista", async () => {
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    const botoes = await screen.findAllByTestId("admin-comentario-apagar");
    await userEvent.click(botoes[0] as HTMLElement);
    await waitFor(() => expect(screen.getAllByTestId("admin-comentario")).toHaveLength(1));
    expect(pedidos.some((p) => p.metodo === "DELETE" && p.url === "/api/admin/comentarios/a")).toBe(true);
  });

  it("se se cancelar a confirmação não se apaga nada", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.click((await screen.findAllByTestId("admin-comentario-apagar"))[0] as HTMLElement);
    expect(pedidos.some((p) => p.metodo === "DELETE")).toBe(false);
  });

  it("em modo de leitura (o Claude) não há botões de apagar", async () => {
    render(<AdminComentarios leitura aoSairDaSessao={() => {}} />);
    await screen.findAllByTestId("admin-comentario");
    expect(screen.queryByTestId("admin-comentario-apagar")).toBeNull();
    expect(screen.queryByRole("columnheader", { name: "Apagar" })).toBeNull();
  });

  it("sem comentários diz-o; sem sessão volta a pedir a palavra-passe", async () => {
    lista = [];
    const { unmount } = render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("admin-comentarios-vazio")).toBeInTheDocument();
    unmount();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response("{}", { status: 404 }))),
    );
    const aoSair = vi.fn();
    render(<AdminComentarios leitura={false} aoSairDaSessao={aoSair} />);
    await waitFor(() => expect(aoSair).toHaveBeenCalled());
  });
});
