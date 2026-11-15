import { type KeyboardEvent, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import {
  ANO_MAXIMO,
  ANO_MINIMO,
  celulasDoMes,
  dataNumerica,
  dataPorExtenso,
  limitar,
  msDeIso,
  nomesDosDias,
  primeiroDiaDaSemana,
  somarDias,
  somarMeses,
  tituloDoMes,
} from "./calendario";
import { dataDeHoje } from "./dataSorteio";
import { useI18n } from "./i18n";
import { Icone } from "./icones";
import { useMenuFlutuante } from "./menu";

const LARGURA_CALENDARIO = 312; // px
const ALTURA_CALENDARIO = 360; // px: o que o calendário ocupa; com menos espaço por baixo do botão abre para cima

/** Para onde vai o foco com cada tecla (setas ±1 dia e ±1 semana, PageUp/PageDown ±1 mês, Home/End início e fim da semana); `null` se a tecla não conta. */
function destinoDaTecla(tecla: string, iso: string, primeiroDia: number): string | null {
  const naSemana = (new Date(msDeIso(iso)).getUTCDay() - primeiroDia + 7) % 7; // 0 = o primeiro dia da semana
  switch (tecla) {
    case "ArrowLeft":
      return somarDias(iso, -1);
    case "ArrowRight":
      return somarDias(iso, 1);
    case "ArrowUp":
      return somarDias(iso, -7);
    case "ArrowDown":
      return somarDias(iso, 7);
    case "PageUp":
      return somarMeses(iso, -1);
    case "PageDown":
      return somarMeses(iso, 1);
    case "Home":
      return somarDias(iso, -naSemana);
    case "End":
      return somarDias(iso, 6 - naSemana);
    default:
      return null;
  }
}

/**
 * O calendário da data do sorteio. Um `<input type="date">` não serve: o texto «dd/mm/aaaa» e o seletor são do browser, na língua do
 * browser e não na do site. Aqui os meses, os dias da semana, a ordem da data (dd/mm/aaaa, mm/dd/yyyy…) e o primeiro dia da semana
 * seguem a língua escolhida no site (`Intl`), e os botões («Hoje», «Limpar», mês anterior/seguinte) vêm das 22 línguas.
 *
 * Teclado: setas movem o dia (±1 e ±7), PageUp/PageDown o mês, Home/End o início e o fim da semana, Enter/Espaço escolhem, Esc fecha.
 * O painel desenha-se no `body`: os cartões têm máscara nos entalhes e cortariam um painel fixo.
 */
export function SeletorData({
  valor,
  aoMudar,
  rotulo,
  testid,
}: {
  valor: string; // aaaa-mm-dd ou ""
  aoMudar: (iso: string) => void;
  rotulo: string;
  testid: string;
}) {
  const { t, lingua } = useI18n();
  const menu = useMenuFlutuante<HTMLDivElement>("esq", LARGURA_CALENDARIO, ALTURA_CALENDARIO);
  const { aberto, alternar, fechar, refPainel, refBotao } = menu;
  const hoje = dataDeHoje();
  const [foco, setFoco] = useState(valor || hoje); // o dia com o foco do teclado; o mês mostrado é o dele
  const focarDia = useRef(false); // só se leva o foco para o dia ao abrir e ao navegar por teclado (não ao clicar nas setas do mês)

  const primeiro = primeiroDiaDaSemana(lingua);
  const ms = msDeIso(foco);
  const ano = new Date(ms).getUTCFullYear();
  const mes = new Date(ms).getUTCMonth();
  const celulas = celulasDoMes(ano, mes, primeiro);
  const dias = nomesDosDias(lingua, primeiro);
  const texto = valor ? dataNumerica(lingua, valor) : t("web_data_escolher");

  // biome-ignore lint/correctness/useExhaustiveDependencies: só quando o dia com o foco muda ou o painel abre
  useEffect(() => {
    if (!aberto || !focarDia.current) return;
    focarDia.current = false;
    refPainel.current?.querySelector<HTMLElement>(`[data-iso="${foco}"]`)?.focus();
  }, [aberto, foco]);

  const abrir = () => {
    setFoco(valor || hoje);
    focarDia.current = true;
    alternar();
  };
  const escolher = (iso: string) => {
    aoMudar(iso);
    fechar();
    refBotao.current?.focus();
  };
  const ir = (iso: string) => {
    focarDia.current = true;
    setFoco(limitar(iso));
  };
  const aoTeclar = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Tab") {
      // o foco dá a volta dentro do calendário enquanto está aberto
      const todos = [
        ...(refPainel.current?.querySelectorAll<HTMLElement>("button:not([disabled]):not([tabindex='-1'])") ??
          []),
      ];
      const primeiroEl = todos[0];
      const ultimoEl = todos[todos.length - 1];
      if (e.shiftKey && document.activeElement === primeiroEl) {
        e.preventDefault();
        ultimoEl?.focus();
      } else if (!e.shiftKey && document.activeElement === ultimoEl) {
        e.preventDefault();
        primeiroEl?.focus();
      }
      return;
    }
    const alvo = (e.target as HTMLElement).dataset.iso;
    if (!alvo) return; // as setas só movem o dia quando o foco está num dia
    const destino = destinoDaTecla(e.key, alvo, primeiro);
    if (destino) {
      e.preventDefault();
      ir(destino);
    }
  };
  const mudarMes = (n: number) => setFoco(somarMeses(foco, n));

  const painel = (
    <div
      ref={refPainel}
      id={`${testid}-calendario`}
      role="dialog"
      aria-label={rotulo}
      className="painel-flutuante calendario"
      style={menu.estilo}
      onKeyDown={aoTeclar}
      data-testid={`${testid}-calendario`}
    >
      <div className="calendario-topo">
        <button
          type="button"
          onClick={() => mudarMes(-1)}
          disabled={ano <= ANO_MINIMO && mes === 0}
          aria-label={t("web_data_anterior")}
          data-testid={`${testid}-anterior`}
        >
          <Icone nome="anterior" tamanho={18} />
        </button>
        <strong aria-live="polite" data-testid={`${testid}-mes`}>
          {tituloDoMes(lingua, foco)}
        </strong>
        <button
          type="button"
          onClick={() => mudarMes(1)}
          disabled={ano >= ANO_MAXIMO && mes === 11}
          aria-label={t("web_data_seguinte")}
          data-testid={`${testid}-seguinte`}
        >
          <Icone nome="seguinte" tamanho={18} />
        </button>
      </div>
      <table className="calendario-grelha" aria-label={tituloDoMes(lingua, foco)}>
        <thead>
          <tr>
            {dias.map((d) => (
              <th key={d} scope="col">
                {d}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: 6 }, (_, linha) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: a posição da semana no mês é o que a identifica
            <tr key={linha}>
              {celulas.slice(linha * 7, linha * 7 + 7).map((c) => (
                <td key={c.iso}>
                  <button
                    type="button"
                    className={`calendario-dia${c.doMes ? "" : " fora"}${c.iso === hoje ? " hoje" : ""}`}
                    tabIndex={c.iso === foco ? 0 : -1}
                    aria-label={dataPorExtenso(lingua, c.iso)}
                    aria-pressed={c.iso === valor}
                    aria-current={c.iso === hoje ? "date" : undefined}
                    data-iso={c.iso}
                    onClick={() => escolher(c.iso)}
                  >
                    {c.dia}
                  </button>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="calendario-pe">
        <button type="button" onClick={() => escolher(hoje)} data-testid={`${testid}-hoje`}>
          {t("web_data_hoje")}
        </button>
        <button type="button" onClick={() => escolher("")} disabled={!valor} data-testid={`${testid}-limpar`}>
          {t("web_data_limpar")}
        </button>
      </div>
    </div>
  );

  return (
    <div className="seletor-data">
      <button
        type="button"
        ref={refBotao}
        className="seletor-botao"
        aria-haspopup="dialog"
        aria-expanded={aberto}
        aria-controls={`${testid}-calendario`}
        aria-label={`${rotulo}: ${texto}`}
        onClick={abrir}
        data-testid={testid}
      >
        <Icone nome="calendario" tamanho={20} />
        <span className={`seletor-nome${valor ? "" : " sem-data"}`}>{texto}</span>
        <Icone nome="baixo" tamanho={14} />
      </button>
      {aberto && createPortal(painel, document.body)}
    </div>
  );
}
