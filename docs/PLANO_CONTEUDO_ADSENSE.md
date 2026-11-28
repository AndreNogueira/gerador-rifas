# Conteúdo para passar a revisão da Google AdSense (por rever)

A Google recusou a candidatura ao AdSense por falta de conteúdo («pouco conteúdo original e útil»). Este documento propõe o que acrescentar — texto, ferramentas e páginas — para lá chegar, e que *plugins*/*skills* do Claude Code ajudam a construir cada peça. Cruza com [`ADSENSE.md`](ADSENSE.md) (passo 5: «se recusarem por pouco conteúdo, acrescenta páginas de como fazer») e [`ROADMAP.md`](ROADMAP.md) (#5). **Nada daqui está implementado — é a lista a priorizar e a confirmar antes de abrir PRs.**

## 0. Antes de tudo: fechar o buraco que já existe

O re-audit SEO de 2026-11-28 (depois de fundidas as reescritas de escolas/bombeiros/clubes/festas) encontrou que **`/rifas-para-associacoes` nunca foi reescrito**: o ficheiro é do PR #44 (v3.30.0), de antes de todo este esforço de diferenciação, e continua genérico — mais curto que os irmãos e a nomear os outros 5 públicos no próprio texto. É exatamente o tipo de página que motivou a recusa da Google. **Isto devia ser o próximo PR, independente de qualquer ideia nova abaixo** — mesmo padrão das reescritas já feitas (escolas, bombeiros, clubes, festas, igrejas): falar da realidade real de uma associação (direção eleita, quotas de sócios, assembleia geral, estatutos), não do genérico «rifa para a sua organização».

Achado secundário, sem urgência mas a decidir: o JSON-LD `Organization` publica o `contactPoint.email` do dono em toda a página pública. É um sinal de E-E-A-T legítimo (contacto real = confiança), mas é o endereço pessoal — vale a pena confirmar que é essa a intenção antes de continuar a publicá-lo.

## 1. Ideias de conteúdo original (não só "mais páginas de como fazer")

Ordenadas por originalidade/dificuldade de copiar — o critério real da Google não é "quantidade de texto", é "ninguém mais tem isto, e é útil".

| # | Ideia | Porque é original (não templada) | Tam. | *Skills* que ajudam |
|---|---|---|---|---|
| 1 | **FAQ construído a partir de comentários reais** (`/comentarios` já existe, guarda texto + país, o dono vê tudo em `/admin`) | Não é texto inventado "do género FAQ" — são perguntas que utilizadores reais desta ferramenta já fizeram. Sinal de "Experience" (o E do E-E-A-T) que nenhum concorrente pode imitar sem ter o próprio histórico de utilizadores. `FAQPage` schema. | S | `design:research-synthesis` (sintetizar os comentários em perguntas/respostas sem copiar texto de visitante nenhum à letra — a política de privacidade já promete nunca publicar o texto de um comentário tal como está) |
| 2 | **Calculadora de rentabilidade da rifa** (preço do bilhete × quantidade vendida − custo dos prémios e impressão = lucro; sugere preço e quantidade) | É uma ferramenta, não texto — a Google não consegue "templar" um cálculo. Serve a dor real de quem organiza (quanto cobrar, quantos bilhetes fazer) e já existem as peças: `core/moeda.py` para a moeda por país, o guia `/quantos-bilhetes-de-rifa-fazer` para a lógica. | S/M | nenhuma externa — é código do próprio stack (React + `core.moeda`) |
| 3 | **Glossário dos termos da rifa** (série, talão, sangria, folha de controlo, sorteio verificável…) | Conteúdo de referência genuíno, link interno natural para todos os guias e para o tutorial; capta long-tail ("o que é uma série numa rifa"). Fácil de escrever bem porque os termos já estão todos definidos neste `CLAUDE.md` e no código. | S | `zizi-skills:plain-language` (garantir que cada definição é mesmo clara para um leigo, não jargão) |
| 4 | **Exemplo real resolvido**: um caso completo com números a sério ("rifa de Natal para 200 alunos: X bilhetes a Y€, prémio Z, resultado") | Conteúdo de "worked example", categoria que a Google trata bem (prova prática, não teoria); diferente em formato dos guias "como fazer" — não arrisca parecer mais do mesmo. | S | `social-media-skills:data-and-original-research` (desenhar o exemplo com números coerentes e realistas) |
| 5 | **Comparação**: rifa vs. outras formas de angariação de fundos (venda de bolos, crowdfunding, quotas extra) | Formato de "decisão" que a Google também recompensa, e nenhum guia atual tem esta forma — ajuda quem ainda não decidiu que é isto que quer fazer. | S | `marketing:competitive-brief` (adaptado: comparação de métodos, não de concorrentes) |
| 6 | **Checklist descarregável** ("o que preparar, do início ao sorteio") em PDF, ligado ao rodapé dos guias | Conteúdo-isco (lead magnet) genuíno: ficheiro próprio, não só HTML; dá vontade de voltar à página para o descarregar outra vez. Reutiliza o motor de PDF que já existe (`core.editor`/`reportlab`, já usado no preçário e nas etiquetas). | S/M | nenhuma externa |
| 7 | **Guias por público que ainda faltam**: misericórdias, IPSS, juntas de freguesia, ranchos folclóricos, equipas amadoras — já nomeados em `ROADMAP.md` #5 como "a fazer" | Expande a cobertura real (são públicos genuinamente diferentes: lógica de autarquia local é diferente da de uma escola), mas **só se cada um tiver mesmo uma voz própria** — repetir o erro do `associacoes.py` antigo (texto quase igual aos outros) é o cenário que a Google já penalizou uma vez. | M (cada) | `claude-seo:seo-content-brief` (escrever o briefing de diferenciação ANTES do texto, para cada guia novo, evitando repetir o que já saiu nos outros 6) |
| 8 | **Infográfico "como funciona uma rifa verificável"** (visual, não só texto) — o sorteio já é verificável (`core/sorteio.py`, QR de cada bilhete); mostrar visualmente o processo | Conteúdo visual original é um sinal forte de investimento editorial a sério, e distingue a página de concorrentes que só têm texto. | S/M | `dataviz` skill (desenhar o diagrama com o mesmo sistema de cores/tema do site) |

## 2. O que NÃO fazer

- **Não multiplicar guias por público só para ter mais páginas.** A lição desta sessão (associações) é precisamente essa: uma página "como fazer" sem voz própria conta como conteúdo fraco mesmo que exista. Cada guia novo (item 7) só deve avançar com um briefing de diferenciação escrito primeiro.
- **Não inventar números legais ou específicos de licenciamento por município** — contraria a regra já assumida no projeto («a lei varia, nada se afirma»; CLAUDE.md, secção SEO). As ideias acima evitam esse território de propósito.
- **Não gerar conteúdo em massa com IA sem revisão humana da voz** — é exatamente o padrão que a Google procura detetar; cada peça nova devia continuar a passar pelo mesmo cuidado que os guias reescritos (voz própria, exemplos concretos, nada de frases intercambiáveis entre páginas).

## 3. Ordem sugerida

1. Fechar `rifas-para-associacoes` (secção 0) — antes de tudo, é o buraco que já foi assinalado.
2. FAQ de comentários reais (#1) + Glossário (#3) — mais baratos, mais sinal de autoridade/E-E-A-T, zero risco de parecer templado.
3. Calculadora de rentabilidade (#2) — ferramenta, o tipo de conteúdo mais difícil de copiar.
4. Exemplo resolvido (#4) + Comparação (#5).
5. Checklist PDF (#6) + infográfico (#8).
6. Só depois, e com cuidado (briefing primeiro), os guias por público que faltam (#7).

Cada item vira o seu próprio PR pequeno, como sempre (`CLAUDE.md`, fluxo de PRs).
