import { useI18n } from "./i18n";

/** A imagem (o ícone) de um artigo do preçário: o emoji do catálogo em miniatura, ou um espaço em branco se não há. */
export function Miniatura({ emoji, className = "" }: { emoji: string; className?: string }) {
  if (!emoji) return <span className={`precario-sem-imagem ${className}`} aria-hidden="true" />;
  return (
    <img
      className={className}
      src={`/precario/${emoji}.webp`}
      alt=""
      width={28}
      height={28}
      loading="lazy"
      decoding="async"
    />
  );
}

/** As imagens que o catálogo oferece a um artigo (até 8): a pessoa escolhe a que mais gosta; a de omissão é a primeira. */
export function IconesArtigo({
  chave,
  nome,
  icones,
  atual,
  aoEscolher,
}: {
  chave: string;
  nome: string;
  icones: string[];
  atual: string;
  aoEscolher: (emoji: string) => void;
}) {
  const { t } = useI18n();
  return (
    <fieldset className="precario-icones">
      <legend className="so-leitores">{`${t("web_precario_icone")}: ${nome}`}</legend>
      {icones.map((codigo, i) => (
        <button
          key={codigo}
          type="button"
          className={`precario-icone${codigo === atual ? " ligada" : ""}`}
          aria-pressed={codigo === atual}
          aria-label={`${t("web_precario_icone_n", { n: i + 1 })}: ${nome}`}
          data-testid={`precario-icone-${chave}-${i + 1}`}
          onClick={() => aoEscolher(codigo)}
        >
          <Miniatura emoji={codigo} />
        </button>
      ))}
    </fieldset>
  );
}
