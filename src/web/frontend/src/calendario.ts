/**
 * A matemática do calendário da data do sorteio (`SeletorData.tsx`), sem estado nem DOM: os dias de um mês, o primeiro dia da semana e os nomes
 * (meses, dias) vêm do `Intl` na língua do site, por isso nada disto tem textos traduzidos à mão. As datas são `aaaa-mm-dd` (o que o resto do
 * código usa) e contam-se em UTC para o fuso nunca mudar o dia.
 */

export interface Celula {
  iso: string;
  dia: number;
  doMes: boolean;
}

const DIA_MS = 86_400_000;
/** O que o calendário aguenta navegar (o pedido à rifa só leva texto, mas anos absurdos só confundem). */
export const ANO_MINIMO = 1970;
export const ANO_MAXIMO = 2100;

/** A língua do calendário: o português do site é o de Portugal (a semana começa à segunda-feira), as outras seguem o código. */
export function localeDoCalendario(lingua: string): string {
  return lingua === "pt" ? "pt-PT" : lingua;
}

/** `aaaa-mm-dd` de um instante UTC. */
export function isoDe(ms: number): string {
  return new Date(ms).toISOString().slice(0, 10);
}

/** Os milissegundos UTC de uma data `aaaa-mm-dd` (NaN se não é válida). */
export function msDeIso(iso: string): number {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return Number.NaN;
  const [a, me, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const ms = Date.UTC(a, me - 1, d);
  return isoDe(ms) === iso ? ms : Number.NaN; // recusa 31 de fevereiro
}

export function somarDias(iso: string, dias: number): string {
  const ms = msDeIso(iso);
  return Number.isNaN(ms) ? iso : limitar(isoDe(ms + dias * DIA_MS));
}

/** Soma meses mantendo o dia, ou o último dia do mês se ele não existir (31 de janeiro + 1 mês = 28/29 de fevereiro). */
export function somarMeses(iso: string, meses: number): string {
  const ms = msDeIso(iso);
  if (Number.isNaN(ms)) return iso;
  const d = new Date(ms);
  const ano = d.getUTCFullYear();
  const mes = d.getUTCMonth() + meses; // o Date.UTC arruma os meses fora de 0–11
  const ultimo = new Date(Date.UTC(ano, mes + 1, 0)).getUTCDate();
  return limitar(isoDe(Date.UTC(ano, mes, Math.min(d.getUTCDate(), ultimo))));
}

/** Mantém a data dentro dos anos que o calendário mostra. */
export function limitar(iso: string): string {
  const ms = msDeIso(iso);
  if (Number.isNaN(ms)) return iso;
  const minimo = Date.UTC(ANO_MINIMO, 0, 1);
  const maximo = Date.UTC(ANO_MAXIMO, 11, 31);
  return isoDe(Math.min(maximo, Math.max(minimo, ms)));
}

/**
 * O primeiro dia da semana na língua (0 = domingo … 6 = sábado), do `Intl.Locale` do browser; sem ele, o costume de cada língua
 * (domingo em inglês, japonês, coreano e hindi; segunda-feira nas outras). O português é sempre à segunda-feira.
 */
export function primeiroDiaDaSemana(lingua: string): number {
  if (lingua === "pt") return 1; // o CLDR põe Portugal a começar ao domingo, mas os calendários e as agendas portuguesas começam à segunda-feira
  const locale = localeDoCalendario(lingua);
  try {
    const l = new Intl.Locale(locale) as Intl.Locale & {
      getWeekInfo?: () => { firstDay: number };
      weekInfo?: { firstDay: number };
    };
    const info = l.getWeekInfo?.() ?? l.weekInfo;
    if (info && typeof info.firstDay === "number") return info.firstDay % 7; // 1 = segunda … 7 = domingo
  } catch {
    /* língua que o browser não conhece: segue o costume */
  }
  return ["en", "ja", "ko", "hi"].includes(lingua) ? 0 : 1;
}

/** As 42 células (6 semanas) do mês `mes` (0–11) de `ano`, com os dias dos meses vizinhos a preencher. */
export function celulasDoMes(ano: number, mes: number, primeiroDia: number): Celula[] {
  const primeiro = Date.UTC(ano, mes, 1);
  const recuo = (new Date(primeiro).getUTCDay() - primeiroDia + 7) % 7;
  return Array.from({ length: 42 }, (_, i) => {
    const ms = primeiro + (i - recuo) * DIA_MS;
    const d = new Date(ms);
    return { iso: isoDe(ms), dia: d.getUTCDate(), doMes: d.getUTCMonth() === mes };
  });
}

/** Os nomes curtos dos dias da semana, a começar em `primeiroDia`, na língua. */
export function nomesDosDias(lingua: string, primeiroDia: number): string[] {
  const f = formatador(lingua, { weekday: "short" });
  const domingo = Date.UTC(2021, 0, 3); // um domingo qualquer
  // «short» já é curto na maioria das línguas («Mo.», «lun.», «月»); onde sai por extenso («segunda») ficam as 3 primeiras letras
  return Array.from({ length: 7 }, (_, i) => {
    const nome = f.format(new Date(domingo + ((primeiroDia + i) % 7) * DIA_MS)).replace(/\.$/, "");
    return nome.length > 3 ? nome.slice(0, 3) : nome;
  });
}

function formatador(lingua: string, opcoes: Intl.DateTimeFormatOptions): Intl.DateTimeFormat {
  const base = { ...opcoes, timeZone: "UTC" };
  try {
    return new Intl.DateTimeFormat(`${localeDoCalendario(lingua)}-u-nu-latn`, base);
  } catch {
    return new Intl.DateTimeFormat("en-GB", base);
  }
}

/** «novembro de 2026», na língua. */
export function tituloDoMes(lingua: string, iso: string): string {
  const ms = msDeIso(iso);
  return Number.isNaN(ms) ? "" : formatador(lingua, { month: "long", year: "numeric" }).format(new Date(ms));
}

/** A data como esta língua a escreve em números (dd/mm/aaaa em português, mm/dd/yyyy em inglês dos EUA, aaaa/mm/dd em japonês…). */
export function dataNumerica(lingua: string, iso: string): string {
  const ms = msDeIso(iso);
  return Number.isNaN(ms)
    ? ""
    : formatador(lingua, { day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(ms));
}

/** «domingo, 15 de novembro de 2026»: o nome completo de um dia, para os leitores de ecrã. */
export function dataPorExtenso(lingua: string, iso: string): string {
  const ms = msDeIso(iso);
  return Number.isNaN(ms)
    ? ""
    : formatador(lingua, { weekday: "long", day: "numeric", month: "long", year: "numeric" }).format(
        new Date(ms),
      );
}
