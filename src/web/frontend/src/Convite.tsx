import { useEffect, useState } from "react";
import { useI18n } from "./i18n";
import { Ligacao } from "./rota";

// Um convite discreto para deixar um comentário, DEPOIS de a pessoa descarregar as suas rifas: aparece no máximo UMA vez por aparelho (a marca fica no armazenamento
// local), não tapa nada (não é uma janela: é um aviso de estado, `role="status"`) e dispensa-se com «Agora não». Sem armazenamento local não se mostra (para não repetir).

const CHAVE = "rifas.convite";

/** Se já se convidou neste aparelho (ou não há como saber: então não se convida). */
export function jaConvidou(): boolean {
  try {
    return localStorage.getItem(CHAVE) !== null;
  } catch {
    return true;
  }
}

export function ConviteComentario() {
  const { t } = useI18n();
  const [aberto, setAberto] = useState(true);

  useEffect(() => {
    try {
      localStorage.setItem(CHAVE, "1");
    } catch {
      /* sem armazenamento */
    }
  }, []);

  if (!aberto) return null;
  return (
    <div className="convite" role="status" data-testid="convite-comentario">
      <p>{t("web_convite_texto")}</p>
      <div className="botoes">
        <Ligacao para="/opiniao" className="botao secundario" data-testid="convite-abrir">
          {t("web_convite_botao")}
        </Ligacao>
        <button type="button" className="texto" onClick={() => setAberto(false)} data-testid="convite-depois">
          {t("web_convite_depois")}
        </button>
      </div>
    </div>
  );
}
