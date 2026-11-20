import { expect, test } from "@playwright/test";

test.describe("páginas, sorteio e PWA", () => {
  test("o português do Brasil abre em /pt-br, com o vocabulário de lá, lang pt-BR e o seletor nesse valor", async ({
    page,
  }) => {
    await page.goto("/pt-br/tutorial");
    await expect(page.locator("html")).toHaveAttribute("lang", "pt-BR");
    await expect(page.getByTestId("lingua")).toHaveValue("pt-br");
    await expect(page.locator("body")).toContainText(/arquivo|tela|baixar/i); // o vocabulário do Brasil (espera pelo tutorial)
    await expect(page.locator("body")).not.toContainText(/ficheiro|ecrã|descarregar/i); // e nada de Portugal
  });

  test("o preçário: escolher a ocasião, escrever preços, ver a pré-visualização e descarregar o PDF e a imagem", async ({
    page,
  }) => {
    await page.goto("/precario");
    await page.getByTestId("precario-ocasiao").selectOption("festa_popular");
    await page.getByTestId("precario-preco-agua").fill("1,5");
    await page.getByTestId("precario-pais").selectOption("BR");
    await expect(page.getByTestId("precario-moeda")).toHaveValue("BRL");
    await expect(page.getByTestId("precario-previa-img")).toBeVisible(); // desenhada pelo servidor (PNG a sério)
    const [pdf] = await Promise.all([
      page.waitForEvent("download"),
      page.getByTestId("precario-pdf").click(),
    ]);
    expect(pdf.suggestedFilename()).toBe("precario.pdf");
    const [img] = await Promise.all([
      page.waitForEvent("download"),
      page.getByTestId("precario-imagem").click(),
    ]);
    expect(img.suggestedFilename()).toBe("precario.png");
    await page.getByTestId("precario-formato").selectOption("A6x4"); // cartões de mesa: 4 por folha A4
    await expect(page.getByTestId("precario-orientacao")).toBeDisabled();
    await expect(page.getByTestId("precario-previa-img")).toBeVisible();
    await expect(page.getByTestId("precario-erro")).toHaveCount(0);
    await page.getByTestId("precario-formato").selectOption("A4");
    await page.getByTestId("precario-tamanhos").check(); // dois tamanhos: o segundo preço e os rótulos
    await page.getByTestId("precario-preco2-agua").fill("2,5");
    await page.getByTestId("precario-rotulo-1").fill("Média");
    await expect(page.getByTestId("precario-previa-img")).toBeVisible();
    await expect(page.getByTestId("precario-erro")).toHaveCount(0);
    await page.getByTestId("precario-tamanhos").uncheck();
    await page.getByTestId("precario-icone-agua").click(); // as imagens à escolha do artigo: troca-se a imagem e o PDF continua a desenhar-se
    await page.getByTestId("precario-icone-agua-4").click();
    await expect(page.getByTestId("precario-icone-agua-4")).toHaveAttribute("aria-pressed", "true");
    await expect(page.getByTestId("precario-previa-img")).toBeVisible();
    await expect(page.getByTestId("precario-erro")).toHaveCount(0);
    // um combo de dois artigos de secções diferentes: entra em «Menus e combos» e a pré-visualização continua a desenhar-se
    await page.getByTestId("precario-combo-artigo-1").selectOption("agua");
    await page.getByTestId("precario-combo-artigo-2").selectOption("bolo");
    await page.getByTestId("precario-combo-juntar").click();
    await expect(page.getByTestId("precario-previa-img")).toBeVisible();
    await expect(page.getByTestId("precario-erro")).toHaveCount(0);
    // etiquetas de levantamento: a zona de cada secção, as cópias e a 1.ª folha desenhada pelo servidor
    await page.getByTestId("etiquetas-zona-bebidas").fill("Bar");
    await page.getByTestId("etiquetas-copias").fill("3");
    await page.getByTestId("etiquetas-ver").click();
    await expect(page.getByTestId("etiquetas-previa")).toBeVisible();
    const [etiquetas] = await Promise.all([
      page.waitForEvent("download"),
      page.getByTestId("etiquetas-pdf").click(),
    ]);
    expect(etiquetas.suggestedFilename()).toBe("etiquetas.pdf");
    // cores à escolha e logótipo (um PNG de 8 x 8 px): vão no pedido e a pré-visualização continua a desenhar-se
    await page.getByTestId("precario-cor-0").fill("#0a3d62");
    await page.getByTestId("precario-logo").setInputFiles({
      name: "logo.png",
      mimeType: "image/png",
      buffer: Buffer.from(
        "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAFElEQVR4nGM8YWPDgA0wYRUdtBIA/xQBUEfB7b0AAAAASUVORK5CYII=",
        "base64",
      ),
    });
    await page.getByTestId("precario-logo-lugar").selectOption("rodape");
    await expect(page.getByTestId("precario-logo-mini")).toBeVisible();
    await expect(page.getByTestId("precario-previa-img")).toBeVisible();
    await expect(page.getByTestId("precario-erro")).toHaveCount(0);
    await page.getByTestId("precario-logo-tirar").click();
    await page.getByTestId("precario-cores-repor").click();
    // uma foto própria (um PNG de 8 x 8 px): reduz-se no browser, vai no pedido e a pré-visualização continua a desenhar-se
    const png = Buffer.from(
      "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAFElEQVR4nGM8YWPDgA0wYRUdtBIA/xQBUEfB7b0AAAAASUVORK5CYII=",
      "base64",
    );
    await page
      .getByTestId("precario-foto-agua")
      .setInputFiles({ name: "agua.png", mimeType: "image/png", buffer: png });
    await expect(page.getByTestId("precario-foto-tirar-agua")).toBeVisible();
    await expect(page.getByTestId("precario-previa-img")).toBeVisible();
    await expect(page.getByTestId("precario-erro")).toHaveCount(0);
    await page.getByTestId("precario-meu-nome").fill("Bolo da avó");
    await page.getByTestId("precario-meu-juntar").click();
    await expect(page.getByTestId("precario-erro")).toHaveCount(0);
  });

  test("os vales de fichas: com uma moeda inventada, criar os vales leva ao gerador com o template do vale", async ({
    page,
  }) => {
    await page.goto("/precario");
    await expect(page.getByTestId("vales")).toHaveCount(0); // sem moeda inventada não há vales
    await page.getByTestId("precario-inventada").check();
    await page.getByTestId("precario-inv-nome").fill("fichas");
    await expect(page.getByTestId("vales-previa")).toBeVisible(); // o vale desenhado pelo servidor (PNG a sério)
    await page.getByTestId("vales-quantidade").fill("2");
    await page.getByTestId("vales-nota").fill("Só na festa");
    await expect(page.getByTestId("vales-erro")).toHaveCount(0);
    await page.getByTestId("vales-criar").click();
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByTestId("estado-template")).toContainText("✔"); // o template do vale ficou na sessão, com 1 rifa (o vale)
    await expect(page.getByTestId("estado-algarismos")).toContainText("✔");
    await expect(page.getByTestId("papel")).toBeVisible(); // um só vale: aparece o painel da folha (o QR e as séries são os de sempre)
  });

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

  test("os comentários: deixar um (anónimo) e vê-lo na lista, sem IP nem país; os botões estão à vista", async ({
    page,
    request,
  }) => {
    await page.goto("/");
    await expect(page.getByTestId("nav-comentarios")).toBeVisible();
    await expect(page.getByTestId("nav-reportar-problema")).toBeVisible();
    await page.getByTestId("nav-comentarios").click();
    await page.getByTestId("comentarios-escrever").click();
    await page.getByTestId("opiniao-texto").fill("Comentário do teste e2e, muito útil.");
    await page.getByTestId("opiniao-enviar").click();
    await expect(page.getByTestId("comentario-enviado")).toBeVisible();
    await page.getByTestId("comentario-ver").click();
    const c = page.getByTestId("comentario").first();
    await expect(c).toContainText("Comentário do teste e2e");
    await expect(c).toContainText("Anónimo(a)");
    const api = await (await request.get("/api/comentarios")).text();
    expect(api).not.toMatch(/127\.0\.0\.1|"ip"/); // a página pública nunca devolve o IP
  });

  test("reportar problema sem o GitHub ligado avisa e não deixa abrir; o painel dos comentários não existe sem sessão", async ({
    page,
    request,
  }) => {
    await page.goto("/reportar-problema");
    await expect(page.getByTestId("problema-inativo")).toBeVisible();
    await expect(page.getByTestId("problema-abrir")).toBeDisabled();
    expect(
      (
        await request.post("/api/problemas", { data: { resumo: "x".repeat(20), descricao: "y".repeat(20) } })
      ).status(),
    ).toBe(503);
    expect((await request.get("/api/admin/comentarios")).status()).toBe(404);
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

  test("cada língua tem o seu URL: o HTML já vem na língua, a interface segue o URL e o seletor muda-o", async ({
    page,
    request,
  }) => {
    // para quem não corre JavaScript (robôs): título, canónico e hreflang na língua do URL
    const html = await (await request.get("/ja/tutorial")).text();
    expect(html).toContain('<html lang="ja"');
    expect(html).toContain('<link rel="canonical" href="http://127.0.0.1:8123/ja/tutorial" />');
    expect(html).toContain('hreflang="x-default" href="http://127.0.0.1:8123/tutorial"');
    // no browser: a língua do URL ganha à do browser (pt-PT) e as ligações levam o prefixo
    await page.goto("/ja/tutorial");
    await expect(page.getByTestId("lingua")).toHaveValue("ja");
    await expect(page).toHaveTitle(/チュートリアル/);
    await expect(page.getByRole("link", { name: "抽選" })).toHaveAttribute("href", "/ja/sorteio");
    await page.getByRole("link", { name: "抽選" }).click();
    await expect(page).toHaveURL(/\/ja\/sorteio$/);
    // mudar de língua muda o prefixo; o português fica sem ele
    await page.getByTestId("lingua").selectOption("en");
    await expect(page).toHaveURL(/\/en\/sorteio$/);
    await page.getByTestId("lingua").selectOption("pt");
    await expect(page).toHaveURL(/127\.0\.0\.1:8123\/sorteio$/);
    // um URL com prefixo desconhecido é 404 a sério
    expect((await request.get("/xx/tutorial")).status()).toBe(404);
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
