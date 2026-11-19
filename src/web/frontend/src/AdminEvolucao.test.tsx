import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Admin } from "./Admin";
import { AdminEvolucao, paraCsv, tendencia } from "./AdminEvolucao";
import type { Evolucao, PainelDiario } from "./admin-api";
import { corDaSerie, GraficoDiario } from "./graficos";

const DIAS = ["2027-01-12", "2027-01-13", "2027-01-14", "2027-01-15"];

function painel(
  p: Partial<Omit<PainelDiario, "series">> & {
    id: string;
    titulo: string;
    series: { nome: string; valores: (number | null)[]; agregado?: PainelDiario["agregado"] }[];
  },
): PainelDiario {
  const agregado = p.agregado ?? "soma";
  return {
    grupo: "Utilização",
    explica: `Explicação de ${p.titulo}`,
    tipo: "barras",
    unidade: "",
    rotulos: "",
    ...p,
    agregado,
    series: p.series.map((s) => ({ ...s, agregado: s.agregado ?? agregado })),
  };
}

const EVOLUCAO: Evolucao = {
  dias: 4,
  fuso_min: 0,
  dias_lista: DIAS,
  retencao: { eventos_dias: 90, sistema_dias: 35 },
  dados_desde: 1_800_000_000,
  paineis: [
    painel({
      id: "sessoes",
      titulo: "Sessões abertas",
      series: [{ nome: "Sessões", valores: [1, 1, 3, 5] }],
    }),
    painel({
      id: "geracoes",
      titulo: "Gerações",
      series: [
        { nome: "Concluída", valores: [0, 2, 2, 2] },
        { nome: "Falhou", valores: [0, 0, 1, 0] },
      ],
    }),
    painel({
      id: "numeros",
      titulo: "Números gerados",
      series: [{ nome: "Números", valores: [0, 1200, 0, 300] }],
    }),
    painel({ id: "descargas", titulo: "Descargas", series: [{ nome: "pdf", valores: [0, 0, 0, 0] }] }),
    painel({
      id: "paginas_vistas",
      titulo: "Páginas vistas",
      series: [{ nome: "Pessoas", valores: [2, 2, 2, 2] }],
    }),
    painel({
      id: "paises",
      grupo: "Público",
      titulo: "Países",
      rotulos: "pais",
      series: [
        { nome: "PT", valores: [2, 2, 2, 2] },
        { nome: "??", valores: [0, 1, 0, 0] },
      ],
    }),
    painel({
      id: "cpu",
      grupo: "Sistema",
      titulo: "CPU",
      tipo: "linhas",
      unidade: " %",
      agregado: "media",
      series: [
        { nome: "Média", valores: [null, 10, 30, null] },
        { nome: "Máxima", valores: [null, 40, 90, null], agregado: "max" },
      ],
    }),
  ],
};

let pedidos: string[] = [];

