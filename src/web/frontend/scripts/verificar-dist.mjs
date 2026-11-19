// Corre no fim de `pnpm build` (depois de `comprimir-dist.mjs`): garante o que prometemos entregar ao browser.
//  - UM só ficheiro de estilos e UM só script ligado no index.html (o principal); só as páginas «preguiçosas» conhecidas (PARTES: painel, editor, sorteio) têm o seu
//    ficheiro `.js` à parte, que o principal carrega quando se vai a elas (`src/preguicoso.ts`);
//  - nenhum mapa (.map) nem <style> embutido nem pré-carregamentos (menos o do pedaço partilhado, COMUNS);
//  - o JS e o CSS têm a versão .br e .gz e descomprimem para o mesmo conteúdo;
//  - com a ofuscação por omissão, o código da app não aparece em claro (ver mais abaixo).
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { brotliDecompressSync, gunzipSync } from "node:zlib";

const dist = new URL("../dist/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const assets = join(dist, "assets");
const ficheiros = readdirSync(assets);
const erros = [];

// as únicas partes que se carregam à parte (o nome do ficheiro leva o da página: `Admin-<hash>.js`); uma parte nova tem de se acrescentar aqui de propósito
const PARTES = ["Admin", "Editor", "Sorteio"];
// o pedaço que o principal e as partes partilham (o runtime do JSX): fica à parte e o index.html liga-o com `modulepreload` (única ligação permitida)
const COMUNS = ["jsx-runtime"];
const css = ficheiros.filter((f) => f.endsWith(".css"));
const todosJs = ficheiros.filter((f) => f.endsWith(".js"));
const comuns = todosJs.filter((f) => COMUNS.some((p) => f.startsWith(`${p}-`)));
const partes = todosJs.filter((f) => PARTES.some((p) => f.startsWith(`${p}-`)));
const js = todosJs.filter((f) => !partes.includes(f) && !comuns.includes(f)); // o principal
if (css.length !== 1) erros.push(`esperava 1 .css em dist/assets e há ${css.length}: ${css.join(", ") || "nenhum"}`);
if (js.length !== 1) erros.push(`esperava 1 .js principal em dist/assets e há ${js.length}: ${js.join(", ") || "nenhum"} (partes permitidas: ${PARTES.join(", ")})`);
for (const p of PARTES) if (partes.filter((f) => f.startsWith(`${p}-`)).length !== 1) erros.push(`falta o ficheiro da página preguiçosa ${p} (ou há mais do que um)`);
const mapas = [...ficheiros, ...readdirSync(dist)].filter((f) => f.endsWith(".map"));
if (mapas.length) erros.push(`não pode haver mapas (.map): ${mapas.join(", ")}`);

// o service worker (PWA): um ficheiro à parte, na raiz, legível e SEM a versão no nome (o registo leva `?v=`); não conta como «um só JS»
// porque as páginas não o carregam como script: só o registam.
if (!readdirSync(dist).includes("sw.js")) erros.push("falta dist/sw.js (o service worker da PWA, de public/sw.js)");

const html = readFileSync(join(dist, "index.html"), "utf8");
const conta = (re) => [...html.matchAll(re)].length;
if (conta(/<link[^>]+rel="stylesheet"[^>]*>/g) !== 1) erros.push("o index.html deve ligar exatamente 1 folha de estilos");
if (conta(/<script[^>]+src="[^"]+"[^>]*>/g) !== 1) erros.push("o index.html deve ligar exatamente 1 script");
for (const f of partes) if (html.includes(f)) erros.push(`o index.html não deve ligar ${f}: carrega-se à parte, quando se abre a página`);
if (/<style[\s>]/.test(html)) erros.push("o index.html não deve ter <style> embutido");
for (const m of html.matchAll(/<link[^>]+rel="modulepreload"[^>]*>/g)) {
  const href = /href="\/assets\/([^"]+)"/.exec(m[0])?.[1] ?? "";
  if (!comuns.includes(href)) erros.push(`o index.html só pode pré-carregar o pedaço partilhado (${COMUNS.join(", ")}), não ${href || m[0]}`);
}

for (const nome of [...css, ...js, ...partes, ...comuns]) {
  const original = readFileSync(join(assets, nome));
  for (const [ext, descomprimir] of [[".br", brotliDecompressSync], [".gz", gunzipSync]]) {
    try {
      const volta = descomprimir(readFileSync(join(assets, nome + ext)));
      if (!volta.equals(original)) erros.push(`${nome}${ext} não descomprime para o original`);
    } catch {
      erros.push(`falta ${nome}${ext} (corre comprimir-dist.mjs)`);
    }
  }
}

// Com a ofuscação por omissão (`medio`: texto da app em base64 numa tabela) uma chave do nosso código, como a do localStorage da
// sessão, não pode aparecer em claro; o Vite minifica depois, por isso procurar `_0x…` não serve.
const nivel = process.env.OFUSCAR_NIVEL ?? "medio";
if (js[0] && nivel === "medio") {
  for (const nome of [...js, ...partes, ...comuns]) {
    const codigo = readFileSync(join(assets, nome), "utf8");
    if (codigo.includes("rifas.sessao")) erros.push(`${nome} não parece ofuscado: a chave «rifas.sessao» do nosso código aparece em claro`);
  }
}

if (erros.length) {
  console.error(`verificar-dist: ${erros.length} problema(s):\n - ${erros.join("\n - ")}`);
  process.exit(1);
}
console.log(`verificar-dist: ok (${js[0]}${partes.length ? ` + ${partes.join(", ")}` : ""}, ${css[0]})`);
