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
  servidor = new ServidorFalso();
  servidor.instalar();
});
afterEach(() => vi.unstubAllGlobals());

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

describe("rodapé e páginas de texto", () => {
  it("sem configuração o rodapé só tem Changelog, Termos e Privacidade", async () => {
    abrir();
    const rodape = await screen.findByRole("navigation", { name: "Informação" });
    expect(Array.from(rodape.querySelectorAll("a")).map((a) => a.textContent)).toEqual([
      "Changelog",
      "Termos",
      "Privacidade",
    ]);
    expect(screen.queryByTestId("donativo")).toBeNull();
  });

  it("com contacto e donativo configurados aparecem; o donativo abre noutro separador sem referrer", async () => {
    servidor.donativoUrl = "https://exemplo.pt/doar";
    servidor.temContacto = true;
    abrir();
    const doar = await screen.findByTestId("donativo");
    expect(doar).toHaveAttribute("href", "https://exemplo.pt/doar");
    expect(doar).toHaveAttribute("target", "_blank");
    expect(doar).toHaveAttribute("rel", "noopener noreferrer");
    expect(screen.getByRole("link", { name: "Contacto" })).toBeInTheDocument();
  });

  it("os Termos abrem com o texto do servidor, o aviso de versão provisória e o título do separador", async () => {
    abrir();
    await userEvent.click(await screen.findByRole("link", { name: "Termos" }));
    expect(await screen.findByTestId("pagina-termos")).toHaveTextContent("Um parágrafo de teste.");
    expect(screen.getByText("Versão provisória de teste.")).toBeInTheDocument();
    await waitFor(() => expect(document.title).toBe("Termos de utilização | Gerador de Rifas"));
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });
});
