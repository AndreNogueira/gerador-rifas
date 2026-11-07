# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Projeto em português (pt-PT): comentários, docs e mensagens ao utilizador em português. Análise completa da migração: `docs/MIGRATION_PLAN.md`
(abordagem B decidida). Plano de execução (fases, API): `webapp/PLANO.md`.

## Objetivo da migração

Passar o «Gerador de Rifas» (app Windows em `app/`, Tkinter/CustomTkinter, Python 3.13, Nuitka `.exe`) para uma **webapp** com deploy
automático, **sem perder** a app Windows: o motor de geração (análise do template do Canva, arrumação da folha, escrita dos números,
verificação) passa a ser **um só código** usado pelas duas. Uso só do dono (sem contas), repo GitHub privado `AndreNogueira/gerador-rifas`.

## Stack alvo (abordagem B)

- **Regra das versões: usar sempre as últimas estáveis, fixadas exatamente** (`pnpm-lock.yaml`, `uv.lock`, `packageManager`/`devEngines` no `package.json`, tags do Docker) — nunca intervalos flutuantes.
  Estado em 2026-11-07: **Python 3.15** (`.python-version`; o `core` corre também em 3.13 = a da app Windows), FastAPI 0.162, **Node 26** (LTS desde 2026-10-28), **pnpm 12**, **React 19.3**, **Vite 8**, **TypeScript 7** (compilador nativo),
  **Vitest 5**, **Biome 2** (lint/formato). Ao pedir «últimas versões»: `npm view <pacote> version` / PyPI / `uv self update`, e voltar a correr tudo. A app Windows (`app/`: Python 3.13, Nuitka, CustomTkinter) fica **fora** desta regra (o build demora 10–20 min e tem de manter o `--selftest` igual).
- **Backend:** FastAPI + uvicorn (`src/web/app.py`), serve a API em `/api`, `/health` e os estáticos do frontend (com *fallback* para o `index.html`).
- **Frontend:** **React + Vite + TypeScript** (pnpm), em `src/web/frontend/`. Escolhido **em vez de Angular** (avaliado em 2026-11-07, ver `docs/MIGRATION_PLAN.md` §10): o Angular 22 impede o TypeScript 7 (`typescript >=6.0 <6.1`),
  o i18n embutido do Angular compila uma build por língua (aqui as 18 línguas vêm em JSON da API) e a app é pequena. **Sem** ESLint/typescript-eslint (limitam o TypeScript a <6.1): lint e formato com **Biome**. Dependências mínimas: só `react` e `react-dom`
  em produção; sem Tailwind, sem biblioteca de i18n nem de estado. O prototipo NiceGUI foi **arquivado** no ramo local `nicegui-prototipo` (não está em `main`): não usar.
- **Pré-visualização:** PDF.js (`pdfjs-dist`) no browser; o servidor devolve um PDF de 1 página com os primeiros números (não PNG).
- **Testes:** pytest (backend/core), Vitest + Testing Library (frontend), Playwright (e2e, mais tarde).
- **Docker** multi-stage (`node:26.13.0-slim` faz `pnpm teste` e `pnpm build`; `python:3.15.2-slim` + uv 0.13.7 servem API + estáticos, sem Node; contentor sem root; tags exatas). **GitHub Actions** (`.github/workflows/`): `ci.yml` (ruff, pytest em Linux/Windows × Python 3.13/3.15, frontend, imagem Docker) e `deploy.yml` (só em push para `main` **depois** de o CI passar, via `workflow_run`: publica em `ghcr.io/<dono>/<repo>` e chama o *deploy hook* do Render com `imgURL`). Credenciais só como *secrets* do GitHub (`RENDER_DEPLOY_HOOK_URL`; o `GITHUB_TOKEN` é automático); a lista e onde os obter está no `README.md`. Actions em tag *major* (`checkout@v7`, `setup-node@v7`, `pnpm/action-setup@v6`, `docker/*`) exceto `astral-sh/setup-uv`, que **já não tem tag flutuante** e usa a versão exata (`@v10.3.3`; o `v10` não resolve — foi o que fez falhar o 1.º CI).
- **Alojamento: Render** (web service gratuito, Docker): 512 MB RAM, adormece aos 15 min, disco efémero. Deploy a cada push para `main`,
  **só depois do CI passar**. Teto de ~100 000 números por pedido, ZIP em *streaming*, 1 trabalho de cada vez, PDFium em processo isolado.
- **Dependências do core:** `pypdf`, `pypdfium2`, `pillow` (todas com rodas Linux). `customtkinter`, `nuitka` e afins ficam só em `app/`.

