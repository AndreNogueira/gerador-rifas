// Cliente da API do painel de administração. A palavra-passe só viaja no pedido de entrada: o servidor responde com um cookie
// HttpOnly (que o JavaScript nem consegue ler), por isso aqui nunca se guarda nada em localStorage nem em memória.

export interface Sistema {
  cpu: number;
  cpu_nucleos: number;
  mem_servidor_mb: number;
  mem_motor_mb: number;
  mem_contentor_mb: number;
  mem_limite_mb: number | null;
  mem_no_contentor: boolean;
  disco_usado_mb: number;
  disco_livre_mb: number;
  sessoes_ativas: number;
  geracao_em_curso: boolean;
  motor_vivo: boolean;
  motor_reinicios: number;
  python: string;
  plataforma: string;
}
export type VeredictoProxy = "sem_dados" | "poucos_pedidos" | "sem_proxy" | "ok" | "problema";
export interface Estado {
  /** «leitura»: entrou com o CLAUDE_TOKEN (só vê); «admin»: o dono. */
  papel?: "admin" | "leitura";
  versao: string;
  agora: number;
  arranque: number;
  dados_desde: number;
  dados_efemeros: boolean;
  base_de_dados: { tipo: "sqlite" | "postgres"; erro: boolean; intervalo_min: number };
  sistema: Sistema;
  limites: Record<string, number | string>;
  proxy: {
    pedidos: number;
    ips_distintos: number;
    privados_pct: number | null;
    xff_pct: number | null;
    pais_pct: number | null;
    veredicto: VeredictoProxy;
  };
  acordado: {
    ativo: boolean;
    cada_min: number;
    chamadas: number;
    falhas: number;
    ultima_em: number | null;
    ultima_ok: boolean | null;
    ultimo_ms: number;
  };
  intervalos: string[];
}
export interface ErroAssinatura {
  tipo: string;
  rota: string;
  estado: number;
  excecao: string;
  onde: string;
  n: number;
  primeira: number;
  ultima: number;
}
export interface LivroErros {
  intervalo: string;
  desde_arranque: number;
  total: number;
  erros: ErroAssinatura[];
  recentes: { t: number; tipo: string; rota: string; estado: number; excecao: string }[];
}
export interface PontoSistema {
  t: number;
  cpu: number | null;
  mem_servidor: number | null;
  mem_motor: number | null;
  mem_contentor: number | null;
  disco: number | null;
  sessoes: number | null;
  geracoes: number | null;
}
export interface PontoPedidos {
  t: number;
  n: number;
  e4: number;
  e5: number;
  p50: number | null;
  p95: number | null;
}
export interface PontoEventos {
  t: number;
  sessoes: number;
  previas: number;
  geracoes: number;
  paginas: number;
  numeros: number;
}
export interface LinhaPedido {
  pedido: string;
  n: number;
  e4: number;
  e5: number;
  medio_ms: number;
  p50: number | null;
  p95: number | null;
  max_ms: number;
  sondagem: boolean;
}
export interface Contagem {
  chave: string;
  n: number;
}
export interface Resumo {
  sessoes: number;
  previas: { ok: number; erro: number };
  templates: { ok: number; erro: number };
  algarismos: { ok: number; erro: number };
  geracoes: Record<string, number>;
  numeros: number;
  paginas: number;
  descargas: Contagem[];
  funil: Contagem[];
  duracao: { mediana_s: number | null; p95_s: number | null; max_s: number | null; histograma: Contagem[] };
  linguas: Contagem[];
  temas: Contagem[];
  dispositivos: Contagem[];
  /** Códigos ISO de duas letras (`??` = desconhecido): o nome escreve-se no browser. */
  paises: Contagem[];
  paginas_vistas: Contagem[];
  robos: number;
  erros_http: Contagem[];
  falhas: Contagem[];
  classes_de_ecra: Contagem[];
  ecras: Contagem[];
  dispositivos_detalhe: Contagem[];
  janelas: Contagem[];
  toque: Contagem[];
  reinicios_motor: number;
  arranques: number;
}
export interface Dados {
  intervalo: string;
  desde: number;
  passo_s: number;
  sistema: PontoSistema[];
  pedidos: PontoPedidos[];
  eventos: PontoEventos[];
  tabela_pedidos: LinhaPedido[];
  resumo: Resumo;
}

