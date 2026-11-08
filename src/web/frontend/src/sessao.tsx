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
import { api, type Campos, ErroApi, ErroRede, type Sessao } from "./api";
import { useDialogos } from "./dialogos";
import { useI18n } from "./i18n";
import { esquecerAlgarismos, guardarAlgarismos, lerAlgarismos } from "./memoria";

export type Ocupado = "template" | "algarismos" | "previa" | "gerar" | null;
const CHAVE = "rifas.sessao";
const A_CORRER = ["a_gerar", "a_cancelar"];
const INTERVALO_MS = 500;

export const aCorrer = (s: Sessao | null): boolean => !!s && A_CORRER.includes(s.trabalho.estado);

interface Contexto {
  sessao: Sessao | null;
  /** O registo da geração (linhas já traduzidas, em ordem). */
  registo: string[];
  /** Que pedido está em curso (para mostrar «a analisar…» e desativar botões). */
  ocupado: Ocupado;
  carregarTemplate: (f: File) => Promise<void>;
  carregarAlgarismos: (f: File) => Promise<void>;
  pedirPrevia: (c: Campos) => Promise<void>;
  /** `confirmacao`: texto a confirmar antes de gerar (muitas rifas por folha); vazio = não pergunta. */
  pedirGerar: (c: Campos, confirmacao: string) => Promise<void>;
  cancelar: () => Promise<void>;
  /** O nome do ficheiro dos algarismos reutilizado da última vez nesta sessão ("" se não houve). */
  algarismosLembrados: string;
  /** «Limpar tudo»: apaga os ficheiros no servidor e começa uma sessão nova. */
  limpar: () => Promise<void>;
}

const Ctx = createContext<Contexto | null>(null);

function guardado(): string | null {
  try {
    return localStorage.getItem(CHAVE);
  } catch {
    return null;
  }
}
function guardar(id: string | null): void {
  try {
    if (id) localStorage.setItem(CHAVE, id);
    else localStorage.removeItem(CHAVE);
  } catch {
    /* sem armazenamento */
  }
}

