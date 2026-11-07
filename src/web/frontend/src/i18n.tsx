import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { api, type Lingua } from "./api";

export type Params = Record<string, string | number>;

/** Troca {parametros} pelos valores; o que não vier nos parâmetros fica como está (igual ao `str.format` do motor). */
export function traduzir(textos: Record<string, string>, chave: string, params?: Params): string {
  const texto = textos[chave];
  if (texto === undefined) return chave;
  if (!params) return texto;
  return texto.replace(/\{(\w+)\}/g, (inteiro, nome: string) =>
    nome in params ? String(params[nome]) : inteiro,
  );
}

interface Contexto {
  t: (chave: string, params?: Params) => string;
  lingua: string;
  linguas: Lingua[];
  mudarLingua: (codigo: string) => void;
}

const I18n = createContext<Contexto | null>(null);
const CHAVE = "rifas.lingua";

function lerGuardada(): string | null {
  try {
    return localStorage.getItem(CHAVE);
  } catch {
    return null; // modo privado ou armazenamento bloqueado
  }
}

export function ProvedorI18n({ children }: { children: ReactNode }) {
  const [linguas, setLinguas] = useState<Lingua[]>([]);
  const [lingua, setLingua] = useState<string | null>(null);
  const [textos, setTextos] = useState<Record<string, string> | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    api
      .linguas()
      .then((l) => {
        setLinguas(l.linguas);
        const guardada = lerGuardada();
        setLingua(l.linguas.some((x) => x.codigo === guardada) ? guardada : l.por_defeito);
      })
      .catch((e: Error) => setErro(e.message));
  }, []);

  useEffect(() => {
    if (!lingua) return;
    let atual = true;
    api
      .textos(lingua)
      .then((r) => {
        if (!atual) return;
        setTextos(r.textos);
        document.documentElement.lang = lingua;
        try {
          localStorage.setItem(CHAVE, lingua);
        } catch {
          /* sem armazenamento */
        }
      })
      .catch((e: Error) => {
        if (atual) setErro(e.message);
      });
    return () => {
      atual = false;
    };
  }, [lingua]);

  const valor = useMemo<Contexto | null>(
    () =>
      textos && lingua
        ? { t: (c, p) => traduzir(textos, c, p), lingua, linguas, mudarLingua: setLingua }
        : null,
    [textos, lingua, linguas],
  );

  if (erro) return <p role="alert">Erro / Error: {erro}</p>;
  if (!valor) return <p aria-busy="true">…</p>;
  return <I18n.Provider value={valor}>{children}</I18n.Provider>;
}

export function useI18n(): Contexto {
  const c = useContext(I18n);
  if (!c) throw new Error("useI18n fora do ProvedorI18n");
  return c;
}
