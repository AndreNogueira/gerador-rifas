import { useEffect, useState } from "react";
import { api } from "./api";
import { Cabecalho } from "./Cabecalho";
import { ProvedorDialogos } from "./dialogos";
import { useFormulario } from "./formulario";
import { Gerador } from "./Gerador";
import { Sobre, Tutorial, Video } from "./paginas";
import { useLocalizacao } from "./rota";
import { ProvedorSessao, useSessao } from "./sessao";
import { useTema } from "./tema";

function Aplicacao() {
  const [tema, mudarTema] = useTema();
  const [versao, setVersao] = useState("");
  const caminho = useLocalizacao().split("?")[0];
  const { sessao } = useSessao();
  // o formulário vive aqui para não se perder ao ir ao tutorial e voltar
  const formulario = useFormulario(sessao);

  useEffect(() => {
    api
      .saude()
      .then((s) => setVersao(s.versao))
      .catch(() => setVersao(""));
  }, []);

  return (
    <>
      <Cabecalho tema={tema} mudarTema={mudarTema} />
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
