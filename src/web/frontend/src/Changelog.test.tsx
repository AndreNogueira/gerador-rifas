import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;
beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  servidor = new ServidorFalso().instalar();
});
afterEach(() => vi.unstubAllGlobals());

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

describe("changelog", () => {
  it("tem uma ligação para descarregar a app Windows (o programa, sem código-fonte, do repositório público)", async () => {
    window.history.pushState({}, "", "/changelog");
    abrir();
    const ligacao = await screen.findByTestId("descarga-windows");
    expect(ligacao).toHaveAttribute(
      "href",
      "https://github.com/AndreNogueira/gerador-rifas-windows/releases/latest/download/GeradorRifas.exe",
    );
    expect(ligacao).toHaveTextContent("Descarregar a app Windows");
  });

  it("o rodapé leva-o à página com as versões, da mais recente para a mais antiga", async () => {
    abrir();
    await userEvent.click(await screen.findByRole("link", { name: "Changelog" }));
    expect(await screen.findByTestId("versao-3.0.0")).toHaveTextContent("Uma novidade de teste.");
    const versoes = screen.getAllByTestId(/^versao-/).map((e) => e.getAttribute("data-testid"));
    expect(versoes).toEqual(["versao-3.0.0", "versao-2.9.0"]);
    await waitFor(() => expect(document.title).toBe("Changelog | Gerador de Rifas"));
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("pede o changelog na língua escolhida: em português é o completo, nas outras avisa que é um resumo traduzido", async () => {
    abrir();
    await userEvent.click(await screen.findByRole("link", { name: "Changelog" }));
    await screen.findByTestId("versao-3.0.0");
    expect(screen.queryByTestId("changelog-resumo")).toBeNull();
    expect(screen.getByTestId("versao-3.0.0")).toHaveTextContent("Versão 3.0.0");
    await userEvent.selectOptions(screen.getByTestId("lingua"), "en");
    expect(await screen.findByTestId("changelog-resumo")).toHaveTextContent("This is a translated summary.");
    expect(screen.getByTestId("versao-3.0.0")).toHaveTextContent("Version 3.0.0");
    const pedidos = servidor.pedidos.filter((p) => p.url === "/api/changelog").map((p) => p.lingua);
    expect(pedidos.at(0)).toBe("pt");
    expect(pedidos.at(-1)).toBe("en"); // mudar de língua volta a pedir o texto
  });
});
