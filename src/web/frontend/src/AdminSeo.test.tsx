import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminSeo } from "./AdminSeo";
import type { ItemSeo, VistaSeo } from "./admin-api";

let itens: ItemSeo[];
let pedidos: { metodo: string; url: string; corpo?: string }[];
let persistente: boolean;

function vista(lingua: string): VistaSeo {
  return {
    lingua,
    linguas: ["pt", "en", "ja"],
    persistente,
    erro: false,
    limites: { titulo: 66, descricao: [50, 158], max: 1000 },
    itens,
  };
}
function json(corpo: unknown, estado = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(corpo), { status: estado, headers: { "Content-Type": "application/json" } }),
  );
}

beforeEach(() => {
  persistente = true;
  pedidos = [];
  itens = [
    {
      chave: "d_inicio",
      tipo: "descricao",
      rotulo: "Descrição de /",
      padrao: "Rifas numeradas em PDF a partir do Canva.",
      valor: null,
    },
    {
      chave: "titulo:/tutorial",
      tipo: "titulo",
      rotulo: "Título de /tutorial",
      padrao: "Tutorial | Gerador de Rifas",
      valor: "Tutorial novo | Gerador",
    },
  ];
  vi.stubGlobal(
    "fetch",
    vi.fn((entrada: RequestInfo | URL, init?: RequestInit) => {
      const url = String(entrada);
      const metodo = init?.method ?? "GET";
      pedidos.push({ metodo, url, corpo: init?.body as string | undefined });
      if (url.startsWith("/api/admin/seo") && metodo === "GET")
        return json(vista(new URL(url, "http://x").searchParams.get("lingua") ?? "pt"));
      if (url === "/api/admin/seo" && metodo === "PUT") {
        const d = JSON.parse(String(init?.body)) as { chave: string; valor: string };
        if (d.valor.length < 10)
          return json({ detail: "A descrição deve ter entre 50 e 158 de largura (tem 5)." }, 422);
        itens = itens.map((i) => (i.chave === d.chave ? { ...i, valor: d.valor } : i));
        return json({ valor: d.valor });
      }
      if (url.startsWith("/api/admin/seo?") && metodo === "DELETE") {
        const chave = new URL(url, "http://x").searchParams.get("chave");
        itens = itens.map((i) => (i.chave === chave ? { ...i, valor: null } : i));
        return Promise.resolve(new Response(null, { status: 204 }));
      }
      return json({}, 404);
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

async function abrir() {
  render(<AdminSeo />);
  await userEvent.click(screen.getByText("SEO por língua"));
  await screen.findByTestId("seo-d_inicio");
}

describe("SEO por língua no painel", () => {
  it("só carrega os textos quando se abre a secção, e mostra o original dos editados", async () => {
    render(<AdminSeo />);
    expect(pedidos).toEqual([]);
    await userEvent.click(screen.getByText("SEO por língua"));
    await screen.findByTestId("seo-d_inicio");
    expect(pedidos[0]?.url).toBe("/api/admin/seo?lingua=pt");
    expect(screen.getByTestId("seo-titulo:/tutorial")).toHaveTextContent("editado");
    expect(screen.getByTestId("seo-titulo:/tutorial")).toHaveTextContent(
      "Original: Tutorial | Gerador de Rifas",
    );
  });

  it("edita e guarda um texto (o servidor valida) e mostra a razão se recusar", async () => {
    await abrir();
    const caixa = screen.getByTestId("seo-d_inicio").querySelector("textarea") as HTMLTextAreaElement;
    await userEvent.clear(caixa);
    await userEvent.type(caixa, "curto");
    await userEvent.click(screen.getByTestId("seo-d_inicio").querySelector("button") as HTMLButtonElement);
    expect(await screen.findByRole("alert")).toHaveTextContent("A descrição deve ter entre 50 e 158");
    await userEvent.clear(caixa);
    await userEvent.type(caixa, "Uma descrição nova, bem mais comprida, para a página inicial do site.");
    await userEvent.click(screen.getByTestId("seo-d_inicio").querySelector("button") as HTMLButtonElement);
    await waitFor(() =>
      expect(pedidos.some((p) => p.metodo === "PUT" && p.corpo?.includes('"lingua":"pt"'))).toBe(true),
    );
    await waitFor(() => expect(screen.getByTestId("seo-d_inicio")).toHaveTextContent("editado"));
  });

  it("repor o original apaga o editado", async () => {
    await abrir();
    await userEvent.click(screen.getByRole("button", { name: "Repor o original" }));
    await waitFor(() =>
      expect(
        pedidos.some((p) => p.metodo === "DELETE" && p.url.includes("chave=titulo%3A%2Ftutorial&lingua=pt")),
      ).toBe(true),
    );
    await waitFor(() => expect(screen.queryByRole("button", { name: "Repor o original" })).toBeNull());
  });

  it("mudar de língua volta a pedir os textos dessa língua; a pesquisa filtra", async () => {
    await abrir();
    await userEvent.selectOptions(screen.getByTestId("seo-lingua"), "ja");
    await waitFor(() => expect(pedidos.some((p) => p.url === "/api/admin/seo?lingua=ja")).toBe(true));
    await userEvent.type(screen.getByRole("searchbox"), "tutorial");
    expect(screen.queryByTestId("seo-d_inicio")).toBeNull();
    expect(screen.getByTestId("seo-titulo:/tutorial")).toBeInTheDocument();
  });

  it("avisa que a base é temporária quando não há DATABASE_URL", async () => {
    persistente = false;
    await abrir();
    expect(screen.getByRole("note")).toHaveTextContent("local e temporária");
  });

  it("conta a largura dos carateres largos a dobrar", async () => {
    itens = [{ chave: "titulo:/tutorial", tipo: "titulo", rotulo: "Título", padrao: "抽奖券", valor: null }];
    render(<AdminSeo />);
    await userEvent.click(screen.getByText("SEO por língua"));
    expect(await screen.findByText("Largura 6 / 66")).toBeInTheDocument();
  });
});
