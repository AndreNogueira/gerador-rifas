import { Suspense, useEffect, useState } from "react";
import { Anuncio } from "./Anuncio";
import { api, type Publico } from "./api";
import { Cabecalho } from "./Cabecalho";
import { Changelog } from "./Changelog";
import { Comentarios, DeixarComentario } from "./Comentarios";
import { iniciarDesempenho } from "./desempenho";
import { ProvedorDialogos } from "./dialogos";
import { registarEcra } from "./ecra";
import { useFormulario } from "./formulario";
import { Gerador } from "./Gerador";
import { GUIAS, Guia } from "./Guia";
import { IndiceGuias } from "./IndiceGuias";
import { useI18n } from "./i18n";
import { NaoEncontrada } from "./NaoEncontrada";
import { PaginaTexto } from "./PaginaTexto";
import { ReportarProblema } from "./Problema";
import { Sobre, Tutorial, Video } from "./paginas";
import { preguicoso } from "./preguicoso";
import { registarServiceWorker } from "./pwa";
import { Ligacao, useLocalizacao } from "./rota";
import { ProvedorSessao, useSessao } from "./sessao";
import { useTema, useVisual } from "./tema";

// carregam-se à parte, só quando se abre a página (ver `preguicoso.ts`): o painel do dono, o editor de templates e o sorteio
const Admin = preguicoso(() => import("./Admin").then((m) => ({ default: m.Admin })));
const Editor = preguicoso(() => import("./Editor").then((m) => ({ default: m.Editor })));
const Sorteio = preguicoso(() => import("./Sorteio").then((m) => ({ default: m.Sorteio })));
const Precario = preguicoso(() => import("./Precario").then((m) => ({ default: m.Precario })));

/** Páginas com título fixo: «Changelog» é um nome e o painel é só em português. Os Termos, a Privacidade e o Contacto põem o título que o servidor
 * entrega, já na língua escolhida (ver PaginaTexto). */
const TITULOS_PT: Record<string, string> = {
  "/changelog": "Changelog",
  "/admin": "Painel",
};

/** Os caminhos que têm página própria (fora dos guias, em `GUIAS`): o mesmo conjunto do `switch` abaixo. Um caminho
 * fora daqui (e que não seja "/") é um 404 a sério, nunca o gerador silenciosamente. */
const PATHS_CONHECIDOS = [
  "/tutorial",
  "/video",
  "/sobre",
  "/sorteio",
  "/precario",
  "/editor",
  "/como-fazer",
  "/comentarios",
  "/opiniao",
  "/reportar-problema",
  "/changelog",
  "/termos",
  "/privacidade",
  "/contacto",
  "/admin",
];

