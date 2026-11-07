// Mede o tamanho do JS e do CSS de `dist/assets` (bruto, gzip e brotli). Uso: `node scripts/medir-js.mjs [rótulo]`.
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { brotliCompressSync, constants, gzipSync } from "node:zlib";

const pasta = new URL("../dist/assets/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const rotulo = process.argv[2] ?? "";
const kb = (n) => `${(n / 1024).toFixed(1)} KB`;
for (const nome of readdirSync(pasta).filter((f) => /\.(js|css)$/.test(f))) {
  const dados = readFileSync(join(pasta, nome));
  const br = brotliCompressSync(dados, { params: { [constants.BROTLI_PARAM_QUALITY]: 11 } });
  console.log(`${rotulo.padEnd(8)} ${nome.padEnd(28)} bruto ${kb(dados.length).padStart(9)}  gzip ${kb(gzipSync(dados, { level: 9 }).length).padStart(8)}  brotli ${kb(br.length).padStart(8)}`);
}
