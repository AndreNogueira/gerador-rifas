import { afterEach, describe, expect, it, vi } from "vitest";
import { registarServiceWorker } from "./pwa";

afterEach(() => vi.unstubAllGlobals());

function comServiceWorker(register = vi.fn().mockResolvedValue({ scope: "/" })) {
  vi.stubGlobal("navigator", { ...navigator, serviceWorker: { register } });
  return register;
}

describe("registo do service worker", () => {
  it("em produção regista /sw.js com a versão e o âmbito da raiz", async () => {
    const register = comServiceWorker();
    await registarServiceWorker("3.14.0", true, "/");
    expect(register).toHaveBeenCalledWith("/sw.js?v=3.14.0", { scope: "/" });
  });

  it("não regista em desenvolvimento, no painel, sem versão ou sem suporte", async () => {
    const register = comServiceWorker();
    await registarServiceWorker("3.14.0", false, "/");
    await registarServiceWorker("3.14.0", true, "/admin");
    await registarServiceWorker("", true, "/");
    expect(register).not.toHaveBeenCalled();
    vi.stubGlobal("navigator", {}); // um browser sem service worker
    await expect(registarServiceWorker("3.14.0", true, "/")).resolves.toBeUndefined();
  });

  it("um registo que falha não rebenta a app", async () => {
    comServiceWorker(vi.fn().mockRejectedValue(new Error("bloqueado")));
    await expect(registarServiceWorker("3.14.0", true, "/")).resolves.toBeUndefined();
  });
});
