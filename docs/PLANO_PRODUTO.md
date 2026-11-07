# Plano de produto: novas funcionalidades e monetização

Escrito para o dono do projeto. Os números de preços são **hipóteses para testar**, não factos; o que foi confirmado na internet leva a fonte, e o que **não** foi confirmado está marcado com «⚠ confirmar».

## 1. Ponto de partida

- **O que existe:** uma webapp pública e sem contas que gera as rifas numeradas a partir de um template do Canva (template + algarismos → pré-visualização → PDF/ZIP), em 18 línguas e 9 temas, com painel de métricas (`/admin`), e a app Windows com o mesmo motor.
- **O que já é um ponto forte:** é rápido, não pede registo, e **apaga os ficheiros em 30 minutos** (bom argumento de privacidade para associações e escolas).
- **O que limita o negócio hoje** (`docs/ONLINE.md`, `docs/ADMIN.md`): o Render gratuito adormece, não tem disco persistente, só tem 750 horas por mês, e o próprio Render diz para **não o usar em produção**. Um serviço que cobra dinheiro não pode viver aí.

### Custos de funcionar a sério (Render, [render.com/pricing](https://render.com/pricing), consultado em 2026-11-07)

| Opção | Custo | Para quê |
|---|---|---|
| Gratuito | 0 | hoje; adormece; sem disco persistente |
| **Starter** (0,5 CPU, 512 MB) | **7 $/mês** | nunca adormece; mesma memória que agora |
| 1 CPU, 2 GB | 25 $/mês | gerações grandes e vários utilizadores em simultâneo |
| Disco persistente | 0,25 $/GB/mês | métricas e, mais tarde, contas e histórico |

## 2. Quem paga e porquê

A necessidade é **sazonal e pontual**: Natal, Santos Populares, festas de aldeia, fim de ano escolar, angariações de associações. Por isso o produto casa melhor com **pagar por evento** do que com uma subscrição mensal.

| Segmento | Dor | Disposição a pagar |
|---|---|---|
| Associações, IPSS, comissões de festas, pais de escolas | numerar à mão centenas de bilhetes; erros e repetidos | baixa por evento, mas repetem todos os anos |
| Pequenos comércios e clubes (sorteios de campanha) | imagem profissional, números únicos | média |
| Gráficas e serviços de impressão | produzir rifas para clientes | **a mais alta**: usam em volume |
| Particulares (rifa de Natal, aniversário) | simplicidade | muito baixa: ficam no gratuito |

## 3. Funcionalidades

Ordenadas por **valor ÷ esforço**. Tamanhos: XS = uma tarde, S = um dia, M = uns dias, L = semanas, XL = um mês ou mais. Cada linha é um PR (ver `CONTRIBUTING.md`).

### A. Tirar fricção (fazer primeiro, são grátis para todos e trazem gente)

| Funcionalidade | Tam. | Porquê |
|---|---|---|
| Lembrar o ficheiro dos algarismos e o último pedido no browser | S | quem volta todos os anos não repete o trabalho |
| **Galeria de templates prontos** (para quem não sabe fazer no Canva) | M | hoje o maior obstáculo é o passo do Canva; muitos desistem aí |
| **Séries e prefixos** (A-0001, B-0001), saltar números, cor por série | S | pedido típico de rifas com vários prémios |
| **Exportar a lista de números** em CSV/Excel + **folha de controlo de vendas** imprimível | M | quem vende precisa de saber quem tem que número |
| **Talão e canhoto** (numeração dupla) e marcas de corte/sangria | M | rifas físicas a sério; diferencia de um gerador genérico |
| QR por bilhete (verificação do número no dia do sorteio) | M | confiança; abre a porta a funcionalidades pagas |
| Instalar como app (PWA) e vista de telemóvel afinada | S | já há ícone e manifesto |

### B. Valor que se pode cobrar

| Funcionalidade | Tam. | Porquê |
|---|---|---|
| **Sorteio verificável** (semente pública, registo do resultado, página para partilhar) | M | no dia do sorteio toda a gente quer «ver que foi justo»; os concorrentes (Funraise, RallyUp) têm geradores de sorteio |
| **Contas e histórico** (guardar rifas, duplicar a do ano passado) | L | é a base de qualquer plano pago e de disco persistente |
| **API e geração em lote** para gráficas | M | o segmento que mais paga |
| Logótipo e cores da associação em todas as rifas (marca própria) | M | associações gostam de se ver |
| Mais volume por pedido (acima dos 30 000 números) e prioridade de fila | M | custa CPU: é natural cobrar |
| **Funil no painel** (sessão → template → pré-visualização → geração → descarga) | S | os eventos já existem; mostra onde se perdem as pessoas e valida cada experiência de preço |

