import { useEffect, useRef, useState } from "react";
import { useDialogos } from "./dialogos";
import { useI18n } from "./i18n";
import { Voltar } from "./paginas";
import { lerExcluir, MAX_NUMEROS, MAX_QUANTOS, MAX_SEMENTE, sortear } from "./sorteador";

interface Campos {
  de: string;
  ate: string;
  n: string;
  s: string;
  x: string;
}

function lerPesquisa(pesquisa: string): Partial<Campos> {
  const p = new URLSearchParams(pesquisa);
  const saida: Partial<Campos> = {};
  for (const k of ["de", "ate", "n"] as const) {
    const v = p.get(k);
    if (v && /^\d{1,9}$/.test(v)) saida[k] = v;
  }
  const s = p.get("s");
  if (s && s.length <= MAX_SEMENTE) saida.s = s;
  const x = p.get("x");
  if (x && /^[0-9 ,-]{1,300}$/.test(x)) saida.x = x;
  return saida;
}

/** O endereço que repete este sorteio: quem o abrir vê os mesmos números. */
export function ligacaoDoSorteio(c: Campos, base: string): string {
  const p = new URLSearchParams({ de: c.de, ate: c.ate, n: c.n, s: c.s.trim() });
  if (c.x.trim()) p.set("x", c.x.trim());
  return `${base}?${p.toString()}`;
}

/**
 * Sorteio verificável (M7): o resultado só depende dos números, de quantos se sorteiam, dos números saltados e da semente pública;
 * qualquer pessoa repete o sorteio com a ligação. Faz-se tudo no browser: nada vai ao servidor.
 */
export function Sorteio() {
  const { t } = useI18n();
  const { aviso } = useDialogos();
  const inicial = useRef(lerPesquisa(window.location.search));
  const [c, setC] = useState<Campos>({
    de: inicial.current.de ?? "1",
    ate: inicial.current.ate ?? "100",
    n: inicial.current.n ?? "1",
    s: inicial.current.s ?? "",
    x: inicial.current.x ?? "",
  });
  const [resultado, setResultado] = useState<number[] | null>(null);
  const [erro, setErro] = useState("");

  const executar = (campos: Campos) => {
    setErro("");
    setResultado(null);
    const excluir = lerExcluir(campos.x);
    if (excluir === null) return setErro(t("err_saltar"));
    if (!campos.s.trim() || campos.s.trim().length > MAX_SEMENTE)
      return setErro(t("web_sorteio_erro_semente", { max: MAX_SEMENTE }));
    const r = sortear(Number(campos.de), Number(campos.ate), Number(campos.n), campos.s, excluir);
    if (r === null)
      return setErro(
        t("web_sorteio_erro_numeros", { max: MAX_NUMEROS.toLocaleString("pt-PT"), quantos: MAX_QUANTOS }),
      );
    setResultado(r);
    window.history.replaceState(null, "", ligacaoDoSorteio(campos, window.location.pathname));
  };

  // uma ligação partilhada com tudo preenchido repete logo o sorteio
  // biome-ignore lint/correctness/useExhaustiveDependencies: só ao abrir a página
  useEffect(() => {
    const i = inicial.current;
    if (i.de && i.ate && i.n && i.s) executar({ de: i.de, ate: i.ate, n: i.n, s: i.s, x: i.x ?? "" });
  }, []);

  const mudar = (k: keyof Campos, v: string) => setC((x) => ({ ...x, [k]: v }));

  const usarDrand = async () => {
    try {
      const r = await fetch("https://api.drand.sh/public/latest");
      const d = (await r.json()) as { round?: number; randomness?: string };
      if (!r.ok || typeof d.round !== "number" || typeof d.randomness !== "string")
        throw new Error("resposta inesperada");
      mudar("s", `drand:${d.round}:${d.randomness}`);
    } catch {
      aviso(t("web_sorteio_drand_erro"), "aviso");
    }
  };

  const copiar = async () => {
    const ligacao = ligacaoDoSorteio(c, `${window.location.origin}${window.location.pathname}`);
    try {
      await navigator.clipboard.writeText(ligacao);
      aviso(t("web_ligacao_copiada"), "aviso");
    } catch {
      aviso(ligacao, "aviso");
    }
  };

  return (
    <div className="pagina">
      <section className="cartao sorteio">
        <h1>{t("web_sorteio")}</h1>
        <p className="texto-longo">{t("web_sorteio_intro")}</p>
        <div className="linha">
          <label>
            {t("de")}
            <input
              value={c.de}
              onChange={(e) => mudar("de", e.target.value)}
              inputMode="numeric"
              data-testid="sorteio-de"
            />
          </label>
          <label>
            {t("ate")}
            <input
              value={c.ate}
              onChange={(e) => mudar("ate", e.target.value)}
              inputMode="numeric"
              data-testid="sorteio-ate"
            />
          </label>
          <label>
            {t("web_sorteio_quantos")}
            <input
              value={c.n}
              onChange={(e) => mudar("n", e.target.value)}
              inputMode="numeric"
              data-testid="sorteio-n"
            />
          </label>
        </div>
        <label>
          {t("web_saltar")}
          <input
            value={c.x}
            onChange={(e) => mudar("x", e.target.value)}
            placeholder="13, 100-110"
            data-testid="sorteio-x"
          />
        </label>
        <label>
          {t("web_sorteio_semente")}
          <input
            value={c.s}
            onChange={(e) => mudar("s", e.target.value)}
            maxLength={MAX_SEMENTE}
            autoComplete="off"
            aria-describedby="dica-semente"
            data-testid="sorteio-semente"
          />
        </label>
        <p className="suave dica" id="dica-semente">
          {t("web_sorteio_semente_dica")}
        </p>
        <div className="botoes">
          <button
            type="button"
            className="secundario"
            onClick={() => void usarDrand()}
            data-testid="sorteio-drand"
          >
            {t("web_sorteio_drand")}
          </button>
          <button type="button" onClick={() => executar(c)} data-testid="sorteio-sortear">
            {t("web_sorteio_sortear")}
          </button>
        </div>
        {erro && (
          <p role="alert" className="cor-aviso" data-testid="sorteio-erro">
            {erro}
          </p>
        )}
        {resultado && (
          <div className="sorteados" data-testid="sorteio-resultado">
            <h2>{t("web_sorteio_resultado")}</h2>
            <ol>
              {resultado.map((n, i) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: a posição é o que identifica cada prémio
                <li key={i}>{n}</li>
              ))}
            </ol>
            <button
              type="button"
              className="texto"
              onClick={() => void copiar()}
              data-testid="sorteio-copiar"
            >
              {t("web_copiar_ligacao")}
            </button>
          </div>
        )}
        <p className="suave">{t("web_sorteio_como")}</p>
        <Voltar />
      </section>
    </div>
  );
}
