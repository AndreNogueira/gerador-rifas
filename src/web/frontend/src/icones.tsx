import type { SVGProps } from "react";

/**
 * Os ícones da interface: desenhados à mão numa grelha de 24 px, traço de 2 px com pontas redondas.
 * São decorativos (`aria-hidden`): o texto ao lado diz o que o botão faz.
 */
const DESENHOS = {
  template: "M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8zM14 3v5h5M9 13h6M9 17h4",
  algarismos: "M5 9h14M5 15h14M10 4 8 20M16 4l-2 16",
  bilhete:
    "M3 7a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v3a2 2 0 0 0 0 4v3a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-3a2 2 0 0 0 0-4zM15 6v2M15 11v2M15 16v2",
  destino: "M12 4v11M7.5 11 12 15.5 16.5 11M5 19h14",
  carregar: "M12 16V5M7.5 9.5 12 5l4.5 4.5M5 19h14",
  olho: "M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
  faiscas:
    "M10 3l1.9 5.4L17.5 10l-5.6 1.6L10 17l-1.9-5.4L2.5 10l5.6-1.6zM18.5 14l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z",
  fechar: "M6 6l12 12M18 6 6 18",
  ligacao:
    "M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1",
  lixo: "M4 7h16M10 7V4h4v3M6 7l1 13h10l1-13M10 11v6M14 11v6",
  livro: "M12 6c-2-1.5-5-2-8-2v14c3 0 6 .5 8 2 2-1.5 5-2 8-2V4c-3 0-6 .5-8 2zM12 6v14",
  video: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM10 8.5v7l6-3.5z",
  info: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 11v5M12 8h.01",
  expandir: "M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5",
  reduzir: "M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5",
  calendario: "M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM4 10h16M8 3v4M16 3v4",
  coracao: "M12 20.5s-8-4.8-8-10.7A4.6 4.6 0 0 1 12 7a4.6 4.6 0 0 1 8 2.8c0 5.9-8 10.7-8 10.7z",
  externo: "M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5",
  paleta:
    "M12 3a9 9 0 1 0 0 18c1.1 0 1.8-.8 1.8-1.7 0-.5-.2-.8-.4-1.2-.3-.4-.4-.7-.4-1.1 0-.9.7-1.6 1.6-1.6H17a4 4 0 0 0 4-4C21 6.7 17 3 12 3zM7.5 12h.01M9.5 8h.01M14.5 8h.01",
  globo: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M12 3c3.2 3 3.2 15 0 18M12 3c-3.2 3-3.2 15 0 18",
  sol: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.4 1.4M17.6 17.6 19 19M19 5l-1.4 1.4M6.4 17.6 5 19",
  lua: "M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z",
  auto: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 3v18",
  esquerda: "M19 12H5M11 6l-6 6 6 6",
  anterior: "M15 6l-6 6 6 6",
  seguinte: "M9 6l6 6-6 6",
  verificado: "M5 12.5l4.5 4.5L19 7.5",
  descarregar: "M12 4v11M7.5 11 12 15.5 16.5 11M5 20h14",
  partilhar:
    "M18 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM6 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM18 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM8.6 13.5l6.8 4M15.4 6.5l-6.8 4",
  // as redes sociais e afins (traço, como o resto; só a forma que as identifica, sem logótipos oficiais)
  whatsapp:
    "M3 21l1.7-4.9A9 9 0 1 1 8 19.3zM9 8.8c.3 2.6 2.8 5.2 5.6 5.7l1.4-1.4-2.1-1-.9.8c-1-.4-1.9-1.3-2.3-2.3l.8-.9-1-2.1z",
  telegram: "M21.5 3.5 2.5 10.8l6.6 2.4 2.4 6.6 3-4.2 4.6 3.4zM9.2 13.2l8-6.2",
  facebook: "M15 3h-2.3A3.7 3.7 0 0 0 9 6.7V9H6.5v3H9v9h3.2v-9h2.5l.5-3h-3V6.9c0-.5.4-.9.9-.9H15z",
  email: "M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM3 7l9 6.5L21 7",
  copiar:
    "M9 9h10a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V10a1 1 0 0 1 1-1zM16 9V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3",
  lista: "M10 6h10M10 12h10M10 18h10M4 5.5l1.2 1.2L7.5 4.5M4 11.5l1.2 1.2 2.3-2.2M4 17.5l1.2 1.2 2.3-2.2",
  baixo: "M6 9l6 6 6-6",
} as const;

export type NomeIcone = keyof typeof DESENHOS;

export function Icone({
  nome,
  tamanho = 20,
  ...resto
}: { nome: NomeIcone; tamanho?: number } & SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={tamanho}
      height={tamanho}
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      className="icone"
      {...resto}
    >
      <path d={DESENHOS[nome]} />
    </svg>
  );
}
