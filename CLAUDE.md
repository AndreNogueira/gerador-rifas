# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Projeto em português (pt-PT): comentários, docs e mensagens ao utilizador em português. Análise completa da migração: `docs/MIGRATION_PLAN.md`
(abordagem B decidida). Plano de execução (fases, API): `webapp/PLANO.md`.

## Objetivo da migração

Passar o «Gerador de Rifas» (app Windows em `app/`, Tkinter/CustomTkinter, Python 3.13, Nuitka `.exe`) para uma **webapp** com deploy
automático, **sem perder** a app Windows: o motor de geração (análise do template do Canva, arrumação da folha, escrita dos números,
verificação) passa a ser **um só código** usado pelas duas. Uso só do dono (sem contas), repo GitHub privado `AndreNogueira/gerador-rifas`.

## Stack alvo (abordagem B)

- **Backend:** FastAPI + uvicorn, **Python 3.12** (imagem Docker). O `core` tem de correr também em 3.13 (a app Windows usa 3.13) → o CI testa 3.12 e 3.13.
- **Frontend:** React + Vite + TypeScript (pnpm, Node 22). Decidido pelo utilizador em vez de HTMX/Jinja; **NiceGUI está de fora**.
- **Pré-visualização:** PDF.js (`pdfjs-dist`) no browser; o servidor devolve um PDF de 1 página com os primeiros números (não PNG).
- **Testes:** pytest (backend/core), vitest (frontend), Playwright (e2e, mais tarde).
- **Docker** multi-stage (Node faz `pnpm build`, Python serve API + estáticos; contentor sem root). **GitHub Actions**: testes → build → deploy.
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
src/web/     (a criar) API FastAPI (+ trabalhos, sessões, limites) e frontend React/Vite (src/web/frontend/)
tests/       pytest (raiz): testes do core e fixtures
app/         app Windows: só interface (Tk/CustomTkinter) e build do .exe. `app/ambiente.py` põe ..\src no sys.path e é o ÚNICO sítio com winreg/ctypes/os.startfile (`SistemaWindows`)
docs/        análise e planos · webapp/PLANO.md  plano da webapp
```

Estado: **Fase 0 feita** (lógica em `src/core`, a app Windows importa de lá; língua por pedido, mensagens estruturadas, entrada por bytes e `pdf_da_previa` existem;
testes a passar em Windows e em Linux, Python 3.12 e 3.13). Falta para a webapp: `src/web/` (Fase 1), `Dockerfile` de produção, `.github/` (CI).
Substitutos das dependências do Windows (tabela completa e o que não tem substituto: `docs/MIGRATION_PLAN.md` §9): lingua → `Accept-Language`; registo/tema → CSS do browser;
`%APPDATA%` → `RIFAS_DADOS`; ficheiros locais → upload + `armazenamento`; `os.startfile` → `saida` (download); `--selftest` → `python -m core`; build do `.exe` → `Dockerfile` + `.github/workflows/ci.yml`.
O `.gitignore` da raiz só deixa entrar `app/`, `webapp/`, `docs/`, `tests/`, `src/`, `docker/`, `.github/`, `Dockerfile`, `.dockerignore`, `pytest.ini`, `pyproject.toml`, `uv.lock` e este ficheiro.
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
  Previstas para a webapp: `ACCESS_PASSWORD`, `SECRET_KEY` (assinar o cookie), `MAX_UPLOAD_MB`, `MAX_NUMEROS`, `JOB_TTL_MIN`; valores por defeito seguros, falhar ao arrancar se faltar `ACCESS_PASSWORD`.
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

### Hoje (existem)
**Testes de caracterização (pytest)** — a partir da raiz do repo, com o venv de `app/` (`pytest` está em `app/requirements.txt`; instalar com
`uv pip install --python app/.venv/Scripts/python.exe pytest`). Cobrem o `src/core` (430 testes, ≈18 s; `pytest.ini` aponta `pythonpath = src`).
Se um falhar depois de uma alteração: é regressão, ou o comportamento mudou de propósito e o teste deve ser atualizado conscientemente. Fixtures em `tests/fixtures/`.
```
app/.venv/Scripts/python.exe -m pytest                                        # todos
app/.venv/Scripts/python.exe -m pytest tests/test_folha.py::test_maximo_por_folha   # um só
```
O que continua preso a Tkinter/Windows está listado em `docs/MIGRATION_PLAN.md` §8 («Não testável ainda»); os testes nunca importam `app.py`.

**Em Linux (contentor)** — com o Rancher Desktop aberto (motor dockerd/moby). Corre `pytest` + `teste_folha`, `teste_canva`, `teste_5000` (pdf e png) e `teste_digitos`
com `uv sync` (`pyproject.toml`/`uv.lock`), numa imagem `python:3.12-slim` (ou `-Python 3.13`); sai com código ≠ 0 se algo falhar. O `docker.exe` do Rancher não está no PATH
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

### Alvo (a criar na Fase 1; as 3 primeiras linhas já funcionam)
```
uv sync                                          # instalar dependências (Python >=3.12) incluindo as de dev (pyproject.toml)
uv run pytest                                    # todos os testes
uv run pytest tests/test_folha.py::test_maximo_por_folha -x    # um só teste
ACCESS_PASSWORD=dev SECRET_KEY=dev uv run uvicorn web.main:app --reload --app-dir src   # API em http://localhost:8000
pnpm -C src/web/frontend install && pnpm -C src/web/frontend dev    # frontend (Vite) com proxy para a API
pnpm -C src/web/frontend build                   # gera os estáticos servidos pela API
docker build -t gerador-rifas . && docker run --rm -p 8000:8000 -e ACCESS_PASSWORD=dev -e SECRET_KEY=dev gerador-rifas
```
`docker` só funciona depois de abrir o Rancher Desktop e escolher o motor dockerd (moby).

## Armadilhas do motor

`core.preparar(template, algarismos)` → `Preparado` (não serializável entre processos: recriar no worker, ≈1 s) → `core.gerar(Trabalho, Preparado)`
escreve os PDFs → `core.verificar` relê-os. `pdftexto.py` é um interpretador próprio de *content streams* PDF. Nomes privados (`core._arrumar`, `_f`, …) estão
reexportados em `core/__init__.py` só porque os testes os usam; as funções de imagem (`_segmentar`, …) acedem-se por `core.motor`. API baseada em `Path` (adaptar a
bytes/temporários), cancelar = `threading.Event` (em processo de trabalho precisa de evento de `multiprocessing`). Para o resto ver `docs/MIGRATION_PLAN.md` §3.
