import { useEffect, useRef, useState } from "react";
import { api, ErroApi, type PedidoVale } from "./api";
import { useI18n } from "./i18n";
import { navegar } from "./rota";
import { useSessao } from "./sessao";

const ATRASO_MS = 350;

/** O singular que se propõe a partir do plural que a pessoa escreveu («fichas» → «ficha»): só tira um «s» final; a pessoa corrige se for preciso. */
export function singularDe(plural: string): string {
  const p = plural.trim();
  return p.length > 2 && p.toLowerCase().endsWith("s") ? p.slice(0, -1) : p;
}

interface Props {
  /** O desenho (da galeria) do preçário: o vale sai com o mesmo aspeto. */
  desenho: string;
  /** O nome da moeda inventada, no plural, como está no preçário. */
  moeda: string;
  /** A organização que se propõe (o subtítulo do preçário). */
  organizacao: string;
}

/**
 * «Vales numerados» (fase 7 do preçário): quando a moeda é inventada, desenha o vale (o mesmo desenho do preçário, o valor em grande) e «Criar vales
 * numerados» põe o template e os algarismos na sessão: o resto (séries, QR de verificação, folhas) é o gerador de rifas, no ecrã principal.
 */
export function Vales({ desenho, moeda, organizacao }: Props) {
  const { t, lingua } = useI18n();
  const s = useSessao();
  const [titulo, setTitulo] = useState(() => t("web_vales_cabecalho_padrao"));
  const [singular, setSingular] = useState("");
  const [quantidade, setQuantidade] = useState("1");
  const [nota, setNota] = useState("");
  const [org, setOrg] = useState("");
  const [previa, setPrevia] = useState("");
  const [erro, setErro] = useState("");
  const contador = useRef(0);
  const q = Number.parseInt(quantidade, 10);
  const pedido: PedidoVale = {
    desenho,
    titulo,
    organizacao: org || organizacao,
    moeda: singular || singularDe(moeda),
    moeda_plural: moeda,
    quantidade: Number.isFinite(q) ? q : 0,
    nota,
  };
  const chave = JSON.stringify(pedido);

  // biome-ignore lint/correctness/useExhaustiveDependencies: `chave` resume o pedido inteiro
  useEffect(() => {
    const ctl = new AbortController();
    const eu = ++contador.current;
    const espera = setTimeout(() => {
      api
        .valesPrevia(pedido, ctl.signal)
        .then((b) => {
          if (eu !== contador.current) return;
          setPrevia((antes) => {
            if (antes) URL.revokeObjectURL(antes);
            return URL.createObjectURL(b);
          });
          setErro("");
        })
        .catch((x: unknown) => {
          if (x instanceof DOMException && x.name === "AbortError") return;
          if (eu === contador.current) setErro(x instanceof ErroApi ? x.message : String(x));
        });
    }, ATRASO_MS);
    return () => {
      clearTimeout(espera);
      ctl.abort();
    };
  }, [chave, lingua]);

  return (
    <section className="cartao texto-pagina vales" data-testid="vales">
      <h2>{t("web_vales_titulo")}</h2>
      <p>{t("web_vales_intro")}</p>
      <div className="vales-campos">
        <label>
          {t("web_vales_cabecalho")}
          <input
            data-testid="vales-titulo"
            maxLength={24}
            value={titulo}
            onChange={(ev) => setTitulo(ev.target.value)}
          />
        </label>
        <label>
          {t("web_vales_singular")}
          <input
            data-testid="vales-singular"
            maxLength={14}
            placeholder={singularDe(moeda)}
            value={singular}
            onChange={(ev) => setSingular(ev.target.value)}
          />
        </label>
        <label>
          {t("web_vales_quantidade")}
          <input
            data-testid="vales-quantidade"
            inputMode="numeric"
            maxLength={2}
            value={quantidade}
            onChange={(ev) => setQuantidade(ev.target.value.replace(/\D/g, ""))}
          />
        </label>
        <label>
          {t("web_galeria_organizacao")}
          <input
            data-testid="vales-organizacao"
            maxLength={50}
            placeholder={organizacao}
            value={org}
            onChange={(ev) => setOrg(ev.target.value)}
          />
        </label>
        <label>
          {t("web_vales_nota")}
          <input
            data-testid="vales-nota"
            maxLength={60}
            value={nota}
            onChange={(ev) => setNota(ev.target.value)}
          />
        </label>
      </div>
      {previa && (
        <img className="vales-previa" src={previa} alt={t("web_vales_previa")} data-testid="vales-previa" />
      )}
      {erro && (
        <p role="alert" data-testid="vales-erro">
          {erro}
        </p>
      )}
      <button
        type="button"
        className="botao"
        data-testid="vales-criar"
        disabled={!!erro || !previa}
        onClick={() => void s.usarVales(pedido, () => navegar("/"))}
      >
        {t("web_vales_criar")}
      </button>
    </section>
  );
}
