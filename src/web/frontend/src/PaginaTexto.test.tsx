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
  it("sem configuração o rodapé só tem as páginas dos visitantes, o Changelog, os Termos e a Privacidade", async () => {
    abrir();
    const rodape = await screen.findByRole("navigation", { name: "Informação" });
    expect(Array.from(rodape.querySelectorAll("a")).map((a) => a.textContent)).toEqual([
      "Comentários",
      "Deixar um comentário",
      "Reportar problema",
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
    await waitFor(() => expect(document.title).toBe("Página termos | Gerador de Rifas"));
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("as páginas de texto voltam a pedir-se quando a língua muda (o texto vem do servidor, já traduzido)", async () => {
    abrir();
    await userEvent.click(await screen.findByRole("link", { name: "Privacidade" }));
    await screen.findByTestId("pagina-privacidade");
    await userEvent.selectOptions(screen.getByTestId("lingua"), "en");
    await waitFor(() => {
      const linguas = servidor.pedidos
        .filter((p) => p.url === "/api/pagina/privacidade")
        .map((p) => p.lingua);
      expect(linguas.at(0)).toBe("pt");
      expect(linguas.at(-1)).toBe("en");
    });
  });
});