beforeEach(() => {
  pedidos = [];
  vi.stubGlobal(
    "fetch",
    vi.fn((entrada: RequestInfo | URL) => {
      const url = String(entrada);
      pedidos.push(url);
      if (url.startsWith("/api/admin/evolucao")) {
        const dias = Number(new URL(url, "http://x").searchParams.get("dias"));
        const historico = dias > 90 ? { origem: "historico", dias_com_dados: 4 } : {};
        return Promise.resolve(
          new Response(JSON.stringify({ ...EVOLUCAO, dias, ...historico }), { status: 200 }),
        );
      }
      return Promise.resolve(new Response("{}", { status: 404 }));
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

describe("a vista «Evolução diária»", () => {
  it("pede 30 dias com o fuso do browser e mostra os grupos, os destaques e os painéis", async () => {
    render(<AdminEvolucao aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("evolucao-grupo-Utilização")).toBeInTheDocument();
    expect(pedidos[0]).toBe(`/api/admin/evolucao?dias=30&fuso=${-new Date().getTimezoneOffset()}`);
    expect(screen.getByTestId("evolucao-grupo-Público")).toBeInTheDocument();
    expect(screen.getByTestId("evolucao-grupo-Sistema")).toBeInTheDocument();
    const destaques = within(screen.getByTestId("evolucao-destaques"));
    expect(destaques.getByText("Sessões")).toBeInTheDocument();
    expect(destaques.getByText("Números gerados")).toBeInTheDocument();
    expect(destaques.getByText("1.5 k")).toBeInTheDocument(); // 1200 + 300 números no período
    const sessoes = within(screen.getByTestId("evolucao-sessoes"));
    expect(sessoes.getByText("10", { selector: "strong" })).toBeInTheDocument(); // 1 + 1 + 3 + 5
    expect(sessoes.getByText(/▲ 300 % face à 1.ª metade/)).toBeInTheDocument(); // (3+5) contra (1+1)
    expect(sessoes.getByRole("img")).toHaveAttribute(
      "aria-label",
      expect.stringContaining("Sessões 10 no total"),
    );
  });

  it("um painel sem registos diz-o em vez de desenhar um gráfico vazio", async () => {
    render(<AdminEvolucao aoSairDaSessao={() => {}} />);
    const vazio = await screen.findByTestId("evolucao-descargas");
    expect(within(vazio).getByText(/Ainda sem registos/)).toBeInTheDocument();
    expect(within(vazio).queryByRole("img")).toBeNull();
  });

  it("os países aparecem por extenso e a média/o pico ignoram os dias sem dados", async () => {
    render(<AdminEvolucao aoSairDaSessao={() => {}} />);
    const paises = await screen.findByTestId("evolucao-paises");
    expect(within(paises).getByText(/Portugal \(PT\)/)).toBeInTheDocument();
    expect(within(paises).getByText("Desconhecido")).toBeInTheDocument();
    const cpu = within(screen.getByTestId("evolucao-cpu"));
    expect(cpu.getByText("20 %")).toBeInTheDocument(); // a média de 10 e 30, sem os dias vazios (e não a soma das séries)
    expect(cpu.getByText("90 %")).toBeInTheDocument(); // a série «Máxima» resume-se pelo pico
    expect(cpu.getByText("média")).toBeInTheDocument();
    expect(cpu.getByText("pico")).toBeInTheDocument();
  });

  it("mudar o período volta a pedir a evolução com esses dias", async () => {
    render(<AdminEvolucao aoSairDaSessao={() => {}} />);
    await userEvent.selectOptions(await screen.findByTestId("evolucao-periodo"), "7");
    await waitFor(() => expect(pedidos.some((u) => u.startsWith("/api/admin/evolucao?dias=7&"))).toBe(true));
  });

  it("avisa quando o período é maior do que o que se guarda", async () => {
    render(<AdminEvolucao aoSairDaSessao={() => {}} />);
    await screen.findByTestId("evolucao-grupo-Utilização");
    expect(screen.queryByRole("note")).toBeNull();
    await userEvent.selectOptions(screen.getByTestId("evolucao-periodo"), "90");
    await waitFor(() => expect(screen.getByTestId("evolucao-intervalo")).toBeInTheDocument());
    expect(screen.queryByRole("note")).toBeNull(); // 90 dias cabem na retenção dos eventos
  });

  it("mais de 90 dias vêm do histórico permanente e a vista avisa quantos dias há gravados", async () => {
    render(<AdminEvolucao aoSairDaSessao={() => {}} />);
    await userEvent.selectOptions(await screen.findByTestId("evolucao-periodo"), "365");
    const aviso = await screen.findByTestId("evolucao-historico");
    expect(aviso).toHaveTextContent("histórico permanente");
    expect(aviso).toHaveTextContent("Só há 4 dias gravados");
    expect(pedidos.some((u) => u.startsWith("/api/admin/evolucao?dias=365&"))).toBe(true);
  });

  it("sem sessão (404) avisa o painel para voltar a pedir a palavra-passe", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response("{}", { status: 404 }))),
    );
    const aoSair = vi.fn();
    render(<AdminEvolucao aoSairDaSessao={aoSair} />);
    await waitFor(() => expect(aoSair).toHaveBeenCalled());
  });

  it("um erro do servidor mostra um aviso e não parte a página", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response("{}", { status: 500 }))),
    );
    render(<AdminEvolucao aoSairDaSessao={() => {}} />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/Não foi possível carregar a evolução/);
  });
});

