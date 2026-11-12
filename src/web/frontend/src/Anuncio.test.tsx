import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/");
  window.adsbygoogle = undefined;
  servidor = new ServidorFalso().instalar();
});
afterEach(() => {
  window.adsbygoogle = undefined;
});

function abrir(caminho = "/") {
  window.history.pushState({}, "", caminho);
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

describe("anúncios (AdSense)", () => {
  it("sem configuração não há bloco nem nada carregado da Google", async () => {
    abrir("/tutorial");
    await screen.findByRole("heading", { name: /tutorial/i, level: 1 }).catch(() => undefined);
    expect(screen.queryByTestId("anuncio")).toBeNull();
    expect(window.adsbygoogle).toBeUndefined();
  });

  it("só o identificador, sem bloco: não mostra nada", async () => {
    servidor.anunciosCliente = "ca-pub-1234567890123456";
    abrir("/");
    await screen.findByTestId("upload-template");
    await new Promise((r) => setTimeout(r, 50));
    expect(screen.queryByTestId("anuncio")).toBeNull();
  });

  it("com identificador e bloco mostra o bloco no fim da página inicial e das de leitura, uma só vez", async () => {
    servidor.anunciosCliente = "ca-pub-1234567890123456";
    servidor.anunciosSlot = "1234567890";
    abrir("/");
    const bloco = await screen.findByTestId("anuncio");
    const ins = bloco.querySelector("ins.adsbygoogle");
    expect(ins).toHaveAttribute("data-ad-client", "ca-pub-1234567890123456");
    expect(ins).toHaveAttribute("data-ad-slot", "1234567890");
    expect(bloco).toHaveTextContent("Publicidade");
    await waitFor(() => expect(window.adsbygoogle).toHaveLength(1));
  });

  it("nunca no editor, no vídeo nem nos textos legais", async () => {
    servidor.anunciosCliente = "ca-pub-1234567890123456";
    servidor.anunciosSlot = "1234567890";
    for (const caminho of ["/editor", "/video", "/termos", "/privacidade", "/admin"]) {
      const { unmount } = render(
        <ProvedorI18n>
          <App />
        </ProvedorI18n>,
      );
      window.history.pushState({}, "", caminho);
      window.dispatchEvent(new Event("popstate"));
      await new Promise((r) => setTimeout(r, 60));
      expect(screen.queryByTestId("anuncio"), caminho).toBeNull();
      unmount();
    }
  });
});
