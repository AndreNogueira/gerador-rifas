import { useEffect, useState } from "react";
import { api } from "./api";
import { useI18n } from "./i18n";

/** Os 4 passos da app Windows. Por agora só os títulos: os cartões a sério vêm nas fases seguintes (ver webapp/PLANO.md). */
const PASSOS = ["c1_titulo", "c2_titulo", "c3_titulo", "c4_titulo"] as const;

export function App() {
  const { t, lingua, linguas, mudarLingua } = useI18n();
  const [versao, setVersao] = useState<string | null>(null);

  useEffect(() => {
    api
      .saude()
      .then((s) => setVersao(s.versao))
      .catch(() => setVersao(null));
  }, []);

  return (
    <>
      <header className="topo">
        <h1>{t("app_nome")}</h1>
        <label>
          {t("m_idioma")}{" "}
          <select value={lingua} onChange={(e) => mudarLingua(e.target.value)} data-testid="lingua">
            {linguas.map((l) => (
              <option key={l.codigo} value={l.codigo}>
                {l.nome}
              </option>
            ))}
          </select>
        </label>
      </header>
      <main className="conteudo">
        <ol className="passos">
          {PASSOS.map((chave, i) => (
            <li key={chave} className="cartao">
              <span className="numero">{i + 1}</span> {t(chave)}
            </li>
          ))}
        </ol>
        <section className="visor" aria-label={t("previa_titulo")}>
          <h2>{t("previa_titulo")}</h2>
          <p>{t("previa_vazio")}</p>
        </section>
        <div className="acoes">
          <button type="button" disabled>
            {t("previa")}
          </button>
          <button type="button" disabled>
            {t("gerar")}
          </button>
        </div>
      </main>
      {versao && <footer className="rodape">v{versao}</footer>}
    </>
  );
}
