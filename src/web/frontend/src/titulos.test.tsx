import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

beforeEach(() => {
  localStorage.clear();
  document.title = "";
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

describe("título do separador", () => {
  it("acompanha a página (SEO e acessibilidade)", async () => {
    abrir();
    await waitFor(() => expect(document.title).toBe("Gerador de Rifas"));
    await userEvent.click(await screen.findByTestId("nav-ajuda"));
    await userEvent.click(screen.getByTestId("nav-tutorial"));
    await waitFor(() => expect(document.title).toMatch(/^Tutorial.* \| Gerador de Rifas$/));
    await userEvent.click(screen.getByTestId("nav-sobre"));
    await waitFor(() => expect(document.title).toMatch(/\| Gerador de Rifas$/));
    expect(document.title.startsWith("Tutorial")).toBe(false);
  });

  it("só há um h1 por página", async () => {
    abrir();
    await screen.findByRole("heading", { level: 1, name: "Gerador de Rifas" });
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    await userEvent.click(screen.getByTestId("nav-ajuda"));
    await userEvent.click(screen.getByTestId("nav-tutorial"));
    await waitFor(() => expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1));
    expect(screen.getByRole("heading", { level: 1 }).textContent).toMatch(/Tutorial/);
  });
});
