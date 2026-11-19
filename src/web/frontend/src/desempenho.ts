// Mede, nos browsers que o permitem, o desempenho REAL da pagina (os «Core Web Vitals») e diz-o ao servidor UMA vez por separador, quando se sai da pagina:
// quanto demorou a aparecer (LCP), quanto o conteudo se mexeu (CLS) e a resposta mais lenta a um clique (INP). Vao so estes tres numeros: nada que identifique
// quem visita nem que pagina era. O servidor guarda-os com a classe do aparelho (telemovel ou computador) e o painel mostra o percentil 75 de cada dia.

/** Junta as medidas à medida que o browser as dá e devolve os três números pedidos ao servidor. */
export class Coletor {
  private lcpMs = 0;
  private janelaCls = 0;
  private maiorCls = 0;
  private inicioJanela = 0;
  private ultimoSalto = 0;
  private interacoes = new Map<number, number>();

  /** O maior elemento desenhado até agora (o último valor é o que conta). */
  lcp(ms: number): void {
    if (ms > this.lcpMs) this.lcpMs = ms;
  }

  /** Um salto do conteúdo: soma-se à «janela» em curso (até 1 s de intervalo e 5 s no total); o CLS é a pior janela. Os saltos logo após um clique não contam. */
  saltoDeLayout(valor: number, inicio: number, houveInteracao: boolean): void {
    if (houveInteracao) return;
    if (this.janelaCls > 0 && inicio - this.ultimoSalto < 1000 && inicio - this.inicioJanela < 5000) {
      this.janelaCls += valor;
    } else {
      this.janelaCls = valor;
      this.inicioJanela = inicio;
    }
    this.ultimoSalto = inicio;
    if (this.janelaCls > this.maiorCls) this.maiorCls = this.janelaCls;
  }

  /** Uma interação (clique, tecla): fica a duração mais longa de cada uma. */
  interacao(id: number, duracaoMs: number): void {
    if (id > 0 && duracaoMs > (this.interacoes.get(id) ?? 0)) this.interacoes.set(id, duracaoMs);
  }

  /** O INP: a pior interação (ou a 50.ª pior quando há muitas), 0 se não houve nenhuma. */
  private inp(): number {
    const duracoes = [...this.interacoes.values()].sort((a, b) => b - a);
    return duracoes[Math.min(duracoes.length - 1, Math.floor(duracoes.length / 50))] ?? 0;
  }

  /** O que se envia: LCP e INP em ms, CLS vezes 1000, tudo inteiro e dentro dos limites do servidor. Sem LCP (nada foi desenhado) não há o que enviar. */
  resumo(): { lcp: number; cls: number; inp: number } | null {
    if (this.lcpMs <= 0) return null;
    return {
      lcp: Math.round(Math.min(this.lcpMs, 60000)),
      cls: Math.round(Math.min(this.maiorCls, 10) * 1000),
      inp: Math.round(Math.min(this.inp(), 10000)),
    };
  }
}

type EntradaDeLayout = PerformanceEntry & { value: number; hadRecentInput: boolean };
type EntradaDeEvento = PerformanceEntry & { interactionId?: number };

function observar(tipo: string, aoVer: (e: PerformanceEntry[]) => void, extra: object = {}): void {
  try {
    if (!PerformanceObserver.supportedEntryTypes?.includes(tipo)) return;
    new PerformanceObserver((lista) => aoVer(lista.getEntries())).observe({
      type: tipo,
      buffered: true,
      ...extra,
    } as PerformanceObserverInit);
  } catch {
    /* este browser não mede isto */
  }
}

export function iniciarDesempenho(): void {
  try {
    if (typeof PerformanceObserver === "undefined" || sessionStorage.getItem("rifas.desempenho")) return;
  } catch {
    return; // sem armazenamento: não se mede (para não repetir a cada página)
  }
  const c = new Coletor();
  observar("largest-contentful-paint", (es) => {
    for (const e of es) c.lcp(e.startTime);
  });
  observar("layout-shift", (es) => {
    for (const e of es as EntradaDeLayout[]) c.saltoDeLayout(e.value, e.startTime, e.hadRecentInput);
  });
  observar(
    "event",
    (es) => {
      for (const e of es as EntradaDeEvento[]) c.interacao(e.interactionId ?? 0, e.duration);
    },
    { durationThreshold: 40 },
  );

  let enviado = false;
  const enviar = (forcar = false) => {
    if (enviado || (!forcar && document.visibilityState !== "hidden")) return;
    const r = c.resumo();
    if (!r) return;
    enviado = true;
    try {
      sessionStorage.setItem("rifas.desempenho", "1");
    } catch {
      /* ignora */
    }
    const corpo = JSON.stringify(r);
    try {
      if (navigator.sendBeacon?.("/api/desempenho", new Blob([corpo], { type: "application/json" }))) return;
      void fetch("/api/desempenho", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: corpo,
        keepalive: true,
      });
    } catch {
      /* as estatísticas nunca incomodam o utilizador */
    }
  };
  document.addEventListener("visibilitychange", () => enviar());
  addEventListener("pagehide", () => enviar(true));
}
