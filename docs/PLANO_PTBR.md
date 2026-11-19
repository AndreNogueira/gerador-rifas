# Plano: português do Brasil (`pt-BR`) como 23.ª língua

> **Estado (2026-11-19): feito na 3.69.0** (derivado do pt por `core/ptbr.py`; ver `docs/LINGUAS.md`). Por fazer: revisão por brasileiros, revisão jurídica das páginas legais, guias com exemplos próprios do Brasil (festa junina, condomínio…) e a decisão sobre a lei das rifas (ponto 1 abaixo).

## Porquê

- O português do site é **de Portugal** (ecrã, ficheiro, descarregar, utilizador, talão, câmara municipal). Quem pesquisa no Brasil escreve outras palavras («arquivo», «baixar», «usuário», «canhoto», «prefeitura») e o Google serve-lhe páginas em `pt-BR`.
- A «rifa» é uma prática muito corrente no Brasil (rifas beneficentes, de escola, de igreja, de condomínio, de festa junina) e o público é várias vezes o de Portugal. É a língua nova com **mais visitas potenciais por esforço**, porque o texto parte do português que já existe.
- Tudo o que se fizer a seguir (guias, preçário com `R$`) passa a ter uma versão brasileira «de graça» se a infraestrutura estiver feita.

## O que muda (por ordem do `docs/LINGUAS.md`)

| # | Peça | Como | Tam. |
|---|---|---|---|
| 1 | **Língua nova** `pt-BR` (código de URL `pt-br`, `hreflang="pt-BR"`, `og:locale pt_BR`) | `idiomas/pt_br.py` com **todas** as chaves; registo em `idiomas/__init__.py`, `rota.tsx` (`LINGUAS_COM_PREFIXO`), `e2e/capturas.spec.ts`; contagens 22 → 23 nos testes e nos textos «N línguas». O português de Portugal continua **sem prefixo** (`/tutorial`), o brasileiro em `/pt-br/tutorial`. | M |
| 2 | **Texto da interface** (≈ 1 300 chaves, tutorial incluído) | Não se traduz à mão: um script `scripts/derivar_ptbr.py` parte do `pt` e aplica um **glossário** (ecrã→tela, ficheiro→arquivo, descarregar→baixar, utilizador→usuário, rato→mouse, telemóvel→celular, talão→canhoto, câmara municipal→prefeitura, a gente/você, gerúndio…); eu reviso à mão o que o glossário não apanha e um **teste proíbe** palavras de Portugal no `pt_br.py` (lista negra). | M |
| 3 | **Páginas legais** (Termos, Privacidade, Contacto) | **Não é cópia:** o Brasil tem a **LGPD** (não o RGPD), outras autoridades e outro direito do consumidor. Adapto as referências e o aviso («sem revisão jurídica»), e **recomendo que um jurista brasileiro as reveja** antes de divulgar. | M |
| 4 | **SEO e guias** | Títulos/descrições `pt-BR` (≤ 66 / 50–158), e os 9 guias **adaptados ao Brasil** (prefeitura, condomínio, festa junina, igreja, escola…) e não só trocados de palavras. Entram em `guias/novas.py`/módulos e no sitemap (23 línguas × páginas). | M |
| 5 | **Changelog** | Um resumo `pt-BR` por versão (tal como as outras línguas; derivado do pt com o glossário). | S |
| 6 | **Moeda e datas** (para o preçário e o calendário) | `R$ 1.234,56`, `dd/mm/aaaa`, primeiro dia da semana domingo: vêm do `Intl` no site e da tabela de `moeda.py` no PDF. | S |
| 7 | **Capturas e vídeos** | Capturas do tutorial na língua nova; os vídeos continuam só em pt e en (o pt-BR usa os pt). | S |
| 8 | **Letras e galeria** | Sem problema: latim com acentos (Vera). | — |

## Decisões que preciso de si

1. **A lei das rifas no Brasil é mais restritiva e complexa do que em Portugal** (autorização, tipos de sorteio, regras federais e locais). Eu **não afirmo nada** sobre a lei (como nos guias de Portugal: o 1.º passo manda confirmar com a autoridade competente), mas **é um risco de reputação**: peço-lhe que confirme, com uma fonte brasileira, que o site pode ser apresentado a quem organiza rifas lá e como quer redigir o aviso. Se preferir, o pt-BR pode abrir só com o gerador e o sorteio verificável, e os guias de rifas ficam para depois.
2. **Quem revê o texto?** Sem falante nativo o risco é soar a «português de Portugal com palavras trocadas». Idealmente uma pessoa brasileira lê a interface (1 h) e as páginas legais (jurista).
3. **Prefixo do URL:** `/pt-br/` (recomendado, igual às outras línguas) ou usar um domínio `.com.br` mais tarde (não depende deste plano).
4. **Antes ou depois do preçário?** Recomendo **antes**: é pequeno (≈ 1–2 dias), tudo o que se fizer depois (guias, preçário, moedas) já nasce nas 23 línguas, e a procura no Brasil é grande.

## Riscos

- **Conteúdo quase duplicado** `pt` vs `pt-BR`: o `hreflang` existe exatamente para isto, mas os guias têm de ser **adaptados** (exemplos, vocabulário, ocasiões), não clonados; o Google trata como páginas diferentes quando servem públicos diferentes.
- **Custo contínuo:** cada funcionalidade nova passa a ter 23 traduções; o `derivar_ptbr.py` reduz o custo da nova a uma execução + revisão do que o glossário não cobre.
- **App Windows:** a língua entra na lista (`core.i18n.LINGUAS`) sem mais trabalho (a escolha segue a língua do Windows: `pt-BR` → `pt-BR`); o `.exe` só se reconstrói quando o dono decidir publicar.

## Depois de lançado

- Search Console: a mesma propriedade (os endereços `/pt-br/` entram no sitemap); ver «Segmentação internacional» passado um mês.
- Bing: o IndexNow (`docs/SEO.md`) já avisa as páginas novas a cada versão.
- Divulgação no Brasil só depois da revisão nativa e da decisão sobre a lei (ponto 1).
