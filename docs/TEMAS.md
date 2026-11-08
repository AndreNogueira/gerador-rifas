# Temas visuais

A webapp tem vários **temas** (escolhidos no cabeçalho, ícone da paleta); cada um tem versão **clara e escura** (escolhida à parte, com o ícone do sol/lua). O tema e o modo guardam-se no browser (`rifas.visual`, `rifas.tema`) e aplicam-se antes de a página pintar (script em `index.html`), por isso não há «piscar» ao abrir.

| Tema | Ideia | Letra | Assinatura |
|---|---|---|---|
| **Premiado** (por omissão) | o bilhete premiado | Bricolage Grotesque | violeta e magenta, picotado e entalhes, faixa de confetis |
| **Quermesse** | feira popular | Alfa Slab One | tenda vermelha com lâmpadas e festo; toldo às riscas em cada bilhete |
| **Arcade** | máquina de jogos | Pixelify Sans | néon, grelha e linhas de varrimento, sombras de pixel, progresso em blocos |
| **Brutalista** | neobrutalismo | Space Grotesk | contornos grossos, sombras duras, cores chapadas; no escuro, sombras amarelas |
| **Risografia** | impressão de duas tintas | Fraunces + Space Grotesk | círculos de tinta que se multiplicam, retícula, sombras «mal registadas» |
| **Janela 98** | computador dos anos 90 | Tahoma | relevo clássico nos botões e janelas, barra de título azul em cada passo |
| **Gala** | art déco | Marcellus + Jost | dourado sobre azul-noite, molduras duplas, raios de leque, insígnias chanfradas |
| **Natal** | rifa de Natal | Fraunces + Bricolage | verde-pinheiro, risca de bengala doce, luzinhas e neve a cair devagar |
| **Matrix Gamer** | chuva de caracteres e HUD de jogo | Orbitron + JetBrains Mono | chuva verde em duas velocidades (`assets/matrix-chuva.svg`), brilho de neon, insígnias hexagonais, RGB nos passos, barra de vida em blocos |

## A regra: a estrutura nunca muda, só cores e formatação

Mudar de tema **não pode mexer na estrutura do site**: os blocos ficam nos mesmos sítios, com a mesma ordem, os mesmos espaços e o mesmo tamanho de letra. Um tema muda só:

- **cores** (todas as da interface, em claro e escuro);
- **letra** (a família e o peso; nunca o tamanho nem o espaçamento);
- **raios** dos cantos e **sombras** (inclui contornos e relevo desenhados com sombras interiores);
- **fundos** que só pintam (a faixa do cabeçalho, a decoração da página, o toldo ou a bengala doce no topo do bilhete, a barra do visor).

Por isso um tema **é um único bloco de variáveis**. A estrutura (inclui a letra dos controlos do cabeçalho) vive em `src/estilos/_geometria.scss` e nas regras da base; as variáveis que um tema pode mudar estão todas em `src/estilos/_tokens.scss`, com os valores do Premiado. `temas.test.tsx` compila cada tema com o Sass e **falha** se o tema:

- tiver mais do que um bloco `:root[data-visual="<id>"]`, ou qualquer `@media`/`@keyframes`;
- declarar algo que não seja uma variável (nada de `padding`, `display`, `width`…);
- mexer numa variável de geometria (`--corte`, `--banda-altura`, `--borda`…);
- usar uma variável que não esteja em `_tokens.scss` (as auxiliares do próprio tema chamam-se `--t-…`).

Medido no browser (Playwright, 1300 px de largura, claro e escuro): as posições dos blocos de todos os temas coincidem com as do Premiado até ≈ 28 px, **só pelo que depende da própria letra** (a largura do texto num botão, e no Arcade uma linha a mais num título). Para o cabeçalho não saltar de linha com letras largas: os botões e seletores do cabeçalho usam sempre a mesma letra (`--fonte-controlos`, em `_geometria.scss`), e em ecrã largo o cabeçalho é uma só linha (o nome da app encolhe com reticências). O nome da app tem a sua variável (`--fonte-marca`).

O que isto custou aos temas já feitos: **Janela 98** perdeu a barra de título «de verdade» (agora é o cabeçalho do bilhete pintado de azul, com o relevo clássico), a faixa e os entalhes; o **Quermesse** e o **Natal** já não alargam o bilhete (o toldo e a bengala doce são pintura no topo); **Arcade**, **Brutalista** e **Janela 98** ficaram sem entalhes (`--entalhe: 0px`); o **Gala** deixou de ter margens próprias.

## Como está feito

