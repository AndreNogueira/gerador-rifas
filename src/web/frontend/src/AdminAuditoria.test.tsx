import { render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminAuditoria } from "./AdminAuditoria";

let resposta: { estado: number; corpo: unknown };

const BASE = {
  total: 3,
  retencao_dias: 400,
  persistente: true,
  itens: [
    {
      ts: 1_800_000_200,
      acao: "comentario_apagado",
      texto: "Apagou um comentário",
      papel: "admin",
      detalhe: "abc123",
    },
    {
      ts: 1_800_000_100,
      acao: "entrou_leitura",
      texto: "Entrou no painel (só leitura)",
      papel: "leitura",
      detalhe: "",
    },
    {
      ts: 1_800_000_000,
      acao: "chave_criada",
      texto: "Criou uma chave da API",
      papel: "admin",
      detalhe: "Escola (k1)",
    },
  ],
};

beforeEach(() => {
  resposta = { estado: 200, corpo: BASE };
  vi.stubGlobal(
    "fetch",
    vi.fn(() => Promise.resolve(new Response(JSON.stringify(resposta.corpo), { status: resposta.estado }))),
  );
});
afterEach(() => vi.unstubAllGlobals());

describe("o registo de ações do painel", () => {
  it("lista quem fez o quê, com o detalhe e o papel em português", async () => {
    render(<AdminAuditoria aoSairDaSessao={() => {}} />);
    const linhas = await screen.findAllByTestId("admin-auditoria-linha");
    expect(linhas).toHaveLength(3);
    expect(within(linhas[0] as HTMLElement).getByText("Apagou um comentário")).toBeInTheDocument();
    expect(within(linhas[0] as HTMLElement).getByText("abc123")).toBeInTheDocument();
    expect(within(linhas[0] as HTMLElement).getByText("Dono")).toBeInTheDocument();
    expect(within(linhas[1] as HTMLElement).getByText("Só leitura")).toBeInTheDocument();
    expect(within(linhas[1] as HTMLElement).getByText("—")).toBeInTheDocument();
    const cabecalhos = within(screen.getByTestId("admin-tabela-auditoria"))
      .getAllByRole("columnheader")
      .map((c) => c.textContent);
    expect(cabecalhos).toEqual(["Quando", "Quem", "Ação", "Detalhe"]);
    expect(screen.getByTestId("admin-auditoria")).toHaveTextContent("400 dias");
  });

  it("sem registos diz-o, e sem Postgres avisa que se perde ao reiniciar", async () => {
    resposta.corpo = { ...BASE, total: 0, itens: [], persistente: false };
    render(<AdminAuditoria aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("admin-auditoria-vazio")).toBeInTheDocument();
    expect(screen.getByText(/perde-se quando o serviço reinicia/)).toBeInTheDocument();
  });

  it("sem sessão (404) avisa o painel e um erro mostra o aviso", async () => {
    const sair = vi.fn();
    resposta = { estado: 404, corpo: {} };
    const { unmount } = render(<AdminAuditoria aoSairDaSessao={sair} />);
    await waitFor(() => expect(sair).toHaveBeenCalled());
    unmount();
    resposta = { estado: 503, corpo: {} };
    render(<AdminAuditoria aoSairDaSessao={() => {}} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível carregar o registo");
  });
});
