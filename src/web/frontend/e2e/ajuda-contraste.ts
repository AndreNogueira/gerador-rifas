import type { Page } from "@playwright/test";

/**
 * Mede o contraste do texto contra o fundo REAL, pixel a pixel: o axe não consegue medir texto sobre gradientes, padrões ou imagens
 * (marca-o «incompleto»), e os nossos temas têm muitos. Aqui: 1) recolhe as caixas do texto visível (as dos próprios nós de texto, com a
 * cor, o tamanho e o peso); 2) torna todo o texto transparente e tira uma captura da página; 3) amostra os pixéis do fundo dentro de cada
 * caixa e calcula o contraste da cor do texto contra o pior de dois extremos do fundo (percentis 5 e 95 da luminância: ignora o ruído de
 * um pixel). Controlos desativados ficam de fora (o WCAG isenta-os). Limites AA: 4,5 para texto normal e 3 para texto grande (>= 24 px,
 * ou >= 18,66 px em negrito).
 */
export interface Falha {
  alvo: string;
  rácio: number;
  esperado: number;
  texto: string;
  tamanho: string;
}

interface Caixa {
  x: number;
  y: number;
  l: number;
  a: number;
}

interface Alvo {
  alvo: string;
  caixas: Caixa[];
  cor: [number, number, number, number];
  grande: boolean;
  tamanho: string;
}

export interface Medicao {
  falhas: Falha[];
  medidos: number;
}

