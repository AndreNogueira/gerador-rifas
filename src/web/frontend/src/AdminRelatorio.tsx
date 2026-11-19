import { useCallback, useEffect, useState } from "react";
import {
  adminApi,
  ErroEntrada,
  NaoAutenticado,
  type RelatorioEstado,
  type RelatorioPrevia,
  type TipoRelatorio,
} from "./admin-api";
import { Icone } from "./icones";

/*
 * A vista «Relatório diário»: o e-mail que o servidor manda todos os dias depois da meia-noite com tudo o que se gravou no dia que acabou (`relatorio.py`).
 * Aqui vê-se se está ligado, para onde vai, quando foi o último envio, e pode-se pré-visualizar qualquer dia e mandar um e-mail de teste.
 * Texto só em português (o painel é do dono).
 */
const quando = (ts: number) =>
  new Date(ts * 1000).toLocaleString("pt-PT", { dateStyle: "short", timeStyle: "short" });

export function AdminRelatorio({
  leitura,
  aoSairDaSessao,
}: {
  leitura: boolean;
  aoSairDaSessao: () => void;
}) {
  const [estado, setEstado] = useState<RelatorioEstado | null>(null);
  const [previa, setPrevia] = useState<RelatorioPrevia | null>(null);
  const [dia, setDia] = useState("");
  const [tipo, setTipo] = useState<TipoRelatorio>("dia");
  const [aFazer, setAFazer] = useState<"" | "previa" | "enviar">("");
  const [aviso, setAviso] = useState<{ ok: boolean; texto: string } | null>(null);

  const falhou = useCallback(
    (e: unknown, texto: string) => {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setAviso({ ok: false, texto: e instanceof ErroEntrada ? e.message : texto });
    },
    [aoSairDaSessao],
  );

  const carregar = useCallback(async () => {
    try {
      setEstado(await adminApi.relatorio());
    } catch (e) {
      falhou(e, "Não foi possível carregar o estado do relatório.");
    }
  }, [falhou]);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  async function ver() {
    setAFazer("previa");
    setAviso(null);
    try {
      setPrevia(await adminApi.relatorioPrevia(dia, tipo));
    } catch (e) {
      falhou(e, "Não foi possível montar o relatório.");
    } finally {
      setAFazer("");
    }
  }

  async function alertaTeste() {
    setAFazer("enviar");
    setAviso(null);
    try {
      await adminApi.alertaTeste();
      setAviso({
        ok: true,
        texto: "Alerta de teste enviado: veja a caixa de entrada (e o spam, da primeira vez).",
      });
    } catch (e) {
      falhou(e, "Não foi possível enviar o alerta de teste.");
    } finally {
      setAFazer("");
    }
  }

  async function enviar() {
    setAFazer("enviar");
    setAviso(null);
    try {
      await adminApi.relatorioEnviar(dia, tipo);
      setAviso({
        ok: true,
        texto: "E-mail de teste enviado: veja a caixa de entrada (e o spam, da primeira vez).",
      });
    } catch (e) {
      falhou(e, "Não foi possível enviar o e-mail.");
    } finally {
      setAFazer("");
    }
  }

  return (
    <section className="cartao admin-seccao" aria-labelledby="relatorio-t" data-testid="admin-relatorio">
      <h2 id="relatorio-t">Relatório diário por e-mail</h2>
      <p className="explica">
        Todos os dias, um pouco depois da meia-noite, o servidor envia-lhe um e-mail com tudo o que se gravou
        no dia que acabou (sessões, gerações, público, erros, memória…), comparado com a média dos 7 dias
        anteriores. Serve para acompanhar a app sem abrir o painel. Só contagens: nunca IPs, nomes nem textos.
        Se o serviço estava a dormir à meia-noite, o e-mail sai quando acordar, e nunca sai duas vezes.
      </p>
      {!estado && <p aria-busy="true">…</p>}
      {estado && (
        <>
          {estado.ativo ? (
            <p className="cor-ok" role="status" data-testid="admin-relatorio-ativo">
              Ligado: vai para <b>{estado.destinos.join(", ")}</b> (dias no fuso {estado.fuso}).
              {estado.ultimo
                ? ` Último relatório enviado: o de ${estado.ultimo.dia}, em ${quando(estado.ultimo.enviado)}.`
                : " Ainda não saiu nenhum."}
              {estado.periodicos && (
                <span data-testid="admin-relatorio-periodicos">
                  {" "}
                  Também chega um <b>resumo semanal</b> (segunda-feira
                  {estado.ultimo_semana
                    ? `; último: ${estado.ultimo_semana.dia.replace("semana:", "semana de ")}`
                    : ""}
                  ) e um <b>resumo mensal</b> (dia 1
                  {estado.ultimo_mes ? `; último: ${estado.ultimo_mes.dia.replace("mes:", "mês ")}` : ""}).
                </span>
              )}
            </p>
          ) : (
            <div className="aviso-efemero" role="note" data-testid="admin-relatorio-desligado">
              <p>
                <b>Desligado.</b> No Render, em <i>Environment</i>, defina{" "}
                {!estado.tem_chave && (
                  <>
                    <code>RESEND_API_KEY</code> (a chave da conta gratuita em resend.com)
                    {estado.destinos.length === 0 ? " e " : ""}
                  </>
                )}
                {estado.destinos.length === 0 && (
                  <>
                    <code>RELATORIO_EMAIL_PARA</code> (o seu e-mail, o mesmo da conta do Resend)
                  </>
                )}
                . Os passos estão em <code>docs/ADMIN.md</code>.
              </p>
            </div>
          )}
          {!estado.persistente && (
            <p className="aviso-efemero" role="note">
              Sem <code>DATABASE_URL</code> a reserva do dia perde-se quando o serviço reinicia: uma
              atualização a meio da manhã pode repetir o relatório.
            </p>
          )}
          {estado.erro && (
            <p role="alert" className="cor-aviso" data-testid="admin-relatorio-erro">
              O último envio falhou ({estado.erro}
              {estado.erro_em ? `, ${quando(estado.erro_em)}` : ""}). Volta a tentar de hora a hora.
            </p>
          )}
          <div className="botoes">
            <label className="seletor-admin">
              <span>Relatório</span>
              <select
                value={tipo}
                onChange={(e) => setTipo(e.target.value as TipoRelatorio)}
                data-testid="admin-relatorio-tipo"
              >
                <option value="dia">Diário</option>
                <option value="semana">Resumo semanal</option>
                <option value="mes">Resumo mensal</option>
              </select>
            </label>
            <label className="seletor-admin">
              <span>Dia</span>
              <input
                type="date"
                value={dia}
                onChange={(e) => setDia(e.target.value)}
                data-testid="admin-relatorio-dia"
                aria-describedby="relatorio-dia-ajuda"
              />
            </label>
            <button
              type="button"
              className="secundario"
              onClick={() => void ver()}
              disabled={aFazer !== ""}
              data-testid="admin-relatorio-ver"
            >
              <Icone nome="olho" />
              Pré-visualizar
            </button>
            {!leitura && (
              <button
                type="button"
                className="secundario"
                onClick={() => void enviar()}
                disabled={aFazer !== "" || !estado.ativo}
                data-testid="admin-relatorio-enviar"
              >
                <Icone nome="email" />
                Enviar um teste agora
              </button>
            )}
          </div>
          <p id="relatorio-dia-ajuda" className="explica">
            Deixe o dia em branco para o último período completo (ontem, a semana ou o mês que acabaram); com
            um dia, vê o período que o contém. Os resumos leem do histórico permanente. O teste leva «[Teste]»
            no assunto e não conta como o envio do dia.
          </p>
          <h3>Alertas imediatos</h3>
          <p className="explica">
            Sem esperar pela meia-noite: o servidor avisa por e-mail (o mesmo destino) assim que uma destas
            condições se verifica, e só volta a avisar da mesma passadas {estado.alertas.espera_h} horas.
          </p>
          <ul data-testid="admin-alertas-regras">
            {estado.alertas.regras.map((r) => {
              const ultimo = estado.alertas.ultimos[r.chave];
              return (
                <li key={r.chave}>
                  {r.texto}
                  {ultimo ? ` (último aviso: ${quando(ultimo)})` : ""}
                </li>
              );
            })}
          </ul>
          {!estado.alertas.ativo && (
            <p className="aviso-efemero" role="note" data-testid="admin-alertas-desligados">
              Desligados: precisam das mesmas variáveis do relatório (e de <code>ALERTAS_EMAIL</code>{" "}
              diferente de 0).
            </p>
          )}
          {estado.alertas.erro && (
            <p role="alert" className="cor-aviso">
              O último alerta não saiu ({estado.alertas.erro}). Volta a tentar passados 15 minutos.
            </p>
          )}
          {!leitura && (
            <div className="botoes">
              <button
                type="button"
                className="secundario"
                onClick={() => void alertaTeste()}
                disabled={aFazer !== "" || !estado.alertas.ativo}
                data-testid="admin-alerta-teste"
              >
                <Icone nome="email" />
                Enviar um alerta de teste
              </button>
            </div>
          )}
        </>
      )}
      {aviso && (
        <p
          role={aviso.ok ? "status" : "alert"}
          className={aviso.ok ? "cor-ok" : "cor-aviso"}
          data-testid="admin-relatorio-aviso"
        >
          {aviso.texto}
        </p>
      )}
      {previa && (
        <div data-testid="admin-relatorio-previa">
          <h3>{previa.assunto}</h3>
          <iframe
            className="relatorio-previa"
            title={`Pré-visualização do relatório de ${previa.dia}`}
            sandbox=""
            srcDoc={previa.html}
          />
        </div>
      )}
    </section>
  );
}
