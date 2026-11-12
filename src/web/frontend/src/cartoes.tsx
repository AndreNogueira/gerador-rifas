import { type ReactNode, useEffect, useRef, useState } from "react";
import type { Calculo, Campos, Cor, Ficheiro, Sessao } from "./api";
import { PAPEIS } from "./formulario";
import { Galeria } from "./Galeria";
import { useI18n } from "./i18n";
import { Icone, type NomeIcone } from "./icones";
import { MarcaPropria } from "./MarcaPropria";
import { Ligacao } from "./rota";
import type { Ocupado } from "./sessao";

const COR_DO_ESTADO: Record<Ficheiro["estado"], Cor> = {
  vazio: "suave",
  precisa: "erro",
  ok: "ok",
  erro: "erro",
};

const ICONE_DO_PASSO: Record<number, NomeIcone> = {
  1: "template",
  2: "algarismos",
  3: "bilhete",
  4: "destino",
};

/** Um passo é um bilhete: insígnia colorida com o ícone, o título, e o número do passo como o número do bilhete. */
export function Cartao({ passo, titulo, children }: { passo: number; titulo: string; children: ReactNode }) {
  return (
    <section className={`cartao passo passo-${passo}`} aria-label={titulo}>
      <h2>
        <span className="insignia">
          <Icone nome={ICONE_DO_PASSO[passo] ?? "bilhete"} tamanho={22} />
        </span>
        <span className="titulo-passo">{titulo}</span>
        <span className="numero" aria-hidden="true">
          {passo}
        </span>
      </h2>
      {children}
    </section>
  );
}

function Estado({ cor, testid, children }: { cor: Cor; testid: string; children: ReactNode }) {
  return (
    <p className={`estado cor-${cor}`} data-testid={testid}>
      {children}
    </p>
  );
}

/** Escolher um ficheiro (botão ou arrastar). No servidor o tipo REAL é verificado pelos bytes, não pela extensão. */
function Carregar({
  rotulo,
  aceita,
  desativado,
  testid,
  aoEscolher,
}: {
  rotulo: string;
  aceita: string;
  desativado: boolean;
  testid: string;
  aoEscolher: (f: File) => void;
}) {
  const entrada = useRef<HTMLInputElement>(null);
  const zona = useRef<HTMLDivElement>(null);
  const [por_cima, setPorCima] = useState(false);

  // arrastar um ficheiro para a zona (ouvintes no elemento: um <div> com eventos de rato não é acessível por si)
  useEffect(() => {
    const el = zona.current;
    if (!el) return;
    const sobre = (e: Event) => {
      e.preventDefault();
      setPorCima(true);
    };
    const saiu = () => setPorCima(false);
    const largou = (e: Event) => {
      e.preventDefault();
      setPorCima(false);
      const f = (e as globalThis.DragEvent).dataTransfer?.files[0];
      if (f && !desativado) aoEscolher(f);
    };
    el.addEventListener("dragover", sobre);
    el.addEventListener("dragleave", saiu);
    el.addEventListener("drop", largou);
    return () => {
      el.removeEventListener("dragover", sobre);
      el.removeEventListener("dragleave", saiu);
      el.removeEventListener("drop", largou);
    };
  }, [desativado, aoEscolher]);

  return (
    <div ref={zona} className={`carregar${por_cima ? " por-cima" : ""}`}>
      <button
        type="button"
        className="secundario"
        disabled={desativado}
        onClick={() => entrada.current?.click()}
      >
        <Icone nome="carregar" />
        {rotulo}
      </button>
      <input
        ref={entrada}
        type="file"
        accept={aceita}
        hidden
        data-testid={testid}
        onChange={(e) => {
          const f = e.target.files?.[0];
          e.target.value = ""; // permite escolher o mesmo ficheiro outra vez
          if (f) aoEscolher(f);
        }}
      />
    </div>
  );
}

