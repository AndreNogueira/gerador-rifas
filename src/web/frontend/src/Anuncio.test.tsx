import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CONSULTA_LATERAIS } from "./Anuncio";
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
  vi.unstubAllGlobals();
});

/** Simula um ecrã largo (com espaço para as laterais) ou estreito. */
function ecra(largo: boolean) {
  vi.stubGlobal("matchMedia", (q: string) => ({
    matches: largo && q === CONSULTA_LATERAIS,
    media: q,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
  }));
}

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

  it("em ecrã largo ficam nas duas laterais (anúncio vertical), sem bloco no fim da página", async () => {
    servidor.anunciosCliente = "ca-pub-1234567890123456";
    servidor.anunciosSlot = "1234567890";
    ecra(true);
    abrir("/");
    await waitFor(() => expect(screen.getAllByTestId("anuncio")).toHaveLength(2));
    const [esq, dir] = screen.getAllByTestId("anuncio");
    expect(esq).toHaveClass("anuncio-lateral", "esquerda");
    expect(dir).toHaveClass("anuncio-lateral", "direita");
    for (const lado of [esq, dir])
      expect(lado?.querySelector("ins")).toHaveAttribute("data-ad-format", "vertical");
    await waitFor(() => expect(window.adsbygoogle).toHaveLength(2));
  });

  it("em ecrã estreito fica um só bloco, no fim da página", async () => {
    servidor.anunciosCliente = "ca-pub-1234567890123456";
    servidor.anunciosSlot = "1234567890";
    ecra(false);
    abrir("/tutorial");
    const bloco = await screen.findByTestId("anuncio");
    expect(screen.getAllByTestId("anuncio")).toHaveLength(1);
    expect(bloco).not.toHaveClass("anuncio-lateral");
    expect(bloco.querySelector("ins")).toHaveAttribute("data-ad-format", "auto");
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

  describe("o preçário (/precario)", () => {
    const configurar = () => {
      servidor.anunciosCliente = "ca-pub-1234567890123456";
      servidor.anunciosSlot = "1234567890";
    };

    it("em ecrã largo leva os dois laterais, fora do conteúdo e nunca dentro da pré-visualização", async () => {
      configurar();
      ecra(true);
      abrir("/precario");
      await waitFor(() => expect(screen.getAllByTestId("anuncio")).toHaveLength(2));
      await screen.findByTestId("precario-ocasiao");
      for (const lado of screen.getAllByTestId("anuncio")) {
        expect(lado).toHaveClass("anuncio-lateral");
        expect(lado.closest(".precario-previa")).toBeNull();
        expect(lado.closest(".precario")).toBeNull();
        expect(document.querySelector(".precario-previa")?.contains(lado)).toBe(false);
      }
    });

    it("em ecrã estreito não leva nenhum (os botões de descarregar ficam no fim da página)", async () => {
      configurar();
      ecra(false);
      abrir("/precario");
      await screen.findByTestId("precario-ocasiao");
      await new Promise((r) => setTimeout(r, 50));
      expect(screen.queryByTestId("anuncio")).toBeNull();
      expect(window.adsbygoogle).toBeUndefined();
    });

    it("sem configuração não há nada, e o guia do preçário continua sem anúncios", async () => {
      ecra(true);
      abrir("/precario");
      await screen.findByTestId("precario-ocasiao");
      expect(screen.queryByTestId("anuncio")).toBeNull();
      configurar();
      abrir("/como-fazer-o-precario-de-uma-festa");
      await new Promise((r) => setTimeout(r, 50));
      expect(screen.queryByTestId("anuncio")).toBeNull();
    });
  });
});
