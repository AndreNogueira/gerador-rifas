# Plano: gerador de preçários para festas

> **Estado (2026-11-19): aprovado pelo dono com estas decisões** (as recomendações seguem-se; o pt-BR já está feito na 3.69.0) e em execução pela ordem das fases abaixo. A ideia: o utilizador escolhe os artigos de uma lista extensa nossa (com imagens e temas ligados às épocas do ano), escreve os preços na moeda do seu **país** (ou numa moeda inventada) e sai um preçário pronto a imprimir, na webapp **e** na app Windows (que é também onde se valida o resultado).
> Ideia do dono: o utilizador escolhe os artigos de uma lista extensa nossa (com imagens e temas ligados às épocas do ano), escreve os preços na moeda que quiser
> (por omissão a da língua do site, ou uma moeda inventada) e sai um preçário pronto a imprimir. Na webapp **e** na app Windows.

## 1. Porquê encaixa bem neste projeto

- **Mesmo público.** Quem organiza uma rifa para uma festa de associação, escola ou bombeiros também precisa do preçário do bar, da tasquinha ou do arraial. Os guias de rifas já falam destas festas.
- **Já temos 80 % da base.** Os 24 desenhos da galeria (Santos Populares, Natal, Halloween, Magusto, Páscoa, Carnaval, Praia…) com cores e motivos desenhados em código (`core/galeria_enfeites.py`), o reportlab, as letras que cobrem as 22 línguas (`core/letras.py`), a pré-visualização em PNG desenhada no processo do motor, o padrão «rota sem sessão» (`rotas_listas.py`) e o padrão de janela da app Windows (`app/extras.py`).
- **SEO novo e com procura real.** «Preçário para imprimir», «lista de preços para festa», «ementa para arraial/tasquinha» são pesquisas concretas que hoje o site não apanha. Uma página própria (`/precario`) mais 1–2 guias com utilidade própria.
- **Sem contas, sem guardar nada.** Como a galeria: os textos só entram no PDF que se desenha.

## 2. O que o utilizador vê (fluxo)

1. **Ocasião e tema.** Cartões com os temas (reutilizam os 24 desenhos); o da época aparece primeiro e destacado («Agora: Santos Populares» em junho, Natal em dezembro, Magusto em novembro). Cada ocasião traz uma **lista pré-selecionada** (p. ex. Arraial: sardinhas, bifana, caldo verde, sangria, cerveja…) que se pode alterar.
2. **Artigos.** Catálogo por categorias (bebidas, comida salgada, doces, sobremesas, jogos e atividades, extras) com pesquisa e imagem em cada artigo; marcar/desmarcar; «acrescentar o meu artigo» (texto livre, com ou sem imagem do catálogo).
3. **Preços.** Tabela simples (artigo, preço), «mesmo preço para toda a categoria», e opcionalmente **dois tamanhos** (pequeno/grande) ou **combos**. A moeda vem escolhida pela língua; muda-se numa lista curta, ou escolhe-se **«moeda inventada»** (nome/símbolo, antes ou depois do número, 0/1/2 decimais: «fichas», «tostões», «bolotas»).
4. **Aspeto.** Título e subtítulo (nome da festa, data, local), formato (A5, A4, A3; vertical/horizontal), 1 ou 2 colunas, com/sem imagens, rodapé opcional («Perguntar por alergénios», «Preços com IVA» — texto livre, **nada se afirma por nós sobre a lei**, como nos guias).
5. **Pré-visualização a cada alteração** e **descarregar PDF** (e PNG para partilhar no WhatsApp).

## 3. Decisões que quero que reveja (com a minha recomendação)

