// Corre no fim de `pnpm build` (depois de `comprimir-dist.mjs`): garante o que prometemos entregar ao browser.
//  - UM só ficheiro de estilos e UM só de JS, cada um ligado uma vez no index.html;
//  - nenhum mapa (.map) nem <style> embutido nem pré-carregamentos;
//  - o JS e o CSS têm a versão .br e .gz e descomprimem para o mesmo conteúdo;
//  - com a ofuscação por omissão, o código da app não aparece em claro (ver mais abaixo).
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { brotliDecompressSync, gunzipSync } from "node:zlib";

const dist = new URL("../dist/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const assets = join(dist, "assets");
const ficheiros = readdirSync(assets);
const erros = [];

const css = ficheiros.filter((f) => f.endsWith(".css"));
const js = ficheiros.filter((f) => f.endsWith(".js"));
if (css.length !== 1) erros.push(`esperava 1 .css em dist/assets e há ${css.length}: ${css.join(", ") || "nenhum"}`);
if (js.length !== 1) erros.push(`esperava 1 .js em dist/assets e há ${js.length}: ${js.join(", ") || "nenhum"}`);
const mapas = [...ficheiros, ...readdirSync(dist)].filter((f) => f.endsWith(".map"));
if (mapas.length) erros.push(`não pode haver mapas (.map): ${mapas.join(", ")}`);

// o service worker (PWA): um ficheiro à parte, na raiz, legível e SEM a versão no nome (o registo leva `?v=`); não conta como «um só JS»
// porque as páginas não o carregam como script: só o registam.
if (!readdirSync(dist).includes("sw.js")) erros.push("falta dist/sw.js (o service worker da PWA, de public/sw.js)");

const html = readFileSync(join(dist, "index.html"), "utf8");
const conta = (re) => [...html.matchAll(re)].length;
if (conta(/<link[^>]+rel="stylesheet"[^>]*>/g) !== 1) erros.push("o index.html deve ligar exatamente 1 folha de estilos");
if (conta(/<script[^>]+src="[^"]+"[^>]*>/g) !== 1) erros.push("o index.html deve ligar exatamente 1 script");
if (/<style[\s>]/.test(html)) erros.push("o index.html não deve ter <style> embutido");
if (/rel="modulepreload"/.test(html)) erros.push("o index.html não deve ter modulepreload (há um só JS)");

for (const nome of [...css, ...js]) {
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
  const codigo = readFileSync(join(assets, js[0]), "utf8");
  if (codigo.includes("rifas.sessao")) erros.push("o JS não parece ofuscado: a chave «rifas.sessao» do nosso código aparece em claro");
}

if (erros.length) {
  console.error(`verificar-dist: ${erros.length} problema(s):\n - ${erros.join("\n - ")}`);
  process.exit(1);
}
console.log(`verificar-dist: ok (${js[0]}, ${css[0]})`);
