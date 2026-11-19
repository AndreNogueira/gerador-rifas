import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminRelatorio } from "./AdminRelatorio";

let estado: Record<string, unknown>;
let pedidos: { metodo: string; url: string }[];
let respostaEnviar: { status: number; detail?: string };

const json = (corpo: unknown, status = 200) =>
  Promise.resolve(new Response(JSON.stringify(corpo), { status }));

beforeEach(() => {
  pedidos = [];
  respostaEnviar = { status: 200 };
  estado = {
    ativo: true,
    tem_chave: true,
    destinos: ["a**@exemplo.pt"],
    fuso: "Europe/Lisbon",
    persistente: true,
    ultimo: { dia: "2026-11-18", enviado: 1_800_000_000 },
    erro: "",
    erro_em: null,
    alertas: {
      ativo: true,
      espera_h: 6,
      regras: [
        { chave: "erros5xx", texto: "5 ou mais erros do servidor (5xx) em 15 minutos" },
        { chave: "memoria", texto: "memória do contentor acima de 460 MB (limite do Render: 512)" },
      ],
      ultimos: { erros5xx: 1_800_000_000, memoria: null },
      erro: "",
    },
  };
  vi.stubGlobal(
    "fetch",
    vi.fn((entrada: RequestInfo | URL, init?: RequestInit) => {
      const url = String(entrada);
      pedidos.push({ metodo: init?.method ?? "GET", url });
      if (url.startsWith("/api/admin/relatorio/previa"))
        return json({
          assunto: "Gerador de Rifas · 18 de nov: 5 sessões",
          html: "<p>Olá</p>",
          texto: "Olá",
          dia: "2026-11-18",
          alertas: 0,
        });
      if (url.startsWith("/api/admin/relatorio/enviar"))
        return json(
          respostaEnviar.status === 200 ? { enviado: true } : { detail: respostaEnviar.detail },
          respostaEnviar.status,
        );
      return json(estado);
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

describe("o relatório diário no painel", () => {
  it("mostra para onde vai (mascarado) e quando saiu o último", async () => {
    render(<AdminRelatorio leitura={false} aoSairDaSessao={() => {}} />);
    const ativo = await screen.findByTestId("admin-relatorio-ativo");
    expect(ativo).toHaveTextContent("a**@exemplo.pt");
    expect(ativo).toHaveTextContent("2026-11-18");
  });

  it("desligado, diz o que falta definir no Render e não deixa enviar", async () => {
    estado = { ...estado, ativo: false, tem_chave: false, destinos: [], ultimo: null };
    render(<AdminRelatorio leitura={false} aoSairDaSessao={() => {}} />);
    const aviso = await screen.findByTestId("admin-relatorio-desligado");
    expect(aviso).toHaveTextContent("RESEND_API_KEY");
    expect(aviso).toHaveTextContent("RELATORIO_EMAIL_PARA");
    expect(screen.getByTestId("admin-relatorio-enviar")).toBeDisabled();
  });

  it("pré-visualiza o relatório num iframe sem permissões", async () => {
    render(<AdminRelatorio leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.click(await screen.findByTestId("admin-relatorio-ver"));
    const previa = await screen.findByTestId("admin-relatorio-previa");
    const iframe = previa.querySelector("iframe") as HTMLIFrameElement;
    expect(iframe).toHaveAttribute("sandbox", ""); // nada de scripts no HTML do e-mail
    expect(iframe.getAttribute("srcdoc")).toContain("Olá");
    expect(previa).toHaveTextContent("5 sessões");
  });

  it("o teste envia o dia escolhido e confirma", async () => {
    render(<AdminRelatorio leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.type(await screen.findByTestId("admin-relatorio-dia"), "2026-11-17");
    await userEvent.click(screen.getByTestId("admin-relatorio-enviar"));
    expect(await screen.findByTestId("admin-relatorio-aviso")).toHaveTextContent("E-mail de teste enviado");
    expect(
      pedidos.some((p) => p.metodo === "POST" && p.url === "/api/admin/relatorio/enviar?dia=2026-11-17"),
    ).toBe(true);
  });

  it("lista as regras dos alertas, quando avisaram, e envia um alerta de teste", async () => {
    render(<AdminRelatorio leitura={false} aoSairDaSessao={() => {}} />);
    const regras = await screen.findByTestId("admin-alertas-regras");
    expect(regras).toHaveTextContent("5 ou mais erros do servidor");
    expect(regras).toHaveTextContent("último aviso");
    await userEvent.click(screen.getByTestId("admin-alerta-teste"));
    expect(await screen.findByTestId("admin-relatorio-aviso")).toHaveTextContent("Alerta de teste enviado");
    expect(pedidos.some((p) => p.metodo === "POST" && p.url === "/api/admin/relatorio/alerta-teste")).toBe(
      true,
    );
  });

  it("alertas desligados avisam e não deixam enviar o teste", async () => {
    estado = { ...estado, alertas: { ...(estado.alertas as object), ativo: false } };
    render(<AdminRelatorio leitura={false} aoSairDaSessao={() => {}} />);
    expect(await screen.findByTestId("admin-alertas-desligados")).toBeInTheDocument();
    expect(screen.getByTestId("admin-alerta-teste")).toBeDisabled();
  });

  it("um envio recusado mostra o motivo", async () => {
    respostaEnviar = { status: 502, detail: "Nao foi possivel enviar (HTTP 403)." };
    render(<AdminRelatorio leitura={false} aoSairDaSessao={() => {}} />);
    await userEvent.click(await screen.findByTestId("admin-relatorio-enviar"));
    await waitFor(() => expect(screen.getByTestId("admin-relatorio-aviso")).toHaveTextContent("HTTP 403"));
  });

  it("quem só tem leitura pode ver mas não enviar", async () => {
    render(<AdminRelatorio leitura aoSairDaSessao={() => {}} />);
    await screen.findByTestId("admin-relatorio-ver");
    expect(screen.queryByTestId("admin-relatorio-enviar")).not.toBeInTheDocument();
  });
});
