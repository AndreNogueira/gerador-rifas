import { useCallback, useEffect, useMemo, useState } from "react";
import { adminApi, type Evolucao, NaoAutenticado, type PainelDiario } from "./admin-api";
import { corDaSerie, formatarNumero, GraficoDiario, rotuloDia } from "./graficos";
import { Icone } from "./icones";

/*
 * A vista «Evolução diária» do painel: TUDO o que o servidor grava na base (sessões, gerações, línguas, países, pedidos, CPU…), dia a dia, até
 * 90 dias. Os painéis vêm prontos do servidor (`GET /api/admin/evolucao`); aqui só se desenham, resumem e exportam. Texto só em português
 * (o painel é do dono).
 */

const PERIODOS = [7, 14, 30, 60, 90] as const;

const resumir = (valores: (number | null)[], como: PainelDiario["agregado"]): number | null => {
  const reais = valores.filter((v): v is number => v !== null);
  if (reais.length === 0) return null;
  if (como === "max") return Math.max(...reais);
  const soma = reais.reduce((a, b) => a + b, 0);
  return como === "media" ? soma / reais.length : soma;
};

/** Soma (ou média) por dia de todas as séries do painel. */
const porDia = (p: PainelDiario): (number | null)[] =>
  (p.series[0]?.valores ?? []).map((_, i) =>
    p.series.every((s) => s.valores[i] === null)
      ? null
      : p.series.reduce((a, s) => a + (s.valores[i] ?? 0), 0),
  );

const temDados = (p: PainelDiario) => p.series.some((s) => s.valores.some((v) => v !== null && v !== 0));

/** A variação da segunda metade do período face à primeira (só faz sentido com contagens: «soma»). */
export function tendencia(valores: (number | null)[]): number | null {
  const meio = Math.floor(valores.length / 2);
  if (meio < 1) return null;
  const antes = valores.slice(0, meio).reduce<number>((a, v) => a + (v ?? 0), 0);
  const depois = valores.slice(valores.length - meio).reduce<number>((a, v) => a + (v ?? 0), 0);
  if (antes === 0) return depois === 0 ? 0 : null;
  return ((depois - antes) / antes) * 100;
}

function Tendencia({ valor }: { valor: number | null }) {
  if (valor === null) return <span className="tendencia">novo</span>;
  const r = Math.round(valor);
  if (r === 0) return <span className="tendencia">igual à 1.ª metade</span>;
  return (
    <span className={`tendencia ${r > 0 ? "sobe" : "desce"}`}>
      {r > 0 ? "▲" : "▼"} {Math.abs(r)} % face à 1.ª metade
    </span>
  );
}

/** Nomes de países por extenso (os painéis trazem os códigos de duas letras). */
export function nomePais(codigo: string): string {
  if (!/^[A-Z]{2}$/.test(codigo)) return codigo === "Outros" ? "Outros" : "Desconhecido";
  try {
    const nome = new Intl.DisplayNames(["pt-PT"], { type: "region" }).of(codigo);
    return nome && nome !== codigo ? `${nome} (${codigo})` : codigo;
  } catch {
    return codigo;
  }
}

function formatarValor(v: number | null, p: PainelDiario): string {
  return v === null ? "—" : `${formatarNumero(v)}${p.unidade}`;
}

function Painel({ p, dias }: { p: PainelDiario; dias: string[] }) {
  const series = p.series.map((s, i) => {
    const nome = p.rotulos === "pais" ? nomePais(s.nome) : s.nome;
    return { nome, cor: corDaSerie(s.nome, i), valores: s.valores };
  });
  const total = resumir(porDia(p), "soma");
  const nomeDoResumo = { soma: "total", media: "média", max: "pico" } as const;
  return (
    <div className="grafico-bloco painel-diario" data-testid={`evolucao-${p.id}`}>
      <h3>{p.titulo}</h3>
      {temDados(p) ? (
        <>
          {p.agregado === "soma" ? (
            <p className="resumo-diario">
              <strong>{formatarValor(total, p)}</strong> <span>total no período</span>
              <Tendencia valor={tendencia(porDia(p))} />
            </p>
          ) : (
            <ul className="resumo-diario resumo-series">
              {p.series.map((s, i) => (
                <li key={s.nome}>
                  <span className="amostra" style={{ background: corDaSerie(s.nome, i) }} />
                  {s.nome}: <strong>{formatarValor(resumir(s.valores, s.agregado), p)}</strong>{" "}
                  <span>{nomeDoResumo[s.agregado]}</span>
                </li>
              ))}
            </ul>
          )}
          <GraficoDiario titulo={p.titulo} dias={dias} series={series} tipo={p.tipo} unidade={p.unidade} />
        </>
      ) : (
        <p className="sem-dados-diario">Ainda sem registos neste período.</p>
      )}
      <p className="explica">{p.explica}</p>
    </div>
  );
}

