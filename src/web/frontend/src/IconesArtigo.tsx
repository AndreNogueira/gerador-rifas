import { useI18n } from "./i18n";

/** O ficheiro de um ícone, pelo seu id: um código Noto Emoji sozinho ("1f382") ou "<fonte>:<código>" de outra
 * biblioteca ("fluent:1f382", numa subpasta — o mesmo que `core.precario.caminho_icone` no servidor). */
function caminhoIcone(id: string): string {
  const i = id.indexOf(":");
  return i === -1 ? `/precario/${id}.webp` : `/precario/${id.slice(0, i)}/${id.slice(i + 1)}.webp`;
}

/** O nome de cada biblioteca de ícones, pelo prefixo do id ("" = Noto Emoji, sem prefixo): espelho de
 * `core.precario_catalogo.FONTES_EXTRA` (nomes próprios, não se traduzem — `tests/test_web_api.py` verifica que
 * bate certo com o servidor). */
export const NOME_FONTE: Record<string, string> = {
  "": "Noto Emoji",
  fluent: "Fluent Emoji",
  twemoji: "Twemoji",
  openmoji: "OpenMoji",
  tabler: "Tabler Icons",
  lucide: "Lucide",
  material: "Material Symbols",
};

/** Bibliotecas de contorno (preto sobre transparente, ver scripts/gerar_icones_precario.py): pintam-se da cor do
 * texto do momento (`mask-image`, não `<img>`), em vez de aparecerem sempre a preto — invisíveis no tema escuro.
 * Espelho de `core.precario_catalogo.FONTES_EXTRA[fonte].monocromatica`. */
const MONOCROMATICAS = new Set(["tabler", "lucide", "material"]);

function fonteDoId(id: string): string {
  const i = id.indexOf(":");
  return i === -1 ? "" : id.slice(0, i);
}

/** A imagem (o ícone) de um artigo do preçário: o emoji do catálogo em miniatura, ou um espaço em branco se não há. */
export function Miniatura({ emoji, className = "" }: { emoji: string; className?: string }) {
  if (!emoji) return <span className={`precario-sem-imagem ${className}`} aria-hidden="true" />;
  if (MONOCROMATICAS.has(fonteDoId(emoji))) {
    return (
      <span
        className={`precario-icone-linha ${className}`}
        style={{ maskImage: `url(${caminhoIcone(emoji)})`, WebkitMaskImage: `url(${caminhoIcone(emoji)})` }}
        aria-hidden="true"
      />
    );
  }
  return (
    <img
      className={className}
      src={caminhoIcone(emoji)}
      alt=""
      width={28}
      height={28}
      loading="lazy"
      decoding="async"
    />
  );
}

/** As imagens que o catálogo oferece a um artigo (até 56, entre o Noto Emoji curado e outras bibliotecas): a pessoa escolhe a que mais gosta; a de omissão é a primeira. */
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
  // agrupadas por biblioteca (a ordem em que aparecem pela 1.ª vez: o Noto Emoji vem sempre primeiro, por construção
  // do catálogo), mas o índice de cada botão (para o aria-label e o data-testid) é o da lista toda, não o do grupo
  const porFonte = new Map<string, { codigo: string; i: number }[]>();
  icones.forEach((codigo, i) => {
    const fonte = fonteDoId(codigo);
    const itens = porFonte.get(fonte) ?? [];
    itens.push({ codigo, i });
    porFonte.set(fonte, itens);
  });
  const grupos = [...porFonte.entries()].map(([fonte, itens]) => ({ fonte, itens }));
  return (
    <fieldset className="precario-icones">
      <legend className="so-leitores">{`${t("web_precario_icone")}: ${nome}`}</legend>
      {grupos.map((g) => (
        <div className="precario-icones-fonte" key={g.fonte}>
          {grupos.length > 1 && (
            <p className="precario-icones-fonte-nome">{NOME_FONTE[g.fonte] ?? g.fonte}</p>
          )}
          <div className="precario-icones-linha">
            {g.itens.map(({ codigo, i }) => (
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
          </div>
        </div>
      ))}
    </fieldset>
  );
}