interface PropsComuns {
  sessao: Sessao | null;
  ocupado: Ocupado;
  /** a gerar: nada se carrega nem se apaga */
  bloqueado: boolean;
}

export function CartaoTemplate({
  sessao,
  ocupado,
  bloqueado,
  campos,
  calculo,
  mudar,
  aoEscolher,
}: PropsComuns & {
  campos: Campos;
  calculo: Calculo | null;
  mudar: (c: keyof Campos, v: string) => void;
  aoEscolher: (f: File) => void;
}) {
  const { t } = useI18n();
  const ficheiro = sessao?.template;
  const folha = sessao?.info?.tem_folha ? calculo?.folha : null;
  return (
    <Cartao passo={1} titulo={t("c1_titulo")}>
      <Carregar
        rotulo={`${t("escolher")}  (${t("c1_placeholder")})`}
        aceita=".pdf,application/pdf"
        desativado={bloqueado || !sessao || ocupado === "template"}
        testid="upload-template"
        aoEscolher={aoEscolher}
      />
      {ocupado === "template" ? (
        <Estado cor="suave" testid="estado-template">
          {t("c1_analisar")}
        </Estado>
      ) : (
        <Estado cor={ficheiro ? COR_DO_ESTADO[ficheiro.estado] : "suave"} testid="estado-template">
          {ficheiro?.texto ?? ""}
        </Estado>
      )}
      <Galeria desativado={bloqueado || !sessao || ocupado !== null} />
      <p className="suave">
        <Ligacao para="/editor" className="editor-ligacao" data-testid="ligacao-editor">
          {t("web_editor")} →
        </Ligacao>
      </p>
      {sessao?.info?.tem_folha && (
        <div className="folha">
          <p className="suave">{t("lay_info")}</p>
          <div className="linha">
            <label>
              {t("lay_papel")}
              <select
                value={campos.papel}
                onChange={(e) => mudar("papel", e.target.value)}
                data-testid="papel"
              >
                {PAPEIS.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("lay_margem")}
              <input
                value={campos.margem}
                onChange={(e) => mudar("margem", e.target.value)}
                inputMode="numeric"
                data-testid="margem"
              />
            </label>
            <label>
              {t("lay_por_folha")}
              <input
                value={campos.porfolha}
                onChange={(e) => mudar("porfolha", e.target.value)}
                inputMode="numeric"
                data-testid="porfolha"
              />
            </label>
          </div>
          <label className="opcao">
            <input
              type="checkbox"
              checked={campos.marcas === "1"}
              onChange={(e) => mudar("marcas", e.target.checked ? "1" : "")}
              data-testid="marcas"
            />
            {t("web_marcas")}
          </label>
          {folha && (
            <Estado cor={folha.erro ? "erro" : folha.aviso ? "aviso" : "suave"} testid="texto-folha">
              {folha.texto}
            </Estado>
          )}
        </div>
      )}
    </Cartao>
  );
}

export function CartaoAlgarismos({
  sessao,
  ocupado,
  bloqueado,
  aoEscolher,
  aoPedirAjuda,
  lembrado = "",
}: PropsComuns & { aoEscolher: (f: File) => void; aoPedirAjuda: ReactNode; lembrado?: string }) {
  const { t } = useI18n();
  const ficheiro = sessao?.algarismos;
  return (
    <Cartao passo={2} titulo={t("c2_titulo")}>
      <Carregar
        rotulo={`${t("escolher")}  (${t("c2_placeholder")})`}
        aceita=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
        desativado={bloqueado || !sessao || ocupado === "algarismos"}
        testid="upload-algarismos"
        aoEscolher={aoEscolher}
      />
      {ocupado === "algarismos" ? (
        <Estado cor="suave" testid="estado-algarismos">
          {t("c2_analisar")}
        </Estado>
      ) : (
        <Estado cor={ficheiro ? COR_DO_ESTADO[ficheiro.estado] : "suave"} testid="estado-algarismos">
          {ficheiro?.texto ?? ""}
        </Estado>
      )}
      {lembrado && ficheiro?.estado === "ok" && (
        <p className="suave" data-testid="algarismos-lembrados">
          {t("web_algarismos_lembrados", { nome: lembrado })}
        </p>
      )}
      {aoPedirAjuda}
    </Cartao>
  );
}

