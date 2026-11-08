// Um servidor falso (em memória) para os testes: responde às rotas de src/web com os mesmos JSON, sem rede.
import { vi } from "vitest";
import type { Campos, Sessao, Trabalho } from "./api";

export const TEXTOS: Record<string, Record<string, string>> = {
  pt: {
    app_nome: "Gerador de Rifas",
    m_idioma: "Idioma",
    mi_tema: "Tema",
    mi_tema_claro: "Claro",
    mi_tema_escuro: "Escuro",
    web_tema_auto: "Automático",
    web_visual: "Estilo",
    web_termos: "Termos",
    web_privacidade: "Privacidade",
    web_contacto: "Contacto",
    web_donativo: "Donativo",
    web_algarismos_lembrados: "Reutilizámos os algarismos da última vez ({nome}).",
    web_prefixos: "Prefixo ou séries",
    web_prefixos_dica: "Texto antes dos algarismos.",
    web_saltar: "Saltar números",
    web_cor_serie: "Uma cor para cada série",
    web_marcas: "Marcas de corte",
    web_sorteio: "Sorteio",
    web_sorteio_intro: "Sorteie números de forma verificável.",
    web_sorteio_quantos: "Quantos números sortear",
    web_sorteio_semente: "Semente pública",
    web_sorteio_semente_dica: "Escreva algo que ninguém controla.",
    web_sorteio_sortear: "Sortear",
    web_sorteio_resultado: "Números sorteados, pela ordem em que saíram",
    web_sorteio_drand: "Usar a semente do drand",
    web_sorteio_drand_erro: "Não foi possível obter a semente do drand.",
    web_sorteio_como: "Para verificar, repita o sorteio com os mesmos dados.",
    web_sorteio_erro_numeros:
      "Escolha um intervalo válido (até {max} números) e quantos sortear (de 1 a {quantos}).",
    web_sorteio_erro_semente: "Escreva a semente pública (até {max} caracteres).",
    err_saltar: "«Saltar»: escreva números ou intervalos separados por vírgulas.",
    web_cor_numeros: "Cor dos números",
    web_qr: "Código QR de verificação em cada bilhete",
    web_qr_posicao: "Posição do QR",
    web_qr_tamanho: "Tamanho do QR",
    web_logotipo: "Logótipo (PNG ou JPG)",
    web_logo_posicao: "Posição do logótipo",
    web_logo_tamanho: "Tamanho do logótipo",
    web_logo_remover: "Remover logótipo",
    web_galeria: "Sem template? Escolha um da galeria",
    web_galeria_usar: "Usar este template",
    web_galeria_titulo: "Título",
    web_galeria_organizacao: "Organização ou evento",
    web_galeria_premios: "Prémios (uma linha cada, até 3)",
    web_galeria_data: "Data do sorteio",
    web_exportar_csv: "Exportar lista (CSV)",
    web_folha_controlo: "Folha de controlo (PDF)",
    web_copiar_ligacao: "Copiar ligação",
    web_ligacao_copiada: "Ligação copiada.",
    tut_titulo: "Tutorial",
    mi_video: "Vídeo tutorial",
    mi_sobre: "Acerca de…",
    c1_titulo: "Template (PDF)",
    c1_placeholder: "PDF do Canva",
    c1_analisar: "A analisar o template…",
    c2_titulo: "Algarismos",
    c2_placeholder: "PDF, PNG ou JPG",
    c2_analisar: "A analisar os algarismos…",
    c2_ajuda: "Como criar este ficheiro?",
    c3_titulo: "Números",
    c4_titulo: "Destino",
    escolher: "Escolher…",
    de: "De",
    ate: "Até",
    algarismos: "Algarismos",
    modo_varios: "Vários PDFs",
    modo_unico: "Um único PDF",
    max_ficheiro: "Máximo por ficheiro",
    nome_ficheiros: "Nome dos ficheiros",
    nome_placeholder: "Escreva o nome",
    lay_info: "Uma só rifa",
    lay_papel: "Papel",
    lay_margem: "Margem",
    lay_por_folha: "Rifas por folha",
    previa: "Pré-visualizar",
    previa_titulo: "Pré-visualização",
    previa_vazio: "Escolha o template.",
    template_titulo: "Template",
    gerar: "Gerar PDFs",
    cancelar: "Cancelar",
    limpar: "Limpar tudo",
    mi_expandir: "Expandir",
    mi_reduzir: "Reduzir",
    web_descarregar: "Descarregar",
    web_ficheiros_gerados: "PDFs gerados",
    web_nova_janela: "Abrir noutra janela",
    web_voltar: "Voltar",
    web_sessao_expirada: "A sessão expirou.",
    web_erro_rede: "Sem ligação ao servidor.",
    tut_ant: "Anterior",
    tut_seg: "Seguinte",
    video_falta: "Falta {nome}",
    sobre_texto: "{app}\nVersão {versao}\n\nGera PDFs.\n\nUsa X.",
  },
  en: {
    app_nome: "Raffle Generator",
    m_idioma: "Language",
    c1_titulo: "Template (PDF)",
    c2_titulo: "Digits",
    c3_titulo: "Numbers",
    c4_titulo: "Destination",
    gerar: "Generate PDFs",
    cancelar: "Cancel",
    previa: "Preview",
    limpar: "Clear all",
    web_sessao_expirada: "The session expired.",
  },
};

