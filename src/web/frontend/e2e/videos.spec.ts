import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { type Browser, expect, type Locator, type Page, test } from "@playwright/test";
import { fixture } from "./ajuda";

// Grava os vídeos das funcionalidades (um por funcionalidade e por língua, em português e inglês) a partir da própria interface do site.
// NÃO corre nos testes normais: `pnpm videos` (GRAVAR_VIDEOS=1). Escreve `videos-gravados/web_<id>_<lg>.webm` e `.json` (o instante em que
// a preparação acaba: o começo, em que se carregam os ficheiros, corta-se depois). `scripts/videos_para_mp4.py` (na raiz do repositório)
// converte-os para `app/assets/video/web_<id>_<lg>.mp4`. Regra do projeto: uma funcionalidade nova leva a sua cena aqui (CLAUDE.md).
const GRAVAR = !!process.env.GRAVAR_VIDEOS;
const DESTINO = join(import.meta.dirname, "..", "videos-gravados"); // fora de test-results: o Playwright apaga essa pasta a cada execução
const LOGOTIPO = join(import.meta.dirname, "ficheiros", "logotipo.png");
const TAMANHO = { width: 1280, height: 720 };
type Lg = "pt" | "en";
type Texto = (pt: string, en: string) => string;

const PALCO = `
(() => {
  const css = document.createElement("style");
  css.textContent = \`
    #__legenda { position: fixed; left: 50%; bottom: 22px; transform: translateX(-50%); max-width: 82%; z-index: 2147483646; pointer-events: none;
      background: rgba(20, 16, 40, .93); color: #fff; font: 600 26px/1.35 system-ui, sans-serif; padding: 14px 26px; border-radius: 14px;
      text-align: center; box-shadow: 0 6px 24px rgba(0,0,0,.35); transition: opacity .25s; }
    #__legenda:empty { opacity: 0; }
    #__cursor { position: fixed; top: 0; left: 0; width: 30px; height: 30px; z-index: 2147483647; pointer-events: none; transition: transform .05s linear;
      filter: drop-shadow(1px 2px 2px rgba(0,0,0,.5)); }
    #__barra { position: fixed; left: 50%; top: 10px; transform: translateX(-50%); z-index: 2147483645; pointer-events: none; width: 620px; height: 44px;
      border-radius: 22px; background: #fff; border: 2px solid #6a35f5; display: none; align-items: center; justify-content: space-between;
      padding: 0 16px; font: 500 18px system-ui; color: #333; box-shadow: 0 6px 24px rgba(0,0,0,.3); }
    #__barra b { display: inline-block; width: 30px; height: 30px; border-radius: 50%; background: #6a35f5; color: #fff; text-align: center; line-height: 30px;
      animation: __pulsa 1s ease-in-out infinite; }
    @keyframes __pulsa { 50% { transform: scale(1.35); } }
  \`;
  const montar = () => {
    document.head.appendChild(css);
    const l = document.createElement("div"); l.id = "__legenda"; document.body.appendChild(l);
    const b = document.createElement("div"); b.id = "__barra"; b.innerHTML = "<span>https://</span><b>⊕</b>"; document.body.appendChild(b);
    const c = document.createElement("div"); c.id = "__cursor";
    c.innerHTML = '<svg viewBox="0 0 24 24" width="30" height="30"><path d="M3 2l7 19 3-8 8-3z" fill="#fff" stroke="#111" stroke-width="1.5" stroke-linejoin="round"/></svg>';
    document.body.appendChild(c);
    addEventListener("mousemove", (e) => { c.style.transform = "translate(" + e.clientX + "px," + e.clientY + "px)"; }, true);
  };
  if (document.body) montar(); else addEventListener("DOMContentLoaded", montar);
})();`;

const pausa = (page: Page, ms = 1800) => page.waitForTimeout(ms);

async function legenda(page: Page, texto: string, ms = 2200) {
  await page.evaluate((t) => {
    const l = document.getElementById("__legenda");
    if (l) l.textContent = t;
  }, texto);
  if (ms) await pausa(page, ms);
}

async function ir(page: Page, alvo: Locator) {
  await alvo.scrollIntoViewIfNeeded();
  const b = await alvo.boundingBox();
  if (b) await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2, { steps: 28 });
}

async function clicar(page: Page, alvo: Locator) {
  await ir(page, alvo);
  await pausa(page, 350);
  await alvo.click();
}

