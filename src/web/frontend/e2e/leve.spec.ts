import { expect, test } from "@playwright/test";

// O site fica leve para quem só gera rifas: o painel do dono, o editor e o sorteio são ficheiros à parte (`src/preguicoso.ts`) que só se pedem quando se abre a página.
const PARTES = /\/assets\/(Admin|Editor|Sorteio)-[^/]+\.js/;

function partesPedidas(page: import("@playwright/test").Page): string[] {
  const nomes: string[] = [];
  page.on("request", (r) => {
    const m = PARTES.exec(new URL(r.url()).pathname);
    if (m) nomes.push(m[1] as string);
  });
  return nomes;
}

test("a página inicial não descarrega o painel, o editor nem o sorteio", async ({ page }) => {
  const pedidas = partesPedidas(page);
  await page.goto("/");
  await expect(page.getByTestId("gerador").or(page.locator("main"))).toBeVisible();
  await page.waitForLoadState("networkidle");
  expect(pedidas).toEqual([]);
});

test("o sorteio descarrega só o seu ficheiro e funciona", async ({ page }) => {
  const pedidas = partesPedidas(page);
  await page.goto("/sorteio");
  await expect(page.getByTestId("sorteio-n")).toBeVisible(); // só existe na página desenhada (o <h1> do HTML estático de SEO aparece antes de o React montar)
  await page.waitForLoadState("networkidle");
  expect(pedidas).toEqual(["Sorteio"]);
});

test("o editor descarrega só o seu ficheiro e funciona", async ({ page }) => {
  const pedidas = partesPedidas(page);
  await page.goto("/editor");
  await expect(page.getByTestId("editor-modelo")).toBeVisible(); // só existe na página desenhada
  await page.waitForLoadState("networkidle");
  expect(pedidas).toEqual(["Editor"]);
});

test("ir da página inicial ao sorteio, dentro da app, carrega-o nessa altura", async ({ page }) => {
  const pedidas = partesPedidas(page);
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  expect(pedidas).toEqual([]);
  // navegação dentro da app (sem recarregar a página): o endereço muda e o router mostra o sorteio
  await page.evaluate(() => {
    window.history.pushState({}, "", "/sorteio");
    window.dispatchEvent(new PopStateEvent("popstate"));
  });
  await expect(page).toHaveURL(/\/sorteio$/);
  await expect(page.getByTestId("sorteio-n")).toBeVisible();
  await page.waitForLoadState("networkidle");
  expect(pedidas).toEqual(["Sorteio"]);
});

test("um separador com o site antigo aberto recarrega-se sozinho quando o ficheiro da página já não existe", async ({
  page,
}) => {
  // o 1.º pedido da parte falha (como depois de um deploy, em que o nome antigo deixou de existir); depois da recarga corre bem. (Não se conta o 2.º pedido: o service worker, que já
  // está ativo na recarga, faz-o por fora do `page.route`; conta-se antes que a página carregou duas vezes e que acabou desenhada.)
  let falhou = false;
  await page.route(PARTES, (rota) => {
    if (falhou) return rota.continue();
    falhou = true;
    return rota.fulfill({ status: 404, body: "não existe" });
  });
  let cargas = 0;
  page.on("load", () => {
    cargas += 1;
  });
  await page.goto("/sorteio");
  await expect(page.getByTestId("sorteio-n")).toBeVisible({ timeout: 15000 });
  expect(falhou).toBe(true);
  expect(cargas).toBeGreaterThanOrEqual(2); // carregou, falhou a parte, recarregou UMA vez e desenhou
  await page.waitForLoadState("networkidle");
  expect(cargas).toBe(2); // e não entrou em ciclo
});