## Estrutura de pastas

```
src/core/    lógica pura, SEM UI nem Windows (pacote `core`, usado pela app Windows e, mais tarde, pela webapp)
  motor.py       análise do template, folha, geração, verificação, pré-visualização (o antigo app/core.py)
  pdftexto.py    interpretador de content streams PDF · i18n.py + idiomas/  textos das 18 línguas
  pedido.py      campos de texto -> Trabalho e resumo        · escolha_folha.py  papel/margem/rifas por folha
  config.py      preferências (config.json) e pasta de dados · tutorial.py  conteúdo do tutorial · autoteste.py  exemplos do --selftest
  entradas.py    uploads em bytes: tipo real (%PDF-/PNG/JPG), ficheiros temporários, `preparar_de_bytes`
  armazenamento.py  sessões em disco (RIFAS_ARMAZENAMENTO), limite e limpeza · saida.py  descarregar PDF/ZIP em streaming (em vez de «abrir a pasta»)
  sistema.py     contrato `Sistema` (língua, dados, tema, abrir) + `SistemaNeutro` (variáveis de ambiente) · tema.py  paleta de cores e CSS, sem registo do Windows
  __main__.py    `python -m core <exemplos> <saida>`: auto-teste sem janela (CI/Linux)
  __init__.py    reexporta o motor: `import core; core.preparar(...)` e `from core import i18n, pedido, ...`
src/web/     API FastAPI e frontend. Só chama `core` (um teste proíbe imports de pypdf/PIL/Tk aqui). `python -m src.web` (PORT, por omissão 8080)
  app.py         `criar_app()`: /health, /api/linguas, /api/textos/{lingua}, estáticos do frontend · config.py  variáveis de ambiente
  frontend/      React + Vite + TS (pnpm): `src/api.ts` (cliente), `src/i18n.tsx` (textos vindos da API), `src/App.tsx`; `dist/` (compilado, ignorado pelo git) é o que o FastAPI serve
tests/       pytest (raiz): testes do core, da API (`test_web_api.py`) e fixtures; os do frontend ficam ao lado do código (`*.test.tsx`)
app/         app Windows: só interface (Tk/CustomTkinter) e build do .exe. `app/ambiente.py` põe ..\src no sys.path e é o ÚNICO sítio com winreg/ctypes/os.startfile (`SistemaWindows`)
docs/        análise e planos · webapp/PLANO.md  plano da webapp
```

Estado: **Fase 0 feita** (lógica em `src/core`, a app Windows importa de lá; língua por pedido, mensagens estruturadas, entrada por bytes e `pdf_da_previa` existem;
testes a passar em Windows e em Linux, Python 3.13 e 3.15). **Esqueleto da webapp feito**: API FastAPI com `/health`, `/api/linguas` e `/api/textos/{lingua}`; frontend React que carrega as línguas e os textos da API (os 4 passos só como
títulos); Dockerfile multi-stage (alvos `testes` e `web`) e CI (pytest 3.13/3.15, frontend, Docker). **Falta (Fase 1 em diante, ver `webapp/PLANO.md`):** palavra-passe `ACCESS_PASSWORD`, sessões, upload, análise, pré-visualização, gerar/cancelar/ZIP,
**processo isolado para o PDFium** (pool de processos + `multiprocessing.Event`; recriar o `Preparado` no worker), os 4 cartões e o visor, tutorial/vídeo, deploy no Render.
Substitutos das dependências do Windows (tabela completa e o que não tem substituto: `docs/MIGRATION_PLAN.md` §9): lingua → `Accept-Language`; registo/tema → CSS do browser;
`%APPDATA%` → `RIFAS_DADOS`; ficheiros locais → upload + `armazenamento`; `os.startfile` → `saida` (download); `--selftest` → `python -m core`; build do `.exe` → `Dockerfile` + `.github/workflows/ci.yml`.
O `.gitignore` da raiz só deixa entrar `app/`, `webapp/`, `docs/`, `tests/`, `src/`, `docker/`, `.github/`, `Dockerfile`, `.dockerignore`, `pytest.ini`, `pyproject.toml`, `.python-version`, `uv.lock`, `README.md` e este ficheiro.
Todo o ponto de entrada da app Windows ou de `app/testes/` tem de fazer `import ambiente` antes de importar `core`; o `construir.bat` define `PYTHONPATH=..\src` e `--include-package=core` para o Nuitka.

## Regras

