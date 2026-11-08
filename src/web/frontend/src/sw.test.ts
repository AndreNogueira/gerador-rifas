// Corre o public/sw.js a sério (num contexto isolado) com uma cache e uma rede falsas.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";
import { describe, expect, it, vi } from "vitest";

const CODIGO = readFileSync(join(__dirname, "..", "public", "sw.js"), "utf8");
const ORIGEM = "https://rifas.exemplo.pt";

interface Evento {
  request: { method: string; url: string; mode?: string };
  respondWith?: (r: Promise<Response>) => void;
  waitUntil?: (p: Promise<unknown>) => void;
}

function carregar(versao = "1.0.0", nomesAntigos: string[] = []) {
  const ouvintes: Record<string, (e: Evento) => void> = {};
  const guardados = new Map<string, Response>();
  const apagadas: string[] = [];
  const chave = (k: string | { url: string }) => (typeof k === "string" ? new URL(k, ORIGEM).href : k.url);
  const caches = {
    open: async () => ({
      addAll: async () => undefined,
      put: async (k: string | { url: string }, v: Response) => void guardados.set(chave(k), v),
    }),
    match: async (k: string | { url: string }) => guardados.get(chave(k))?.clone(),
    keys: async () => [`rifas-casca-${versao}`, ...nomesAntigos],
    delete: async (n: string) => void apagadas.push(n),
  };
  const rede = vi.fn(async (_p: unknown) => new Response("da rede"));
  const self = {
    location: { href: `${ORIGEM}/sw.js?v=${versao}`, origin: ORIGEM },
    addEventListener: (tipo: string, f: (e: Evento) => void) => {
      ouvintes[tipo] = f;
    },
    skipWaiting: () => undefined,
    clients: { claim: async () => undefined },
  };
  vm.runInNewContext(CODIGO, { self, caches, fetch: rede, URL, Response, Promise });
  /** Pede `url`: devolve a resposta, ou null se o service worker não a intercetou (vai direita à rede). */
  async function pedir(url: string, extra: Partial<Evento["request"]> = {}): Promise<string | null> {
    let resposta: Promise<Response> | null = null;
    const ev: Evento = {
      request: { method: "GET", url: `${ORIGEM}${url}`, ...extra },
      respondWith: (r) => {
        resposta = r;
      },
    };
    ouvintes.fetch?.(ev);
    if (!resposta) return null;
    return (resposta as Promise<Response>).then(
      (r) => (r.type === "error" ? "ERRO" : r.text()), // Response.error() é o que o service worker devolve sem rede nem cache
      () => "ERRO",
    );
  }
  return { pedir, rede, guardados, apagadas, ouvintes };
}

describe("service worker", () => {
  it("nunca toca na API (exceto os textos), no /health, no painel, nas imagens e nos vídeos", async () => {
    const { pedir } = carregar();
    for (const u of [
      "/api/sessoes/x/trabalho",
      "/api/sessoes",
      "/health",
      "/admin",
      "/api/admin/dados",
      "/ajuda/1.png",
      "/videos/t.mp4",
      "/sw.js",
    ])
      expect(await pedir(u), u).toBeNull();
    expect(await pedir("/api/sessoes", { method: "POST" })).toBeNull();
    expect(await pedir("/x", { url: "https://outro.site/x" })).toBeNull(); // outra origem
  });

  it("páginas: rede primeiro; sem rede, a casca guardada da página inicial", async () => {
    const { pedir, rede } = carregar();
    expect(await pedir("/", { mode: "navigate" })).toBe("da rede"); // guarda a casca
    rede.mockRejectedValue(new Error("offline"));
    expect(await pedir("/", { mode: "navigate" })).toBe("da rede"); // veio da cache
    expect(await pedir("/tutorial", { mode: "navigate" })).toBe("da rede"); // outra página: a casca
  });

  it("sem rede e sem nada guardado dá erro (o browser mostra a sua página de erro)", async () => {
    const { pedir, rede } = carregar();
    rede.mockRejectedValue(new Error("offline"));
    expect(await pedir("/", { mode: "navigate" })).toBe("ERRO");
  });

  it("os textos da interface: rede primeiro, cache sem rede", async () => {
    const { pedir, rede } = carregar();
    expect(await pedir("/api/textos/pt")).toBe("da rede");
    rede.mockRejectedValue(new Error("offline"));
    expect(await pedir("/api/textos/pt")).toBe("da rede");
    expect(await pedir("/api/linguas")).toBe("ERRO"); // nunca visto: nada a devolver
  });

  it("os ficheiros com hash: cache primeiro (a rede só no 1.º pedido)", async () => {
    const { pedir, rede } = carregar();
    await pedir("/assets/index-ab12.js");
    await pedir("/assets/index-ab12.js");
    await pedir("/icone.svg");
    expect(rede).toHaveBeenCalledTimes(2); // o js (1x) e o ícone (1x)
  });

  it("ao ativar apaga só as caches antigas da app", async () => {
    const { ouvintes, apagadas } = carregar("2.0.0", ["rifas-casca-1.0.0", "outra-app", "rifas-casca-0.9.0"]);
    let espera: Promise<unknown> = Promise.resolve();
    ouvintes.activate?.({
      request: { method: "GET", url: "" },
      waitUntil: (p) => {
        espera = p;
      },
    });
    await espera;
    expect(apagadas.sort()).toEqual(["rifas-casca-0.9.0", "rifas-casca-1.0.0"]);
  });
});