const celulaCsv = (v: string) => (/[;"\n]/.test(v) ? `"${v.replaceAll('"', '""')}"` : v);

/** Todas as séries numa tabela (uma linha por série, uma coluna por dia), em CSV com `;` e vírgula decimal para o Excel em português. */
export function paraCsv(e: Evolucao): string {
  const linhas = [["Grupo", "Painel", "Série", ...e.dias_lista]];
  for (const p of e.paineis)
    for (const s of p.series)
      linhas.push([
        p.grupo,
        p.titulo,
        p.rotulos === "pais" ? nomePais(s.nome) : s.nome,
        ...s.valores.map((v) => (v === null ? "" : String(v).replace(".", ","))),
      ]);
  return `﻿${linhas.map((l) => l.map(celulaCsv).join(";")).join("\r\n")}\r\n`;
}

const DESTAQUES: [string, string, string][] = [
  ["sessoes", "Sessões", "sessões abertas"],
  ["geracoes", "Gerações", "pedidos de «Gerar»"],
  ["numeros", "Números gerados", "números de rifa escritos"],
  ["descargas", "Descargas", "ficheiros descarregados"],
  ["paginas_vistas", "Páginas vistas", "pessoas e robôs"],
];

export function AdminEvolucao({ aoSairDaSessao }: { aoSairDaSessao: () => void }) {
  const [dias, setDias] = useState<number>(30);
  const [dados, setDados] = useState<Evolucao | null>(null);
  const [falha, setFalha] = useState(false);

  const carregar = useCallback(async () => {
    try {
      setDados(await adminApi.evolucao(dias));
      setFalha(false);
    } catch (e) {
      if (e instanceof NaoAutenticado) aoSairDaSessao();
      else setFalha(true);
    }
  }, [dias, aoSairDaSessao]);

  useEffect(() => {
    void carregar();
    const a = setInterval(() => void carregar(), 60000);
    return () => clearInterval(a);
  }, [carregar]);

  const grupos = useMemo(() => {
    const m = new Map<string, PainelDiario[]>();
    for (const p of dados?.paineis ?? []) m.set(p.grupo, [...(m.get(p.grupo) ?? []), p]);
    return [...m.entries()];
  }, [dados]);

  function descarregarCsv() {
    if (!dados) return;
    const url = URL.createObjectURL(new Blob([paraCsv(dados)], { type: "text/csv;charset=utf-8" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `evolucao-${dados.dias_lista[0]}_${dados.dias_lista[dados.dias_lista.length - 1]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="admin-evolucao" data-testid="admin-evolucao">
      <section className="cartao admin-seccao" aria-labelledby="evolucao-t">
        <h2 id="evolucao-t">Evolução dia a dia</h2>
        <p className="explica">
          Tudo o que o servidor guarda na base de dados, dia a dia, para ver para onde as coisas vão: uso,
          funcionalidades, público, saúde do serviço e consumo de recursos. Os dias são os do seu fuso horário
          e o último (hoje) está incompleto. Só há contagens: nunca se guarda quem fez o quê.
        </p>
        <div className="botoes">
          <label className="seletor-admin">
            <span className="so-leitores">Período</span>
            <select
              value={dias}
              onChange={(e) => setDias(Number(e.target.value))}
              data-testid="evolucao-periodo"
            >
              {PERIODOS.map((d) => (
                <option key={d} value={d}>
                  Últimos {d} dias
                </option>
              ))}
            </select>
          </label>
          <button type="button" className="secundario" onClick={() => void carregar()}>
            <Icone nome="auto" />
            Atualizar
          </button>
          <button
            type="button"
            className="secundario"
            onClick={descarregarCsv}
            disabled={!dados}
            data-testid="evolucao-csv"
          >
            <Icone nome="descarregar" />
            Descarregar CSV
          </button>
        </div>
        {falha && (
          <p role="alert" className="cor-aviso">
            Não foi possível carregar a evolução (a base de dados pode estar a acordar). Tente outra vez daqui
            a pouco.
          </p>
        )}
        {dados && dados.dias > dados.retencao.eventos_dias && (
          <p className="aviso-efemero" role="note">
            Só se guardam {dados.retencao.eventos_dias} dias de eventos e {dados.retencao.sistema_dias} de
            pedidos e sistema: os dias mais antigos aparecem vazios.
          </p>
        )}
        {dados && (
          <div className="stats" data-testid="evolucao-destaques">
            {DESTAQUES.map(([id, rotulo, sub]) => {
              const p = dados.paineis.find((x) => x.id === id);
              if (!p) return null;
              const v = porDia(p);
              return (
                <div className="stat" key={id}>
                  <span className="rotulo">{rotulo}</span>
                  <span className="valor">{formatarNumero(resumir(v, "soma") ?? 0)}</span>
                  <span className="sub">
                    {sub} · {dados.dias} dias
                  </span>
                  <Tendencia valor={tendencia(v)} />
                </div>
              );
            })}
          </div>
        )}
      </section>

      {!dados && !falha && <p aria-busy="true">…</p>}
      {dados &&
        grupos.map(([grupo, paineis]) => (
          <section
            className="cartao admin-seccao"
            key={grupo}
            aria-labelledby={`evolucao-g-${grupo}`}
            data-testid={`evolucao-grupo-${grupo}`}
          >
            <h2 id={`evolucao-g-${grupo}`}>{grupo}</h2>
            <div className="graficos">
              {paineis.map((p) => (
                <Painel key={p.id} p={p} dias={dados.dias_lista} />
              ))}
            </div>
          </section>
        ))}
      {dados && (
        <p className="explica" data-testid="evolucao-intervalo">
          De {rotuloDia(dados.dias_lista[0] as string)} a{" "}
          {rotuloDia(dados.dias_lista[dados.dias_lista.length - 1] as string)} ({dados.dias} dias).
        </p>
      )}
    </div>
  );
}
