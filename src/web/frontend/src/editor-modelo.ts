// O desenho do editor de templates (`src/core/editor.py`): tipos, o modelo inicial, as verificações que o servidor também faz e o que se envia.
// Coordenadas em pt, origem em cima à esquerda; um texto (e o número) ancora-se na linha de base.

export type Tipo = "texto" | "retangulo" | "linha" | "numero";
export type Alinhamento = "e" | "c" | "d";

export interface Elemento {
  id: string;
  tipo: Tipo;
  x: number;
  y: number;
  w: number;
  h: number;
  cor: string;
  contorno: string;
  espessura: number;
  raio: number;
  tracejado: boolean;
  texto: string;
  tamanho: number;
  negrito: boolean;
  alinhamento: Alinhamento;
  rot: 0 | 90;
}

export interface Desenho {
  largura: number;
  altura: number;
  fundo: string;
  elementos: Elemento[];
}

export const LIMITES = {
  larguraMin: 120,
  larguraMax: 800,
  alturaMin: 50,
  alturaMax: 500,
  texto: 80,
  elementos: 40,
  tamanhoMin: 4,
  tamanhoMax: 120,
} as const;

/** O que o motor confundiria com o número do bilhete: um 0 seguido de, pelo menos, 2 algarismos (como `PADRAO_EXEMPLO` do motor). */
export const PADRAO_NUMERO = /(?<!\d)0\d{2,}(?!\d)/;

/** A linha de base fica a 0,8 × tamanho abaixo do topo da caixa do texto (`core.editor.ASCENTE`). */
export const ASCENTE = 0.8;

let sequencia = 0;
export const novoId = () => `e${++sequencia}`;

const BASE: Omit<Elemento, "id" | "tipo"> = {
  x: 0,
  y: 0,
  w: 0,
  h: 0,
  cor: "#000000",
  contorno: "",
  espessura: 1,
  raio: 0,
  tracejado: false,
  texto: "",
  tamanho: 12,
  negrito: false,
  alinhamento: "e",
  rot: 0,
};

export function elemento(tipo: Tipo, extra: Partial<Elemento> = {}): Elemento {
  return { ...BASE, id: novoId(), tipo, ...extra };
}

/** Um elemento novo, no meio do desenho e com valores que se veem logo. */
export function novo(tipo: Tipo, d: Pick<Desenho, "largura" | "altura">): Elemento {
  const cx = Math.round(d.largura / 2);
  const cy = Math.round(d.altura / 2);
  switch (tipo) {
    case "texto":
      return elemento("texto", { x: cx - 40, y: cy, texto: "Texto", tamanho: 16 });
    case "retangulo":
      return elemento("retangulo", {
        x: cx - 40,
        y: cy - 20,
        w: 80,
        h: 40,
        cor: "#dbeafe",
        contorno: "#1e3a8a",
        espessura: 1.5,
      });
    case "linha":
      return elemento("linha", { x: cx - 50, y: cy, w: 100, h: 0, contorno: "#555555", espessura: 1.5 });
    case "numero":
      return elemento("numero", { x: cx - 30, y: cy, tamanho: 20, cor: "#c2410c" });
  }
}

