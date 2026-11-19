import { useCallback, useEffect, useState } from "react";
import { nomePais } from "./AdminEvolucao";
import { adminApi, type ComentarioDoDono, ErroEntrada, NaoAutenticado } from "./admin-api";
import { Icone } from "./icones";

/*
 * A vista «Comentários» do painel: SÓ o país e o texto de cada comentário (mais o botão de apagar, para o dono). Não se mostra nem se guarda
 * para aqui quem escreveu: não interessa, e o endereço IP nem sequer se guarda (`opiniao.py`). Texto só em português (o painel é do dono).
 */
export function AdminComentarios({
  leitura,
  aoSairDaSessao,
}: {
  leitura: boolean;
  aoSairDaSessao: () => void;
}) {
  const [dados, setDados] = useState<{ total: number; itens: ComentarioDoDono[] } | null>(null);
  const [falha, setFalha] = useState("");

  const carregar = useCallback(async () => {
    try {
      setDados(await adminApi.comentarios());
      setFalha("");
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha("Não foi possível carregar os comentários.");
    }
  }, [aoSairDaSessao]);

  useEffect(() => {
    void carregar();
    const a = setInterval(() => void carregar(), 60000);
    return () => clearInterval(a);
  }, [carregar]);

  async function apagar(c: ComentarioDoDono) {
    if (!window.confirm("Apagar este comentário? Deixa de aparecer na página pública.")) return;
    try {
      await adminApi.apagarComentario(c.id);
      await carregar();
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha(e instanceof ErroEntrada ? e.message : "Não foi possível apagar.");
    }
  }

  return (
    <section className="cartao admin-seccao" aria-labelledby="comentarios-t" data-testid="admin-comentarios">
      <h2 id="comentarios-t">Comentários dos visitantes</h2>
      <p className="explica">
        O que as pessoas escreveram na página «Comentários», só com o <b>país</b> de onde vieram e o texto
        (quem escreveu não interessa: não se mostra; e o endereço IP nem se guarda). O país vem da rede do
        alojamento; «Desconhecido» quer dizer que ela não o indicou. Se um comentário for spam ou abuso,
        apague-o: deixa logo de aparecer na página pública.
      </p>
      {falha && (
        <p role="alert" className="cor-aviso">
          {falha}
        </p>
      )}
      {!dados && !falha && <p aria-busy="true">…</p>}
      {dados && (
        <>
          <p>
            <b>{dados.total}</b> {dados.total === 1 ? "comentário" : "comentários"}
            {dados.itens.length < dados.total && ` (os ${dados.itens.length} mais recentes)`}
          </p>
          {dados.itens.length === 0 ? (
            <p data-testid="admin-comentarios-vazio">Ainda não há comentários.</p>
          ) : (
            <div className="tabela-rolavel">
              <table data-testid="admin-tabela-comentarios">
                <caption className="so-leitores">Comentários: país e texto</caption>
                <thead>
                  <tr>
                    <th scope="col">País</th>
                    <th scope="col">Texto</th>
                    {!leitura && <th scope="col">Apagar</th>}
                  </tr>
                </thead>
                <tbody>
                  {dados.itens.map((c) => (
                    <tr key={c.id} data-testid="admin-comentario">
                      <td className="ip-comentario">{nomePais(c.pais)}</td>
                      <td className="texto-longo">{c.texto}</td>
                      {!leitura && (
                        <td>
                          <button
                            type="button"
                            className="texto"
                            aria-label="Apagar este comentário"
                            onClick={() => void apagar(c)}
                            data-testid="admin-comentario-apagar"
                          >
                            <Icone nome="lixo" />
                          </button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}
