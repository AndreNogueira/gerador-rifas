import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminQuotas } from "./AdminQuotas";
import type { QuotasEstado } from "./admin-api";

let resposta: { estado: number; corpo: unknown };

const BASE: QuotasEstado = {
  render: {
    mes: "2026-11",
    gastas: 432,
    limite: 750,
    pct: 58,
    projecao: 701,
    horas_do_mes: 720,
    decorridas: 444,
    persistente: true,
    dados_desde: null,
  },
  neon: {
    total_mb: 41.5,
    limite_mb: 512,
    pct: 8,
    tabelas: [
      { nome: "eventos", mb: 30.2 },
      { nome: "pedidos", mb: 5 },
    ],
  },
  avisos: [],
};

beforeEach(() => {
  resposta = { estado: 200, corpo: BASE };
  vi.stubGlobal(
    "fetch",
    vi.fn(() => Promise.resolve(new Response(JSON.stringify(resposta.corpo), { status: resposta.estado }))),
  );
});
afterEach(() => vi.unstubAllGlobals());

describe("as quotas do alojamento no painel", () => {
  it("mostra as horas do mês com a projeção e o espaço do Neon com as tabelas", async () => {
    render(<AdminQuotas aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("admin-quotas-horas")).toHaveTextContent("432 de 750 h (58 %) em 444 h");
    expect(screen.getByTestId("admin-quotas-horas")).toHaveTextContent("701 h até ao fim do mês");
    expect(screen.getByTestId("admin-quotas-neon")).toHaveTextContent("de 512 MB (8 %)");
    expect(screen.getByTestId("admin-quotas-tabelas")).toHaveTextContent("eventos: 30,2 MB");
    expect(screen.getAllByRole("progressbar")).toHaveLength(2);
    expect(screen.queryByTestId("admin-quotas-aviso")).toBeNull();
  });

  it("os avisos aparecem e uma projeção acima do limite diz-o", async () => {
    resposta.corpo = {
      ...BASE,
      render: { ...BASE.render, gastas: 700, pct: 93, projecao: 800 },
      avisos: ["Este serviço já gastou 700 das 750 horas do mês no Render (93 %)."],
    };
    render(<AdminQuotas aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("admin-quotas-aviso")).toHaveTextContent("700 das 750 horas");
    expect(screen.getByTestId("admin-quotas-horas")).toHaveTextContent("acima do limite");
  });

  it("sem Postgres explica porque não há espaço do Neon e avisa que as horas são desde o reinício", async () => {
    resposta.corpo = { ...BASE, neon: null, render: { ...BASE.render, persistente: false } };
    render(<AdminQuotas aoSairDaSessao={() => {}} />);
    await screen.findByTestId("admin-quotas-horas");
    expect(screen.getByText(/Só com/)).toBeInTheDocument();
    expect(screen.getByText(/desde o último reinício/)).toBeInTheDocument();
    expect(screen.queryByTestId("admin-quotas-neon")).toBeNull();
  });

  it("sem sessão (404) avisa o painel e um erro mostra o aviso", async () => {
    const sair = vi.fn();
    resposta = { estado: 404, corpo: {} };
    render(<AdminQuotas aoSairDaSessao={sair} />);
    await vi.waitFor(() => expect(sair).toHaveBeenCalled());
  });

  it("um erro do servidor mostra um aviso e não parte a página", async () => {
    resposta = { estado: 500, corpo: {} };
    render(<AdminQuotas aoSairDaSessao={() => {}} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível calcular as quotas");
  });
});
