// Cliente da API FastAPI (src/web). Os tipos espelham os modelos Pydantic de src/web/modelos.py.
// Todos os textos que o utilizador le vem do servidor ja traduzidos, na lingua do cabecalho X-Lingua.
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

export type Cor = "suave" | "ok" | "aviso" | "erro";

export interface Ficheiro {
  nome: string;
  estado: "vazio" | "precisa" | "ok" | "erro";
  texto: string;
  detalhe: string;
}
export interface InfoTemplate {
  n_campos: number;
  primeiro: string;
  ultimo: string;
  digitos: number;
  tem_folha: boolean;
}
export interface PreviaInfo {
  n: number;
  titulo: string;
  url: string;
}
export interface EntregaInfo {
  tipo: "pdf" | "zip";
  nome: string;
  ficheiros: string[];
  total: number;
  url: string;
}
export type EstadoTrabalho = "livre" | "a_gerar" | "a_cancelar" | "ok" | "erros" | "cancelado" | "falhou";
export interface Trabalho {
  estado: EstadoTrabalho;
  texto: string;
  cor: Cor;
  feitas: number;
  total: number;
  registo: string[];
  proximo: number;
  erro: string;
  entrega: EntregaInfo | null;
}
export interface Sessao {
  sessao: string;
  template: Ficheiro;
  algarismos: Ficheiro;
  info: InfoTemplate | null;
  pronto: boolean;
  tem_modelo: boolean;
  modelo_url: string;
  previa: PreviaInfo | null;
  avisos: string[];
  trabalho: Trabalho;
}

/** O que o utilizador escreveu nos cartoes 3 e 4 e no painel da folha. */
export interface Campos {
  nome: string;
  inicio: string;
  fim: string;
  digitos: string;
  modo: "varios" | "unico";
  max_ficheiro: string;
  papel: string;
  margem: string;
  porfolha: string;
  /** Prefixo («A-») ou séries («A-, B-, C-»); vazio = sem prefixo. */
  prefixos: string;
  /** Números ou intervalos que nunca se imprimem («13, 100-110»). */
  saltar: string;
  /** «1» = uma cor para cada série. */
  cor_serie: string;
  /** «1» = marcas de corte nas margens da folha (só templates de uma rifa). */
  marcas: string;
}
export interface FolhaInfo {
  ativa: boolean;
  texto: string;
  aviso: boolean;
  erro: boolean;
  n: number;
  maximo: number;
}
export interface Calculo {
  folha: FolhaInfo | null;
  resumo: { texto: string; aviso: boolean; max_ativo: boolean };
  confirmar: string;
}

export interface DadosGaleria {
  desenho: string;
  titulo: string;
  organizacao: string;
  premios: string[];
  data: string;
}

export interface EntradaChangelog {
  versao: string;
  data: string;
  seccoes: { titulo: string; itens: string[] }[];
}

export interface PaginaDeTexto {
  titulo: string;
  aviso: string;
  seccoes: { titulo: string; paragrafos: string[] }[];
}
export interface Publico {
  donativo_url: string;
  contacto: boolean;
}

export interface Imagem {
  url: string;
  largura: number | null;
}
export interface Topico {
  menu: string;
  titulo: string;
  texto: string;
  imagens: Imagem[];
}
export interface Tutorial {
  topicos: Topico[];
  video: string;
}

/** Erro devolvido pelo servidor, com texto pronto a mostrar. `tipo`: «aviso» (o utilizador pode corrigir) ou «erro». */
export class ErroApi extends Error {
  constructor(
    readonly estado: number,
    mensagem: string,
    readonly tipo: "aviso" | "erro" = "erro",
  ) {
    super(mensagem);
  }
}

/** Nao houve resposta (sem rede, servidor a reiniciar). */
export class ErroRede extends Error {}

let linguaAtual = "";
export function definirLingua(lingua: string): void {
  linguaAtual = lingua;
}

// O tema visual escolhido: só vai ao servidor (cabeçalho X-Visual) para a estatística de que temas se usam; nunca muda nada.
let visualAtual = "";
export function definirVisual(visual: string): void {
  visualAtual = visual;
}

interface Opcoes {
  /** Devolve o corpo como Blob (descarregar um ficheiro) em vez de JSON. */
  bruto?: boolean;
  json?: unknown;
  ficheiro?: File;
  sinal?: AbortSignal;
}

