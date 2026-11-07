import { type PointerEvent, useId, useState } from "react";

/**
 * Gráficos do painel de administração, desenhados à mão em SVG (sem biblioteca: o JS fica pequeno). As cores vêm das variáveis do
 * tema (`var(--destaque)`…), por isso acompanham o tema e o modo claro/escuro. Cada gráfico é uma imagem com `aria-label` e o
 * valor mais recente, e tem um balão ao passar o rato.
 */
export const CORES = ["var(--destaque)", "var(--destaque-2)", "var(--passo-3)", "var(--passo-4)"];

const L = 640; // largura do desenho (o SVG escala)
const A = 220;
const MARGEM = { e: 46, d: 12, c: 10, b: 24 };
const AREA = { l: L - MARGEM.e - MARGEM.d, a: A - MARGEM.c - MARGEM.b };

/** Um máximo «redondo» (1, 2, 5, 10…) para o eixo Y, e os valores das linhas de grelha. */
export function escalaY(maximo: number, linhas = 4): { topo: number; marcas: number[] } {
  const m = Math.max(maximo, 1e-9);
  const potencia = 10 ** Math.floor(Math.log10(m));
  const base = [1, 2, 2.5, 5, 10].map((f) => f * potencia).find((v) => v >= m) ?? 10 * potencia;
  return { topo: base, marcas: Array.from({ length: linhas + 1 }, (_, i) => (base * i) / linhas) };
}

