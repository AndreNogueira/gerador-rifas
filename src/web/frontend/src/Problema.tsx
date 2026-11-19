import { type FormEvent, useState } from "react";
import { api, ErroApi } from "./api";
import { useI18n } from "./i18n";
import { Icone } from "./icones";
import { Ligacao } from "./rota";

const MAX_RESUMO = 100;
const MAX_TEXTO = 4000;
const letras = (s: string) => [...s].filter((c) => /[\p{L}\p{N}]/u.test(c)).length;

/** A informação técnica que a pessoa aceita juntar: o navegador e o tamanho do ecrã e da janela (nunca o IP: nem o servidor o envia ao GitHub). */
export function informacaoTecnica(): string {
  const w = window;
  return `${navigator.userAgent} | ecrã ${w.screen.width}x${w.screen.height} | janela ${w.innerWidth}x${w.innerHeight}`.slice(
    0,
    590,
  );
}

/** A página de onde a pessoa veio (só o caminho, e só se for do próprio site). */
export function paginaDeOrigem(): string {
  try {
    const r = new URL(document.referrer);
    return r.origin === window.location.origin ? r.pathname.slice(0, 100) : "";
  } catch {
    return "";
  }
}

/**
 * «Reportar problema»: o resumo, o que aconteceu e (se quiser) como repetir. «Abrir» cria um *issue* no GitHub do projeto, sem conta.
 * `ativo` = o servidor tem o token do GitHub (`/api/publico` → `problemas`).
 */
export function ReportarProblema({ ativo }: { ativo: boolean }) {
  const { t } = useI18n();
  const [resumo, setResumo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [passos, setPassos] = useState("");
  const [tecnica, setTecnica] = useState(false);
  const [isco, setIsco] = useState("");
  const [a_enviar, setEnviar] = useState(false);
  const [numero, setNumero] = useState<number | null>(null);
  const [erro, setErro] = useState("");

  async function abrir(e: FormEvent) {
    e.preventDefault();
    if (letras(resumo) < 10 || letras(descricao) < 10) return setErro(t("web_bug_curto"));
    setEnviar(true);
    setErro("");
    try {
      const r = await api.reportarProblema({
        resumo,
        descricao,
        passos,
        tecnica: tecnica ? informacaoTecnica() : "",
        pagina: paginaDeOrigem(),
        site: isco,
      });
      setNumero(r.numero);
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : String(e));
    } finally {
      setEnviar(false);
    }
  }

  if (numero !== null)
    return (
      <div className="pagina">
        <section className="cartao opiniao" data-testid="problema-registado">
          <h1>{t("web_bug_titulo")}</h1>
          <p role="status">{t("web_bug_obrigado", { n: numero })}</p>
          <div className="botoes">
            <Ligacao para="/" className="botao secundario">
              {t("app_nome")}
            </Ligacao>
          </div>
        </section>
      </div>
    );

  return (
    <div className="pagina">
      <section className="cartao opiniao" data-testid="pagina-problema">
        <h1>{t("web_bug_titulo")}</h1>
        <p className="suave">{t("web_bug_intro")}</p>
        {!ativo && (
          <p role="note" className="aviso-opiniao" data-testid="problema-inativo">
            {t("web_bug_indisponivel")}
          </p>
        )}
        <form onSubmit={abrir} className="formulario-opiniao">
          <label>
            {t("web_bug_resumo")}
            <span className="campo-contado">
              <input
                value={resumo}
                maxLength={MAX_RESUMO}
                onChange={(e) => setResumo(e.target.value)}
                data-testid="problema-resumo"
                required
              />
              <span className="contagem" aria-hidden="true">
                {resumo.length}/{MAX_RESUMO}
              </span>
            </span>
          </label>
          <label>
            {t("web_bug_descricao")}
            <textarea
              rows={5}
              value={descricao}
              maxLength={MAX_TEXTO}
              onChange={(e) => setDescricao(e.target.value)}
              data-testid="problema-descricao"
              required
            />
          </label>
          <label>
            {t("web_bug_passos")}
            <textarea
              rows={3}
              value={passos}
              maxLength={MAX_TEXTO}
              onChange={(e) => setPassos(e.target.value)}
              data-testid="problema-passos"
            />
          </label>
          <label className="opcao">
            <input
              type="checkbox"
              checked={tecnica}
              onChange={(e) => setTecnica(e.target.checked)}
              data-testid="problema-tecnica"
            />
            {t("web_bug_tecnica")}
          </label>
          <div className="isco" aria-hidden="true">
            <label>
              Site
              <input
                value={isco}
                onChange={(e) => setIsco(e.target.value)}
                tabIndex={-1}
                autoComplete="off"
              />
            </label>
          </div>
          <p className="suave aviso-ip">{t("web_bug_aviso")}</p>
          {erro && (
            <p role="alert" className="cor-erro" data-testid="problema-erro">
              {erro}
            </p>
          )}
          <div className="botoes">
            <button type="submit" disabled={a_enviar || !ativo} data-testid="problema-abrir">
              <Icone nome="bug" />
              {t("web_bug_abrir")}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
