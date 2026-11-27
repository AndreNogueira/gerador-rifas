import { type ReactNode, useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Donativo } from "./Donativo";
import { useI18n } from "./i18n";
import { Icone, type NomeIcone } from "./icones";
import { useMenuFlutuante } from "./menu";
import { Partilhar } from "./Partilhar";
import { Ligacao, useLocalizacao } from "./rota";
import type { Tema } from "./tema";
import { VISUAIS, type Visual } from "./temas";

/** As páginas soltas do cabeçalho; o tutorial, o vídeo e os guias «como fazer» vivem todos no menu «Ajuda». */
const PAGINAS: readonly {
  para: string;
  chave: string;
  icone: NomeIcone;
  id: "sorteio" | "precario" | "sobre" | "comentarios" | "reportar";
}[] = [
  { para: "/sorteio", chave: "web_sorteio", icone: "faiscas", id: "sorteio" },
  { para: "/precario", chave: "web_precario", icone: "lista", id: "precario" },
  { para: "/sobre", chave: "mi_sobre", icone: "info", id: "sobre" },
  { para: "/comentarios", chave: "web_comentarios", icone: "comentario", id: "comentarios" },
  { para: "/reportar-problema", chave: "web_reportar", icone: "bug", id: "reportar" },
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

export type ItemId =
  | "ajuda"
  | "sorteio"
  | "precario"
  | "sobre"
  | "comentarios"
  | "reportar"
  | "donativo"
  | "partilhar"
  | "lingua"
  | "visual"
  | "tema";
/** A ordem em que se vêem, da esquerda para a direita. */
const ORDEM: readonly ItemId[] = [
  "ajuda",
  "sorteio",
  "precario",
  "sobre",
  "comentarios",
  "reportar",
  "donativo",
  "partilhar",
  "lingua",
  "visual",
  "tema",
];
/** A ordem em que saem do cabeçalho para o menu «hambúrguer» quando o ecrã estreita. «Comentários» e «Reportar problema» têm de se ver: saem quase por último. */
export const SAI_PRIMEIRO: readonly ItemId[] = [
  "tema",
  "visual",
  "sobre",
  "precario",
  "sorteio",
  "lingua",
  "ajuda",
  "partilhar",
  "reportar",
  "comentarios",
  "donativo",
];
const FOLGA_ENTRE_ITENS = 8; // px: o `gap` do `.cluster`
const LARGURA_DO_BURGER = 44; // px

/**
 * Quais dos itens não cabem ao lado do nome da app. Usa as larguras reais (todos desenhados no medidor invisível, ver `Cabecalho`) e vai tirando por
 * `SAI_PRIMEIRO` até o resto, mais o botão do menu, caber. Em testes (sem layout) nem se chama.
 */
export function calcularOcultos(
  disponivel: number,
  larguras: ReadonlyMap<ItemId, number>,
  existentes: readonly ItemId[],
): ItemId[] {
  const total = (ids: readonly ItemId[]) =>
    ids.reduce((soma, id) => soma + (larguras.get(id) ?? 0), 0) +
    FOLGA_ENTRE_ITENS * Math.max(0, ids.length - 1);
  let visiveis = [...existentes];
  if (total(visiveis) <= disponivel) return [];
  const ocultos: ItemId[] = [];
  for (const id of SAI_PRIMEIRO) {
    if (!visiveis.includes(id)) continue;
    visiveis = visiveis.filter((x) => x !== id);
    ocultos.push(id);
    if (total(visiveis) + FOLGA_ENTRE_ITENS + LARGURA_DO_BURGER <= disponivel) break;
  }
  // as sobras de espaço aproveitam-se: volta ao cabeçalho, dos mais importantes para os menos, o que ainda couber (sem buracos)
  for (const id of [...ocultos].reverse()) {
    const com = ORDEM.filter((x) => x === id || visiveis.includes(x));
    if (total(com) + FOLGA_ENTRE_ITENS + LARGURA_DO_BURGER <= disponivel) {
      visiveis = com;
      ocultos.splice(ocultos.indexOf(id), 1);
    }
  }
  return ocultos;
}

function LigacoesDeAjuda({
  caminho,
  aoEscolher,
  testidDe,
}: {
  caminho: string;
  aoEscolher: () => void;
  testidDe: (para: string) => string;
}) {
  const { t } = useI18n();
  return (
    <>
      {AJUDA.map((g) => (
        <li key={g.para}>
          <Ligacao
            para={g.para}
            onClick={aoEscolher}
            aria-current={caminho === g.para ? "page" : undefined}
            data-testid={testidDe(g.para)}
          >
            <Icone nome={g.icone} tamanho={18} />
            {t(g.chave).replace(/…$/, "")}
          </Ligacao>
        </li>
      ))}
      <li className="menu-titulo" role="presentation">
        {t("web_como_fazer")}
      </li>
      <li>
        <Ligacao
          para="/como-fazer"
          onClick={aoEscolher}
          aria-current={caminho === "/como-fazer" ? "page" : undefined}
          data-testid="guia-como-fazer"
        >
          {t("web_guia_todos")}
        </Ligacao>
      </li>
      {MENU_COMO_FAZER.map((g) => (
        <li key={g.para}>
          <Ligacao
            para={g.para}
            onClick={aoEscolher}
            aria-current={caminho === g.para ? "page" : undefined}
            data-testid={`guia-${g.para.slice(1)}`}
          >
            {t(g.chave)}
          </Ligacao>
        </li>
      ))}
    </>
  );
}

const estaNaAjuda = (caminho: string) =>
  AJUDA.some((g) => g.para === caminho) ||
  caminho === "/como-fazer" ||
  MENU_COMO_FAZER.some((g) => g.para === caminho);

/** Um só separador para tudo o que ensina a usar o site (tutorial, vídeo e «como fazer»): o cabeçalho fica curto e o nome da app cabe sempre inteiro. */
function MenuAjuda({ caminho }: { caminho: string }) {
  const { t } = useI18n();
  const menu = useMenuFlutuante("esq");
  const { fechar } = menu;
  // biome-ignore lint/correctness/useExhaustiveDependencies: fecha-se quando a página muda
  useEffect(() => fechar(), [caminho, fechar]);
  return (
    <div className="grupo-menu">
      <button
        type="button"
        ref={menu.refBotao}
        className="nav-botao"
        aria-expanded={menu.aberto}
        aria-controls="menu-ajuda"
        aria-current={estaNaAjuda(caminho) ? "page" : undefined}
        onClick={menu.alternar}
        data-testid="nav-ajuda"
      >
        <Icone nome="livro" tamanho={18} />
        {t("m_ajuda")}
        <Icone nome="baixo" tamanho={14} />
      </button>
      {menu.aberto && (
        <ul id="menu-ajuda" ref={menu.refPainel} className="painel-flutuante" style={menu.estilo}>
          <LigacoesDeAjuda
            caminho={caminho}
            aoEscolher={menu.fechar}
            testidDe={(para) => `nav-${para.slice(1)}`}
          />
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
  const caminho = useLocalizacao().split("?")[0] ?? "";
  const topo = useRef<HTMLElement>(null);
  // as larguras reais vêm de um medidor sempre invisível e fora do fluxo (`medidorRef`, no fim do JSX), nunca do `.cluster`
  // visível: assim o cabeçalho que se vê nunca precisa de mostrar-se por completo só para se medir a si próprio (era a
  // causa real de um CLS medido em produção, ~0.14, não os anúncios — ver `_cabecalho.scss`, `.cluster-medidor`).
  const medidorRef = useRef<HTMLDivElement>(null);
  const [ocultos, setOcultos] = useState<ItemId[]>([]);
  const [pedidos, setPedidos] = useState(0); // um contador: pedir uma nova medição (o medidor já está sempre lá, só se lê de novo)
  const remedir = useCallback(() => setPedidos((n) => n + 1), []);
  const existentes = ORDEM.filter((id) => id !== "donativo" || donativoUrl);

  // biome-ignore lint/correctness/useExhaustiveDependencies: `existentes` só muda com o donativo, que já faz medir de novo
  useLayoutEffect(() => {
    const el = topo.current;
    const medidor = medidorRef.current;
    const marca = el?.querySelector<HTMLElement>(".marca");
    if (!el || !medidor || !marca) return;
    const css = getComputedStyle(el);
    const disponivel =
      el.clientWidth -
      (Number.parseFloat(css.paddingLeft) || 0) -
      (Number.parseFloat(css.paddingRight) || 0) -
      marca.offsetWidth -
      (Number.parseFloat(css.columnGap) || 0);
    const larguras = new Map<ItemId, number>();
    for (const item of medidor.querySelectorAll<HTMLElement>("[data-item]"))
      larguras.set(item.dataset.item as ItemId, item.offsetWidth);
    setOcultos(el.clientWidth ? calcularOcultos(disponivel, larguras, existentes) : []);
  }, [pedidos]);

  // volta a medir quando o espaço muda (largura da janela) ou o que se desenha muda (textos de outra língua, donativo, letras a carregar)
  // biome-ignore lint/correctness/useExhaustiveDependencies: estes valores só servem para disparar a nova medição
  useEffect(remedir, [remedir, lingua, visual, tema, donativoUrl]);
  useEffect(() => {
    const el = topo.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    let largura = el.clientWidth;
    const observador = new ResizeObserver(() => {
      if (el.clientWidth !== largura) {
        largura = el.clientWidth;
        remedir();
      }
    });
    observador.observe(el);
    void document.fonts?.ready.then(remedir);
    return () => observador.disconnect();
  }, [remedir]);

  const burger = useMenuFlutuante("dir", 320, 200);
  const fecharBurger = burger.fechar;
  // biome-ignore lint/correctness/useExhaustiveDependencies: fecha-se quando a página muda
  useEffect(() => fecharBurger(), [caminho, fecharBurger]);

  const visivel = (id: ItemId) => existentes.includes(id) && !ocultos.includes(id);
  const escondido = (id: ItemId) => existentes.includes(id) && ocultos.includes(id);
  const item = (id: ItemId, filho: ReactNode) =>
    visivel(id) ? (
      <div className="item-cab" data-item={id} key={id}>
        {filho}
      </div>
    ) : null;

  const seletorLingua = (
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
  );
  const seletorVisual = (
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
  );
  const seletorTema = (
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
  );

  const paginasVisiveis = PAGINAS.filter((p) => visivel(p.id));
  const algumEscondido = ocultos.length > 0;

  return (
    <header className="topo" ref={topo}>
      <Ligacao para="/" className="marca">
        <img src="/icone.svg" alt="" width={46} height={46} />
        {caminho === "/" ? (
          <h1 className="nome">{t("app_nome")}</h1>
        ) : (
          <p className="nome">{t("app_nome")}</p>
        )}
      </Ligacao>
      <div className="cluster">
        {(visivel("ajuda") || paginasVisiveis.length > 0) && (
          <nav className="navegacao" aria-label={t("app_nome")}>
            {item("ajuda", <MenuAjuda caminho={caminho} />)}
            {paginasVisiveis.map((p) =>
              item(
                p.id,
                <Ligacao
                  para={p.para}
                  aria-current={caminho === p.para ? "page" : undefined}
                  data-testid={`nav-${p.para.slice(1)}`}
                >
                  <Icone nome={p.icone} tamanho={18} />
                  {t(p.chave).replace(/…$/, "")}
                </Ligacao>,
              ),
            )}
          </nav>
        )}
        {item("donativo", <Donativo url={donativoUrl} variante="topo" />)}
        {item("partilhar", <Partilhar variante="topo" />)}
        {item("lingua", seletorLingua)}
        {item("visual", seletorVisual)}
        {item("tema", seletorTema)}
        {algumEscondido && (
          <div className="item-cab">
            <button
              type="button"
              ref={burger.refBotao}
              className="burger"
              aria-expanded={burger.aberto}
              aria-controls="menu-burger"
              aria-label={t("web_menu")}
              onClick={burger.alternar}
              data-testid="nav-burger"
            >
              <Icone nome="menu" tamanho={22} />
            </button>
            {burger.aberto && (
              <ul
                id="menu-burger"
                ref={burger.refPainel}
                className="painel-flutuante menu-burger"
                style={burger.estilo}
                aria-label={t("web_menu")}
              >
                {escondido("ajuda") && (
                  <>
                    <li className="menu-titulo menu-titulo-primeiro" role="presentation">
                      {t("m_ajuda")}
                    </li>
                    <LigacoesDeAjuda
                      caminho={caminho}
                      aoEscolher={burger.fechar}
                      testidDe={(para) => `burger-${para.slice(1)}`}
                    />
                  </>
                )}
                {PAGINAS.filter((p) => escondido(p.id)).map((p) => (
                  <li key={p.id}>
                    <Ligacao
                      para={p.para}
                      onClick={burger.fechar}
                      aria-current={caminho === p.para ? "page" : undefined}
                      data-testid={`burger-${p.id}`}
                    >
                      <Icone nome={p.icone} tamanho={18} />
                      {t(p.chave).replace(/…$/, "")}
                    </Ligacao>
                  </li>
                ))}
                {escondido("donativo") && (
                  <li>
                    <Donativo url={donativoUrl} variante="menu" />
                  </li>
                )}
                {escondido("partilhar") && <Partilhar variante="menu" aoEscolher={burger.fechar} />}
                {escondido("lingua") && (
                  <li>
                    <label className="seletor-menu">
                      {t("m_idioma")}
                      <select
                        value={lingua}
                        onChange={(e) => mudarLingua(e.target.value)}
                        data-testid="burger-lingua"
                      >
                        {linguas.map((l) => (
                          <option key={l.codigo} value={l.codigo}>
                            {l.nome}
                          </option>
                        ))}
                      </select>
                    </label>
                  </li>
                )}
                {escondido("visual") && (
                  <li>
                    <label className="seletor-menu">
                      {t("web_visual")}
                      <select
                        value={visual}
                        onChange={(e) => mudarVisual(e.target.value as Visual)}
                        data-testid="burger-visual"
                      >
                        {VISUAIS.map((v) => (
                          <option key={v.id} value={v.id}>
                            {v.nome}
                          </option>
                        ))}
                      </select>
                    </label>
                  </li>
                )}
                {escondido("tema") && (
                  <li>
                    <label className="seletor-menu">
                      {t("mi_tema")}
                      <select
                        value={tema}
                        onChange={(e) => mudarTema(e.target.value as Tema)}
                        data-testid="burger-tema"
                      >
                        <option value="auto">{t("web_tema_auto")}</option>
                        <option value="claro">{t("mi_tema_claro")}</option>
                        <option value="escuro">{t("mi_tema_escuro")}</option>
                      </select>
                    </label>
                  </li>
                )}
              </ul>
            )}
          </div>
        )}
      </div>
      {/* Mede as larguras reais de TODOS os itens (mesmo os que não cabem) para o `useLayoutEffect` acima decidir o que
          sai para o menu. Fica sempre invisível e fora do fluxo (`.cluster-medidor`, CSS em `_cabecalho.scss`): o
          `.cluster` visível NUNCA precisa de se mostrar por completo só para se medir a si próprio — isso já chegou a
          quebrar para 2 linhas por um instante e empurrar o resto da página (um CLS medido em produção, ~0.14, que
          não era dos anúncios). Sem `data-testid` nem `onChange` a sério, de propósito: nunca pode duplicar o que os
          testes (e os leitores de ecrã) veem no `.cluster` real. */}
      <div className="cluster cluster-medidor" ref={medidorRef} aria-hidden="true">
        {(existentes.includes("ajuda") || PAGINAS.some((p) => existentes.includes(p.id))) && (
          <nav className="navegacao">
            {existentes.includes("ajuda") && (
              <div className="item-cab" data-item="ajuda">
                <button type="button" className="nav-botao" tabIndex={-1}>
                  <Icone nome="livro" tamanho={18} />
                  {t("m_ajuda")}
                  <Icone nome="baixo" tamanho={14} />
                </button>
              </div>
            )}
            {PAGINAS.filter((p) => existentes.includes(p.id)).map((p) => (
              <div className="item-cab" data-item={p.id} key={p.id}>
                <span className="nav-botao" tabIndex={-1}>
                  <Icone nome={p.icone} tamanho={18} />
                  {t(p.chave).replace(/…$/, "")}
                </span>
              </div>
            ))}
          </nav>
        )}
        {existentes.includes("donativo") && (
          <div className="item-cab" data-item="donativo">
            <div className="donativo donativo-topo">
              <span className="donativo-botao" tabIndex={-1}>
                <Icone nome="coracao" />
                <span className="donativo-texto">{t("web_donativo")}</span>
              </span>
            </div>
          </div>
        )}
        <div className="item-cab" data-item="partilhar">
          <div className="partilhar partilhar-topo">
            <button type="button" className="partilhar-botao" tabIndex={-1}>
              <Icone nome="partilhar" />
              <span className="partilhar-texto">{t("web_partilhar")}</span>
            </button>
          </div>
        </div>
        <div className="item-cab" data-item="lingua">
          <label className="seletor">
            <Icone nome="globo" tamanho={18} />
            <span className="so-leitores">{t("m_idioma")}</span>
            <select value={lingua} onChange={() => undefined} tabIndex={-1}>
              {linguas.map((l) => (
                <option key={l.codigo} value={l.codigo}>
                  {l.nome}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="item-cab" data-item="visual">
          <label className="seletor">
            <Icone nome="paleta" tamanho={18} />
            <span className="so-leitores">{t("web_visual")}</span>
            <select value={visual} onChange={() => undefined} tabIndex={-1}>
              {VISUAIS.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.nome}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="item-cab" data-item="tema">
          <label className="seletor modo-tema">
            <Icone nome={ICONE_DO_TEMA[tema]} tamanho={18} />
            <span className="so-leitores">{t("mi_tema")}</span>
            <select value={tema} onChange={() => undefined} tabIndex={-1}>
              <option value="auto">{t("web_tema_auto")}</option>
              <option value="claro">{t("mi_tema_claro")}</option>
              <option value="escuro">{t("mi_tema_escuro")}</option>
            </select>
          </label>
        </div>
      </div>
    </header>
  );
}