/** Uma rifa com talão, para começar: moldura, talão com o número rodado, título, prémios, data e o número na parte principal. */
export function modeloComTalao(): Desenho {
  return {
    largura: 535,
    altura: 152,
    fundo: "#ffffff",
    elementos: [
      elemento("retangulo", {
        x: 2,
        y: 2,
        w: 531,
        h: 148,
        cor: "#fffdf5",
        contorno: "#0f6e73",
        espessura: 2,
        raio: 10,
      }),
      elemento("retangulo", { x: 3, y: 3, w: 60, h: 146, cor: "#e6f4f1", raio: 9 }),
      elemento("linha", { x: 64, y: 8, w: 0, h: 136, contorno: "#0f6e73", espessura: 1, tracejado: true }),
      elemento("texto", {
        x: 84,
        y: 40,
        texto: "TÍTULO DA RIFA",
        tamanho: 21,
        cor: "#0f6e73",
        negrito: true,
      }),
      elemento("texto", { x: 84, y: 56, texto: "Associação · Local do evento", tamanho: 9, cor: "#555555" }),
      elemento("texto", { x: 84, y: 84, texto: "1.º Prémio: …", tamanho: 10, cor: "#222222" }),
      elemento("texto", { x: 84, y: 98, texto: "2.º Prémio: …", tamanho: 10, cor: "#222222" }),
      elemento("texto", {
        x: 84,
        y: 138,
        texto: "Sorteio: dd/mm/aaaa",
        tamanho: 10,
        cor: "#0f6e73",
        negrito: true,
      }),
      elemento("texto", { x: 392, y: 54, texto: "Nº", tamanho: 11, cor: "#555555" }),
      elemento("numero", { x: 412, y: 56, tamanho: 20, cor: "#c2410c" }),
      elemento("numero", { x: 42, y: 112, tamanho: 19, cor: "#c2410c", rot: 90 }),
    ],
  };
}

export interface Problemas {
  /** O número 0001 tem de aparecer uma ou duas vezes. */
  numero: boolean;
  /** O primeiro texto com algo que o motor confundiria com o número ("" se nenhum). */
  digitos: string;
  elementos: boolean;
}

export function problemas(d: Desenho): Problemas {
  const n = d.elementos.filter((e) => e.tipo === "numero").length;
  const mau = d.elementos.find((e) => e.tipo === "texto" && PADRAO_NUMERO.test(e.texto));
  return {
    numero: n < 1 || n > 2,
    digitos: mau?.texto ?? "",
    elementos: d.elementos.length > LIMITES.elementos,
  };
}

export const semProblemas = (p: Problemas) => !p.numero && !p.digitos && !p.elementos;

/** O que se envia ao servidor: sem os ids do ecrã e sem contorno quando a espessura é 0. */
export function paraEnviar(d: Desenho) {
  return {
    largura: d.largura,
    altura: d.altura,
    fundo: d.fundo,
    elementos: d.elementos.map(({ id: _id, ...e }) => ({
      ...e,
      contorno: e.tipo === "retangulo" && e.espessura <= 0 ? "" : e.contorno,
    })),
  };
}

export const limitar = (v: number, min: number, max: number) =>
  Math.min(max, Math.max(min, Number.isFinite(v) ? v : min));

const COR = /^#[0-9a-fA-F]{6}$/;

/** Lê um desenho guardado no browser; qualquer coisa que não presta dá `null` (e o editor arranca com o modelo). */
export function lerGuardado(bruto: string | null): Desenho | null {
  if (!bruto) return null;
  try {
    const o = JSON.parse(bruto) as Partial<Desenho>;
    if (!o || typeof o !== "object" || !Array.isArray(o.elementos) || o.elementos.length > LIMITES.elementos)
      return null;
    if (typeof o.fundo !== "string" || !COR.test(o.fundo)) return null;
    const elementos: Elemento[] = [];
    for (const e of o.elementos as Partial<Elemento>[]) {
      if (!e || !["texto", "retangulo", "linha", "numero"].includes(e.tipo as string)) return null;
      const el = { ...BASE, ...e, id: novoId() } as Elemento;
      if (![el.x, el.y, el.w, el.h, el.espessura, el.raio, el.tamanho].every(Number.isFinite)) return null;
      if (!COR.test(el.cor) || (el.contorno && !COR.test(el.contorno))) return null;
      if (typeof el.texto !== "string" || el.texto.length > LIMITES.texto) return null;
      elementos.push(el);
    }
    return {
      largura: limitar(Number(o.largura), LIMITES.larguraMin, LIMITES.larguraMax),
      altura: limitar(Number(o.altura), LIMITES.alturaMin, LIMITES.alturaMax),
      fundo: o.fundo,
      elementos,
    };
  } catch {
    return null;
  }
}
