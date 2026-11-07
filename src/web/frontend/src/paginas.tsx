import { useEffect, useState } from "react";
import { api, ErroApi, type Tutorial as TutorialDados } from "./api";
import { useI18n } from "./i18n";
import { Icone } from "./icones";
import { Ligacao, navegar, useLocalizacao } from "./rota";

function useTutorial(): { dados: TutorialDados | null; erro: string } {
  const { lingua } = useI18n();
  const [dados, setDados] = useState<TutorialDados | null>(null);
  const [erro, setErro] = useState("");
  // biome-ignore lint/correctness/useExhaustiveDependencies: o tutorial pede-se de novo quando a língua muda
  useEffect(() => {
    let ativo = true;
    setErro("");
    api
      .tutorial()
      .then((d) => ativo && setDados(d))
      .catch((e: unknown) => ativo && setErro(e instanceof ErroApi ? e.message : String(e)));
    return () => {
      ativo = false;
    };
  }, [lingua]);
  return { dados, erro };
}

function Voltar() {
  const { t } = useI18n();
  return (
    <Ligacao para="/" className="botao secundario voltar">
      <Icone nome="esquerda" />
      {t("web_voltar")}
    </Ligacao>
  );
}

/** O tutorial passo a passo (os mesmos tópicos da app Windows), com «Anterior»/«Seguinte» e o tópico em `?p=`. */
export function Tutorial() {
  const { t } = useI18n();
  const localizacao = useLocalizacao();
  const { dados, erro } = useTutorial();
  const pedido = Number(new URLSearchParams(localizacao.split("?")[1] ?? "").get("p"));
  const topicos = dados?.topicos ?? [];
  const atual = topicos.length
    ? Math.min(Math.max(Number.isFinite(pedido) ? pedido : 0, 0), topicos.length - 1)
    : 0;
  const ir = (i: number) => navegar(`/tutorial?p=${i}`, true);
  const topico = topicos[atual];

  return (
    <div className="pagina">
      <h1>{t("tut_titulo")}</h1>
      {erro && <p role="alert">{erro}</p>}
      {!dados && !erro && <p aria-busy="true">…</p>}
      {topico && (
        <div className="tutorial">
          <nav className="topicos" aria-label={t("tut_titulo")} data-testid="topicos">
            {topicos.map((p, i) => (
              <button
                key={p.menu}
                type="button"
                className={`topico${i === atual ? " atual" : ""}`}
                aria-current={i === atual ? "page" : undefined}
                onClick={() => ir(i)}
                data-testid={`topico-${i}`}
              >
                {p.menu.trim()}
              </button>
            ))}
          </nav>
          <article className="cartao" data-testid="topico">
            <h2>{topico.titulo}</h2>
            <p className="texto-longo">{topico.texto}</p>
            {topico.imagens.map((img) => (
              <img
                key={img.url}
                src={img.url}
                alt={topico.titulo}
                loading="lazy"
                className="imagem-tutorial"
                style={img.largura ? { width: `min(100%, ${img.largura}px)` } : undefined}
              />
            ))}
            <div className="botoes">
              <button
                type="button"
                className="secundario"
                disabled={atual === 0}
                onClick={() => ir(atual - 1)}
              >
                <Icone nome="anterior" />
                {t("tut_ant")}
              </button>
              <button
                type="button"
                className="secundario"
                disabled={atual >= topicos.length - 1}
                onClick={() => ir(atual + 1)}
              >
                {t("tut_seg")}
                <Icone nome="seguinte" />
              </button>
              <span className="suave">
                {atual + 1} / {topicos.length}
              </span>
            </div>
          </article>
        </div>
      )}
      <Voltar />
    </div>
  );
}

/** O vídeo tutorial (há em português e inglês; para as outras línguas vale o que `core.tutorial.ficheiro_video` escolher, e se não houver diz-se que falta). */
export function Video() {
  const { t, lingua } = useI18n();
  const { dados, erro } = useTutorial();
  return (
    <div className="pagina">
      <h1>{t("mi_video")}</h1>
      {erro && <p role="alert">{erro}</p>}
      {!dados && !erro && <p aria-busy="true">…</p>}
      {dados &&
        (dados.video ? (
          <video className="video" src={dados.video} controls preload="metadata" data-testid="video">
            <track kind="captions" />
          </video>
        ) : (
          <p className="cor-erro" data-testid="video-falta">
            {t("video_falta", { nome: `tutorial_${lingua}.mp4` })}
          </p>
        ))}
      <Voltar />
    </div>
  );
}

/** «Acerca de»: o texto da app Windows, sem a linha das bibliotecas dela (aqui são outras). */
export function Sobre({ versao }: { versao: string }) {
  const { t } = useI18n();
  const texto = t("sobre_texto", { app: t("app_nome"), versao })
    .split("\n\n")
    .slice(0, 2)
    .join("\n\n");
  return (
    <div className="pagina">
      <section className="cartao sobre">
        <h1>{t("mi_sobre").replace(/…$/, "")}</h1>
        <p className="texto-longo" data-testid="sobre-texto">
          {texto}
        </p>
        <p className="suave">FastAPI · React · pypdf · pypdfium2 · Pillow</p>
        <Voltar />
      </section>
    </div>
  );
}
