import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { api, definirLingua, type Lingua } from "./api";
import { definirLinguaDaRota, linguaDoCaminho } from "./rota";

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
  /** A língua dos textos que já chegaram (muda só quando os textos novos estão prontos). */
  lingua: string;
  linguas: Lingua[];
  mudarLingua: (codigo: string) => void;
}

const I18n = createContext<Contexto | null>(null);

export function ProvedorI18n({ children }: { children: ReactNode }) {
  const [linguas, setLinguas] = useState<Lingua[]>([]);
  const [linguasProntas, setLinguasProntas] = useState(false);
  // a língua do URL (`/en/tutorial`) manda; sem prefixo é sempre português (`rota.tsx`): nunca a guardada nem a do
  // browser/servidor, senão um robô ou um browser sem Accept-Language em português acabava a ver a página em inglês
  // e o URL era reescrito sozinho (ver `docs/SEO.md`). `linguaDoCaminho()` lê uma lista fixa no próprio ficheiro
  // (`LINGUAS_COM_PREFIXO`, testada contra a do servidor), por isso decide-se já aqui, sem esperar por `/api/linguas`:
  // isso deixa pedir `/api/textos/<lingua>` em paralelo com `/api/linguas`, em vez de só a seguir a ela resolver
  // (antes era em série, ~0.6 s perdidos no LCP). A app só se mostra quando as duas tiverem respondido (abaixo,
  // `linguasProntas && carregados`): sem isso o cabeçalho chegou a montar-se com o seletor de línguas ainda vazio
  // (zero <option>), por um instante, sempre que `/api/textos` respondia primeiro — um teste de contraste apanhou-o.
  const [escolhida, setEscolhida] = useState<string>(() => linguaDoCaminho() ?? "pt");
  const [carregados, setCarregados] = useState<{ lingua: string; textos: Record<string, string> } | null>(
    null,
  );
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    api
      .linguas()
      .then((l) => setLinguas(l.linguas))
      .catch((e: Error) => setErro(e.message))
      .finally(() => setLinguasProntas(true));
  }, []);

  useEffect(() => {
    let atual = true;
    api
      .textos(escolhida)
      .then((r) => {
        if (!atual) return;
        definirLingua(r.lingua); // antes de os componentes pedirem à API na língua nova
        document.documentElement.lang = r.lingua.replace(
          /-([a-z]{2})$/,
          (_, regiao: string) => `-${regiao.toUpperCase()}`,
        ); // pt-br → pt-BR
        definirLinguaDaRota(r.lingua); // o URL passa a ter o prefixo desta língua
        setCarregados({ lingua: r.lingua, textos: r.textos });
      })
      .catch((e: Error) => {
        if (atual) setErro(e.message);
      });
    return () => {
      atual = false;
    };
  }, [escolhida]);

  const valor = useMemo<Contexto | null>(
    () =>
      carregados && linguasProntas
        ? {
            t: (c, p) => traduzir(carregados.textos, c, p),
            lingua: carregados.lingua,
            linguas,
            mudarLingua: setEscolhida,
          }
        : null,
    [carregados, linguasProntas, linguas],
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