/** Sem sessão de administrador (o servidor responde 404 para não confirmar que o painel existe). */
export interface SerieDiaria {
  nome: string;
  /** Um valor por dia (`null` = sem dados nesse dia). */
  valores: (number | null)[];
  /** Como se resume a série no período. */
  agregado: "soma" | "media" | "max";
}
export interface PainelDiario {
  id: string;
  grupo: string;
  titulo: string;
  explica: string;
  tipo: "barras" | "linhas";
  unidade: string;
  agregado: "soma" | "media" | "max";
  /** «pais»: os nomes das séries são códigos de país a escrever por extenso. */
  rotulos: string;
  series: SerieDiaria[];
}
export interface Evolucao {
  dias: number;
  fuso_min: number;
  /** Os dias de cada valor, `aaaa-mm-dd`, do mais antigo ao de hoje (incompleto). */
  dias_lista: string[];
  retencao: { eventos_dias: number; sistema_dias: number };
  dados_desde: number;
  paineis: PainelDiario[];
}

export interface ComentarioDoDono {
  id: string;
  /** Vazio quando já passaram 90 dias (o IP apaga-se do comentário). */
  ip: string;
  texto: string;
}

export class NaoAutenticado extends Error {}
export class ErroEntrada extends Error {
  constructor(
    readonly estado: number,
    mensagem: string,
  ) {
    super(mensagem);
  }
}

async function ver<T>(url: string): Promise<T> {
  const r = await fetch(url, { credentials: "same-origin", cache: "no-store" });
  if (r.status === 404) throw new NaoAutenticado();
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return (await r.json()) as T;
}

export interface ItemSeo {
  chave: string;
  tipo: "titulo" | "descricao" | "texto";
  rotulo: string;
  padrao: string;
  valor: string | null;
}
export interface VistaSeo {
  lingua: string;
  linguas: string[];
  persistente: boolean;
  erro: boolean;
  limites: { titulo: number; descricao: [number, number]; max: number };
  itens: ItemSeo[];
}

async function pedirJson(url: string, metodo: string, corpo?: unknown): Promise<Response> {
  const r = await fetch(url, {
    method: metodo,
    headers: corpo === undefined ? undefined : { "Content-Type": "application/json" },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
    credentials: "same-origin",
  });
  if (r.status === 404) throw new NaoAutenticado();
  if (!r.ok) {
    let detalhe = `${r.status} ${r.statusText}`;
    try {
      const d = (await r.json()) as { detail?: string };
      if (typeof d.detail === "string") detalhe = d.detail;
    } catch {
      /* sem JSON */
    }
    throw new ErroEntrada(r.status, detalhe);
  }
  return r;
}

export const adminApi = {
  seoVer: (lingua: string) => ver<VistaSeo>(`/api/admin/seo?lingua=${encodeURIComponent(lingua)}`),
  async seoGuardar(chave: string, lingua: string, valor: string): Promise<string> {
    const r = await pedirJson("/api/admin/seo", "PUT", { chave, lingua, valor });
    return ((await r.json()) as { valor: string }).valor;
  },
  async seoRepor(chave: string, lingua: string): Promise<void> {
    await pedirJson(
      `/api/admin/seo?chave=${encodeURIComponent(chave)}&lingua=${encodeURIComponent(lingua)}`,
      "DELETE",
    );
  },
  /** Os comentários como o dono os vê: só o IP e o texto. */
  comentarios: () => ver<{ total: number; itens: ComentarioDoDono[] }>("/api/admin/comentarios"),
  async apagarComentario(id: string): Promise<void> {
    await pedirJson(`/api/admin/comentarios/${encodeURIComponent(id)}`, "DELETE");
  },
  estado: () => ver<Estado>("/api/admin/estado"),
  erros: (intervalo: string) =>
    ver<LivroErros>(`/api/admin/erros?intervalo=${encodeURIComponent(intervalo)}`),
  /** Tudo o que está na base, dia a dia; os dias são os do fuso deste browser. */
  evolucao: (dias: number) =>
    ver<Evolucao>(`/api/admin/evolucao?dias=${dias}&fuso=${-new Date().getTimezoneOffset()}`),
  dados: (intervalo: string) => ver<Dados>(`/api/admin/dados?intervalo=${encodeURIComponent(intervalo)}`),
  async entrar(token: string): Promise<void> {
    const r = await fetch("/api/admin/entrar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
      credentials: "same-origin",
    });
    if (r.ok) return;
    let detalhe = "Não foi possível entrar.";
    try {
      const d = (await r.json()) as { detail?: string };
      if (typeof d.detail === "string") detalhe = d.detail;
    } catch {
      /* sem JSON */
    }
    throw new ErroEntrada(r.status, detalhe);
  },
  async sair(): Promise<void> {
    await fetch("/api/admin/sair", { method: "POST", credentials: "same-origin" });
  },
};
