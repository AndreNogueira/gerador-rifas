import { useCallback, useEffect, useState } from "react";
import { adminApi, type CopiaEstado, ErroEntrada, NaoAutenticado } from "./admin-api";
import { Icone } from "./icones";

/*
 * A «Cópia de segurança»: toda a semana (segunda-feira, depois da meia-noite) o serviço grava no armazenamento de objetos do Neon uma cópia dos dados que não se refazem
 * (histórico, objetivos, registo de ações, comentários, textos de SEO e chaves da API em hash), em 8 posições rotativas (`copia.py`). Aqui vê-se se está ligada, quando foi a
 * última, e o dono pode fazer uma agora. Texto só em português (o painel é do dono).
 */
const quando = (ts: number) =>
  new Date(ts * 1000).toLocaleString("pt-PT", { dateStyle: "short", timeStyle: "short" });
const kb = (b: number) => `${(b / 1024).toLocaleString("pt-PT", { maximumFractionDigits: 1 })} KB`;

export function AdminCopia({ leitura, aoSairDaSessao }: { leitura: boolean; aoSairDaSessao: () => void }) {
  const [estado, setEstado] = useState<CopiaEstado | null>(null);
  const [aFazer, setAFazer] = useState(false);
  const [aviso, setAviso] = useState<{ ok: boolean; texto: string } | null>(null);

  const carregar = useCallback(async () => {
    try {
      setEstado(await adminApi.copia());
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
    }
  }, [aoSairDaSessao]);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  async function fazer() {
    setAFazer(true);
    setAviso(null);
    try {
      const r = await adminApi.copiaFazer();
      setAviso({
        ok: true,
        texto: `Cópia feita (${kb(r.bytes)}, ${Object.values(r.linhas).reduce((a, n) => a + n, 0)} linhas) em ${r.chave}.`,
      });
      await carregar();
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else
        setAviso({
          ok: false,
          texto: e instanceof ErroEntrada ? e.message : "Não foi possível fazer a cópia.",
        });
    } finally {
      setAFazer(false);
    }
  }

  return (
    <section className="cartao admin-seccao" aria-labelledby="copia-t" data-testid="admin-copia">
      <h2 id="copia-t">Cópia de segurança semanal</h2>
      <p className="explica">
        Todas as segundas-feiras, depois da meia-noite, o serviço grava no armazenamento do Neon uma cópia dos
        dados que não se refazem: o histórico diário, os objetivos, o registo de ações, os comentários, os
        textos de SEO e as chaves da API (só o hash). Guardam-se as últimas {estado?.posicoes ?? 8} semanas,
        em posições rotativas. A credencial do serviço só consegue escrever: nunca lê nem apaga as cópias.
      </p>
      {!estado && <p aria-busy="true">…</p>}
      {estado &&
        (estado.ativa ? (
          <p className="cor-ok" role="status" data-testid="admin-copia-ativa">
            Ligada: para o bucket <b>{estado.bucket}</b>.{" "}
            {estado.ultimo
              ? `Última cópia semanal: a da ${estado.ultimo.dia.replace("backup:", "semana de ")}, em ${quando(estado.ultimo.enviado)}${estado.ultimo_tamanho ? ` (${kb(estado.ultimo_tamanho)})` : ""}.`
              : "Ainda não saiu nenhuma."}
          </p>
        ) : (
          <div className="aviso-efemero" data-testid="admin-copia-desligada">
            <p>
              <b>Desligada.</b>{" "}
              {!estado.tem_bd && (
                <>
                  Só funciona com a base Postgres (<code>DATABASE_URL</code>).{" "}
                </>
              )}
              {!estado.tem_s3 && (
                <>
                  No Render, em <i>Environment</i>, defina <code>BACKUP_S3_ENDPOINT</code>,{" "}
                  <code>BACKUP_S3_BUCKET</code>, <code>BACKUP_S3_REGION</code>,{" "}
                  <code>BACKUP_S3_ACCESS_KEY_ID</code> e <code>BACKUP_S3_SECRET_ACCESS_KEY</code> (uma
                  credencial do Neon só com «storage:write»). Os passos estão em <code>docs/ADMIN.md</code>.
                </>
              )}
            </p>
          </div>
        ))}
      {estado?.erro && (
        <p role="alert" className="cor-aviso" data-testid="admin-copia-erro">
          A última tentativa falhou ({estado.erro}
          {estado.erro_em ? `, ${quando(estado.erro_em)}` : ""}). Volta a tentar de hora a hora.
        </p>
      )}
      {estado && !leitura && (
        <div className="botoes">
          <button
            type="button"
            className="secundario"
            onClick={() => void fazer()}
            disabled={aFazer || !estado.ativa}
            data-testid="admin-copia-fazer"
          >
            <Icone nome="descarregar" />
            Fazer uma cópia agora
          </button>
        </div>
      )}
      {estado && (
        <p className="explica">
          Dentro da cópia: {estado.tabelas.join(", ")}. «Fazer uma cópia agora» grava em{" "}
          <code>backups/rifas-manual.json.gz</code> sem mexer nas semanas. Para restaurar:{" "}
          <code>scripts/restaurar_copia.py</code> (ver <code>docs/ADMIN.md</code>).
        </p>
      )}
      {aviso && (
        <p
          role={aviso.ok ? "status" : "alert"}
          className={aviso.ok ? "cor-ok" : "cor-aviso"}
          data-testid="admin-copia-aviso"
        >
          {aviso.texto}
        </p>
      )}
    </section>
  );
}
