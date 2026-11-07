import { useEffect, useRef, useState } from "react";
import type { Calculo, Campos, Sessao } from "./api";
import { CartaoAlgarismos, CartaoDestino, CartaoNumeros, CartaoTemplate } from "./cartoes";
import { useI18n } from "./i18n";
import { Ligacao } from "./rota";
import { aCorrer, useSessao } from "./sessao";

const TOPICO_ALGARISMOS = 3; // posição de «2 Algarismos» na lista do tutorial (core.tutorial.TOPICO_ALGARISMOS)

interface Props {
  campos: Campos;
  calculo: Calculo | null;
  mudar: (c: keyof Campos, v: string) => void;
  reiniciar: () => void;
}

/** O ecrã principal: os 4 passos, as ações, o registo e o visor (o mesmo da janela da app Windows). */
export function Gerador({ campos, calculo, mudar, reiniciar }: Props) {
  const { t } = useI18n();
  const s = useSessao();
  const [expandido, setExpandido] = useState(false);
  const a_gerar = aCorrer(s.sessao);

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
            aoLimpar={async () => {
              await s.limpar();
              reiniciar();
            }}
          />
        </div>
      )}
      <Visor sessao={s.sessao} expandido={expandido} aoAlternar={() => setExpandido((e) => !e)} />
    </div>
  );
}

function Acoes({
  campos,
  calculo,
  aoLimpar,
}: {
  campos: Campos;
  calculo: Calculo | null;
  aoLimpar: () => Promise<void>;
}) {
  const { t } = useI18n();
  const s = useSessao();
  const sessao = s.sessao;
  const a_gerar = aCorrer(sessao);
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
          {t("previa")}
        </button>
        <button
          type="button"
          disabled={a_gerar ? tr?.estado === "a_cancelar" : !livre}
          onClick={() => (a_gerar ? void s.cancelar() : void s.pedirGerar(campos, calculo?.confirmar ?? ""))}
          data-testid="gerar"
        >
          {a_gerar ? t("cancelar") : t("gerar")}
        </button>
        <button
          type="button"
          className="texto"
          disabled={a_gerar || !sessao || s.ocupado !== null}
          onClick={() => void aoLimpar()}
          data-testid="limpar"
        >
          {t("limpar")}
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
    </section>
  );
}

function Entrega({ entrega }: { entrega: NonNullable<Sessao["trabalho"]["entrega"]> }) {
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
      <a className="botao" href={entrega.url} download={entrega.nome} data-testid="descarregar">
        {t("web_descarregar")} — {entrega.nome}
      </a>
    </div>
  );
}

function Visor({
  sessao,
  expandido,
  aoAlternar,
}: {
  sessao: Sessao | null;
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
        <h2 data-testid="titulo-visor">{titulo}</h2>
        <div className="botoes">
          <button type="button" className="texto" onClick={aoAlternar} data-testid="expandir">
            {t(expandido ? "mi_reduzir" : "mi_expandir")}
          </button>
          {url && (
            <a href={url} target="_blank" rel="noreferrer" data-testid="nova-janela">
              {t("web_nova_janela")}
            </a>
          )}
        </div>
      </div>
      {url ? (
        <iframe key={url} className="pdf" src={`${url}#view=FitH`} title={titulo} data-testid="visor" />
      ) : (
        <p className="suave">{t("previa_vazio")}</p>
      )}
    </section>
  );
}
