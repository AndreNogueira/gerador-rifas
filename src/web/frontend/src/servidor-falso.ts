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
    web_donativo_chamada: "Foi útil? Ajude a manter o serviço gratuito com um donativo.",
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
    web_galeria_premios: "Prémios (uma linha cada)",
    web_galeria_n_premios: "Quantos prémios",
    web_galeria_data: "Data do sorteio",
    web_publicidade: "Publicidade",
    web_changelog_windows: "Descarregar a app Windows (.exe)",
    web_como_fazer: "Como fazer",
    m_ajuda: "Ajuda",
    web_menu: "Menu",
    web_comentarios: "Comentários",
    web_precario: "Preçário",
    web_precario_titulo: "Gerador de preçários para festas",
    web_precario_intro: "Escolha os artigos, escreva os preços e imprima.",
    web_precario_ocasiao: "Ocasião e tema",
    web_precario_sugerida: "Sugerido para esta época",
    web_precario_artigos: "Artigos",
    web_precario_pesquisar: "Procurar artigos…",
    web_precario_meu_artigo: "Acrescentar um artigo meu",
    web_precario_nome_artigo: "Nome do artigo",
    web_precario_escolhidos: "Preços ({n} artigos)",
    web_precario_preco: "Preço",
    web_precario_tirar: "Tirar",
    web_precario_dica_preco: "Sem preço, fica um traço.",
    web_precario_moeda: "País e moeda",
    web_precario_pais: "País",
    web_precario_moeda_inventada: "Moeda inventada",
    web_precario_inventada_nome: "Nome da moeda",
    web_vales_titulo: "Vales numerados",
    web_vales_intro: "Com uma moeda inventada, faça também os vales.",
    web_vales_singular: "Nome no singular",
    web_vales_quantidade: "Unidades em cada vale (1 a 99)",
    web_vales_cabecalho: "Título do vale",
    web_vales_cabecalho_padrao: "VALE",
    web_vales_nota: "Nota (opcional)",
    web_vales_criar: "Criar vales numerados",
    web_vales_previa: "Pré-visualização do vale",
    web_precario_inventada_antes: "Escrever antes do número",
    web_precario_inventada_casas: "Casas decimais",
    web_precario_aspeto: "Aspeto",
    web_precario_campo_titulo: "Título",
    web_precario_campo_subtitulo: "Subtítulo",
    web_precario_campo_rodape: "Rodapé",
    web_precario_formato: "Formato",
    web_precario_vertical: "Vertical",
    web_precario_horizontal: "Horizontal",
    web_precario_colunas: "Colunas",
    web_precario_auto: "Automático",
    web_precario_imagens: "Com imagens",
    web_precario_cartoes: "Cartões de mesa (4 por folha A4)",
    web_precario_partilha_ok: "Ligação copiada. O preçário fica guardado 90 dias.",
    web_precario_ligacao_invalida: "Esta ligação já não existe ou o preçário expirou.",
    web_precario_foto: "Foto",
    web_precario_foto_tirar: "Tirar a foto",
    web_precario_fotos_dica: "Pode pôr a sua foto em cada artigo.",
    err_editor_imagem: "A imagem não presta.",
    web_precario_tamanhos: "Dois tamanhos (dois preços por artigo)",
    web_precario_rotulos: "Nomes dos dois tamanhos",
    web_precario_tamanho_1: "Pequeno",
    web_precario_tamanho_2: "Grande",
    web_precario_previa: "Pré-visualização do preçário",
    web_precario_pdf: "Descarregar PDF",
    web_precario_imagem: "Descarregar imagem",
    web_precario_vazio: "Escolha pelo menos um artigo.",
    web_precario_recomecar: "Recomeçar",
    web_precario_a_desenhar: "A desenhar…",
    web_precario_preco_categoria: "Preço da categoria",
    web_comofazer_titulo: "Como fazer uma rifa: guias passo a passo",
    web_comofazer_intro: "Guias passo a passo para organizar a sua rifa.",
    web_guias_outros: "Outros guias",
    web_guia_todos: "Todos os guias",
    web_convite_texto: "Gostou? Diga-nos o que achou.",
    web_convite_botao: "Deixar um comentário",
    web_convite_depois: "Agora não",
    web_reportar: "Reportar problema",
    web_op_titulo: "Deixe o seu comentário",
    web_op_intro:
      "Diga-nos o que acha do {app}: o que correu bem, o que falta e o que podemos melhorar. Lemos tudo.",
    web_op_texto: "O seu comentário",
    web_op_anonimo: "Quero ficar anónimo(a)",
    web_op_com_nome: "Mostrar um nome junto ao comentário",
    web_op_nome: "Nome a mostrar",
    web_op_nome_ajuda: "Pode ser um apelido. Se o deixar em branco, aparece «Visitante n.º …».",
    web_op_aviso_pais:
      "Guardamos apenas o país de onde envia o comentário (nunca o endereço IP), e só o responsável do site o vê. Ver a Política de privacidade.",
    web_op_enviar: "Enviar comentário",
    web_op_obrigado: "Obrigado! O seu comentário já aparece na página de comentários.",
    web_op_curto: "Escreva pelo menos 5 letras.",
    web_erro_envios: "Enviou muitas mensagens seguidas. Tente outra vez daqui a pouco.",
    web_com_intro: "O que as pessoas dizem do {app}. Os comentários anónimos aparecem sem nome.",
    web_com_vazio: "Ainda não há comentários. Seja a primeira pessoa!",
    web_com_anonimo: "Anónimo(a)",
    web_com_visitante: "Visitante n.º {n}",
    web_com_escrever: "Deixar um comentário",
    web_com_mais: "Ver mais comentários",
    web_bug_titulo: "Reportar um problema",
    web_bug_intro:
      "Encontrou um erro? Descreva-o e, ao carregar em «Abrir», criamos um registo diretamente no GitHub do projeto para o corrigirmos.",
    web_bug_resumo: "Resumo do problema",
    web_bug_descricao: "O que aconteceu?",
    web_bug_passos: "Como repetir o problema (opcional)",
    web_bug_tecnica: "Juntar informação técnica (versão, língua, navegador e ecrã)",
    web_bug_aviso:
      "O que escrever fica visível para a equipa no GitHub. Não escreva dados pessoais nem palavras-passe; o seu endereço IP não é enviado.",
    web_bug_abrir: "Abrir",
    web_bug_obrigado: "Obrigado! O problema ficou registado (n.º {n}). Vamos analisá-lo.",
    web_bug_curto: "Preencha o resumo e a descrição (pelo menos 10 letras cada).",
    web_bug_indisponivel: "Esta função ainda não está ativa. Tente mais tarde.",
    web_bug_falhou: "Não foi possível registar o problema agora. Tente outra vez daqui a pouco.",
    web_galeria_data_formato: "Como mostrar a data",
    web_galeria_data_livre: "Escrever à mão",
    web_galeria_data_antes: "Texto antes da data (opcional)",
    web_guia_escolas: "Para escolas",
    web_guia_associacoes: "Para associações",
    web_guia_clubes: "Para clubes",
    web_guia_bombeiros: "Para bombeiros",
    web_guia_festas: "Para festas de bairro",
    web_guia_igrejas: "Para paróquias",
    web_partilhar: "Partilhar",
    web_partilhar_texto: "Gerador de Rifas: bilhetes de rifa numerados em PDF, grátis e sem registo.",
    web_partilhar_chamada: "Gostou? Partilhe com quem também faz rifas.",
    web_editor: "Editor de templates",
    web_editor_desfazer: "Desfazer",
    web_editor_refazer: "Refazer",
    web_editor_duplicar: "Duplicar",
    web_editor_frente: "Para a frente",
    web_editor_tras: "Para trás",
    web_editor_imagem: "Imagem (logótipo)",
    web_editor_partilhar: "Partilhar por ligação",
    web_editor_partilha_ok: "Ligação copiada. O desenho fica guardado 90 dias (sem imagens).",
    web_editor_ligacao_invalida: "Esta ligação já não existe ou o desenho expirou.",
    web_editor_imagem_invalida: "Imagem inválida: use um PNG ou JPG até 1 MB.",
    web_editor_intro: "Desenhe a sua rifa sem o Canva.",
    web_editor_texto: "Texto",
    web_editor_retangulo: "Retângulo",
    web_editor_linha: "Linha",
    web_editor_numero: "Número 0001",
    web_editor_modelo: "Começar com um modelo",
    web_editor_cor: "Cor",
    web_editor_contorno: "Contorno",
    web_editor_tamanho: "Tamanho",
    web_editor_negrito: "Negrito",
    web_editor_apagar: "Apagar",
    web_editor_fundo: "Fundo",
    web_editor_pagina: "Tamanho da rifa (largura × altura, pt)",
    web_editor_rodar: "Rodar 90°",
    err_editor_numero: "O desenho tem de ter o número 0001 uma vez, ou duas (talão e parte principal).",
    err_editor_digitos:
      "O texto «{texto}» tem algarismos que o programa confundiria com o número do bilhete.",
    web_exportar_csv: "Exportar lista (CSV)",
    web_folha_controlo: "Folha de controlo (PDF)",
    web_copiar_ligacao: "Copiar ligação",
    web_ligacao_copiada: "Ligação copiada.",
    web_changelog_sub: "O que mudou, versão a versão.",
    web_changelog_resumo: "Resumo",
    web_versao: "Versão {versao}",
    tut_ver_video: "Ver o vídeo deste tópico",
    tut_titulo: "Tutorial",
    mi_video: "Vídeo tutorial",
    mi_sobre: "Acerca de…",
    c1_titulo: "Template (PDF)",
    c1_placeholder: "PDF do Canva",
    c1_analisar: "A analisar o template…",
    c2_titulo: "Algarismos (obrigatório)",
    c2_titulo_sem_obrigatorio: "Algarismos",
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
    web_404_titulo: "Página não encontrada",
    web_404_texto: "Esta página não existe, ou a ligação está errada.",
    web_sessao_expirada: "A sessão expirou.",
    web_erro_rede: "Sem ligação ao servidor.",
    tut_ant: "Anterior",
    tut_seg: "Seguinte",
    video_falta: "Falta {nome}",
    sobre_texto: "{app}\nVersão {versao}\n\nGera PDFs.\n\nUsa X.",
    web_sobre_corpo:
      "**Para quem é.** {app} é para escolas e associações.\n\n**O que faz.** Numera bilhetes e arruma-os na folha.\n\n**Gratuito e privado.** Sem conta nem registo.",
    web_sobre_quem: "**Quem o faz.** {app} é feito por {nome}.",
    web_data_escolher: "Escolher a data",
    web_data_anterior: "Mês anterior",
    web_data_seguinte: "Mês seguinte",
    web_data_hoje: "Hoje",
    web_data_limpar: "Limpar",
  },
  en: {
    web_changelog_sub: "What changed, version by version.",
    web_changelog_resumo: "This is a translated summary.",
    web_versao: "Version {versao}",
    app_nome: "Raffle Generator",
    m_idioma: "Language",
    c1_titulo: "Template (PDF)",
    c2_titulo: "Digits (required)",
    c2_titulo_sem_obrigatorio: "Digits",
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
  /** O `por_defeito` de `/api/linguas` (um teste pode pôr uma língua diferente de "pt" para confirmar que o URL sem prefixo nunca a usa). */
  porDefeito = "pt";
  donativoUrl = "";
  exportarErro = "";
  galeriaErro = "";
  /** Se preenchido, o preçário responde 422 com este texto (pré-visualização e descarregar). */
  precarioErro = "";
  valesErro = "";
  /** Se preenchido, a pré-visualização responde 422 com este texto. */
  previaErro = "";
  anunciosCliente = "";
  anunciosSlot = "";
  partilhaEditor = false;
  problemasAtivos = true;
  responsavel = "";
  comentarios: {
    id: string;
    criado: number;
    anonimo: boolean;
    nome: string;
    visitante: number;
    texto: string;
  }[] = [];
  comentariosEnviados: { texto: string; anonimo: boolean; nome: string; site: string }[] = [];
  comentarioErro = "";
  problemasEnviados: unknown[] = [];
  problemaErro = "";
  partilhados = new Map<string, unknown>();
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
    if (url.startsWith("/api/precario/catalogo")) {
      return this.responder({
        categorias: [
          { id: "menus", nome: "Menus e combos", artigos: [] },
          {
            id: "bebidas",
            nome: "Bebidas",
            artigos: [
              {
                id: "agua",
                nome: "Água",
                emoji: "1f4a7",
                icones: ["1f4a7", "1f6b0", "1f9ca", "fluent:1f4a7"],
              },
              { id: "sumo", nome: "Sumo", emoji: "1f9c3", icones: ["1f9c3", "1f34a"] },
            ],
          },
          {
            id: "comida",
            nome: "Comida",
            artigos: [
              { id: "pizza", nome: "Pizza", emoji: "1f355", icones: ["1f355", "1f9c0"] },
              { id: "sopa", nome: "Sopa", emoji: "1f372", icones: ["1f372", "1f963"] },
            ],
          },
          {
            id: "doces",
            nome: "Doces",
            artigos: [{ id: "bolo", nome: "Bolo", emoji: "1f370", icones: ["1f370", "1f382"] }],
          },
          { id: "extras", nome: "Outros", artigos: [] },
        ],
        ocasioes: [
          {
            id: "festa_popular",
            nome: "Festa popular",
            desenho: "arraial",
            artigos: ["agua", "pizza", "bolo"],
            meses: [6, 7, 8],
          },
          { id: "natal", nome: "Natal", desenho: "natal", artigos: ["sumo", "bolo"], meses: [11, 12] },
        ],
        sugerida: "festa_popular",
        desenhos: [
          { id: "arraial", nome: "Arraial", cores: ["#bf1a2e", "#e68c00", "#fffaf0"] },
          { id: "natal", nome: "Natal", cores: ["#1f6b3a", "#c0392b", "#ffffff"] },
          { id: "quermesse", nome: "Quermesse", cores: ["#bf1a2e", "#e38c00", "#fffae6"] },
        ],
        moedas: [
          { codigo: "EUR", simbolo: "€", decimais: 2 },
          { codigo: "BRL", simbolo: "R$", decimais: 2 },
          { codigo: "USD", simbolo: "$", decimais: 2 },
        ],
        paises: { PT: "EUR", BR: "BRL", US: "USD" },
        pais: "PT",
        moeda: "EUR",
        limites: { linhas: 80, titulo: 40, subtitulo: 70, rodape: 120, nome: 40, moeda_inventada: 14 },
        logo_lugares: ["esquerda", "direita", "rodape"],
        formatos: ["A5", "A4", "A3"],
      });
    }
    if (
      url === "/api/precario/previa.png" ||
      url === "/api/precario/pdf" ||
      url === "/api/precario/etiquetas.pdf" ||
      url === "/api/precario/etiquetas-previa.png" ||
      url === "/api/precario/imagem.png"
    ) {
      if (this.precarioErro) return this.responder({ detail: this.precarioErro, tipo: "aviso" }, 422);
      return Promise.resolve(new Response(new Blob([url.endsWith("pdf") ? "%PDF" : "png"]), { status: 200 }));
    }
    if (url === "/api/vales/previa.png") {
      if (this.valesErro) return this.responder({ detail: this.valesErro, tipo: "aviso" }, 422);
      return Promise.resolve(new Response(new Blob(["png"]), { status: 200 }));
    }
    if (url.startsWith("/api/galeria/previa.png")) {
      if (this.galeriaErro) return this.responder({ detail: this.galeriaErro, tipo: "aviso" }, 422);
      return Promise.resolve(new Response(new Blob(["png"]), { status: 200 }));
    }
    if (url.startsWith("/api/comentarios")) {
      if (metodo === "POST") {
        const c = corpo as { texto: string; anonimo: boolean; nome: string; site: string };
        if (this.comentarioErro) return this.responder({ detail: this.comentarioErro, tipo: "aviso" }, 429);
        this.comentariosEnviados.push(c);
        this.comentarios.unshift({
          id: `c${this.comentarios.length}`,
          criado: 1_800_000_000 + this.comentarios.length,
          anonimo: c.anonimo,
          nome: c.anonimo ? "" : c.nome,
          visitante: c.anonimo || c.nome ? 0 : 4321,
          texto: c.texto,
        });
        return this.responder({ ok: true }, 201);
      }
      const antes = new URL(url, "http://x").searchParams.get("antes") ?? "";
      const inicio = antes ? this.comentarios.findIndex((c) => `${c.criado}~${c.id}` === antes) + 1 : 0;
      const itens = this.comentarios.slice(inicio, inicio + 2); // 2 por página: assim se testa o «Ver mais»
      const ultimo = itens[itens.length - 1];
      return this.responder({
        total: this.comentarios.length,
        itens,
        seguinte: ultimo && inicio + 2 < this.comentarios.length ? `${ultimo.criado}~${ultimo.id}` : "",
      });
    }
    if (url === "/api/problemas" && metodo === "POST") {
      if (this.problemaErro) return this.responder({ detail: this.problemaErro, tipo: "erro" }, 502);
      this.problemasEnviados.push(corpo);
      return this.responder({ numero: 42 }, 201);
    }
    if (url === "/api/publico")
      return this.responder({
        donativo_url: this.donativoUrl,
        contacto: this.temContacto,
        qr: this.temQr,
        anuncios_cliente: this.anunciosCliente,
        anuncios_slot: this.anunciosSlot,
        partilha_editor: this.partilhaEditor,
        problemas: this.problemasAtivos,
        responsavel: this.responsavel,
      });
    const pg = /^\/api\/pagina\/(\w+)$/.exec(url);
    if (pg?.[1])
      return ["termos", "privacidade", "contacto"].includes(pg[1])
        ? this.responder({
            titulo: `Página ${pg[1]}`,
            aviso: "Versão provisória de teste.",
            seccoes: [{ titulo: "Primeira secção", paragrafos: ["Um parágrafo de teste."] }],
          })
        : this.responder({ detail: "x" }, 404);
    if (url === "/api/tutorial")
      return this.responder({
        topicos: [
          { menu: "1   Template", titulo: "Template (PDF)", texto: "Escolha o template.", imagens: [] },
          {
            menu: "Galeria de templates",
            titulo: "Galeria de templates",
            texto: "Sem template do Canva? Escolha um desenho.",
            imagens: [],
            video: "/videos/web_galeria_pt.mp4",
          },
        ],
        video: "",
      });
    if (url === "/api/editor/partilhar" && init?.method === "POST") {
      const id = `abc${this.partilhados.size}xyzxyz`;
      this.partilhados.set(id, corpo);
      return this.responder({ id });
    }
    if (url === "/api/precario/partilhar" && init?.method === "POST") {
      const id = `prc${this.partilhados.size}xyzxyz`;
      this.partilhados.set(id, corpo);
      return this.responder({ id });
    }
    if (url.startsWith("/api/precario/partilha/")) {
      const d = this.partilhados.get(decodeURIComponent(url.slice("/api/precario/partilha/".length))) as
        | { linhas: { artigo: string; nome: string; preco: string; preco2?: string }[] }
        | undefined;
      if (!d)
        return this.responder(
          { detail: "Esta ligação já não existe ou o preçário expirou.", tipo: "aviso" },
          404,
        );
      // o servidor devolve o formato de `para_dict`: preços em milésimos
      const mil = (s: string) =>
        s.trim() ? Math.round(Number.parseFloat(s.replace(",", ".")) * 1000) : null;
      return this.responder({
        precario: {
          ...d,
          linhas: d.linhas.map((l) => ({ ...l, preco: mil(l.preco), preco2: mil(l.preco2 ?? "") })),
        },
      });
    }
    if (url.startsWith("/api/editor/partilha/")) {
      const d = this.partilhados.get(decodeURIComponent(url.slice("/api/editor/partilha/".length)));
      return d
        ? this.responder({ desenho: d, sem_imagens: true })
        : this.responder({ detail: "Esta ligação já não existe ou o desenho expirou.", tipo: "aviso" }, 404);
    }
    if (url === "/api/guias")
      return this.responder({
        guias: [
          {
            nome: "escolas",
            caminho: "/rifas-para-escolas",
            titulo: "Como fazer uma rifa para a escola",
            resumo: "Uma forma simples de angariar fundos.",
          },
          {
            nome: "associacoes",
            caminho: "/rifas-para-associacoes",
            titulo: "Como fazer uma rifa para a associação",
            resumo: "Bilhetes numerados em minutos.",
          },
        ],
      });
    if (url.startsWith("/api/guia/")) {
      const nome = url.slice("/api/guia/".length);
      return this.responder({
        titulo:
          nome === "escolas"
            ? "Como fazer uma rifa para a escola"
            : nome === "numerar"
              ? "Como numerar os bilhetes de uma rifa"
              : nome === "precario"
                ? "Como fazer o preçário de uma festa"
                : "Como fazer uma rifa para a associação",
        intro: "Uma introdução de teste.",
        passos: [1, 2, 3, 4, 5].map((n) => ({ titulo: `Passo ${n}`, texto: `O texto do passo ${n}.` })),
        dicas: ["Dica 1", "Dica 2", "Dica 3"],
        fim: "O serviço é gratuito.",
      });
    }
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
        por_defeito: this.porDefeito,
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
    if (acao === "vales" && metodo === "POST") {
      if (this.valesErro) return this.responder({ detail: this.valesErro, tipo: "aviso" }, 422);
      const novo: Sessao = {
        ...s,
        pronto: true,
        tem_modelo: true,
        modelo_url: `/api/sessoes/${id}/modelo.pdf`,
        template: { nome: "vales-arraial.pdf", estado: "ok", texto: "✔ 1 bilhete (vale)", detalhe: "" },
        algarismos: {
          nome: "vales-arraial-algarismos.pdf",
          estado: "ok",
          texto: "✔ letra Vera",
          detalhe: "",
        },
        info: { n_campos: 1, primeiro: "0001", ultimo: "0001", digitos: 4, tem_folha: true },
      };
      this.sessoes.set(id, novo);
      return this.responder(novo);
    }
    if (acao === "editor" && metodo === "POST") {
      if (this.galeriaErro) return this.responder({ detail: this.galeriaErro, tipo: "aviso" }, 422);
      const novo: Sessao = {
        ...s,
        pronto: true,
        tem_modelo: true,
        modelo_url: `/api/sessoes/${id}/modelo.pdf`,
        template: { nome: "editor.pdf", estado: "ok", texto: "✔ 1 bilhete (editor)", detalhe: "" },
        algarismos: { nome: "editor-algarismos.pdf", estado: "ok", texto: "✔ letra Vera", detalhe: "" },
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
      if (this.previaErro) return this.responder({ detail: this.previaErro, tipo: "aviso" }, 422);
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
