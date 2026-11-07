import { useCallback, useEffect, useState } from "react";
import { definirVisual } from "./api";
import { VISUAL_POR_OMISSAO, type Visual, visualValido } from "./temas";

/** Claro/escuro (`data-tema`) e, separado, o tema visual (`data-visual`): cada tema visual tem as duas versões. */
export type Tema = "auto" | "claro" | "escuro";
const CHAVE = "rifas.tema";
const CHAVE_VISUAL = "rifas.visual";

function lido(): Tema {
  try {
    const v = localStorage.getItem(CHAVE);
    return v === "claro" || v === "escuro" ? v : "auto";
  } catch {
    return "auto";
  }
}

export function aplicarTema(tema: Tema): void {
  const raiz = document.documentElement;
  if (tema === "auto")
    raiz.removeAttribute("data-tema"); // segue o sistema (prefers-color-scheme)
  else raiz.setAttribute("data-tema", tema === "claro" ? "light" : "dark");
}

export function useTema(): [Tema, (t: Tema) => void] {
  const [tema, setTema] = useState<Tema>(lido);
  useEffect(() => aplicarTema(tema), [tema]);
  const mudar = useCallback((t: Tema) => {
    setTema(t);
    try {
      if (t === "auto") localStorage.removeItem(CHAVE);
      else localStorage.setItem(CHAVE, t);
    } catch {
      /* sem armazenamento */
    }
  }, []);
  return [tema, mudar];
}

function visualLido(): Visual {
  try {
    const v = localStorage.getItem(CHAVE_VISUAL);
    return visualValido(v) ? v : VISUAL_POR_OMISSAO;
  } catch {
    return VISUAL_POR_OMISSAO;
  }
}

export function aplicarVisual(visual: Visual): void {
  document.documentElement.setAttribute("data-visual", visual);
  definirVisual(visual);
}

export function useVisual(): [Visual, (v: Visual) => void] {
  const [visual, setVisual] = useState<Visual>(visualLido);
  useEffect(() => aplicarVisual(visual), [visual]);
  const mudar = useCallback((v: Visual) => {
    setVisual(v);
    try {
      if (v === VISUAL_POR_OMISSAO) localStorage.removeItem(CHAVE_VISUAL);
      else localStorage.setItem(CHAVE_VISUAL, v);
    } catch {
      /* sem armazenamento */
    }
  }, []);
  return [visual, mudar];
}
