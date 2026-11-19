# Gerador de Rifas

Gera PDFs de rifas numerados a partir de um template feito no Canva. Há duas interfaces sobre o **mesmo motor** (`src/core`):

- **app Windows** (`app/`, Tkinter/CustomTkinter, `.exe` com Nuitka) — ver `app/README.md`;
- **webapp** (`src/web`: API FastAPI + frontend React/Vite/TypeScript): carregas o template e os algarismos, vês a pré-visualização e descarregas os PDFs (ZIP ou PDF único). Pública e sem palavra-passe; 22 línguas; tutorial e vídeo.

Planos: [`docs/PLANO_PRODUTO.md`](docs/PLANO_PRODUTO.md) (funcionalidades e monetização), [`docs/ONLINE.md`](docs/ONLINE.md) (manter o serviço acordado), [`docs/ADMIN.md`](docs/ADMIN.md) (painel), [`docs/SEO.md`](docs/SEO.md).

Contexto, decisões e regras de trabalho: [`CLAUDE.md`](CLAUDE.md), [`webapp/PLANO.md`](webapp/PLANO.md), [`docs/MIGRATION_PLAN.md`](docs/MIGRATION_PLAN.md).

## Correr localmente

```
uv sync                                  # Python 3.15 + dependências (grupos dev e web)
uv run pytest                            # testes
uv run ruff check .                      # lint
cd src/web/frontend && pnpm install && pnpm build && cd ../../..
uv run python -m src.web                 # http://127.0.0.1:8080  (PORT, HOST)
docker build --target web -t gerador-rifas . && docker run --rm -p 8080:8080 gerador-rifas
```

## CI/CD

| Workflow | Quando | O que faz |
|---|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | cada push e pull request (um PR só de documentação não corre) | **num PR:** `ruff`, `pytest` em Linux (Python 3.15) e o frontend (Biome, `tsc`, Vitest, build). **Em `main`, ou num PR com a etiqueta `completo`:** também `pytest` em Windows, as métricas em Postgres, o e2e (Playwright) e a imagem Docker (`testes` e `web`). Poupa minutos do plano gratuito do GitHub; o resto corre-se com `scripts/verificar.ps1 -Docker -E2e` |
| [`deploy.yml`](.github/workflows/deploy.yml) | push para `main`, **só depois de o CI passar** | publica a imagem em `ghcr.io/<dono>/<repo>:latest` e `:sha-<commit>`; manda o Render puxar essa imagem |

Alojamento: **Render** (web service gratuito, a partir de uma imagem Docker). Nenhum segredo está nos ficheiros: o repositório só usa os *secrets* abaixo.

### Secrets do GitHub que tens de criar

Criam-se em **GitHub → o repositório → Settings → Secrets and variables → Actions → New repository secret**.

| Secret | Obrigatório | Para quê | Onde o obter |
|---|---|---|---|
| `GITHUB_TOKEN` | — | publicar no ghcr.io | **Automático**: o GitHub cria-o em cada execução; não há nada para criar. O `deploy.yml` pede-lhe `packages: write`. |
| `RENDER_DEPLOY_HOOK_URL` | para o passo do Render | mandar o Render fazer deploy da imagem nova | **Render → o teu serviço → Settings → Deploy Hook** → copiar o URL completo (inclui `?key=...`). Sem este secret a imagem é publicada e o passo do Render é saltado, com um aviso. |

### O que configurar no Render (não são secrets do GitHub)

0. O serviço é **público e sem palavra-passe** (por agora é grátis; mais tarde será pago).
1. **Primeiro faz um push para `main`** e espera que o `Deploy` publique a imagem (separador *Packages* do repositório). O serviço só se pode criar depois de a imagem existir.
2. **Credencial para puxar a imagem privada** (tem de se chamar **`ghcr`**, é o nome que o `render.yaml` usa): a imagem herda a visibilidade *privada* do repositório. No GitHub cria um *Personal access token (classic)* só com o âmbito `read:packages`
   (**GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**). No Render: **Workspace Settings → Container Registry Credentials → Add Credential** (tem de ser o mesmo *workspace* onde vais criar o serviço), *Name* = `ghcr` (exatamente, minúsculas), *Registry* = *GitHub Container Registry*, *Username* = o teu utilizador do GitHub e *Personal Access Token* = esse token. Se o Blueprint der «credentials "ghcr" not found», é porque esta credencial não existe nesse workspace ou tem outro nome.
