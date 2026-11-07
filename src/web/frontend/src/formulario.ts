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
  const [campos, setCampos] = useState<Campos>(() => ({ ...PADRAO, ...lembrados() }));
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
