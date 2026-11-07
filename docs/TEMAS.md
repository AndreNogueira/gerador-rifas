# Temas visuais

A webapp tem **8 temas** (escolhidos no cabeçalho, ícone da paleta) e cada um tem versão **clara e escura** (escolhida à parte, com o ícone do sol/lua). O tema e o modo guardam-se no browser (`rifas.visual`, `rifas.tema`) e aplicam-se antes de a página pintar (script em `index.html`), por isso não há «piscar» ao abrir.

| Tema | Ideia | Letra | Assinatura |
|---|---|---|---|
| **Premiado** (por omissão) | o bilhete premiado | Bricolage Grotesque | violeta e magenta, picotado e entalhes, faixa de confetis |
| **Quermesse** | feira popular | Alfa Slab One | tenda vermelha com lâmpadas e festo; toldo às riscas (na cor do passo) em cada bilhete |
| **Arcade** | máquina de jogos | Pixelify Sans | néon, grelha e linhas de varrimento, sombras de pixel, barra de progresso em blocos |
| **Brutalista** | neobrutalismo | Space Grotesk | contornos de 3 px, sombras duras, cores chapadas; no escuro, sombras amarelas |
| **Risografia** | impressão de duas tintas | Fraunces + Space Grotesk | círculos de tinta que se multiplicam, retícula, sombras «mal registadas» |
| **Janela 98** | computador dos anos 90 | Tahoma | cada passo é uma janela com barra de título e relevo |
| **Gala** | art déco | Marcellus + Jost | dourado sobre azul-noite, molduras duplas, raios de leque, insígnias chanfradas |
| **Natal** | rifa de Natal | Fraunces + Bricolage | verde-pinheiro, risca de bengala doce, luzinhas e neve a cair devagar |

Ideias vistas na pesquisa de tendências para 2026 (neobrutalismo, pixel e retrofuturismo, interfaces de sistemas antigos, bilhetes de feira vintage, impressão riso) e o que o produto tem de próprio (**bilhetes, picotado, números**) deram os temas. O primeiro nasceu do próprio bilhete: tudo o resto são variações do mesmo vocabulário.

## Como funciona

- `src/estilos.css` define **todas as variáveis** com os valores do **Premiado** (que é também o tema de reserva, antes de o React arrancar) e as regras de layout. Nada nele é «de um tema» além desses valores.
- `src/temas/<id>.css` **reescreve variáveis** (e, quando faz falta, junta um adorno) debaixo de `:root[data-visual="<id>"]`. O atributo `data-visual` vem de `tema.ts`; o modo claro/escuro é `data-tema` (`light`/`dark`) ou, sem ele, o do sistema.
- As cores usam **`light-dark(claro, escuro)`**, por isso cada tema escreve as duas versões lado a lado e o modo troca-as sozinho. Podes usar `light-dark()` também dentro de gradientes.
- `src/temas.ts` regista o `id`, o nome (próprio, não se traduz) e a descrição (vai no `title` da opção).

### Variáveis principais

| Grupo | Variáveis |
|---|---|
| Cores | `--fundo --cartao --texto --suave --linha --campo --destaque --destaque-2 --ok --aviso --erro --sombra-cor` e as quatro cores dos passos `--passo-1…4` |
| Faixa do cabeçalho | `--banda` (qualquer *background*), `--banda-altura`, `--banda-forma` (`clip-path`), `--b1 --b2 --b3`, `--topo-texto`, `--pilula`, `--pilula-texto`, `--nav-ativo`, `--nav-ativo-texto` |
| Botões | `--botao-1 --botao-2` (gradiente), `--botao-texto`, `--botao-borda`, `--botao-sombra`, `--botao-sombra-hover`, `--botao-hover`, `--botao-ativo` (os *transform*), `--entrega-1 --entrega-2` |
| Forma e letra | `--fonte`, `--fonte-titulo`, `--peso-titulo`, `--raio`, `--raio-c`, `--borda`, `--filtro-coluna` e `--sombra-visor` (sombras), `--corte` (altura do cabeçalho do bilhete), `--extra` (espaço por cima, para toldo/barra de título), `--entalhe` (raio dos entalhes) |

## Receita: um tema novo

1. **`src/temas/<id>.css`**: começa por um comentário de 2–3 linhas com a ideia. **Todos os seletores começam por `:root[data-visual="<id>"]`** (um teste verifica-o). Define claro **e** escuro com `light-dark()`.
2. **Regista-o** em `src/temas.ts` e **importa a folha** em `src/main.tsx` (um teste verifica as duas coisas).
3. **Letras**: só se forem necessárias, de `@fontsource` / `@fontsource-variable`, **versão exata** (`pnpm add -E …`), importadas em `main.tsx`. O browser só descarrega as que o tema usa. Mantém um *fallback* de sistema.
4. **Vê-o a sério**: `pnpm build`, `python -m src.web`, carrega os ficheiros de `tests/fixtures/`, e olha para o ecrã principal, o tutorial, um diálogo, em claro e escuro, em largo e em ecrã de telemóvel (390 px). Junta capturas ao PR.
5. **Acessibilidade**: texto com contraste suficiente (≥ 4,5:1; ≥ 3:1 para texto grande e ícones), foco visível (`:focus-visible` já usa `--destaque-2`), nada essencial só em cor. Movimento só discreto: o CSS global respeita `prefers-reduced-motion`.
6. **Sem tocar na estrutura**: não mudes os componentes React para um tema. Se precisas de um gancho novo, junta uma variável a `estilos.css` com o valor do Premiado e usa-a.

## Limites conhecidos

- Os contrastes foram **vistos**, não medidos (ver `docs/ROADMAP.md`).
- Os nomes dos temas não estão traduzidos (são nomes próprios); o rótulo do seletor («Estilo») está nas 18 línguas.
- O PDF.js do browser (visor) mantém sempre o seu aspeto, em qualquer tema.