| # | Decisão | Opções | Recomendação |
|---|---|---|---|
| D1 | **Imagens dos artigos** | (a) desenhá-las nós em código, como os enfeites; (b) usar um conjunto aberto de emojis/pictogramas (Noto Emoji, Apache 2.0 ou OFL; Twemoji pede atribuição); (c) misto | **(b)** para ter ~150 artigos já, no mesmo estilo; reservar (a) para os enfeites dos temas, onde já existe. **Antes de começar a fase 3 confirmo a licença exata do conjunto escolhido** e, se pedir atribuição, ponho-a no rodapé do PDF e na página «Acerca». |
| D2 | **Nomes dos artigos nas 22 línguas** | (a) as 22 desde o início (≈150 × 22 = 3 300 textos); (b) pt+en agora e as outras por fases, com recurso à língua do site → en → pt | **(a) por categorias**, mas sem bloquear o resto: o catálogo cai para en → pt enquanto falta. O texto livre do utilizador nunca precisa de tradução. As 4 línguas que não têm letra (hindi) saem em inglês como já acontece na folha de controlo. |
| D3 | **Moeda** | por língua / por país | **Por país** (decidido pelo dono): a língua só sugere o país de omissão (`pt`→PT, `pt-br`→BR, `en`→US…) e o browser afina-o pela região do `navigator.language` (`en-GB`→GBP, `es-MX`→MXN; nada vai ao servidor); o utilizador muda o país ou a moeda numa lista. Separadores e posição do símbolo seguem a **língua** do site. |
| D4 | **Sem sessão** | Preçário como rota «sem sessão» (campos → PDF), como a folha de controlo | **Sem sessão.** Rascunho no `localStorage` (`rifas.precario`), como o editor. Partilhar por ligação fica para depois (precisa de BD). |
| D5 | **Imagem do utilizador** (logótipo da associação, foto de um artigo) | já / depois | **Logótipo já** (reaproveita `core/marca.py`); fotos de artigos depois. |
| D6 | **pt-BR** | antes / depois do preçário | **Feito antes** (3.69.0): o catálogo tem itens de Portugal (bifana, caldo verde…) e do Brasil (coxinha, pão de queijo, quentão, pipoca…), mostrados conforme a língua. |

## 4. Desenho técnico

### 4.1 Núcleo (`src/core`, sem UI, partilhado pelas duas apps)

- **`moeda.py`** — a tabela das moedas (código ISO, símbolo, casas decimais) e dos **países** (código ISO → moeda), `moeda_do_pais(pais)`, `pais_por_omissao(lingua)` e `formatar(valor, moeda, lingua)`: o separador decimal e de milhares e o símbolo antes/depois seguem a língua («1,50 €», «€1.50», «R$ 1,50», «1,50 zł»). **Moeda inventada** = `{nome, posicao, decimais}` (validada nas letras do PDF). O valor guarda-se como **inteiro em milésimos** (nunca `float`: 0,10 + 0,20 não pode dar 0,30000001). Verificado: os símbolos das moedas das 23 línguas têm letra nas famílias que já embebemos (`letras.em_falta` devolve vazio; o ฿ tailandês não, mas não há tailandês).
- **`precario_catalogo.py`** — `Artigo(id, categoria, icone, nomes{lg})`, `Categoria`, `Ocasiao(id, desenho, artigos)`; funções `nome(artigo, lingua)` (com o recurso en → pt) e `sugestao_da_epoca(data)` (mês → tema). Dados em ficheiros «lado a lado» por categoria, como os guias.
- **`precario.py`** — o modelo `Precario` (título, subtítulo, desenho, formato, orientação, colunas, moeda, linhas, rodapé, logótipo opcional) e o **motor de disposição**: reparte as linhas por colunas e páginas, encolhe a letra até um mínimo legível e, se ainda não couber, passa a **2.ª página** (com aviso na interface). Usa `letras.fonte(texto)` por texto, nunca mistura famílias numa linha. Limites validados (n.º de linhas, tamanho dos textos) com `ErroRifas("err_precario_*")` traduzidos, como a galeria e o editor.
- **Imagens** em `core/icones_precario/*.png` (256 px, ~10 KB cada) geradas por `scripts/gerar_icones_precario.py` a partir do conjunto escolhido; a interface web usa uma folha de miniaturas `.webp` (como `public/galeria/`).
- **Temas**: cada desenho da galeria ganha uma função «cartaz» (moldura, faixa do título, divisores, cantos) que reaproveita os motivos que já existem em `galeria_enfeites.py` (`_ovo`, `_abobora`, `_coracao`, `_laco`, `_bandeirinhas`…). Sem motivos novos no 1.º PR.