function Aplicacao() {
  const [tema, mudarTema] = useTema();
  const [visual, mudarVisual] = useVisual();
  const [versao, setVersao] = useState("");
  const [publico, setPublico] = useState<Publico>({
    donativo_url: "",
    contacto: false,
    qr: false,
    anuncios_cliente: "",
    anuncios_slot: "",
    partilha_editor: false,
    problemas: false,
  });
  const caminho = useLocalizacao().split("?")[0] ?? "/";
  const { sessao } = useSessao();
  const { t } = useI18n();
  // o formulário vive aqui para não se perder ao ir ao tutorial e voltar
  const formulario = useFormulario(sessao);

  // o título do separador acompanha a página e a língua (o servidor já entrega o certo em português para quem não corre JS)
  useEffect(() => {
    const nome = t("app_nome");
    const traduzidas: Record<string, string> = {
      "/tutorial": t("tut_titulo"),
      "/video": t("mi_video"),
      "/sobre": t("mi_sobre"),
      "/sorteio": t("web_sorteio"),
      "/editor": t("web_editor"),
      "/como-fazer": t("web_comofazer_titulo"),
      "/precario": t("web_precario_titulo"),
      "/comentarios": t("web_comentarios"),
      "/opiniao": t("web_op_titulo"),
      "/reportar-problema": t("web_bug_titulo"),
    };
    const pagina = traduzidas[caminho] ?? TITULOS_PT[caminho] ?? "";
    const conhecido = caminho === "/" || PATHS_CONHECIDOS.includes(caminho) || !!GUIAS[caminho];
    document.title = pagina
      ? `${pagina.replace(/…$/, "")} | ${nome}`
      : conhecido
        ? nome
        : `${t("web_404_titulo")} | ${nome}`;
  }, [caminho, t]);

  // o tipo de ecra, para as estatisticas (uma vez por separador; o painel do dono nao conta)
  useEffect(() => {
    if (window.location.pathname === "/admin") return;
    void registarEcra();
    iniciarDesempenho();
  }, []);

  useEffect(() => {
    api
      .saude()
      .then((s) => {
        setVersao(s.versao);
        void registarServiceWorker(s.versao);
      })
      .catch(() => setVersao(""));
    api
      .publico()
      .then(setPublico)
      .catch(() => undefined); // sem isto o rodapé só não mostra o donativo e o contacto
  }, []);

  return (
    <>
      <Cabecalho
        tema={tema}
        mudarTema={mudarTema}
        visual={visual}
        mudarVisual={mudarVisual}
        donativoUrl={publico.donativo_url}
      />
      <main className="conteudo">
        <Suspense fallback={<p aria-busy="true">…</p>}>
          {caminho === "/tutorial" ? (
            <Tutorial />
          ) : caminho === "/video" ? (
            <Video />
          ) : caminho === "/sobre" ? (
            <Sobre versao={versao} />
          ) : caminho === "/sorteio" ? (
            <Sorteio />
          ) : caminho === "/precario" ? (
            <Precario partilha={publico.partilha_editor} />
          ) : caminho === "/editor" ? (
            <Editor partilha={publico.partilha_editor} />
          ) : caminho === "/como-fazer" ? (
            <IndiceGuias />
          ) : GUIAS[caminho] ? (
            <Guia nome={GUIAS[caminho]} />
          ) : caminho === "/comentarios" ? (
            <Comentarios />
          ) : caminho === "/opiniao" ? (
            <DeixarComentario />
          ) : caminho === "/reportar-problema" ? (
            <ReportarProblema ativo={publico.problemas} />
          ) : caminho === "/changelog" ? (
            <Changelog />
          ) : caminho === "/termos" || caminho === "/privacidade" || caminho === "/contacto" ? (
            <PaginaTexto nome={caminho.slice(1)} />
          ) : caminho === "/admin" ? (
            <Admin />
          ) : caminho === "/" ? (
            <Gerador {...formulario} donativoUrl={publico.donativo_url} />
          ) : (
            <NaoEncontrada />
          )}
        </Suspense>
      </main>
      <Anuncio key={caminho} publico={publico} caminho={caminho} />
      {versao && (
        <footer className="rodape">
          <span>v{versao}</span>
          <nav aria-label="Informação">
            <Ligacao para="/comentarios">{t("web_comentarios")}</Ligacao>
            <Ligacao para="/opiniao">{t("web_com_escrever")}</Ligacao>
            <Ligacao para="/reportar-problema">{t("web_reportar")}</Ligacao>
            <Ligacao para="/changelog">Changelog</Ligacao>
            <Ligacao para="/termos">{t("web_termos")}</Ligacao>
            <Ligacao para="/privacidade">{t("web_privacidade")}</Ligacao>
            {publico.contacto && <Ligacao para="/contacto">{t("web_contacto")}</Ligacao>}
            {publico.donativo_url && (
              <a href={publico.donativo_url} target="_blank" rel="noopener noreferrer" data-testid="donativo">
                {t("web_donativo")}
              </a>
            )}
          </nav>
        </footer>
      )}
    </>
  );
}

export function App() {
  return (
    <ProvedorDialogos>
      <ProvedorSessao>
        <Aplicacao />
      </ProvedorSessao>
    </ProvedorDialogos>
  );
}
