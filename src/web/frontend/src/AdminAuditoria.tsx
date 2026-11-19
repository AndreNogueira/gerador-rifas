import { useCallback, useEffect, useState } from "react";
import { type AuditoriaEstado, adminApi, NaoAutenticado } from "./admin-api";

/*
 * O «Registo de ações»: o que se fez no painel, por quem (o dono ou o acesso só de leitura) e quando, durante 400 dias (`auditoria.py`). Só o código da ação e um
 * detalhe curto (o id do comentário, o nome da chave da API…): nunca o texto dos visitantes, a palavra-passe nem a chave. Texto só em português (o painel é do dono).
 */
const quando = (ts: number) =>
  new Date(ts * 1000).toLocaleString("pt-PT", { dateStyle: "short", timeStyle: "medium" });

export function AdminAuditoria({ aoSairDaSessao }: { aoSairDaSessao: () => void }) {
  const [dados, setDados] = useState<AuditoriaEstado | null>(null);
  const [falha, setFalha] = useState(false);

  const carregar = useCallback(async () => {
    try {
      setDados(await adminApi.auditoria());
      setFalha(false);
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha(true);
    }
  }, [aoSairDaSessao]);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  return (
    <section className="cartao admin-seccao" aria-labelledby="auditoria-t" data-testid="admin-auditoria">
      <h2 id="auditoria-t">Registo de ações do painel</h2>
      <p className="explica">
        Quem fez o quê e quando no painel: entradas, comentários apagados ou escondidos, chaves da API criadas
        ou revogadas, textos de SEO, objetivos e e-mails de teste. Guarda-se durante{" "}
        {dados?.retencao_dias ?? 400} dias. As palavras-passe erradas e os bloqueios não entram aqui
        (contam-se em «Acessos ao painel»). Nunca leva o texto dos visitantes nem chaves.
      </p>
      {falha && (
        <p role="alert" className="cor-aviso">
          Não foi possível carregar o registo (a base de dados pode estar a acordar).
        </p>
      )}
      {!dados && !falha && <p aria-busy="true">…</p>}
      {dados && !dados.persistente && (
        <p className="aviso-efemero" role="note">
          Sem <code>DATABASE_URL</code> o registo vive no disco temporário e perde-se quando o serviço
          reinicia.
        </p>
      )}
      {dados &&
        (dados.itens.length === 0 ? (
          <p data-testid="admin-auditoria-vazio">Ainda não há ações registadas.</p>
        ) : (
          <>
            <p>
              <b>{dados.total}</b> {dados.total === 1 ? "ação registada" : "ações registadas"}
              {dados.itens.length < dados.total && ` (as ${dados.itens.length} mais recentes)`}
            </p>
            <div className="tabela-rolavel">
              <table data-testid="admin-tabela-auditoria">
                <caption className="so-leitores">Registo de ações do painel</caption>
                <thead>
                  <tr>
                    <th scope="col">Quando</th>
                    <th scope="col">Quem</th>
                    <th scope="col">Ação</th>
                    <th scope="col">Detalhe</th>
                  </tr>
                </thead>
                <tbody>
                  {dados.itens.map((i) => (
                    <tr key={`${i.ts}-${i.acao}-${i.detalhe}`} data-testid="admin-auditoria-linha">
                      <td>{quando(i.ts)}</td>
                      <td>{i.papel === "leitura" ? "Só leitura" : "Dono"}</td>
                      <td>{i.texto}</td>
                      <td className="texto-longo">{i.detalhe || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ))}
    </section>
  );
}
