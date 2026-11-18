import { expect, test } from "@playwright/test";

// O nome da aplicação nunca se corta nem parte em duas linhas, em nenhuma língua nem largura (o cabeçalho cresce em altura, não o nome).
const LINGUAS = ["", "en", "de", "el", "ru", "ja", "hi", "vi", "uk", "id"]; // sem prefixo = português
const LARGURAS = [360, 768, 1440, 3300];

test.describe("cabeçalho", () => {
  for (const largura of LARGURAS) {
    test(`o nome da app cabe inteiro numa só linha a ${largura}px`, async ({ page }) => {
      await page.setViewportSize({ width: largura, height: 800 });
      for (const lg of LINGUAS) {
        await page.goto(`/${lg}`);
        const nome = page.locator(".topo .nome");
        await expect(nome).toBeVisible();
        const medida = await nome.evaluate((el) => {
          const linha = Number.parseFloat(getComputedStyle(el).lineHeight);
          return {
            linhas: Math.round((el.getClientRects()[0]?.height ?? 0) / linha),
            cortado: el.scrollWidth > el.clientWidth + 1,
            fora: el.getBoundingClientRect().right > document.documentElement.clientWidth,
            rolaPagina: document.documentElement.scrollWidth > document.documentElement.clientWidth,
          };
        });
        expect(medida, `lingua ${lg || "pt"} a ${largura}px`).toEqual({
          linhas: 1,
          cortado: false,
          fora: false,
          rolaPagina: false,
        });
      }
    });
  }

  test("em ecrãs pequenos as opções passam para o menu «hambúrguer», que funciona", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 800 });
    await page.goto("/");
    await expect(page.getByTestId("nav-burger")).toBeVisible();
    await expect(page.getByTestId("nav-sorteio")).toHaveCount(0);
    await page.getByTestId("nav-burger").click();
    await expect(page.locator("#menu-burger")).toBeVisible();
    await page.getByTestId("burger-sorteio").click();
    await expect(page).toHaveURL(/\/sorteio$/);
    await expect(page.locator("#menu-burger")).toHaveCount(0);
  });

  test("à medida que a janela estreita o menu vai recebendo mais opções", async ({ page }) => {
    const visiveis: number[] = [];
    for (const largura of [1600, 1100, 800, 500, 360]) {
      await page.setViewportSize({ width: largura, height: 800 });
      await page.goto("/");
      await expect(page.locator(".topo .nome")).toBeVisible();
      await page.waitForTimeout(150);
      visiveis.push(await page.locator(".cluster [data-item]").count());
    }
    expect(visiveis[0]).toBeGreaterThanOrEqual(visiveis[1] ?? 0);
    for (let i = 1; i < visiveis.length; i++)
      expect(visiveis[i - 1]).toBeGreaterThanOrEqual(visiveis[i] ?? 0);
    expect(visiveis.at(-1)).toBe(0); // 360 px: só o nome e o botão do menu
  });

  test("o menu «Ajuda» junta o tutorial, o vídeo e os guias «Como fazer»", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("nav-tutorial")).toHaveCount(0); // já não são separadores soltos
    await page.getByTestId("nav-ajuda").click();
    await expect(page.locator("#menu-ajuda a")).toHaveCount(8);
    await page.getByTestId("nav-video").click();
    await expect(page).toHaveURL(/\/video$/);
    await expect(page.getByTestId("nav-ajuda")).toHaveAttribute("aria-current", "page");
  });
});
