import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminComentarios } from "./AdminComentarios";
import type { ComentarioDoDono } from "./admin-api";

let lista: ComentarioDoDono[];
let pedidos: { metodo: string; url: string; corpo?: string }[];

function json(corpo: unknown, estado = 200) {
  return Promise.resolve(new Response(estado === 204 ? null : JSON.stringify(corpo), { status: estado }));
}

beforeEach(() => {
  pedidos = [];
  lista = [
    { id: "a", pais: "PT", texto: "Muito bom, obrigado!", estado: "novo" },
    { id: "b", pais: "??", texto: "Um comentário vindo de um país desconhecido", estado: "lido" },
  ];
  vi.stubGlobal(
    "fetch",
    vi.fn((entrada: RequestInfo | URL, init?: RequestInit) => {
      const url = String(entrada);
      const metodo = init?.method ?? "GET";
      pedidos.push({ metodo, url, corpo: init?.body as string | undefined });
      if (metodo === "DELETE") {
        lista = lista.filter((c) => url !== `/api/admin/comentarios/${c.id}`);
        return json(null, 204);
      }
      if (metodo === "PATCH") {
        const id = decodeURIComponent(url.split("/").pop() as string);
        const { estado } = JSON.parse(init?.body as string);
        lista = lista.map((c) => (c.id === id ? { ...c, estado } : c));
        return json({ estado });
      }
      if (metodo === "POST") {
        const marcados = lista.filter((c) => c.estado === "novo").length;
        lista = lista.map((c) => (c.estado === "novo" ? { ...c, estado: "lido" } : c));
        return json({ marcados });
      }
      const filtro = new URL(url, "http://x").searchParams.get("estado");
      return json({
        total: lista.length,
        por_ler: lista.filter((c) => c.estado === "novo").length,
        escondidos: lista.filter((c) => c.estado === "escondido").length,
        itens: filtro ? lista.filter((c) => c.estado === filtro) : lista,
      });
    }),
  );
  vi.spyOn(window, "confirm").mockReturnValue(true);
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("os comentários no painel do dono", () => {
  it("mostra só o país, o texto e o estado de cada um, e quantos há por ler", async () => {
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    const linhas = await screen.findAllByTestId("admin-comentario");
    expect(linhas).toHaveLength(2);
    expect(within(linhas[0] as HTMLElement).getByText("Portugal (PT)")).toBeInTheDocument();
    expect(within(linhas[0] as HTMLElement).getByText("Muito bom, obrigado!")).toBeInTheDocument();
    expect(within(linhas[0] as HTMLElement).getByTestId("admin-comentario-estado")).toHaveTextContent("Novo");
    expect(within(linhas[1] as HTMLElement).getByText("Desconhecido")).toBeInTheDocument();
    const cabecalhos = within(screen.getByTestId("admin-tabela-comentarios"))
      .getAllByRole("columnheader")
      .map((c) => c.textContent);
    expect(cabecalhos).toEqual(["País", "Texto", "Estado", "Ações"]); // nada sobre quem escreveu, nem IP
    expect(screen.getByTestId("admin-comentarios-resumo")).toHaveTextContent("2 comentários · 1 por ler");
  });

  it("marcar como lido muda o estado e atualiza a contagem", async () => {
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.click(await screen.findByTestId("admin-comentario-lido"));
    await waitFor(() =>
      expect(screen.getByTestId("admin-comentarios-resumo")).toHaveTextContent("0 por ler"),
    );
    expect(
      pedidos.some(
        (p) =>
          p.metodo === "PATCH" && p.url === "/api/admin/comentarios/a" && p.corpo === '{"estado":"lido"}',
      ),
    ).toBe(true);
    expect(screen.queryByTestId("admin-comentario-lido")).toBeNull();
  });

  it("favorito e esconder alternam, e esconder avisa quantos estão escondidos", async () => {
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    const linhas = await screen.findAllByTestId("admin-comentario");
    await userEvent.click(within(linhas[1] as HTMLElement).getByTestId("admin-comentario-esconder"));
    await waitFor(() =>
      expect(screen.getByTestId("admin-comentarios-resumo")).toHaveTextContent("1 escondido"),
    );
    expect(screen.getAllByTestId("admin-comentario")[1]).toHaveAttribute("data-estado", "escondido");
    await userEvent.click(
      within(screen.getAllByTestId("admin-comentario")[1] as HTMLElement).getByTestId(
        "admin-comentario-esconder",
      ),
    );
    await waitFor(() =>
      expect(screen.getAllByTestId("admin-comentario")[1]).toHaveAttribute("data-estado", "lido"),
    );
    await userEvent.click(
      within(screen.getAllByTestId("admin-comentario")[0] as HTMLElement).getByTestId(
        "admin-comentario-favorito",
      ),
    );
    await waitFor(() =>
      expect(screen.getAllByTestId("admin-comentario")[0]).toHaveAttribute("data-estado", "favorito"),
    );
  });

  it("os filtros pedem só o estado escolhido", async () => {
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    await screen.findAllByTestId("admin-comentario");
    await userEvent.click(screen.getByTestId("admin-comentarios-filtro-novo"));
    await waitFor(() => expect(screen.getAllByTestId("admin-comentario")).toHaveLength(1));
    expect(pedidos.some((p) => p.url === "/api/admin/comentarios?estado=novo")).toBe(true);
    await userEvent.click(screen.getByTestId("admin-comentarios-filtro-escondido"));
    expect(await screen.findByTestId("admin-comentarios-vazio")).toHaveTextContent(
      "Nenhum comentário neste estado",
    );
  });

  it("marcar todos como lidos", async () => {
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.click(await screen.findByTestId("admin-comentarios-todos-lidos"));
    await waitFor(() =>
      expect(screen.getByTestId("admin-comentarios-resumo")).toHaveTextContent("0 por ler"),
    );
    expect(pedidos.some((p) => p.metodo === "POST" && p.url === "/api/admin/comentarios/lidos")).toBe(true);
    expect(screen.queryByTestId("admin-comentarios-todos-lidos")).toBeNull();
  });

  it("apagar pede confirmação, apaga e atualiza a lista", async () => {
    render(<AdminComentarios leitura={false} aoSairDaSessao={() => {}} />);
    const botoes = await screen.findAllByTestId("admin-comentario-apagar");
    await userEvent.click(botoes[0] as HTMLElement);
    await waitFor(() => expect(screen.getAllByTestId("admin-comentario")).toHaveLength(1));
    expect(pedidos.some((p) => p.metodo === "DELETE" && p.url === "/api/admin/comentarios/a")).toBe(true);
  });

  it("quem só tem leitura vê os estados mas não tem nenhuma ação", async () => {
    render(<AdminComentarios leitura aoSairDaSessao={() => {}} />);
    expect(await screen.findAllByTestId("admin-comentario")).toHaveLength(2);
    expect(screen.queryByTestId("admin-comentario-apagar")).toBeNull();
    expect(screen.queryByTestId("admin-comentario-esconder")).toBeNull();
    expect(screen.queryByTestId("admin-comentarios-todos-lidos")).toBeNull();
    expect(screen.getByTestId("admin-comentarios-resumo")).toHaveTextContent("1 por ler");
  });
});
