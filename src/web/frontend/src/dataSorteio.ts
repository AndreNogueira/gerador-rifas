/** A data do sorteio na rifa: escolhe-se no calendário e depois como se apresenta (a mesma data, escrita de quatro maneiras na língua do site). */
export type FormatoData = "curto" | "medio" | "longo" | "completo" | "livre";

export const FORMATOS_DATA: readonly Exclude<FormatoData, "livre">[] = [
  "curto",
  "medio",
  "longo",
  "completo",
];

/** O que a rifa aguenta (`core/galeria.py`: `MAX_DATA`). */
export const MAX_DATA = 60;

const OPCOES: Record<Exclude<FormatoData, "livre">, Intl.DateTimeFormatOptions> = {
  curto: { day: "2-digit", month: "2-digit", year: "numeric" },
  medio: { day: "numeric", month: "short", year: "numeric" },
  longo: { day: "numeric", month: "long", year: "numeric" },
  completo: { weekday: "long", day: "numeric", month: "long", year: "numeric" },
};

/** A letra da rifa não tem hindi (docs/LETRAS.md): nesta língua os nomes dos meses e dos dias saem em inglês; os algarismos são sempre latinos. */
export function linguaDaData(lingua: string): string {
  return lingua === "hi" ? "en-GB" : lingua;
}

export function dataDeHoje(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** `aaaa-mm-dd` (o valor de um `<input type="date">`) escrita no formato pedido; "" se a data não é válida. */
export function formatarData(iso: string, formato: Exclude<FormatoData, "livre">, lingua: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return "";
  const d = new Date(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3])));
  if (Number.isNaN(d.getTime())) return "";
  try {
    return new Intl.DateTimeFormat(linguaDaData(lingua), {
      ...OPCOES[formato],
      numberingSystem: "latn",
      timeZone: "UTC",
    }).format(d);
  } catch {
    return new Intl.DateTimeFormat("en-GB", { ...OPCOES[formato], timeZone: "UTC" }).format(d);
  }
}

/** O texto que vai para a rifa: o texto antes da data (opcional, p.ex. «Sorteio:») e a data; no modo «livre», o que a pessoa escreveu. */
export function textoDaData(o: {
  iso: string;
  formato: FormatoData;
  antes: string;
  livre: string;
  lingua: string;
}): string {
  if (o.formato === "livre") return o.livre.trim().slice(0, MAX_DATA);
  const data = formatarData(o.iso, o.formato, o.lingua);
  if (!data) return "";
  return `${o.antes.trim()} ${data}`.trim().slice(0, MAX_DATA);
}
