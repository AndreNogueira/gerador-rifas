import { useEffect, useState } from "react";
import { api, ErroApi, type GuiaDeTexto } from "./api";
import { OutrosGuias } from "./IndiceGuias";
import { useI18n } from "./i18n";
import { Voltar } from "./paginas";
import { Ligacao } from "./rota";

/** Os caminhos dos guias «como fazer» (`web/guias`): o nome na API e o URL (o servidor tem a mesma tabela em `guias.CAMINHOS`). */
export const GUIAS: Record<string, string> = {
  "/rifas-para-escolas": "escolas",
  "/rifas-para-associacoes": "associacoes",
  "/rifas-para-clubes": "clubes",
  "/rifas-para-bombeiros": "bombeiros",
  "/rifas-para-festas": "festas",
  "/rifas-para-igrejas": "igrejas",
};

/**
 * «Como fazer uma rifa para a escola / a associação»: texto escrito (título, introdução, 5 passos e 3 dicas) na língua escolhida, que o servidor
 * também põe no HTML estático para os motores de pesquisa, e ligações para o gerador, o editor e o tutorial.
 */
export function Guia({ nome }: { nome: string }) {
  const { lingua, t } = useI18n();
  const [guia, setGuia] = useState<GuiaDeTexto | null>(null);
  const [erro, setErro] = useState("");
  // biome-ignore lint/correctness/useExhaustiveDependencies: o guia pede-se de novo quando a língua muda
  useEffect(() => {
    let ativo = true;
    setGuia(null);
    setErro("");
    api
      .guia(nome)
      .then((d) => ativo && setGuia(d))
      .catch((e: unknown) => ativo && setErro(e instanceof ErroApi ? e.message : String(e)));
    return () => {
      ativo = false;
    };
  }, [nome, lingua]);
  useEffect(() => {
    if (guia) document.title = `${guia.titulo} | ${t("app_nome")}`;
  }, [guia, t]);
  return (
    <div className="pagina">
      <article className="cartao texto-pagina guia" data-testid={`guia-${nome}`}>
        <h1>{guia ? guia.titulo : "…"}</h1>
        {erro && <p role="alert">{erro}</p>}
        {!guia && !erro && <p aria-busy="true">…</p>}
        {guia && (
          <>
            <p className="texto-longo">{guia.intro}</p>
            <ol className="guia-passos">
              {guia.passos.map((p) => (
                <li key={p.titulo}>
                  <h2>{p.titulo}</h2>
                  <p>{p.texto}</p>
                </li>
              ))}
            </ol>
            <ul className="guia-dicas">
              {guia.dicas.map((d) => (
                <li key={d}>{d}</li>
              ))}
            </ul>
            <p>{guia.fim}</p>
            <p className="guia-ligacoes">
              <Ligacao para="/" className="botao" data-testid="guia-gerador">
                {t("app_nome")}
              </Ligacao>
              <Ligacao para="/editor" className="botao secundario">
                {t("web_editor")}
              </Ligacao>
              <Ligacao para="/tutorial" className="botao secundario">
                {t("tut_titulo")}
              </Ligacao>
            </p>
            <OutrosGuias menos={nome} />
          </>
        )}
        <Voltar />
      </article>
    </div>
  );
}
