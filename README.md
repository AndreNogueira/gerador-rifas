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

1. **Primeiro faz um push para `main`** e espera que o `Deploy` publique a imagem (separador *Packages* do repositório). O serviço só se pode criar depois de a imagem existir.
2. **Credencial para puxar a imagem privada:** a imagem herda a visibilidade *privada* do repositório. No GitHub cria um *Personal access token (classic)* só com o âmbito `read:packages`
   (**GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**). No Render: **Account Settings → Registry Credentials → Add Credential**, registo *GitHub Container Registry*, o teu utilizador do GitHub e esse token.
3. **Criar o serviço:** *New → Web Service → Existing Image* → `ghcr.io/andrenogueira/gerador-rifas:latest`, plano *Free*, *Health Check Path* `/health`. O Render define `PORT` sozinho e a app ouve nessa porta.
4. **Variáveis de ambiente do serviço** (no painel do Render, nunca no repositório): `SECRET_KEY` (um valor aleatório longo) e, quando existir, `ACCESS_PASSWORD`.
5. Copia o *Deploy Hook* do serviço para o secret `RENDER_DEPLOY_HOOK_URL` (tabela acima).

> **Atenção:** a palavra-passe de acesso (`ACCESS_PASSWORD`) ainda **não está implementada** na webapp. Enquanto não estiver, não crie o serviço no Render nem o secret `RENDER_DEPLOY_HOOK_URL`: o servidor ficaria público.
