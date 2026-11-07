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

## Estrutura de pastas alvo

```
src/core/    lógica pura: análise do template, folha, geração, verificação, pdftexto, textos das 18 línguas (i18n)
src/web/     interface: API FastAPI (+ trabalhos, sessões, limites) e frontend React/Vite (src/web/frontend/)
tests/       pytest: testes do core (migrados de app/testes/) e da API
app/         app Windows (continua; passa a importar o core de src/core). Só UI Windows + build do .exe
docs/        análise e planos
webapp/      PLANO.md (rascunho/plano; o código vai para src/)
```

Estado atual: `src/` **ainda não existe** (`tests/` já existe, com os testes de caracterização); hoje o motor vive em `app/core.py`, `app/pdftexto.py`, `app/i18n.py`, `app/idiomas/`.
A **Fase 0** cria `src/core` movendo-os (sem mudar o comportamento da app Windows) e acrescenta à raiz o `pyproject.toml`; o `.gitignore`
da raiz só deixa entrar `app/`, `webapp/`, `docs/`, `tests/`, `pytest.ini` e este ficheiro → **acrescentar `src/`, `pyproject.toml`, `Dockerfile`, `.github/`**.
Estes nomes já estão refletidos em `webapp/PLANO.md` e `docs/MIGRATION_PLAN.md` (antes `rifas_core`, `backend/`, `frontend/`).

## Regras

- **Nenhuma alteração ao `src/core` sem os testes passarem** — antes e depois. Hoje: `pytest` (raiz) e ainda `teste_folha`, `teste_canva`,
  `teste_5000` (ver Comandos) em Windows **e** em Linux (contentor). Nunca "ajustar o teste" para passar sem perceber porquê.
- **`src/core` não importa nada de interface desktop nem de Windows:** nada de `tkinter`, `customtkinter`, `pywin32`/`win32*`, `winreg`,
  `ctypes.windll`, `os.startfile`, `%APPDATA%`, nem de FastAPI/Starlette (o core não conhece a web). Verificar com `grep` antes de fechar uma tarefa.
- **Configuração só por variáveis de ambiente** (previstas: `ACCESS_PASSWORD`, `SECRET_KEY` para assinar o cookie, `MAX_UPLOAD_MB`,
  `MAX_NUMEROS`, `JOB_TTL_MIN`); valores por defeito seguros, falhar ao arrancar se faltar `ACCESS_PASSWORD`. Sem caminhos absolutos no código.
- **Sem segredos no código nem no repo** (palavra-passe, chaves, certificados privados, `.env`); o `.cer` público é a única exceção. Documentar um `.env.example` sem valores reais.
- Segurança dos uploads: validar o tipo real (`%PDF-`, PNG/JPG), nunca usar nomes/caminhos do cliente (`core.nome_seguro`), limites de tamanho/números/tempo.
- **PDFium não é thread-safe** → todas as chamadas ao motor vão para um processo de trabalho (1 processo = 1 PDFium), nunca threads do servidor.
- Língua **por pedido** (o `i18n.t` global tem de deixar de ser usado no core); o log do core emite chave + parâmetros, traduz-se na fronteira.
- Regras de produto iguais às da app: o template nunca é guardado, o nome dos ficheiros é escrito pelo utilizador, aviso/confirmação com >24 rifas por
  folha, «Limpar tudo» no fim, 18 línguas. Nos blocos da folha a numeração é sequencial **por bloco** (não ordenar globalmente).

## Comandos

### Hoje (existem)
**Testes de caracterização (pytest)** — a partir da raiz do repo, com o venv de `app/` (`pytest` está em `app/requirements.txt`; instalar com
`uv pip install --python app/.venv/Scripts/python.exe pytest`). Fixam o comportamento atual de `core`, `pdftexto`, `i18n` e `idiomas` (145 testes, ≈10 s).
Se um falhar depois de uma alteração: é regressão, ou o comportamento mudou de propósito e o teste deve ser atualizado conscientemente. Fixtures em `tests/fixtures/`.
```
app/.venv/Scripts/python.exe -m pytest                                        # todos
app/.venv/Scripts/python.exe -m pytest tests/test_folha.py::test_maximo_por_folha   # um só
```
O que não se testa por estar preso a Tkinter/Windows está listado em `docs/MIGRATION_PLAN.md` §8 («Não testável ainda»); os testes nunca importam `app.py`.

**Scripts antigos** — correr a partir de `app/` com o venv `app/.venv` (Windows; `PYTHONIOENCODING=utf-8` na consola). Cada script sai com código 1 se falhar; não há runner.
```
python testes/teste_folha.py   <pasta_exemplos> <pasta_saida>            # arrumação, rifa única, rotação
python testes/teste_canva.py   <pasta_saida> [pasta_pdfs]                # templates reais do Canva em app/testes/
python testes/teste_5000.py    <pasta_templates> <pasta_saida> pdf|png [N]
python testes/teste_digitos.py <pasta_templates_aleatorios> <pasta_saida>
python app.py                                                           # app Windows (GUI)
python app.py --selftest <pasta>                                        # auto-teste sem janela
```
`teste_gui.py` e `teste_limpar.py` precisam de ecrã. Build do `.exe`: `construir.bat` (só Windows).

### Alvo (a criar nas Fases 0–1; não existem ainda — ajustar aqui quando existirem)
```
uv sync                                          # instalar dependências (Python 3.12), incluindo as de dev
uv run pytest                                    # todos os testes (hoje: ver acima)
uv run pytest tests/test_folha.py::test_a4 -x    # um só teste
ACCESS_PASSWORD=dev SECRET_KEY=dev uv run uvicorn web.main:app --reload --app-dir src   # API em http://localhost:8000
pnpm -C src/web/frontend install && pnpm -C src/web/frontend dev    # frontend (Vite) com proxy para a API
pnpm -C src/web/frontend build                   # gera os estáticos servidos pela API
docker build -t gerador-rifas . && docker run --rm -p 8000:8000 -e ACCESS_PASSWORD=dev -e SECRET_KEY=dev gerador-rifas
```
`docker` só funciona depois de abrir o Rancher Desktop e escolher o motor dockerd (moby).

## Armadilhas do motor

`core.preparar(template, algarismos)` → `Preparado` (não serializável entre processos: recriar no worker, ≈1 s) → `core.gerar(Trabalho, Preparado)`
escreve os PDFs → `core.verificar` relê-os. `pdftexto.py` é um interpretador próprio de *content streams* PDF. API baseada em `Path` (adaptar a
bytes/temporários), cancelar = `threading.Event` (em processo de trabalho precisa de evento de `multiprocessing`). Para o resto ver `docs/MIGRATION_PLAN.md` §3.