export function CartaoNumeros({
  campos,
  calculo,
  mudar,
}: {
  campos: Campos;
  calculo: Calculo | null;
  mudar: (c: keyof Campos, v: string) => void;
}) {
  const { t } = useI18n();
  const resumo = calculo?.resumo;
  return (
    <Cartao passo={3} titulo={t("c3_titulo")}>
      <div className="linha">
        <label>
          {t("de")}
          <input
            value={campos.inicio}
            onChange={(e) => mudar("inicio", e.target.value)}
            inputMode="numeric"
            data-testid="de"
          />
        </label>
        <label>
          {t("ate")}
          <input
            value={campos.fim}
            onChange={(e) => mudar("fim", e.target.value)}
            inputMode="numeric"
            data-testid="ate"
          />
        </label>
        <label>
          {t("algarismos")}
          <input
            value={campos.digitos}
            onChange={(e) => mudar("digitos", e.target.value)}
            inputMode="numeric"
            data-testid="algarismos"
          />
        </label>
      </div>
      <fieldset className="modo" data-testid="modo">
        {(["varios", "unico"] as const).map((m) => (
          <label key={m} className="opcao">
            <input
              type="radio"
              name="modo"
              value={m}
              checked={campos.modo === m}
              onChange={() => mudar("modo", m)}
            />
            {t(m === "varios" ? "modo_varios" : "modo_unico")}
          </label>
        ))}
      </fieldset>
      <label>
        {t("max_ficheiro")}
        <input
          value={campos.max_ficheiro}
          onChange={(e) => mudar("max_ficheiro", e.target.value)}
          disabled={campos.modo !== "varios"}
          inputMode="numeric"
          data-testid="max-ficheiro"
        />
      </label>
      <div className="linha extras">
        <label>
          {t("web_prefixos")}
          <input
            value={campos.prefixos}
            onChange={(e) => mudar("prefixos", e.target.value)}
            placeholder="A-   /   A-, B-, C-"
            maxLength={120}
            autoComplete="off"
            aria-describedby="dica-prefixos"
            data-testid="prefixos"
          />
        </label>
        <label>
          {t("web_saltar")}
          <input
            value={campos.saltar}
            onChange={(e) => mudar("saltar", e.target.value)}
            placeholder="13, 100-110"
            maxLength={300}
            autoComplete="off"
            data-testid="saltar"
          />
        </label>
      </div>
      <p className="suave dica" id="dica-prefixos">
        {t("web_prefixos_dica")}
      </p>
      <label className="opcao">
        <input
          type="checkbox"
          checked={campos.cor_serie === "1"}
          onChange={(e) => mudar("cor_serie", e.target.checked ? "1" : "")}
          data-testid="cor-serie"
        />
        {t("web_cor_serie")}
      </label>
      <MarcaPropria campos={campos} mudar={mudar} />
      <Estado cor={resumo?.aviso ? "aviso" : "suave"} testid="resumo">
        {resumo?.texto ?? ""}
      </Estado>
    </Cartao>
  );
}

export function CartaoDestino({
  campos,
  mudar,
}: {
  campos: Campos;
  mudar: (c: keyof Campos, v: string) => void;
}) {
  const { t } = useI18n();
  return (
    <Cartao passo={4} titulo={t("c4_titulo")}>
      <label>
        {t("nome_ficheiros")}
        <input
          value={campos.nome}
          onChange={(e) => mudar("nome", e.target.value)}
          placeholder={t("nome_placeholder")}
          maxLength={200}
          data-testid="nome"
        />
      </label>
    </Cartao>
  );
}
