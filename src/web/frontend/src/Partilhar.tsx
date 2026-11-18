import { useState } from "react";
import { useDialogos } from "./dialogos";
import { useI18n } from "./i18n";
import { Icone } from "./icones";
import { useMenuFlutuante } from "./menu";
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
 * e copiar a ligação) para dar a conhecer o gerador a outras associações, escolas e comissões de festas. Está no cabeçalho (`variante="topo"`,
 * bem à vista, com a lista num painel flutuante) e, depois de gerar, no cartão dos ficheiros (`variante="cartao"`, com uma frase a convidar).
 */
export function Partilhar({
  variante,
  aoEscolher,
}: {
  variante: "topo" | "cartao" | "menu";
  aoEscolher?: () => void;
}) {
  const { t, lingua } = useI18n();
  const { aviso } = useDialogos();
  const menu = useMenuFlutuante("dir");
  const [abertoCartao, setAbertoCartao] = useState(false);
  const flutuante = variante === "topo";
  const aberto = flutuante ? menu.aberto : abertoCartao;
  const fechar =
    variante === "menu" ? (aoEscolher ?? (() => {})) : flutuante ? menu.fechar : () => setAbertoCartao(false);
  const url = enderecoParaPartilhar(window.location.origin, lingua);
  const texto = t("web_partilhar_texto");
  const nativa = typeof navigator !== "undefined" && typeof navigator.share === "function";

  const partilharNativa = async () => {
    try {
      await navigator.share({ title: t("app_nome"), text: texto, url });
      fechar();
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
    fechar();
  };

  const itens = (
    <>
      {nativa && (
        <li>
          <button type="button" onClick={() => void partilharNativa()} data-testid="partilhar-nativa">
            <span className="rede-icone rede-nativa" aria-hidden="true">
              <Icone nome="partilhar" tamanho={18} />
            </span>
            {t("web_partilhar")}…
          </button>
        </li>
      )}
      {ligacoesDePartilha(url, texto, t("app_nome")).map((l) => (
        <li key={l.id}>
          <a
            href={l.href}
            target="_blank"
            rel="noopener noreferrer"
            onClick={fechar}
            data-testid={`partilhar-${l.id}`}
          >
            <span className={`rede-icone rede-${l.id}`} aria-hidden="true">
              <Icone nome={l.id} tamanho={18} />
            </span>
            {l.nome}
          </a>
        </li>
      ))}
      <li>
        <button type="button" onClick={() => void copiar()} data-testid="partilhar-copiar">
          <span className="rede-icone rede-copiar" aria-hidden="true">
            <Icone nome="copiar" tamanho={18} />
          </span>
          {t("web_copiar_ligacao")}
        </button>
      </li>
    </>
  );
  const lista = (
    <ul
      id={`partilhar-lista-${variante}`}
      ref={flutuante ? menu.refPainel : undefined}
      className={`partilhar-lista${flutuante ? " painel-flutuante" : ""}`}
      style={flutuante ? menu.estilo : undefined}
      aria-label={t("web_partilhar")}
    >
      {itens}
    </ul>
  );

  // dentro do menu «hambúrguer»: as mesmas opções, já abertas, como linhas do menu
  if (variante === "menu")
    return (
      <>
        <li className="menu-titulo" role="presentation">
          {t("web_partilhar")}
        </li>
        {itens}
      </>
    );

  return (
    <div className={`partilhar partilhar-${variante}`} data-testid={`partilhar-${variante}`}>
      {variante === "cartao" && <p className="partilhar-chamada">{t("web_partilhar_chamada")}</p>}
      <button
        type="button"
        ref={flutuante ? menu.refBotao : undefined}
        className={variante === "cartao" ? "botao secundario" : "partilhar-botao"}
        aria-expanded={aberto}
        aria-controls={`partilhar-lista-${variante}`}
        onClick={flutuante ? menu.alternar : () => setAbertoCartao((a) => !a)}
        data-testid={`partilhar-abrir-${variante}`}
      >
        <Icone nome="partilhar" />
        <span className="partilhar-texto">{t("web_partilhar")}</span>
      </button>
      {aberto && lista}
    </div>
  );
}
