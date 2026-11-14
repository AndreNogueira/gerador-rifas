import { useState } from "react";
import { useDialogos } from "./dialogos";
import { useI18n } from "./i18n";
import { Icone } from "./icones";
import { comPrefixo } from "./rota";

/** O endereço que se partilha: a página inicial na língua em que se está (`/en`, `/ja`…); o português fica em `/`. */
export function enderecoParaPartilhar(origem: string, lingua: string | null): string {
  return `${origem}${comPrefixo("/", lingua)}`;
}

export interface LigacaoDePartilha {
  id: "whatsapp" | "telegram" | "facebook" | "email";
  nome: string;
  href: string;
}

/**
 * As ligações de partilha: ligações simples para o próprio serviço de cada rede, sem scripts de terceiros nem rastreio (a política de
 * privacidade diz «quase nenhum dado»). O texto e o endereço vão no URL; nada sai daqui até alguém carregar numa delas.
 */
export function ligacoesDePartilha(url: string, texto: string, assunto: string): LigacaoDePartilha[] {
  const u = encodeURIComponent(url);
  const t = encodeURIComponent(texto);
  return [
    {
      id: "whatsapp",
      nome: "WhatsApp",
      href: `https://wa.me/?text=${encodeURIComponent(`${texto} ${url}`)}`,
    },
    { id: "telegram", nome: "Telegram", href: `https://t.me/share/url?url=${u}&text=${t}` },
    { id: "facebook", nome: "Facebook", href: `https://www.facebook.com/sharer/sharer.php?u=${u}` },
    {
      id: "email",
      nome: "E-mail",
      href: `mailto:?subject=${encodeURIComponent(assunto)}&body=${encodeURIComponent(`${texto}\n\n${url}`)}`,
    },
  ];
}

/**
 * O botão «Partilhar»: abre uma lista curta (partilha do telemóvel/computador quando o browser a tem, WhatsApp, Telegram, Facebook, e-mail
 * e copiar a ligação) para dar a conhecer o gerador a outras associações, escolas e comissões de festas. Está no rodapé e, depois de gerar,
 * no cartão dos ficheiros (`variante="cartao"`, com uma frase a convidar).
 */
export function Partilhar({ variante }: { variante: "rodape" | "cartao" }) {
  const { t, lingua } = useI18n();
  const { aviso } = useDialogos();
  const [aberto, setAberto] = useState(false);
  const url = enderecoParaPartilhar(window.location.origin, lingua);
  const texto = t("web_partilhar_texto");
  const nativa = typeof navigator !== "undefined" && typeof navigator.share === "function";

  const partilharNativa = async () => {
    try {
      await navigator.share({ title: t("app_nome"), text: texto, url });
      setAberto(false);
    } catch {
      /* o utilizador fechou a janela de partilha: não é um erro */
    }
  };
  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(url);
      aviso(t("web_ligacao_copiada"), "aviso");
    } catch {
      aviso(url, "aviso");
    }
    setAberto(false);
  };

  return (
    <div className={`partilhar partilhar-${variante}`} data-testid={`partilhar-${variante}`}>
      {variante === "cartao" && <p className="partilhar-chamada">{t("web_partilhar_chamada")}</p>}
      <button
        type="button"
        className={variante === "cartao" ? "botao secundario" : "partilhar-botao"}
        aria-expanded={aberto}
        aria-controls={`partilhar-lista-${variante}`}
        onClick={() => setAberto((a) => !a)}
        data-testid={`partilhar-abrir-${variante}`}
      >
        <Icone nome="partilhar" />
        {t("web_partilhar")}
      </button>
      {aberto && (
        <ul id={`partilhar-lista-${variante}`} className="partilhar-lista" aria-label={t("web_partilhar")}>
          {nativa && (
            <li>
              <button type="button" onClick={() => void partilharNativa()} data-testid="partilhar-nativa">
                {t("web_partilhar")}…
              </button>
            </li>
          )}
          {ligacoesDePartilha(url, texto, t("app_nome")).map((l) => (
            <li key={l.id}>
              <a href={l.href} target="_blank" rel="noopener noreferrer" data-testid={`partilhar-${l.id}`}>
                {l.nome}
              </a>
            </li>
          ))}
          <li>
            <button type="button" onClick={() => void copiar()} data-testid="partilhar-copiar">
              <Icone nome="ligacao" />
              {t("web_copiar_ligacao")}
            </button>
          </li>
        </ul>
      )}
    </div>
  );
}
