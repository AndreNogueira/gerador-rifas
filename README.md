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
4. Não há variáveis de ambiente **obrigatórias**. Opcionais, no **Environment** do serviço (são variáveis do Render, **não** *secrets* do GitHub):
   - **`CLAUDE_TOKEN`** (opcional): um segundo acesso ao painel, **só de leitura**, para um assistente (≥ 24 caracteres e diferente do `ADMIN_TOKEN`; ver [`docs/ADMIN.md`](docs/ADMIN.md)).
   - **`ADMIN_TOKEN`**: liga o painel de administração em `/admin` (gráficos do servidor e da utilização). Uma palavra-passe longa e aleatória (≥ 12 caracteres: `python -c "import secrets; print(secrets.token_urlsafe(32))"`). Sem ela o painel não existe (404). Ver [`docs/ADMIN.md`](docs/ADMIN.md).
   - **`PUBLIC_URL`**: o URL do site (p.ex. um domínio próprio) para o canónico, o Open Graph e o sitemap; sem ela usa-se o `RENDER_EXTERNAL_URL` do Render. Ver [`docs/SEO.md`](docs/SEO.md).
5. Copia o *Deploy Hook* do serviço para o secret `RENDER_DEPLOY_HOOK_URL` (tabela acima).

> **Nota:** o serviço é público e sem palavra-passe. A defesa contra abuso são os limites (tamanho dos uploads, nº de números por pedido, uma geração de cada vez, pedidos por IP): ver `src/web/config.py` e `src/web/limites.py`.

## Contribuir

Trabalha-se em **pull requests pequenos**, um por funcionalidade. O fluxo, as regras e as receitas estão em [`CONTRIBUTING.md`](CONTRIBUTING.md); as ideias por fazer em [`docs/ROADMAP.md`](docs/ROADMAP.md). Antes de abrir um PR corre tudo o que o CI corre:

```
powershell -File scripts/verificar.ps1      # Windows (-Docker para construir também as imagens)
sh scripts/verificar.sh                     # Linux/macOS
```