export async function medirContraste(page: Page): Promise<Medicao> {
  // 1) as caixas do texto visível
  const alvos = await page.evaluate((): Alvo[] => {
    const saida: Alvo[] = [];
    const analisar = (c: string): [number, number, number, number] => {
      const srgb = /color\(srgb ([\d.]+) ([\d.]+) ([\d.]+)(?: \/ ([\d.]+))?\)/.exec(c); // o que o color-mix() devolve
      if (srgb)
        return [
          Number(srgb[1]) * 255,
          Number(srgb[2]) * 255,
          Number(srgb[3]) * 255,
          srgb[4] === undefined ? 1 : Number(srgb[4]),
        ];
      const m = /rgba?\(([^)]+)\)/.exec(c);
      const p = (m?.[1] ?? "0,0,0").split(/[ ,/]+/).map(Number);
      return [p[0] ?? 0, p[1] ?? 0, p[2] ?? 0, p[3] ?? 1];
    };
    const descricao = (el: Element) => {
      const id = el.getAttribute("data-testid");
      const cls =
        typeof el.className === "string" ? el.className.trim().split(/\s+/).slice(0, 2).join(".") : "";
      return `${el.tagName.toLowerCase()}${id ? `[${id}]` : ""}${cls ? `.${cls}` : ""}`;
    };
    const caixa = (r: DOMRect, encolher = 0): Caixa => ({
      x: Math.round(r.left + window.scrollX + encolher),
      y: Math.round(r.top + window.scrollY + encolher),
      l: Math.round(r.width - 2 * encolher),
      a: Math.round(r.height - 2 * encolher),
    });
    for (const el of Array.from(document.body.querySelectorAll("*"))) {
      const cs = getComputedStyle(el);
      if (cs.visibility === "hidden" || cs.display === "none" || Number(cs.opacity) === 0) continue;
      if (
        el.closest(
          "[aria-hidden='true'], .so-leitores, .seo-estatico, script, style, noscript, svg, template",
        )
      )
        continue;
      if (el.matches(":disabled") || el.closest("[disabled], fieldset:disabled, [aria-disabled='true']"))
        continue;
      const caixas: Caixa[] = [];
      let cor = cs.color;
      if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
        const tipo = (el as HTMLInputElement).type;
        if (["checkbox", "radio", "file", "range", "color", "hidden"].includes(tipo)) continue;
        if (el.value === "" && el.placeholder === "") continue;
        if (el.value === "") cor = getComputedStyle(el, "::placeholder").color;
        const r = el.getBoundingClientRect();
        if (r.width > 12 && r.height > 12) caixas.push(caixa(r, 5));
      } else if (el instanceof HTMLSelectElement) {
        const r = el.getBoundingClientRect();
        if (r.width > 12 && r.height > 12) caixas.push(caixa(r, 5));
      } else {
        for (const no of Array.from(el.childNodes)) {
          if (no.nodeType !== 3 || (no.textContent ?? "").trim() === "") continue;
          const intervalo = document.createRange();
          intervalo.selectNodeContents(no);
          for (const r of Array.from(intervalo.getClientRects()))
            if (r.width >= 2 && r.height >= 2) caixas.push(caixa(r));
        }
      }
      if (caixas.length === 0) continue;
      const px = Number.parseFloat(cs.fontSize);
      const negrito = Number.parseInt(cs.fontWeight, 10) >= 700;
      saida.push({
        alvo: descricao(el),
        caixas,
        cor: analisar(cor),
        grande: px >= 24 || (px >= 18.66 && negrito),
        tamanho: `${px}px${negrito ? " bold" : ""}`,
      });
    }
    return saida;
  });

  // 2) o texto transparente e uma captura da página inteira
  const estilo = await page.addStyleTag({
    content:
      "*, *::before, *::after { color: transparent !important; text-shadow: none !important; -webkit-text-fill-color: transparent !important; caret-color: transparent !important; } ::placeholder { color: transparent !important; -webkit-text-fill-color: transparent !important; }",
  });
  await page.evaluate(() => document.fonts.ready);
  const png = (await page.screenshot({ fullPage: true, animations: "disabled" })).toString("base64");
  await estilo.evaluate((e) => (e as HTMLElement).remove());

  // 3) os pixéis do fundo de cada caixa
  const falhas = await page.evaluate(
    async ([dados, alvosJson]) => {
      const lista = JSON.parse(alvosJson as string) as Alvo[];
      const img = new Image();
      img.src = `data:image/png;base64,${dados}`;
      await img.decode();
      const c = document.createElement("canvas");
      c.width = img.width;
      c.height = img.height;
      const ctx = c.getContext("2d", { willReadFrequently: true }) as CanvasRenderingContext2D;
      ctx.drawImage(img, 0, 0);
      const lum = (r: number, g: number, b: number) => {
        const f = (v: number) => (v / 255 <= 0.03928 ? v / 255 / 12.92 : ((v / 255 + 0.055) / 1.055) ** 2.4);
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
      };
      const saida: { alvo: string; rácio: number; esperado: number; texto: string; tamanho: string }[] = [];
      for (const a of lista) {
        let pior = Number.POSITIVE_INFINITY;
        for (const cx of a.caixas) {
          const x = Math.max(0, Math.min(cx.x, c.width - 1));
          const y = Math.max(0, Math.min(cx.y, c.height - 1));
          const l = Math.max(1, Math.min(cx.l, c.width - x));
          const h = Math.max(1, Math.min(cx.a, c.height - y));
          const px = ctx.getImageData(x, y, l, h).data;
          const passo = Math.max(1, Math.floor((l * h) / 400)); // ~400 amostras por caixa
          const amostras: [number, number, number][] = [];
          for (let i = 0; i < l * h; i += passo)
            amostras.push([px[i * 4] ?? 0, px[i * 4 + 1] ?? 0, px[i * 4 + 2] ?? 0]);
          amostras.sort((p, q) => lum(...p) - lum(...q));
          const escuro = amostras[Math.floor(amostras.length * 0.05)] as [number, number, number];
          const claro = amostras[Math.min(amostras.length - 1, Math.floor(amostras.length * 0.95))] as [
            number,
            number,
            number,
          ];
          const [tr, tg, tb, ta] = a.cor;
          for (const f of [escuro, claro]) {
            const R = Math.round(tr * ta + f[0] * (1 - ta));
            const G = Math.round(tg * ta + f[1] * (1 - ta));
            const B = Math.round(tb * ta + f[2] * (1 - ta));
            const l1 = lum(R, G, B);
            const l2 = lum(...f);
            pior = Math.min(pior, (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05));
          }
        }
        const esperado = a.grande ? 3 : 4.5;
        const [tr, tg, tb] = a.cor;
        if (pior < esperado)
          saida.push({
            alvo: a.alvo,
            rácio: Math.round(pior * 100) / 100,
            esperado,
            texto: `rgb(${tr},${tg},${tb})`,
            tamanho: a.tamanho,
          });
      }
      return saida;
    },
    [png, JSON.stringify(alvos)] as const,
  );
  return { falhas, medidos: alvos.length };
}
