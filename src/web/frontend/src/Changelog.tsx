import { useEffect, useState } from "react";
import { api, type EntradaChangelog, ErroApi } from "./api";
import { Voltar } from "./paginas";

/** O changelog (`src/web/CHANGELOG.md`): só em português, como o painel (é a história do produto, não a interface). */
export function Changelog() {
  const [entradas, setEntradas] = useState<EntradaChangelog[] | null>(null);
  const [erro, setErro] = useState("");
  useEffect(() => {
    let ativo = true;
    api
      .changelog()
      .then((d) => ativo && setEntradas(d.entradas))
      .catch((e: unknown) => ativo && setErro(e instanceof ErroApi ? e.message : String(e)));
    return () => {
      ativo = false;
    };
  }, []);
  return (
    <div className="pagina">
      <section className="cartao changelog">
        <h1>Changelog</h1>
        <p className="suave">O que mudou, versão a versão (só em português).</p>
        {erro && <p role="alert">{erro}</p>}
        {!entradas && !erro && <p aria-busy="true">…</p>}
        {entradas?.map((e) => (
          <article key={e.versao} data-testid={`versao-${e.versao}`}>
            <h2>
              Versão {e.versao} <time dateTime={e.data}>{e.data}</time>
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