async function escrever(page: Page, alvo: Locator, texto: string) {
  await ir(page, alvo);
  await alvo.click();
  await alvo.fill("");
  await alvo.pressSequentially(texto, { delay: 95 });
}

async function carregar(page: Page, input: Locator, ficheiro: string) {
  await ir(page, input.locator("xpath=.."));
  await pausa(page, 400);
  await input.setInputFiles(ficheiro);
}

/** Abre a página e carrega o template e os algarismos (a parte que se corta do vídeo). */
async function preparar(page: Page, template: string, algarismos: string) {
  await page.goto("/");
  await expect(page.getByTestId("upload-template")).toBeAttached();
  await page.getByTestId("upload-template").setInputFiles(fixture(template));
  await expect(page.getByTestId("estado-template")).toContainText("✔");
  await page.getByTestId("upload-algarismos").setInputFiles(fixture(algarismos));
  await expect(page.getByTestId("estado-algarismos")).toContainText("✔");
  await page.waitForTimeout(500);
}

const UMA_RIFA = ["template_exemplo_1_rifa.pdf", "digitos_exemplo.png"] as const;
const VARIAS = ["template_exemplo.pdf", "digitos_exemplo.pdf"] as const;

interface Cena {
  id: string;
  template?: readonly [string, string];
  rodar: (page: Page, T: Texto) => Promise<void>;
}

