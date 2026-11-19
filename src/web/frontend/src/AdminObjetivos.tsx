import { type FormEvent, useCallback, useEffect, useState } from "react";
import { adminApi, ErroEntrada, NaoAutenticado, type ObjetivosEstado } from "./admin-api";
import { formatarNumero } from "./graficos";

/*
 * «Objetivos diários»: o dono põe uma meta por dia para os números que acompanha e vê se ontem a cumpriu, a média dos últimos 7 dias e em quantos deles
 * se cumpriu (`objetivos.py`). O relatório diário por e-mail leva a mesma secção. Só contagens. Texto só em português (o painel é do dono).
 */
export function AdminObjetivos({
  leitura,
  aoSairDaSessao,
}: {
  leitura: boolean;
  aoSairDaSessao: () => void;
}) {
  const [dados, setDados] = useState<ObjetivosEstado | null>(null);
  const [metas, setMetas] = useState<Record<string, string>>({});
  const [falha, setFalha] = useState("");
  const [guardado, setGuardado] = useState("");

  const carregar = useCallback(async () => {
    try {
      const d = await adminApi.objetivos();
      setDados(d);
      setMetas(Object.fromEntries(d.kpis.map((k) => [k.chave, k.meta === null ? "" : String(k.meta)])));
      setFalha("");
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha("Não foi possível carregar os objetivos (a base de dados pode estar a acordar).");
    }
  }, [aoSairDaSessao]);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  async function guardar(e: FormEvent, chave: string, rotulo: string) {
    e.preventDefault();
    setGuardado("");
    const texto = (metas[chave] ?? "").trim().replace(",", ".");
    const meta = texto === "" ? null : Number(texto);
    if (meta !== null && !(meta > 0)) {
      setFalha("A meta tem de ser um número maior que zero (ou deixe vazio para apagar).");
      return;
    }
    try {
      await adminApi.definirObjetivo(chave, meta);
      setGuardado(meta === null ? `Objetivo de «${rotulo}» apagado.` : `Objetivo de «${rotulo}» guardado.`);
      await carregar();
    } catch (err) {
      if (err instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha(err instanceof ErroEntrada ? err.message : "Não foi possível guardar o objetivo.");
    }
  }

  return (
    <section className="cartao admin-seccao" aria-labelledby="objetivos-t" data-testid="admin-objetivos">
      <h2 id="objetivos-t">Objetivos diários</h2>
      <p className="explica">
        Uma meta <b>por dia</b> (pelo menos) para os números que quer acompanhar. Aqui vê se o último dia
        completo{dados ? ` (${dados.dia})` : ""} a cumpriu, a média dos últimos 7 dias e em quantos deles a
        meta foi atingida; o relatório diário por e-mail leva a mesma secção. Deixe o campo vazio para não ter
        meta.
      </p>
      {falha && (
        <p role="alert" className="cor-aviso">
          {falha}
        </p>
      )}
      {guardado && (
        <p role="status" className="cor-ok" data-testid="admin-objetivos-guardado">
          {guardado}
        </p>
      )}
      {!dados && !falha && <p aria-busy="true">…</p>}
      {dados && (
        <div className="tabela-rolavel">
          <table data-testid="admin-tabela-objetivos">
            <caption className="so-leitores">Objetivos diários</caption>
            <thead>
              <tr>
                <th scope="col">Número</th>
                <th scope="col">Meta por dia</th>
                <th scope="col">Ontem</th>
                <th scope="col">Média 7 dias</th>
                <th scope="col">Dias cumpridos</th>
              </tr>
            </thead>
            <tbody>
              {dados.kpis.map((k) => (
                <tr key={k.chave} data-testid={`objetivo-${k.chave}`}>
                  <th scope="row">{k.rotulo}</th>
                  <td>
                    <form onSubmit={(e) => void guardar(e, k.chave, k.rotulo)} className="meta-objetivo">
                      <input
                        type="text"
                        inputMode="decimal"
                        aria-label={`Meta por dia de ${k.rotulo}`}
                        value={metas[k.chave] ?? ""}
                        disabled={leitura}
                        onChange={(e) => setMetas({ ...metas, [k.chave]: e.target.value })}
                        data-testid={`objetivo-meta-${k.chave}`}
                      />
                      {!leitura && (
                        <button
                          type="submit"
                          className="secundario"
                          data-testid={`objetivo-guardar-${k.chave}`}
                        >
                          Guardar
                        </button>
                      )}
                    </form>
                  </td>
                  <td data-testid={`objetivo-ontem-${k.chave}`}>
                    {formatarNumero(k.ontem)}
                    {k.atingido !== null && (
                      <span className={k.atingido ? "cor-ok" : "cor-aviso"}>
                        {" "}
                        {k.atingido ? "✔" : "✘"} {k.pct} %
                      </span>
                    )}
                  </td>
                  <td>{formatarNumero(Math.round(k.media7 * 10) / 10)}</td>
                  <td>{k.meta === null ? "—" : `${k.dias_cumpridos} de ${k.dias}`}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
