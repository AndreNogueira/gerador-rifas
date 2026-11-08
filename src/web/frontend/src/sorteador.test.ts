import { createHash, randomBytes } from "node:crypto";
import { describe, expect, it } from "vitest";
import { type Intervalo, lerExcluir, MAX_NUMEROS, sha256, sortear } from "./sorteador";

const hex = (b: Uint8Array) => Buffer.from(b).toString("hex");

describe("sha256 em TypeScript", () => {
  it("dá os resultados conhecidos", () => {
    expect(hex(sha256(new Uint8Array()))).toBe(
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    );
    expect(hex(sha256(new TextEncoder().encode("abc")))).toBe(
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
    );
  });

  it("é igual ao do Node para entradas de 0 a 300 bytes (as fronteiras dos blocos de 64) e para texto com acentos", () => {
    for (let n = 0; n <= 300; n++) {
      const dados = new Uint8Array(randomBytes(n));
      expect(hex(sha256(dados))).toBe(createHash("sha256").update(dados).digest("hex"));
    }
    const texto = new TextEncoder().encode("açúcar ∑ 日本:0:0");
    expect(hex(sha256(texto))).toBe(createHash("sha256").update(texto).digest("hex"));
  });
});

// os mesmos vetores de tests/test_sorteio.py (a referência em Python)
const VETORES: [[number, number, number, string, Intervalo[]], number[]][] = [
  [
    [1, 100, 3, "semente-um", []],
    [29, 38, 74],
  ],
  [
    [1, 1000, 5, "drand:5000000:abcdef", []],
    [401, 161, 907, 932, 644],
  ],
  [
    [0, 9, 10, "todos", []],
    [5, 3, 9, 6, 1, 8, 2, 4, 0, 7],
  ],
  [
    [
      1,
      500,
      4,
      "Lotaria 2026-12-24 12 34 45",
      [
        [13, 13],
        [100, 110],
      ],
    ],
    [495, 382, 7, 329],
  ],
  [
    [100, 199, 2, "açúcar ∑ 日本", []],
    [109, 170],
  ],
  [[1, 7, 1, "x", [[1, 6]]], [7]],
];

describe("sortear", () => {
  it.each(VETORES)("dá o mesmo que a referência em Python: %j", (args, esperado) => {
    expect(sortear(...args)).toEqual(esperado);
  });

  it("a semente sem espaços nas pontas é a mesma; sem repetições; sortear todos é uma permutação", () => {
    expect(sortear(1, 1000, 5, "  abc \n")).toEqual(sortear(1, 1000, 5, "abc"));
    const r = sortear(1, 50, 20, "a", [[10, 20]]) as number[];
    expect(new Set(r).size).toBe(20);
    expect(r.every((n) => n >= 1 && n <= 50 && !(n >= 10 && n <= 20))).toBe(true);
    expect([...(sortear(5, 14, 10, "todos") as number[])].sort((a, b) => a - b)).toEqual([
      5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    ]);
    expect(sortear(1, 1000, 10, "s")?.slice(0, 3)).toEqual(sortear(1, 1000, 3, "s"));
  });

  it("recusa o que não serve", () => {
    for (const a of [
      [5, 1, 1, "s"],
      [1, 10, 0, "s"],
      [1, 10, 11, "s"],
      [1, 10, 1, ""],
      [1, 10, 1, "  "],
      [1, 10, 1, "x".repeat(201)],
      [1, MAX_NUMEROS + 1, 1, "s"],
      [1, 500, 101, "s"],
      [1.5, 10, 1, "s"],
    ] as [number, number, number, string][])
      expect(sortear(...a), JSON.stringify(a)).toBeNull();
    expect(sortear(1, 10, 1, "s", [[1, 10]])).toBeNull();
  });

  it("um milhão de números sorteia-se depressa", () => {
    const t0 = performance.now();
    expect(sortear(1, 1_000_000, 100, "grande")).toHaveLength(100);
    expect(performance.now() - t0).toBeLessThan(5000);
  });
});

describe("lerExcluir", () => {
  it("lê números e intervalos e recusa o resto", () => {
    expect(lerExcluir("")).toEqual([]);
    expect(lerExcluir("13, 100-110 , 666 ,7 - 9")).toEqual([
      [13, 13],
      [100, 110],
      [666, 666],
      [7, 9],
    ]);
    for (const mau of ["a", "5-3", "1-2-3", "-5", "1e3"]) expect(lerExcluir(mau), mau).toBeNull();
    expect(lerExcluir(Array.from({ length: 51 }, (_, i) => i).join(","))).toBeNull();
  });
});
