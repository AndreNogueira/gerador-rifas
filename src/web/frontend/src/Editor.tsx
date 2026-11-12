import {
  type KeyboardEvent,
  type PointerEvent,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ASCENTE,
  type Desenho,
  type Elemento,
  LIMITES,
  lerGuardado,
  limitar,
  modeloComTalao,
  novo,
  paraEnviar,
  problemas,
  semProblemas,
  type Tipo,
} from "./editor-modelo";
import { useI18n } from "./i18n";
import { navegar } from "./rota";
import { useSessao } from "./sessao";

const CHAVE = "rifas.editor";

function lerDoBrowser(): Desenho {
  try {
    return lerGuardado(localStorage.getItem(CHAVE)) ?? modeloComTalao();
  } catch {
    return modeloComTalao();
  }
}

/** A caixa (em pt) de um elemento, para o contorno de seleção: a do browser (`getBBox`) para texto, a geométrica para o resto. */
function caixa(e: Elemento, no: SVGGraphicsElement | null) {
  if (e.tipo === "retangulo" || e.tipo === "linha") {
    return {
      x: Math.min(e.x, e.x + e.w),
      y: Math.min(e.y, e.y + e.h),
      w: Math.abs(e.w) || 1,
      h: Math.abs(e.h) || 1,
    };
  }
  try {
    const b = no?.getBBox();
    if (b && (b.width || b.height)) return { x: b.x, y: b.y, w: b.width, h: b.height };
  } catch {
    // sem layout (jsdom): usa a estimativa
  }
  const w = Math.max(e.tipo === "numero" ? 4 : e.texto.length || 1, 1) * e.tamanho * 0.6;
  const x = e.alinhamento === "c" ? e.x - w / 2 : e.alinhamento === "d" ? e.x - w : e.x;
  return e.rot === 90
    ? { x: e.x - e.tamanho * ASCENTE, y: e.y - w, w: e.tamanho, h: w }
    : { x, y: e.y - e.tamanho * ASCENTE, w, h: e.tamanho };
}

function Numero({
  valor,
  aoMudar,
  rotulo,
  min,
  max,
  passo = 1,
}: {
  valor: number;
  aoMudar: (v: number) => void;
  rotulo: string;
  min?: number;
  max?: number;
  passo?: number;
}) {
  return (
    <label>
      {rotulo}
      <input
        type="number"
        value={Number.isFinite(valor) ? valor : 0}
        min={min}
        max={max}
        step={passo}
        onChange={(ev) => aoMudar(Number(ev.target.value))}
      />
    </label>
  );
}

function Cor({ valor, aoMudar, rotulo }: { valor: string; aoMudar: (v: string) => void; rotulo: string }) {
  return (
    <label className="editor-cor">
      {rotulo}
      <input type="color" value={valor || "#000000"} onChange={(ev) => aoMudar(ev.target.value)} />
    </label>
  );
}

/**
 * O editor de templates (X1): em vez de um template do Canva, desenha-se UMA rifa (retângulos, linhas, textos e o número 0001, uma ou duas vezes).
 * O ecrã é um SVG com a letra Vera (a mesma do PDF), por isso o que se vê é o que sai; «Usar este template» envia o desenho ao servidor, que
 * cria o PDF e os algarismos na sessão, e volta-se ao ecrã principal. O rascunho fica só neste browser.
 */
