import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminCopia } from "./AdminCopia";
import type { CopiaEstado } from "./admin-api";

let estado: CopiaEstado;
let pedidos: { metodo: string; url: string }[];
let resposta: { estado: number; corpo: unknown };

const json = (corpo: unknown, status = 200) =>
  Promise.resolve(new Response(JSON.stringify(corpo), { status }));

beforeEach(() => {
  pedidos = [];
  resposta = {
    estado: 200,
    corpo: {
      chave: "backups/rifas-manual.json.gz",
      bytes: 2048,
      linhas: { historico_diario: 10, comentarios: 3 },
    },
  };
  estado = {
    ativa: true,
    tem_s3: true,
    tem_bd: true,
    bucket: "rifas-backups",
    tabelas: ["historico_diario", "comentarios"],
    posicoes: 8,
    ultimo: { dia: "backup:2026-11-16", enviado: 1_800_000_000 },
    ultimo_tamanho: 5120,
    erro: "",
    erro_em: null,
  };
  vi.stubGlobal(
    "fetch",
    vi.fn((entrada: RequestInfo | URL, init?: RequestInit) => {
      const url = String(entrada);
      const metodo = init?.method ?? "GET";
      pedidos.push({ metodo, url });
      if (metodo === "POST") return json(resposta.corpo, resposta.estado);
      return json(estado);
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

describe("a cópia de segurança no painel", () => {
  it("ligada diz o bucket e quando foi a última semana (sem credenciais)", async () => {
    render(<AdminCopia leitura={false} aoSairDaSessao={() => {}} />);
    const ativa = await screen.findByTestId("admin-copia-ativa");
    expect(ativa).toHaveTextContent("rifas-backups");
    expect(ativa).toHaveTextContent("semana de 2026-11-16");
    expect(ativa).toHaveTextContent("5 KB");
    expect(screen.getByTestId("admin-copia")).toHaveTextContent("historico_diario, comentarios");
  });

  it("desligada diz o que falta e não deixa fazer a cópia", async () => {
    estado = { ...estado, ativa: false, tem_s3: false, ultimo: null, bucket: "" };
    render(<AdminCopia leitura={false} aoSairDaSessao={() => {}} />);
    const aviso = await screen.findByTestId("admin-copia-desligada");
    expect(aviso).toHaveTextContent("BACKUP_S3_SECRET_ACCESS_KEY");
    expect(screen.getByTestId("admin-copia-fazer")).toBeDisabled();
  });

  it("sem Postgres explica que só funciona com a base externa", async () => {
    estado = { ...estado, ativa: false, tem_bd: false };
    render(<AdminCopia leitura={false} aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("admin-copia-desligada")).toHaveTextContent("DATABASE_URL");
  });

  it("fazer uma cópia agora mostra o tamanho e as linhas", async () => {
    render(<AdminCopia leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.click(await screen.findByTestId("admin-copia-fazer"));
    const aviso = await screen.findByTestId("admin-copia-aviso");
    expect(aviso).toHaveTextContent("Cópia feita (2 KB, 13 linhas) em backups/rifas-manual.json.gz");
    expect(pedidos.some((p) => p.metodo === "POST" && p.url === "/api/admin/copia/fazer")).toBe(true);
  });

  it("um erro do servidor mostra o motivo", async () => {
    resposta = {
      estado: 502,
      corpo: { detail: "Nao foi possivel fazer a copia (armazenamento: HTTP 403)." },
    };
    render(<AdminCopia leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.click(await screen.findByTestId("admin-copia-fazer"));
    await waitFor(() => expect(screen.getByTestId("admin-copia-aviso")).toHaveTextContent("HTTP 403"));
  });

  it("um erro da última cópia semanal aparece, e a leitura não tem o botão", async () => {
    estado = { ...estado, erro: "armazenamento: HTTP 403", erro_em: 1_800_000_100 };
    render(<AdminCopia leitura aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("admin-copia-erro")).toHaveTextContent("HTTP 403");
    expect(screen.queryByTestId("admin-copia-fazer")).toBeNull();
  });

  it("sem sessão (404) avisa o painel", async () => {
    const sair = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => json({}, 404)),
    );
    render(<AdminCopia leitura={false} aoSairDaSessao={sair} />);
    await waitFor(() => expect(sair).toHaveBeenCalled());
  });
});
