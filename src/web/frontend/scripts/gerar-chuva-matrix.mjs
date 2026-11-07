// Gera `src/estilos/assets/matrix-chuva.svg`: um mosaico (220×400) de colunas de caracteres a cair, para o tema «Matrix Gamer».
// Determinístico (mesma semente = mesmo SVG). Uso: `node scripts/gerar-chuva-matrix.mjs`.
// O mosaico repete-se na vertical sem emenda: cada caracter é desenhado em `y mod 400` e a opacidade depende só da sua posição no rasto.
import { writeFileSync } from "node:fs";

const L = 220; // largura
const A = 400; // altura
const PASSO = 20; // altura de cada caracter
const COLUNAS = 10;
const CARACTERES = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789Z:.=*+<>|";

let semente = 1337;
const aleatorio = () => {
  semente = (semente * 1664525 + 1013904223) % 4294967296;
  return semente / 4294967296;
};

const linhas = [];
for (let c = 0; c < COLUNAS; c++) {
  const x = c * (L / COLUNAS) + 3;
  const comprimento = 8 + Math.floor(aleatorio() * 9); // 8 a 16 caracteres
  const cabeca = Math.floor(aleatorio() * (A / PASSO)); // linha da «cabeça» do rasto
  for (let i = 0; i < comprimento; i++) {
    const y = ((cabeca - i + A / PASSO) % (A / PASSO)) * PASSO + PASSO - 4;
    const ch = CARACTERES[Math.floor(aleatorio() * CARACTERES.length)];
    const escapado = ch === "<" ? "&lt;" : ch === ">" ? "&gt;" : ch; // o XML não aceita < nem > soltos
    const opacidade = i === 0 ? 1 : Math.max(0.08, 0.85 - (i / comprimento) * 0.8);
    const cor = i === 0 ? "#d8ffe3" : "#00ff66";
    linhas.push(`<text x="${x.toFixed(1)}" y="${y}" fill="${cor}" fill-opacity="${opacidade.toFixed(2)}">${escapado}</text>`);
  }
}

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${L}" height="${A}" viewBox="0 0 ${L} ${A}"><g font-family="'MS Gothic','Yu Gothic','Noto Sans Mono CJK JP',monospace" font-size="17">${linhas.join("")}</g></svg>\n`;
writeFileSync(new URL("../src/estilos/assets/matrix-chuva.svg", import.meta.url), svg);
console.log(`matrix-chuva.svg: ${svg.length} bytes, ${linhas.length} caracteres`);
