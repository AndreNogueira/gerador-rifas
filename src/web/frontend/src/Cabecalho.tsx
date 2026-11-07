import { useI18n } from "./i18n";
import { Ligacao, useLocalizacao } from "./rota";
import type { Tema } from "./tema";

const PAGINAS = [
  { para: "/tutorial", chave: "tut_titulo" },
  { para: "/video", chave: "mi_video" },
  { para: "/sobre", chave: "mi_sobre" },
] as const;

export function Cabecalho({ tema, mudarTema }: { tema: Tema; mudarTema: (t: Tema) => void }) {
  const { t, lingua, linguas, mudarLingua } = useI18n();
  const caminho = useLocalizacao().split("?")[0];
  return (
    <header className="topo">
      <Ligacao para="/" className="marca">
        <h1>{t("app_nome")}</h1>
      </Ligacao>
      <nav className="navegacao" aria-label={t("app_nome")}>
        {PAGINAS.map((p) => (
          <Ligacao
            key={p.para}
            para={p.para}
            aria-current={caminho === p.para ? "page" : undefined}
            data-testid={`nav-${p.para.slice(1)}`}
          >
            {t(p.chave).replace(/…$/, "")}
          </Ligacao>
        ))}
      </nav>
      <div className="definicoes">
        <label>
          <span className="so-leitores">{t("m_idioma")}</span>
          <select
            value={lingua}
            onChange={(e) => mudarLingua(e.target.value)}
            data-testid="lingua"
            aria-label={t("m_idioma")}
          >
            {linguas.map((l) => (
              <option key={l.codigo} value={l.codigo}>
                {l.nome}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span className="so-leitores">{t("mi_tema")}</span>
          <select
            value={tema}
            onChange={(e) => mudarTema(e.target.value as Tema)}
            data-testid="tema"
            aria-label={t("mi_tema")}
          >
            <option value="auto">{t("web_tema_auto")}</option>
            <option value="claro">{t("mi_tema_claro")}</option>
            <option value="escuro">{t("mi_tema_escuro")}</option>
          </select>
        </label>
      </div>
    </header>
  );
}
