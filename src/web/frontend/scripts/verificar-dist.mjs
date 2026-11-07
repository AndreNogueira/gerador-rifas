// Corre depois de `vite build` (faz parte de `pnpm build`): garante o que prometemos entregar ao browser.
// Hoje: UM só ficheiro de estilos e o index.html a ligar exatamente um. (O JS único, sem mapas, junta-se noutro PR.)
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const dist = new URL("../dist/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const assets = join(dist, "assets");
const ficheiros = readdirSync(assets);
const erros = [];

const css = ficheiros.filter((f) => f.endsWith(".css"));
if (css.length !== 1) erros.push(`esperava 1 ficheiro .css em dist/assets e há ${css.length}: ${css.join(", ") || "nenhum"}`);

const html = readFileSync(join(dist, "index.html"), "utf8");
const ligacoes = [...html.matchAll(/<link[^>]+rel="stylesheet"[^>]*>/g)];
if (ligacoes.length !== 1) erros.push(`o index.html deve ligar 1 folha de estilos e liga ${ligacoes.length}`);
if (/<style[\s>]/.test(html)) erros.push("o index.html não deve ter <style> embutido");

if (erros.length) {
  console.error(`verificar-dist: ${erros.length} problema(s):\n - ${erros.join("\n - ")}`);
  process.exit(1);
}
console.log(`verificar-dist: ok (${css[0]})`);
