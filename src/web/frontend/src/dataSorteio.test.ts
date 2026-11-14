import { describe, expect, it } from "vitest";
import { FORMATOS_DATA, formatarData, linguaDaData, MAX_DATA, textoDaData } from "./dataSorteio";

describe("data do sorteio", () => {
  it("a mesma data escreve-se de quatro maneiras, na língua do site", () => {
    const iso = "2026-12-31";
    expect(FORMATOS_DATA.map((f) => formatarData(iso, f, "pt"))).toEqual([
      "31/12/2026",
      "31 de dez. de 2026",
      "31 de dezembro de 2026",
      "quinta-feira, 31 de dezembro de 2026",
    ]);
    expect(formatarData(iso, "longo", "en")).toBe("December 31, 2026");
    expect(formatarData(iso, "longo", "de")).toBe("31. Dezember 2026");
    expect(formatarData(iso, "completo", "es")).toContain("31 de diciembre de 2026");
  });

  it("não muda de dia com o fuso horário e rejeita datas que não existem", () => {
    expect(formatarData("2026-01-01", "curto", "pt")).toBe("01/01/2026");
    expect(formatarData("2026-02-30", "curto", "pt")).not.toBe("30/02/2026");
    expect(formatarData("", "curto", "pt")).toBe("");
    expect(formatarData("31/12/2026", "curto", "pt")).toBe("");
  });

  it("usa sempre algarismos latinos e, em hindi (sem letra na rifa), os nomes em inglês", () => {
    expect(linguaDaData("hi")).toBe("en-GB");
    expect(linguaDaData("pt")).toBe("pt");
    expect(formatarData("2026-12-31", "longo", "hi")).toBe("31 December 2026");
    expect(formatarData("2026-12-31", "curto", "hi")).toBe("31/12/2026");
    expect(formatarData("2026-12-31", "longo", "ja")).toBe("2026年12月31日");
  });

  it("junta o texto antes da data; sem data não escreve nada; o modo livre usa o texto escrito", () => {
    const base = { iso: "2026-12-31", formato: "curto" as const, antes: "", livre: "", lingua: "pt" };
    expect(textoDaData(base)).toBe("31/12/2026");
    expect(textoDaData({ ...base, antes: "Sorteio:" })).toBe("Sorteio: 31/12/2026");
    expect(textoDaData({ ...base, iso: "", antes: "Sorteio:" })).toBe("");
    expect(textoDaData({ ...base, formato: "livre", livre: "  No dia da festa  " })).toBe("No dia da festa");
    expect(textoDaData({ ...base, formato: "livre", livre: "x".repeat(200) })).toHaveLength(MAX_DATA);
  });
});
