# Gerador de Rifas

Gera PDFs de rifas numerados a partir de um template feito no Canva. Há duas interfaces sobre o **mesmo motor** (`src/core`):

- **app Windows** (`app/`, Tkinter/CustomTkinter, `.exe` com Nuitka) — ver `app/README.md`;
- **webapp** (`src/web`: API FastAPI + frontend React/Vite/TypeScript) — em construção.

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
| [`ci.yml`](.github/workflows/ci.yml) | cada push e pull request | `ruff`; `pytest` (Linux e Windows, Python 3.13 e 3.15); frontend (Biome, `tsc`, Vitest, build); constrói a imagem Docker (`testes` e `web`) |
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
   (**GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**). No Render: **Account Settings → Registry Credentials → Add Credential**, registo *GitHub Container Registry*, o teu utilizador do GitHub e esse token.
3. **Criar o serviço com o Blueprint:** no Render, *New → Blueprint* e escolhe este repositório (o Render pede autorização para a app GitHub dele ler o repositório privado). O [`render.yaml`](render.yaml) já define o serviço `gerador-rifas`
   (imagem `ghcr.io/andrenogueira/gerador-rifas:latest`, credencial `ghcr`, plano *Free*, região Frankfurt, *Health Check Path* `/health`). O Render define `PORT` sozinho e a app ouve nessa porta. O plano gratuito adormece após 15 min sem uso (o 1.º pedido demora cerca de 1 min).
4. Não há variáveis de ambiente obrigatórias. Se um dia precisares de algum valor secreto, define-o no painel do Render, nunca no repositório.
5. Copia o *Deploy Hook* do serviço para o secret `RENDER_DEPLOY_HOOK_URL` (tabela acima).

> **Nota:** o serviço é público. Hoje só mostra o esqueleto (língua e títulos), por isso não há risco. Antes de a app aceitar uploads e gerar PDFs, têm de existir os limites contra abuso (tamanho, nº de números, uma geração de cada vez, por IP): estão no `webapp/PLANO.md`.