describe("funções da evolução", () => {
  it("a tendência compara a segunda metade com a primeira", () => {
    expect(tendencia([1, 1, 3, 5])).toBe(300);
    expect(tendencia([4, 4, 2, 2])).toBe(-50);
    expect(tendencia([0, 0, 0, 0])).toBe(0);
    expect(tendencia([0, 0, 3, 3])).toBeNull(); // não há com que comparar
    expect(tendencia([5])).toBeNull();
  });

  it("o CSV tem uma linha por série, vírgula decimal, país por extenso e BOM", () => {
    const e: Evolucao = {
      ...EVOLUCAO,
      paineis: [
        painel({
          id: "x",
          titulo: "Com; ponto e vírgula",
          series: [{ nome: 'Aspas "a"', valores: [1.5, null, 3, 0] }],
        }),
        painel({
          id: "paises",
          titulo: "Países",
          rotulos: "pais",
          series: [{ nome: "PT", valores: [1, 2, 3, 4] }],
        }),
      ],
    };
    const linhas = paraCsv(e).replace("﻿", "").trim().split("\r\n");
    expect(paraCsv(e).startsWith("﻿")).toBe(true);
    expect(linhas[0]).toBe("Grupo;Painel;Série;2027-01-12;2027-01-13;2027-01-14;2027-01-15");
    expect(linhas[1]).toBe('Utilização;"Com; ponto e vírgula";"Aspas ""a""";1,5;;3;0');
    expect(linhas[2]).toBe("Utilização;Países;Portugal (PT);1;2;3;4");
  });

  it("as cores têm significado fixo para certo, erro, aviso e outros", () => {
    expect(corDaSerie("Concluída", 0)).toBe("var(--ok)");
    expect(corDaSerie("Falhou", 1)).toBe("var(--erro)");
    expect(corDaSerie("Erros do servidor (5xx)", 2)).toBe("var(--erro)");
    expect(corDaSerie("Erros do cliente (4xx)", 0)).toBe("var(--aviso)");
    expect(corDaSerie("Outros", 3)).toBe("var(--suave)");
    expect(corDaSerie("pt", 0)).not.toBe(corDaSerie("en", 1));
  });

  it("o gráfico desenha uma barra por série e dia com valor, e diz que hoje está incompleto", async () => {
    const { container } = render(
      <GraficoDiario
        titulo="T"
        dias={DIAS}
        tipo="barras"
        series={[
          { nome: "A", cor: "red", valores: [1, 0, 2, 3] },
          { nome: "B", cor: "blue", valores: [0, 0, 1, 0] },
        ]}
      />,
    );
    expect(container.querySelectorAll("rect[style*='fill']")).toHaveLength(4); // A: 3 dias com valor; B: 1
    expect(screen.getByRole("img")).toHaveAttribute("aria-label", expect.stringContaining("A 6 no total"));
  });
});

describe("as abas do painel", () => {
  it("a vista «Evolução diária» esconde a visão geral e volta a mostrá-la", async () => {
    const estado = {
      versao: "3.49.0",
      agora: 1_800_000_000,
      arranque: 1_799_990_000,
      dados_desde: 1_799_990_000,
      dados_efemeros: false,
      base_de_dados: { tipo: "postgres", erro: false, intervalo_min: 60 },
      sistema: {
        cpu: 1,
        cpu_nucleos: 1,
        mem_servidor_mb: 1,
        mem_motor_mb: 1,
        mem_contentor_mb: 1,
        mem_limite_mb: null,
        mem_no_contentor: false,
        disco_usado_mb: 1,
        disco_livre_mb: 1,
        sessoes_ativas: 0,
        geracao_em_curso: false,
        motor_vivo: true,
        motor_reinicios: 0,
        python: "3",
        plataforma: "x",
      },
      limites: {},
      proxy: {
        pedidos: 0,
        ips_distintos: 0,
        privados_pct: null,
        xff_pct: null,
        pais_pct: null,
        veredicto: "sem_dados",
      },
      acordado: {
        ativo: false,
        cada_min: 10,
        chamadas: 0,
        falhas: 0,
        ultima_em: null,
        ultima_ok: null,
        ultimo_ms: 0,
      },
      intervalos: ["1h", "6h"],
    };
    vi.stubGlobal(
      "fetch",
      vi.fn((entrada: RequestInfo | URL) => {
        const url = String(entrada);
        const corpo = url.startsWith("/api/admin/estado")
          ? estado
          : url.startsWith("/api/admin/evolucao")
            ? EVOLUCAO
            : null;
        if (!corpo) return new Promise<Response>(() => {}); // dados, erros e SEO ficam por responder: só interessam as abas
        return Promise.resolve(new Response(JSON.stringify(corpo), { status: 200 }));
      }),
    );
    render(<Admin />);
    const aba = await screen.findByTestId("admin-vista-evolucao");
    expect(screen.getByTestId("admin-vista-geral")).toHaveAttribute("aria-pressed", "true");
    expect(screen.queryByTestId("admin-evolucao")).toBeNull();
    await userEvent.click(aba);
    expect(await screen.findByTestId("admin-evolucao")).toBeInTheDocument();
    expect(aba).toHaveAttribute("aria-pressed", "true");
    expect(screen.queryByTestId("admin-intervalo")).toBeNull(); // o intervalo é da visão geral
    expect(screen.queryByText("Agora")).toBeNull();
    await userEvent.click(screen.getByTestId("admin-vista-geral"));
    expect(screen.queryByTestId("admin-evolucao")).toBeNull();
    expect(await screen.findByTestId("admin-intervalo")).toBeInTheDocument();
  });
});
