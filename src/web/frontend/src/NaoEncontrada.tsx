import { useI18n } from "./i18n";
import { Voltar } from "./paginas";

/**
 * 404 a sério: qualquer URL que não seja uma página conhecida nem a inicial cai aqui (nunca silenciosamente no
 * gerador). O servidor já envia este pedido com o estado HTTP 404 e o `<head>` de `seo.pagina_nao_encontrada()`
 * (que agora também está traduzido); isto é só o que o React mostra depois de arrancar, na língua da interface.
 */
export function NaoEncontrada() {
  const { t } = useI18n();
  return (
    <div className="pagina">
      <section className="cartao texto-pagina" data-testid="pagina-404">
        <h1>{t("web_404_titulo")}</h1>
        <p>{t("web_404_texto")}</p>
        <Voltar />
      </section>
    </div>
  );
}
