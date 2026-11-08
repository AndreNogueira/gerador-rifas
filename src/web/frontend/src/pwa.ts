/**
 * Regista o service worker (`public/sw.js`) para a app poder ser instalada e abrir sem rede. Só em produção, nunca no painel, e
 * em silêncio se o browser não suportar. O `?v=` leva a versão: cada versão nova da app instala uma cache nova.
 */
export function registarServiceWorker(
  versao: string,
  producao: boolean = import.meta.env.PROD,
  caminho: string = window.location.pathname,
): Promise<ServiceWorkerRegistration | undefined> {
  if (!producao || !versao || caminho === "/admin" || !("serviceWorker" in navigator))
    return Promise.resolve(undefined);
  return navigator.serviceWorker
    .register(`/sw.js?v=${encodeURIComponent(versao)}`, { scope: "/" })
    .catch(() => undefined);
}
