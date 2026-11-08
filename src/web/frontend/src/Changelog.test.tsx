import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  new ServidorFalso().instalar();
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
  it("o rodapé leva-o à página com as versões, da mais recente para a mais antiga", async () => {
    abrir();
    await userEvent.click(await screen.findByRole("link", { name: "Changelog" }));
    expect(await screen.findByTestId("versao-3.0.0")).toHaveTextContent("Uma novidade de teste.");
    const versoes = screen.getAllByTestId(/^versao-/).map((e) => e.getAttribute("data-testid"));
    expect(versoes).toEqual(["versao-3.0.0", "versao-2.9.0"]);
    await waitFor(() => expect(document.title).toBe("Changelog | Gerador de Rifas"));
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });
});