### C. A explorar (maior risco ou esforço)

| Funcionalidade | Tam. | Nota |
|---|---|---|
| Editor de templates no próprio site (sem Canva) | XL | reduz a dependência do Canva (se o Canva mudar o PDF, o motor tem de se adaptar); mas é um produto novo |
| Página pública da rifa com reserva/pagamento de números online | XL | **evitar até haver parecer jurídico** (ver 5): passa de «gerar bilhetes» a «operar a rifa» |
| Integração com serviços de impressão (comissão por encomenda) | M | receita sem custo para o utilizador; depende de parceiros |

## 4. Monetização

### Princípios

1. **O essencial fica grátis** (gerar as rifas de uma associação pequena): é o que traz pesquisa, boca-a-boca e confiança.
2. **Cobrar por volume e por conforto**, não por bloquear: mais números, guardar/duplicar, marca própria, API, sorteio verificável.
3. **Sem marca-de-água nos bilhetes**: o produto é impresso e vendido; uma marca-de-água estraga-o e empurra as pessoas para a concorrência.
4. Preço **pequeno e claro**, por evento: combina com uma necessidade que aparece duas ou três vezes por ano.

### Modelos candidatos

| # | Modelo | Como seria | Prós | Contras |
|---|---|---|---|---|
| 1 | **Donativo** («oferece-me um café», MB Way/PayPal) | botão depois de uma geração com sucesso | zero fricção; começa no dia 1; mede a boa vontade | receita baixa e incerta |
| 2 | **Packs pré-pagos, sem conta** | p.ex. 4,90 € = 5 000 números durante 30 dias; 9,90 € = 30 000. Pagamento → um código/link por e-mail | casa com a sazonalidade; sem contas; fácil de explicar | o grátis tem de ter um teto claro (p.ex. 500 números por dia por pessoa) |
| 3 | **Plano anual «Associação»** | p.ex. 19 €/ano: uso generoso, guardar e duplicar rifas, marca própria, suporte | receita previsível; fideliza as que repetem todos os anos | precisa de contas e histórico (L) |
| 4 | **B2B para gráficas** | API/lote, mensal ou por volume | o cliente que mais paga | vendas diretas; suporte |
| 5 | **Comissões** de gráficas parceiras | link «imprimir estas rifas» | grátis para o utilizador | depende de acordos |

**Recomendação por fases:**
- **Fase 0 (agora, sem contas):** donativo + passar para o **plano pago do Render** (7 $/mês) + monitor externo. Medir com o painel quantas gerações, de que tamanho e em que época.
- **Fase 1 (1–2 meses):** packs pré-pagos com **Stripe Checkout** (sem contas). O grátis passa a ter um teto diário por IP (o limite já existe; basta mostrar a mensagem de compra).
- **Fase 2 (3+ meses):** contas, histórico e plano anual; piloto com uma ou duas gráficas.

### Contas simples (hipóteses a validar, com os custos reais)

| Custo mensal fixo | Quantos packs de 4,90 € pagam | Quantos de 9,90 € |
|---|---|---|
| Render Starter 7 $ (≈ 6,5 €) + domínio (≈ 1 €) ≈ **7,5 €** | ≈ **2** | ≈ 1 |
| Render 1 CPU/2 GB 25 $ (≈ 23 €) + domínio ≈ **24 €** | ≈ **6** | ≈ 3 |

Taxas do Stripe em Portugal: **1,5 % + 0,25 € por cartão da UE** e 3,25 % + 0,25 € por cartão internacional (+ 2 % se houver conversão de moeda), segundo uma fonte secundária (Studio Ninja); **⚠ confirmar em stripe.com/pt/pricing**. Num pack de 4,90 €: ≈ 0,32 € de taxa (6,6 %), ficam ≈ 4,58 €. Câmbio 1 $ ≈ 0,92 € é uma suposição.

O **ponto de equilíbrio é baixo** (poucos packs por mês). A questão não é cobrir a infraestrutura, é haver **procura**: por isso as fases 0 e 1 são pequenas e medem antes de investir nas contas.

### Pagamentos em Portugal

Stripe (cartões, Apple/Google Pay) é o mais rápido de integrar. Muita gente em Portugal prefere **MB Way e Multibanco**: **⚠ confirmar** se o Stripe os oferece à tua conta, ou usar um agregador português (p.ex. ifthenpay, Easypay: **⚠ confirmar tarifas**). Oferecer MB Way pode ser a diferença entre vender e não vender a associações.

