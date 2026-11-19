import { useCallback, useEffect, useState } from "react";
import { nomePais } from "./AdminEvolucao";
import {
  adminApi,
  type ComentarioDoDono,
  type ComentariosDoDono,
  ErroEntrada,
  type EstadoComentario,
  NaoAutenticado,
} from "./admin-api";
import { Icone } from "./icones";

/*
 * A vista «Comentários» do painel: SÓ o país e o texto de cada comentário, com o estado que o dono lhe dá (novo, lido, favorito, escondido) e o botão de apagar.
 * «Escondido» tira o comentário da página pública sem o apagar. Não se mostra nem se guarda para aqui quem escreveu: não interessa, e o endereço IP nem sequer
 * se guarda (`opiniao.py`). Texto só em português (o painel é do dono).
 */
const FILTROS: [EstadoComentario | "", string][] = [
  ["", "Todos"],
  ["novo", "Novos"],
  ["favorito", "Favoritos"],
  ["escondido", "Escondidos"],
];
const NOME_ESTADO: Record<EstadoComentario, string> = {
  novo: "Novo",
  lido: "Lido",
  favorito: "Favorito",
  escondido: "Escondido",
};

export function AdminComentarios({
  leitura,
  aoSairDaSessao,
}: {
  leitura: boolean;
  aoSairDaSessao: () => void;
}) {
  const [dados, setDados] = useState<ComentariosDoDono | null>(null);
  const [filtro, setFiltro] = useState<EstadoComentario | "">("");
  const [falha, setFalha] = useState("");

  const carregar = useCallback(async () => {
    try {
      setDados(await adminApi.comentarios(filtro));
      setFalha("");
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha("Não foi possível carregar os comentários.");
    }
  }, [aoSairDaSessao, filtro]);

  useEffect(() => {
    void carregar();
    const a = setInterval(() => void carregar(), 60000);
    return () => clearInterval(a);
  }, [carregar]);

  async function agir(tarefa: () => Promise<unknown>, erro: string) {
    try {
      await tarefa();
      await carregar();
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha(e instanceof ErroEntrada ? e.message : erro);
    }
  }

  async function apagar(c: ComentarioDoDono) {
    if (!window.confirm("Apagar este comentário? Deixa de aparecer na página pública.")) return;
    await agir(() => adminApi.apagarComentario(c.id), "Não foi possível apagar.");
  }

  const mudar = (c: ComentarioDoDono, estado: EstadoComentario) =>
    agir(() => adminApi.comentarioEstado(c.id, estado), "Não foi possível mudar o estado.");

  return (
    <section className="cartao admin-seccao" aria-labelledby="comentarios-t" data-testid="admin-comentarios">
      <h2 id="comentarios-t">Comentários dos visitantes</h2>
      <p className="explica">
        O que as pessoas escreveram na página «Comentários», só com o <b>país</b> de onde vieram e o texto
        (quem escreveu não interessa: não se mostra; e o endereço IP nem se guarda). Cada comentário tem um
        estado: <b>novo</b> até o marcar, <b>lido</b>, <b>favorito</b> ou <b>escondido</b> (deixa de aparecer
        na página pública, mas não se perde). Se for spam ou abuso, apague-o.
      </p>
      {falha && (
        <p role="alert" className="cor-aviso">
          {falha}
        </p>
      )}
      {!dados && !falha && <p aria-busy="true">…</p>}
      {dados && (
        <>
          <p data-testid="admin-comentarios-resumo">
            <b>{dados.total}</b> {dados.total === 1 ? "comentário" : "comentários"} · <b>{dados.por_ler}</b>{" "}
            por ler
            {dados.escondidos > 0 && ` · ${dados.escondidos} escondido${dados.escondidos === 1 ? "" : "s"}`}
            {dados.itens.length < dados.total && filtro === "" && ` (os ${dados.itens.length} mais recentes)`}
          </p>
          <div className="botoes">
            <fieldset className="admin-vistas">
              <legend className="so-leitores">Filtrar por estado</legend>
              {FILTROS.map(([valor, nome]) => (
                <button
                  key={valor || "todos"}
                  type="button"
                  aria-pressed={filtro === valor}
                  onClick={() => setFiltro(valor)}
                  data-testid={`admin-comentarios-filtro-${valor || "todos"}`}
                >
                  {nome}
                </button>
              ))}
            </fieldset>
            {!leitura && dados.por_ler > 0 && (
              <button
                type="button"
                className="secundario"
                onClick={() => void agir(() => adminApi.comentariosLidos(), "Não foi possível marcar.")}
                data-testid="admin-comentarios-todos-lidos"
              >
                <Icone nome="verificado" />
                Marcar todos como lidos
              </button>
            )}
          </div>
          {dados.itens.length === 0 ? (
            <p data-testid="admin-comentarios-vazio">
              {filtro === "" ? "Ainda não há comentários." : "Nenhum comentário neste estado."}
            </p>
          ) : (
            <div className="tabela-rolavel">
              <table data-testid="admin-tabela-comentarios">
                <caption className="so-leitores">Comentários: país, texto e estado</caption>
                <thead>
                  <tr>
                    <th scope="col">País</th>
                    <th scope="col">Texto</th>
                    <th scope="col">Estado</th>
                    {!leitura && <th scope="col">Ações</th>}
                  </tr>
                </thead>
                <tbody>
                  {dados.itens.map((c) => (
                    <tr key={c.id} data-testid="admin-comentario" data-estado={c.estado}>
                      <td className="ip-comentario">{nomePais(c.pais)}</td>
                      <td className="texto-longo">{c.texto}</td>
                      <td>
                        <span
                          className={`estado-comentario estado-${c.estado}`}
                          data-testid="admin-comentario-estado"
                        >
                          {NOME_ESTADO[c.estado]}
                        </span>
                      </td>
                      {!leitura && (
                        <td className="acoes-comentario">
                          {c.estado === "novo" && (
                            <button
                              type="button"
                              className="texto"
                              onClick={() => void mudar(c, "lido")}
                              data-testid="admin-comentario-lido"
                            >
                              Lido
                            </button>
                          )}
                          <button
                            type="button"
                            className="texto"
                            aria-pressed={c.estado === "favorito"}
                            onClick={() => void mudar(c, c.estado === "favorito" ? "lido" : "favorito")}
                            data-testid="admin-comentario-favorito"
                          >
                            {c.estado === "favorito" ? "Tirar favorito" : "Favorito"}
                          </button>
                          <button
                            type="button"
                            className="texto"
                            onClick={() => void mudar(c, c.estado === "escondido" ? "lido" : "escondido")}
                            data-testid="admin-comentario-esconder"
                          >
                            {c.estado === "escondido" ? "Mostrar" : "Esconder"}
                          </button>
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