export const CAMPOS_PADRAO: Campos = {
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
  logo_posicao: "sd",
  logo_tamanho: "25",
  cor_numeros: "",
  qr: "",
  qr_posicao: "ie",
  qr_tamanho: "28",
};

const trabalhoLivre = (): Trabalho => ({
  estado: "livre",
  texto: "",
  cor: "suave",
  feitas: 0,
  total: 0,
  registo: [],
  proximo: 0,
  erro: "",
  entrega: null,
});

export interface Pedido {
  metodo: string;
  url: string;
  lingua: string;
  corpo: unknown;
  nome: string;
}

/** O que o servidor falso faz: o teste pode mudar estes campos para simular situações. */
export class ServidorFalso {
  sessoes = new Map<string, Sessao>();
  pedidos: Pedido[] = [];
  proximoId = 1;
  /** a resposta ao próximo PUT de template (um teste pode pôr um erro) */
  respostaTemplate: ((s: Sessao, nome: string) => Sessao) | null = null;
  /** o estado do trabalho a devolver enquanto "gera": uma lista que se vai gastando */
  passos: Trabalho[] = [];
  falhaSessaoPerdida = false;
  donativoUrl = "";
  exportarErro = "";
  galeriaErro = "";
  logotipoErro = "";
  temContacto = false;
  temQr = false;

  nova(): Sessao {
    const id = `sessao${this.proximoId++}`;
    const s: Sessao = {
      sessao: id,
      template: { nome: "", estado: "vazio", texto: "Escolha o PDF do template.", detalhe: "" },
      algarismos: { nome: "", estado: "vazio", texto: "—", detalhe: "" },
      info: null,
      pronto: false,
      tem_modelo: false,
      modelo_url: "",
      previa: null,
      avisos: [],
      logotipo: "",
      trabalho: trabalhoLivre(),
    };
    this.sessoes.set(id, s);
    return s;
  }

  responder(corpo: unknown, estado = 200): Promise<Response> {
    return Promise.resolve(new Response(estado === 204 ? null : JSON.stringify(corpo), { status: estado }));
  }

