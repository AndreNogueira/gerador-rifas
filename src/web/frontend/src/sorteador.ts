// O sorteio verificável (M7): o mesmo algoritmo de `src/core/sorteio.py` (a referência), feito no browser, sem enviar nada ao servidor.
// 1. números possíveis = os inteiros de `de` a `ate` menos os excluídos, por ordem; 2. um inteiro em [0, m) com o contador c vem de
// SHA-256(semente ":" c ":" j) (8 bytes, com rejeição para não enviesar); 3. baralha-se parcialmente: para i = 0..quantos-1, troca-se
// a posição i com i + r, r em [0, N-i); 4. saem as primeiras posições. Os vetores de `sorteador.test.ts` são os de `tests/test_sorteio.py`.

export const MAX_NUMEROS = 1_000_000;
export const MAX_QUANTOS = 100;
export const MAX_SEMENTE = 200;
export const MAX_EXCLUIR = 50;

const K = [
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98,
  0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
  0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8,
  0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
  0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819,
  0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
  0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
  0xc67178f2,
];

const rotd = (x: number, n: number) => (x >>> n) | (x << (32 - n));

/** SHA-256 em TypeScript puro (síncrono, sem depender de `crypto.subtle`); o teste confere-o com o do Node. */
export function sha256(dados: Uint8Array): Uint8Array {
  const h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
  const n = dados.length;
  const total = (((n + 9 + 63) >> 6) << 6) >>> 0; // com o 0x80 e os 8 bytes do comprimento, em múltiplos de 64
  const m = new Uint8Array(total);
  m.set(dados);
  m[n] = 0x80;
  const vista = new DataView(m.buffer);
  vista.setUint32(total - 8, Math.floor((n * 8) / 2 ** 32), false);
  vista.setUint32(total - 4, (n * 8) >>> 0, false);
  const w = new Uint32Array(64);
  for (let bloco = 0; bloco < total; bloco += 64) {
    for (let i = 0; i < 16; i++) w[i] = vista.getUint32(bloco + i * 4, false);
    for (let i = 16; i < 64; i++) {
      const a = w[i - 15] as number;
      const b = w[i - 2] as number;
      const s0 = rotd(a, 7) ^ rotd(a, 18) ^ (a >>> 3);
      const s1 = rotd(b, 17) ^ rotd(b, 19) ^ (b >>> 10);
      w[i] = ((w[i - 16] as number) + s0 + (w[i - 7] as number) + s1) >>> 0;
    }
    let [a, b, c, d, e, f, g, hh] = h as [number, number, number, number, number, number, number, number];
    for (let i = 0; i < 64; i++) {
      const t1 =
        (hh +
          (rotd(e, 6) ^ rotd(e, 11) ^ rotd(e, 25)) +
          ((e & f) ^ (~e & g)) +
          (K[i] as number) +
          (w[i] as number)) >>>
        0;
      const t2 = ((rotd(a, 2) ^ rotd(a, 13) ^ rotd(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) >>> 0;
      hh = g;
      g = f;
      f = e;
      e = (d + t1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (t1 + t2) >>> 0;
    }
    const novo = [a, b, c, d, e, f, g, hh];
    for (let i = 0; i < 8; i++) h[i] = ((h[i] as number) + (novo[i] as number)) >>> 0;
  }
  const saida = new Uint8Array(32);
  const vs = new DataView(saida.buffer);
  for (let i = 0; i < 8; i++) vs.setUint32(i * 4, h[i] as number, false);
  return saida;
}

const codificador = new TextEncoder();
const DOIS64 = 1n << 64n;

/** Um inteiro em [0, m) sem enviesamento, determinista a partir da semente e do contador. */
function abaixoDe(m: number, semente: Uint8Array, contador: number): number {
  const M = BigInt(m);
  const limite = DOIS64 - (DOIS64 % M);
  for (let j = 0; ; j++) {
    const sufixo = codificador.encode(`:${contador}:${j}`);
    const entrada = new Uint8Array(semente.length + sufixo.length);
    entrada.set(semente);
    entrada.set(sufixo, semente.length);
    const h = sha256(entrada);
    let x = 0n;
    for (let i = 0; i < 8; i++) x = (x << 8n) | BigInt(h[i] as number);
    if (x < limite) return Number(x % M);
  }
}

export type Intervalo = [number, number];

/** «13, 100-110» -> [[13,13],[100,110]]; vazio -> []; algo inválido -> null. */
export function lerExcluir(txt: string): Intervalo[] | null {
  const saida: Intervalo[] = [];
  for (const parte of txt.split(",").map((p) => p.trim())) {
    if (!parte) continue;
    const m = /^(\d{1,9})(?:\s*-\s*(\d{1,9}))?$/.exec(parte);
    if (!m) return null;
    const a = Number(m[1]);
    const b = m[2] === undefined ? a : Number(m[2]);
    if (b < a) return null;
    saida.push([a, b]);
  }
  return saida.length > MAX_EXCLUIR ? null : saida;
}

/** Os números sorteados pela ordem em que saem, ou null se os dados não servem (intervalo, quantidade ou semente inválidos). */
export function sortear(
  de: number,
  ate: number,
  quantos: number,
  semente: string,
  excluir: Intervalo[] = [],
): number[] | null {
  const s = semente.trim();
  if (!s || s.length > MAX_SEMENTE) return null;
  if (!Number.isInteger(de) || !Number.isInteger(ate) || ate < de || ate - de + 1 > MAX_NUMEROS) return null;
  const numeros: number[] = [];
  for (let n = de; n <= ate; n++) if (!excluir.some(([a, b]) => a <= n && n <= b)) numeros.push(n);
  if (!Number.isInteger(quantos) || quantos < 1 || quantos > Math.min(MAX_QUANTOS, numeros.length))
    return null;
  const base = codificador.encode(s);
  for (let i = 0; i < quantos; i++) {
    const r = abaixoDe(numeros.length - i, base, i);
    const a = numeros[i] as number;
    numeros[i] = numeros[i + r] as number;
    numeros[i + r] = a;
  }
  return numeros.slice(0, quantos);
}
