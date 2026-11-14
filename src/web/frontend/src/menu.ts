import { type CSSProperties, useCallback, useEffect, useRef, useState } from "react";

const LARGURA_PAINEL = 280; // px: a mesma do CSS (`.painel-flutuante`)
const FOLGA = 8;

/**
 * Um painel que abre por baixo de um botão do cabeçalho («Como fazer», «Partilhar»). Fica em `position: fixed` com a posição calculada ao abrir:
 * assim não o cortam as faixas que deslizam na horizontal nem o cabeçalho em ecrãs estreitos. Fecha com Esc, ao tocar fora, ao rolar ou ao redimensionar.
 */
export function useMenuFlutuante(alinhar: "esq" | "dir") {
  const [aberto, setAberto] = useState(false);
  const [estilo, setEstilo] = useState<CSSProperties>({});
  const refBotao = useRef<HTMLButtonElement>(null);
  const refPainel = useRef<HTMLUListElement>(null);

  const fechar = useCallback(() => setAberto(false), []);
  const alternar = useCallback(() => {
    setAberto((a) => {
      if (!a && refBotao.current) {
        const r = refBotao.current.getBoundingClientRect();
        const largura = Math.min(LARGURA_PAINEL, window.innerWidth - 2 * FOLGA);
        const esquerda = alinhar === "dir" ? r.right - largura : r.left;
        setEstilo({
          top: r.bottom + FOLGA,
          left: Math.max(FOLGA, Math.min(esquerda, window.innerWidth - largura - FOLGA)),
          width: largura,
        });
      }
      return !a;
    });
  }, [alinhar]);

  useEffect(() => {
    if (!aberto) return;
    const tecla = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      setAberto(false);
      refBotao.current?.focus();
    };
    const fora = (e: PointerEvent) => {
      const alvo = e.target as Node;
      if (!refPainel.current?.contains(alvo) && !refBotao.current?.contains(alvo)) setAberto(false);
    };
    const fecha = () => setAberto(false);
    document.addEventListener("keydown", tecla);
    document.addEventListener("pointerdown", fora);
    window.addEventListener("scroll", fecha, { passive: true });
    window.addEventListener("resize", fecha);
    return () => {
      document.removeEventListener("keydown", tecla);
      document.removeEventListener("pointerdown", fora);
      window.removeEventListener("scroll", fecha);
      window.removeEventListener("resize", fecha);
    };
  }, [aberto]);

  return { aberto, fechar, alternar, estilo, refBotao, refPainel };
}
