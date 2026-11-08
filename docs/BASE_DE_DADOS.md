# Base de dados: fornecedores gratuitos e recomendação

Escrito para o dono do projeto, que vai decidir. Pesquisado em **2026-11-08**. Os planos gratuitos mudam muitas vezes (o PlanetScale acabou com o seu, o CockroachDB parece ter acabado há semanas), por isso **os números são para confirmar na página oficial no dia em que criares a conta**. Onde as fontes se contradizem está marcado «⚠».

## 1. Para que serve a base de dados

Hoje não há base de dados a sério: as métricas do painel ficam num SQLite no disco do Render, que **é apagado** quando o serviço adormece ou é atualizado. Uma base externa resolve isso e é a **base de tudo o que é pago** (ver `PLANO_FEATURES.md`):

| Dado | Exemplo | Tamanho típico | Sensível? |
|---|---|---|---|
| Métricas agregadas | eventos, pedidos, amostras de sistema | poucos MB por mês | não (já não guardam nada pessoal) |
| Contas | e-mail, plano, preferências | KB por pessoa | **sim** (dados pessoais, RGPD) |
| Histórico de rifas | os campos do pedido (nunca os ficheiros) | KB por rifa | pouco |
| Packs e pagamentos | código, saldo, ID do pagamento no Stripe | KB | **sim** (faturação) |
| Sorteios verificáveis | semente, resultado, hora | KB | não |
| Chaves de API (gráficas) | hash da chave, limites | KB | sim |

**Conclusão: os dados são pequenos** (muito abaixo de 1 GB durante anos). O que decide **não é o tamanho**, é: (1) o plano **não expirar nem pausar**, (2) **região na UE** (o serviço está em Frankfurt e vamos guardar e-mails), (3) **ser relacional e transacional** (pagamentos e saldos precisam de transações), (4) ligar-se com **um só endereço** (`DATABASE_URL`) e (5) não ficar preso a um fornecedor.

Os ficheiros dos utilizadores (templates, PDFs) **continuam a não ir para a base** nem para disco: apagam-se em 30 minutos, é uma promessa do produto.

## 2. Critérios

| Critério | Porquê |
|---|---|
| Sem expiração nem pausa por inatividade | o serviço tem de acordar sempre com os dados |
| Região na UE (⚠ confirmar a lista de regiões de cada um) | latência a partir de Frankfurt e RGPD |
| SQL padrão (Postgres de preferência) | transações, migrações, sair para outro fornecedor sem reescrever |
| Ligação por URL + Python (`psycopg`) | um único segredo no Render, nada no repositório |
| Limites generosos para dados pequenos | cabemos muito dentro de qualquer plano |
| Cópias de segurança / restauro | contas e pagamentos não se podem perder |
| Risco de o gratuito mudar | todos mudam; interessa poder sair |

## 3. Comparação

| Fornecedor | Tipo | Limites gratuitos (resumo) | Expira / pausa? | Veredicto |
|---|---|---|---|---|
| **Neon** | Postgres | 1 GB por projeto, 100 horas de computação/mês, 5 GB de rede | **Não expira.** A computação suspende ao fim de 5 min sem uso e acorda no pedido seguinte | **Recomendado** |
| **Supabase** | Postgres + contas + ficheiros | 500 MB, 5 GB de rede, 2 projetos (⚠ uma fonte diz 500 MB de rede) | **Pausa após 7 dias sem atividade** e tem de ser reativado à mão | 2.ª escolha |
| **Turso** | SQLite distribuído (libSQL) | 100 bases, 5 GB (⚠ uma fonte diz 9 GB), 500 M leituras e 10 M escritas/mês | Não expira | Boa só para métricas/dados simples |
| **Aiven** | Postgres | 1 GB, 1 CPU, 20 ligações, sem cópias de segurança (⚠ uma fonte diz 5 GB) | Não tem prazo, mas **pode desligar serviços que não se usam** | Aceitável, mais limitado |
| **Render Postgres (gratuito)** | Postgres | 1 GB, 1 por conta | **Expira aos 30 dias** (14 de tolerância e depois apaga), sem cópias | **Evitar** |
| **TiDB Cloud Starter** | MySQL-compatível | 5 GiB por instância (⚠ páginas comerciais dizem 25 GiB), 50 M unidades de pedido/mês | Não expira; **abranda** ao chegar ao limite | Possível, menos comum em Python |
| **CockroachDB** | Postgres-compatível | era 10 GiB + 50 M unidades com um crédito de 15 $ | ⚠ **uma fonte diz que o plano foi retirado a 15-09-2026** | **Evitar** até haver certeza |
| **MongoDB Atlas (M0)** | Documentos (NoSQL) | 512 MB, ~100 operações/s | Pode terminar clusters parados | Não serve: os dados são relacionais |
| **Cloudflare D1** | SQLite | 5 GB, 5 M leituras e 100 mil escritas por dia | Sem prazo; **desde 01-09-2026 as consultas falham** ao passar o limite diário | Pensado para Workers: de fora, só por API |
| **Firebase Firestore** | Documentos (NoSQL) | 1 GiB, 50 mil leituras e 20 mil escritas/dia | Sem prazo | Prende ao Google; modelo não relacional |
| **Upstash Redis** | Chave-valor | 256 MB, 500 mil comandos/mês | Sem prazo | Bom para limites/filas, **não** para dados principais |

