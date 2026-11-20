import { useState } from "react";
import type { PrecarioCatalogo } from "./api";
import { useI18n } from "./i18n";

const MIN = 2;
const MAX = 4;
const RANHURAS = ["primeiro", "segundo", "terceiro", "quarto"]; // as 4 listas (a chave de cada uma)

/**
 * O formulário de um combo (um «menu»): 2 a 4 artigos do catálogo, de qualquer secção, num só preço (uma bifana e uma bebida…), com um nome opcional;
 * o combo vai para a secção «Menus e combos» e, sem nome, chama-se pelos nomes dos artigos unidos por « + ».
 */
export function CriarCombo({
  cat,
  limiteNome,
  cheio,
  aoJuntar,
}: {
  cat: PrecarioCatalogo;
  limiteNome: number;
  cheio: boolean;
  aoJuntar: (artigos: string[], nome: string) => void;
}) {
  const { t } = useI18n();
  const [escolhas, setEscolhas] = useState<string[]>(["", "", "", ""]);
  const [nome, setNome] = useState("");
  const validos = escolhas.filter(Boolean);
  const pode = !cheio && validos.length >= MIN && new Set(validos).size === validos.length;
  const juntar = () => {
    if (!pode) return;
    aoJuntar(validos.slice(0, MAX), nome.trim());
    setEscolhas(["", "", "", ""]);
    setNome("");
  };
  return (
    <fieldset className="precario-categoria precario-combo" data-testid="precario-combo">
      <legend>{t("web_precario_combos")}</legend>
      <p className="suave">{t("web_precario_combos_dica")}</p>
      <div className="precario-combo-artigos">
        {RANHURAS.map((ranhura, i) => (
          <label key={ranhura}>
            <span className="so-leitores">{t("web_precario_combo_artigo", { n: i + 1 })}</span>
            <select
              data-testid={`precario-combo-artigo-${i + 1}`}
              value={escolhas[i]}
              onChange={(ev) => setEscolhas(escolhas.map((x, k) => (k === i ? ev.target.value : x)))}
            >
              <option value="">
                {i < MIN ? t("web_precario_combo_artigo", { n: i + 1 }) : t("web_precario_combo_nenhum")}
              </option>
              {cat.categorias
                .filter((c) => c.artigos.length > 0)
                .map((c) => (
                  <optgroup key={c.id} label={c.nome}>
                    {c.artigos.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.nome}
                      </option>
                    ))}
                  </optgroup>
                ))}
            </select>
          </label>
        ))}
      </div>
      <div className="precario-meu">
        <input
          data-testid="precario-combo-nome"
          placeholder={t("web_precario_combo_nome")}
          aria-label={t("web_precario_combo_nome")}
          maxLength={limiteNome}
          value={nome}
          onChange={(ev) => setNome(ev.target.value)}
          onKeyDown={(ev) => ev.key === "Enter" && juntar()}
        />
        <button
          type="button"
          className="botao secundario"
          data-testid="precario-combo-juntar"
          disabled={!pode}
          onClick={juntar}
        >
          {t("web_precario_combo_juntar")}
        </button>
      </div>
    </fieldset>
  );
}
