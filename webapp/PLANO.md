# Webapp «Gerador de Rifas» — plano (rascunho para aprovar)

Decidido: **backend Python (FastAPI) + frontend React/Vite/TypeScript** (opção B do `docs/MIGRATION_PLAN.md`). Ferramentas (últimas versões, fixadas exatamente): Node 26, pnpm 12, uv, git, `gh` e Rancher Desktop (docker).

Python: **3.15** no backend/imagem Docker; o `src/core` tem de correr também em 3.13 (app Windows) — o CI testa as duas.
Regra: **sempre as últimas versões estáveis, fixadas** (`pnpm-lock.yaml`, `uv.lock`, tags do Docker). Quadro das versões e a avaliação React × Angular: §7.
Regras e comandos: `CLAUDE.md` (raiz).

## 1. Ideia
Os mesmos 4 passos da app Windows (template → algarismos → números → destino/nome), mas no browser: o utilizador carrega
o template (PDF do Canva) e o ficheiro dos algarismos, vê a pré-visualização e descarrega os PDFs (ZIP, ou um PDF só).
Inclui os dois modos do template (vários bilhetes por página / uma só rifa que enche a folha), 18 línguas, tutorial e vídeo.

## 2. Arquitetura
Estrutura alvo (raiz do repo; ver `CLAUDE.md`):
```
src/core/             motor puro, sem UI nem Windows: motor, pdftexto, i18n, idiomas/ (18 línguas), pedido, escolha_folha, config, tutorial, autoteste
src/web/              FastAPI (Python 3.15, uv)
  app.py              `criar_app()`: rotas da API, /health e estáticos do frontend (já existe)
  trabalhos.py        (a criar) pool de processos para o PDFium + fila de trabalhos + limpeza
  frontend/           React + Vite + TypeScript (pnpm)
tests/                pytest: testes do motor (migrados de app/testes: templates aleatórios + os do Canva) e da API
app/                  app Windows (passa a importar o core de src/core)
Dockerfile, docker-compose.yml, .github/workflows/   na raiz
```
- **Motor partilhado:** o `core.py` deixa de estar duplicado — vive em `src/core` e é usado pela app Windows e pela webapp
  (decidido: pasta partilhada na raiz, sem copiar). Substitui os nomes antigos `rifas_core`, `backend/` e `frontend/`.
- **PDFium não é thread-safe** (já nos mordeu): os pedidos ao motor vão para processos de trabalho (`ProcessPoolExecutor`,
  1 processo = 1 PDFium) e nunca para threads do servidor.
- **Sem contas:** cada sessão recebe um id aleatório; ficheiros temporários apagados ao fim de ~30 min.

## 3. API (esboço)
| Método | Rota | Faz |
|---|---|---|
| POST | `/api/sessoes` | cria sessão |
| POST | `/api/sessoes/{id}/template` e `/algarismos` | envia PDF/PNG/JPG; devolve `InfoTemplate` (bilhetes/página, letra, rifa única?, erros traduzidos) |
| POST | `/api/sessoes/{id}/folha` | papel, margem, rifas por folha → disposição, máximo, avisos (>24) |
| POST | `/api/sessoes/{id}/previa` | PDF de 1 página com os primeiros números (o browser desenha-o com PDF.js) |
| POST | `/api/sessoes/{id}/gerar` | cria trabalho; progresso por SSE; cancelar |
| GET | `/api/trabalhos/{id}/ficheiros` | ZIP (ou PDF único) |
| GET | `/api/textos/{lingua}` | textos (exportados dos `idiomas/*.py` para JSON) |

## 4. Frontend
Página única com os 4 cartões + visor (PDF.js: zoom, deslocamento, expandir) como na app; menu Idioma/Tema (claro/escuro do sistema);
tutorial com as imagens/vídeos já feitos (`assets/ajuda`, `assets/video`); botão «Limpar tudo» no fim.
Mesmas regras: template nunca guardado, nome dos ficheiros escrito pelo utilizador, avisos e confirmações iguais.

