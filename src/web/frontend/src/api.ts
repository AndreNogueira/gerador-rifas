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
  /** O nome do logótipo carregado ("" = nenhum). */
  logotipo: string;
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
  /** Onde fica o logótipo em cada rifa: se | sd | ie | id. */
  logo_posicao: string;
  /** Altura do logótipo em % da rifa (10 a 40). */
  logo_tamanho: string;
  /** «#RRGGBB»: a cor dos números; vazio = a do template. */
  cor_numeros: string;
  /** «1» = um QR de verificação em cada rifa (só templates de uma rifa e com a chave configurada no servidor). */
  qr: string;
  qr_posicao: string;
  qr_tamanho: string;
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
export interface GuiaDeTexto {
  titulo: string;
  intro: string;
  passos: { titulo: string; texto: string }[];
  dicas: string[];
  fim: string;
}
/** Um guia «como fazer» na lista (o índice e as ligações entre guias): o título e o resumo na língua escolhida. */
export interface GuiaNaLista {
  nome: string;
  caminho: string;
  titulo: string;
  resumo: string;
}
/** O catálogo do preçário na língua escolhida (`GET /api/precario/catalogo`): artigos por categoria (com o código do emoji que é a imagem), ocasiões, desenhos, moedas e países. */
export interface PrecarioCatalogo {
  categorias: { id: string; nome: string; artigos: { id: string; nome: string; emoji: string }[] }[];
  ocasioes: { id: string; nome: string; desenho: string; artigos: string[]; meses: number[] }[];
  sugerida: string;
  desenhos: { id: string; nome: string }[];
  moedas: { codigo: string; simbolo: string; decimais: number }[];
  paises: Record<string, string>;
  pais: string;
  moeda: string;
  limites: {
    linhas: number;
    titulo: number;
    subtitulo: number;
    rodape: number;
    nome: number;
    moeda_inventada: number;
  };
  formatos: string[];
}
/** O corpo de `POST /api/precario/{previa.png,pdf,imagem.png}`: os preços vão como o utilizador os escreveu (o servidor lê-os na língua do pedido). */
export interface PedidoPrecario {
  linhas: { artigo: string; nome: string; preco: string; categoria: string; emoji: string }[];
  titulo: string;
  subtitulo: string;
  rodape: string;
  desenho: string;
  formato: string;
  orientacao: string;
  colunas: number;
  imagens: boolean;
  moeda: { codigo?: string; nome?: string; antes?: boolean; decimais?: number };
}
export interface ComentarioPublico {
  id: string;
  /** Segundos desde 1970. */
  criado: number;
  anonimo: boolean;
  /** O nome que a pessoa escolheu mostrar (vazio: anónimo, ou o `visitante`). */
  nome: string;
  /** Sem nome e sem anonimato: o número de «Visitante n.º …» (0 = não se aplica). */
  visitante: number;
  texto: string;
}
export interface ListaComentarios {
  total: number;
  itens: ComentarioPublico[];
  /** Vazio = não há mais comentários; senão passa-se em `antes` para pedir os seguintes. */
  seguinte: string;
}

export interface Publico {
  donativo_url: string;
  contacto: boolean;
  /** O servidor tem a chave que assina os QR dos bilhetes. */
  qr: boolean;
  /** Identificador da AdSense (ca-pub-…): vazio = sem anúncios. */
  anuncios_cliente: string;
  /** Bloco de anúncios: vazio = o script carrega-se mas não se mostra nenhum bloco. */
  anuncios_slot: string;
  /** O editor pode partilhar desenhos por ligação (o servidor tem base de dados). */
  partilha_editor: boolean;
  /** «Reportar problema» está ligado ao GitHub do projeto. */
  problemas: boolean;
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
  video?: string; // o vídeo da funcionalidade (só os tópicos das funcionalidades o têm)
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
  /** O PNG de um desenho da galeria com estes textos (`t`, `o`, os prémios, de 3 a 10, em `p` repetido, e `d`). */
  galeriaPrevia: (
    p: { desenho: string; t: string; o: string; p: string[]; d: string },
    sinal?: AbortSignal,
  ) => {
    const q = new URLSearchParams({ desenho: p.desenho, t: p.t, o: p.o, d: p.d });
    for (const premio of p.p) q.append("p", premio);
    return pedir<Blob>("GET", `/api/galeria/previa.png?${q.toString()}`, { bruto: true, sinal });
  },
  logotipo: (id: string, ficheiro: File) => pedir<Sessao>("PUT", `${s(id)}/logotipo`, { ficheiro }),
  removerLogotipo: (id: string) => pedir<Sessao>("DELETE", `${s(id)}/logotipo`),
  usarGaleria: (id: string, dados: DadosGaleria) =>
    pedir<Sessao>("POST", `${s(id)}/galeria`, { json: dados }),
  /** «Usar este template» do editor: o servidor desenha o PDF do desenho e cria o template e os algarismos na sessão. */
  /** Partilha o desenho (sem imagens) por ligação: devolve o id de `/editor?d=<id>`. Só existe com base de dados (`Publico.partilha_editor`). */
  partilharEditor: (desenho: unknown) =>
    pedir<{ id: string }>("POST", "/api/editor/partilhar", { json: desenho }),
  desenhoPartilhado: (id: string) =>
    pedir<{ desenho: unknown; sem_imagens: boolean }>(
      "GET",
      `/api/editor/partilha/${encodeURIComponent(id)}`,
    ),
  usarEditor: (id: string, desenho: unknown) => pedir<Sessao>("POST", `${s(id)}/editor`, { json: desenho }),
  /** A lista de bilhetes em CSV e a folha de controlo em PDF do pedido que está no formulário. */
  listaCsv: (campos: Campos) => pedir<Blob>("POST", "/api/exportar/lista.csv", { json: campos, bruto: true }),
  folhaDeControlo: (campos: Campos) =>
    pedir<Blob>("POST", "/api/exportar/controlo.pdf", { json: campos, bruto: true }),
  precarioCatalogo: (mes: number) => pedir<PrecarioCatalogo>("GET", `/api/precario/catalogo?mes=${mes}`),
  precarioPrevia: (p: PedidoPrecario, sinal?: AbortSignal) =>
    pedir<Blob>("POST", "/api/precario/previa.png", { json: p, bruto: true, sinal }),
  precarioPdf: (p: PedidoPrecario) => pedir<Blob>("POST", "/api/precario/pdf", { json: p, bruto: true }),
  precarioImagem: (p: PedidoPrecario) =>
    pedir<Blob>("POST", "/api/precario/imagem.png", { json: p, bruto: true }),
  publico: () => pedir<Publico>("GET", "/api/publico"),
  comentarios: (antes = "") =>
    pedir<ListaComentarios>("GET", `/api/comentarios${antes ? `?antes=${encodeURIComponent(antes)}` : ""}`),
  comentar: (c: { texto: string; anonimo: boolean; nome: string; site: string }) =>
    pedir<{ ok: boolean }>("POST", "/api/comentarios", { json: c }),
  reportarProblema: (p: {
    resumo: string;
    descricao: string;
    passos: string;
    tecnica: string;
    pagina: string;
    site: string;
  }) => pedir<{ numero: number }>("POST", "/api/problemas", { json: p }),
  guia: (nome: string) => pedir<GuiaDeTexto>("GET", `/api/guia/${encodeURIComponent(nome)}`),
  guias: () => pedir<{ guias: GuiaNaLista[] }>("GET", "/api/guias"),
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