### Detalhe dos três candidatos sérios

**Neon (Postgres)**
- ✅ Não expira nem pausa: só «adormece» a computação (5 minutos) e acorda no pedido seguinte (cerca de meio segundo; ⚠ medir).
- ✅ Postgres a sério: transações, restrições, índices; migração para qualquer outro Postgres (Render, Supabase, Aiven, RDS) é só copiar.
- ✅ Um endereço `postgres://…` (um segredo só); tem ramos de base de dados (útil para testar migrações sem tocar nos dados reais) e **conector MCP** próprio.
- ✅ Tem regiões na UE (⚠ confirmar Frankfurt, a mesma do Render).
- ⚠ 1 GB e 100 horas de computação por mês: sobra (o painel e as contas são poucas operações), mas uma base sempre acordada gastaria as 100 horas em poucos dias; **na prática suspende ao fim de 5 minutos**, e o serviço só a toca quando há tráfego (por isso o anti-sono do serviço **não** deve tocar na base).
- ❌ O 1.º pedido depois de 5 minutos de silêncio é mais lento (acordar). Para o painel de métricas, que grava em *buffer*, é irrelevante; para um *login* é perceptível.
- ❌ Ao chegar a 1 GB as escritas **falham** (não cobra, mas para): é preciso vigiar.

**Supabase**
- ✅ Dá Postgres **e** autenticação (contas por e-mail, Google, etc.) **e** armazenamento de ficheiros: poupava escrever as contas à mão.
- ✅ Painel muito bom; tem conector MCP.
- ❌ **Pausa ao fim de 7 dias sem atividade** e é preciso reativar à mão: num serviço sazonal (rifas de Natal, junho) isto vai acontecer. Dá para contornar com um pedido semanal (o anti-sono do serviço já faz um *ping* de 10 em 10 minutos, mas esse chama o `/health`, que **não toca na base**: teria de passar a tocar).
- ❌ Fica-se mais preso ao Supabase se se usar a autenticação deles.
- ❌ 500 MB.

**Turso (SQLite distribuído)**
- ✅ Muito generoso nos limites (5 GB, 500 M leituras); não expira.
- ✅ Como as métricas **já usam SQLite**, a migração do `metricas.py` seria quase só mudar a ligação.
- ❌ SQLite/libSQL é menos adequado a **pagamentos e saldos** (menos tipos, concorrência de escrita limitada) e mais difícil de trocar por outro fornecedor depois.
- ❌ Preços e limites pagos pouco claros nas fontes (⚠).

## 4. Recomendação

**Neon (Postgres), numa região da UE**, por esta ordem de razões: não expira nem pausa, é Postgres padrão (podemos sair quando quisermos), os limites sobram para dados pequenos e tem conector. A **2.ª escolha é o Supabase** se, mais tarde, quiseres que ele trate das contas (mas é preciso resolver a pausa de 7 dias). O **Turso** só se quiseres manter tudo em SQLite (métricas) e adiares as contas.

**Plano de fuga** (porque o gratuito pode mudar): o código usa SQL padrão e um só `DATABASE_URL`; se o Neon mudar, passa-se para o Postgres do Render (pago; ⚠ ver o preço em render.com/pricing) ou para o Aiven copiando a base. Faz-se uma **cópia de segurança semanal** (`pg_dump` num *workflow* do GitHub Actions, cifrada, fora do Neon) antes de haver pagamentos.