## 5. Segurança e limites (importante: recebemos ficheiros de desconhecidos)
- Limites: tamanho do upload (ex. 25 MB), nº máximo de números por pedido (ex. 100 000), tempo máximo por trabalho, 1 trabalho
  por sessão, limite de pedidos por IP.
- Validar tipo real (`%PDF-`, PNG/JPG), nunca confiar em nomes (`nome_seguro`), sem caminhos fornecidos pelo cliente.
- PDFs maliciosos: motor corre em processo isolado com limite de memória/tempo; contentor sem root e sem rede de saída.
- Apagar tudo no fim; sem registo de conteúdo; política de privacidade curta.

## 6. Fases
1. **Esqueleto** — **feito** (FastAPI + React/Vite a falar um com o outro: `/health`, `/api/linguas`, `/api/textos/{lingua}`; Dockerfile multi-stage e CI; falta só o `docker-compose`, que não é preciso).
2. **Motor como pacote** partilhado + testes a passar (`teste_folha`, `teste_canva`, `teste_5000`, `teste_limpar` adaptado).
3. **API de análise + pré-visualização** (template, algarismos, folha) e os 4 cartões + visor.
4. **Geração** (trabalhos, progresso, cancelar, ZIP) + «Limpar tudo».
5. **i18n (18 línguas)**, tutorial, vídeos, tema.
6. **Endurecimento** (limites, isolamento, limpeza) e testes de carga com 5000/30000 rifas.
7. **Deploy** (imagem Docker; escolher alojamento) e repositório no GitHub (`gh`).

## 7. Decisões
**Tomadas** (ver `docs/MIGRATION_PLAN.md`, que tem a análise completa da app desktop e as estimativas):
- Abordagem **B**: backend **FastAPI** com processos de trabalho isolados para o PDFium.
- Frontend **React + Vite + TypeScript** (pnpm), mantido (não HTMX/Jinja). Imagem Docker multi-stage.
- **React e não Angular** (avaliado em 2026-11-07 contra os registos npm/PyPI; detalhe em `docs/MIGRATION_PLAN.md` §10). Pesou, por esta ordem: (1) o Angular 22 fixa `typescript >=6.0 <6.1` e a regra
  «últimas versões» pede o TypeScript 7.0; (2) o i18n do Angular compila uma build por língua, e aqui as 18 línguas vêm em JSON da API; (3) 5 ecrãs e um formulário não justificam o peso do Angular.
  O Angular teria a vantagem de trazer router/formulários/HTTP/testes de origem, mas isso não compensa os pontos acima.
- **Versões (2026-11-07):** Python 3.15.2 · FastAPI 0.162 · uvicorn 0.54 · Node 26.13 · pnpm 12.18 · React 19.3 · Vite 8.3 · `@vitejs/plugin-react` 6 · TypeScript 7.0 · Vitest 5.1 · Biome 2.6. Lint com **Biome**
  porque `typescript-eslint` limita o TypeScript a <6.1. Só `react` e `react-dom` em produção.
- Estimativa revista: ≈ 25 dias úteis (±30 %).

- **Alojamento:** serviço **gratuito** (qual: ver «Em aberto»).
- **Público (decisão de 2026-11-07, substitui «só o dono»):** serviço **público e sem palavra-passe**; sem contas por agora (mais tarde será pago, e aí haverá contas/pagamento).
  Como qualquer pessoa pode usar a CPU de 512 MB, os limites passam a ser obrigatórios antes de haver upload/geração: tamanho, nº de números, tempo, 1 geração de cada vez e *rate limiting* por IP.
- **Repositório:** GitHub **privado** `AndreNogueira/gerador-rifas` (criado), com `app/`, `webapp/` e `docs/` (a raiz usa `.gitignore`
  que deixa de fora `final/`, `saida/`, `.venv`, `dist` e caches).
- **Motor:** **partilhado** — `src/core` usado pela app Windows e pela webapp (a app passa a importá-lo; testes comuns).
- **Pré-visualização:** **PDF.js no browser**. O servidor gera um PDF de **1 página** com os primeiros números (`Documento` já
  faz isto; novo `pdf_da_previa()` em vez de `pagina_previa()` em PNG) e o browser desenha-o: zoom/pan nativos e nítidos a
  qualquer ampliação, menos carga no servidor. O template carregado vê-se logo no browser (PDF.js lê o ficheiro local, sem upload).
  Consequência: o visor passa a ser um componente React sobre PDF.js (`pdfjs-dist`, Apache-2.0) e o PNG a 200 dpi deixa de existir.

