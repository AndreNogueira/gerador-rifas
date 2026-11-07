import JavaScriptObfuscator, { type ObfuscatorOptions } from "javascript-obfuscator";
import type { Plugin } from "vite";

/**
 * Ofusca o NOSSO código (`src/`, já em JS) com `javascript-obfuscator`; o React e as outras bibliotecas só são minificados.
 * Só corre em `vite build`.
 *
 * Ofuscar torna o código difícil de ler, NÃO o torna secreto: o que corre no browser é sempre do utilizador. Por isso a lógica
 * sensível (limites, validação, motor) está no servidor. Ofuscar também custa tamanho; ofuscar só o código da app (e não o
 * React) é o que menos pesa. Os níveis e os números medidos estão em `docs/BUNDLE.md`; `OFUSCAR_NIVEL=leve|nenhum pnpm build` troca-o. (O nível «forte», com achatamento do fluxo e código morto, nem compila com o Rolldown.)
 */
const BASE: ObfuscatorOptions = {
  target: "browser",
  compact: true,
  simplify: true,
  sourceMap: false,
  identifierNamesGenerator: "mangled", // nomes curtos (a, b, c…): não aumenta o tamanho
  renameGlobals: false,
  renameProperties: false, // as chaves do JSON da API e as props do React não se podem mudar
  selfDefending: false, // quebra com formatadores
  debugProtection: false,
  disableConsoleOutput: false,
  transformObjectKeys: false,
  numbersToExpressions: false,
  splitStrings: false,
  unicodeEscapeSequence: false,
};

const NIVEIS: Record<string, ObfuscatorOptions> = {
  leve: {
    ...BASE,
    stringArray: true,
    stringArrayThreshold: 0.75,
    stringArrayEncoding: [],
    rotateStringArray: true,
    shuffleStringArray: true,
  },
  medio: {
    ...BASE,
    stringArray: true,
    stringArrayThreshold: 0.9,
    stringArrayEncoding: ["base64"],
    rotateStringArray: true,
    shuffleStringArray: true,
    stringArrayWrappersCount: 1,
    stringArrayWrappersType: "variable",
  },
};

export function ofuscar(): Plugin {
  const nivel = process.env.OFUSCAR_NIVEL ?? "medio";
  let pastaSrc = "";
  /** Só o código da app: `<frontend>/src/**` em JS/TS(X), sem testes nem `node_modules`. */
  const eCodigoDaApp = (id: string) => {
    const caminho = (id.split("?")[0] ?? "").replaceAll("\\", "/");
    return (
      caminho.startsWith(pastaSrc) &&
      !caminho.includes("/node_modules/") &&
      /\.[jt]sx?$/.test(caminho) &&
      !/\.test\./.test(caminho)
    );
  };
  return {
    name: "ofuscar-js",
    apply: "build",
    enforce: "post", // depois de o TypeScript e o JSX virarem JS
    configResolved(config) {
      pastaSrc = `${config.root.replaceAll("\\", "/")}/src/`;
    },
    transform(codigo, id) {
      if (nivel === "nenhum" || !eCodigoDaApp(id)) return null;
      const opcoes = NIVEIS[nivel];
      if (!opcoes)
        throw new Error(`OFUSCAR_NIVEL desconhecido: ${nivel} (nenhum, ${Object.keys(NIVEIS).join(", ")})`);
      return { code: JavaScriptObfuscator.obfuscate(codigo, opcoes).getObfuscatedCode(), map: null };
    },
  };
}