## 5. Legal, fiscal e privacidade (⚠ tudo a confirmar com um contabilista e um advogado)

- **Rifas e a lei.** O enquadramento das rifas em Portugal (licenças das câmaras municipais, regras para associações, fronteira com o jogo) **não foi verificado aqui**. A pesquisa encontrou o Decreto-Lei n.º 310/2002, que dá às câmaras o licenciamento de várias atividades (leilões, venda ambulante de lotaria da Santa Casa, espetáculos…), mas **o excerto lido não diz que cubra as rifas**. **Pede um parecer** antes de qualquer funcionalidade que venda ou reserve números online. Os *Termos* devem dizer que **quem organiza a rifa é responsável por cumprir a lei**, e que esta ferramenta **só gera bilhetes** (não vende, não recebe dinheiro, não faz o sorteio).
- **Atividade e faturação:** abrir atividade nas Finanças, faturação certificada, IVA em serviços digitais a particulares (e regras de vendas a outros países da UE). **⚠ confirmar com o contabilista**, incluindo se te enquadras num regime de isenção.
- **RGPD:** política de privacidade (que dados se guardam: nenhuns pessoais nas métricas; ficheiros apagados em 30 minutos), base legal, contacto. Quem paga fornece e-mail e dados de faturação: passam a ser dados pessoais.
- **Livro de Reclamações Eletrónico** (obrigatório para prestadores de serviços em Portugal) e **Termos e Condições**. **⚠ confirmar** o que se aplica a um serviço digital pequeno.
- **Licenças do código:** o motor usa pypdf, PDFium e Pillow (licenças permissivas); confirmar a lista final antes de cobrar.

## 6. Como medir (já tens o painel)

- **Funil:** sessões → template carregado → pré-visualização → geração concluída → descarga. Onde cai mais é onde trabalhar (a galeria de templates ataca o 1.º degrau).
- **Procura por tamanho:** quantas gerações passam de 500 / 5 000 / 30 000 números: diz que packs fazem sentido e se o teto de 30 000 está certo.
- **Sazonalidade:** sessões por semana: Natal, Santos Populares, junho.
- **Quem usa o quê:** língua, tema, ecrã (os dispositivos mostram se vale a pena investir mais no telemóvel).
- **Experiências de preço:** mostrar o botão de donativo/pack depois de uma geração bem-sucedida e contar cliques (um evento novo, só códigos e números).

## 7. Calendário sugerido (90 dias)

| Quando | O que | Quem |
|---|---|---|
| Semana 1 | Render pago (7 $/mês), domínio próprio (`PUBLIC_URL`), monitor externo, `ADMIN_TOKEN`, Search Console | **tu** |
| Semanas 1–2 | Páginas de Termos, Privacidade e contacto; botão de donativo; parecer jurídico sobre rifas | tu (+ contabilista/advogado), eu nas páginas |
| Semanas 2–4 | A: guardar o último pedido, séries/prefixos, exportar CSV, galeria de templates (3 a 5 templates) | eu (PRs pequenos) |
| Mês 2 | Stripe Checkout + packs; teto diário do grátis; funil no painel | eu |
| Mês 3 | Contas, histórico, plano anual; piloto com 1–2 gráficas | eu + tu (vendas) |

## 8. Riscos

- **Dependência do Canva:** o motor lê o PDF exportado do Canva; se o Canva mudar a forma como exporta, é preciso adaptar (há testes com PDFs reais em `app/testes/`).
- **Sazonalidade:** a receita concentra-se em poucas semanas; o plano pago de infraestrutura é um custo fixo todo o ano.
- **Abuso do grátis:** o limite por IP e o teto de números já existem; o painel mostra se o limite funciona (ver «Proxy e limite por IP»).
- **Suporte:** cobrar traz pedidos de suporte e de reembolso: ter uma política clara de reembolso nos Termos.
- **Tentação de operar a rifa:** passar de «gerar bilhetes» a «vender números» muda o risco legal e fiscal: só com parecer.

## 9. O que preciso que decidas

1. **Público-alvo principal** (associações/escolas ou gráficas) e se queres vender já em Portugal ou também noutros países (afeta IVA e línguas).
2. **Fase 0 já?** Passar para o Render pago e pôr o donativo.
3. **Preços** de partida para os packs (os de cima são só um ponto de partida).
4. **Quem emite faturas** (nome, atividade, IVA) e **o nome/domínio** final do produto.
5. Se queres que avance com a **galeria de templates** (a maior alavanca de crescimento) antes das funcionalidades pagas.
