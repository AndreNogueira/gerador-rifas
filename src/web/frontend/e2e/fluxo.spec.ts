import { readFile } from "node:fs/promises";
import { expect, type Page, test } from "@playwright/test";
import { fixture } from "./ajuda";

/** Carrega o template e os algarismos de exemplo e espera que a app os aceite. */
async function prepararFicheiros(page: Page) {
  await page.goto("/");
  await expect(page.getByTestId("upload-template")).toBeAttached();
  await page.getByTestId("upload-template").setInputFiles(fixture("template_exemplo.pdf"));
  await expect(page.getByTestId("estado-template")).toContainText("5 bilhetes");
  await page.getByTestId("upload-algarismos").setInputFiles(fixture("digitos_exemplo.pdf"));
  await expect(page.getByTestId("estado-algarismos")).toContainText("✔");
}

/** Gera (um só PDF) e descarrega: devolve o nome e os bytes do ficheiro. */
async function gerarEDescarregar(page: Page, nome: string, ate = "12") {
  await page.getByTestId("ate").fill(ate);
  await page.locator('input[name="modo"][value="unico"]').check();
  await page.getByTestId("nome").fill(nome);
  await page.getByTestId("gerar").click();
  const descarregar = page.getByTestId("descarregar");
  await expect(descarregar).toBeVisible();
  const [download] = await Promise.all([page.waitForEvent("download"), descarregar.click()]);
  return { nome: download.suggestedFilename(), bytes: await readFile(await download.path()) };
}

test.describe("o gerador, de ponta a ponta", () => {
  test("a pré-visualização aparece e refaz-se sozinha, sem carregar no botão", async ({ page }) => {
    await prepararFicheiros(page);
    await expect(page.getByTestId("titulo-visor")).toContainText("1 a 5", { timeout: 10_000 }); // veio sozinha
    const primeira = await page.getByTestId("visor").getAttribute("src");
    await page.getByTestId("algarismos").fill("6");
    await expect(page.getByTestId("visor")).not.toHaveAttribute("src", primeira ?? "", { timeout: 10_000 }); // outro `n`: refez-se
    await expect(page.getByTestId("previa-erro")).toHaveCount(0);
  });

  test("do template ao PDF descarregado, com pré-visualização", async ({ page }) => {
    await prepararFicheiros(page);
    await page.getByTestId("ate").fill("12");
    await page.getByTestId("nome").fill("Rifa E2E");
    await page.getByTestId("previa").click();
    await expect(page.getByTestId("titulo-visor")).toContainText("1 a 5");
    await expect(page.getByTestId("visor")).toBeVisible();
    const f = await gerarEDescarregar(page, "Rifa E2E");
    expect(f.nome).toBe("Rifa E2E - 0001 - 0012.pdf");
    expect(f.bytes.subarray(0, 5).toString("latin1")).toBe("%PDF-");
    expect(f.bytes.length).toBeGreaterThan(5_000);
  });

  test("várias séries com saltos dão um ZIP com um PDF por série", async ({ page }) => {
    await prepararFicheiros(page);
    await page.getByTestId("ate").fill("10");
    await page.getByTestId("prefixos").fill("A-, B-");
    await page.getByTestId("saltar").fill("3");
    await page.locator('input[name="modo"][value="unico"]').check();
    await page.getByTestId("nome").fill("Series");
    await expect(page.getByTestId("resumo")).toContainText("18 números");
    await page.getByTestId("gerar").click();
    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.getByTestId("descarregar").click(),
    ]);
    expect(download.suggestedFilename()).toMatch(/\.zip$/);
    const bytes = await readFile(await download.path());
    expect(bytes.subarray(0, 2).toString("latin1")).toBe("PK");
    expect(bytes.toString("latin1")).toContain("Series - A - 0001 - 0010.pdf");
    expect(bytes.toString("latin1")).toContain("Series - B - 0001 - 0010.pdf");
  });

  test("a galeria cria o template e os algarismos, e o QR de verificação aparece", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("galeria")).toBeAttached();
    await page.getByTestId("galeria").locator("summary").click();
    await page.getByTestId("galeria-desenho").click();
    await expect(page.getByRole("listbox").getByRole("option")).toHaveCount(25);
    await page.getByRole("listbox").getByRole("option", { name: "Natal", exact: true }).click();
    await page.getByTestId("galeria-titulo").fill("Rifa de Natal");
    await expect(page.getByTestId("galeria-previa")).toBeVisible();
    await page.getByTestId("galeria-usar").click();
    await expect(page.getByTestId("estado-template")).toContainText("galeria-natal.pdf");
    await expect(page.getByTestId("estado-algarismos")).toContainText("✔");
    await expect(page.getByTestId("papel")).toBeVisible(); // uma rifa: aparece o painel da folha
    await page.getByTestId("qr").check(); // o servidor de teste tem a chave
    await page.getByTestId("marcas").check();
    const f = await gerarEDescarregar(page, "Galeria", "10");
    expect(f.bytes.subarray(0, 5).toString("latin1")).toBe("%PDF-");
    expect(f.bytes.length).toBeGreaterThan(20_000); // duas folhas com o desenho, QR e marcas de corte
  });

  test("a lista sai em CSV e a folha de controlo em PDF", async ({ page }) => {
    await page.goto("/");
    await page.getByTestId("ate").fill("40");
    await page.getByTestId("nome").fill("Lista");
    const [csv] = await Promise.all([
      page.waitForEvent("download"),
      page.getByTestId("exportar-csv").click(),
    ]);
    expect(csv.suggestedFilename()).toBe("Lista.csv");
    expect((await readFile(await csv.path(), "utf8")).split("\n").length).toBeGreaterThan(40);
    const [pdf] = await Promise.all([
      page.waitForEvent("download"),
      page.getByTestId("exportar-controlo").click(),
    ]);
    expect(pdf.suggestedFilename()).toBe("Controlo - Lista.pdf");
    expect((await readFile(await pdf.path())).subarray(0, 5).toString("latin1")).toBe("%PDF-");
  });

  test("«Limpar tudo» recomeça do zero", async ({ page }) => {
    await prepararFicheiros(page);
    await page.getByTestId("limpar").click();
    await expect(page.getByTestId("estado-template")).not.toContainText("5 bilhetes");
    await expect(page.getByTestId("previa")).toBeDisabled();
  });
});
