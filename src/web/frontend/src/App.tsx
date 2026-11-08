import { useEffect, useState } from "react";
import { Admin } from "./Admin";
import { api, type Publico } from "./api";
import { Cabecalho } from "./Cabecalho";
import { Changelog } from "./Changelog";
import { ProvedorDialogos } from "./dialogos";
import { registarEcra } from "./ecra";
import { useFormulario } from "./formulario";
import { Gerador } from "./Gerador";
import { useI18n } from "./i18n";
import { PaginaTexto } from "./PaginaTexto";
import { Sobre, Tutorial, Video } from "./paginas";
import { registarServiceWorker } from "./pwa";
import { Ligacao, useLocalizacao } from "./rota";
import { Sorteio } from "./Sorteio";
import { ProvedorSessao, useSessao } from "./sessao";
import { useTema, useVisual } from "./tema";

/** Páginas com título fixo: «Changelog» é um nome e o painel é só em português. Os Termos, a Privacidade e o Contacto põem o título que o servidor
 * entrega, já na língua escolhida (ver PaginaTexto). */
const TITULOS_PT: Record<string, string> = {
  "/changelog": "Changelog",
  "/admin": "Painel",
};

function Aplicacao() {
  const [tema, mudarTema] = useTema();
  const [visual, mudarVisual] = useVisual();
  const [versao, setVersao] = useState("");
  const [publico, setPublico] = useState<Publico>({ donativo_url: "", contacto: false, qr: false });
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
    };
    const pagina = traduzidas[caminho] ?? TITULOS_PT[caminho] ?? "";
    document.title = pagina ? `${pagina.replace(/…$/, "")} | ${nome}` : nome;
  }, [caminho, t]);

  // o tipo de ecra, para as estatisticas (uma vez por separador; o painel do dono nao conta)
  useEffect(() => {
    if (window.location.pathname !== "/admin") void registarEcra();
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
      <Cabecalho tema={tema} mudarTema={mudarTema} visual={visual} mudarVisual={mudarVisual} />
      <main className="conteudo">
        {caminho === "/tutorial" ? (
          <Tutorial />
        ) : caminho === "/video" ? (
          <Video />
        ) : caminho === "/sobre" ? (
          <Sobre versao={versao} />
        ) : caminho === "/sorteio" ? (
          <Sorteio />
        ) : caminho === "/changelog" ? (
          <Changelog />
        ) : caminho === "/termos" || caminho === "/privacidade" || caminho === "/contacto" ? (
          <PaginaTexto nome={caminho.slice(1)} />
        ) : caminho === "/admin" ? (
          <Admin />
        ) : (
          <Gerador {...formulario} />
        )}
      </main>
      {versao && (
        <footer className="rodape">
          <span>v{versao}</span>
          <nav aria-label="Informação">
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
