import { expect, test } from "@playwright/test";

test.describe("páginas, sorteio e PWA", () => {
  test("o sorteio dá os números de referência e a ligação repete-o", async ({ page }) => {
    await page.goto("/sorteio");
    await page.getByTestId("sorteio-n").fill("3");
    await page.getByTestId("sorteio-semente").fill("semente-um");
    await page.getByTestId("sorteio-sortear").click();
    await expect(page.getByTestId("sorteio-resultado").locator("li")).toHaveText(["29", "38", "74"]); // os vetores de tests/test_sorteio.py
    const ligacao = page.url();
    expect(ligacao).toContain("s=semente-um");
    await page.goto(ligacao);
    await expect(page.getByTestId("sorteio-resultado").locator("li")).toHaveText(["29", "38", "74"]);
  });

  test("changelog, termos e privacidade abrem; o rodapé liga-os", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Changelog" }).click();
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Changelog");
    await expect(page.getByTestId(/^versao-/).first()).toBeVisible();
    await page.getByRole("link", { name: "Termos" }).click();
    await expect(page.getByTestId("pagina-termos")).toContainText("Versão provisória");
    await page.getByRole("link", { name: "Privacidade" }).click();
    await expect(page.getByTestId("pagina-privacidade")).toContainText("RGPD");
  });

  test("o changelog, os termos e a privacidade aparecem na língua escolhida (resumo traduzido e aviso do português)", async ({
    page,
  }) => {
    await page.goto("/changelog");
    await expect(page.getByTestId("changelog-resumo")).toHaveCount(0); // em português é o completo
    await page.getByTestId("lingua").selectOption("ja");
    await expect(page.getByTestId("changelog-resumo")).toContainText("ポルトガル語");
    await expect(page.getByTestId(/^versao-/).first()).toContainText("バージョン");
    await page.getByRole("link", { name: "利用規約" }).click();
    await expect(page.getByTestId("pagina-termos")).toContainText("ポルトガル語版が優先");
    await expect(page).toHaveTitle(/利用規約 \| /);
    await page.getByTestId("lingua").selectOption("en");
    await expect(page.getByTestId("pagina-termos")).toContainText("the Portuguese one prevails");
  });

  test("o tutorial tem um tópico com vídeo por funcionalidade e o vídeo carrega a sério", async ({
    page,
  }) => {
    await page.goto("/tutorial?p=11");
    await expect(page.getByTestId("topico")).toContainText("Galeria de templates");
    const video = page.getByTestId("video-topico");
    await expect(video).toBeVisible();
    await expect
      .poll(() => video.evaluate((v: HTMLVideoElement) => v.videoWidth), { timeout: 20_000 })
      .toBe(1280);
    expect(await video.evaluate((v: HTMLVideoElement) => v.duration)).toBeGreaterThan(8);
    await page.goto("/tutorial?p=3");
    await expect(page.getByTestId("video-topico")).toHaveCount(0); // os tópicos de base não têm vídeo próprio
  });

  test("uma página que não existe é um 404 a sério e o painel sem token não revela nada", async ({
    request,
  }) => {
    expect((await request.get("/nao-existe")).status()).toBe(404);
    expect((await request.get("/api/admin/estado")).status()).toBe(404);
    expect((await request.get("/api/sessoes/xxx")).status()).toBe(404);
  });

  test("o service worker instala-se e guarda só a casca da versão atual", async ({ page }) => {
    const versao = ((await (await page.request.get("/health")).json()) as { versao: string }).versao;
    await page.goto("/");
    await page.evaluate(() => navigator.serviceWorker.ready);
    const nomes = await page.evaluate(() => caches.keys());
    expect(nomes).toContain(`rifas-casca-${versao}`);
    const guardados = await page.evaluate(
      async (v) => (await (await caches.open(`rifas-casca-${v}`)).keys()).map((r) => new URL(r.url).pathname),
      versao,
    );
    expect(guardados).toContain("/");
    expect(guardados.some((p) => p.startsWith("/api/sessoes") || p === "/health")).toBe(false); // nunca a geração nem a API
  });

  test("a página de verificação do QR recusa um código inventado", async ({ page }) => {
    const r = await page.goto("/V/AAAA.BBBB");
    expect(r?.status()).toBe(404);
    await expect(page.locator("main")).toContainText("inválido");
  });
});