### 4.2 Web (`src/web`)

- `rotas_precario.py` (prefixo `/api/precario`): `GET /catalogo` (na língua do pedido, cache público curto), `POST /previa.png` (desenhado no processo do motor, como `galeria_png`), `POST /pdf` e `/png` (descarga). Corpo em JSON, limites de pedido e de tamanho como em `rotas_listas.py`, `leve`/`pesado` conforme o custo.
- **Métricas só agregadas** (evento `precario`): tema, formato, nº de artigos em classes (1–5, 6–15, 16–40, 41+), código da moeda (ou `inventada`), com/sem imagens. **Nunca** títulos, nomes de artigos, preços nem o nome da moeda inventada; teste de privacidade como nos outros eventos.
- Frontend: `Precario.tsx` (+ `precario-modelo.ts`, `precario.scss`), página `/precario` em `seo.ROTAS` e `App.tsx`, entrada no menu «Ajuda»/«Extras» do cabeçalho (item novo = `ItemId` em `ORDEM`/`SAI_PRIMEIRO` **e** versão no menu hambúrguer, regra do `CLAUDE.md`), `sw.js` sem alterações (nada de `/api`).
- **Peso**: página preguiçosa (`preguicoso.ts`, `PARTES` em `verificar-dist.mjs`, `e2e/leve.spec.ts`) para não engordar o 1.º carregamento que acabámos de aligeirar.

### 4.3 App Windows (`app/`)

- Janela **«Preçário»** no menu «Extras» (`app/extras.py`, mesmo molde da `Galeria`): temas, lista com caixas, preços, moeda, pré-visualização PNG feita por `core`, «Guardar PDF…». O equivalente do rascunho é um ficheiro **`.precario`** (só os campos, sem logótipo, como o `.rifas`; `core/pedido_ficheiro.py` serve de modelo).
- A lógica fica toda em `src/core` (testável sem janelas); testes em `tests/test_windows_extras.py` e `app/testes/teste_extras.py`. O Nuitka tem de incluir `core/icones_precario/` (`--include-data-dir`) e o `--selftest` passa a gerar um preçário de exemplo.
- **Não publico o `.exe`** sem o seu «sim» (regra do `CLAUDE.md`).

### 4.4 Regras do projeto que isto obriga a cumprir

Funcionalidade de utilizador = **tópico no tutorial** (`FUNCIONALIDADES`, 22 línguas) + **vídeo web e Windows em pt e en** + **entrada no Changelog** (pt + 21) + chaves de interface nas 22 línguas (contagens em `tests/test_i18n.py` e `tests/test_web_api.py`) + Política de privacidade das 22 línguas atualizada se se guardar algo (aqui **não** se guarda nada além dos agregados).

## 5. Fases (cada uma = um PR, com testes e CI verde)

