// O histórico (desfazer e refazer) do editor: guarda até 50 estados anteriores e junta numa só as alterações seguidas ao mesmo valor (arrastar,
// escrever num campo, carregar numa seta), para um «desfazer» desfazer o gesto inteiro e não um píxel.
import { useCallback, useRef, useState } from "react";

const MAX = 50;
const JUNTAR_MS = 1200;

interface Estado<T> {
  atual: T;
  passado: T[];
  futuro: T[];
}

export function useHistorico<T>(inicial: () => T) {
  const [estado, setEstado] = useState<Estado<T>>(() => ({ atual: inicial(), passado: [], futuro: [] }));
  const grupo = useRef<{ chave: string; ts: number } | null>(null);

  /** Muda o estado; com `chave`, mudanças seguidas com a mesma chave (a menos de 1,2 s) contam como uma só. */
  const definir = useCallback((alterar: (x: T) => T, chave?: string) => {
    const agora = Date.now();
    const junta = !!chave && grupo.current?.chave === chave && agora - grupo.current.ts < JUNTAR_MS;
    grupo.current = chave ? { chave, ts: agora } : null;
    setEstado((e) => {
      const novo = alterar(e.atual);
      if (novo === e.atual) return e;
      return {
        atual: novo,
        passado: junta ? e.passado : [...e.passado.slice(-(MAX - 1)), e.atual],
        futuro: [],
      };
    });
  }, []);

  /** Troca o estado e apaga o histórico (abrir um desenho partilhado, recomeçar). */
  const substituir = useCallback((novo: T) => {
    grupo.current = null;
    setEstado({ atual: novo, passado: [], futuro: [] });
  }, []);

  const desfazer = useCallback(() => {
    grupo.current = null;
    setEstado((e) => {
      const anterior = e.passado[e.passado.length - 1];
      if (anterior === undefined) return e;
      return { atual: anterior, passado: e.passado.slice(0, -1), futuro: [e.atual, ...e.futuro] };
    });
  }, []);

  const refazer = useCallback(() => {
    grupo.current = null;
    setEstado((e) => {
      const seguinte = e.futuro[0];
      if (seguinte === undefined) return e;
      return { atual: seguinte, passado: [...e.passado, e.atual], futuro: e.futuro.slice(1) };
    });
  }, []);

  return {
    atual: estado.atual,
    definir,
    substituir,
    desfazer,
    refazer,
    podeDesfazer: estado.passado.length > 0,
    podeRefazer: estado.futuro.length > 0,
  };
}
