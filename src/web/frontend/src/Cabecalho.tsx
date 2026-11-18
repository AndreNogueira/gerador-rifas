import { useEffect } from "react";
import { Donativo } from "./Donativo";
import { useI18n } from "./i18n";
import { Icone, type NomeIcone } from "./icones";
import { useMenuFlutuante } from "./menu";
import { Partilhar } from "./Partilhar";
import { Ligacao, useLocalizacao } from "./rota";
import type { Tema } from "./tema";
import { VISUAIS, type Visual } from "./temas";

/** As páginas soltas do cabeçalho; o tutorial, o vídeo e os guias «como fazer» vivem todos no menu «Ajuda». */
const PAGINAS: readonly { para: string; chave: string; icone: NomeIcone }[] = [
  { para: "/sorteio", chave: "web_sorteio", icone: "faiscas" },
  { para: "/sobre", chave: "mi_sobre", icone: "info" },
];

/** O que o menu «Ajuda» abre à frente dos guias: o tutorial e o vídeo. */
const AJUDA: readonly { para: string; chave: string; icone: NomeIcone }[] = [
  { para: "/tutorial", chave: "tut_titulo", icone: "livro" },
  { para: "/video", chave: "mi_video", icone: "video" },
];

/** Os guias «como fazer» (o servidor tem a mesma tabela em `guias.CAMINHOS`): a segunda parte do menu «Ajuda». */
export const MENU_COMO_FAZER: readonly { para: string; chave: string }[] = [
  { para: "/rifas-para-escolas", chave: "web_guia_escolas" },
  { para: "/rifas-para-associacoes", chave: "web_guia_associacoes" },
  { para: "/rifas-para-clubes", chave: "web_guia_clubes" },
  { para: "/rifas-para-bombeiros", chave: "web_guia_bombeiros" },
  { para: "/rifas-para-festas", chave: "web_guia_festas" },
  { para: "/rifas-para-igrejas", chave: "web_guia_igrejas" },
];

/** Um só separador para tudo o que ensina a usar o site (tutorial, vídeo e «como fazer»): o cabeçalho fica curto e o nome da app cabe sempre inteiro. */
function MenuAjuda({ caminho }: { caminho: string }) {
  const { t } = useI18n();
  const menu = useMenuFlutuante("esq");
  const { fechar } = menu;
  // biome-ignore lint/correctness/useExhaustiveDependencies: fecha-se quando a página muda
  useEffect(() => fechar(), [caminho, fechar]);
  const ativo = AJUDA.some((g) => g.para === caminho) || MENU_COMO_FAZER.some((g) => g.para === caminho);
  return (
    <div className="grupo-menu">
      <button
        type="button"
        ref={menu.refBotao}
        className="nav-botao"
        aria-expanded={menu.aberto}
        aria-controls="menu-ajuda"
        aria-current={ativo ? "page" : undefined}
        onClick={menu.alternar}
        data-testid="nav-ajuda"
      >
        <Icone nome="livro" tamanho={18} />
        {t("m_ajuda")}
        <Icone nome="baixo" tamanho={14} />
      </button>
      {menu.aberto && (
        <ul id="menu-ajuda" ref={menu.refPainel} className="painel-flutuante" style={menu.estilo}>
          {AJUDA.map((g) => (
            <li key={g.para}>
              <Ligacao
                para={g.para}
                onClick={menu.fechar}
                aria-current={caminho === g.para ? "page" : undefined}
                data-testid={`nav-${g.para.slice(1)}`}
              >
                <Icone nome={g.icone} tamanho={18} />
                {t(g.chave).replace(/…$/, "")}
              </Ligacao>
            </li>
          ))}
          <li className="menu-titulo" role="presentation">
            {t("web_como_fazer")}
          </li>
          {MENU_COMO_FAZER.map((g) => (
            <li key={g.para}>
              <Ligacao
                para={g.para}
                onClick={menu.fechar}
                aria-current={caminho === g.para ? "page" : undefined}
                data-testid={`guia-${g.para.slice(1)}`}
              >
                {t(g.chave)}
              </Ligacao>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

const ICONE_DO_TEMA: Record<Tema, NomeIcone> = { auto: "auto", claro: "sol", escuro: "lua" };

interface Props {
  tema: Tema;
  mudarTema: (t: Tema) => void;
  visual: Visual;
  mudarVisual: (v: Visual) => void;
  /** O `DONATIVO_URL` do servidor: vazio = sem botão de donativo. */
  donativoUrl?: string;
}

export function Cabecalho({ tema, mudarTema, visual, mudarVisual, donativoUrl = "" }: Props) {
  const { t, lingua, linguas, mudarLingua } = useI18n();
  const caminho = useLocalizacao().split("?")[0];
  return (
    <header className="topo">
      <Ligacao para="/" className="marca">
        <img src="/icone.svg" alt="" width={46} height={46} />
        {caminho === "/" ? (
          <h1 className="nome">{t("app_nome")}</h1>
        ) : (
          <p className="nome">{t("app_nome")}</p>
        )}
      </Ligacao>
      <nav className="navegacao" aria-label={t("app_nome")}>
        <MenuAjuda caminho={caminho ?? ""} />
        {PAGINAS.map((p) => (
          <Ligacao
            key={p.para}
            para={p.para}
            aria-current={caminho === p.para ? "page" : undefined}
            data-testid={`nav-${p.para.slice(1)}`}
          >
            <Icone nome={p.icone} tamanho={18} />
            {t(p.chave).replace(/…$/, "")}
          </Ligacao>
        ))}
      </nav>
      <div className="definicoes">
        <Donativo url={donativoUrl} variante="topo" />
        <Partilhar variante="topo" />
        <label className="seletor">
          <Icone nome="globo" tamanho={18} />
          <span className="so-leitores">{t("m_idioma")}</span>
          <select
            value={lingua}
            onChange={(e) => mudarLingua(e.target.value)}
            data-testid="lingua"
            aria-label={t("m_idioma")}
          >
            {linguas.map((l) => (
              <option key={l.codigo} value={l.codigo}>
                {l.nome}
              </option>
            ))}
          </select>
        </label>
        <label className="seletor">
          <Icone nome="paleta" tamanho={18} />
          <span className="so-leitores">{t("web_visual")}</span>
          <select
            value={visual}
            onChange={(e) => mudarVisual(e.target.value as Visual)}
            data-testid="visual"
            aria-label={t("web_visual")}
          >
            {VISUAIS.map((v) => (
              <option key={v.id} value={v.id} title={v.descricao}>
                {v.nome}
              </option>
            ))}
          </select>
        </label>
        <label className="seletor modo-tema">
          <Icone nome={ICONE_DO_TEMA[tema]} tamanho={18} />
          <span className="so-leitores">{t("mi_tema")}</span>
          <select
            value={tema}
            onChange={(e) => mudarTema(e.target.value as Tema)}
            data-testid="tema"
            aria-label={t("mi_tema")}
          >
            <option value="auto">{t("web_tema_auto")}</option>
            <option value="claro">{t("mi_tema_claro")}</option>
            <option value="escuro">{t("mi_tema_escuro")}</option>
          </select>
        </label>
      </div>
    </header>
  );
}
