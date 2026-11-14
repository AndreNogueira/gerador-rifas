import { useEffect, useRef, useState } from "react";
import { api, ErroApi } from "./api";
import {
  dataDeHoje,
  FORMATOS_DATA,
  type FormatoData,
  formatarData,
  MAX_DATA,
  textoDaData,
} from "./dataSorteio";
import { useI18n } from "./i18n";
import { SeletorDesenho } from "./SeletorDesenho";
import { useSessao } from "./sessao";

/** Os desenhos da galeria (`core/galeria.py`); os nomes são próprios e não se traduzem, como os dos temas. */
export const DESENHOS = [
  { id: "bosque", nome: "Bosque" },
  { id: "quermesse", nome: "Quermesse" },
  { id: "natal", nome: "Natal" },
  { id: "gala", nome: "Gala" },
  { id: "pascoa", nome: "Páscoa" },
  { id: "carnaval", nome: "Carnaval" },
  { id: "santos", nome: "Santos Populares" },
  { id: "coracao", nome: "Coração" },
  { id: "praia", nome: "Praia" },
  { id: "halloween", nome: "Halloween" },
  { id: "magusto", nome: "Magusto" },
  { id: "futebol", nome: "Futebol" },
  { id: "escola", nome: "Escola" },
  { id: "festival", nome: "Festival" },
  { id: "solidaria", nome: "Solidária" },
  { id: "bombeiros", nome: "Bombeiros" },
  { id: "retro", nome: "Retro" },
  { id: "minimal", nome: "Minimalista" },
  { id: "vindima", nome: "Vindima" },
  { id: "arraial", nome: "Arraial" },
  { id: "tesouro", nome: "Tesouro" },
  { id: "primavera", nome: "Primavera" },
  { id: "inverno", nome: "Inverno" },
  { id: "cinema", nome: "Cinema" },
] as const;

/** Quantos prémios a pessoa pode escolher (`core/galeria.py`: `MIN_PREMIOS`, `MAX_PREMIOS`); a rifa passa a duas colunas a partir de 6. */
export const MIN_PREMIOS = 3;
export const MAX_PREMIOS = 10;
const QUANTOS = Array.from({ length: MAX_PREMIOS - MIN_PREMIOS + 1 }, (_, i) => MIN_PREMIOS + i);

interface Textos {
  titulo: string;
  organizacao: string;
  premios: string[];
  data: string;
}
const VAZIOS: Textos = { titulo: "", organizacao: "", premios: Array(MAX_PREMIOS).fill(""), data: "" };

/**
 * «Sem template? Escolha um da galeria»: um desenho, os textos da rifa, e «Usar este template» cria o template e os algarismos na sessão.
 * A pré-visualização desenha-se no servidor (com os textos escritos); as letras que a Vera não tem dão um aviso em vez de uma imagem.
 */
