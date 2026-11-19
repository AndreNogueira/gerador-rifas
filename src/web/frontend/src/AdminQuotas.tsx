import { useCallback, useEffect, useState } from "react";
import { adminApi, NaoAutenticado, type QuotasEstado } from "./admin-api";

/*
 * «Quotas do alojamento»: as horas do Render no mês (750 por conta) e o espaço da base no Neon (0,5 GB), com a projeção até ao fim do mês e os avisos
 * (`quotas.py`). São estimativas DESTE serviço. Texto só em português (o painel é do dono).
 */
function Barra({ pct, aviso, rotulo }: { pct: number; aviso: boolean; rotulo: string }) {
  return (
    <div
      className={`barra-quota${aviso ? " aviso" : ""}`}
      role="progressbar"
      aria-label={rotulo}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.min(100, pct)}
    >
      <span style={{ width: `${Math.min(100, Math.max(0, pct))}%` }} />
    </div>
  );
}

export function AdminQuotas({ aoSairDaSessao }: { aoSairDaSessao: () => void }) {
  const [q, setQ] = useState<QuotasEstado | null>(null);
  const [falha, setFalha] = useState(false);

  const carregar = useCallback(async () => {
    try {
      setQ(await adminApi.quotas());
      setFalha(false);
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha(true);
    }
  }, [aoSairDaSessao]);

  useEffect(() => {
    void carregar();
    const a = setInterval(() => void carregar(), 300000);
    return () => clearInterval(a);
  }, [carregar]);

  return (
    <section className="cartao admin-seccao" aria-labelledby="quotas-t" data-testid="admin-quotas">
      <h2 id="quotas-t">Quotas do alojamento gratuito</h2>
      <p className="explica">
        Quanto falta antes de as quotas acabarem: as horas do Render no mês e o espaço da base no Neon. São
        estimativas deste serviço (o limite do Render é da conta inteira: outros serviços também gastam).
      </p>
      {falha && (
        <p role="alert" className="cor-aviso">
          Não foi possível calcular as quotas (a base de dados pode estar a acordar).
        </p>
      )}
      {!q && !falha && <p aria-busy="true">…</p>}
      {q && (
        <>
          {q.avisos.map((a) => (
            <p key={a} role="alert" className="cor-aviso" data-testid="admin-quotas-aviso">
              {a}
            </p>
          ))}
          <h3>Render: horas acordado em {q.render.mes}</h3>
          <Barra
            pct={q.render.pct}
            aviso={q.render.pct >= 90}
            rotulo={`Horas do Render gastas: ${q.render.pct} %`}
          />
          <p data-testid="admin-quotas-horas">
            <b>{q.render.gastas}</b> de {q.render.limite} h ({q.render.pct} %) em {q.render.decorridas} h
            decorridas do mês
            {q.render.projecao !== null && (
              <>
                {" "}
                · ao ritmo atual, <b>{q.render.projecao} h</b> até ao fim do mês
                {q.render.projecao > q.render.limite ? " (acima do limite!)" : ""}
              </>
            )}
            .
          </p>
          {!q.render.persistente && (
            <p className="aviso-efemero" role="note">
              Sem <code>DATABASE_URL</code> as horas só contam desde o último reinício do serviço.
            </p>
          )}
          {q.render.dados_desde && (
            <p className="aviso-efemero" role="note">
              Só há amostras desde {new Date(q.render.dados_desde * 1000).toLocaleDateString("pt-PT")}: o que
              veio antes não se contou.
            </p>
          )}
          <h3>Neon: espaço da base de dados</h3>
          {q.neon ? (
            <>
              <Barra
                pct={q.neon.pct}
                aviso={q.neon.pct >= 80}
                rotulo={`Espaço do Neon usado: ${q.neon.pct} %`}
              />
              <p data-testid="admin-quotas-neon">
                <b>{q.neon.total_mb.toLocaleString("pt-PT")} MB</b> de {q.neon.limite_mb} MB ({q.neon.pct} %).
              </p>
              <ul className="resumo-series" data-testid="admin-quotas-tabelas">
                {q.neon.tabelas.map((t) => (
                  <li key={t.nome}>
                    {t.nome}: <strong>{t.mb.toLocaleString("pt-PT")} MB</strong>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p>
              Só com <code>DATABASE_URL</code> (a base do Neon): sem ela as métricas ficam num ficheiro local.
            </p>
          )}
          <p className="explica">
            As horas de computação do Neon (191,9 h por mês no plano grátis) só se veem no painel do Neon; os
            limites mudam-se com <code>RENDER_HORAS_LIMITE</code> e <code>NEON_LIMITE_MB</code>.
          </p>
        </>
      )}
    </section>
  );
}