## 5. Como ficaria ligado (sem segredos no repositório)

1. Crias a conta no Neon e o projeto (região na UE), e **copias o endereço de ligação**.
2. No Render, em *Environment*, defines **`DATABASE_URL`** (nunca vai para o Git nem para ficheiros; o `render.yaml` leva `sync: false`, como o `ADMIN_TOKEN`).
3. O serviço usa-a **só se existir**: sem `DATABASE_URL` continua como hoje (SQLite local), por isso testes e a app Windows não mudam.
4. As tabelas criam-se por **migrações** (ficheiros SQL numerados, um PR cada), e há testes que correm contra um Postgres de verdade no CI (contentor `postgres`), não contra uma imitação.
5. Primeiro PR: **métricas persistentes** (as de hoje passam a sobreviver ao adormecer), que é o menor risco e já resolve um problema real. Contas e pagamentos só depois.

## 6. Conectores (o que precisas de instalar)

Para **escrever o código** não preciso de nenhum: basta o `DATABASE_URL` no Render. Os conectores só servem para eu **ver e gerir** a base por ti (criar o projeto, ver tabelas, correr uma consulta de verificação). Se escolheres o **Neon**, instala o **conector do Neon**:

- no teu terminal, dentro do projeto: `npx neon@latest init` (abre o navegador para autorizares e configura o Claude Code), **ou** `claude mcp add --transport http neon https://mcp.neon.tech/mcp` (⚠ confirmar o comando na documentação do Neon no dia);
- começa em modo **só de leitura** se tiver essa opção: o conector pode alterar dados reais;
- eu **não consigo autorizar** isto nesta sessão (precisa do navegador): terás de o fazer tu.

O **Render** já tem conector (o plugin `render` está disponível): serve para eu confirmar variáveis e *logs* do serviço sem ires ao painel. **Stripe** (packs pagos) e outros só mais tarde; aviso quando chegarmos lá.

## 7. O que preciso que decidas

1. **Fornecedor**: Neon (recomendado), Supabase ou Turso?
2. **Região**: UE (recomendado, por causa do RGPD e do Render em Frankfurt).
3. Queres que o **primeiro PR** seja as **métricas persistentes**? (recomendado)
4. Se escolheres Neon: instalas o conector? (opcional)

## Fontes

- Neon, [limites do plano gratuito](https://neon.com/faqs/free-plan-limits-and-quotas) (atualizado a 2026-10-01; as páginas de terceiros com 0,5 GB estão desatualizadas).
- Supabase: [Jetadmin](https://www.jetadmin.io/blog/supabase-pricing-2026-guide-to-plans-limits-and-real-world-costs/), [Makerkit](https://makerkit.dev/blog/saas/supabase-pricing) (fontes secundárias; confirmar em supabase.com/pricing).
- Turso: [CostBench](https://costbench.com/software/database-as-service/turso/free-plan) e outras comparações (secundárias).
- Render Postgres: [documentação oficial](https://render.com/docs/free) e [planos flexíveis](https://render.com/docs/postgresql-refresh).
- Aiven: [plano gratuito](https://aiven.io/docs/platform/concepts/free-plan).
- CockroachDB: [documentação](https://www.cockroachlabs.com/docs/cockroachcloud/learn-about-pricing) e [relato de setembro de 2026](https://devtoolpicks.com/blog/best-cockroachdb-alternatives-indie-hackers-2026).
- TiDB: [limites oficiais](https://docs.pingcap.com/tidbcloud/serverless-limitations/).
- MongoDB: [limitações do plano gratuito](https://docs.atlas.mongodb.com/reference/free-shared-limitations).
- Cloudflare D1: [alteração de 2026-09-01](https://developers.cloudflare.com/changelog/post/2026-09-01-d1-free-tier-limit-enforcement/).
- Firebase: [planos](https://firebase.google.com/docs/projects/billing/firebase-pricing-plans?hl=ca).
- Upstash: [preços do Redis](https://upstash.com/pricing/redis).
- Conectores: [Neon MCP](https://claudemarketplaces.com/mcp/neondatabase/mcp-server-neon), [guias de MCP para Claude Code](https://www.lowcode.agency/blog/best-mcp-servers-claude-code).
