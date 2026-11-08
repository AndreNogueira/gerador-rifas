// Corre depois de `vite build`: escreve ao lado de cada ficheiro de texto de `dist/` a versão comprimida (`.br` e `.gz`), para o
// servidor a entregar já pronta (sem gastar CPU: a instância gratuita tem pouca). O FastAPI escolhe pelo `Accept-Encoding`.
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { brotliCompressSync, constants, gzipSync } from "node:zlib";

const dist = new URL("../dist/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const COMPRIMIVEL = /\.(js|css|svg|webmanifest|json|txt|xml)$/; // o index.html não: o servidor monta-o por rota (SEO)
const MINIMO = 256; // abaixo disto não compensa

let total = 0;
let comprimido = 0;
const ver = (pasta) => {
  for (const nome of readdirSync(pasta)) {
    const caminho = join(pasta, nome);
    if (statSync(caminho).isDirectory()) ver(caminho);
    else if (COMPRIMIVEL.test(nome) && statSync(caminho).size >= MINIMO) {
      const dados = readFileSync(caminho);
      const br = brotliCompressSync(dados, { params: { [constants.BROTLI_PARAM_QUALITY]: 11 } });
      writeFileSync(`${caminho}.br`, br);
      writeFileSync(`${caminho}.gz`, gzipSync(dados, { level: 9 }));
      total += dados.length;
      comprimido += br.length;
    }
  }
};
ver(dist);
console.log(`comprimir-dist: ${(total / 1024).toFixed(0)} KB de texto -> ${(comprimido / 1024).toFixed(0)} KB em brotli`);
