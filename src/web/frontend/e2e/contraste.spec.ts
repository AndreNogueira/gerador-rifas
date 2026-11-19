import { expect, type Page, test } from "@playwright/test";
import { medirContraste } from "./ajuda-contraste";

// M10: o contraste dos 14 temas medido a sério num browser (WCAG AA), em claro e em escuro, na página inicial (com a galeria aberta), no
// sorteio e nas páginas de texto. Mede o texto contra os pixéis reais do fundo (ver ajuda-contraste.ts: o axe não mede gradientes).
// Quem muda as cores de um tema volta a correr isto: `pnpm e2e -g contraste`.
const TEMAS = [
  "premiado",
  "quermesse",
  "arcade",
  "brutalista",
  "risografia",
  "janela98",
  "gala",
  "matrix",
  "natal",
  "halloween",
  "praia",
  "jornal",
  "terminal",
  "circo",
] as const;
const MODOS = ["claro", "escuro"] as const;
const PAGINAS = [
  "/",
  "/sorteio",
  "/tutorial",
  "/termos",
  "/editor",
  "/como-fazer",
  "/rifas-para-escolas",
  "/como-numerar-bilhetes-de-rifa",
  "/precario",
  "/comentarios",
  "/opiniao",
  "/reportar-problema",
] as const;

async function abrir(page: Page, caminho: string, tema: string, modo: string) {
  await page.addInitScript(
    ([t, m]) => {
      localStorage.setItem("rifas.visual", t as string);
      localStorage.setItem("rifas.tema", m as string);
    },
    [tema, modo],
  );
  await page.emulateMedia({ colorScheme: modo === "escuro" ? "dark" : "light", reducedMotion: "reduce" });
  await page.goto(caminho);
  await page.waitForLoadState("networkidle"); // o tutorial pede o conteudo a API e desloca tudo: so se mede com a pagina assente
  await expect(page.getByRole("navigation").first()).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-visual", tema);
  await page.evaluate(() => document.fonts.ready);
}

for (const tema of TEMAS) {
  for (const modo of MODOS) {
    test(`contraste: ${tema} (${modo})`, async ({ page }, info) => {
      const falhas: string[] = [];
      let medidos = 0;
      for (const caminho of PAGINAS) {
        await abrir(page, caminho, tema, modo);
        if (caminho === "/") {
          await page.getByTestId("galeria").locator("summary").click();
          await expect(page.getByTestId("galeria-previa")).toBeVisible(); // a imagem desloca o resto da página: só se mede depois de chegar
        }
        const m = await medirContraste(page);
        medidos += m.medidos;
        for (const f of m.falhas)
          falhas.push(`${caminho}  ${f.alvo}  ${f.rácio} < ${f.esperado}  (${f.texto}, ${f.tamanho})`);
        if (caminho === "/") {
          // o seletor de desenhos aberto: o painel é uma superfície nova do tema (com uma opção ativa e outra escolhida)
          await page.getByTestId("galeria-desenho").click();
          await expect(page.getByRole("listbox")).toBeVisible();
          await page.keyboard.press("ArrowDown"); // uma opção ativa e outra escolhida (o hover rolaria a página e fecharia o painel)
          const aberto = await medirContraste(page, "[role=listbox]");
          medidos += aberto.medidos;
          for (const f of aberto.falhas)
            falhas.push(
              `${caminho} (seletor aberto)  ${f.alvo}  ${f.rácio} < ${f.esperado}  (${f.texto}, ${f.tamanho})`,
            );
          await page.keyboard.press("Escape");
          // o calendário da data: dia escolhido («Hoje»), dia com o foco, dias de outros meses, «Limpar» ativo
          // o painel fecha-se ao rolar: leva-se o botão para o ecrã e espera-se que o scroll assente antes de clicar
          const abrirCalendario = async () => {
            await page.getByTestId("galeria-data").scrollIntoViewIfNeeded();
            await page.evaluate(
              () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))),
            );
            await page.getByTestId("galeria-data").click();
          };
          await abrirCalendario();
          await page.getByTestId("galeria-data-hoje").click();
          await abrirCalendario();
          await expect(page.getByRole("dialog")).toBeVisible();
          await page.keyboard.press("ArrowRight");
          const calendario = await medirContraste(page, "[role=dialog]");
          medidos += calendario.medidos;
          for (const f of calendario.falhas)
            falhas.push(
              `${caminho} (calendário)  ${f.alvo}  ${f.rácio} < ${f.esperado}  (${f.texto}, ${f.tamanho})`,
            );
          await page.keyboard.press("Escape");
        }
      }
      info.annotations.push({ type: "medidos", description: `${medidos} elementos de texto medidos` });
      expect(medidos, "tem de medir muitos elementos (senão o teste não prova nada)").toBeGreaterThan(80);
      expect(falhas, falhas.join("\n")).toEqual([]);
    });
  }
}
