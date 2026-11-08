import type { Campos } from "./api";
import { useI18n } from "./i18n";
import { aCorrer, useSessao } from "./sessao";

const POSICOES = [
  { id: "se", seta: "↖" },
  { id: "sd", seta: "↗" },
  { id: "ie", seta: "↙" },
  { id: "id", seta: "↘" },
] as const;

/**
 * A marca própria: a cor dos números (qualquer template) e o logótipo da associação em cada rifa (só templates de uma rifa, que a
 * folha repete: é onde se sabe onde cada rifa começa). O logótipo vai ao servidor para a sessão e apaga-se com ela.
 */
export function MarcaPropria({
  campos,
  mudar,
}: {
  campos: Campos;
  mudar: (c: keyof Campos, v: string) => void;
}) {
  const { t } = useI18n();
  const s = useSessao();
  const sessao = s.sessao;
  const parado = !sessao || aCorrer(sessao) || s.ocupado !== null;
  return (
    <div className="marca-propria">
      <label>
        {t("web_cor_numeros")}
        <span className="cor-controlo">
          <input
            type="color"
            value={campos.cor_numeros || "#000000"}
            onChange={(e) => mudar("cor_numeros", e.target.value.toUpperCase())}
            data-testid="cor-numeros"
          />
          {campos.cor_numeros && (
            <button
              type="button"
              className="texto"
              aria-label={`${t("web_cor_numeros")}: ✕`}
              onClick={() => mudar("cor_numeros", "")}
              data-testid="cor-numeros-limpar"
            >
              ✕
            </button>
          )}
        </span>
      </label>
      {sessao?.info?.tem_folha && (
        <>
          <label>
            {t("web_logotipo")}
            <input
              type="file"
              accept="image/png,image/jpeg"
              disabled={parado}
              data-testid="upload-logotipo"
              onChange={(e) => {
                const f = e.target.files?.[0];
                e.target.value = ""; // permite escolher o mesmo ficheiro outra vez
                if (f) void s.carregarLogotipo(f);
              }}
            />
          </label>
          {sessao.logotipo && (
            <p className="suave">
              <span data-testid="logotipo-nome">{sessao.logotipo}</span>{" "}
              <button
                type="button"
                className="texto"
                disabled={parado}
                onClick={() => void s.removerLogotipo()}
                data-testid="remover-logotipo"
              >
                {t("web_logo_remover")}
              </button>
            </p>
          )}
          <div className="linha extras">
            <label>
              {t("web_logo_posicao")}
              <select
                value={campos.logo_posicao}
                onChange={(e) => mudar("logo_posicao", e.target.value)}
                data-testid="logo-posicao"
              >
                {POSICOES.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.seta}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("web_logo_tamanho")}
              <input
                type="range"
                min={10}
                max={40}
                step={5}
                value={Number(campos.logo_tamanho) || 25}
                onChange={(e) => mudar("logo_tamanho", e.target.value)}
                data-testid="logo-tamanho"
              />
            </label>
          </div>
        </>
      )}
    </div>
  );
}