async function pedir<T>(metodo: string, url: string, opcoes: Opcoes = {}): Promise<T> {
  const cabecalhos: Record<string, string> = {};
  if (linguaAtual) cabecalhos["X-Lingua"] = linguaAtual;
  if (visualAtual) cabecalhos["X-Visual"] = visualAtual;
  let corpo: BodyInit | undefined;
  if (opcoes.json !== undefined) {
    cabecalhos["Content-Type"] = "application/json";
    corpo = JSON.stringify(opcoes.json);
  } else if (opcoes.ficheiro) {
    cabecalhos["Content-Type"] = "application/octet-stream";
    cabecalhos["X-Nome"] = encodeURIComponent(opcoes.ficheiro.name);
    corpo = opcoes.ficheiro; // o corpo vai em bruto (sem multipart): o servidor corta-o ao tamanho maximo
  }
  let r: Response;
  try {
    r = await fetch(url, { method: metodo, headers: cabecalhos, body: corpo, signal: opcoes.sinal });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new ErroRede();
  }
  if (!r.ok) {
    let detalhe = r.statusText;
    let tipo: "aviso" | "erro" = "erro";
    try {
      const d = (await r.json()) as { detail?: unknown; tipo?: "aviso" | "erro" };
      if (typeof d.detail === "string") detalhe = d.detail;
      if (d.tipo === "aviso" || d.tipo === "erro") tipo = d.tipo;
    } catch {
      /* resposta sem JSON (p.ex. um erro do proxy) */
    }
    throw new ErroApi(r.status, detalhe, tipo);
  }
  if (r.status === 204) return undefined as T;
  if (opcoes.bruto) return (await r.blob()) as T;
  return (await r.json()) as T;
}

const s = (id: string) => `/api/sessoes/${encodeURIComponent(id)}`;

export const api = {
  saude: () => pedir<Saude>("GET", "/health"),
  linguas: () => pedir<Linguas>("GET", "/api/linguas"),
  textos: (lingua: string) => pedir<Textos>("GET", `/api/textos/${encodeURIComponent(lingua)}`),
  tutorial: () => pedir<Tutorial>("GET", "/api/tutorial"),
  /** O PNG de um desenho da galeria com estes textos (`t`, `o`, `p1`..`p3`, `d`). */
  galeriaPrevia: (p: Record<string, string>, sinal?: AbortSignal) =>
    pedir<Blob>("GET", `/api/galeria/previa.png?${new URLSearchParams(p).toString()}`, {
      bruto: true,
      sinal,
    }),
  usarGaleria: (id: string, dados: DadosGaleria) =>
    pedir<Sessao>("POST", `${s(id)}/galeria`, { json: dados }),
  /** A lista de bilhetes em CSV e a folha de controlo em PDF do pedido que está no formulário. */
  listaCsv: (campos: Campos) => pedir<Blob>("POST", "/api/exportar/lista.csv", { json: campos, bruto: true }),
  folhaDeControlo: (campos: Campos) =>
    pedir<Blob>("POST", "/api/exportar/controlo.pdf", { json: campos, bruto: true }),
  publico: () => pedir<Publico>("GET", "/api/publico"),
  pagina: (nome: string) => pedir<PaginaDeTexto>("GET", `/api/pagina/${encodeURIComponent(nome)}`),
  changelog: () => pedir<{ entradas: EntradaChangelog[] }>("GET", "/api/changelog"),
  criarSessao: () => pedir<Sessao>("POST", "/api/sessoes"),
  sessao: (id: string, desde = 0) => pedir<Sessao>("GET", `${s(id)}?desde=${desde}`),
  apagarSessao: (id: string) => pedir<void>("DELETE", s(id)),
  template: (id: string, ficheiro: File) => pedir<Sessao>("PUT", `${s(id)}/template`, { ficheiro }),
  algarismos: (id: string, ficheiro: File) => pedir<Sessao>("PUT", `${s(id)}/algarismos`, { ficheiro }),
  calcular: (id: string, campos: Campos, sinal?: AbortSignal) =>
    pedir<Calculo>("POST", `${s(id)}/calcular`, { json: campos, sinal }),
  previa: (id: string, campos: Campos) => pedir<Sessao>("POST", `${s(id)}/previa`, { json: campos }),
  gerar: (id: string, campos: Campos) => pedir<Sessao>("POST", `${s(id)}/gerar`, { json: campos }),
  trabalho: (id: string, desde: number) => pedir<Trabalho>("GET", `${s(id)}/trabalho?desde=${desde}`),
  cancelar: (id: string) => pedir<Trabalho>("POST", `${s(id)}/cancelar`),
};
