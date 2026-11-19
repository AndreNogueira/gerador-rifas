import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminObjetivos } from "./AdminObjetivos";
import type { ObjetivosEstado } from "./admin-api";

let estado: ObjetivosEstado;
let pedidos: { metodo: string; url: string; corpo?: string }[];
let falhaAoGuardar: { estado: number; detail: string } | null;

const json = (corpo: unknown, status = 200) =>
  Promise.resolve(new Response(JSON.stringify(corpo), { status }));

const kpi = (chave: string, rotulo: string, extra: Partial<ObjetivosEstado["kpis"][number]> = {}) => ({
  chave,
  rotulo,
  meta: null,
  ontem: 0,
  media7: 0,
  dias_cumpridos: 0,
  dias: 7,
  atingido: null,
  pct: null,
  ...extra,
});

beforeEach(() => {
  pedidos = [];
  falhaAoGuardar = null;
  estado = {
    dia: "2026-11-18",
    kpis: [
      kpi("sessoes", "Sessões", {
        meta: 4,
        ontem: 5,
        media7: 2.4,
        dias_cumpridos: 1,
        atingido: true,
        pct: 125,
      }),
      kpi("geracoes", "Gerações pedidas", { meta: 10, ontem: 3, media7: 1.3, atingido: false, pct: 30 }),
      kpi("numeros", "Números gerados", { ontem: 6000, media7: 3000 }),
    ],
  };
  vi.stubGlobal(
    "fetch",
    vi.fn((entrada: RequestInfo | URL, init?: RequestInit) => {
      const url = String(entrada);
      const metodo = init?.method ?? "GET";
      pedidos.push({ metodo, url, corpo: init?.body as string | undefined });
      if (metodo === "PUT") {
        if (falhaAoGuardar) return json({ detail: falhaAoGuardar.detail }, falhaAoGuardar.estado);
        const { chave, meta } = JSON.parse(init?.body as string);
        estado = { ...estado, kpis: estado.kpis.map((k) => (k.chave === chave ? { ...k, meta } : k)) };
        return json({ chave, meta });
      }
      return json(estado);
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

describe("os objetivos diários no painel", () => {
  it("mostra a meta, ontem (cumprido ou não), a média e os dias cumpridos", async () => {
    render(<AdminObjetivos leitura={false} aoSairDaSessao={() => {}} />);
    const sessoes = await screen.findByTestId("objetivo-sessoes");
    expect(within(sessoes).getByTestId("objetivo-meta-sessoes")).toHaveValue("4");
    expect(within(sessoes).getByTestId("objetivo-ontem-sessoes")).toHaveTextContent("5 ✔ 125 %");
    expect(sessoes).toHaveTextContent("1 de 7");
    expect(screen.getByTestId("objetivo-ontem-geracoes")).toHaveTextContent("3 ✘ 30 %");
    expect(screen.getByTestId("objetivo-ontem-numeros")).not.toHaveTextContent("%");
    expect(screen.getByTestId("objetivo-numeros")).toHaveTextContent("—");
    expect(screen.getByTestId("admin-objetivos")).toHaveTextContent("2026-11-18");
  });

  it("guardar envia a meta (com vírgula decimal) e confirma", async () => {
    render(<AdminObjetivos leitura={false} aoSairDaSessao={() => {}} />);
    const campo = await screen.findByTestId("objetivo-meta-numeros");
    await userEvent.type(campo, "5000,5");
    await userEvent.click(screen.getByTestId("objetivo-guardar-numeros"));
    expect(await screen.findByTestId("admin-objetivos-guardado")).toHaveTextContent(
      "Objetivo de «Números gerados» guardado",
    );
    expect(pedidos.some((p) => p.metodo === "PUT" && p.corpo === '{"chave":"numeros","meta":5000.5}')).toBe(
      true,
    );
  });

  it("deixar o campo vazio apaga o objetivo", async () => {
    render(<AdminObjetivos leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.clear(await screen.findByTestId("objetivo-meta-sessoes"));
    await userEvent.click(screen.getByTestId("objetivo-guardar-sessoes"));
    expect(await screen.findByTestId("admin-objetivos-guardado")).toHaveTextContent("apagado");
    expect(pedidos.some((p) => p.metodo === "PUT" && p.corpo === '{"chave":"sessoes","meta":null}')).toBe(
      true,
    );
  });

  it("uma meta inválida nem chega ao servidor", async () => {
    render(<AdminObjetivos leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.type(await screen.findByTestId("objetivo-meta-numeros"), "-3");
    await userEvent.click(screen.getByTestId("objetivo-guardar-numeros"));
    expect(await screen.findByRole("alert")).toHaveTextContent("maior que zero");
    expect(pedidos.some((p) => p.metodo === "PUT")).toBe(false);
  });

  it("um erro do servidor ao guardar mostra a mensagem", async () => {
    falhaAoGuardar = { estado: 422, detail: "A meta tem de ser maior que zero" };
    render(<AdminObjetivos leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.type(await screen.findByTestId("objetivo-meta-numeros"), "7");
    await userEvent.click(screen.getByTestId("objetivo-guardar-numeros"));
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("A meta tem de ser maior que zero"),
    );
  });

  it("quem só tem leitura vê mas não pode editar", async () => {
    render(<AdminObjetivos leitura aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("objetivo-meta-sessoes")).toBeDisabled();
    expect(screen.queryByTestId("objetivo-guardar-sessoes")).toBeNull();
  });

  it("sem sessão (404) avisa o painel", async () => {
    const sair = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => json({}, 404)),
    );
    render(<AdminObjetivos leitura={false} aoSairDaSessao={sair} />);
    await waitFor(() => expect(sair).toHaveBeenCalled());
  });
});
