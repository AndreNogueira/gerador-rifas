// Service worker do Gerador de Rifas: guarda só a «casca» da app (HTML, JS, CSS, ícones e os textos da interface) para a app
// instalada abrir mesmo sem rede. A geração precisa SEMPRE do servidor e nunca passa por aqui: /api (exceto os textos), /health,
// /admin, /ajuda e /videos vão direitos à rede. O nome da cache leva a versão da app (`/sw.js?v=3.14.0`): cada versão nova
// instala uma cache nova e apaga as antigas. Ficheiro simples e legível de propósito (não passa pelo ofuscador).
const VERSAO = new URL(self.location.href).searchParams.get("v") || "0";
const CACHE = `rifas-casca-${VERSAO}`;
const NUNCA = ["/api", "/health", "/admin", "/ajuda", "/videos", "/sw.js"]; // o caminho ou o que está debaixo dele
const TEXTOS = /^\/api\/(linguas|textos\/\w+)$/;

self.addEventListener("install", (evento) => {
  evento.waitUntil(
    caches
      .open(CACHE)
      .then((c) => c.addAll(["/", "/icone.svg"]))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches
      .keys()
      .then((nomes) => Promise.all(nomes.filter((n) => n.startsWith("rifas-casca-") && n !== CACHE).map((n) => caches.delete(n))))
      .then(() => self.clients.claim()),
  );
});

function guardar(pedido, resposta) {
  if (resposta && resposta.ok) {
    const copia = resposta.clone();
    caches.open(CACHE).then((c) => c.put(pedido, copia));
  }
  return resposta;
}

self.addEventListener("fetch", (evento) => {
  const pedido = evento.request;
  if (pedido.method !== "GET") return;
  const url = new URL(pedido.url);
  if (url.origin !== self.location.origin) return;
  const caminho = url.pathname;
  const eTextos = TEXTOS.test(caminho);
  if (!eTextos && NUNCA.some((p) => caminho === p || caminho.startsWith(`${p}/`))) return;

  if (pedido.mode === "navigate") {
    // páginas: rede primeiro (o servidor monta o HTML por rota); sem rede, a casca da página inicial
    evento.respondWith(
      fetch(pedido)
        .then((r) => (caminho === "/" ? guardar("/", r) : r))
        .catch(() => caches.match("/").then((m) => m || Response.error())),
    );
  } else if (eTextos) {
    // os textos da interface: rede primeiro (podem mudar com a versão), cache se não houver rede
    evento.respondWith(
      fetch(pedido)
        .then((r) => guardar(pedido, r))
        .catch(() => caches.match(pedido).then((m) => m || Response.error())),
    );
  } else if (caminho.startsWith("/assets/") || caminho.startsWith("/icone") || caminho === "/manifest.webmanifest") {
    // ficheiros com hash no nome (ou ícones): cache primeiro
    evento.respondWith(caches.match(pedido).then((m) => m || fetch(pedido).then((r) => guardar(pedido, r))));
  }
});
