import { useRef } from "react";
import { useDialogos } from "./dialogos";
import { LOGO_LADO, prepararFoto } from "./foto";
import { useI18n } from "./i18n";

const NOMES_COR = [
  "web_precario_cor_principal",
  "web_precario_cor_destaque",
  "web_precario_cor_papel",
] as const;

/**
 * As cores do preçário (principal, destaque e papel: parte das do desenho e a pessoa muda as que quiser) e o logótipo (PNG ou JPG, reduzido aqui no browser) com o sítio onde fica.
 * O logótipo só vai no pedido que desenha a pré-visualização e o PDF: não se guarda (nem no rascunho, nem na ligação partilhada).
 */
export function CoresELogo({
  cores,
  padroes,
  logo,
  lugar,
  lugares,
  aoMudarCores,
  aoMudarLogo,
  aoMudarLugar,
}: {
  cores: string[];
  padroes: string[];
  logo: string;
  lugar: string;
  lugares: string[];
  aoMudarCores: (cores: string[]) => void;
  aoMudarLogo: (logo: string) => void;
  aoMudarLugar: (lugar: string) => void;
}) {
  const { t } = useI18n();
  const { aviso } = useDialogos();
  const ficheiro = useRef<HTMLInputElement>(null);
  const escolher = async (f: File | undefined) => {
    if (!f) return;
    try {
      aoMudarLogo(await prepararFoto(f, LOGO_LADO));
    } catch {
      aviso(t("err_logotipo", { mb: 2 }));
    }
  };
  return (
    <fieldset className="precario-cores-logo">
      <legend>{t("web_precario_cores")}</legend>
      <div className="precario-cores">
        {NOMES_COR.map((chave, i) => (
          <label key={chave} className="precario-cor">
            <input
              type="color"
              data-testid={`precario-cor-${i}`}
              value={cores[i] || padroes[i] || "#000000"}
              onChange={(ev) => aoMudarCores(cores.map((c, k) => (k === i ? ev.target.value : c)))}
            />
            <span>{t(chave)}</span>
          </label>
        ))}
      </div>
      <button
        type="button"
        className="botao secundario"
        data-testid="precario-cores-repor"
        disabled={cores.every((c) => !c)}
        onClick={() => aoMudarCores(["", "", ""])}
      >
        {t("web_precario_cores_repor")}
      </button>
      <h3 className="precario-sub">{t("web_precario_logo")}</h3>
      <div className="precario-logo">
        {logo ? (
          <>
            <img src={logo} alt="" className="precario-logo-mini" data-testid="precario-logo-mini" />
            <button
              type="button"
              className="botao secundario"
              data-testid="precario-logo-tirar"
              onClick={() => aoMudarLogo("")}
            >
              {t("web_precario_logo_tirar")}
            </button>
          </>
        ) : (
          <>
            <button type="button" className="botao secundario" onClick={() => ficheiro.current?.click()}>
              {t("web_precario_logo_escolher")}
            </button>
            <input
              ref={ficheiro}
              type="file"
              accept="image/png,image/jpeg"
              hidden
              data-testid="precario-logo"
              aria-label={t("web_precario_logo_escolher")}
              onChange={(ev) => {
                void escolher(ev.target.files?.[0]);
                ev.target.value = "";
              }}
            />
          </>
        )}
      </div>
      <label className="precario-logo-onde">
        {t("web_precario_logo_onde")}
        <select
          data-testid="precario-logo-lugar"
          value={lugar}
          disabled={!logo}
          onChange={(ev) => aoMudarLugar(ev.target.value)}
        >
          {lugares.map((l) => (
            <option key={l} value={l}>
              {t(`web_precario_logo_${l}`)}
            </option>
          ))}
        </select>
      </label>
      <p className="suave">{t("web_precario_logo_dica")}</p>
    </fieldset>
  );
}