const CENAS: Cena[] = [
  {
    id: "series",
    template: VARIAS,
    rodar: async (page, T) => {
      await legenda(page, T("Séries, prefixos e números a saltar", "Series, prefixes and skipped numbers"));
      await escrever(page, page.getByTestId("ate"), "30");
      await legenda(
        page,
        T(
          "Escreva os prefixos separados por vírgulas: cada um é uma série",
          "Type the prefixes separated by commas: each one is a series",
        ),
        1200,
      );
      await escrever(page, page.getByTestId("prefixos"), "A-, B-");
      await pausa(page, 1500);
      await legenda(
        page,
        T("Números que não se imprimem: 13 e de 20 a 22", "Numbers that are not printed: 13 and 20 to 22"),
        1200,
      );
      await escrever(page, page.getByTestId("saltar"), "13, 20-22");
      await legenda(
        page,
        T(
          "O resumo conta só o que se imprime, série a série",
          "The summary counts only what gets printed, series by series",
        ),
        2600,
      );
      await legenda(page, T("Cada série pode ter a sua cor", "Each series can have its own color"), 800);
      await clicar(page, page.getByTestId("cor-serie"));
      await pausa(page, 800);
      await clicar(page, page.getByTestId("previa"));
      await expect(page.getByTestId("visor")).toBeVisible();
      await legenda(
        page,
        T(
          "A pré-visualização mostra o prefixo A- e a cor da série",
          "The preview shows the A- prefix and the series color",
        ),
        3600,
      );
      await legenda(
        page,
        T("Cada série sai nos seus próprios PDFs", "Each series comes out in its own PDFs"),
        2600,
      );
    },
  },
  {
    id: "lista",
    rodar: async (page, T) => {
      await page.goto("/");
      await legenda(page, T("Lista de bilhetes e folha de controlo", "Ticket list and control sheet"), 2000);
      await escrever(page, page.getByTestId("ate"), "120");
      await escrever(page, page.getByTestId("nome"), T("Rifa de Natal", "Christmas raffle"));
      await legenda(
        page,
        T(
          "Não precisa de template: usa só o intervalo e o nome",
          "No template needed: it only uses the range and the name",
        ),
        2600,
      );
      await legenda(
        page,
        T("«Exportar lista» dá um CSV que abre no Excel", "“Export list” gives a CSV that opens in Excel"),
        800,
      );
      const [csv] = await Promise.all([
        page.waitForEvent("download"),
        clicar(page, page.getByTestId("exportar-csv")),
      ]);
      await csv.path();
      await legenda(
        page,
        T(
          "Um bilhete por linha, com Nome, Contacto e Pago para preencher",
          "One ticket per row, with Name, Contact and Paid to fill in",
        ),
        3200,
      );
      await legenda(
        page,
        T(
          "A folha de controlo é um PDF para imprimir e ir marcando quem pagou",
          "The control sheet is a PDF to print and tick off who paid",
        ),
        800,
      );
      const [pdf] = await Promise.all([
        page.waitForEvent("download"),
        clicar(page, page.getByTestId("exportar-controlo")),
      ]);
      await pdf.path();
      await legenda(
        page,
        T("36 bilhetes por página, com uma caixa de «pago»", "36 tickets per page, with a “paid” box"),
        3200,
      );
    },
  },
  {
    id: "marcas",
    template: UMA_RIFA,
    rodar: async (page, T) => {
      await legenda(page, T("Marcas de corte", "Crop marks"), 1800);
      await legenda(
        page,
        T(
          "Com uma só rifa repetida na folha, a margem deve ter 3 mm ou mais",
          "With a single ticket repeated on the sheet, the margin must be 3 mm or more",
        ),
        3000,
      );
      await clicar(page, page.getByTestId("marcas"));
      await legenda(page, T("Ligue «Marcas de corte»", "Turn on “Crop marks”"), 1600);
      await escrever(page, page.getByTestId("ate"), "20");
      await clicar(page, page.getByTestId("previa"));
      await expect(page.getByTestId("visor")).toBeVisible();
      await legenda(
        page,
        T(
          "Os traços nas margens prolongam as linhas de corte",
          "The marks in the margins extend the cutting lines",
        ),
        4200,
      );
    },
  },
  {
    id: "galeria",
    rodar: async (page, T) => {
      await page.goto("/");
      await legenda(
        page,
        T("Sem template do Canva? Use a galeria", "No Canva template? Use the gallery"),
        2200,
      );
      await clicar(page, page.getByTestId("galeria").locator("summary"));
      await clicar(page, page.getByTestId("galeria-desenho"));
      await legenda(page, T("Escolha um dos 24 desenhos", "Pick one of the 24 designs"), 2200);
      await clicar(page, page.getByRole("listbox").getByRole("option", { name: "Natal", exact: true }));
      await escrever(page, page.getByTestId("galeria-titulo"), T("Rifa de Natal", "Christmas raffle"));
      await expect(page.getByTestId("galeria-previa")).toBeVisible();
      await legenda(
        page,
        T(
          "Escreva o título, a organização, os prémios e a data",
          "Write the title, the organization, the prizes and the date",
        ),
        3000,
      );
      await clicar(page, page.getByTestId("galeria-usar"));
      await expect(page.getByTestId("estado-template")).toContainText("galeria-natal.pdf");
      await legenda(
        page,
        T(
          "«Usar este template»: o template e os algarismos ficam prontos",
          "“Use this template”: the template and the digits are ready",
        ),
        3200,
      );
      await legenda(
        page,
        T("Só falta escolher os números e gerar", "All that is left is choosing the numbers and generating"),
        2400,
      );
    },
  },
  {
    id: "editor",
    rodar: async (page, T) => {
      await page.goto("/");
      await legenda(
        page,
        T("Sem Canva? Desenhe a sua rifa no editor", "No Canva? Design your ticket in the editor"),
        2200,
      );
      await clicar(page, page.getByTestId("ligacao-editor"));
      await expect(page.getByTestId("editor-tela")).toBeVisible();
      await legenda(
        page,
        T("Começa com um modelo de rifa com talão", "It starts with a sample ticket with a stub"),
        2400,
      );
      await clicar(page, page.getByTestId("el-texto").first());
      await escrever(page, page.getByTestId("editor-texto"), T("RIFA DE NATAL", "CHRISTMAS RAFFLE"));
      await legenda(
        page,
        T(
          "Escolha um elemento e mude o texto, a cor e o tamanho",
          "Pick an element and change its text, color and size",
        ),
        3000,
      );
      const alvo = page.getByTestId("el-texto").nth(1);
      const caixa = await alvo.boundingBox();
      if (caixa) {
        await page.mouse.move(caixa.x + caixa.width / 2, caixa.y + caixa.height / 2);
        await page.mouse.down();
        await page.mouse.move(caixa.x + caixa.width / 2 + 90, caixa.y + caixa.height / 2 + 6, { steps: 14 });
        await page.mouse.up();
      }
      await legenda(
        page,
        T(
          "Arraste os elementos para o sítio (ou use as setas)",
          "Drag the elements into place (or use the arrow keys)",
        ),
        2800,
      );
      await clicar(page, page.getByTestId("editor-duplicar"));
      await legenda(
        page,
        T(
          "Duplicar, desfazer e refazer (Ctrl+D, Ctrl+Z, Ctrl+Y)",
          "Duplicate, undo and redo (Ctrl+D, Ctrl+Z, Ctrl+Y)",
        ),
        2200,
      );
      await clicar(page, page.getByTestId("editor-desfazer"));
      await pausa(page, 900);
      await page.getByTestId("editor-ficheiro").setInputFiles(LOGOTIPO);
      await legenda(page, T("Junte o logótipo da associação", "Add your association's logo"), 2600);
      await clicar(page, page.getByTestId("editor-tras"));
      await pausa(page, 900);
      await clicar(page, page.getByTestId("add-retangulo"));
      await legenda(
        page,
        T(
          "Junte textos, retângulos, linhas e o número 0001 (uma ou duas vezes)",
          "Add texts, rectangles, lines and the number 0001 (once or twice)",
        ),
        3200,
      );
      await clicar(page, page.getByTestId("editor-apagar"));
      await clicar(page, page.getByTestId("editor-usar"));
      await expect(page.getByTestId("estado-template")).toContainText("editor");
      await legenda(
        page,
        T(
          "«Usar este template»: o template e os algarismos ficam prontos",
          "“Use this template”: the template and the digits are ready",
        ),
        3200,
      );
      await legenda(
        page,
        T("Só falta escolher os números e gerar", "All that is left is choosing the numbers and generating"),
        2400,
      );
    },
  },
  {
    id: "marca",
    template: UMA_RIFA,
    rodar: async (page, T) => {
      await legenda(page, T("Marca própria: cor e logótipo", "Your brand: color and logo"), 1800);
      await legenda(page, T("Escolha a cor dos números", "Choose the color of the numbers"), 800);
      await ir(page, page.getByTestId("cor-numeros"));
      await page.getByTestId("cor-numeros").fill("#c1121f");
      await pausa(page, 1500);
      await legenda(
        page,
        T("Carregue o logótipo da associação (PNG ou JPG)", "Upload the association's logo (PNG or JPG)"),
        800,
      );
      await carregar(page, page.getByTestId("upload-logotipo"), LOGOTIPO);
      await expect(page.getByTestId("logotipo-nome")).toBeVisible();
      await pausa(page, 1500);
      await legenda(page, T("Escolha o canto e o tamanho", "Choose the corner and the size"), 800);
      await page.getByTestId("logo-posicao").selectOption({ index: 0 });
      await page.getByTestId("logo-tamanho").fill("30");
      await pausa(page, 1200);
      await clicar(page, page.getByTestId("previa"));
      await expect(page.getByTestId("visor")).toBeVisible();
      await legenda(
        page,
        T("O logótipo e a cor aparecem em cada rifa", "The logo and the color appear on every ticket"),
        4000,
      );
    },
  },
  {
    id: "qr",
    template: UMA_RIFA,
    rodar: async (page, T) => {
      await legenda(page, T("QR em cada bilhete", "A QR code on every ticket"), 1800);
      await clicar(page, page.getByTestId("qr"));
      await legenda(page, T("Ligue «QR de verificação»", "Turn on “Verification QR”"), 1800);
      await legenda(
        page,
        T("Escolha o canto e o tamanho do código", "Choose the corner and the size of the code"),
        1800,
      );
      await escrever(page, page.getByTestId("ate"), "10");
      await clicar(page, page.getByTestId("previa"));
      await expect(page.getByTestId("visor")).toBeVisible();
      await legenda(
        page,
        T("Cada bilhete leva o seu código QR", "Each ticket carries its own QR code"),
        3600,
      );
      await legenda(
        page,
        T(
          "Ler o QR confirma que o código foi emitido por este serviço para aquele bilhete",
          "Scanning it confirms the code was issued by this service for that ticket",
        ),
        4200,
      );
      await legenda(
        page,
        T("Não prova que foi pago nem que ganhou", "It does not prove it was paid or has won"),
        3000,
      );
    },
  },
  {
    id: "sorteio",
    rodar: async (page, T) => {
      await page.goto("/sorteio");
      await expect(page.getByTestId("sorteio-sortear")).toBeVisible();
      await legenda(page, T("Sorteio verificável", "Verifiable draw"), 1800);
      await escrever(page, page.getByTestId("sorteio-de"), "1");
      await escrever(page, page.getByTestId("sorteio-ate"), "500");
      await escrever(page, page.getByTestId("sorteio-n"), "3");
      await legenda(
        page,
        T("O intervalo de números e quantos sortear", "The range of numbers and how many to draw"),
        2200,
      );
      await legenda(
        page,
        T(
          "A semente pública: algo que ninguém controla, como o resultado de uma lotaria",
          "The public seed: something nobody controls, like a lottery result",
        ),
        1200,
      );
      await escrever(
        page,
        page.getByTestId("sorteio-semente"),
        T("lotaria-2026-12-22", "lottery-2026-12-22"),
      );
      await pausa(page, 800);
      await clicar(page, page.getByTestId("sorteio-sortear"));
      await expect(page.getByTestId("sorteio-resultado")).toBeVisible();
      await legenda(
        page,
        T("Os números saem pela ordem do sorteio", "The numbers come out in draw order"),
        3200,
      );
      await legenda(
        page,
        T(
          "Quem repetir com os mesmos dados obtém sempre o mesmo resultado",
          "Anyone repeating it with the same data always gets the same result",
        ),
        3600,
      );
      await clicar(page, page.getByTestId("sorteio-copiar"));
      await legenda(
        page,
        T(
          "«Copiar ligação» partilha o sorteio para os outros o confirmarem",
          "“Copy link” shares the draw so others can confirm it",
        ),
        3200,
      );
    },
  },
  {
    id: "guardar",
    template: VARIAS,
    rodar: async (page, T) => {
      await legenda(page, T("Guardar e partilhar o pedido", "Save and share your request"), 1800);
      await escrever(page, page.getByTestId("ate"), "250");
      await legenda(
        page,
        T(
          "O site lembra-se do pedido e dos algarismos, só no seu browser",
          "The site remembers your request and the digits, only in your browser",
        ),
        2800,
      );
      await page.evaluate(() => localStorage.removeItem("rifas.sessao")); // «um ano depois»: sessão nova, mas a memória do browser (IndexedDB) fica
      await page.reload();
      await legenda(
        page,
        T("Um ano depois: basta carregar o template", "A year later: just load the template"),
        1000,
      );
      await carregar(page, page.getByTestId("upload-template"), fixture(VARIAS[0]));
      await expect(page.getByTestId("algarismos-lembrados")).toBeVisible();
      await legenda(
        page,
        T("Os algarismos da última vez já lá estão", "Last time's digits are already there"),
        3400,
      );
      await clicar(page, page.getByTestId("copiar-ligacao"));
      await legenda(
        page,
        T(
          "«Copiar ligação» cria um endereço com toda a configuração",
          "“Copy link” creates an address with the whole setup",
        ),
        3200,
      );
      await legenda(
        page,
        T(
          "Envie-o à equipa e todos veem o mesmo pedido",
          "Send it to your team and everyone sees the same request",
        ),
        2600,
      );
    },
  },
  {
    id: "partilhar",
    rodar: async (page, T) => {
      await page.goto("/");
      await legenda(page, T("Partilhar o gerador", "Share the generator"), 1800);
      const abrir = page.getByTestId("partilhar-abrir-topo");
      await abrir.scrollIntoViewIfNeeded();
      await legenda(
        page,
        T(
          "No cabeçalho (e depois de gerar) está o botão «Partilhar»",
          "In the header (and after generating) there is a “Share” button",
        ),
        2600,
      );
      await clicar(page, abrir);
      await expect(page.getByTestId("partilhar-whatsapp")).toBeVisible();
      await legenda(
        page,
        T(
          "WhatsApp, Telegram, Facebook, e-mail, ou a partilha do telemóvel",
          "WhatsApp, Telegram, Facebook, e-mail, or your phone's share sheet",
        ),
        1200,
      );
      for (const id of [
        "partilhar-whatsapp",
        "partilhar-telegram",
        "partilhar-facebook",
        "partilhar-email",
      ]) {
        await ir(page, page.getByTestId(id));
        await pausa(page, 700);
      }
      await legenda(
        page,
        T(
          "As ligações só levam o endereço do site: não há rastreio",
          "The links carry only the site address: there is no tracking",
        ),
        2800,
      );
      await clicar(page, page.getByTestId("partilhar-copiar"));
      await legenda(
        page,
        T(
          "«Copiar ligação» põe o endereço na área de transferência",
          "“Copy link” puts the address on the clipboard",
        ),
        2600,
      );
    },
  },
  {
    id: "instalar",
    rodar: async (page, T) => {
      await page.goto("/");
      await legenda(page, T("Instalar como app", "Install as an app"), 1800);
      await page.evaluate(() => {
        const b = document.getElementById("__barra");
        if (b) b.style.display = "flex";
      });
      await legenda(
        page,
        T(
          "No Chrome ou no Edge: clique no botão de instalar da barra de endereços",
          "In Chrome or Edge: click the install button in the address bar",
        ),
        4200,
      );
      await page.evaluate(() => {
        const b = document.getElementById("__barra");
        if (b) b.style.display = "none";
      });
      await legenda(
        page,
        T(
          "No iPhone (Safari): «Partilhar» e «Adicionar ao ecrã principal»",
          "On iPhone (Safari): “Share” then “Add to Home Screen”",
        ),
        4200,
      );
      await legenda(
        page,
        T("Abre numa janela própria e arranca depressa", "It opens in its own window and starts fast"),
        3000,
      );
    },
  },
  {
    id: "visual",
    rodar: async (page, T) => {
      await page.goto("/");
      await legenda(
        page,
        T("Temas visuais e Natal automático", "Visual themes and automatic Christmas"),
        2000,
      );
      await legenda(
        page,
        T("Escolha o tema no seletor do cabeçalho", "Pick the theme in the header selector"),
        1000,
      );
      for (const v of ["halloween", "praia", "jornal", "terminal", "circo", "natal", "premiado"]) {
        await ir(page, page.getByTestId("visual"));
        await page.getByTestId("visual").selectOption(v);
        await pausa(page, 1700);
      }
      await legenda(
        page,
        T(
          "A estrutura é a mesma: só mudam as cores e o aspeto",
          "The layout is the same: only colors and look change",
        ),
        3000,
      );
      await legenda(
        page,
        T("O claro e o escuro são independentes do tema", "Light and dark are independent of the theme"),
        800,
      );
      await page.getByTestId("tema").selectOption("escuro");
      await pausa(page, 2000);
      await page.getByTestId("tema").selectOption("claro");
      await legenda(
        page,
        T("Em dezembro o Natal é o tema automático", "In December, Christmas is the automatic theme"),
        3000,
      );
    },
  },
];