3. **Criar o serviço com o Blueprint:** no Render, *New → Blueprint* e escolhe este repositório (o Render pede autorização para a app GitHub dele ler o repositório privado). O [`render.yaml`](render.yaml) já define o serviço `gerador-rifas`
   (imagem `ghcr.io/andrenogueira/gerador-rifas:latest`, credencial `ghcr`, plano *Free*, região Frankfurt, *Health Check Path* `/health`). O Render define `PORT` sozinho e a app ouve nessa porta. O plano gratuito adormece após 15 min sem uso (o 1.º pedido demora cerca de 1 min).
4. Não há variáveis de ambiente **obrigatórias**; as opcionais (painel, contacto, donativos, anúncios, QR, base de dados…) estão explicadas, uma a uma, em [Variáveis de ambiente do Render](#variáveis-de-ambiente-do-render) e em [Donativos](#donativos-donativo_url).
5. Copia o *Deploy Hook* do serviço para o secret `RENDER_DEPLOY_HOOK_URL` (tabela acima).

> **Nota:** o serviço é público e sem palavra-passe. A defesa contra abuso são os limites (tamanho dos uploads, nº de números por pedido, uma geração de cada vez, pedidos por IP): ver `src/web/config.py` e `src/web/limites.py`.

## Variáveis de ambiente do Render

Definem-se no Render: **o serviço → Environment → Add Environment Variable → Save**. Cada alteração reinicia o serviço (cerca de 1 min). São variáveis do **Render**, nunca *secrets* do GitHub, e **nenhum valor vai para o repositório** (nem para este README, nem para conversas: se um token for partilhado onde não devia, gera outro e troca-o). **Não há variáveis obrigatórias**: sem nenhuma, o site funciona; cada uma abaixo liga uma funcionalidade. O código que as lê está em [`src/web/config.py`](src/web/config.py).

Para confirmar de fora o que está ligado: `https://<o-teu-site>/api/publico` devolve `contacto`, `qr`, `partilha_editor`, `anuncios_cliente`, `anuncios_slot` e `donativo_url` (vazio = não definido).

### Painel de administração

| Variável | O que é | Sem ela |
|---|---|---|
| `ADMIN_TOKEN` | A palavra-passe do dono para `/admin` (gráficos do servidor e da utilização, erros, chaves da API, textos de SEO). Mínimo **12 caracteres**; gera uma assim: `python -c "import secrets; print(secrets.token_urlsafe(32))"`. | O painel **não existe** (tudo em `/admin` e `/api/admin/*` dá 404). |
| `CLAUDE_TOKEN` | Um segundo acesso ao painel, **só de leitura**, para um assistente (o Claude) ver as métricas e os erros sem poder mudar nada. Mínimo **24 caracteres** e **diferente** do `ADMIN_TOKEN` (se for igual ou curto, fica desligado): `python -c "import secrets; print(secrets.token_hex(16))"` dá 32. Entra-se em `/admin` com ele (o painel mostra «Só de leitura») ou, sem cookie, com `Authorization: Bearer <token>` num pedido **GET** a `/api/admin/estado`, `/dados`, `/erros`…; os pedidos que mudam coisas respondem 403. | Só o dono vê o painel. Mudar qualquer um dos dois tokens fecha todas as sessões abertas. |

O painel só mostra **agregados** (nunca IPs, nomes de ficheiros, conteúdo ou textos de erro) e inclui uma secção com a ligação para o **Swagger UI** da API pública (`/api/v1/docs`). Detalhes em [`docs/ADMIN.md`](docs/ADMIN.md).

### Contacto, donativos e identificação legal

| Variável | O que é | Sem ela |
|---|---|---|
| `CONTACTO_EMAIL` | O e-mail que as páginas **Termos**, **Privacidade** e **Contacto** mostram. | A página Contacto desaparece do rodapé e os textos não mostram nenhum e-mail. |
| `RESPONSAVEL` | O nome de quem gere o serviço («O serviço é gerido por …»), nas páginas Termos e Privacidade. Até 100 caracteres. | Os textos dizem «gerido pelo seu autor». |
| `DONATIVO_URL` | Uma ligação `https://` onde as pessoas podem apoiar o projeto (ver [Donativos](#donativos-donativo_url)). | Não aparece o botão «Donativo» (cabeçalho, fim da geração e rodapé). |
| `BACKUP_S3_ENDPOINT`, `BACKUP_S3_BUCKET`, `BACKUP_S3_REGION`, `BACKUP_S3_ACCESS_KEY_ID`, `BACKUP_S3_SECRET_ACCESS_KEY` | A **cópia de segurança semanal** dos dados que não se refazem para o armazenamento de objetos do Neon (ver [`docs/ADMIN.md`](docs/ADMIN.md)): uma credencial `storage:write` (que também lê e apaga). **As duas últimas são palavras-passe: só no Render.** | Não há cópias; o cartão «Cópia de segurança» do painel diz o que falta. |
| `RESEND_API_KEY` + `RELATORIO_EMAIL_PARA` (+ `RELATORIO_EMAIL_DE`, `RELATORIO_FUSO`, `ALERTAS_EMAIL=0` / `RELATORIOS_PERIODICOS=0` para desligar os alertas imediatos / os resumos semanal e mensal) | O **relatório diário por e-mail** (à meia-noite, hora de `Europe/Lisbon` por omissão) com as métricas do dia que acabou: chave da API do Resend e o teu e-mail (ver [`docs/ADMIN.md`](docs/ADMIN.md)). **A chave é uma palavra-passe: só no Render.** | Não se envia nada; a aba «Relatório diário» do painel diz o que falta. |
| `GITHUB_ISSUES_TOKEN` + `GITHUB_REPO` | Um *fine-grained token* só com «Issues: Read and write» no repositório e o `dono/nome` dele: «Reportar problema» cria um *issue* no GitHub (ver [`docs/OPINIAO.md`](docs/OPINIAO.md)). **O token é uma palavra-passe: só no Render.** | A página «Reportar problema» existe mas diz que ainda não está ativa e o botão «Abrir» fica desligado. |

### Anúncios (Google AdSense)

| Variável | O que é | Sem ela |
|---|---|---|
| `ADSENSE_CLIENTE` | O teu ID de editor, `ca-pub-` + 16 algarismos (AdSense → *Conta* → *Informações da conta*: `pub-…`). Põe o script da Google nas páginas públicas (verificação do site e mensagem de consentimento), serve o `/ads.txt` e acrescenta o texto de anúncios à Política de privacidade. | Nada disto existe. |
| `ADSENSE_SLOT` | O **número do bloco de anúncio**: só os algarismos do `data-ad-slot` (AdSense → *Anúncios* → *Por unidade de anúncio* → *Anúncios de display*, bloco **responsivo**; copia só os algarismos do código). | O site fica «ligado à Google» mas **não mostra nenhum anúncio** (é o estado certo enquanto o AdSense não aprova o site). |

Passo a passo completo e mapa de onde os anúncios aparecem: [`docs/ADSENSE.md`](docs/ADSENSE.md).

### Site, SEO e QR dos bilhetes

| Variável | O que é | Sem ela |
|---|---|---|
| `PUBLIC_URL` | O endereço público do site, sem barra final (ex.: `https://rifas.exemplo.pt`), para o canónico, o Open Graph, o `hreflang` e o sitemap. Só é preciso com **domínio próprio**. | Usa o `RENDER_EXTERNAL_URL` que o Render define sozinho (`https://gerador-rifas.onrender.com`). |
| `GOOGLE_VERIFICACAO` | O código (`content`) da etiqueta *google-site-verification* que o Search Console te dá; é escrito na página inicial. | Sem etiqueta (verifica o site por outro método). |
| `VERIFICACAO_CHAVE` | A chave (≥ 16 caracteres) que **assina** os QR dos bilhetes; a página `/v/<código>` só confirma os que ela assinou. **Nunca a mudes depois de imprimir bilhetes com QR** (deixariam de verificar). | Não há QR. |
| `MAX_NUMEROS_QR` | O máximo de números de um pedido com QR (por omissão 10 000). | — |

### Base de dados e métricas

| Variável | O que é | Sem ela |
|---|---|---|
| `DATABASE_URL` | A ligação Postgres (Neon). Guarda as métricas, as ligações de partilha do editor, as chaves da API e os textos de SEO editados. | SQLite local **efémero**: perde-se quando o serviço adormece ou é atualizado (o painel avisa) e a partilha do editor por ligação não existe. |
| `METRICAS_BD_MIN` | De quantos em quantos minutos as métricas vão para a base (1 a 720; por omissão 60). | — |
| `RIFAS_METRICAS` | Pasta onde fica o `metricas.sqlite3` (útil com um disco persistente). | — |

### Manter o serviço acordado (plano gratuito)

O Render gratuito adormece após 15 min sem pedidos de fora. O serviço chama o seu próprio `/health` pelo endereço público de 10 em 10 min e **liga-se sozinho no Render**; só mexes nisto para o alterar: `KEEPALIVE=0` desliga, `KEEPALIVE_URL` escolhe outro endereço (p.ex. o domínio próprio) e `KEEPALIVE_MIN` muda o intervalo (1 a 14). Não acorda um serviço que já adormeceu (para isso, um monitor externo ou um plano pago). Ver [`docs/ONLINE.md`](docs/ONLINE.md).

### Vídeos e capturas do tutorial

`ASSETS_URL` e `ASSETS_SHA256` apontam para o `.zip` dos vídeos e capturas do site (no armazenamento de objetos do Neon). **Já vêm no Dockerfile**: só os defines no Render para usar outro `.zip`. Para publicar um novo: [`docs/ASSETS.md`](docs/ASSETS.md).

### Limites (todos têm valor por omissão; a defesa de um serviço público)

| Variável | Por omissão | O que limita |
|---|---|---|
| `MAX_UPLOAD_MB` | 25 | Tamanho de cada ficheiro carregado. |
| `MAX_NUMEROS` | 30 000 | Números por pedido (≈ 58 s a gerar no Render gratuito). |
| `JOB_MAX_MIN` | 10 | Duração máxima de uma geração. |
| `JOB_TTL_MIN` | 30 | Quanto tempo ficam os ficheiros gerados. |
| `MAX_SESSOES` | 200 | Sessões em simultâneo. |
| `RIFAS_LIMITE_SESSAO_MB` | 300 | Espaço em disco de cada sessão. |
| `RATE_PESADOS_POR_MIN` / `RATE_LEVES_POR_MIN` | 30 / 300 | Pedidos por minuto e por IP (uploads, pré-visualizações e gerações / os restantes). |
| `CANCELAR_ESPERA_S` | 3 | Segundos até um cancelamento mata o processo do motor. |
| `FORWARDED_ALLOW_IPS` | redes privadas | Proxies em que se confia para ler o IP real (`X-Forwarded-For`). |
| `API_MAX_ITENS` / `API_MAX_NUMEROS_LOTE` / `API_LOTES_ATIVOS` / `API_PEDIDOS_POR_MIN` / `API_ESPERA_MIN` | 20 / 3 × `MAX_NUMEROS` / 3 / 120 / 20 | A API pública em lote ([`docs/API.md`](docs/API.md)). |
| `LOG_PEDIDOS` | ligado | `LOG_PEDIDOS=0` desliga o registo JSON de cada pedido ([`docs/OBSERVABILIDADE.md`](docs/OBSERVABILIDADE.md)). |

O Render define `PORT`, `RENDER` e `RENDER_EXTERNAL_URL` sozinho; não as definas.

## Donativos (`DONATIVO_URL`)

`DONATIVO_URL` é só **uma ligação**: o site não processa pagamentos nem guarda dados de ninguém. Quando está definida, aparece **«Donativo»** em três sítios — um botão com um coração no cabeçalho (ao lado de «Partilhar»), um convite depois de gerar os ficheiros (`Donativo.tsx`) e a ligação do rodapé —, a abrir noutro separador. Só se aceita `https://`.

### Que serviço escolher

| Serviço | Ligação que obténs | Notas |
|---|---|---|
| [**Ko-fi**](https://ko-fi.com) | `https://ko-fi.com/o-teu-nome` | Pensado para apoiar criadores, com donativos únicos. Não cobra comissão sobre donativos (o PayPal ou o Stripe cobram a taxa deles). O mais simples para começar. |
| [**PayPal.Me**](https://www.paypal.com/paypalme) | `https://paypal.me/o-teu-nome` | Quem doa não precisa de conta (paga com cartão). Podes fixar um valor (`…/5` = 5 €). Taxas do PayPal. |
| [**Liberapay**](https://liberapay.com) | `https://liberapay.com/o-teu-nome` | Sem comissão da plataforma e de código aberto; **orientado a apoios recorrentes** (semanais, mensais). |
| [**Buy Me a Coffee**](https://www.buymeacoffee.com) | `https://buymeacoffee.com/o-teu-nome` | Parecido com o Ko-fi; a plataforma cobra uma comissão. |
| [**Revolut.Me**](https://revolut.com) | `https://revolut.me/o-teu-nome` | Só se já tens conta Revolut (app → Perfil → Revolut.Me). Gratuito entre contas Revolut. |
| [**Stripe Payment Links**](https://dashboard.stripe.com/payment-links) | `https://donate.stripe.com/…` ou `https://buy.stripe.com/…` | Exige conta Stripe verificada (IBAN, NIF). Os métodos de pagamento (cartão, MB WAY, Multibanco…) dependem do que ativares na conta. O mais profissional, o mais trabalhoso. |

O **MB WAY** de um telemóvel pessoal **não tem ligação pública**, por isso não serve diretamente; só chega ao site por um dos serviços acima (o Stripe, por exemplo, pode aceitá-lo).

### Passo a passo (exemplo com o Ko-fi; os outros são parecidos)

1. Cria a conta em [ko-fi.com](https://ko-fi.com) (*Sign up*) e escolhe o nome da página: será o fim do endereço (`ko-fi.com/o-teu-nome`).
2. No painel do Ko-fi, liga **onde recebes o dinheiro** (*Settings → Payments*: o PayPal ou o Stripe; sem isto a página não recebe).
3. Preenche a página (foto, uma frase: «Ajuda a manter o Gerador de Rifas gratuito»).
4. Abre a tua página num separador privado e confirma que o endereço funciona: **esse endereço é o valor**.
5. No Render: serviço `gerador-rifas` → **Environment → Add Environment Variable** → *Key* `DONATIVO_URL`, *Value* `https://ko-fi.com/o-teu-nome` → **Save Changes** (o serviço reinicia).
6. Confirma: `https://<o-teu-site>/api/publico` mostra o endereço em `donativo_url` e o cabeçalho e o rodapé passam a ter «Donativo» (nas 22 línguas).

Para tirar o botão, apaga a variável. **Antes de aceitar dinheiro** confirma com o teu contabilista ou as Finanças se há obrigações fiscais ou de declaração (variam com o país, o valor e a regularidade) e se a associação ou o projeto precisa de estar registado; o site não decide isto por ti.

## Contribuir

Trabalha-se em **pull requests pequenos**, um por funcionalidade. O fluxo, as regras e as receitas estão em [`CONTRIBUTING.md`](CONTRIBUTING.md); as ideias por fazer em [`docs/ROADMAP.md`](docs/ROADMAP.md). Antes de abrir um PR corre tudo o que o CI corre:

```
powershell -File scripts/verificar.ps1      # Windows (-Docker para construir também as imagens)
sh scripts/verificar.sh                     # Linux/macOS
```