| Fase | Entrega | Tam. | Critério de «feito» |
|---|---|---|---|
| **0** | Esta página revista; decisões D1–D6 fechadas | — | O dono aprova ou corrige |
| **1** | `core/moeda.py` + testes | S | Todas as 22 línguas formatam bem (separadores, casas, símbolo antes/depois); inteiros em milésimos; moeda inventada; zero `float` |
| **2** | `core/precario_catalogo.py` com as ocasiões e **~150 artigos**, nomes nas 22 línguas, testes de integridade | M | Todo o artigo tem categoria, ícone e nome en+pt; nomes cabem nas letras (`em_falta`), ou têm o recurso en → pt |
| **3** | Ícones: script de geração, licença confirmada, `core/icones_precario/`, miniaturas `.webp`, linha na página «Acerca» se for preciso | M | PDF com as imagens a 300 dpi sem pixelização visível a 25 mm |
| **4** | `core/precario.py`: disposição (A5/A4/A3, 1–2 colunas, páginas), **cartaz do tema Quermesse** como primeiro caso e depois os outros 23 | L | Testes por língua e com 0/1/12/60 artigos, nomes longos, CJK; nenhuma linha corta o texto; PDF abre no PDFium |
| **5** | API web + métricas + teste de privacidade | S | `GET /catalogo`, `POST /previa.png`, `/pdf`; limites; evento sem texto |
| **6** | Página `/precario` (React: rascunho em `localStorage`, página preguiçosa, menu, país/moeda, acessibilidade) **e a janela «Preçário» da app Windows** (`app/extras.py`, `.precario`) no mesmo PR ou em dois seguidos; tutorial + vídeos (web e Windows, pt/en) + Changelog (pt + 21) + `CLAUDE.md`/`docs/`; e2e (contraste dos 14 temas) | L | Fluxo completo no telemóvel e no ecrã grande; `e2e/leve.spec.ts` verde; **`app\testes\teste_extras.py` e `--selftest` validam o mesmo preçário na app Windows** |
| **6b** ✅ | SEO e **guia do preçário**: `/precario` em `seo.ROTAS` + `d_precario` ×23, texto estático, **1 guia** (como preparar um preçário para a festa e definir os preços) com ligações cruzadas a `/como-fazer` e aos guias de rifas | M | Larguras de `test_web_seo_linguas`; sitemap atualizado; sem promessas de lei |
| **7** ✅ | **Vales de fichas numerados**: quando a «moeda inventada» são fichas, gerar os próprios vales com o motor das rifas (séries, QR de verificação): um vale por ficha, numerado, pronto a imprimir | M | Mesmo motor e mesmos limites das rifas; teste com séries e QR; validado na app Windows |
| **8** | **Extras**: fotos próprias dos artigos; 2 tamanhos e combos mais ricos; cartões de mesa (menus pequenos, 4 por folha); preçário em formato «quadro negro»; partilha por ligação (precisa de BD) | L | Cada extra é um PR pequeno, com os seus testes |
| **9** | **Anúncios** na página `/precario` **só onde `docs/ADSENSE.md` já os permite**; **nunca dentro da pré-visualização** do preçário nem do PDF | S | O mapa de anúncios de `docs/ADSENSE.md` atualizado; teste de que a pré-visualização não tem anúncios |

**Ordem de valor:** as fases 1–6 dão já o preçário na web e na app Windows; a 6b traz as visitas; 7–9 são os extras que o dono pediu. Posso entregar 1–3 antes de ver nada de visual, mas **a 4 pede-lhe um olhar** (o aspeto dos cartazes é o que decide se agrada).

## 6. Riscos e como os tratamos

- **Aspeto** (o risco principal): um cartaz feio mata a ideia. Mitigação: fase 4 começa por **um** tema, mostro-lhe o PDF/PNG e só então estendo aos 24.
- **Texto que não cabe** (nomes longos em alemão ou finlandês-like, CJK): encolher até um mínimo, depois 2.ª página; testes com os piores casos das 22 línguas.
- **Hindi/árabe/hebraico**: sem letra no PDF (já assim na galeria): os nomes saem em inglês e a interface avisa.
- **Tradução do catálogo** (3 300 textos): feita por mim, **sem falante nativo**; fica na lista «rever traduções» (como as `web_*`), e o recurso en → pt evita buracos.
- **Lei dos alimentos e dos preços** (alergénios, IVA, licença da festa): o site **não afirma nada**; o rodapé é texto livre do utilizador e o guia manda confirmar na câmara/autoridade local, como nos guias de rifas.
- **Conteúdo parecido em massa e o Google** (nota do agente lateral): poucas páginas novas, cada uma com utilidade própria (a ferramenta `/precario`, 1–2 guias de intenções diferentes); nada de uma página por artigo ou por tema.
- **Tamanho do `.exe` e da imagem Docker**: ~150 PNG × 10 KB ≈ 1,5 MB; aceitável.

## 7. Decisões já tomadas pelo dono (2026-11-19)

- Ordem: pt-BR → preçário (fases 1–6) → guia do preçário → vales de fichas (7) → extras (8) → anúncios (9). **A app Windows serve para validar** cada fase com lógica em `core`.
- Moeda **por país** (não só por língua) e `pt-BR` com `R$`; moeda inventada.
- Anúncios: só onde `docs/ADSENSE.md` já os permite; nunca dentro da pré-visualização do preçário.
