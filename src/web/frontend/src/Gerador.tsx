import { useEffect, useRef, useState } from "react";
import type { Calculo, Campos, Sessao } from "./api";
import { api, ErroApi, ErroRede } from "./api";
import { ConviteComentario, jaConvidou } from "./Convite";
import { CartaoAlgarismos, CartaoDestino, CartaoNumeros, CartaoTemplate } from "./cartoes";
import { Donativo } from "./Donativo";
import { useDialogos } from "./dialogos";
import { ligacaoDosCampos } from "./formulario";
import { useI18n } from "./i18n";
import { Icone } from "./icones";
import { Partilhar } from "./Partilhar";
import { Ligacao } from "./rota";
import { aCorrer, chaveDaPrevia, useSessao } from "./sessao";

/** Um nome para o ficheiro descarregado: sem o que o Windows não aceita e sem nada de caminhos. */
export function nomeSeguro(nome: string): string {
  return [...nome]
    .filter((c) => c >= " " && !'<>:"/\\|?*'.includes(c))
    .join("")
    .trim()
    .replace(/^[. ]+|[. ]+$/g, "")
    .slice(0, 80);
}

/** Entrega um Blob como descarga. */
export function guardarBlob(blob: Blob, nome: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nome;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Quanto se espera, depois da última alteração, para refazer a pré-visualização sozinha (o servidor aceita 30 pedidos pesados por minuto). */
export const ESPERA_PREVIA_MS = 700;
const TOPICO_ALGARISMOS = 3; // posição de «2 Algarismos» na lista do tutorial (core.tutorial.TOPICO_ALGARISMOS)

interface Props {
  campos: Campos;
  calculo: Calculo | null;
  mudar: (c: keyof Campos, v: string) => void;
  reiniciar: () => void;
  /** O `DONATIVO_URL` do servidor: vazio = nada de donativo. */
  donativoUrl?: string;
}

/** O ecrã principal: os 4 passos, as ações, o registo e o visor (o mesmo da janela da app Windows). */
export function Gerador({ campos, calculo, mudar, reiniciar, donativoUrl = "" }: Props) {
  const { t } = useI18n();
  const s = useSessao();
  const [expandido, setExpandido] = useState(false);
  const a_gerar = aCorrer(s.sessao);

  // A pré-visualização refaz-se sozinha quando muda algo que altera a página final (o template, os algarismos, o logótipo ou qualquer campo
  // da folha e dos números): ninguém tem de carregar em «Pré-visualizar» para ver como fica. Não corre a gerar nem com outro pedido em curso.
  const { sessao, ocupado, pedirPrevia, previaDe } = s;
  const livre = !!sessao?.pronto && !a_gerar && ocupado === null;
  const chaveCampos = chaveDaPrevia(campos);
  const precisa = !!sessao && (sessao.previa === null || chaveCampos !== previaDe); // o que se vê já não é o que se pede
  const tentativa = JSON.stringify([
    chaveCampos,
    sessao?.sessao,
    sessao?.template,
    sessao?.algarismos,
    sessao?.info,
    sessao?.logotipo,
    sessao?.previa === null,
  ]);
  const ultimaTentativa = useRef("");
  // biome-ignore lint/correctness/useExhaustiveDependencies: `tentativa` resume os campos e a sessão; `campos` muda de identidade a cada render
  useEffect(() => {
    if (!livre || !precisa || ultimaTentativa.current === tentativa) return;
    const espera = setTimeout(() => {
      ultimaTentativa.current = tentativa; // se falhar, não se repete até algo mudar
      void pedirPrevia(campos, true);
    }, ESPERA_PREVIA_MS);
    return () => clearTimeout(espera);
  }, [livre, precisa, tentativa, pedirPrevia]);

  return (
    <div className={`gerador${expandido ? " expandido" : ""}`}>
      {!expandido && (
        <div className="coluna">
          <CartaoTemplate
            sessao={s.sessao}
            ocupado={s.ocupado}
            bloqueado={a_gerar}
            campos={campos}
            calculo={calculo}
            mudar={mudar}
            aoEscolher={(f) => void s.carregarTemplate(f)}
          />
          <CartaoAlgarismos
            sessao={s.sessao}
            ocupado={s.ocupado}
            bloqueado={a_gerar}
            lembrado={s.algarismosLembrados}
            aoEscolher={(f) => void s.carregarAlgarismos(f)}
            aoPedirAjuda={
              <Ligacao para={`/tutorial?p=${TOPICO_ALGARISMOS}`} className="ajuda">
                {t("c2_ajuda")}
              </Ligacao>
            }
          />
          <CartaoNumeros campos={campos} calculo={calculo} mudar={mudar} />
          <CartaoDestino campos={campos} mudar={mudar} />
          <Acoes
            campos={campos}
            calculo={calculo}
            donativoUrl={donativoUrl}
            aoLimpar={async () => {
              await s.limpar();
              reiniciar();
            }}
          />
        </div>
      )}
      <Visor
        sessao={s.sessao}
        erro={s.erroPrevia}
        expandido={expandido}
        aoAlternar={() => setExpandido((e) => !e)}
      />
    </div>
  );
}

function Acoes({
  campos,
  calculo,
  donativoUrl,
  aoLimpar,
}: {
  campos: Campos;
  calculo: Calculo | null;
  donativoUrl: string;
  aoLimpar: () => Promise<void>;
}) {
  const { t } = useI18n();
  const { aviso } = useDialogos();
  const s = useSessao();
  const sessao = s.sessao;
  const a_gerar = aCorrer(sessao);
  /** Pede ao servidor a lista ou a folha de controlo e entrega-a como descarga (nada fica guardado no servidor). */
  const exportar = async (pedir: () => Promise<Blob>, extensao: string, prefixo = "") => {
    try {
      const nome = `${prefixo}${nomeSeguro(campos.nome) || "rifas"}.${extensao}`;
      guardarBlob(await pedir(), nome);
    } catch (e) {
      if (e instanceof ErroApi) aviso(e.message, e.tipo);
      else if (e instanceof ErroRede) aviso(t("web_erro_rede"), "erro");
      else throw e;
    }
  };
  const copiarLigacao = async () => {
    const ligacao = ligacaoDosCampos(campos, `${window.location.origin}/`);
    try {
      await navigator.clipboard.writeText(ligacao);
      aviso(t("web_ligacao_copiada"), "aviso");
    } catch {
      aviso(ligacao, "aviso"); // sem acesso à área de transferência: mostra-se a ligação para copiar à mão
    }
  };
  const registoEl = useRef<HTMLPreElement>(null);
  const linhas = s.registo.length;
  // o registo desliza para a linha mais recente
  useEffect(() => {
    if (registoEl.current && linhas >= 0) registoEl.current.scrollTop = registoEl.current.scrollHeight;
  }, [linhas]);
  const livre = !!sessao?.pronto && !a_gerar && s.ocupado === null;
  const tr = sessao?.trabalho;
  const progresso = tr?.total ? tr.feitas / tr.total : tr?.estado === "ok" || tr?.estado === "erros" ? 1 : 0;

  return (
    <section className="cartao acoes" aria-label={t("gerar")}>
      <div className="botoes">
        <button
          type="button"
          className="secundario"
          disabled={!livre}
          onClick={() => void s.pedirPrevia(campos)}
          data-testid="previa"
        >
          <Icone nome="olho" />
          {t("previa")}
        </button>
        <button
          type="button"
          disabled={a_gerar ? tr?.estado === "a_cancelar" : !livre}
          onClick={() => (a_gerar ? void s.cancelar() : void s.pedirGerar(campos, calculo?.confirmar ?? ""))}
          data-testid="gerar"
        >
          <Icone nome={a_gerar ? "fechar" : "faiscas"} />
          {a_gerar ? t("cancelar") : t("gerar")}
        </button>
        <button
          type="button"
          className="texto"
          disabled={a_gerar || !sessao || s.ocupado !== null}
          onClick={() => void aoLimpar()}
          data-testid="limpar"
        >
          <Icone nome="lixo" />
          {t("limpar")}
        </button>
        <button
          type="button"
          className="texto"
          onClick={() => void copiarLigacao()}
          data-testid="copiar-ligacao"
        >
          <Icone nome="ligacao" />
          {t("web_copiar_ligacao")}
        </button>
        <button
          type="button"
          className="texto"
          onClick={() => void exportar(() => api.listaCsv(campos), "csv")}
          data-testid="exportar-csv"
        >
          <Icone nome="descarregar" />
          {t("web_exportar_csv")}
        </button>
        <button
          type="button"
          className="texto"
          onClick={() => void exportar(() => api.folhaDeControlo(campos), "pdf", "Controlo - ")}
          data-testid="exportar-controlo"
        >
          <Icone nome="descarregar" />
          {t("web_folha_controlo")}
        </button>
      </div>
      <progress value={progresso} max={1} data-testid="progresso" aria-label={t("gerar")} />
      <p className={`estado cor-${tr?.cor ?? "suave"}`} data-testid="estado" aria-live="polite">
        {tr?.texto ?? ""}
      </p>
      {(s.registo.length > 0 || (sessao?.avisos.length ?? 0) > 0) && (
        <pre ref={registoEl} className="registo" data-testid="registo">
          {[...(sessao?.avisos ?? []), ...s.registo].join("\n")}
        </pre>
      )}
      {tr?.entrega && !a_gerar && <Entrega entrega={tr.entrega} />}
      {tr?.entrega && !a_gerar && <Donativo url={donativoUrl} variante="cartao" />}
      {tr?.entrega && !a_gerar && <Partilhar variante="cartao" />}
    </section>
  );
}

function Entrega({ entrega }: { entrega: NonNullable<Sessao["trabalho"]["entrega"]> }) {
  const [convidar, setConvidar] = useState(false);
  const { t } = useI18n();
  return (
    <div className="entrega">
      <h3>{t("web_ficheiros_gerados")}</h3>
      <ul>
        {entrega.ficheiros.map((f) => (
          <li key={f}>{f}</li>
        ))}
        {entrega.total > entrega.ficheiros.length && <li>… (+{entrega.total - entrega.ficheiros.length})</li>}
      </ul>
      <a
        className="botao"
        href={entrega.url}
        download={entrega.nome}
        data-testid="descarregar"
        onClick={() => {
          if (!jaConvidou()) setConvidar(true); // um convite a deixar um comentário, uma só vez por aparelho e só depois de descarregar
        }}
      >
        <Icone nome="descarregar" />
        {t("web_descarregar")} — {entrega.nome}
      </a>
      {convidar && <ConviteComentario />}
    </div>
  );
}

/** `navigator.pdfViewerEnabled` é false onde o browser não mostra PDFs dentro de uma página (p.ex. o Chrome do Android). */
function sem_visor_de_pdf(): boolean {
  return typeof navigator !== "undefined" && navigator.pdfViewerEnabled === false;
}

function Visor({
  sessao,
  erro,
  expandido,
  aoAlternar,
}: {
  sessao: Sessao | null;
  erro: string;
  expandido: boolean;
  aoAlternar: () => void;
}) {
  const { t } = useI18n();
  // a pré-visualização se já a há; senão o template que se carregou; senão nada
  const url = sessao?.previa?.url ?? (sessao?.tem_modelo ? sessao.modelo_url : "");
  const titulo = sessao?.previa
    ? sessao.previa.titulo
    : sessao?.tem_modelo
      ? t("template_titulo")
      : t("previa_titulo");
  return (
    <section className="visor" aria-label={titulo}>
      <div className="visor-topo">
        <h2>
          <Icone nome="olho" tamanho={22} />
          <span data-testid="titulo-visor">{titulo}</span>
        </h2>
        <div className="botoes">
          <button type="button" className="texto" onClick={aoAlternar} data-testid="expandir">
            <Icone nome={expandido ? "reduzir" : "expandir"} tamanho={18} />
            {t(expandido ? "mi_reduzir" : "mi_expandir")}
          </button>
          {url && (
            <a href={url} target="_blank" rel="noreferrer" data-testid="nova-janela">
              <Icone nome="externo" tamanho={16} />
              {t("web_nova_janela")}
            </a>
          )}
        </div>
      </div>
      {erro && (
        <p role="status" className="cor-aviso" data-testid="previa-erro">
          {erro}
        </p>
      )}
      {url ? (
        sem_visor_de_pdf() ? (
          // browsers sem visor de PDF (Chrome do Android): uma imagem da 1.ª página; «Abrir noutra janela» continua a abrir o PDF
          <img
            key={url}
            className="pdf-imagem"
            src={url.replace(".pdf", ".png")}
            alt={titulo}
            data-testid="visor"
          />
        ) : (
          <iframe key={url} className="pdf" src={`${url}#view=FitH`} title={titulo} data-testid="visor" />
        )
      ) : (
        <div className="vazio">
          <Icone nome="bilhete" tamanho={64} strokeWidth={1.5} />
          <p className="suave">{t("previa_vazio")}</p>
        </div>
      )}
    </section>
  );
}
