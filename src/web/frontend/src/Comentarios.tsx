import { type FormEvent, useCallback, useEffect, useState } from "react";
import { api, type ComentarioPublico, ErroApi, type ListaComentarios } from "./api";
import { useI18n } from "./i18n";
import { Icone } from "./icones";
import { Voltar } from "./paginas";
import { Ligacao } from "./rota";

const MAX_TEXTO = 1000;
const MAX_NOME = 40;

/** Quem escreveu, como se mostra: o nome escolhido, «Anónimo(a)», ou «Visitante n.º …» (nunca mais do que isto: o servidor nem manda o resto). */
function Autor({ c }: { c: ComentarioPublico }) {
  const { t } = useI18n();
  if (c.nome) return <>{c.nome}</>;
  if (c.anonimo || !c.visitante) return <>{t("web_com_anonimo")}</>;
  return <>{t("web_com_visitante", { n: c.visitante })}</>;
}

/** A página «Comentários»: o que as pessoas escreveram, sem endereços IP, anónimos ou com o nome que cada uma escolheu. */
export function Comentarios() {
  const { t, lingua } = useI18n();
  const [dados, setDados] = useState<ListaComentarios | null>(null);
  const [itens, setItens] = useState<ComentarioPublico[]>([]);
  const [erro, setErro] = useState("");
  const [a_carregar, setCarregar] = useState(false);

  const carregar = useCallback(async (antes = "") => {
    setCarregar(true);
    try {
      const d = await api.comentarios(antes);
      setDados(d);
      setItens((atuais) => (antes ? [...atuais, ...d.itens] : d.itens));
      setErro("");
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : String(e));
    } finally {
      setCarregar(false);
    }
  }, []);

  useEffect(() => {
    void carregar();
  }, [carregar]);

  const dia = (segundos: number) =>
    new Date(segundos * 1000).toLocaleDateString(lingua === "pt" ? "pt-PT" : lingua, {
      day: "numeric",
      month: "short",
      year: "numeric",
    });

  return (
    <div className="pagina">
      <section className="cartao opiniao" data-testid="pagina-comentarios">
        <h1>{t("web_comentarios")}</h1>
        <p className="suave">{t("web_com_intro", { app: t("app_nome") })}</p>
        <div className="botoes">
          <Ligacao para="/opiniao" className="botao" data-testid="comentarios-escrever">
            <Icone nome="comentario" />
            {t("web_com_escrever")}
          </Ligacao>
          <Ligacao para="/reportar-problema" className="botao secundario">
            <Icone nome="bug" />
            {t("web_reportar")}
          </Ligacao>
        </div>
        {erro && <p role="alert">{erro}</p>}
        {!dados && !erro && <p aria-busy="true">…</p>}
        {dados && itens.length === 0 && <p data-testid="comentarios-vazio">{t("web_com_vazio")}</p>}
        <ul className="lista-comentarios" aria-label={t("web_comentarios")}>
          {itens.map((c) => (
            <li key={c.id} className="comentario" data-testid="comentario">
              <p className="comentario-autor">
                <strong>
                  <Autor c={c} />
                </strong>
                <time dateTime={new Date(c.criado * 1000).toISOString()}>{dia(c.criado)}</time>
              </p>
              <p className="texto-longo">{c.texto}</p>
            </li>
          ))}
        </ul>
        {dados?.seguinte && (
          <button
            type="button"
            className="secundario"
            disabled={a_carregar}
            onClick={() => void carregar(dados.seguinte)}
            data-testid="comentarios-mais"
          >
            {t("web_com_mais")}
          </button>
        )}
        <Voltar />
      </section>
    </div>
  );
}

const letras = (s: string) => [...s].filter((c) => /[\p{L}\p{N}]/u.test(c)).length;

/** A página «Deixar um comentário»: o texto e a escolha entre ficar anónimo(a) ou mostrar um nome (sem nome: «Visitante n.º …»). */
export function DeixarComentario() {
  const { t } = useI18n();
  const [texto, setTexto] = useState("");
  const [anonimo, setAnonimo] = useState(true);
  const [nome, setNome] = useState("");
  const [isco, setIsco] = useState("");
  const [a_enviar, setEnviar] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [erro, setErro] = useState("");

  async function enviar(e: FormEvent) {
    e.preventDefault();
    if (letras(texto) < 5) return setErro(t("web_op_curto"));
    setEnviar(true);
    setErro("");
    try {
      await api.comentar({ texto, anonimo, nome: anonimo ? "" : nome, site: isco });
      setEnviado(true);
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : String(e));
    } finally {
      setEnviar(false);
    }
  }

  if (enviado)
    return (
      <div className="pagina">
        <section className="cartao opiniao" data-testid="comentario-enviado">
          <h1>{t("web_op_titulo")}</h1>
          <p role="status">{t("web_op_obrigado")}</p>
          <div className="botoes">
            <Ligacao para="/comentarios" className="botao" data-testid="comentario-ver">
              {t("web_comentarios")}
            </Ligacao>
          </div>
        </section>
      </div>
    );

  return (
    <div className="pagina">
      <section className="cartao opiniao" data-testid="pagina-opiniao">
        <h1>{t("web_op_titulo")}</h1>
        <p className="suave">{t("web_op_intro", { app: t("app_nome") })}</p>
        <form onSubmit={enviar} className="formulario-opiniao">
          <label>
            {t("web_op_texto")}
            <span className="campo-contado">
              <textarea
                rows={6}
                value={texto}
                maxLength={MAX_TEXTO}
                onChange={(e) => setTexto(e.target.value)}
                data-testid="opiniao-texto"
                required
              />
              <span className="contagem" aria-hidden="true">
                {texto.length}/{MAX_TEXTO}
              </span>
            </span>
          </label>
          <fieldset className="escolha-nome">
            <legend className="so-leitores">{t("web_op_nome")}</legend>
            <label className="opcao">
              <input
                type="radio"
                name="anonimato"
                checked={anonimo}
                onChange={() => setAnonimo(true)}
                data-testid="opiniao-anonimo"
              />
              {t("web_op_anonimo")}
            </label>
            <label className="opcao">
              <input
                type="radio"
                name="anonimato"
                checked={!anonimo}
                onChange={() => setAnonimo(false)}
                data-testid="opiniao-com-nome"
              />
              {t("web_op_com_nome")}
            </label>
          </fieldset>
          {!anonimo && (
            <label>
              {t("web_op_nome")}
              <input
                value={nome}
                maxLength={MAX_NOME}
                onChange={(e) => setNome(e.target.value)}
                autoComplete="nickname"
                data-testid="opiniao-nome"
              />
              <span className="suave ajuda-campo">{t("web_op_nome_ajuda")}</span>
            </label>
          )}
          {/* o campo-isco: escondido das pessoas, os robôs preenchem-no e o servidor ignora-os */}
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
          <p className="suave aviso-ip">
            {t("web_op_aviso_ip")} <Ligacao para="/privacidade">{t("web_privacidade")}</Ligacao>
          </p>
          {erro && (
            <p role="alert" className="cor-erro" data-testid="opiniao-erro">
              {erro}
            </p>
          )}
          <div className="botoes">
            <button type="submit" disabled={a_enviar} data-testid="opiniao-enviar">
              {t("web_op_enviar")}
            </button>
            <Ligacao para="/comentarios" className="botao secundario">
              {t("web_comentarios")}
            </Ligacao>
          </div>
        </form>
      </section>
    </div>
  );
}
