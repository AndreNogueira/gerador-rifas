import { type KeyboardEvent, useEffect, useState } from "react";
import { Icone } from "./icones";
import { useMenuFlutuante } from "./menu";

export interface OpcaoDesenho {
  id: string;
  nome: string;
}

const LARGURA_LISTA = 360; // px

/** A miniatura estática de um desenho (`scripts/gerar_miniaturas_galeria.py`): o seletor mostra as 24 de uma vez sem pedir nada ao motor. */
export const miniaturaDoDesenho = (id: string) => `/galeria/${id}.webp`;

/**
 * Uma caixa de escolha de uma só linha em que cada opção mostra um mini desenho do template («select-only combobox» do WAI-ARIA: o foco fica
 * no botão e a opção ativa vai em `aria-activedescendant`). Teclado: setas, Home/End, Enter/Espaço escolhem, Esc fecha, uma letra salta para o
 * primeiro nome que começa por ela. Um `<select>` nativo não mostra imagens.
 */
export function SeletorDesenho({
  opcoes,
  valor,
  aoEscolher,
  nomeDaLista,
}: {
  opcoes: readonly OpcaoDesenho[];
  valor: string;
  aoEscolher: (id: string) => void;
  nomeDaLista: string;
}) {
  const menu = useMenuFlutuante("esq", LARGURA_LISTA);
  const { aberto, alternar, fechar, refPainel } = menu;
  const indiceDoValor = Math.max(
    0,
    opcoes.findIndex((o) => o.id === valor),
  );
  const [ativo, setAtivo] = useState(indiceDoValor);
  const atual = opcoes[indiceDoValor];

  // ao abrir, a opção ativa é a escolhida; a lista rola por dentro para a mostrar (sem `scrollIntoView`, que rolaria a página e fecharia o painel)
  // biome-ignore lint/correctness/useExhaustiveDependencies: só ao abrir e quando a opção ativa muda
  useEffect(() => {
    const painel = refPainel.current;
    const el = painel?.querySelector<HTMLElement>('[data-ativo="true"]');
    if (!painel || !el) return;
    if (el.offsetTop < painel.scrollTop) painel.scrollTop = el.offsetTop;
    else if (el.offsetTop + el.offsetHeight > painel.scrollTop + painel.clientHeight)
      painel.scrollTop = el.offsetTop + el.offsetHeight - painel.clientHeight;
  }, [aberto, ativo]);

  const abrir = () => {
    setAtivo(indiceDoValor);
    alternar();
  };
  const escolher = (i: number) => {
    const o = opcoes[i];
    if (o) aoEscolher(o.id);
    fechar();
  };
  const aoTeclar = (e: KeyboardEvent<HTMLButtonElement>) => {
    const ultimo = opcoes.length - 1;
    if (!aberto) {
      if (["ArrowDown", "ArrowUp", "Enter", " "].includes(e.key)) {
        e.preventDefault();
        abrir();
      }
      return;
    }
    const ir = (i: number) => {
      e.preventDefault();
      setAtivo(Math.max(0, Math.min(ultimo, i)));
    };
    if (e.key === "ArrowDown") ir(ativo + 1);
    else if (e.key === "ArrowUp") ir(ativo - 1);
    else if (e.key === "Home") ir(0);
    else if (e.key === "End") ir(ultimo);
    else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      escolher(ativo);
    } else if (e.key === "Tab") fechar();
    else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
      // uma letra: o primeiro nome (a seguir ao ativo, a dar a volta) que começa por ela
      const letra = e.key.toLocaleLowerCase();
      for (let k = 1; k <= opcoes.length; k++) {
        const i = (ativo + k) % opcoes.length;
        if (opcoes[i]?.nome.toLocaleLowerCase().startsWith(letra)) {
          ir(i);
          break;
        }
      }
    }
  };

  return (
    <div className="seletor-desenho">
      <button
        type="button"
        ref={menu.refBotao}
        role="combobox"
        className="seletor-botao"
        aria-haspopup="listbox"
        aria-expanded={aberto}
        aria-controls="galeria-desenhos"
        aria-activedescendant={aberto ? `galeria-desenho-${opcoes[ativo]?.id}` : undefined}
        onClick={abrir}
        onKeyDown={aoTeclar}
        data-testid="galeria-desenho"
      >
        {atual && <img src={miniaturaDoDesenho(atual.id)} alt="" width={96} height={27} />}
        <span className="seletor-nome">{atual?.nome}</span>
        <Icone nome="baixo" tamanho={14} />
      </button>
      {aberto && (
        <ul
          id="galeria-desenhos"
          ref={refPainel}
          // biome-ignore lint/a11y/noNoninteractiveElementToInteractiveRole: `ul` com `listbox` é permitido (ARIA em HTML)
          role="listbox"
          aria-label={nomeDaLista}
          className="painel-flutuante seletor-lista"
          style={menu.estilo}
          data-testid="galeria-desenhos"
        >
          {opcoes.map((o, i) => (
            // biome-ignore lint/a11y/useFocusableInteractive: o foco fica no botão e a opção ativa vai em `aria-activedescendant`
            // biome-ignore lint/a11y/useKeyWithClickEvents: o teclado trata-se no botão (aria-activedescendant); as opções não recebem o foco
            <li
              key={o.id}
              id={`galeria-desenho-${o.id}`}
              // biome-ignore lint/a11y/noNoninteractiveElementToInteractiveRole: opção de um `listbox` (padrão «select-only combobox»)
              role="option"
              aria-selected={o.id === valor}
              data-ativo={i === ativo}
              data-testid={`galeria-opcao-${o.id}`}
              onClick={() => escolher(i)}
              onMouseMove={() => ativo !== i && setAtivo(i)}
            >
              <img src={miniaturaDoDesenho(o.id)} alt="" width={144} height={41} loading="lazy" />
              <span className="seletor-nome">{o.nome}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
