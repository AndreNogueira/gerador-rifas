import { useEffect, useState } from "react";
import { api } from "./api";
import { Cabecalho } from "./Cabecalho";
import { ProvedorDialogos } from "./dialogos";
import { useFormulario } from "./formulario";
import { Gerador } from "./Gerador";
import { useI18n } from "./i18n";
import { Sobre, Tutorial, Video } from "./paginas";
import { useLocalizacao } from "./rota";
import { ProvedorSessao, useSessao } from "./sessao";
import { useTema, useVisual } from "./tema";

function Aplicacao() {
  const [tema, mudarTema] = useTema();
  const [visual, mudarVisual] = useVisual();
  const [versao, setVersao] = useState("");
  const caminho = useLocalizacao().split("?")[0];
  const { sessao } = useSessao();
  const { t } = useI18n();
  // o formulário vive aqui para não se perder ao ir ao tutorial e voltar
  const formulario = useFormulario(sessao);

  // o título do separador acompanha a página e a língua (o servidor já entrega o certo em português para quem não corre JS)
  useEffect(() => {
    const nome = t("app_nome");
    const pagina =
      caminho === "/tutorial"
        ? t("tut_titulo")
        : caminho === "/video"
          ? t("mi_video")
          : caminho === "/sobre"
            ? t("mi_sobre")
            : "";
    document.title = pagina ? `${pagina.replace(/…$/, "")} | ${nome}` : nome;
  }, [caminho, t]);

  useEffect(() => {
    api
      .saude()
      .then((s) => setVersao(s.versao))
      .catch(() => setVersao(""));
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
        ) : (
          <Gerador {...formulario} />
        )}
      </main>
      {versao && <footer className="rodape">v{versao}</footer>}
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