  manejar = (entrada: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const url = String(entrada);
    const metodo = (init?.method ?? "GET").toUpperCase();
    const cab = (init?.headers ?? {}) as Record<string, string>;
    let corpo: unknown = init?.body;
    if (typeof corpo === "string") corpo = JSON.parse(corpo);
    this.pedidos.push({
      metodo,
      url,
      lingua: cab["X-Lingua"] ?? "",
      corpo,
      nome: decodeURIComponent(cab["X-Nome"] ?? ""),
    });

    if (url === "/health") return this.responder({ estado: "ok", versao: "3.0.0" });
    if (url === "/api/exportar/lista.csv" || url === "/api/exportar/controlo.pdf") {
      if (this.exportarErro) return this.responder({ detail: this.exportarErro, tipo: "aviso" }, 422);
      return Promise.resolve(new Response(new Blob([url.endsWith("csv") ? "csv" : "%PDF"]), { status: 200 }));
    }
    if (url.startsWith("/api/galeria/previa.png")) {
      if (this.galeriaErro) return this.responder({ detail: this.galeriaErro, tipo: "aviso" }, 422);
      return Promise.resolve(new Response(new Blob(["png"]), { status: 200 }));
    }
    if (url === "/api/publico")
      return this.responder({ donativo_url: this.donativoUrl, contacto: this.temContacto, qr: this.temQr });
    const pg = /^\/api\/pagina\/(\w+)$/.exec(url);
    if (pg?.[1])
      return ["termos", "privacidade", "contacto"].includes(pg[1])
        ? this.responder({
            titulo: `Página ${pg[1]}`,
            aviso: "Versão provisória de teste.",
            seccoes: [{ titulo: "Primeira secção", paragrafos: ["Um parágrafo de teste."] }],
          })
        : this.responder({ detail: "x" }, 404);
    if (url === "/api/changelog")
      return this.responder({
        entradas: [
          {
            versao: "3.0.0",
            data: "2026-11-08",
            seccoes: [{ titulo: "Novo", itens: ["Uma novidade de teste."] }],
          },
          {
            versao: "2.9.0",
            data: "2026-10-01",
            seccoes: [{ titulo: "Corrigido", itens: ["Um erro de teste."] }],
          },
        ],
      });
    if (url === "/api/linguas")
      return this.responder({
        por_defeito: "pt",
        linguas: [
          { codigo: "pt", nome: "Português" },
          { codigo: "en", nome: "English" },
        ],
      });
    const t = /^\/api\/textos\/(\w+)$/.exec(url);
    if (t?.[1])
      return TEXTOS[t[1]]
        ? this.responder({ lingua: t[1], textos: { ...TEXTOS.pt, ...TEXTOS[t[1]] } })
        : this.responder({ detail: "x" }, 404);
    if (url === "/api/sessoes" && metodo === "POST") return this.responder(this.nova(), 201);

    const m = /^\/api\/sessoes\/([^/?]+)(?:\/(\w+))?(?:\?.*)?$/.exec(url);
    if (!m?.[1]) return this.responder({ detail: "Rota inexistente" }, 404);
    const [, id, acao] = m;
    const s = this.sessoes.get(id);
    if (!s || this.falhaSessaoPerdida)
      return this.responder({ detail: "Sessão expirada", tipo: "erro" }, 404);

    if (!acao && metodo === "GET") return this.responder(s);
    if (!acao && metodo === "DELETE") {
      this.sessoes.delete(id);
      return this.responder(null, 204);
    }
    if (acao === "template" && metodo === "PUT") {
      const nome = decodeURIComponent(cab["X-Nome"] ?? "");
      const novo = this.respostaTemplate
        ? this.respostaTemplate(s, nome)
        : {
            ...s,
            tem_modelo: true,
            modelo_url: `/api/sessoes/${id}/modelo.pdf`,
            template: { nome, estado: "ok" as const, texto: `✔ 5 bilhetes\n${nome}`, detalhe: "" },
            algarismos: s.algarismos.nome
              ? s.algarismos
              : {
                  nome: "",
                  estado: "precisa" as const,
                  texto: "Falta o ficheiro dos algarismos.",
                  detalhe: "",
                },
            info: { n_campos: 5, primeiro: "0001", ultimo: "0005", digitos: 4, tem_folha: false },
          };
      this.sessoes.set(id, novo);
      return this.responder(novo);
    }
    if (acao === "logotipo" && (metodo === "PUT" || metodo === "DELETE")) {
      if (metodo === "PUT" && this.logotipoErro)
        return this.responder({ detail: this.logotipoErro, tipo: "aviso" }, 422);
      const nome = metodo === "PUT" ? decodeURIComponent(cab["X-Nome"] ?? "") : "";
      const novo: Sessao = { ...s, logotipo: nome };
      this.sessoes.set(id, novo);
      return this.responder(novo);
    }
    if (acao === "galeria" && metodo === "POST") {
      if (this.galeriaErro) return this.responder({ detail: this.galeriaErro, tipo: "aviso" }, 422);
      const d = corpo as { desenho: string };
      const novo: Sessao = {
        ...s,
        pronto: true,
        tem_modelo: true,
        modelo_url: `/api/sessoes/${id}/modelo.pdf`,
        template: {
          nome: `galeria-${d.desenho}.pdf`,
          estado: "ok",
          texto: "✔ 1 bilhete (galeria)",
          detalhe: "",
        },
        algarismos: { nome: "galeria.pdf", estado: "ok", texto: "✔ letra Vera", detalhe: "" },
        info: { n_campos: 1, primeiro: "0001", ultimo: "0001", digitos: 4, tem_folha: true },
      };
      this.sessoes.set(id, novo);
      return this.responder(novo);
    }
    if (acao === "algarismos" && metodo === "PUT") {
      const nome = decodeURIComponent(cab["X-Nome"] ?? "");
      const novo: Sessao = {
        ...s,
        pronto: !!s.info,
        algarismos: { nome, estado: "ok", texto: `✔ imagem ${nome}`, detalhe: "" },
      };
      this.sessoes.set(id, novo);
      return this.responder(novo);
    }
    if (acao === "calcular") {
      const c = corpo as Campos;
      return this.responder({
        folha: null,
        resumo: {
          texto: `${Number(c.fim) - Number(c.inicio) + 1} números`,
          aviso: false,
          max_ativo: c.modo === "varios",
        },
        confirmar: "",
      });
    }
    if (acao === "previa") {
      const novo: Sessao = {
        ...s,
        previa: {
          n: (s.previa?.n ?? 0) + 1,
          titulo: "Pré-visualização · números 1 a 5",
          url: `/api/sessoes/${id}/previa.pdf?n=${(s.previa?.n ?? 0) + 1}`,
        },
      };
      this.sessoes.set(id, novo);
      return this.responder(novo);
    }
    if (acao === "gerar") {
      const primeiro = this.passos[0] ?? { ...trabalhoLivre(), estado: "a_gerar", texto: "A gerar…" };
      const novo: Sessao = { ...s, trabalho: { ...primeiro, estado: "a_gerar" } };
      this.sessoes.set(id, novo);
      return this.responder(novo, 202);
    }
    if (acao === "trabalho") {
      const passo = this.passos.length > 1 ? this.passos.shift() : this.passos[0];
      const tr = passo ?? s.trabalho;
      this.sessoes.set(id, { ...s, trabalho: tr });
      return this.responder(tr);
    }
    if (acao === "cancelar") {
      const tr: Trabalho = { ...s.trabalho, estado: "a_cancelar", texto: "A cancelar…" };
      this.sessoes.set(id, { ...s, trabalho: tr });
      return this.responder(tr);
    }
    return this.responder({ detail: "Rota inexistente" }, 404);
  };

  instalar(): this {
    vi.stubGlobal("fetch", vi.fn(this.manejar));
    return this;
  }

  chamadas(metodo: string, padrao: RegExp): Pedido[] {
    return this.pedidos.filter((p) => p.metodo === metodo && padrao.test(p.url));
  }
}
