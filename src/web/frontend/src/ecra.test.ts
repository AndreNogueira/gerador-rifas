import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { campanhaDaVisita, origemDaVisita, registarEcra } from "./ecra";

describe("a origem da visita (só o nome do servidor, nunca o endereço)", () => {
  it("tira só o nome do servidor do endereço de origem", () => {
    expect(origemDaVisita("https://www.google.com/search?q=rifas+secretas&hl=pt")).toBe("www.google.com");
    expect(origemDaVisita("https://l.facebook.com/l.php?u=https%3A%2F%2Fx")).toBe("l.facebook.com");
    expect(origemDaVisita("http://escola.pt:8080/pagina#x")).toBe("escola.pt");
  });

  it("sem origem ou com um endereço inválido devolve vazio", () => {
    expect(origemDaVisita("")).toBe("");
    expect(origemDaVisita("isto não é um endereço")).toBe("");
  });

  it("o utm_source é a campanha; sem ele, vazio", () => {
    expect(campanhaDaVisita("?utm_source=escola-sol&utm_medium=cartaz")).toBe("escola-sol");
    expect(campanhaDaVisita("?q=1")).toBe("");
    expect(campanhaDaVisita("")).toBe("");
    expect(campanhaDaVisita(`?utm_source=${"a".repeat(80)}`)).toHaveLength(40);
  });
});

describe("registarEcra envia a origem e a campanha, uma vez por separador", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.stubGlobal("screen", { width: 1920, height: 1080 });
    Object.defineProperty(document, "referrer", {
      value: "https://www.bing.com/search?q=segredo",
      configurable: true,
    });
    window.history.replaceState({}, "", "/?utm_source=Escola");
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    window.history.replaceState({}, "", "/");
  });

  it("o corpo leva o servidor de origem e a campanha, sem caminho nem pesquisa", async () => {
    const pedido = vi.fn(() => Promise.resolve(new Response(null, { status: 204 })));
    vi.stubGlobal("fetch", pedido);
    await registarEcra();
    expect(pedido).toHaveBeenCalledTimes(1);
    const corpo = JSON.parse((pedido.mock.calls[0] as unknown as [string, RequestInit])[1].body as string);
    expect(corpo.origem).toBe("www.bing.com");
    expect(corpo.campanha).toBe("Escola");
    expect(JSON.stringify(corpo)).not.toContain("segredo");
    await registarEcra(); // o mesmo separador: não repete
    expect(pedido).toHaveBeenCalledTimes(1);
  });
});