- **Nenhuma alteração ao `src/core` sem os testes passarem** — antes e depois. Hoje: `pytest` (raiz) e ainda `teste_folha`, `teste_canva`,
  `teste_5000` (ver Comandos) em Windows **e** em Linux (contentor). Nunca "ajustar o teste" para passar sem perceber porquê.
- **`src/core` não importa nada de interface desktop nem de Windows:** nada de `tkinter`, `customtkinter`, `pywin32`/`win32*`, `winreg`,
  `ctypes`, `os.startfile`, `%APPDATA%`, nem de FastAPI/Starlette (o core não conhece a web). `tests/test_core_puro.py` verifica-o (AST de todo o `src/core` + `import core`
  num processo limpo). O que é do Windows fica em `app/` (`ambiente.py`: `%APPDATA%`, língua do Windows via kernel32) e passa ao core como parâmetro.
- **Configuração por variáveis de ambiente, sem caminhos absolutos no código** (`pathlib`, relativos a `__file__`). Existem: `RIFAS_LINGUA` (língua por defeito, ganha a tudo),
  `RIFAS_DADOS` (pasta do `config.json`; por defeito `%APPDATA%\GeradorRifas` na app Windows), `RIFAS_FONTES` (letras do sistema, só nos scripts de testes; por defeito `%WINDIR%\Fonts`),
  `RIFAS_ARMAZENAMENTO` (pasta das sessões/uploads/PDFs; por defeito a temporária do sistema), `RIFAS_LIMITE_SESSAO_MB`, `RIFAS_TEMA` (`claro`/`escuro`), `RIFAS_COR_DESTAQUE` (`#RRGGBB`).
  Webapp (`src/web/config.py`): `PORT` (8080), `HOST` (127.0.0.1; no contentor 0.0.0.0), `RIFAS_FRONTEND` (pasta do frontend compilado; por omissão `src/web/frontend/dist`). Previstas: `ACCESS_PASSWORD`, `SECRET_KEY` (assinar o cookie),
  `MAX_UPLOAD_MB`, `MAX_NUMEROS`, `JOB_TTL_MIN`; valores por defeito seguros, falhar ao arrancar se faltar `ACCESS_PASSWORD`.
- **Sem segredos no código nem no repo** (palavra-passe, chaves, certificados privados, `.env`); o `.cer` público é a única exceção. Documentar um `.env.example` sem valores reais.
- Segurança dos uploads: validar o tipo real (`%PDF-`, PNG/JPG), nunca usar nomes/caminhos do cliente (`core.nome_seguro`), limites de tamanho/números/tempo.
- **PDFium não é thread-safe** → todas as chamadas ao motor vão para um processo de trabalho (1 processo = 1 PDFium), nunca threads do servidor.
- **Língua por pedido na webapp:** `i18n.definir()` é global (só a app Windows a usa). Na API usar `with i18n.com_lingua(lg):` (contextvars; **não passa para outras threads nem processos** — chamá-lo dentro do
  worker) ou `ErroRifas.em(lg)` / `Mensagem.em(lg)` / `i18n.traduzir(chave, lg, **params)`. O log do `gerar`/`preparar` e os erros de `verificar` são `i18n.Mensagem` (um `str` com `.chave` e `.params`, picklable).
- **Entradas da API:** `core.entradas.preparar_de_bytes(template, algarismos, ...)` (valida o tipo pelos bytes, nome seguro, apaga os temporários) e `core.pdf_da_previa(prep, inicio, digitos)` para o PDF.js.
  O cancelamento só usa `.is_set()`: serve um `multiprocessing.Event`.
- Regras de produto iguais às da app: o template nunca é guardado, o nome dos ficheiros é escrito pelo utilizador, aviso/confirmação com >24 rifas por
  folha, «Limpar tudo» no fim, 18 línguas. Nos blocos da folha a numeração é sequencial **por bloco** (não ordenar globalmente).

## Comandos

