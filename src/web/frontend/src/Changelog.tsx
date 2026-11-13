import { useEffect, useState } from "react";
import { api, type EntradaChangelog, ErroApi } from "./api";
import { useI18n } from "./i18n";
import { Voltar } from "./paginas";

/** A última versão da app Windows, descarregada direto do repositório público (só tem o programa, sem código-fonte). */
export const DESCARGA_WINDOWS =
  "https://github.com/AndreNogueira/gerador-rifas-windows/releases/latest/download/GeradorRifas.exe";

/** O changelog: em português é o completo (`src/web/CHANGELOG.md`); nas outras línguas o servidor devolve um resumo traduzido de cada versão. */
export function Changelog() {
  const { t, lingua } = useI18n();
  const [entradas, setEntradas] = useState<EntradaChangelog[] | null>(null);
  const [erro, setErro] = useState("");
  // biome-ignore lint/correctness/useExhaustiveDependencies: o changelog pede-se de novo quando a língua muda
  useEffect(() => {
    let ativo = true;
    setErro("");
    api
      .changelog()
      .then((d) => ativo && setEntradas(d.entradas))
      .catch((e: unknown) => ativo && setErro(e instanceof ErroApi ? e.message : String(e)));
    return () => {
      ativo = false;
    };
  }, [lingua]);
  return (
    <div className="pagina">
      <section className="cartao changelog">
        <h1>Changelog</h1>
        <p className="suave">{t("web_changelog_sub")}</p>
        <p>
          <a
            className="botao secundario"
            href={DESCARGA_WINDOWS}
            rel="noopener noreferrer"
            data-testid="descarga-windows"
          >
            {t("web_changelog_windows")}
          </a>
        </p>
        {lingua !== "pt" && (
          <p className="aviso-pagina" data-testid="changelog-resumo">
            {t("web_changelog_resumo")}
          </p>
        )}
        {erro && <p role="alert">{erro}</p>}
        {!entradas && !erro && <p aria-busy="true">…</p>}
        {entradas?.map((e) => (
          <article key={e.versao} data-testid={`versao-${e.versao}`}>
            <h2>
              {t("web_versao", { versao: e.versao })} <time dateTime={e.data}>{e.data}</time>
            </h2>
            {e.seccoes.map((s) => (
              <div key={s.titulo}>
                <h3>{s.titulo}</h3>
                <ul>
                  {s.itens.map((i) => (
                    <li key={i}>{i}</li>
                  ))}
                </ul>
              </div>
            ))}
          </article>
        ))}
        <Voltar />
      </section>
    </div>
  );
}
