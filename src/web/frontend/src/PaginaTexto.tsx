import { useEffect, useState } from "react";
import { api, ErroApi, type PaginaDeTexto } from "./api";
import { useI18n } from "./i18n";
import { Voltar } from "./paginas";

/** Termos, privacidade e contacto: o texto vem do servidor (`textos_legais.py`) já na língua escolhida. */
export function PaginaTexto({ nome }: { nome: string }) {
  const { lingua, t } = useI18n();
  const [pagina, setPagina] = useState<PaginaDeTexto | null>(null);
  const [erro, setErro] = useState("");
  // biome-ignore lint/correctness/useExhaustiveDependencies: a página pede-se de novo quando a língua muda
  useEffect(() => {
    let ativo = true;
    setPagina(null);
    setErro("");
    api
      .pagina(nome)
      .then((d) => ativo && setPagina(d))
      .catch((e: unknown) => ativo && setErro(e instanceof ErroApi ? e.message : String(e)));
    return () => {
      ativo = false;
    };
  }, [nome, lingua]);
  useEffect(() => {
    if (pagina) document.title = `${pagina.titulo} | ${t("app_nome")}`; // o título do separador acompanha a língua da página
  }, [pagina, t]);
  return (
    <div className="pagina">
      <section className="cartao texto-pagina" data-testid={`pagina-${nome}`}>
        {pagina ? <h1>{pagina.titulo}</h1> : <h1>…</h1>}
        {erro && <p role="alert">{erro}</p>}
        {!pagina && !erro && <p aria-busy="true">…</p>}
        {pagina?.aviso && <p className="aviso-pagina">{pagina.aviso}</p>}
        {pagina?.seccoes.map((s) => (
          <div key={s.titulo}>
            <h2>{s.titulo}</h2>
            {s.paragrafos.map((p) => (
              <p key={p}>{p}</p>
            ))}
          </div>
        ))}
        <Voltar />
      </section>
    </div>
  );
}
