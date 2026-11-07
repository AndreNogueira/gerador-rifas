// Cliente da API FastAPI (src/web/app.py). Os tipos espelham os modelos Pydantic.
export interface Lingua {
  codigo: string;
  nome: string;
}
export interface Linguas {
  por_defeito: string;
  linguas: Lingua[];
}
export interface Textos {
  lingua: string;
  textos: Record<string, string>;
}
export interface Saude {
  estado: string;
  versao: string;
}

export class ErroApi extends Error {
  constructor(
    readonly estado: number,
    mensagem: string,
  ) {
    super(mensagem);
  }
}

async function obter<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) {
    let detalhe = r.statusText;
    try {
      detalhe = ((await r.json()) as { detail?: string }).detail ?? detalhe;
    } catch {
      /* resposta sem JSON */
    }
    throw new ErroApi(r.status, detalhe);
  }
  return (await r.json()) as T;
}

export const api = {
  saude: () => obter<Saude>("/health"),
  linguas: () => obter<Linguas>("/api/linguas"),
  textos: (lingua: string) => obter<Textos>(`/api/textos/${encodeURIComponent(lingua)}`),
};
