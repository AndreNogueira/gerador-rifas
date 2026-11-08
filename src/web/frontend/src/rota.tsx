import { type AnchorHTMLAttributes, type MouseEvent, useSyncExternalStore } from "react";

// Um router mínimo: usa o History API. O FastAPI devolve o index.html para qualquer caminho que não seja da API.
// A língua vive no URL (SEO por língua, `docs/SEO.md`): o português sem prefixo (`/tutorial`) e as outras 17 com ele (`/en/tutorial`). Para o resto da
// app o caminho é sempre o «de dentro» (`/tutorial`): `useLocalizacao()` tira o prefixo e `navegar`/`Ligacao` põem o da língua atual.
const EVENTO = "rifas:navegar";

/** As línguas com prefixo no URL, pela ordem de `core.i18n.LINGUAS` sem o português (um teste confere com o servidor: `seo.LINGUAS_URL`). */
export const LINGUAS_COM_PREFIXO = [
  "en",
  "es",
  "fr",
  "de",
  "it",
  "nl",
  "pl",
  "sv",
  "cs",
  "ro",
  "el",
  "ru",
  "tr",
  "zh",
  "ja",
  "ko",
  "hi",
];
const PREFIXO = new RegExp(`^/(${LINGUAS_COM_PREFIXO.join("|")})(?=/|$)`);
let linguaAtual: string | null = null;

/** A língua do prefixo do caminho (`/en/tutorial` → «en»), ou null se não tem (português). */
export function linguaDoCaminho(caminho: string = window.location.pathname): string | null {
  return PREFIXO.exec(caminho)?.[1] ?? null;
}

/** `/en/tutorial` → `/tutorial`; `/en` → `/`. */
export function semPrefixo(caminho: string): string {
  const resto = caminho.replace(PREFIXO, "");
  return resto === "" ? "/" : resto;
}

/** `/tutorial?p=2` → `/en/tutorial?p=2` (o português e o painel não levam prefixo). */
export function comPrefixo(para: string, lingua: string | null): string {
  const i = para.search(/[?#]/);
  const caminho = i < 0 ? para : para.slice(0, i);
  const cauda = i < 0 ? "" : para.slice(i);
  if (!lingua || lingua === "pt" || !LINGUAS_COM_PREFIXO.includes(lingua) || caminho.startsWith("/admin"))
    return para;
  return `/${lingua}${caminho === "/" ? "" : caminho}${cauda}`;
}

/** Diz ao router a língua da interface: o URL passa a ter o prefixo certo (sem criar entrada no histórico) e as ligações atualizam-se. */
export function definirLinguaDaRota(lingua: string): void {
  linguaAtual = lingua;
  const alvo =
    comPrefixo(semPrefixo(window.location.pathname), lingua) + window.location.search + window.location.hash;
  if (alvo !== window.location.pathname + window.location.search + window.location.hash)
    window.history.replaceState(null, "", alvo);
  window.dispatchEvent(new Event(EVENTO));
}

function subscrever(aviso: () => void): () => void {
  window.addEventListener("popstate", aviso);
  window.addEventListener(EVENTO, aviso);
  return () => {
    window.removeEventListener("popstate", aviso);
    window.removeEventListener(EVENTO, aviso);
  };
}
const lerLocalizacao = () => semPrefixo(window.location.pathname) + window.location.search;
const lerBruta = () => window.location.pathname + window.location.search;
const lerLingua = () => linguaAtual;

/** O caminho atual, p.ex. «/tutorial?p=3». */
export function useLocalizacao(): string {
  return useSyncExternalStore(subscrever, lerLocalizacao, () => "/");
}

export function navegar(para: string, substituir = false): void {
  const destino = comPrefixo(para, linguaAtual ?? linguaDoCaminho());
  if (destino === lerBruta()) return;
  if (substituir) window.history.replaceState(null, "", destino);
  else window.history.pushState(null, "", destino);
  window.dispatchEvent(new Event(EVENTO));
}

export function Ligacao({
  para,
  onClick,
  ...resto
}: { para: string } & AnchorHTMLAttributes<HTMLAnchorElement>) {
  const lingua = useSyncExternalStore(subscrever, lerLingua, () => null); // reescreve o href quando a língua muda
  return (
    <a
      href={comPrefixo(para, lingua ?? linguaDoCaminho())}
      {...resto}
      onClick={(e: MouseEvent<HTMLAnchorElement>) => {
        onClick?.(e);
        if (
          e.defaultPrevented ||
          e.button !== 0 ||
          e.metaKey ||
          e.ctrlKey ||
          e.shiftKey ||
          e.altKey ||
          resto.target === "_blank"
        )
          return;
        e.preventDefault();
        navegar(para);
        window.scrollTo(0, 0);
      }}
    />
  );
}
