import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AdminErros } from "./AdminErros";

const LIVRO = {
  intervalo: "24h",
  desde_arranque: 1_800_000_000,
  total: 5,
  erros: [
    {
      tipo: "excecao",
      rota: "POST /api/sessoes/{id_}/gerar",
      estado: 500,
      excecao: "ValueError",
      onde: "motor.py:10:gerar",
      n: 3,
      primeira: 1_800_000_100,
      ultima: 1_800_000_900,
    },
    {
      tipo: "geracao",
      rota: "",
      estado: 0,
      excecao: "falhou",
      onde: "tempo",
      n: 2,
      primeira: 1_800_000_200,
      ultima: 1_800_000_800,
    },
  ],
  recentes: [],
};

function resposta(corpo: unknown, ok = true) {
  return Promise.resolve({ ok, status: ok ? 200 : 404, json: () => Promise.resolve(corpo) } as Response);
}

describe("livro de erros do painel", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("mostra uma linha por assinatura, com a contagem, o sítio e sem mensagens", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => resposta(LIVRO)),
    );
    render(<AdminErros intervalo="24h" />);
    const tabela = await screen.findByTestId("admin-tabela-erros");
    expect(tabela).toHaveTextContent("Erro não tratado (500)");
    expect(tabela).toHaveTextContent("ValueError");
    expect(tabela).toHaveTextContent("motor.py:10:gerar");
    expect(tabela).toHaveTextContent("Geração que falhou");
    expect(tabela.querySelectorAll("tbody tr")).toHaveLength(2);
    expect(String(vi.mocked(fetch).mock.calls[0]?.[0])).toContain("/api/admin/erros?intervalo=24h");
  });

  it("sem erros diz que está tudo bem", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => resposta({ ...LIVRO, total: 0, erros: [] })),
    );
    render(<AdminErros intervalo="6h" />);
    expect(await screen.findByText(/Sem erros neste intervalo/)).toBeInTheDocument();
  });

  it("se o servidor não responde avisa em vez de partir o painel", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => resposta({}, false)),
    );
    render(<AdminErros intervalo="6h" />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/Não foi possível carregar/);
  });
});