- **Alojamento:** **Render** (Web Service gratuito, Docker). Consequências de desenho:
  - **512 MB de RAM** e CPU partilhada → teto de números por pedido (≈ 100 000), geração em *streaming* para o ZIP, 1 trabalho de cada vez,
    1 processo de trabalho para o PDFium; ficheiros só em disco efémero (apagados após ~30 min; perdem-se ao reiniciar).
  - **Adormece após 15 min** sem uso (arranque ≈ 1 min): a página mostra «a acordar o servidor…» (frontend serve-se de ficheiros estáticos).
  - **Sem autenticação** (serviço público): nada de `ACCESS_PASSWORD`; a proteção é a dos limites acima.
  - **Deploy automático:** ligar o repositório no painel do Render (autorizar a app GitHub no repo privado); *Auto-Deploy* a cada *push* para
    `main`, **só depois do CI passar** (GitHub Actions: testes do motor + build do frontend). Dockerfile na **raiz do repo** (contexto vê `app/` e `webapp/`).

## 8. Próximo passo
**Fase 0 — feita.** `src/core` tem o motor, `pdftexto`, `i18n`, `idiomas/` e a lógica que estava na janela (`pedido`, `escolha_folha`, `config`, `tutorial`,
`autoteste`); a app Windows importa de lá (o `--selftest` dá o mesmo resultado). Para a webapp: língua por pedido (`i18n.com_lingua`), log e erros de verificação como
`Mensagem` (chave + parâmetros), `core.entradas.preparar_de_bytes` (tipo real, nome seguro, temporários) e `core.pdf_da_previa` (PDF de 1 página para o PDF.js). 343 testes pytest
+ os scripts `teste_folha`/`teste_canva`/`teste_5000`/`teste_digitos` passam em Windows e em Linux (`docker\testes_linux.ps1`, Python 3.12 e 3.13); `src/core` sem imports
de UI/Windows (verificado por teste). Detalhe: `docs/MIGRATION_PLAN.md` §8.

**Esqueleto feito (React).** `src/web/app.py` (FastAPI: `/health`, `/api/linguas`, `/api/textos/{lingua}`, estáticos com *fallback* para o `index.html`, `/api/...` desconhecido = 404 JSON), `src/web/frontend/` (React 19.3 + Vite 8 + TS 7; carrega as línguas e os textos
da API; os 4 passos só como títulos), Dockerfile (`node:26-slim` → `python:3.15-slim`, sem Node na imagem final, utilizador sem root, `HEALTHCHECK`) e CI (pytest 3.13/3.15 em Linux e Windows, frontend, Docker). 483 testes pytest em 3.15 e 441 em 3.13; 8 do Vitest.
O protótipo em NiceGUI (5 ecrãs completos, 63 testes) ficou arquivado no ramo local `nicegui-prototipo` como referência (por exemplo, o fluxo de sessões/geração em `src/web/estado.py` e `motor.py`).

**Próximo: Fase 1 (API)** em `src/web/`: FastAPI com sessões, upload (`preparar_de_bytes`), análise do template, folha (`escolha_folha`), pré-visualização (`pdf_da_previa`),
trabalhos num processo de trabalho isolado (1 PDFium), progresso por SSE, ZIP; limites contra abuso (tamanho, nº de números, tempo, por IP; o serviço é público). Depois o frontend (Fase 2).

**Atenção ao começar a geração:** o plano e o `CLAUDE.md` exigem o PDFium num **processo** de trabalho (pool de processos, `multiprocessing.Event` para cancelar, `Preparado` recriado dentro do worker porque não é serializável); o protótipo NiceGUI usava um só *thread* (`ThreadPoolExecutor(1)`),
que serve para um utilizador mas não dá isolamento de memória/tempo para os 512 MB do Render. Não copiar esse `motor.py` sem trocar o *thread* por um processo.
