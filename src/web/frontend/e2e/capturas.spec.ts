import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { expect, type Page, test } from "@playwright/test";
import { fixture } from "./ajuda";

// Tira as capturas do tutorial do SITE (as imagens dos tópicos de base), uma série por língua, da própria interface.
// NÃO corre nos testes normais: `pnpm capturas` (GRAVAR_CAPTURAS=1; `GRAVAR_CAPTURAS=pt,en` só essas línguas). Escreve em `app/assets/ajuda/`:
//   <lg>_wa.png  a página com o template e os algarismos carregados e a pré-visualização aberta (zonas c1..c4, visor, barra, janela)
//   <lg>_wb.png  depois de gerar (zona acoes)
//   <lg>_wc.png  o cartão 1 com um template de uma só rifa (painel da folha; zona c1)
// e junta as zonas a `ajuda.json` (chaves wa/wb/wc, ao lado das capturas da app Windows a/b/c). Regra do projeto: o aspeto do site mudou → volta a correr.
const GRAVAR = process.env.GRAVAR_CAPTURAS;
const AJUDA = join(import.meta.dirname, "..", "..", "..", "..", "app", "assets", "ajuda");
const LINGUAS = [
  "pt",
  "en",
  "es",
  "fr",
  "de",
  "it",
  "nl",
  "pl",
  "ru",
  "tr",
  "ja",
  "ko",
  "zh",
  "hi",
  "cs",
  "ro",
  "sv",
  "el",
  "ca",
  "uk",
  "id",
  "vi",
];
const LOCAL: Record<string, string> = { pt: "pt-PT", en: "en-US", zh: "zh-CN" };
const VISTA = { width: 1240, height: 1000 };

type Caixa = [number, number, number, number];

async function caixa(page: Page, seletor: string): Promise<Caixa> {
  const b = await page.locator(seletor).first().boundingBox();
  if (!b) throw new Error(`sem caixa para ${seletor}`);
  const dy = await page.evaluate(() => window.scrollY); // a captura é da página inteira: coordenadas da página, não da janela
  const x = Math.max(0, Math.floor(b.x));
  const y = Math.max(0, Math.floor(b.y + dy));
  return [x, y, Math.ceil(b.x + b.width), Math.ceil(b.y + b.height + dy)];
}

async function gravarZonas(lg: string, zonas: Record<string, Record<string, unknown>>) {
  const ficheiro = join(AJUDA, "ajuda.json");
  const todas = JSON.parse(await readFile(ficheiro, "utf-8"));
  todas[lg] = { ...todas[lg], ...zonas };
  await writeFile(ficheiro, `${JSON.stringify(todas, null, 1)}\n`, "utf-8");
}

/** Carrega um ficheiro e espera pelo visto; se a página ainda estava a trocar de língua e o ficheiro se perdeu, tenta outra vez. */
async function carregar(page: Page, campo: string, estado: string, ficheiro: string) {
  for (let tentativa = 0; ; tentativa++) {
    await page.getByTestId(campo).setInputFiles(ficheiro);
    try {
      await expect(page.getByTestId(estado)).toContainText("✔", { timeout: 8000 });
      return;
    } catch (e) {
      if (tentativa >= 3) throw e;
    }
  }
}

async function foto(page: Page, nome: string) {
  await page.evaluate(() => document.fonts.ready);
  await page.mouse.move(2, 2);
  await page.screenshot({ path: join(AJUDA, nome), fullPage: true });
}

test.describe("capturas do tutorial do site", () => {
  test.skip(!GRAVAR, "só com GRAVAR_CAPTURAS=1 (pnpm capturas)");
  test.describe.configure({ mode: "serial" });
  test.setTimeout(180_000);
  const so = GRAVAR === "1" ? null : GRAVAR?.split(",");
  for (const lg of LINGUAS) {
    if (so && !so.includes(lg)) continue;
    test(`capturas (${lg})`, async ({ browser, baseURL }) => {
      const contexto = await browser.newContext({
        baseURL,
        locale: LOCAL[lg] ?? lg,
        viewport: VISTA,
        colorScheme: "light",
        deviceScaleFactor: 1,
      });
      await contexto.addInitScript(() => {
        try {
          localStorage.setItem("rifas.tema", "claro");
          localStorage.setItem("rifas.visual", "premiado");
        } catch {
          /* sem armazenamento: a página usa os valores por omissão */
        }
      });
      const page = await contexto.newPage();
      // a língua vem do URL, não do browser (sem prefixo é sempre português: ver `src/web/frontend/src/rota.tsx`)
      const base = lg === "pt" ? "/" : `/${lg}`;

      // c: um template de uma só rifa (painel da folha)
      await page.goto(base);
      await page.waitForLoadState("networkidle"); // as 18 línguas vêm da API: só se carrega depois de o texto estar na página
      await carregar(page, "upload-template", "estado-template", fixture("template_exemplo_1_rifa.pdf"));
      await expect(page.getByTestId("papel")).toBeVisible();
      await page.waitForTimeout(600);
      const c = await caixa(page, ".passo-1");
      await foto(page, `${lg}_wc.png`);

      // a: template de várias rifas + algarismos + pré-visualização
      await page.reload();
      await page.waitForLoadState("networkidle");
      await carregar(page, "upload-template", "estado-template", fixture("template_exemplo.pdf"));
      await carregar(page, "upload-algarismos", "estado-algarismos", fixture("digitos_exemplo.pdf"));
      await page.getByTestId("ate").fill("120");
      await page.getByTestId("nome").fill("Rifa de Natal");
      await page.getByTestId("previa").click();
      await expect(page.getByTestId("visor")).toBeVisible();
      await page.waitForTimeout(1800);
      const a = {
        janela: [
          0,
          0,
          VISTA.width,
          await page.evaluate(() => document.documentElement.scrollHeight),
        ] as Caixa,
        c1: await caixa(page, ".passo-1"),
        c2: await caixa(page, ".passo-2"),
        c3: await caixa(page, ".passo-3"),
        c4: await caixa(page, ".passo-4"),
        visor: await caixa(page, ".visor"),
        barra: await caixa(page, ".visor > :first-child"),
        escala: 1.0,
      };
      await foto(page, `${lg}_wa.png`);

      // b: depois de gerar
      await page.getByTestId("gerar").click();
      await expect(page.getByTestId("descarregar")).toBeVisible({ timeout: 120_000 });
      await page.waitForTimeout(600);
      const b = {
        janela: [
          0,
          0,
          VISTA.width,
          await page.evaluate(() => document.documentElement.scrollHeight),
        ] as Caixa,
        acoes: await caixa(page, ".acoes"),
        escala: 1.0,
      };
      await foto(page, `${lg}_wb.png`);
      await gravarZonas(lg, { wa: a, wb: b, wc: { c1: c, escala: 1.0 } });
      await contexto.close();
    });
  }
});
