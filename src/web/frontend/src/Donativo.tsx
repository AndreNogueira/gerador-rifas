import { useI18n } from "./i18n";
import { Icone } from "./icones";

/**
 * O donativo, onde se vê. `url` é o `DONATIVO_URL` do servidor (vazio = não há donativo e nada aparece).
 * - `topo`: uma pílula com um coração no cabeçalho, ao lado de «Partilhar» (só o ícone nos telemóveis);
 * - `cartao`: depois de gerar os ficheiros, que é quando o serviço acabou de ser útil: uma frase e o botão.
 * Abre no serviço de pagamento noutro separador e sem referrer; nada é pedido nem guardado aqui.
 */
export function Donativo({ url, variante }: { url: string; variante: "topo" | "cartao" }) {
  const { t } = useI18n();
  if (!url) return null;
  const ligacao = (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={variante === "cartao" ? "botao secundario" : "donativo-botao"}
      data-testid={`donativo-${variante}`}
    >
      <Icone nome="coracao" />
      <span className="donativo-texto">{t("web_donativo")}</span>
    </a>
  );
  if (variante === "topo") return <div className="donativo donativo-topo">{ligacao}</div>;
  return (
    <div className="donativo donativo-cartao">
      <p className="donativo-chamada">{t("web_donativo_chamada")}</p>
      {ligacao}
    </div>
  );
}
