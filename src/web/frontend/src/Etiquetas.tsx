import { useEffect, useState } from "react";
import { api, ErroApi, type PedidoPrecario } from "./api";
import { useDialogos } from "./dialogos";
import { guardarBlob } from "./Gerador";
import { useI18n } from "./i18n";

const CHAVE = "rifas.etiquetas";
const POR_FOLHA = 24;
const MAX_COPIAS = 99;

interface Guardado {
  zonas: Record<string, string>;
  copias: number;
  preco: boolean;
}

function lerGuardado(): Guardado {
  try {
    const g = JSON.parse(localStorage.getItem(CHAVE) ?? "null") as Partial<Guardado> | null;
    const zonas: Record<string, string> = {};
    for (const [k, v] of Object.entries(g?.zonas ?? {})) if (typeof v === "string") zonas[k] = v.slice(0, 20);
    const copias = Number.isInteger(g?.copias) ? Math.min(MAX_COPIAS, Math.max(1, g?.copias as number)) : 10;
    return { zonas, copias, preco: g?.preco !== false };
  } catch {
    return { zonas: {}, copias: 10, preco: true };
  }
}

/**
 * As etiquetas de levantamento: paga-se num sítio e levanta-se noutro. Cada artigo do preçário vira uma etiqueta com a imagem, o nome e a zona onde se levanta
 * (a zona de cada secção); um combo dá uma etiqueta por artigo, cada uma na zona da sua secção. Imprimem-se `copias` de cada artigo, 24 por folha A4.
 * As zonas e o número de cópias ficam só neste browser (nada vai para o servidor além do pedido que desenha o PDF).
 */
export function Etiquetas({
  pedido,
  secoes,
  total,
}: {
  pedido: PedidoPrecario | null;
  /** As secções que as etiquetas levam (as dos artigos escolhidos e as dos artigos dos combos), pela ordem do catálogo. */
  secoes: { id: string; nome: string }[];
  /** Quantos artigos diferentes dão etiqueta (um combo conta um por artigo). */
  total: number;
}) {
  const { t } = useI18n();
  const { aviso } = useDialogos();
  const [g, setG] = useState<Guardado>(lerGuardado);
  const [previa, setPrevia] = useState("");
  const [copiasTexto, setCopiasTexto] = useState(String(g.copias)); // o que se escreve (pode estar vazio a meio); `g.copias` é sempre 1 a 99
  const [a, setA] = useState(false);

  useEffect(() => {
    try {
      localStorage.setItem(CHAVE, JSON.stringify(g));
    } catch {
      /* sem armazenamento */
    }
  }, [g]);
  useEffect(
    () => () => {
      if (previa) URL.revokeObjectURL(previa);
    },
    [previa],
  );

  const pedidoEtiquetas = () =>
    pedido
      ? {
          precario: pedido,
          zonas: Object.fromEntries(
            secoes.map((s) => [s.id, (g.zonas[s.id] ?? "").trim()] as const).filter(([, z]) => z),
          ),
          copias: g.copias,
          preco: g.preco,
        }
      : null;
  const senhas = total * g.copias;
  const folhas = Math.max(1, Math.ceil(senhas / POR_FOLHA));

  const descarregar = async () => {
    const p = pedidoEtiquetas();
    if (!p) return;
    try {
      guardarBlob(await api.precarioEtiquetasPdf(p), "etiquetas.pdf");
    } catch (x) {
      aviso(x instanceof ErroApi ? x.message : String(x));
    }
  };
  const ver = async () => {
    const p = pedidoEtiquetas();
    if (!p) return;
    setA(true);
    try {
      const b = await api.precarioEtiquetasPrevia(p);
      setPrevia(URL.createObjectURL(b));
    } catch (x) {
      aviso(x instanceof ErroApi ? x.message : String(x));
    } finally {
      setA(false);
    }
  };

  return (
    <section className="cartao texto-pagina precario-etiquetas" data-testid="precario-etiquetas">
      <h2>{t("web_etiquetas_titulo")}</h2>
      <p className="suave">{t("web_etiquetas_intro")}</p>
      <fieldset className="precario-categoria">
        <legend>{t("web_etiquetas_zona")}</legend>
        {secoes.map((s) => (
          <label key={s.id} className="precario-linha precario-linha-categoria">
            <span>{s.nome}</span>
            <input
              data-testid={`etiquetas-zona-${s.id}`}
              placeholder={t("web_etiquetas_zona_ex")}
              maxLength={20}
              value={g.zonas[s.id] ?? ""}
              onChange={(ev) => setG({ ...g, zonas: { ...g.zonas, [s.id]: ev.target.value } })}
            />
          </label>
        ))}
      </fieldset>
      <label>
        {t("web_etiquetas_copias")}
        <input
          type="number"
          min={1}
          max={MAX_COPIAS}
          data-testid="etiquetas-copias"
          value={copiasTexto}
          onChange={(ev) => {
            setCopiasTexto(ev.target.value);
            const n = Math.trunc(Number(ev.target.value));
            if (n >= 1 && n <= MAX_COPIAS) setG({ ...g, copias: n });
          }}
          onBlur={() => setCopiasTexto(String(g.copias))}
        />
      </label>
      <label className="precario-caixa">
        <input
          type="checkbox"
          data-testid="etiquetas-preco"
          checked={g.preco}
          onChange={(ev) => setG({ ...g, preco: ev.target.checked })}
        />
        {t("web_etiquetas_preco")}
      </label>
      <p className="suave" data-testid="etiquetas-total">
        {t("web_etiquetas_total", { n: senhas, folhas })}
      </p>
      <div className="precario-acoes">
        <button
          type="button"
          className="botao"
          data-testid="etiquetas-pdf"
          disabled={!pedido || total === 0}
          onClick={() => void descarregar()}
        >
          {t("web_etiquetas_pdf")}
        </button>
        <button
          type="button"
          className="botao secundario"
          data-testid="etiquetas-ver"
          disabled={!pedido || total === 0 || a}
          onClick={() => void ver()}
        >
          {t("web_etiquetas_ver")}
        </button>
      </div>
      {previa && (
        <img
          className="etiquetas-previa"
          src={previa}
          alt={t("web_etiquetas_titulo")}
          data-testid="etiquetas-previa"
        />
      )}
    </section>
  );
}
