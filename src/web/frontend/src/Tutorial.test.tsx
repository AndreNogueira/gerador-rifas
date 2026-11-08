import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

beforeEach(() => {
  localStorage.clear();
  new ServidorFalso().instalar();
});
afterEach(() => vi.unstubAllGlobals());

function abrir(caminho: string) {
  window.history.pushState({}, "", caminho);
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

describe("tutorial", () => {
  it("os tópicos de base não têm vídeo e o de uma funcionalidade mostra o seu vídeo (com nome acessível)", async () => {
    abrir("/tutorial?p=0");
    expect(await screen.findByTestId("topico")).toHaveTextContent("Escolha o template.");
    expect(screen.queryByTestId("video-topico")).toBeNull();
    await userEvent.click(screen.getByTestId("topico-1"));
    const video = await screen.findByTestId("video-topico");
    expect(video).toHaveAttribute("src", "/videos/web_galeria_pt.mp4");
    expect(video).toHaveAttribute("controls");
    expect(video).toHaveAccessibleName("Ver o vídeo deste tópico: Galeria de templates");
    await userEvent.click(screen.getByRole("button", { name: /Anterior|tut_ant/ }));
    expect(screen.queryByTestId("video-topico")).toBeNull();
  });
});
