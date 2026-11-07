import { useCallback, useEffect, useState } from "react";

export type Tema = "auto" | "claro" | "escuro";
const CHAVE = "rifas.tema";

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
