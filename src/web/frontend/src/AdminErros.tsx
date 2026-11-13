import { useEffect, useState } from "react";
import { adminApi, type LivroErros } from "./admin-api";

const NOMES: Record<string, string> = {
  excecao: "Erro não tratado (500)",
  http: "Resposta de erro da API",
  geracao: "Geração que falhou",
  motor_reiniciado: "Motor reiniciado",
};

function hora(t: number): string {
  return new Date(t * 1000).toLocaleString("pt-PT", { dateStyle: "short", timeStyle: "short" });
}

/**
 * O livro de erros do servidor (`observabilidade.py`): o que falhou desde o último arranque, agrupado por «assinatura» (tipo, rota, estado,
 * classe da exceção e sítio no código), com contagem e primeira/última vez. Nunca mostra mensagens de erro nem dados de utilizadores.
 */
export function AdminErros({ intervalo }: { intervalo: string }) {
  const [livro, setLivro] = useState<LivroErros | null>(null);
  const [falha, setFalha] = useState(false);

  useEffect(() => {
    let ativo = true;
    const carregar = () =>
      adminApi
        .erros(intervalo)
        .then((d) => {
          if (ativo) {
            setLivro(d);
            setFalha(false);
          }
        })
        .catch(() => ativo && setFalha(true));
    void carregar();
    const a = setInterval(() => void carregar(), 30000);
    return () => {
      ativo = false;
      clearInterval(a);
    };
  }, [intervalo]);

  return (
    <section className="cartao admin-seccao" aria-labelledby="erros-t" data-testid="admin-erros">
      <h2 id="erros-t">Erros</h2>
      <p className="explica">
        O que falhou no servidor desde o último arranque ({livro ? hora(livro.desde_arranque) : "…"}),
        agrupado por tipo, rota e sítio no código. Só se guarda a classe da exceção e o ficheiro:linha, nunca
        a mensagem. Cada erro 500 tem um código que o utilizador vê e que se procura nos registos do Render (
        <code>X-Request-ID</code>).
      </p>
      {falha && <p role="alert">Não foi possível carregar o livro de erros.</p>}
      {livro && (
        <div className="tabela-rolavel">
          <table data-testid="admin-tabela-erros">
            <caption className="so-leitores">Erros por assinatura</caption>
            <thead>
              <tr>
                <th scope="col">Tipo</th>
                <th scope="col">Rota</th>
                <th scope="col">Estado</th>
                <th scope="col">Classe</th>
                <th scope="col">Sítio</th>
                <th scope="col">Vezes</th>
                <th scope="col">Última</th>
              </tr>
            </thead>
            <tbody>
              {livro.erros.map((e) => (
                <tr key={`${e.tipo}|${e.rota}|${e.estado}|${e.excecao}|${e.onde}`}>
                  <th scope="row">{NOMES[e.tipo] ?? e.tipo}</th>
                  <td>{e.rota ? <code>{e.rota}</code> : "—"}</td>
                  <td>{e.estado || "—"}</td>
                  <td>{e.excecao || "—"}</td>
                  <td>{e.onde ? <code>{e.onde}</code> : "—"}</td>
                  <td className="cor-erro">{e.n}</td>
                  <td>{hora(e.ultima)}</td>
                </tr>
              ))}
              {livro.erros.length === 0 && (
                <tr>
                  <td colSpan={7} className="suave">
                    Sem erros neste intervalo. 🎉
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