export function Editor() {
  const { t } = useI18n();
  const s = useSessao();
  const [d, setD] = useState<Desenho>(lerDoBrowser);
  const [sel, setSel] = useState<string | null>(null);
  const svg = useRef<SVGSVGElement>(null);
  const nos = useRef(new Map<string, SVGGraphicsElement>());
  const arrasto = useRef<{
    id: string;
    modo: "mover" | "tamanho";
    px: number;
    py: number;
    ex: number;
    ey: number;
    ew: number;
    eh: number;
  } | null>(null);
  const [selecionado, setSelecionado] = useState<{ x: number; y: number; w: number; h: number } | null>(null);

  useEffect(() => {
    try {
      localStorage.setItem(CHAVE, JSON.stringify(d));
    } catch {
      // sem armazenamento (janela privada): o rascunho só dura esta visita
    }
  }, [d]);

  const p = useMemo(() => problemas(d), [d]);
  const atual = d.elementos.find((e) => e.id === sel) ?? null;

  // a caixa de um texto só se conhece depois de desenhado
  useLayoutEffect(() => {
    setSelecionado(atual ? caixa(atual, nos.current.get(atual.id) ?? null) : null);
  }, [atual]);

  const mudar = (id: string, mudancas: Partial<Elemento>) =>
    setD((x) => ({ ...x, elementos: x.elementos.map((e) => (e.id === id ? { ...e, ...mudancas } : e)) }));

  const acrescentar = (tipo: Tipo) => {
    if (d.elementos.length >= LIMITES.elementos) return;
    const e = novo(tipo, d);
    setD((x) => ({ ...x, elementos: [...x.elementos, e] }));
    setSel(e.id);
  };
  const apagar = () => {
    if (!atual) return;
    setD((x) => ({ ...x, elementos: x.elementos.filter((e) => e.id !== atual.id) }));
    setSel(null);
  };

  const escala = () => {
    const r = svg.current?.getBoundingClientRect();
    return r?.width ? d.largura / r.width : 1;
  };
  const comecar = (ev: PointerEvent, e: Elemento, modo: "mover" | "tamanho") => {
    ev.stopPropagation();
    setSel(e.id);
    svg.current?.setPointerCapture?.(ev.pointerId);
    arrasto.current = { id: e.id, modo, px: ev.clientX, py: ev.clientY, ex: e.x, ey: e.y, ew: e.w, eh: e.h };
  };
  const arrastar = (ev: PointerEvent) => {
    const a = arrasto.current;
    if (!a) return;
    const k = escala();
    const dx = (ev.clientX - a.px) * k;
    const dy = (ev.clientY - a.py) * k;
    if (a.modo === "mover") mudar(a.id, { x: Math.round(a.ex + dx), y: Math.round(a.ey + dy) });
    else mudar(a.id, { w: Math.round(a.ew + dx), h: Math.round(a.eh + dy) });
  };
  const teclas = (ev: KeyboardEvent, e: Elemento) => {
    const passo = ev.shiftKey ? 10 : 1;
    const mov: Record<string, [number, number]> = {
      ArrowLeft: [-passo, 0],
      ArrowRight: [passo, 0],
      ArrowUp: [0, -passo],
      ArrowDown: [0, passo],
    };
    const m = mov[ev.key];
    if (m) {
      ev.preventDefault();
      mudar(e.id, { x: e.x + m[0], y: e.y + m[1] });
    } else if (ev.key === "Delete" || ev.key === "Backspace") {
      ev.preventDefault();
      apagar();
    }
  };

  const rotulo = (e: Elemento) =>
    e.tipo === "texto"
      ? `${t("web_editor_texto")}: ${e.texto}`
      : e.tipo === "retangulo"
        ? t("web_editor_retangulo")
        : e.tipo === "linha"
          ? t("web_editor_linha")
          : t("web_editor_numero");

  const desenhar = (e: Elemento) => {
    const ref = (no: SVGGraphicsElement | null) => {
      if (no) nos.current.set(e.id, no);
      else nos.current.delete(e.id);
    };
    const comum = {
      ref,
      tabIndex: 0,
      role: "button",
      "aria-label": rotulo(e),
      "aria-pressed": sel === e.id,
      className: `editor-el${sel === e.id ? " sel" : ""}`,
      "data-testid": `el-${e.tipo}`,
      onPointerDown: (ev: PointerEvent) => comecar(ev, e, "mover"),
      onKeyDown: (ev: KeyboardEvent) => teclas(ev, e),
      onFocus: () => setSel(e.id),
    };
    if (e.tipo === "retangulo") {
      return (
        <g key={e.id} {...comum}>
          <rect
            x={Math.min(e.x, e.x + e.w)}
            y={Math.min(e.y, e.y + e.h)}
            width={Math.abs(e.w)}
            height={Math.abs(e.h)}
            rx={Math.min(e.raio, Math.abs(e.w) / 2, Math.abs(e.h) / 2)}
            fill={e.cor}
            stroke={e.contorno && e.espessura > 0 ? e.contorno : "none"}
            strokeWidth={e.espessura}
          />
        </g>
      );
    }
    if (e.tipo === "linha") {
      return (
        <g key={e.id} {...comum}>
          <line
            x1={e.x}
            y1={e.y}
            x2={e.x + e.w}
            y2={e.y + e.h}
            stroke="transparent"
            strokeWidth={Math.max(10, e.espessura)}
          />
          <line
            x1={e.x}
            y1={e.y}
            x2={e.x + e.w}
            y2={e.y + e.h}
            stroke={e.contorno}
            strokeWidth={Math.max(e.espessura, 0.1)}
            strokeDasharray={e.tracejado ? "3 3" : undefined}
          />
        </g>
      );
    }
    return (
      <g key={e.id} {...comum}>
        <text
          x={e.x}
          y={e.y}
          fill={e.cor}
          fontSize={e.tamanho}
          fontFamily={e.negrito ? "VeraEditorBd, sans-serif" : "VeraEditor, sans-serif"}
          textAnchor={e.alinhamento === "c" ? "middle" : e.alinhamento === "d" ? "end" : "start"}
          transform={e.rot ? `rotate(-${e.rot} ${e.x} ${e.y})` : undefined}
        >
          {e.tipo === "numero" ? "0001" : e.texto}
        </text>
      </g>
    );
  };

  // com a caixa do <text> rodada, o getBBox já vem na unidade do elemento: para o contorno basta desenhá-la com a mesma rotação
  const rotacaoSel =
    atual?.rot && (atual.tipo === "texto" || atual.tipo === "numero")
      ? `rotate(-${atual.rot} ${atual.x} ${atual.y})`
      : undefined;
  const usarOk = semProblemas(p) && !!s.sessao && s.ocupado === null;

  return (
    <div className="pagina pagina-larga">
      <section className="cartao editor" data-testid="editor">
        <h1>{t("web_editor")}</h1>
        <p className="suave">{t("web_editor_intro")}</p>

        <div className="editor-barra" role="toolbar" aria-label={t("web_editor")}>
          {(["texto", "retangulo", "linha", "numero"] as const).map((tp) => (
            <button
              key={tp}
              type="button"
              className="secundario"
              onClick={() => acrescentar(tp)}
              data-testid={`add-${tp}`}
            >
              + {t(`web_editor_${tp}`)}
            </button>
          ))}
          <button
            type="button"
            className="secundario"
            onClick={() => {
              setD(modeloComTalao());
              setSel(null);
            }}
            data-testid="editor-modelo"
          >
            {t("web_editor_modelo")}
          </button>
        </div>

        <div className="editor-corpo">
          <div className="editor-tela">
            <svg
              ref={svg}
              viewBox={`0 0 ${d.largura} ${d.altura}`}
              aria-label={t("web_editor")}
              data-testid="editor-tela"
              onPointerDown={() => setSel(null)}
              onPointerMove={arrastar}
              onPointerUp={() => {
                arrasto.current = null;
              }}
              onPointerCancel={() => {
                arrasto.current = null;
              }}
            >
              <rect x={0} y={0} width={d.largura} height={d.altura} fill={d.fundo} />
              {d.elementos.map(desenhar)}
              {atual && selecionado && (
                <g pointerEvents="none">
                  <rect
                    className="editor-selecao"
                    x={selecionado.x - 2}
                    y={selecionado.y - 2}
                    width={selecionado.w + 4}
                    height={selecionado.h + 4}
                    transform={atual.tipo === "retangulo" || atual.tipo === "linha" ? undefined : rotacaoSel}
                  />
                </g>
              )}
              {atual && (atual.tipo === "retangulo" || atual.tipo === "linha") && (
                <circle
                  className="editor-pega"
                  cx={atual.x + atual.w}
                  cy={atual.y + atual.h}
                  r={5}
                  data-testid="editor-pega"
                  onPointerDown={(ev) => comecar(ev, atual, "tamanho")}
                />
              )}
            </svg>
          </div>

          <div className="editor-inspetor">
            <fieldset>
              <legend>{t("web_editor_pagina")}</legend>
              <div className="linha">
                <Numero
                  rotulo="W"
                  valor={d.largura}
                  min={LIMITES.larguraMin}
                  max={LIMITES.larguraMax}
                  aoMudar={(v) =>
                    setD((x) => ({ ...x, largura: limitar(v, LIMITES.larguraMin, LIMITES.larguraMax) }))
                  }
                />
                <Numero
                  rotulo="H"
                  valor={d.altura}
                  min={LIMITES.alturaMin}
                  max={LIMITES.alturaMax}
                  aoMudar={(v) =>
                    setD((x) => ({ ...x, altura: limitar(v, LIMITES.alturaMin, LIMITES.alturaMax) }))
                  }
                />
                <Cor
                  rotulo={t("web_editor_fundo")}
                  valor={d.fundo}
                  aoMudar={(v) => setD((x) => ({ ...x, fundo: v }))}
                />
              </div>
            </fieldset>

            {atual && (
              <fieldset data-testid="editor-inspetor">
                <legend>{rotulo(atual).slice(0, 40)}</legend>
                <div className="linha">
                  <Numero rotulo="X" valor={atual.x} aoMudar={(v) => mudar(atual.id, { x: v })} passo={0.5} />
                  <Numero rotulo="Y" valor={atual.y} aoMudar={(v) => mudar(atual.id, { y: v })} passo={0.5} />
                  {(atual.tipo === "retangulo" || atual.tipo === "linha") && (
                    <>
                      <Numero rotulo="W" valor={atual.w} aoMudar={(v) => mudar(atual.id, { w: v })} />
                      <Numero rotulo="H" valor={atual.h} aoMudar={(v) => mudar(atual.id, { h: v })} />
                    </>
                  )}
                </div>
                {atual.tipo === "texto" && (
                  <label>
                    {t("web_editor_texto")}
                    <input
                      value={atual.texto}
                      maxLength={LIMITES.texto}
                      onChange={(ev) => mudar(atual.id, { texto: ev.target.value })}
                      data-testid="editor-texto"
                    />
                  </label>
                )}
                <div className="linha">
                  {(atual.tipo === "texto" || atual.tipo === "numero") && (
                    <>
                      <Numero
                        rotulo={t("web_editor_tamanho")}
                        valor={atual.tamanho}
                        min={LIMITES.tamanhoMin}
                        max={LIMITES.tamanhoMax}
                        aoMudar={(v) =>
                          mudar(atual.id, { tamanho: limitar(v, LIMITES.tamanhoMin, LIMITES.tamanhoMax) })
                        }
                      />
                      <Cor
                        rotulo={t("web_editor_cor")}
                        valor={atual.cor}
                        aoMudar={(v) => mudar(atual.id, { cor: v })}
                      />
                    </>
                  )}
                  {atual.tipo === "retangulo" && (
                    <Cor
                      rotulo={t("web_editor_cor")}
                      valor={atual.cor}
                      aoMudar={(v) => mudar(atual.id, { cor: v })}
                    />
                  )}
                  {(atual.tipo === "retangulo" || atual.tipo === "linha") && (
                    <>
                      <Cor
                        rotulo={t("web_editor_contorno")}
                        valor={atual.contorno || "#000000"}
                        aoMudar={(v) => mudar(atual.id, { contorno: v, espessura: atual.espessura || 1 })}
                      />
                      <Numero
                        rotulo={`${t("web_editor_contorno")} (pt)`}
                        valor={atual.espessura}
                        min={atual.tipo === "linha" ? 0.5 : 0}
                        max={20}
                        passo={0.5}
                        aoMudar={(v) => mudar(atual.id, { espessura: limitar(v, 0, 20) })}
                      />
                    </>
                  )}
                </div>
                <div className="linha">
                  {atual.tipo === "texto" && (
                    <label className="opcao">
                      <input
                        type="checkbox"
                        checked={atual.negrito}
                        onChange={(ev) => mudar(atual.id, { negrito: ev.target.checked })}
                      />
                      {t("web_editor_negrito")}
                    </label>
                  )}
                  {(atual.tipo === "texto" || atual.tipo === "numero") && (
                    <label className="opcao">
                      <input
                        type="checkbox"
                        checked={atual.rot === 90}
                        onChange={(ev) => mudar(atual.id, { rot: ev.target.checked ? 90 : 0 })}
                        data-testid="editor-rodar"
                      />
                      {t("web_editor_rodar")}
                    </label>
                  )}
                  <button type="button" className="secundario" onClick={apagar} data-testid="editor-apagar">
                    {t("web_editor_apagar")}
                  </button>
                </div>
              </fieldset>
            )}
          </div>
        </div>

        {p.numero && (
          <p role="alert" className="cor-aviso" data-testid="editor-erro-numero">
            {t("err_editor_numero")}
          </p>
        )}
        {p.digitos && (
          <p role="alert" className="cor-aviso" data-testid="editor-erro-digitos">
            {t("err_editor_digitos", { texto: p.digitos })}
          </p>
        )}
        <div className="linha">
          <button
            type="button"
            disabled={!usarOk}
            onClick={() =>
              void s.usarEditor(paraEnviar(d), () => {
                navegar("/");
              })
            }
            data-testid="editor-usar"
          >
            {t("web_galeria_usar")}
          </button>
        </div>
      </section>
    </div>
  );
}
