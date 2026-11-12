import { useEffect, useRef } from "react";
import type { Publico } from "./api";
import { useI18n } from "./i18n";

declare global {
  interface Window {
    adsbygoogle?: unknown[];
  }
}

/** As páginas com anúncio: a inicial e as de leitura. Nunca o editor, o vídeo, os textos legais, o painel nem a verificação de bilhetes. */
export const PAGINAS_COM_ANUNCIO: readonly string[] = ["/", "/tutorial", "/sobre", "/sorteio", "/changelog"];

/**
 * Um bloco de anúncios da Google (AdSense) no fim da página, por cima do rodapé, ou nada. Só aparece se o dono configurou o identificador
 * e o bloco (`/api/publico`); o script da Google vem no `<head>` que o servidor monta (`seo.cabecalho`). Reserva sempre a mesma altura
 * (não há saltos) e desaparece se a Google não tiver anúncio para mostrar. Ver `docs/ADSENSE.md`.
 */
export function Anuncio({ publico, caminho }: { publico: Publico; caminho: string }) {
  const { t } = useI18n();
  const ins = useRef<HTMLModElement>(null);
  const ativo =
    !!publico.anuncios_cliente && !!publico.anuncios_slot && PAGINAS_COM_ANUNCIO.includes(caminho);

  useEffect(() => {
    if (!ativo || !ins.current || ins.current.dataset.adsbygoogleStatus) return;
    try {
      window.adsbygoogle = window.adsbygoogle ?? [];
      window.adsbygoogle.push({});
    } catch {
      // o script da Google não carregou (bloqueador de anúncios, sem rede): a página fica como estava
    }
  }, [ativo]);

  if (!ativo) return null;
  return (
    <aside className="anuncio" aria-label={t("web_publicidade")} data-testid="anuncio">
      <span className="anuncio-rotulo">{t("web_publicidade")}</span>
      <ins
        ref={ins}
        className="adsbygoogle"
        data-ad-client={publico.anuncios_cliente}
        data-ad-slot={publico.anuncios_slot}
        data-ad-format="auto"
        data-full-width-responsive="true"
      />
    </aside>
  );
}
