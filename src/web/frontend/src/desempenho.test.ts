import { describe, expect, it } from "vitest";
import { Coletor } from "./desempenho";

describe("o coletor de desempenho (LCP, CLS, INP)", () => {
  it("sem nada desenhado não há o que enviar", () => {
    expect(new Coletor().resumo()).toBeNull();
  });

  it("o LCP é o último (maior) valor e vai em ms inteiros", () => {
    const c = new Coletor();
    c.lcp(800.4);
    c.lcp(2100.6);
    c.lcp(1500); // um valor menor depois não baixa o LCP
    expect(c.resumo()).toEqual({ lcp: 2101, cls: 0, inp: 0 });
  });

  it("o CLS é a pior janela de saltos (1 s de intervalo, 5 s no máximo) vezes 1000, e ignora os saltos após um clique", () => {
    const c = new Coletor();
    c.lcp(1000);
    c.saltoDeLayout(0.05, 1000, false);
    c.saltoDeLayout(0.04, 1500, false); // mesma janela: 0,09
    c.saltoDeLayout(0.3, 1800, true); // logo após um clique: não conta
    c.saltoDeLayout(0.02, 9000, false); // outra janela (mais de 1 s depois): 0,02
    expect(c.resumo()?.cls).toBe(90);
  });

  it("uma janela que passa dos 5 s recomeça", () => {
    const c = new Coletor();
    c.lcp(1000);
    for (let t = 0; t <= 6000; t += 800) c.saltoDeLayout(0.01, t, false); // saltos a cada 0,8 s durante 6 s
    const cls = c.resumo()?.cls ?? 0;
    expect(cls).toBeGreaterThan(0);
    expect(cls).toBeLessThan(80); // 8 saltos de 10 não chegam a somar a janela inteira de 6 s
  });

  it("o INP é a pior interação (cada clique conta a sua duração mais longa; id 0 não é interação)", () => {
    const c = new Coletor();
    c.lcp(1000);
    c.interacao(1, 80);
    c.interacao(1, 120); // o mesmo clique, com um evento mais longo
    c.interacao(2, 90);
    c.interacao(0, 5000); // sem interactionId: não é uma interação
    expect(c.resumo()?.inp).toBe(120);
  });

  it("com 50 interações ou mais o INP ignora a pior (o percentil 98)", () => {
    const c = new Coletor();
    c.lcp(1000);
    for (let i = 1; i <= 50; i++) c.interacao(i, i === 50 ? 900 : 100 + i);
    expect(c.resumo()?.inp).toBe(149); // a 2.ª pior: a de 900 ms é ignorada
  });

  it("os valores são cortados aos limites do servidor", () => {
    const c = new Coletor();
    c.lcp(999_999);
    c.saltoDeLayout(50, 0, false);
    c.interacao(1, 99_999);
    expect(c.resumo()).toEqual({ lcp: 60000, cls: 10000, inp: 10000 });
  });
});