async function gravar(browser: Browser, baseURL: string, cena: Cena, lg: Lg) {
  const dir = join(DESTINO, `.tmp-${cena.id}-${lg}`);
  const contexto = await browser.newContext({
    baseURL,
    locale: lg === "pt" ? "pt-PT" : "en-US",
    viewport: TAMANHO,
    recordVideo: { dir, size: TAMANHO },
    acceptDownloads: true,
  });
  await contexto.addInitScript(PALCO);
  const page = await contexto.newPage();
  const t0 = Date.now();
  if (cena.template) await preparar(page, cena.template[0], cena.template[1]);
  else await page.goto("/");
  await page.evaluate(() => document.fonts.ready);
  const corte = (Date.now() - t0) / 1000; // o vídeo começa aqui: tudo o que está antes era preparação
  await cena.rodar(page, (pt, en) => (lg === "pt" ? pt : en));
  await legenda(page, "", 700);
  const video = page.video();
  await contexto.close();
  const nome = `web_${cena.id}_${lg}`;
  await video?.saveAs(join(DESTINO, `${nome}.webm`));
  await writeFile(join(DESTINO, `${nome}.json`), JSON.stringify({ corte: Math.max(0, corte - 0.2) }));
}

test.describe("vídeos das funcionalidades", () => {
  test.skip(!GRAVAR, "só com GRAVAR_VIDEOS=1 (pnpm videos)");
  test.describe.configure({ mode: "serial" });
  test.setTimeout(240_000);
  const so = process.env.GRAVAR_VIDEOS === "1" ? null : process.env.GRAVAR_VIDEOS?.split(","); // GRAVAR_VIDEOS=series,qr grava só essas
  for (const cena of CENAS) {
    if (so && !so.includes(cena.id)) continue;
    for (const lg of ["pt", "en"] as const) {
      test(`${cena.id} (${lg})`, async ({ browser, baseURL }) => {
        await mkdir(DESTINO, { recursive: true });
        await gravar(browser, baseURL ?? "http://127.0.0.1:8123", cena, lg);
      });
    }
  }
});
