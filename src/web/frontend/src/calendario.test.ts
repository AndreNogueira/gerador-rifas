import { describe, expect, it } from "vitest";
import {
  celulasDoMes,
  dataNumerica,
  dataPorExtenso,
  limitar,
  msDeIso,
  nomesDosDias,
  primeiroDiaDaSemana,
  somarDias,
  somarMeses,
  tituloDoMes,
} from "./calendario";

describe("o calendário", () => {
  it("o mês tem sempre 6 semanas; a primeira célula depende do primeiro dia da semana", () => {
    // 1 de novembro de 2026 é domingo
    const segunda = celulasDoMes(2026, 10, 1);
    expect(segunda).toHaveLength(42);
    expect(segunda[0]).toMatchObject({ iso: "2026-10-26", doMes: false });
    expect(segunda[6]).toMatchObject({ iso: "2026-11-01", dia: 1, doMes: true });
    const domingo = celulasDoMes(2026, 10, 0);
    expect(domingo[0]).toMatchObject({ iso: "2026-11-01", doMes: true });
    expect(segunda.filter((c) => c.doMes)).toHaveLength(30);
  });

  it("somar dias e meses não sai do calendário real (31 de janeiro + 1 mês = fim de fevereiro)", () => {
    expect(somarDias("2026-12-31", 1)).toBe("2027-01-01");
    expect(somarDias("2026-03-01", -1)).toBe("2026-02-28");
    expect(somarMeses("2026-01-31", 1)).toBe("2026-02-28");
    expect(somarMeses("2024-01-31", 1)).toBe("2024-02-29");
    expect(somarMeses("2026-12-15", 1)).toBe("2027-01-15");
    expect(somarMeses("2026-01-15", -1)).toBe("2025-12-15");
  });

  it("recusa datas que não existem e limita os anos", () => {
    expect(msDeIso("2026-02-31")).toBeNaN();
    expect(msDeIso("lixo")).toBeNaN();
    expect(limitar("1900-05-05")).toBe("1970-01-01");
    expect(limitar("2200-05-05")).toBe("2100-12-31");
  });

  it("a ordem da data e o primeiro dia da semana seguem a língua", () => {
    expect(dataNumerica("pt", "2026-12-31")).toBe("31/12/2026");
    expect(dataNumerica("en", "2026-12-31")).toBe("12/31/2026");
    expect(dataNumerica("de", "2026-12-31")).toBe("31.12.2026");
    expect(dataNumerica("ja", "2026-12-31")).toBe("2026/12/31");
    expect(dataNumerica("pt", "")).toBe("");
    expect(primeiroDiaDaSemana("pt")).toBe(1); // segunda-feira
    expect(primeiroDiaDaSemana("en")).toBe(0); // domingo
  });

  it("os nomes dos meses e dos dias vêm da língua", () => {
    expect(tituloDoMes("pt", "2026-12-31")).toMatch(/dezembro de 2026/i);
    expect(tituloDoMes("es", "2026-12-31")).toMatch(/diciembre/i);
    expect(tituloDoMes("de", "2026-12-31")).toMatch(/Dezember 2026/);
    expect(nomesDosDias("pt", 1)[0]).toMatch(/^seg/i);
    expect(nomesDosDias("en", 0)[0]).toMatch(/^sun/i);
    expect(nomesDosDias("fr", 1)[0]).toMatch(/^lun/i);
    expect(dataPorExtenso("pt", "2026-12-31")).toMatch(/quinta-feira, 31 de dezembro de 2026/i);
  });
});