- Os estilos são **Sass** (`src/estilos/`), compilado pelo Vite para **um único ficheiro CSS** (`dist/assets/style-*.css`, com as letras incluídas). `pnpm build` corre `scripts/verificar-dist.mjs`, que falha se houver mais do que um CSS ou `<style>` no `index.html`.
- `main.scss` junta: `_tokens` (variáveis e valores do Premiado), `_geometria` (o que não muda), `_base`, `_cabecalho`, `_gerador`, `_paginas` e `temas/_index` (um `@forward` por tema).
- `temas/_<id>.scss` usa o *mixin* `tema(<id>)` (de `_tema.scss`), que gera `:root[data-visual="<id>"] { … }`. O atributo `data-visual` vem de `tema.ts`; o modo claro/escuro é `data-tema` (`light`/`dark`) ou, sem ele, o do sistema.
- As cores usam **`light-dark(claro, escuro)`**, por isso cada tema escreve as duas versões lado a lado. Podes usar `light-dark()` dentro de gradientes.
- Um valor com `var(--cor)` (a cor do passo) **não pode ficar numa variável de tema**: `--cor` só existe dentro de cada bilhete. Por isso os temas passam *parâmetros* (`--cabecalho-tinta`, `--anel-tinta`, `--insignia-luz`…) e a base é que os junta à cor do passo.
- `src/temas.ts` regista o `id`, o nome (próprio, não se traduz) e a descrição (vai no `title` da opção).
- O Biome não lê `.scss`: o que garante os estilos é a compilação do Sass (`pnpm build`) e o teste dos temas.

### Variáveis principais

| Grupo | Variáveis |
|---|---|
| Cores | `--fundo --cartao --texto --suave --linha --campo --destaque --destaque-2 --ok --aviso --erro --sombra-cor --passo-1…4` |
| Letra | `--fonte --fonte-titulo --fonte-marca --peso-titulo --peso-marca --peso-numero --fonte-numero --ligaduras --brilho-titulo --brilho-botao` |
| Raios e sombras | `--raio --raio-c --entalhe --filtro-coluna --sombra-visor` |
| Faixa e página | `--banda --banda-forma --banda-mascara --banda-borda --banda-mistura --banda-animacao --banda-desliza --deco-pagina --deco-pagina-opacidade --deco-pagina-animacao --deco-pagina-desliza` |
| Cabeçalho | `--topo-texto --topo-sombra --marca-anel --pilula --pilula-texto --pilula-anel --nav-ativo --nav-ativo-texto` |
| Botões e campos | `--botao-1 --botao-2 --botao-texto --botao-borda-cor --botao-anel --botao-sombra --botao-sombra-hover --botao-sec-sombra --botao-hover --botao-ativo --entrega-1 --entrega-2 --campo-anel --campo-anel-foco` |
| O bilhete | `--faixa-topo --faixa-topo-altura --anel-largura --anel-tinta --anel-cor --cartao-anel-extra --picotado-estilo --cabecalho-* --insignia-* --numero-pct --numero-sombra --zona-estilo --modo-ativo-*` |
| Progresso, visor, diálogo | `--progresso-raio --progresso-fundo --progresso-barra --visor-barra --visor-anel --dialogo-sombra --dialogo-topo` |

## Receita: um tema novo

1. **`src/estilos/temas/_<id>.scss`**: `@use "../tema" as *;` e `@include tema(<id>) { … }` com as variáveis; começa por um comentário de 2–3 linhas com a ideia. Define claro **e** escuro com `light-dark()`.
2. **Regista-o** em `src/temas.ts` e junta `@forward "<id>";` a `src/estilos/temas/_index.scss` (um teste verifica as duas coisas).
3. **Letras**: só se forem necessárias, de `@fontsource` / `@fontsource-variable`, **versão exata** (`pnpm add -E …`), importadas em `src/main.tsx`. O browser só descarrega as que o tema usa. Mantém um *fallback* de sistema.
4. **Falta uma variável?** Junta-a a `_tokens.scss` com o valor do Premiado e usa-a na base (nas regras de `_base`, `_gerador`…). Nunca resolvas isso no tema com `padding`/`margin`: o teste não deixa.
5. **Vê-o a sério**: `pnpm build`, `python -m src.web`, carrega os ficheiros de `tests/fixtures/`, e olha para o ecrã principal, o tutorial e um diálogo, em claro e escuro, em largo e em telemóvel (390 px). Junta capturas ao PR.
6. **Acessibilidade**: texto com contraste suficiente (≥ 4,5:1; ≥ 3:1 para texto grande e ícones) — **mede-se**: `pnpm build && pnpm e2e -g contraste` corre o teste `e2e/contraste.spec.ts` nos 9 temas em claro e escuro e diz o que não passa; foco visível (`:focus-visible` usa `--destaque-2`), nada essencial só em cor. Movimento só discreto: a base respeita `prefers-reduced-motion`.

## Limites conhecidos

- O contraste está **medido** (`e2e/contraste.spec.ts`, WCAG AA) no ecrã principal (com a galeria aberta), no sorteio, no tutorial e nos termos, em claro e escuro. Não cobre o que só aparece depois de uma ação (diálogos, erros, o estado «a gerar»), o foco nem o *hover*, e isenta os controlos desativados (como o WCAG). O axe-core **não serve** aqui: marca como «incompleto» todo o texto sobre gradientes e padrões (medido: só avaliava 2 elementos em 16 das 18 combinações), por isso o teste mede o texto contra os pixéis reais do fundo (`e2e/ajuda-contraste.ts`).
- Os nomes dos temas não estão traduzidos (são nomes próprios); o rótulo do seletor («Estilo») está nas 18 línguas.
- O PDF.js do browser (visor) mantém sempre o seu aspeto, em qualquer tema.
