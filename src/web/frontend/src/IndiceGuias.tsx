import { useEffect, useState } from "react";
import { api, ErroApi, type GuiaNaLista } from "./api";
import { useI18n } from "./i18n";
import { Ligacao } from "./rota";

/** Os guias «como fazer» na língua escolhida (o servidor devolve o título e o resumo de cada um; o mesmo que põe no HTML estático). */
export function useGuias(): { guias: GuiaNaLista[] | null; erro: string } {
  const { lingua } = useI18n();
  const [guias, setGuias] = useState<GuiaNaLista[] | null>(null);
  const [erro, setErro] = useState("");
  // biome-ignore lint/correctness/useExhaustiveDependencies: a lista pede-se de novo quando a língua muda
  useEffect(() => {
    let ativo = true;
    setGuias(null);
    setErro("");
    api
      .guias()
      .then((d) => ativo && setGuias(d.guias))
      .catch((e: unknown) => ativo && setErro(e instanceof ErroApi ? e.message : String(e)));
    return () => {
      ativo = false;
    };
  }, [lingua]);
  return { guias, erro };
}

export function ListaDeGuias({ guias }: { guias: GuiaNaLista[] }) {
  return (
    <ul className="lista-guias">
      {guias.map((g) => (
        <li key={g.nome}>
          <Ligacao para={g.caminho} data-testid={`indice-${g.nome}`}>
            {g.titulo}
          </Ligacao>
          : {g.resumo}
        </li>
      ))}
    </ul>
  );
}

/** `/como-fazer`: a página que lista todos os guias (a porta de entrada para quem procura «como fazer uma rifa»). */
export function IndiceGuias() {
  const { t } = useI18n();
  const { guias, erro } = useGuias();
  useEffect(() => {
    document.title = `${t("web_comofazer_titulo")} | ${t("app_nome")}`;
  }, [t]);
  return (
    <div className="pagina">
      <article className="cartao texto-pagina guia" data-testid="indice-guias">
        <h1>{t("web_comofazer_titulo")}</h1>
        <p className="texto-longo">{t("web_comofazer_intro")}</p>
        {erro && <p role="alert">{erro}</p>}
        {!guias && !erro && <p aria-busy="true">…</p>}
        {guias && <ListaDeGuias guias={guias} />}
        <p className="guia-ligacoes">
          <Ligacao para="/" className="botao" data-testid="indice-gerador">
            {t("app_nome")}
          </Ligacao>
        </p>
      </article>
    </div>
  );
}

/**
 * No fim de cada guia: as ligações para os outros guias e para o índice (ligações internas que ajudam quem lê e quem indexa).
 * A página inicial reutiliza-o sem excluir nenhum (`menos=""`) e com o título do índice (`titulo`), para os seus próprios
 * guias e a sua ligação de entrada sobreviverem à montagem do React (ver `Gerador.tsx`): sem isto, a página inicial perdia
 * TODAS estas ligações depois de montar (só existiam no HTML estático do servidor, que o React substitui).
 */
export function OutrosGuias({ menos, titulo }: { menos: string; titulo?: string }) {
  const { t } = useI18n();
  const { guias } = useGuias();
  if (!guias) return null;
  return (
    <section className="outros-guias" data-testid="outros-guias">
      <h2>{titulo ?? t("web_guias_outros")}</h2>
      <ListaDeGuias guias={guias.filter((g) => g.nome !== menos)} />
      <p>
        <Ligacao para="/como-fazer" data-testid="outros-guias-todos">
          {t("web_guia_todos")}
        </Ligacao>
      </p>
    </section>
  );
}
