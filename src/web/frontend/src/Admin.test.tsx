import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Admin } from "./Admin";
import type { Dados, Estado } from "./admin-api";
import { escalaY, formatarNumero, GraficoBarras, GraficoLinhas, Medidor } from "./graficos";

const AGORA = 1_800_000_000;
const ESTADO: Estado = {
  versao: "3.8.0",
  agora: AGORA,
  arranque: AGORA - 7200,
  dados_desde: AGORA - 3600,
  dados_efemeros: true,
  sistema: {
    cpu: 12.3,
    cpu_nucleos: 4,
    mem_servidor_mb: 120,
    mem_motor_mb: 90,
    mem_contentor_mb: 480,
    mem_limite_mb: 512,
    mem_no_contentor: true,
    disco_usado_mb: 3.4,
    disco_livre_mb: 800,
    sessoes_ativas: 7,
    geracao_em_curso: false,
    motor_vivo: true,
    motor_reinicios: 2,
    python: "3.15.2",
    plataforma: "Linux 6",
  },
  limites: {
    max_sessoes: 200,
    max_numeros: 30000,
    max_upload_mb: 25,
    validade_min: 30,
    tempo_maximo_geracao_min: 10,
    pedidos_pesados_por_min: 30,
    pedidos_leves_por_min: 300,
    forwarded_allow_ips: "127.0.0.1",
  },
  proxy: { pedidos: 80, ips_distintos: 1, privados_pct: 100, xff_pct: 100, veredicto: "problema" },
  acordado: {
    ativo: true,
    cada_min: 10,
    chamadas: 4,
    falhas: 0,
    ultima_em: AGORA - 300,
    ultima_ok: true,
    ultimo_ms: 12,
  },
  intervalos: ["1h", "6h", "24h", "7d", "30d"],
};
const DADOS: Dados = {
  intervalo: "6h",
  desde: AGORA - 21600,
  passo_s: 60,
  sistema: [
    {
      t: AGORA - 600,
      cpu: 10,
      mem_servidor: 100,
      mem_motor: 80,
      mem_contentor: 400,
      disco: 3,
      sessoes: 3,
      geracoes: 0,
    },
    {
      t: AGORA - 540,
      cpu: 40,
      mem_servidor: 110,
      mem_motor: 90,
      mem_contentor: 450,
      disco: 3,
      sessoes: 5,
      geracoes: 1,
    },
  ],
  pedidos: [{ t: AGORA - 600, n: 30, e4: 2, e5: 1, p50: 25, p95: 250 }],
  eventos: [{ t: AGORA - 600, sessoes: 2, previas: 3, geracoes: 1, paginas: 4, numeros: 500 }],
  tabela_pedidos: [
    {
      pedido: "POST /api/sessoes",
      n: 12,
      e4: 0,
      e5: 0,
      medio_ms: 8,
      p50: 5,
      p95: 10,
      max_ms: 40,
      sondagem: false,
    },
    {
      pedido: "GET /api/sessoes/{id_}/trabalho",
      n: 900,
      e4: 0,
      e5: 0,
      medio_ms: 2,
      p50: 5,
      p95: 5,
      max_ms: 9,
      sondagem: true,
    },
  ],
  resumo: {
    sessoes: 12,
    previas: { ok: 20, erro: 1 },
    templates: { ok: 11, erro: 1 },
    algarismos: { ok: 10, erro: 0 },
    geracoes: { ok: 5, cancelado: 1, falhou: 1 },
    numeros: 4200,
    paginas: 840,
    descargas: [{ chave: "zip", n: 4 }],
    duracao: {
      mediana_s: 14,
      p95_s: 70,
      max_s: 90,
      histograma: [
        { chave: "até 5 s", n: 1 },
        { chave: "até 15 s", n: 3 },
      ],
    },
    linguas: [
      { chave: "pt", n: 9 },
      { chave: "en", n: 3 },
    ],
    temas: [
      { chave: "matrix", n: 6 },
      { chave: "premiado", n: 6 },
    ],
    dispositivos: [
      { chave: "computador", n: 8 },
      { chave: "movel", n: 4 },
    ],
    paginas_vistas: [{ chave: "/", n: 30 }],
    robos: 3,
    erros_http: [{ chave: "429", n: 2 }],
    falhas: [{ chave: "err_digitos", n: 1 }],
    classes_de_ecra: [
      { chave: "telemóvel", n: 8 },
      { chave: "computador Full HD (1800–2399 px)", n: 4 },
    ],
    ecras: [
      { chave: "393×852 @3x", n: 5 },
      { chave: "1920×1080 @1x", n: 4 },
    ],
    dispositivos_detalhe: [
      { chave: "iPhone", n: 5 },
      { chave: "Pixel 9", n: 3 },
    ],
    janelas: [{ chave: "360–413 px (telemóvel)", n: 8 }],
    toque: [
      { chave: "com toque", n: 8 },
      { chave: "sem toque", n: 4 },
    ],
    reinicios_motor: 1,
    arranques: 1,
  },
};

