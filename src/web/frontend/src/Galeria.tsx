import { useEffect, useRef, useState } from "react";
import { api, ErroApi } from "./api";
import { useI18n } from "./i18n";
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

interface Textos {
  titulo: string;
  organizacao: string;
  p1: string;
  p2: string;
  p3: string;
  data: string;
}
const VAZIOS: Textos = { titulo: "", organizacao: "", p1: "", p2: "", p3: "", data: "" };

/**
 * «Sem template? Escolha um da galeria»: um desenho, os textos da rifa, e «Usar este template» cria o template e os algarismos na sessão.
 * A pré-visualização desenha-se no servidor (com os textos escritos); as letras que a Vera não tem dão um aviso em vez de uma imagem.
 */
export function Galeria({ desativado }: { desativado: boolean }) {
  const { t } = useI18n();
  const s = useSessao();
  const [aberto, setAberto] = useState(false);
  const [desenho, setDesenho] = useState<string>(DESENHOS[0].id);
  const [f, setF] = useState<Textos>(VAZIOS);
  const [prev, setPrev] = useState<Textos>(VAZIOS);
  const [imagem, setImagem] = useState("");
  const [erro, setErro] = useState("");
  const anterior = useRef("");

  // os textos só vão ao servidor depois de uma pequena espera (não a cada tecla)
  useEffect(() => {
    const espera = setTimeout(() => setPrev(f), 400);
    return () => clearTimeout(espera);
  }, [f]);

  // a pré-visualização só se pede com a galeria aberta
  useEffect(() => {
    if (!aberto) return;
    const controlo = new AbortController();
    api
      .galeriaPrevia(
        { desenho, t: prev.titulo, o: prev.organizacao, p1: prev.p1, p2: prev.p2, p3: prev.p3, d: prev.data },
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

  const mudar = (campo: keyof Textos, valor: string) => setF((x) => ({ ...x, [campo]: valor }));
  const nomeDoDesenho = DESENHOS.find((d) => d.id === desenho)?.nome ?? "";

  return (
    <details className="galeria" data-testid="galeria" onToggle={(e) => setAberto(e.currentTarget.open)}>
      <summary>{t("web_galeria")}</summary>
      <fieldset className="desenhos" data-testid="desenhos">
        {DESENHOS.map((d) => (
          <label key={d.id} className="opcao">
            <input
              type="radio"
              name="desenho"
              value={d.id}
              checked={desenho === d.id}
              onChange={() => setDesenho(d.id)}
            />
            {d.nome}
          </label>
        ))}
      </fieldset>
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
        {(["p1", "p2", "p3"] as const).map((k) => (
          <input
            key={k}
            value={f[k]}
            onChange={(e) => mudar(k, e.target.value)}
            maxLength={50}
            aria-label={t("web_galeria_premios")}
          />
        ))}
      </fieldset>
      <label>
        {t("web_galeria_data")}
        <input value={f.data} onChange={(e) => mudar("data", e.target.value)} maxLength={30} />
      </label>
      <button
        type="button"
        disabled={desativado || !!erro}
        onClick={() =>
          void s.usarGaleria({
            desenho,
            titulo: f.titulo,
            organizacao: f.organizacao,
            premios: [f.p1, f.p2, f.p3].filter((p) => p.trim()),
            data: f.data,
          })
        }
        data-testid="galeria-usar"
      >
        {t("web_galeria_usar")}
      </button>
    </details>
  );
}
