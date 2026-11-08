import { useCallback, useEffect, useRef, useState } from "react";
import { api, type Calculo, type Campos, type Sessao } from "./api";
import { useI18n } from "./i18n";

export const PAPEIS = ["A4", "A3", "A5", "Letter", "Legal"] as const;

/** Os valores iniciais são os da app Windows. */
export const PADRAO: Campos = {
  nome: "",
  inicio: "1",
  fim: "1000",
  digitos: "4",
  modo: "varios",
  max_ficheiro: "300",
  papel: "A4",
  margem: "5",
  porfolha: "",
  prefixos: "",
  saltar: "",
  cor_serie: "",
  marcas: "",
};

// O que se lembra entre visitas. NUNCA o nome dos ficheiros (cada rifa tem o seu) nem os algarismos/folha (vêm do template).
const LEMBRAR = ["inicio", "fim", "modo", "max_ficheiro", "papel", "margem"] as const;
const CHAVE = "rifas.campos";

function lembrados(): Partial<Campos> {
  try {
    const d = JSON.parse(localStorage.getItem(CHAVE) ?? "{}") as Record<string, unknown>;
    const saida: Record<string, string> = {};
    for (const k of LEMBRAR) {
      const v = d[k];
      if (typeof v === "string" && v.length <= 20) saida[k] = v;
    }
    if (saida.modo !== undefined && saida.modo !== "varios" && saida.modo !== "unico") delete saida.modo;
    return saida as Partial<Campos>;
  } catch {
    return {};
  }
}

/** Os campos que vão na ligação para partilhar (nunca ficheiros; os algarismos e a folha vêm do template). */
const NA_LIGACAO = {
  de: "inicio",
  ate: "fim",
  modo: "modo",
  max: "max_ficheiro",
  papel: "papel",
  margem: "margem",
  nome: "nome",
  pre: "prefixos",
  saltar: "saltar",
  cor: "cor_serie",
  mc: "marcas",
} as const satisfies Record<string, keyof Campos>;

/** A ligação (`/?de=1&ate=100&…`) que repõe estes valores noutro browser. `base` = o endereço do site, com barra final. */
export function ligacaoDosCampos(campos: Campos, base: string): string {
  const p = new URLSearchParams();
  for (const [curto, campo] of Object.entries(NA_LIGACAO)) {
    const v = campos[campo as keyof Campos];
    if (v !== "") p.set(curto, v);
  }
  return `${base}?${p.toString()}`;
}

/** Lê uma ligação partilhada: só valores que o formulário aceitaria; tudo o resto ignora-se (o servidor valida outra vez). */
export function camposDaLigacao(pesquisa: string): Partial<Campos> {
  const p = new URLSearchParams(pesquisa);
  const saida: Partial<Campos> = {};
  const numero = (v: string | null, max: number) =>
    v !== null && /^\d{1,9}$/.test(v) && v.length <= max ? v : null;
  const de = numero(p.get("de"), 9);
  const ate = numero(p.get("ate"), 9);
  const maximo = numero(p.get("max"), 9);
  const margem = numero(p.get("margem"), 3);
  if (de) saida.inicio = de;
  if (ate) saida.fim = ate;
  if (maximo) saida.max_ficheiro = maximo;
  if (margem) saida.margem = margem;
  const modo = p.get("modo");
  if (modo === "varios" || modo === "unico") saida.modo = modo;
  const papel = p.get("papel");
  if (papel && (PAPEIS as readonly string[]).includes(papel)) saida.papel = papel;
  const prefixos = p.get("pre");
  if (prefixos && /^[A-Za-z .\-/,]{1,120}$/.test(prefixos)) saida.prefixos = prefixos;
  const saltar = p.get("saltar");
  if (saltar && /^[0-9 ,-]{1,300}$/.test(saltar)) saida.saltar = saltar;
  if (p.get("cor") === "1") saida.cor_serie = "1";
  if (p.get("mc") === "1") saida.marcas = "1";
  const nome = p.get("nome");
  if (nome && nome.length <= 80 && [...nome].every((c) => c >= " " && c !== "<" && c !== ">"))
    saida.nome = nome; // sem controlo nem HTML
  return saida;
}

/** O que a ligação trouxe, lido uma única vez ao arrancar (e logo apagado do endereço). */
function daLigacaoDeArranque(): Partial<Campos> {
  try {
    if (window.location.pathname !== "/" || !window.location.search) return {};
    const campos = camposDaLigacao(window.location.search);
    window.history.replaceState(null, "", window.location.pathname);
    return campos;
  } catch {
    return {};
  }
}

export interface Formulario {
  campos: Campos;
  /** O painel da folha e o resumo, calculados pelo servidor (null até chegar o primeiro). */
  calculo: Calculo | null;
  mudar: (campo: keyof Campos, valor: string) => void;
  /** «Limpar tudo»: volta aos valores iniciais. */
  reiniciar: () => void;
}

export function useFormulario(sessao: Sessao | null): Formulario {
  const { lingua } = useI18n();
  const [campos, setCampos] = useState<Campos>(() => ({
    ...PADRAO,
    ...lembrados(),
    ...daLigacaoDeArranque(),
  }));
  const [calculo, setCalculo] = useState<Calculo | null>(null);
  const visto = useRef("");

  useEffect(() => {
    try {
      localStorage.setItem(CHAVE, JSON.stringify(Object.fromEntries(LEMBRAR.map((k) => [k, campos[k]]))));
    } catch {
      /* sem armazenamento */
    }
  }, [campos]);

  // Template novo: os algarismos passam a ser os do desenho (0001 -> 4) e a folha volta ao máximo.
  const digitos = sessao?.info?.digitos;
  const chaveTemplate = sessao?.info
    ? `${sessao.template.nome}|${sessao.info.primeiro}|${sessao.info.n_campos}`
    : "";
  useEffect(() => {
    if (!chaveTemplate) {
      visto.current = "";
      return;
    }
    if (chaveTemplate !== visto.current) {
      visto.current = chaveTemplate;
      setCampos((c) => ({ ...c, digitos: String(digitos), porfolha: "" }));
    }
  }, [chaveTemplate, digitos]);

  // O resumo e a folha recalculam-se a cada alteração (com uma pequena espera para não pedir a cada tecla).
  const id = sessao?.sessao;
  const gatilho = `${lingua}|${chaveTemplate}`; // outra língua ou outro template: o texto e os bilhetes por página mudam
  useEffect(() => {
    if (!id || !gatilho) return;
    const controlo = new AbortController();
    const espera = setTimeout(() => {
      api
        .calcular(id, campos, controlo.signal)
        .then(setCalculo)
        .catch(() => {
          /* um cálculo perdido não é um erro: o seguinte corrige */
        });
    }, 250);
    return () => {
      clearTimeout(espera);
      controlo.abort();
    };
  }, [id, campos, gatilho]);

  const mudar = useCallback(
    (campo: keyof Campos, valor: string) => setCampos((c) => ({ ...c, [campo]: valor })),
    [],
  );
  const reiniciar = useCallback(() => setCampos({ ...PADRAO }), []);
  return { campos, calculo, mudar, reiniciar };
}