interface Pedido {
  metodo: string;
  url: string;
  corpo?: string;
  cabecalhos: Record<string, string>;
}
let pedidos: Pedido[];
let autenticado: boolean;
const palavraCerta = "palavra-certa-123";

function json(corpo: unknown, estado = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(corpo), { status: estado, headers: { "Content-Type": "application/json" } }),
  );
}

beforeEach(() => {
  pedidos = [];
  autenticado = false;
  localStorage.clear();
  sessionStorage.clear();
  vi.stubGlobal(
    "fetch",
    vi.fn((entrada: RequestInfo | URL, init?: RequestInit) => {
      const url = String(entrada);
      const metodo = init?.method ?? "GET";
      pedidos.push({
        metodo,
        url,
        corpo: init?.body as string | undefined,
        cabecalhos: (init?.headers ?? {}) as Record<string, string>,
      });
      if (url === "/api/admin/entrar") {
        const { token } = JSON.parse(String(init?.body)) as { token: string };
        if (token === palavraCerta) {
          autenticado = true;
          return json({ ok: true });
        }
        return json({ detail: "Palavra-passe errada." }, 401);
      }
      if (url === "/api/admin/sair") {
        autenticado = false;
        return Promise.resolve(new Response(null, { status: 204 }));
      }
      if (!autenticado) return json({ detail: "Rota inexistente" }, 404);
      if (url === "/api/admin/estado") return json(ESTADO);
      if (url.startsWith("/api/admin/dados"))
        return json({ ...DADOS, intervalo: new URL(url, "http://x").searchParams.get("intervalo") });
      return json({}, 404);
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

describe("painel de administração", () => {
  it("sem sessão pede a palavra-passe e não mostra nenhum dado", async () => {
    render(<Admin />);
    expect(await screen.findByTestId("admin-token")).toHaveAttribute("type", "password");
    expect(screen.queryByText("Agora")).toBeNull();
    expect(pedidos.map((p) => p.url)).toEqual(["/api/admin/estado"]);
  });

  it("uma palavra-passe errada mostra o erro e continua fechado", async () => {
    render(<Admin />);
    await userEvent.type(await screen.findByTestId("admin-token"), "errada");
    await userEvent.click(screen.getByTestId("admin-entrar"));
    expect(await screen.findByTestId("admin-erro")).toHaveTextContent("Palavra-passe errada.");
    expect(screen.queryByText("Agora")).toBeNull();
  });

  it("entra, mostra os números, os gráficos e as explicações, e nunca guarda a palavra-passe", async () => {
    render(<Admin />);
    await userEvent.type(await screen.findByTestId("admin-token"), palavraCerta);
    await userEvent.click(screen.getByTestId("admin-entrar"));
    await screen.findByRole("heading", { name: "Agora" });
    // números atuais, cada um com a sua explicação
    expect(screen.getByText("12 %")).toBeInTheDocument();
    expect(screen.getByText("480 MB")).toBeInTheDocument();
    expect(screen.getByText(/limite 512 MB/)).toBeInTheDocument();
    expect(screen.getAllByText(/Quanto do processador/).length).toBe(1);
    // gráficos (imagens com texto alternativo) e a tabela dos pedidos
    await waitFor(() => expect(screen.getAllByRole("img").length).toBeGreaterThanOrEqual(8));
    expect(screen.getByRole("img", { name: /CPU: CPU 40 %/ })).toBeInTheDocument();
    const tabela = screen.getByTestId("admin-tabela-pedidos");
    expect(within(tabela).getByText("POST /api/sessoes")).toBeInTheDocument();
    expect(within(tabela).getByText(/\(progresso\)/)).toBeInTheDocument();
    // o anti-sono e os ecrãs
    expect(screen.getByText("ativo (10 min)")).toBeInTheDocument();
    expect(screen.getByText(/último pedido ok há 5 min/)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Ecrãs e dispositivos" })).toBeInTheDocument();
    expect(screen.getByText("393×852 @3x")).toBeInTheDocument();
    expect(screen.getByText("Pixel 9")).toBeInTheDocument();
    // aviso dos dados temporários e o veredicto do proxy
    expect(screen.getByRole("note")).toHaveTextContent(/Os dados são temporários/);
    expect(screen.getByTestId("admin-proxy")).toHaveTextContent(/o limite por IP é, na prática, global/);
    expect(screen.getByTestId("admin-proxy").className).toContain("cor-erro");
    // a palavra-passe só foi no corpo do pedido de entrada: não está na página, no URL nem no armazenamento do browser
    expect(document.body.innerHTML).not.toContain(palavraCerta);
    expect(JSON.stringify({ ...localStorage })).not.toContain(palavraCerta);
    expect(JSON.stringify({ ...sessionStorage })).not.toContain(palavraCerta);
    for (const p of pedidos) {
      if (p.url !== "/api/admin/entrar") expect(JSON.stringify(p)).not.toContain(palavraCerta);
    }
  });

  it("mudar o intervalo pede os dados desse intervalo", async () => {
    render(<Admin />);
    await userEvent.type(await screen.findByTestId("admin-token"), palavraCerta);
    await userEvent.click(screen.getByTestId("admin-entrar"));
    await userEvent.selectOptions(await screen.findByTestId("admin-intervalo"), "7d");
    await waitFor(() => expect(pedidos.some((p) => p.url === "/api/admin/dados?intervalo=7d")).toBe(true));
  });

  it("sair volta ao ecrã de entrada", async () => {
    render(<Admin />);
    await userEvent.type(await screen.findByTestId("admin-token"), palavraCerta);
    await userEvent.click(screen.getByTestId("admin-entrar"));
    await userEvent.click(await screen.findByTestId("admin-sair"));
    expect(await screen.findByTestId("admin-token")).toBeInTheDocument();
    expect(pedidos.some((p) => p.url === "/api/admin/sair" && p.metodo === "POST")).toBe(true);
  });

  it("se a sessão expirar a meio, volta ao ecrã de entrada", async () => {
    render(<Admin />);
    await userEvent.type(await screen.findByTestId("admin-token"), palavraCerta);
    await userEvent.click(screen.getByTestId("admin-entrar"));
    await userEvent.click(await screen.findByRole("button", { name: /Atualizar/ }));
    autenticado = false;
    await userEvent.click(screen.getByRole("button", { name: /Atualizar/ }));
    expect(await screen.findByTestId("admin-token")).toBeInTheDocument();
  });
});

describe("gráficos", () => {
  it("escalaY dá máximos redondos", () => {
    expect(escalaY(0.7).topo).toBe(1);
    expect(escalaY(37).topo).toBe(50);
    expect(escalaY(160).topo).toBe(200);
    expect(escalaY(0).marcas).toHaveLength(5);
    expect(escalaY(480).marcas.at(-1)).toBe(500);
  });

  it("formatarNumero abrevia", () => {
    expect([
      formatarNumero(7),
      formatarNumero(7.25),
      formatarNumero(1500),
      formatarNumero(25000),
      formatarNumero(2_500_000),
    ]).toEqual(["7", "7.3", "1.5 k", "25 k", "2.5 M"]);
  });

  it("o gráfico de linhas parte a linha onde faltam dados", () => {
    const pontos = [
      { t: 0, v: 1 },
      { t: 60, v: 2 },
      { t: 600, v: 3 },
      { t: 660, v: 4 },
    ];
    const { container } = render(
      <GraficoLinhas
        titulo="X"
        series={[{ nome: "a", cor: "red", pontos }]}
        desde={0}
        ate={700}
        passo={60}
      />,
    );
    const d = container.querySelector("path.grafico-linha")?.getAttribute("d") ?? "";
    expect(d.match(/M/g)).toHaveLength(2); // o salto de 540 s é maior do que 3 passos
    expect(screen.getByRole("img")).toHaveAccessibleName("X: a 4");
  });

  it("sem dados diz que não há dados", () => {
    render(
      <GraficoLinhas
        titulo="X"
        series={[{ nome: "a", cor: "red", pontos: [{ t: 0, v: null }] }]}
        desde={0}
        ate={100}
        passo={60}
      />,
    );
    expect(screen.getByText("Ainda sem dados neste intervalo")).toBeInTheDocument();
    render(<GraficoBarras titulo="Y" pontos={[]} desde={0} ate={100} passo={60} nome="n" />);
    expect(screen.getAllByText("Ainda sem dados neste intervalo")).toHaveLength(2);
  });

  it("o medidor avisa a partir de 85 % do limite", () => {
    const { container } = render(
      <Medidor titulo="m" limite={512} partes={[{ nome: "A", valor: 450, cor: "red" }]} />,
    );
    expect(container.querySelector("li.cor-erro")?.textContent).toMatch(/88 % do limite de 512 MB/);
    const { container: c2 } = render(
      <Medidor titulo="m" limite={512} partes={[{ nome: "A", valor: 100, cor: "red" }]} />,
    );
    expect(c2.querySelector("li.cor-erro")).toBeNull();
    const { container: c3 } = render(
      <Medidor titulo="m" limite={null} partes={[{ nome: "A", valor: 100, cor: "red" }]} />,
    );
    expect(c3.textContent).toMatch(/sem limite/);
  });
});
