import { type AnchorHTMLAttributes, type MouseEvent, useSyncExternalStore } from "react";

// Um router mínimo (4 páginas): usa o History API. O FastAPI devolve o index.html para qualquer caminho que não seja da API.
const EVENTO = "rifas:navegar";

function subscrever(aviso: () => void): () => void {
  window.addEventListener("popstate", aviso);
  window.addEventListener(EVENTO, aviso);
  return () => {
    window.removeEventListener("popstate", aviso);
    window.removeEventListener(EVENTO, aviso);
  };
}
const lerLocalizacao = () => window.location.pathname + window.location.search;

/** O caminho atual, p.ex. «/tutorial?p=3». */
export function useLocalizacao(): string {
  return useSyncExternalStore(subscrever, lerLocalizacao, () => "/");
}

export function navegar(para: string, substituir = false): void {
  if (para === lerLocalizacao()) return;
  if (substituir) window.history.replaceState(null, "", para);
  else window.history.pushState(null, "", para);
  window.dispatchEvent(new Event(EVENTO));
}

export function Ligacao({
  para,
  onClick,
  ...resto
}: { para: string } & AnchorHTMLAttributes<HTMLAnchorElement>) {
  return (
    <a
      href={para}
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