### Webapp e testes (venv da raiz, Python 3.15, `uv`; frontend com pnpm 12 / Node 26)
```
uv sync                                                      # .venv na raiz (Python 3.15) com core + FastAPI + pytest (grupos dev e web)
uv run pytest                                                # todos os testes (≈480, ≈20 s)
uv run pytest tests/test_folha.py::test_maximo_por_folha -x  # um só
uv run ruff check .                                          # lint (regras E4,E7,E9,F em pyproject.toml; `app/` excluída)
uv run python -m src.web                                     # API + frontend compilado em http://127.0.0.1:8080 (PORT, HOST, RIFAS_FRONTEND)
cd src/web/frontend && pnpm install                          # (o pnpm 12 vem de `npm i -g pnpm@12.18.0`; o Node 26 vem do `devEngines` do package.json)
pnpm dev                                                     # Vite em http://localhost:5173 com proxy de /api e /health para :8080 (correr antes `python -m src.web`)
pnpm build                                                   # tsc --noEmit + vite build -> dist/ (o que o FastAPI serve)
pnpm tipos | pnpm teste | pnpm lint                          # tsc 7, Vitest 5, Biome
docker build --target web -t gerador-rifas . && docker run --rm -p 8080:8080 gerador-rifas
```
Se um teste falhar depois de uma alteração: é regressão, ou o comportamento mudou de propósito e o teste deve ser atualizado conscientemente. Fixtures em `tests/fixtures/`.
No PowerShell o `pnpm` escreve os comandos no *stderr* e parece «erro» (NativeCommandError) mesmo quando passa: ver o código de saída.
**`pnpm.CMD`/`pnpm` 11 não consegue passar para o 12 por si (o `packageManager` falha no Windows): instalar o 12 com `npm install -g pnpm@12.18.0`.** `biome migrate` converte `recommended: true` em `preset: none` (desliga o linter): o `biome.json` usa `"preset": "recommended"`.

### Testes do core com o venv da app Windows (Python 3.13, ainda funciona)
`app/.venv` não tem FastAPI: os testes da API ficam *skipped* e correm os do core. Garante que o core continua a funcionar em 3.13.
```
app/.venv/Scripts/python.exe -m pytest
```
O que continua preso a Tkinter/Windows está listado em `docs/MIGRATION_PLAN.md` §8 («Não testável ainda»); os testes nunca importam `app.py`.

**Em Linux (contentor)** — com o Rancher Desktop aberto (motor dockerd/moby). Corre `pytest` + `teste_folha`, `teste_canva`, `teste_5000` (pdf e png) e `teste_digitos`
com `uv sync` (`pyproject.toml`/`uv.lock`), numa imagem `python:3.15-slim` (ou `-Python 3.13`); sai com código ≠ 0 se algo falhar. O `docker.exe` do Rancher não está no PATH
do Claude Code: o script usa `C:\Program Files\Rancher Desktop\resources\resources\win32\bin`.
```
powershell -File docker\testes_linux.ps1 [-Python 3.13]
docker build --target testes -t gerador-rifas-testes .      # o mesmo, como imagem: pytest + `python -m core` correm durante o build (usa o Dockerfile da raiz)
cd src && python -m core ../app/exemplos <pasta_saida>       # auto-teste sem janela (substitui o --selftest fora do Windows)
```

**Scripts antigos** — correr a partir de `app/` com o venv `app/.venv` (Windows; `PYTHONIOENCODING=utf-8` na consola). Cada script sai com código 1 se falhar; não há runner.
```
python testes/teste_folha.py   <pasta_exemplos> <pasta_saida>            # arrumação, rifa única, rotação
python testes/teste_canva.py   <pasta_saida> [pasta_pdfs]                # templates reais do Canva em app/testes/
python testes/teste_5000.py    <pasta_templates> <pasta_saida> pdf|png [N]
python testes/teste_digitos.py <pasta_templates_aleatorios> <pasta_saida>
python app.py                                                           # app Windows (GUI)
python app.py --selftest <pasta>                                        # auto-teste sem janela (compara com o selftest.txt anterior se mexeres na GUI)
```
`teste_gui.py` e `teste_limpar.py` precisam de ecrã. Build do `.exe`: `construir.bat` (só Windows; ≈10–20 min). Depois de mexer na GUI ou no `construir.bat`,
correr `dist\GeradorRifas.exe --selftest <pasta>`.

`docker` só funciona depois de abrir o Rancher Desktop e escolher o motor dockerd (moby).

## Armadilhas do motor

`core.preparar(template, algarismos)` → `Preparado` (não serializável entre processos: recriar no worker, ≈1 s) → `core.gerar(Trabalho, Preparado)`
escreve os PDFs → `core.verificar` relê-os. `pdftexto.py` é um interpretador próprio de *content streams* PDF. Nomes privados (`core._arrumar`, `_f`, …) estão
reexportados em `core/__init__.py` só porque os testes os usam; as funções de imagem (`_segmentar`, …) acedem-se por `core.motor`. API baseada em `Path` (adaptar a
bytes/temporários), cancelar = `threading.Event` (em processo de trabalho precisa de evento de `multiprocessing`). Para o resto ver `docs/MIGRATION_PLAN.md` §3.
