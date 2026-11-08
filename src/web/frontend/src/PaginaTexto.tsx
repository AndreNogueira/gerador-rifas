import { useEffect, useState } from "react";
import { api, ErroApi, type PaginaDeTexto } from "./api";
import { Voltar } from "./paginas";

/** Termos, privacidade e contacto: o texto vem do servidor (`textos_legais.py`), só em português. */
export function PaginaTexto({ nome }: { nome: string }) {
  const [pagina, setPagina] = useState<PaginaDeTexto | null>(null);
  const [erro, setErro] = useState("");
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
  }, [nome]);
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
