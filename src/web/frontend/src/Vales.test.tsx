import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import type { PedidoVale } from "./api";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";
import { singularDe } from "./Vales";

let servidor: ServidorFalso;
const pedidosA = (fim: string) => servidor.pedidos.filter((p) => p.url === fim);

beforeEach(() => {
  localStorage.clear();
  servidor = new ServidorFalso();
  servidor.instalar();
  URL.createObjectURL = vi.fn(() => "blob:previa");
  URL.revokeObjectURL = vi.fn();
  window.history.pushState({}, "", "/precario");
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
});

describe("o singular proposto", () => {
  it("tira só um «s» final, e deixa em paz nomes curtos ou sem «s»", () => {
    expect(singularDe("fichas")).toBe("ficha");
    expect(singularDe("  tokens ")).toBe("token");
    expect(singularDe("ox")).toBe("ox");
    expect(singularDe("as")).toBe("as");
    expect(singularDe("")).toBe("");
  });
});

describe("os vales de fichas no preçário", () => {
  it("só aparecem com uma moeda inventada que tenha nome", async () => {
    await screen.findByTestId("precario-inventada");
    expect(screen.queryByTestId("vales")).toBeNull();
    await userEvent.click(screen.getByTestId("precario-inventada"));
    expect(screen.queryByTestId("vales")).toBeNull();
    await userEvent.type(screen.getByTestId("precario-inv-nome"), "fichas");
    expect(await screen.findByTestId("vales")).toBeInTheDocument();
  });

  it("desenham a pré-visualização com o pedido certo e «Criar» põe o vale na sessão e vai para o ecrã principal", async () => {
    await userEvent.click(await screen.findByTestId("precario-inventada"));
    await userEvent.type(screen.getByTestId("precario-inv-nome"), "fichas");
    await screen.findByTestId("vales");
    const q = screen.getByTestId("vales-quantidade");
    await userEvent.clear(q);
    await userEvent.type(q, "3");
    await userEvent.type(screen.getByTestId("vales-nota"), "Só na festa");
    await waitFor(() => {
      const p = pedidosA("/api/vales/previa.png").at(-1)?.corpo as PedidoVale;
      expect(p.moeda).toBe("ficha");
      expect(p.moeda_plural).toBe("fichas");
      expect(p.quantidade).toBe(3);
      expect(p.nota).toBe("Só na festa");
      expect(p.titulo).toBe("VALE");
    });
    expect(await screen.findByTestId("vales-previa")).toBeInTheDocument();
    await userEvent.click(screen.getByTestId("vales-criar"));
    await waitFor(() => expect(window.location.pathname).toBe("/"));
    const pedido = servidor.pedidos.find((p) => /\/sessoes\/[^/]+\/vales$/.test(p.url));
    expect((pedido?.corpo as PedidoVale | undefined)?.quantidade).toBe(3);
  });

  it("a quantidade só aceita algarismos e um erro do servidor aparece e trava o botão", async () => {
    await userEvent.click(await screen.findByTestId("precario-inventada"));
    await userEvent.type(screen.getByTestId("precario-inv-nome"), "fichas");
    await screen.findByTestId("vales");
    const q = screen.getByTestId("vales-quantidade");
    await userEvent.clear(q);
    await userEvent.type(q, "a4b");
    expect(q).toHaveValue("4");
    servidor.valesErro = "A quantidade de cada vale tem de estar entre 1 e 99.";
    await userEvent.type(screen.getByTestId("vales-titulo"), "!");
    expect(await screen.findByTestId("vales-erro")).toHaveTextContent("entre 1 e 99");
    expect(screen.getByTestId("vales-criar")).toBeDisabled();
  });
});
