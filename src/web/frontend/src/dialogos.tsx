import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useI18n } from "./i18n";

export type TipoAviso = "aviso" | "erro";

interface Aberto {
  tipo: TipoAviso | "confirmar";
  texto: string;
  rotulo?: string;
  resolver?: (confirmou: boolean) => void;
}

interface Contexto {
  /** Mostra uma mensagem (como a caixa de aviso/erro da app Windows). */
  aviso: (texto: string, tipo?: TipoAviso) => void;
  /** Pede confirmação; devolve true se o utilizador confirmou. */
  confirmar: (texto: string, rotulo: string) => Promise<boolean>;
}

const Dialogos = createContext<Contexto | null>(null);

export function ProvedorDialogos({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  const [aberto, setAberto] = useState<Aberto | null>(null);
  const el = useRef<HTMLDialogElement>(null);

  const aviso = useCallback((texto: string, tipo: TipoAviso = "aviso") => setAberto({ tipo, texto }), []);
  const confirmar = useCallback(
    (texto: string, rotulo: string) =>
      new Promise<boolean>((resolver) => setAberto({ tipo: "confirmar", texto, rotulo, resolver })),
    [],
  );

  useEffect(() => {
    const d = el.current;
    if (!d) return;
    if (aberto && !d.open) {
      if (typeof d.showModal === "function") d.showModal();
      else d.setAttribute("open", "");
    }
    if (!aberto && d.open) d.close?.();
  }, [aberto]);

  function fechar(confirmou: boolean) {
    aberto?.resolver?.(confirmou);
    setAberto(null);
  }

  const valor = useMemo(() => ({ aviso, confirmar }), [aviso, confirmar]);
  return (
    <Dialogos.Provider value={valor}>
      {children}
      <dialog
        ref={el}
        className={`dialogo ${aberto?.tipo ?? ""}`}
        data-testid="dialogo"
        aria-labelledby="dialogo-texto"
        onCancel={(e) => {
          e.preventDefault();
          fechar(false);
        }}
      >
        {aberto && (
          <>
            <p id="dialogo-texto" className="dialogo-texto" data-testid="dialogo-texto">
              {aberto.texto}
            </p>
            <div className="dialogo-botoes">
              {aberto.tipo === "confirmar" && (
                <button
                  type="button"
                  className="secundario"
                  onClick={() => fechar(false)}
                  data-testid="dialogo-cancelar"
                >
                  {t("cancelar")}
                </button>
              )}
              <button type="button" onClick={() => fechar(true)} data-testid="dialogo-ok">
                {aberto.tipo === "confirmar" ? aberto.rotulo : "OK"}
              </button>
            </div>
          </>
        )}
      </dialog>
    </Dialogos.Provider>
  );
}

export function useDialogos(): Contexto {
  const c = useContext(Dialogos);
  if (!c) throw new Error("useDialogos fora do ProvedorDialogos");
  return c;
}