export function formatarNumero(v: number): string {
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)} M`;
  if (v >= 1e4) return `${Math.round(v / 1e3)} k`;
  if (v >= 1e3) return `${(v / 1e3).toFixed(1)} k`;
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}

const hora = (t: number, longo: boolean) =>
  new Date(t * 1000).toLocaleString(
    "pt-PT",
    longo
      ? { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }
      : { hour: "2-digit", minute: "2-digit" },
  );

interface Eixo {
  desde: number;
  ate: number;
}

function EixoX({ desde, ate }: Eixo) {
  const longo = ate - desde > 36 * 3600;
  return (
    <>
      {[0, 0.25, 0.5, 0.75, 1].map((f) => (
        <text
          key={f}
          x={MARGEM.e + f * AREA.l}
          y={A - 6}
          textAnchor={f === 0 ? "start" : f === 1 ? "end" : "middle"}
          className="grafico-eixo"
        >
          {hora(desde + f * (ate - desde), longo || ate - desde > 12 * 3600)}
        </text>
      ))}
    </>
  );
}

function Grelha({
  marcas,
  topo,
  formato,
}: {
  marcas: number[];
  topo: number;
  formato: (v: number) => string;
}) {
  return (
    <>
      {marcas.map((v) => {
        const y = MARGEM.c + AREA.a - (v / topo) * AREA.a;
        return (
          <g key={v}>
            <line x1={MARGEM.e} x2={L - MARGEM.d} y1={y} y2={y} className="grafico-grelha" />
            <text x={MARGEM.e - 6} y={y + 4} textAnchor="end" className="grafico-eixo">
              {formato(v)}
            </text>
          </g>
        );
      })}
    </>
  );
}

export interface Serie {
  nome: string;
  cor: string;
  pontos: { t: number; v: number | null }[];
  tracejada?: boolean;
}

interface PropsLinhas extends Eixo {
  titulo: string;
  series: Serie[];
  passo: number;
  formato?: (v: number) => string;
  unidade?: string;
  /** Uma linha horizontal fixa (p.ex. o limite de memória). */
  limite?: { valor: number; nome: string };
}

export function GraficoLinhas({
  titulo,
  series,
  desde,
  ate,
  passo,
  formato = formatarNumero,
  unidade = "",
  limite,
}: PropsLinhas) {
  const [cursor, setCursor] = useState<number | null>(null);
  const id = useId();
  const maximo = Math.max(limite?.valor ?? 0, ...series.flatMap((s) => s.pontos.map((p) => p.v ?? 0)));
  const { topo, marcas } = escalaY(maximo * 1.05);
  const x = (t: number) => MARGEM.e + ((t - desde) / Math.max(1, ate - desde)) * AREA.l;
  const y = (v: number) => MARGEM.c + AREA.a - (v / topo) * AREA.a;

  const caminho = (s: Serie) => {
    let d = "";
    let anterior: number | null = null;
    for (const p of s.pontos) {
      if (p.v === null) {
        anterior = null;
        continue;
      }
      d += `${anterior === null || p.t - anterior > passo * 3 ? "M" : "L"}${x(p.t).toFixed(1)} ${y(p.v).toFixed(1)}`;
      anterior = p.t;
    }
    return d;
  };

  const ultimo = series.map((s) => [...s.pontos].reverse().find((p) => p.v !== null)?.v ?? null);
  const descricao = `${titulo}: ${series.map((s, i) => `${s.nome} ${ultimo[i] === null ? "sem dados" : formato(ultimo[i] as number) + unidade}`).join("; ")}`;
  const vazio = series.every((s) => s.pontos.every((p) => p.v === null));

  function mover(e: PointerEvent<SVGSVGElement>) {
    const caixa = e.currentTarget.getBoundingClientRect();
    const px = ((e.clientX - caixa.left) / caixa.width) * L;
    setCursor(Math.min(ate, Math.max(desde, desde + ((px - MARGEM.e) / AREA.l) * (ate - desde))));
  }

  const valoresNoCursor =
    cursor === null
      ? []
      : series.map((s) => {
          const perto = s.pontos
            .filter((p) => p.v !== null)
            .reduce<{ t: number; v: number | null } | null>(
              (m, p) => (m === null || Math.abs(p.t - cursor) < Math.abs(m.t - cursor) ? p : m),
              null,
            );
          return {
            nome: s.nome,
            cor: s.cor,
            v: perto && Math.abs(perto.t - cursor) <= passo * 2 ? perto.v : null,
            t: perto?.t ?? cursor,
          };
        });

  return (
    <figure className="grafico">
      <svg
        viewBox={`0 0 ${L} ${A}`}
        role="img"
        aria-label={descricao}
        aria-describedby={`${id}-v`}
        onPointerMove={mover}
        onPointerLeave={() => setCursor(null)}
      >
        <Grelha marcas={marcas} topo={topo} formato={formato} />
        <EixoX desde={desde} ate={ate} />
        {limite && (
          <g>
            <line
              x1={MARGEM.e}
              x2={L - MARGEM.d}
              y1={y(limite.valor)}
              y2={y(limite.valor)}
              className="grafico-limite"
            />
            <text x={L - MARGEM.d - 4} y={y(limite.valor) - 4} textAnchor="end" className="grafico-eixo">
              {limite.nome}
            </text>
          </g>
        )}
        {series.map((s) => (
          <path
            key={s.nome}
            d={caminho(s)}
            className={`grafico-linha${s.tracejada ? " tracejada" : ""}`}
            style={{ stroke: s.cor }}
          />
        ))}
        {cursor !== null && (
          <line
            x1={x(cursor)}
            x2={x(cursor)}
            y1={MARGEM.c}
            y2={MARGEM.c + AREA.a}
            className="grafico-cursor"
          />
        )}
        {vazio && (
          <text x={L / 2} y={A / 2} textAnchor="middle" className="grafico-vazio">
            Ainda sem dados neste intervalo
          </text>
        )}
      </svg>
      <figcaption id={`${id}-v`}>
        <ul className="legenda">
          {series.map((s, i) => (
            <li key={s.nome}>
              <span className="amostra" style={{ background: s.cor }} />
              {s.nome}: <strong>{ultimo[i] === null ? "—" : formato(ultimo[i] as number) + unidade}</strong>
            </li>
          ))}
        </ul>
      </figcaption>
      {cursor !== null && (
        <div className="balao" style={{ left: `${(x(cursor) / L) * 100}%` }}>
          <b>{hora(cursor, ate - desde > 12 * 3600)}</b>
          {valoresNoCursor.map((v) => (
            <span key={v.nome}>
              <i style={{ background: v.cor }} />
              {v.nome}: {v.v === null ? "—" : formato(v.v) + unidade}
            </span>
          ))}
        </div>
      )}
    </figure>
  );
}

interface PropsBarras extends Eixo {
  titulo: string;
  pontos: { t: number; v: number; v2?: number }[];
  passo: number;
  nome: string;
  nome2?: string;
  cor?: string;
  cor2?: string;
}

/** Barras por intervalo de tempo; `v2` (opcional) é a parte de `v` a destacar (p.ex. os erros), desenhada por cima. */
export function GraficoBarras({
  titulo,
  pontos,
  desde,
  ate,
  passo,
  nome,
  nome2,
  cor = CORES[0],
  cor2 = "var(--erro)",
}: PropsBarras) {
  const [ativo, setAtivo] = useState<number | null>(null);
  const maximo = Math.max(0, ...pontos.map((p) => p.v));
  const { topo, marcas } = escalaY(maximo * 1.05);
  const bloco = (passo / Math.max(1, ate - desde)) * AREA.l;
  const largura = Math.max(1, bloco * 0.8);
  const total = pontos.reduce((a, p) => a + p.v, 0);
  const total2 = pontos.reduce((a, p) => a + (p.v2 ?? 0), 0);
  const descricao = `${titulo}: ${formatarNumero(total)} ${nome}${nome2 ? `, ${formatarNumero(total2)} ${nome2}` : ""} no intervalo`;
  const escolhido = ativo === null ? null : pontos[ativo];

  return (
    <figure className="grafico">
      <svg viewBox={`0 0 ${L} ${A}`} role="img" aria-label={descricao} onPointerLeave={() => setAtivo(null)}>
        <Grelha marcas={marcas} topo={topo} formato={formatarNumero} />
        <EixoX desde={desde} ate={ate} />
        {pontos.map((p, i) => {
          const xb = MARGEM.e + ((p.t - desde) / Math.max(1, ate - desde)) * AREA.l;
          const h = (p.v / topo) * AREA.a;
          const h2 = ((p.v2 ?? 0) / topo) * AREA.a;
          return (
            <g key={p.t} onPointerEnter={() => setAtivo(i)}>
              <rect x={xb} y={MARGEM.c} width={Math.max(bloco, 2)} height={AREA.a} className="grafico-zona" />
              <rect
                x={xb + (bloco - largura) / 2}
                y={MARGEM.c + AREA.a - h}
                width={largura}
                height={Math.max(h, 0)}
                style={{ fill: cor }}
                rx={1}
              />
              {h2 > 0 && (
                <rect
                  x={xb + (bloco - largura) / 2}
                  y={MARGEM.c + AREA.a - h2}
                  width={largura}
                  height={h2}
                  style={{ fill: cor2 }}
                  rx={1}
                />
              )}
            </g>
          );
        })}
        {pontos.length === 0 && (
          <text x={L / 2} y={A / 2} textAnchor="middle" className="grafico-vazio">
            Ainda sem dados neste intervalo
          </text>
        )}
      </svg>
      <figcaption>
        <ul className="legenda">
          <li>
            <span className="amostra" style={{ background: cor }} />
            {nome}: <strong>{formatarNumero(total)}</strong>
          </li>
          {nome2 && (
            <li>
              <span className="amostra" style={{ background: cor2 }} />
              {nome2}: <strong>{formatarNumero(total2)}</strong>
            </li>
          )}
        </ul>
      </figcaption>
      {escolhido && (
        <div
          className="balao"
          style={{
            left: `${((MARGEM.e + ((escolhido.t - desde) / Math.max(1, ate - desde)) * AREA.l) / L) * 100}%`,
          }}
        >
          <b>{hora(escolhido.t, ate - desde > 12 * 3600)}</b>
          <span>
            {nome}: {formatarNumero(escolhido.v)}
          </span>
          {nome2 && (
            <span>
              {nome2}: {formatarNumero(escolhido.v2 ?? 0)}
            </span>
          )}
        </div>
      )}
    </figure>
  );
}

/** Barras horizontais para distribuições (línguas, temas, páginas…). */
export function BarrasH({
  titulo,
  itens,
  cor = CORES[0],
  vazio = "Sem dados neste intervalo",
}: {
  titulo: string;
  itens: { chave: string; n: number }[];
  cor?: string;
  vazio?: string;
}) {
  const maximo = Math.max(1, ...itens.map((i) => i.n));
  const total = itens.reduce((a, i) => a + i.n, 0);
  return (
    <figure className="barras-h" aria-label={titulo}>
      {itens.length === 0 ? (
        <p className="suave">{vazio}</p>
      ) : (
        <ul>
          {itens.slice(0, 10).map((i) => (
            <li key={i.chave}>
              <span className="nome">{i.chave}</span>
              <span className="pista">
                <span className="barra" style={{ width: `${(i.n / maximo) * 100}%`, background: cor }} />
              </span>
              <span className="valor">
                {formatarNumero(i.n)} <small>({Math.round((i.n / total) * 100)} %)</small>
              </span>
            </li>
          ))}
        </ul>
      )}
    </figure>
  );
}

/** Uma rosca (distribuição com poucas partes, como o tipo de dispositivo). */
export function Rosca({ titulo, itens }: { titulo: string; itens: { chave: string; n: number }[] }) {
  const total = itens.reduce((a, i) => a + i.n, 0);
  const R = 42;
  const C = 2 * Math.PI * R;
  let acumulado = 0;
  return (
    <figure className="rosca">
      <svg
        viewBox="0 0 120 120"
        role="img"
        aria-label={`${titulo}: ${itens.map((i) => `${i.chave} ${i.n}`).join(", ") || "sem dados"}`}
      >
        <circle cx="60" cy="60" r={R} className="rosca-fundo" />
        {total > 0 &&
          itens.map((i, k) => {
            const parte = (i.n / total) * C;
            const e = (
              <circle
                key={i.chave}
                cx="60"
                cy="60"
                r={R}
                className="rosca-parte"
                style={{ stroke: CORES[k % CORES.length] }}
                strokeDasharray={`${parte} ${C - parte}`}
                strokeDashoffset={-acumulado}
                transform="rotate(-90 60 60)"
              />
            );
            acumulado += parte;
            return e;
          })}
        <text x="60" y="64" textAnchor="middle" className="rosca-total">
          {formatarNumero(total)}
        </text>
      </svg>
      <ul className="legenda">
        {itens.map((i, k) => (
          <li key={i.chave}>
            <span className="amostra" style={{ background: CORES[k % CORES.length] }} />
            {i.chave}: <strong>{formatarNumero(i.n)}</strong>
          </li>
        ))}
        {itens.length === 0 && <li className="suave">Sem dados neste intervalo</li>}
      </ul>
    </figure>
  );
}

/** Uma barra de utilização com partes (p.ex. a memória do servidor e do motor face ao limite). */
export function Medidor({
  titulo,
  partes,
  limite,
  unidade = "MB",
}: {
  titulo: string;
  partes: { nome: string; valor: number; cor: string }[];
  limite: number | null;
  unidade?: string;
}) {
  const soma = partes.reduce((a, p) => a + p.valor, 0);
  const maximo = limite ?? (soma * 1.25 || 1);
  const pct = limite ? Math.round((soma / limite) * 100) : null;
  return (
    <figure
      className="medidor"
      aria-label={`${titulo}: ${Math.round(soma)} ${unidade}${limite ? ` de ${limite} ${unidade}` : ""}`}
    >
      <div className="pista">
        {partes.map((p) => (
          <span
            key={p.nome}
            className="parte"
            style={{ width: `${Math.min(100, (p.valor / maximo) * 100)}%`, background: p.cor }}
            title={`${p.nome}: ${Math.round(p.valor)} ${unidade}`}
          />
        ))}
      </div>
      <ul className="legenda">
        {partes.map((p) => (
          <li key={p.nome}>
            <span className="amostra" style={{ background: p.cor }} />
            {p.nome}:{" "}
            <strong>
              {Math.round(p.valor)} {unidade}
            </strong>
          </li>
        ))}
        <li className={pct !== null && pct >= 85 ? "cor-erro" : "suave"}>
          {limite
            ? `${pct} % do limite de ${limite} ${unidade}`
            : "sem limite definido (fora de um contentor)"}
        </li>
      </ul>
    </figure>
  );
}
