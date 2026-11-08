import "fake-indexeddb/auto";
import { beforeEach, describe, expect, it } from "vitest";
import { esquecerAlgarismos, guardarAlgarismos, lerAlgarismos } from "./memoria";

beforeEach(async () => {
  await esquecerAlgarismos();
});

describe("memória dos algarismos", () => {
  it("guarda, devolve igual e esquece", async () => {
    expect(await lerAlgarismos()).toBeNull();
    const original = new File([new Uint8Array([1, 2, 3, 250])], "meus algarismos.pdf", {
      type: "application/pdf",
    });
    expect(await guardarAlgarismos(original)).toBe(true);
    const lido = await lerAlgarismos();
    expect(lido?.name).toBe("meus algarismos.pdf");
    expect(lido?.type).toBe("application/pdf");
    expect(Array.from(new Uint8Array(await (lido as File).arrayBuffer()))).toEqual([1, 2, 3, 250]);
    await esquecerAlgarismos();
    expect(await lerAlgarismos()).toBeNull();
  });

  it("um segundo ficheiro troca o primeiro e os grandes demais não se guardam", async () => {
    await guardarAlgarismos(new File(["a"], "a.png", { type: "image/png" }));
    await guardarAlgarismos(new File(["b"], "b.png", { type: "image/png" }));
    expect((await lerAlgarismos())?.name).toBe("b.png");
    const grande = new File([new Uint8Array(10 * 1024 * 1024 + 1)], "grande.png", { type: "image/png" });
    expect(await guardarAlgarismos(grande)).toBe(false);
    expect((await lerAlgarismos())?.name).toBe("b.png"); // o anterior fica
  });
});