export function ProvedorSessao({ children }: { children: ReactNode }) {
  const { t, lingua } = useI18n();
  const { aviso, confirmar } = useDialogos();
  const [sessao, setSessao] = useState<Sessao | null>(null);
  const [registo, setRegisto] = useState<string[]>([]);
  const [ocupado, setOcupado] = useState<Ocupado>(null);
  const id = useRef<string | null>(null);
  const desde = useRef(0);
  const iniciou = useRef(false);
  const [lembrado, setLembrado] = useState<{ sessao: string; nome: string } | null>(null);
  const tentouLembrar = useRef(new Set<string>());

  /** Troca o estado pelo que o servidor devolveu (com o registo completo, no idioma do pedido). */
  const aplicar = useCallback((s: Sessao) => {
    id.current = s.sessao;
    guardar(s.sessao);
    desde.current = s.trabalho.proximo;
    setSessao(s);
    setRegisto(s.trabalho.registo);
  }, []);

  const novaSessao = useCallback(async () => aplicar(await api.criarSessao()), [aplicar]);

  const falhar = useCallback(
    async (e: unknown) => {
      if (e instanceof ErroApi && e.estado === 404) {
        // o servidor perdeu a sessão (reiniciou, adormeceu ou apagou-a por inatividade): recomeça-se do zero
        try {
          await novaSessao();
          aviso(t("web_sessao_expirada"), "aviso");
        } catch (e2) {
          aviso(e2 instanceof ErroApi ? e2.message : t("web_erro_rede"), "erro");
        }
      } else if (e instanceof ErroApi) aviso(e.message, e.tipo);
      else if (e instanceof ErroRede) aviso(t("web_erro_rede"), "erro");
      else aviso(String(e), "erro");
    },
    [aviso, novaSessao, t],
  );

  // ---- arranque: retoma a sessão guardada (se o servidor ainda a tem) ou cria uma
  useEffect(() => {
    if (iniciou.current) return;
    iniciou.current = true;
    (async () => {
      const anterior = guardado();
      try {
        if (anterior) {
          try {
            aplicar(await api.sessao(anterior));
            return;
          } catch (e) {
            if (!(e instanceof ErroApi && e.estado === 404)) throw e;
            await novaSessao();
            aviso(t("web_sessao_expirada"), "aviso");
            return;
          }
        }
        await novaSessao();
      } catch (e) {
        await falhar(e);
      }
    })();
  }, [aplicar, aviso, falhar, novaSessao, t]);

  // ---- mudou a língua: pede de novo o estado (os textos vêm traduzidos do servidor)
  useEffect(() => {
    if (!id.current || !lingua) return; // a língua mudou (ou é a 1.ª): os textos vêm traduzidos do servidor
    api.sessao(id.current).then(aplicar).catch(falhar);
  }, [lingua, aplicar, falhar]);

  // ---- a gerar: consulta o progresso de meio em meio segundo
  const idSessao = sessao?.sessao;
  const rodando = aCorrer(sessao);
  useEffect(() => {
    if (!rodando || !idSessao) return;
    let ativo = true;
    let falhas = 0;
    let temporizador: ReturnType<typeof setTimeout>;
    const volta = async () => {
      if (!ativo) return;
      try {
        const tr = await api.trabalho(idSessao, desde.current);
        falhas = 0;
        if (!ativo) return;
        desde.current = tr.proximo;
        if (tr.registo.length) setRegisto((r) => [...r, ...tr.registo]);
        setSessao((s) => (s && s.sessao === idSessao ? { ...s, trabalho: tr } : s));
        if (tr.estado === "falhou" && tr.erro) aviso(tr.erro, "erro");
        if (!A_CORRER.includes(tr.estado)) return;
      } catch (e) {
        if (e instanceof ErroApi && e.estado === 404) {
          await falhar(e);
          return;
        }
        if (++falhas > 20) return; // 10 s sem resposta: pára de insistir (o utilizador vê o estado parado)
      }
      if (ativo) temporizador = setTimeout(volta, INTERVALO_MS);
    };
    temporizador = setTimeout(volta, 300);
    return () => {
      ativo = false;
      clearTimeout(temporizador);
    };
  }, [rodando, idSessao, aviso, falhar]);

  // ---- ações
  const executar = useCallback(
    async (que: Exclude<Ocupado, null>, pedido: () => Promise<Sessao>, depois?: (s: Sessao) => void) => {
      setOcupado(que);
      try {
        const s = await pedido();
        aplicar(s);
        depois?.(s);
      } catch (e) {
        await falhar(e);
      } finally {
        setOcupado(null);
      }
    },
    [aplicar, falhar],
  );

  const mostrarErrosDeFicheiros = useCallback(
    (s: Sessao) => {
      if (s.template.estado === "erro") aviso(s.template.detalhe || s.template.texto, "erro");
      else if (s.algarismos.estado === "erro") aviso(s.algarismos.detalhe || s.algarismos.texto, "erro");
    },
    [aviso],
  );

  // ---- já há template mas faltam os algarismos: reutiliza os da última vez (guardados só neste browser), uma vez por sessão
  useEffect(() => {
    if (!sessao || ocupado !== null || sessao.algarismos.estado !== "precisa") return;
    const sid = sessao.sessao;
    if (tentouLembrar.current.has(sid)) return;
    tentouLembrar.current.add(sid);
    void lerAlgarismos().then((f) => {
      if (!f || id.current !== sid) return;
      void executar(
        "algarismos",
        () => api.algarismos(sid, f),
        (s) => {
          if (s.algarismos.estado === "ok") setLembrado({ sessao: s.sessao, nome: f.name });
          else void esquecerAlgarismos(); // já não serve (ficheiro estragado): não insiste
        },
      );
    });
  }, [sessao, ocupado, executar]);

  const valor = useMemo<Contexto>(
    () => ({
      sessao,
      registo,
      ocupado,
      algarismosLembrados: lembrado && lembrado.sessao === sessao?.sessao ? lembrado.nome : "",
      carregarTemplate: (f) =>
        id.current
          ? executar("template", () => api.template(id.current as string, f), mostrarErrosDeFicheiros)
          : Promise.resolve(),
      carregarAlgarismos: (f) =>
        id.current
          ? executar(
              "algarismos",
              () => api.algarismos(id.current as string, f),
              (s) => {
                mostrarErrosDeFicheiros(s);
                setLembrado(null);
                if (s.algarismos.estado === "ok") void guardarAlgarismos(f); // para a próxima vez
              },
            )
          : Promise.resolve(),
      pedirPrevia: (c) =>
        id.current ? executar("previa", () => api.previa(id.current as string, c)) : Promise.resolve(),
      pedirGerar: async (c, confirmacao) => {
        if (!id.current) return;
        if (confirmacao && !(await confirmar(confirmacao, t("gerar")))) return;
        await executar("gerar", () => api.gerar(id.current as string, c));
      },
      cancelar: async () => {
        if (!id.current) return;
        try {
          const tr = await api.cancelar(id.current);
          setSessao((s) => (s ? { ...s, trabalho: tr } : s));
        } catch (e) {
          await falhar(e);
        }
      },
      limpar: async () => {
        const antigo = id.current;
        try {
          if (antigo) await api.apagarSessao(antigo);
          guardar(null);
          await esquecerAlgarismos(); // «Limpar tudo» apaga também o que ficou neste browser
          setLembrado(null);
          await novaSessao();
        } catch (e) {
          await falhar(e);
        }
      },
    }),
    [sessao, registo, ocupado, lembrado, executar, mostrarErrosDeFicheiros, confirmar, t, falhar, novaSessao],
  );

  return <Ctx.Provider value={valor}>{children}</Ctx.Provider>;
}

export function useSessao(): Contexto {
  const c = useContext(Ctx);
  if (!c) throw new Error("useSessao fora do ProvedorSessao");
  return c;
}