export function Galeria({ desativado }: { desativado: boolean }) {
  const { t, lingua } = useI18n();
  const s = useSessao();
  const [aberto, setAberto] = useState(false);
  const [desenho, setDesenho] = useState<string>(DESENHOS[0].id);
  const [f, setF] = useState<Textos>(VAZIOS);
  const [quantos, setQuantos] = useState(MIN_PREMIOS);
  const [diaIso, setDiaIso] = useState(""); // a data escolhida no calendário (aaaa-mm-dd)
  const [formato, setFormato] = useState<FormatoData>("longo");
  const [antes, setAntes] = useState("");
  const [prev, setPrev] = useState<Textos>(VAZIOS);
  const [imagem, setImagem] = useState("");
  const [erro, setErro] = useState("");
  const anterior = useRef("");

  // só contam os prémios das caixas que se vêem (os das caixas escondidas ficam guardados, mas não vão na rifa)
  const premios = f.premios.slice(0, quantos).filter((p) => p.trim());
  const chavePremios = JSON.stringify(premios);

  // a data que vai na rifa: a do calendário no formato escolhido, ou o texto escrito à mão
  const data = textoDaData({ iso: diaIso, formato, antes, livre: f.data, lingua: lingua });
  const exemplo = diaIso || dataDeHoje(); // os formatos mostram-se com a data escolhida (ou a de hoje)

  // os textos só vão ao servidor depois de uma pequena espera (não a cada tecla)
  // biome-ignore lint/correctness/useExhaustiveDependencies: `chavePremios` já resume os prémios que contam
  useEffect(() => {
    const espera = setTimeout(() => setPrev({ ...f, premios, data }), 400);
    return () => clearTimeout(espera);
  }, [f.titulo, f.organizacao, data, chavePremios]);

  // a pré-visualização só se pede com a galeria aberta
  useEffect(() => {
    if (!aberto) return;
    const controlo = new AbortController();
    api
      .galeriaPrevia(
        { desenho, t: prev.titulo, o: prev.organizacao, p: prev.premios, d: prev.data },
        controlo.signal,
      )
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        if (anterior.current) URL.revokeObjectURL(anterior.current);
        anterior.current = url;
        setImagem(url);
        setErro("");
      })
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return;
        setErro(e instanceof ErroApi ? e.message : t("web_erro_rede"));
      });
    return () => controlo.abort();
  }, [aberto, desenho, prev, t]);

  useEffect(
    () => () => {
      if (anterior.current) URL.revokeObjectURL(anterior.current);
    },
    [],
  );

  const mudar = (campo: "titulo" | "organizacao" | "data", valor: string) =>
    setF((x) => ({ ...x, [campo]: valor }));
  const mudarPremio = (i: number, valor: string) =>
    setF((x) => ({ ...x, premios: x.premios.map((p, j) => (j === i ? valor : p)) }));
  const nomeDoDesenho = DESENHOS.find((d) => d.id === desenho)?.nome ?? "";

  return (
    <details className="galeria" data-testid="galeria" onToggle={(e) => setAberto(e.currentTarget.open)}>
      <summary>{t("web_galeria")}</summary>
      <SeletorDesenho
        opcoes={DESENHOS}
        valor={desenho}
        aoEscolher={setDesenho}
        nomeDaLista={t("web_galeria")}
      />
      {erro ? (
        <p role="alert" className="cor-aviso" data-testid="galeria-erro">
          {erro}
        </p>
      ) : (
        imagem && (
          <img className="galeria-previa" src={imagem} alt={nomeDoDesenho} data-testid="galeria-previa" />
        )
      )}
      <div className="linha">
        <label>
          {t("web_galeria_titulo")}
          <input
            value={f.titulo}
            onChange={(e) => mudar("titulo", e.target.value)}
            maxLength={40}
            data-testid="galeria-titulo"
          />
        </label>
        <label>
          {t("web_galeria_organizacao")}
          <input
            value={f.organizacao}
            onChange={(e) => mudar("organizacao", e.target.value)}
            maxLength={60}
          />
        </label>
      </div>
      <fieldset className="premios">
        <legend>{t("web_galeria_premios")}</legend>
        <label className="quantos-premios">
          {t("web_galeria_n_premios")}
          <select
            value={quantos}
            onChange={(e) => setQuantos(Number(e.target.value))}
            data-testid="galeria-n-premios"
          >
            {QUANTOS.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </label>
        {f.premios.slice(0, quantos).map((valor, i) => (
          <input
            // biome-ignore lint/suspicious/noArrayIndexKey: a posição é o que identifica cada prémio
            key={i}
            value={valor}
            onChange={(e) => mudarPremio(i, e.target.value)}
            maxLength={50}
            aria-label={`${t("web_galeria_premios")} ${i + 1}`}
            data-testid={`galeria-premio-${i + 1}`}
          />
        ))}
      </fieldset>
      <fieldset className="data-sorteio">
        <legend>{t("web_galeria_data")}</legend>
        <div className="linha">
          {formato !== "livre" && (
            <input
              type="date"
              value={diaIso}
              onChange={(e) => setDiaIso(e.target.value)}
              aria-label={t("web_galeria_data")}
              data-testid="galeria-data"
            />
          )}
          <label>
            <span className="so-leitores">{t("web_galeria_data_formato")}</span>
            <select
              value={formato}
              onChange={(e) => setFormato(e.target.value as FormatoData)}
              aria-label={t("web_galeria_data_formato")}
              data-testid="galeria-data-formato"
            >
              {FORMATOS_DATA.map((fm) => (
                <option key={fm} value={fm}>
                  {formatarData(exemplo, fm, lingua)}
                </option>
              ))}
              <option value="livre">{t("web_galeria_data_livre")}</option>
            </select>
          </label>
        </div>
        {formato === "livre" ? (
          <input
            value={f.data}
            onChange={(e) => mudar("data", e.target.value)}
            maxLength={MAX_DATA}
            aria-label={t("web_galeria_data")}
            data-testid="galeria-data-livre"
          />
        ) : (
          <label>
            {t("web_galeria_data_antes")}
            <input
              value={antes}
              onChange={(e) => setAntes(e.target.value)}
              maxLength={20}
              data-testid="galeria-data-antes"
            />
          </label>
        )}
      </fieldset>
      <button
        type="button"
        disabled={desativado || !!erro}
        onClick={() =>
          void s.usarGaleria({
            desenho,
            titulo: f.titulo,
            organizacao: f.organizacao,
            premios,
            data,
          })
        }
        data-testid="galeria-usar"
      >
        {t("web_galeria_usar")}
      </button>
    </details>
  );
}
