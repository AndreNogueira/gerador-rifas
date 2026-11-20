import { useEffect, useRef, useSyncExternalStore } from "react";
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
 * As páginas de ferramenta que só levam os anúncios **laterais** (ecrãs largos), nunca o bloco do fim da página: o preçário tem os botões de descarregar
 * logo ao fim (a Google proíbe anúncios junto deles), por isso em ecrãs estreitos não há anúncio nenhum. Os laterais são fixos e ficam fora do conteúdo:
 * **nunca dentro da pré-visualização** (nem do PDF, que é gerado no servidor sem nada de publicidade).
 */
export const PAGINAS_SO_LATERAIS: readonly string[] = ["/precario"];

/**
 * Há espaço para os anúncios laterais? O conteúdo tem no mínimo 1280 px (`--largura-max`) e cada lateral pede 160 px + 16 px de folga:
 * a partir de 1640 px de largura sobra essa margem de cada lado. Em altura, o anúncio vertical tem 600 px e começa a 290 px do topo (por baixo da faixa do cabeçalho).
 */
export const CONSULTA_LATERAIS = "(min-width: 1640px) and (min-height: 930px)";

function useLaterais(): boolean {
  const subscrever = (aviso: () => void) => {
    if (typeof window === "undefined" || !window.matchMedia) return () => undefined;
    const m = window.matchMedia(CONSULTA_LATERAIS);
    m.addEventListener("change", aviso);
    return () => m.removeEventListener("change", aviso);
  };
  return useSyncExternalStore(
    subscrever,
    () => !!window.matchMedia?.(CONSULTA_LATERAIS).matches,
    () => false,
  );
}

function Bloco({
  publico,
  classe,
  formato,
}: {
  publico: Publico;
  classe: string;
  formato: "auto" | "vertical";
}) {
  const { t } = useI18n();
  const ins = useRef<HTMLModElement>(null);
  useEffect(() => {
    if (!ins.current || ins.current.dataset.adsbygoogleStatus) return;
    try {
      window.adsbygoogle = window.adsbygoogle ?? [];
      window.adsbygoogle.push({});
    } catch {
      // o script da Google não carregou (bloqueador de anúncios, sem rede): a página fica como estava
    }
  }, []);
  return (
    <aside className={classe} aria-label={t("web_publicidade")} data-testid="anuncio">
      <span className="anuncio-rotulo">{t("web_publicidade")}</span>
      <ins
        ref={ins}
        className="adsbygoogle"
        data-ad-client={publico.anuncios_cliente}
        data-ad-slot={publico.anuncios_slot}
        data-ad-format={formato}
        data-full-width-responsive={formato === "auto" ? "true" : "false"}
      />
    </aside>
  );
}

/**
 * Anúncios da Google (AdSense), ou nada. Só aparecem se o dono configurou o identificador e o bloco (`/api/publico`); o script da Google vem
 * no `<head>` que o servidor monta (`seo.cabecalho`). Em ecrãs largos ficam **nas laterais** (um de cada lado do conteúdo, fixos, sem mexer na
 * estrutura da página); onde não há margem, um bloco no fim da página, por cima do rodapé. Reservam sempre o mesmo espaço (não há saltos)
 * e somem se a Google não tiver anúncio. Ver `docs/ADSENSE.md`.
 */
export function Anuncio({ publico, caminho }: { publico: Publico; caminho: string }) {
  const laterais = useLaterais();
  const soLaterais = PAGINAS_SO_LATERAIS.includes(caminho);
  const ativo =
    !!publico.anuncios_cliente &&
    !!publico.anuncios_slot &&
    (PAGINAS_COM_ANUNCIO.includes(caminho) || soLaterais);
  if (!ativo || (soLaterais && !laterais)) return null;
  if (laterais) {
    return (
      <>
        <Bloco publico={publico} classe="anuncio anuncio-lateral esquerda" formato="vertical" />
        <Bloco publico={publico} classe="anuncio anuncio-lateral direita" formato="vertical" />
      </>
    );
  }
  return <Bloco publico={publico} classe="anuncio" formato="auto" />;
}
