# Migração do «Gerador de Rifas» (desktop Windows → web com deploy automático)

Análise feita **só por leitura** da pasta `app/` (nenhum ficheiro de `app/` foi alterado). Versão analisada: 2.2.0,
Python 3.13, ≈ 3 900 linhas (`core.py` 1 158, `app.py` 1 252, `pdftexto.py` 403, `visor.py` 248, `ajuda.py` 213,
`widgets.py` 183, `icones.py` 218, `tema.py` 163, `i18n.py` 49) + 18 línguas em `idiomas/` (≈ 150 chaves cada).

**Resumo:** a app gera PDFs de rifas numeradas a partir de um template do Canva (+ um ficheiro com os algarismos 0–9).
O motor (`core.py` + `pdftexto.py`) é Python puro, sem Tkinter e sem dependências Windows, por isso **migra quase tal como está**.
O que é Windows ou Tk está concentrado em 4 módulos de interface que se descartam. Decisão final: **B — backend FastAPI + frontend React + Vite + TypeScript**.

---

## 1. Framework de GUI e ecrãs

**Framework:** Tkinter + **CustomTkinter 6** (widgets modernos sobre Tk) com widgets próprios:
`widgets.py` (painel deslocável `Rolavel`, barra de menus `BarraMenus`, dicas `Dica`), `visor.py` (`Visor`, um `tk.Canvas`
com zoom/pan), `icones.py` (ícones desenhados com Pillow), `tema.py` (cores do Windows). Não há PyQt, wxPython, pywin32 nem COM.

| Ecrã / janela | Onde | O que faz |
|---|---|---|
| **Janela principal** | `app.py::App` | Barra superior: logo, menus **Ficheiro / Ver / Idioma / Ajuda**, seletor de língua (18), botão de tema. Corpo em 3 colunas: definições · divisória arrastável · visor. |
| ↳ Cartão **1 Template** | `App._construir`, `_construir_folha` | Escolhe o PDF do Canva; mostra bilhetes por página, letra e exemplos detetados. Com template de **uma só rifa** aparece o painel da folha: papel (A4, A3, A5, Letter, Legal), margem (mm), rifas por folha, resumo, avisos (> 24). |
| ↳ Cartão **2 Algarismos 0–9** | idem | Escolhe o ficheiro (PDF/PNG/JPG) com `0123456789`; mostra a letra encontrada; botão limpar; atalho para o tutorial. |
| ↳ Cartão **3 Números** | idem | De / Até / Algarismos; modo «Vários PDFs» (máximo por ficheiro, múltiplo das rifas por folha) ou «Um único PDF»; resumo (números, ficheiros, páginas). |
| ↳ Cartão **4 Destino** | idem | Pasta de saída + nome dos ficheiros (obrigatório, escrito pelo utilizador). |
| ↳ Ações | idem | **Pré-visualizar**, **Gerar / Cancelar**, barra de progresso, estado, **Abrir pasta**, **Limpar tudo**, registo de eventos. |
| ↳ **Visor** | `visor.py` | Pré-visualização da 1.ª página: zoom (botões, Ctrl+roda), deslocamento, ajustar, expandir/reduzir (esconde as definições). |
| **Tutorial** | `ajuda.py::Tutorial` (`CTkToplevel`) | 8 páginas (visão geral, 4 passos, «uma só rifa», pré-visualizar/gerar, dicas) com texto, imagens (`assets/ajuda`, 3,4 MB) e navegação anterior/seguinte. |
| **Diálogos nativos** | `tkinter.filedialog` / `messagebox` | Abrir template; abrir algarismos; escolher pasta; confirmar substituição de ficheiros; confirmar «muitas rifas por folha»; sair a meio da geração; «Acerca de»; avisos e erros. |
| **Vídeo tutorial** | `App._video` | Abre `assets/video/tutorial_<lg>.mp4` no leitor do Windows (`os.startfile`). |

Atalhos: Ctrl+O, Ctrl+L, Ctrl+P, Ctrl+G/F5, F1, F11, Ctrl+±/0.

---

## 2. Dependências específicas de Windows

| Onde | O quê | Gravidade | Equivalente na web |
|---|---|---|---|
| `tema.py` | `winreg`: cor de destaque (`Explorer\Accent\AccentPalette`, DWM) e modo claro/escuro (`AppsUseLightTheme`); sondagem de 2 em 2 s em `App._vigiar_windows` | Só UI | CSS `prefers-color-scheme` e `accent-color`/`AccentColor`; sem sondagem |
| `widgets.py` | `ctypes.windll.user32` (`SetClassLongPtrW`, `RedrawWindow`…) para acelerar o redimensionar do Tk | Só UI | Desaparece |
| `i18n.py::detetar` | `kernel32.GetUserDefaultLocaleName` (com *fallback* `locale`) | Baixa | Cabeçalho `Accept-Language` + escolha guardada |
| `app.py` | `DADOS = %APPDATA%\GeradorRifas\config.json` | Média | Cookie/`localStorage` (preferências) |
| `app.py::abrir_pasta` | `os.startfile` (abrir pasta dos PDFs e o vídeo) | Média | Descarregar ZIP/PDF; `<video>` na página |
| `app.py` | `GeradorRifas.exe --selftest` (corre no `.exe` compilado) | Baixa | Teste automático em CI |
| `construir.bat`, `assinar.ps1`, `instalar_certificado.ps1`, `make_icon.py` | Nuitka → `.exe`, assinatura Authenticode (certificado autoassinado), instalação de certificado, ícone `.ico` | Build | Substituídos por Dockerfile + CI/CD |
| `testes/` | `C:\Windows\Fonts`, `SetCursorPos`, `subprocess` para ffmpeg, strings `C:\Rifas\Exemplo` | Só dev | Não migram (geração de capturas/vídeo e testes aleatórios continuam como ferramentas locais) |

**Não existe:** `pywin32`, COM (Excel/Outlook), impressoras, hardware, registo para além do tema, serviços Windows, `.exe` externos
na execução. **Caminhos absolutos:** o código da app não tem nenhum `C:\` (todos os caminhos vêm do utilizador ou de
`Path(__file__).parent`); `C:\Rifas\Exemplo` só aparece em scripts de demonstração. **Letras do sistema:** não são usadas
(o utilizador fornece os algarismos), logo não há dependência de fontes instaladas — bom para Linux.

---

## 3. Separação entre lógica de negócio e interface

### 3.1 Lógica pura (reutilizar)
| Módulo | Conteúdo | Notas para a web |
|---|---|---|
| `core.py` | `analisar_template`, `_celula_da_rifa`, `disposicao_da_folha`/`_arrumar` (folha com 0°/90°/misto), `preparar`, `Documento`, `gerar`, `verificar`, `pagina_previa`, `pagina_template`, `planear`, `validar`, `ErroRifas` | Sem Tkinter. Ver ressalvas abaixo. |
| `pdftexto.py` | Interpretador de *content streams* (Extrator, Corrida, Token): lê e apaga os números de exemplo | Puro (só `pypdf`). Reutilizar tal como está. |
| `idiomas/*.py`, `i18n.py` | Textos (`<lg>.py` + `ui_<lg>.py`), `t()` | Dicionários reutilizáveis (exportar para JSON se preciso). |

**Ressalvas no motor (a corrigir na Fase 0):**
1. `i18n.t` usa **língua global** (`_atual`) → não serve para pedidos concorrentes. Os erros já guardam `chave + params`
   (`ErroRifas`), por isso traduz-se na fronteira da API com a língua do pedido; o `log(t(...))` do `core.gerar` deve passar a emitir `(chave, params)`.
2. API baseada em `Path`: `preparar(template: Path, algarismos: Path)`, `Documento.gravar(destino)`, `gerar` escreve em `tr.saida` e
   `verificar` volta a ler. Na web usam-se ficheiros temporários por sessão ou `BytesIO` (`_abrir_leitor` e `_abrir_pdfium` já aceitam bytes).
3. `Preparado` contém leitores `pypdf` e `LetraPDF` → **não é serializável** entre processos; recria-se no processo de trabalho (≈ 0,1–1 s).
4. Cancelamento por `threading.Event` (serve numa thread; em processo de trabalho precisa de evento de `multiprocessing` ou terminar o processo).
5. **PDFium não é thread-safe** (já causou problemas): todas as chamadas ao motor têm de ir para **um** processo/worker.
6. `core.py` mistura *planeamento* e *E/S* em `gerar`; convém separar «montar páginas» de «gravar + verificar».

### 3.2 Misturado (extrair para serviço)
| Função (em `app.py`) | O que mistura | Destino |
|---|---|---|
| `_trabalho` | ler campos da UI + converter em `core.Trabalho` + erros traduzidos | Validação em modelo Pydantic |
| `_resumo` | cálculo (páginas/ficheiros/múltiplos) + escrita em labels | Função pura `resumo(...)` |
| `_recalcular_folha`, `_prep_atual` | validação margem/rifas por folha + `core.disposicao_da_folha` + mensagens | Serviço «folha» |
| `_analisar`, `_gerar`, `_previa` | `ThreadPoolExecutor(1)` + fila + `after()` do Tk | Fila de trabalhos + SSE |
| `_carregar_config`/`_guardar_config`, `_limpar_tudo` | estado em `StringVar` + ficheiro JSON | Preferências no cliente; «limpar» passa a ser trivial (nova sessão) |
| `verificar_traducoes`, `selftest` | verificações de qualidade (úteis!) | Passam a testes de CI |

### 3.3 Só interface (descartar/reescrever)
`visor.py`, `widgets.py`, `tema.py`, `icones.py` (→ SVG/CSS), `ajuda.py` (a **lista de tópicos** `lista_de_topicos()` reutiliza-se; a janela não),
`app.py` (layout, menus, divisória), `make_icon.py`.

---

## 4. Onde a app guarda dados e como muda num servidor

| Dado | Hoje | No servidor |
|---|---|---|
| Preferências (língua, tema, caminho dos algarismos, pasta, números, modo, papel, margem) | `%APPDATA%\GeradorRifas\config.json` (nunca guarda o template nem o nome) | Cookie / `localStorage`; **sem caminhos** (o ficheiro dos algarismos não pode ser «lembrado» no servidor: guardar só no browser, se o utilizador quiser) |
| Entrada | Ficheiros locais escolhidos nos diálogos | **Upload** (limite de tamanho, validação do tipo real); diretório temporário por sessão, apagado após ~30 min |
| Saída | PDFs na pasta escolhida, nome `NOME - 0001 - 0300.pdf` | Pasta temporária do trabalho → **ZIP** (ou PDF único) para descarregar; apagar depois |
| Estado de execução | Memória (objetos Tk, `Preparado`) | Sessão com id aleatório; estado do trabalho em memória do worker (sem base de dados na 1.ª versão) |
| Recursos | `assets/ajuda` (3,4 MB), `assets/video` (2,7 MB), `exemplos/` (252 KB), `idiomas/` (348 KB) | Ficheiros estáticos servidos pela app/CDN |
| Base de dados / Excel / rede | **Nenhuma** | Continua sem BD; opcional mais tarde: registo de uso/métricas |

Privacidade: ficheiros de utilizadores desconhecidos → não registar conteúdo, apagar sempre, política curta.

---

## 5. Dependências (`requirements.txt`) e compatibilidade com Linux

| Pacote | Uso | Linux? | Na web |
|---|---|---|---|
| `pypdf` | ler/escrever PDF | ✅ puro Python | manter |
| `pypdfium2` (+ PDFium) | desenhar páginas, extrair texto (verificação) | ✅ rodas `manylinux` x86_64/aarch64 | manter (processo isolado) |
| `pillow` | imagens, máscaras de algarismos | ✅ | manter |
| `customtkinter` (+ `darkdetect`, Tk) | interface | ❌ precisa de Tk e de ecrã; não serve em servidor | **remover** |
| `nuitka`, `ordered-set`, `zstandard` | só construir o `.exe` | n/a | remover |
| `reportlab`, `fonttools`, `psutil` | só testes (`testes/`) | ✅ | manter só em dev |
| *(novas)* `fastapi`, `uvicorn`, `python-multipart`, `sse-starlette` (opcional), `pytest` | backend web | ✅ | acrescentar |
| *(frontend, Node 22 + pnpm)* `react`, `react-dom`, `vite`, `typescript`, `vitest` | interface no browser | n/a (corre no browser; `build` em CI) | acrescentar |
Ferramentas fora do Python: `ffmpeg` (só para refazer o vídeo), Rancher Desktop/Docker (dev). Licenças: tudo permissivo, **sem PyMuPDF/AGPL**.
Nada no motor impede Linux; falta confirmar a suite de testes (`teste_folha`, `teste_canva`, `teste_5000`) num contentor Linux.

---

## 6. Riscos e estimativa de esforço

### 6.1 Riscos
| Risco | Probabilidade/Impacto | Mitigação |
|---|---|---|
| PDFium não é thread-safe | Alta / Alto | 1 processo de trabalho por PDFium (`ProcessPoolExecutor`), nunca threads do servidor |
| Upload de PDFs de desconhecidos (PDF malicioso, bombas de descompressão, DoS) | Média / Alto | Limites de tamanho/páginas/números, *timeouts*, contentor sem root e sem rede de saída, limite por IP/sessão |
| `Preparado` não serializável | Certa / Médio | Recriar no worker a partir dos ficheiros da sessão (≈ 1 s) |
| Memória/tempo em pedidos enormes (1 M números ≈ 190 MB, 1,5 min) | Média / Médio | Teto de números por pedido, geração em *streaming* para ZIP, cancelamento |
| Língua global em `i18n` | Certa / Médio | Língua por pedido; log estruturado |
| Paridade do visor (zoom/pan) | Média / Médio | **PDF.js** no browser sobre um PDF de 1 página gerado pelo servidor (zoom nítido, sem PNG) |
| Manter 18 línguas + capturas/vídeo sincronizados | Média / Baixo | Textos exportados do mesmo `idiomas/`; scripts `fazer_ajuda`/`fazer_video` mantidos |
| Dois códigos (desktop e web) a divergir | Média / Médio | `src/core` partilhado e testes comuns |
| Sessões em memória (se NiceGUI) vs escala | Média / Médio | Preferir API sem estado por ligação (opção B) |
| Experiência de «escolher pasta» não existe no browser | Certa / Baixo | Nome do ficheiro + descarregar ZIP |

### 6.2 Estimativa (1 programador, dias úteis)
| Fase | Conteúdo | **B** FastAPI + React/Vite | **A** NiceGUI |
|---|---|---|---|
| 0 | Extrair `src/core`: língua por pedido, log estruturado, bytes/temp em vez de `Path`, cancelamento; testes existentes a passar em Linux | 3 | 3 |
| 1 | Serviço/API: sessões, upload, análise, folha, pré-visualização, trabalhos em processo isolado, progresso (SSE), ZIP | 4 | 3 |
| 2 | Interface: 4 cartões, visor com zoom/pan, expandir, limpar tudo (React + Vite + TS) | 7 | 4 |
| 3 | i18n (18 línguas), tutorial + vídeo, tema | 3 | 2 |
| 4 | Endurecimento: limites, validação, isolamento, limpeza, testes de carga (5 000 / 30 000 rifas) | 3 | 3 |
| 5 | Docker multi-stage (build do frontend + API) + CI/CD (GitHub Actions → registo → deploy automático) | 3 | 2 |
| 6 | QA: testes e2e (Playwright), PDFs reais do Canva, regressão | 2 | 2 |
| | **Total** | **≈ 25 dias** | **≈ 19 dias** |
(± 30 %. A fase 0 é a mesma nas duas abordagens e é a que mais reduz o risco.)

---

## Decisão: **B — Backend FastAPI + frontend React + Vite + TypeScript**

(Escolhida pelo utilizador: a arquitetura da recomendação B, mantendo React + Vite no frontend em vez de HTMX/Jinja.)

**Porquê B:**
1. **O motor já é puro e sem estado.** O trabalho difícil não é a interface, é correr o PDFium com ficheiros de desconhecidos de
   forma segura; isso é uma API com trabalhos, limites e processos isolados — o terreno natural do FastAPI.
2. **NiceGUI liga estado e computação à ligação websocket**: o motor síncrono correria no mesmo processo/*event loop*, o estado
   vive na memória de cada sessão e é mais difícil impor limites por pedido, escalar horizontalmente e isolar uploads.
   Serve bem para ferramenta interna com poucos utilizadores; não para aberta na internet.
3. **API e interface desacopladas:** o contrato HTTP (OpenAPI do FastAPI) permite testar o backend sem browser e gerar tipos TypeScript para o frontend.
4. Mantém o motor testável isoladamente e a app Windows a funcionar com o mesmo `src/core`.

**Porquê React + Vite (e o que custa):** o visor com zoom/pan, o painel da folha (recálculo ao vivo), o progresso em tempo real e o
tutorial com 8 páginas ganham com componentes e estado no cliente. Custo face ao HTMX: ≈ +1 dia na interface, ≈ +1 dia no CI
(build do frontend, imagem multi-stage) e uma cadeia Node (pnpm) a manter; em troca, a UI pode crescer (ex.: mais modos de folha) sem reescrever.

**Arquitetura-alvo:**
- `src/web/` FastAPI (Python 3.12, uv) + `src/core` (motor, antes «`rifas_core`») + processo(s) de trabalho para o PDFium.
- `src/web/frontend/` React + Vite + TypeScript (pnpm); estado local (React) e *fetch*/SSE para a API; textos das 18 línguas servidos pela API em JSON.
- Uma imagem Docker multi-stage: *stage* Node faz `pnpm build`, *stage* Python serve a API **e** o frontend estático; contentor sem root.

**Quando A teria sido melhor:** ferramenta **estritamente interna** (poucos utilizadores, rede fechada, sem uploads de terceiros) — poupava ≈ 6 dias.

### Próximo passo sugerido
Fase 0 numa pasta nova (`src/core` na raiz), **sem tocar em `app/`** até os testes do motor passarem em Linux (Docker/Rancher). Detalhe em `webapp/PLANO.md`.

---

## 7. Decisões tomadas e alojamento gratuito

| Tema | Decisão |
|---|---|
| Abordagem | B: FastAPI + React/Vite/TypeScript |
| Alojamento | **Render** (Web Service gratuito, Docker, deploy automático do GitHub) |
| Utilizadores | **Só o dono**: sem contas; acesso protegido por palavra-passe/token (ou espaço privado) |
| Repositório | GitHub **privado** `AndreNogueira/gerador-rifas` com `app/`, `webapp/`, `docs/` (criado) |
| Motor | **Partilhado** (`src/core`) entre a app Windows e a webapp |
| Pré-visualização | **PDF.js** no browser; o servidor devolve um PDF de 1 página (não PNG) |

**Opções gratuitas para uma imagem Docker (uso individual):**
| Serviço | Grátis | Prós | Contras |
|---|---|---|---|
| **Hugging Face Spaces (Docker)** | CPU 2 vCPU / 16 GB RAM; Spaces privados | Muita RAM, sem cartão, deploy por git; privado = só tu | Adormece após inatividade; URL do Hugging Face; limites de armazenamento efémero |
| **Render (Web Service free)** | 512 MB RAM, deploy do GitHub | Sem cartão, CI/CD automático a cada *push* | Adormece após 15 min (arranque ≈ 1 min); 512 MB limita pedidos grandes |
| **Google Cloud Run** | Quota mensal gratuita, escala a zero | Docker puro, robusto, deploy via GitHub Actions | Exige conta de faturação (cartão); risco de custos se mal configurado |
| Fly.io / Railway | Sem *free tier* real para contas novas | — | Pagos / créditos de teste |

**Escolhido: Render.** (A recomendação era Hugging Face Spaces pela RAM; o Render dá deploy direto do GitHub e não pede cartão.) Implica: ficheiros temporários só em disco efémero, limites de RAM/tempo
nos pedidos (512 MB!), palavra-passe da app (o plano gratuito não tem autenticação) e arranque a frio tolerado (é uso individual).

---

## 8. Testes de caracterização e «Não testável ainda»

**Fase 0 (feita):** o motor passou de `app/` para o pacote `src/core` (`motor.py` = o antigo `core.py`, `pdftexto.py`, `i18n.py`, `idiomas/`) e a lógica
que estava misturada com a interface foi extraída para módulos novos do mesmo pacote, **sem alterar o comportamento** (a app Windows importa de `src/core`; o
`--selftest` dá exatamente o mesmo resultado que antes). Cada passo foi validado com `pytest`.

**Testes** (`tests/`, pytest, 343 testes, ≈ 16 s): começaram como testes de **caracterização** (fixam o comportamento atual, também as esquisitices) e
cobrem agora todo o `src/core`: validação (`validar`), plano de ficheiros (`planear`, `nome_seguro`), geometria e folha, análise do template (exemplos da app,
5 templates aleatórios e PDFs sintéticos de casos limite), `preparar`, `gerar`/`verificar`/`Documento`/`pagina_previa`, algarismos em imagem (imagens sintéticas),
as 18 línguas, e os módulos extraídos (`pedido`, `escolha_folha`, `config`, `tutorial`, `autoteste`). `tests/test_core_puro.py` verifica que **nenhum ficheiro de
`src/core` importa tkinter, customtkinter, pywin32/win32*, winreg, ctypes, msvcrt ou frameworks web** e que `import core` não carrega Tkinter. Fixtures em
`tests/fixtures/`. Correr: `app\.venv\Scripts\python.exe -m pytest` na raiz. Nenhum teste importa `app.py`, `ajuda.py`, `tema.py`, `widgets.py`, `visor.py` ou `icones.py`.

**«Não testável ainda» — estado:**

| Onde (antes) | Lógica | Agora |
|---|---|---|
| `App._trabalho` | Campos de texto → `Trabalho`; `int_invalido` com o nome traduzido | ✅ `core.pedido.trabalho_de_campos` / `ler_inteiro` · `tests/test_pedido.py` |
| `App._resumo` | Nº de ficheiros/páginas, aviso «máximo não múltiplo» | ✅ `core.pedido.resumo_do_pedido` / `rifas_por_pagina` · `tests/test_pedido.py` |
| `App._recalcular_folha`, `_render_folha` | Margem 0–50, «por folha» vazio = máximo, `acima`, texto da folha | ✅ `core.escolha_folha` (`ler_margem`, `escolher_folha`, `texto_da_folha`) · `tests/test_escolha_folha.py` |
| `App._prep_atual` | Preparado com a folha ou o erro | ✅ `core.escolha_folha.preparado_com_folha` (a interface mostra o aviso) |
| `ler_config`, `gravar_config`, `_carregar_config`, `_guardar_config`, `DADOS` | Que chaves se guardam, validações, `%APPDATA%` fixo | ✅ `core.config` (`preferencias`, `para_gravar`, `pasta_de_dados` com `RIFAS_DADOS`) · `tests/test_config.py`. O valor por defeito `%APPDATA%\GeradorRifas` fica em `app/ambiente.py` |
| `verificar_traducoes` | Paridade de chaves/parâmetros das línguas | ✅ `core.i18n.verificar_traducoes` · `tests/test_i18n.py` |
| `verificar_ajuda`, `ajuda.lista_de_topicos`, `_caixas` | Tópicos e imagens do tutorial | ✅ `core.tutorial` (a janela `Tutorial` fica em `ajuda.py`) · `tests/test_tutorial_e_autoteste.py` |
| `selftest` (metade do motor) | Gerar os exemplos e confirmar | ✅ `core.autoteste.gerar_exemplos`; a metade da janela fica em `app.py` |
| `i18n.detetar` | Língua do sistema (kernel32) | ✅ `core.i18n.detetar(codigo_sistema)` + `RIFAS_LINGUA`; a chamada ao Windows (`ctypes`) foi para `app/ambiente.py` |
| `GlifosImagem.calibrar`, `extrair_glifos`, `mascara_de_imagem` | Algarismos em imagem | ✅ (parcial) `mascara_de_imagem`, `_segmentar`, `extrair_glifos`, `glifos_de_imagem` · `tests/test_glifos.py`. `calibrar` continua só coberto indiretamente (gerar com PNG) |
| Caminhos absolutos em `app/testes/` | `Z:\projects\rifas\app`, `C:\Windows\Fonts` | ✅ relativos a `__file__` / `RIFAS_FONTES` (`%WINDIR%\Fonts`). Ficam só textos de demonstração (`C:\Rifas\Exemplo` nas capturas) |
| `abrir_pasta`, `App._video`, `ficheiro_video` | Abrir pasta/vídeo | ⛔ **fica na app, por natureza** (`os.startfile`): na web é descarregar ZIP/PDF e `<video>` |
| `tema.py`, `widgets.py`, `visor.py`, `icones.py`, janela `Tutorial` | Cores do Windows, visor, ícones | ⛔ **ficam na app** (winreg, ctypes.windll, Tk): na web reescrevem-se (CSS/React/PDF.js) |
| Língua global (`i18n._atual`) em `ErroRifas.__str__`/`verificar`/`log` | Pedidos concorrentes | ✅ **aditivo**, sem mudar a app Windows: `i18n.com_lingua(lg)` (contextvars), `traduzir(chave, lg)`, `ErroRifas.em(lg)`; o log e os erros de `verificar` passam a `Mensagem` (str + chave + parâmetros, picklable) · `tests/test_lingua_por_pedido.py`. Atenção: a língua do pedido não passa para outras threads/processos |
| Entrada por `Path` | Upload em bytes | ✅ `core.entradas` (`detetar_tipo` pelos bytes, `nome_de_upload`, `ficheiro_temporario`, `preparar_de_bytes`) + `core.pdf_da_previa` (PDF de 1 página para o PDF.js) · `tests/test_entradas.py` |
| Cancelar com `threading.Event`; `Preparado` não serializável | Processo de trabalho | ✅ o cancelamento só usa `.is_set()` (serve um `multiprocessing.Event`, testado); `Preparado` continua a recriar-se no worker (≈ 1 s), por desenho |
| Execução em Linux | Os testes só correram em Windows | ✅ `docker\testes_linux.ps1`: 343 testes pytest + `teste_folha`, `teste_canva`, `teste_5000` (pdf/png), `teste_digitos` em `python:3.12-slim` e `3.13-slim` (Rancher Desktop). Único ajuste: `gerar_template_aleatorio.py` usa as letras do reportlab quando não há as do Windows |

**Particularidades fixadas pelos testes** (ver comentários «quirk» em `tests/`): `nome_seguro` apaga `/` em vez de separar pastas e não trata nomes
reservados (`CON`); `validar` aceita `inicio = 0`; `_f(-0.00001)` escreve `-0`; `disposicao_da_folha` com `n <= 0` devolve 1 rifa e com margem negativa usa 0;
papel desconhecido levanta `KeyError`; `PADRAO_EXEMPLO` também apanha `0002` em `a0002b`; o `2099` da data do sorteio dos exemplos conta como número fixo.

---

## 9. Dependências do Windows → substitutos num servidor Linux

Para cada linha da tabela do §2. O código do Windows ficou **todo** em `app/ambiente.py`, atrás do contrato `core.sistema.Sistema`; o `src/core` tem a implementação
neutra (`SistemaNeutro`, só variáveis de ambiente) e os substitutos web. Testes: `tests/test_substitutos_windows.py` e `tests/test_armazenamento_e_saida.py`
(o código do Windows testa-se com um «registo» falso, por isso corre em Linux no CI).

| Dependência (§2) | Substituto no servidor | Onde | Estado |
|---|---|---|---|
| `tema.py` · `winreg`: cor de destaque + claro/escuro | **No browser**: CSS `prefers-color-scheme` e `accent-color`. O servidor só calcula a paleta: `core.tema.construir(7 tons)` (idêntica à da app, comparada em 300 paletas) e `variaveis_css()` para a página; o dono pode fixar `RIFAS_TEMA` (`claro`/`escuro`) e `RIFAS_COR_DESTAQUE` (`#RRGGBB`) via `SistemaNeutro` | `core/tema.py`, `core/sistema.py`; registo em `app/ambiente.py` | ✅ |
| `widgets.py` · `ctypes.windll.user32` (acelerar o redimensionar do Tk) | **Nenhum — não faz falta**: é uma otimização do Tkinter; o browser não tem este problema. Fica em `app/widgets.py` | — | ⛔ sem substituto (nem é preciso) |
| `i18n.detetar` · `kernel32.GetUserDefaultLocaleName` | Cabeçalho **`Accept-Language`**: `i18n.lingua_de_accept_language()` (respeita `q`, `*`, `q=0`, entradas inválidas) + `RIFAS_LINGUA` para forçar | `core/i18n.py` | ✅ |
| `app.py` · `%APPDATA%\GeradorRifas\config.json` | Preferências **no browser** (`localStorage`/cookie), validadas por `config.preferencias(cfg, caminhos=False)` (nunca devolve caminhos); onde houver ficheiro, `RIFAS_DADOS` | `core/config.py` | ✅ |
| Ficheiros locais (template, algarismos, pasta de saída) | **Upload** (`core.entradas.preparar_de_bytes`: tipo real pelos bytes, nome seguro, temporários) e **armazenamento por sessão** numa pasta configurável: `RIFAS_ARMAZENAMENTO` (por defeito a pasta temporária), `RIFAS_LIMITE_SESSAO_MB`, ids de sessão aleatórios, nomes validados contra `..`/barras, limpeza por idade. Interface `Armazenamento` — um S3/Blob futuro implementa o mesmo contrato (o PDFium precisa de ficheiros locais: `ficheiro_local()` descarregaria para uma cache) | `core/entradas.py`, `core/armazenamento.py` | ✅ (S3/Blob: só a interface) |
| `app.py::abrir_pasta` · `os.startfile` (abrir a pasta dos PDFs) | **Descarregar**: um PDF, ou um ZIP em *streaming* (sem o ter inteiro em memória: 512 MB no Render): `saida.entrega()` + `conteudo_da_entrega()`; só entram os PDFs verificados | `core/saida.py`; `os.startfile` em `app/ambiente.py` | ✅ |
| `App._video` · `os.startfile` no vídeo | `<video src=…>` na página; `tutorial.ficheiro_video(pasta, lingua)` escolhe o ficheiro (língua → en → pt) | `core/tutorial.py` | ✅ |
| Impressão local | A app nunca imprimiu: sempre gerou PDF. Na web é o mesmo: o utilizador descarrega e imprime onde quiser | — | ✅ nada a fazer |
| `GeradorRifas.exe --selftest` | `python -m core <exemplos> <saída>` (traduções + gerar os exemplos, código de saída ≠ 0 se falhar) e o CI | `core/__main__.py`, `.github/workflows/ci.yml` | ✅ |
| `construir.bat` · Nuitka, `assinar.ps1`, `instalar_certificado.ps1`, `make_icon.py` | **`Dockerfile`** (alvo `testes`: corre pytest + o auto-teste durante o *build*; o alvo `web` entra na Fase 1) e **GitHub Actions** (pytest em Linux e Windows × Python 3.12/3.13 + a imagem). A assinatura Authenticode não se aplica a um serviço web (HTTPS trata disso) | `Dockerfile`, `.dockerignore`, `.github/workflows/ci.yml` | ✅ (CI ainda não correu no GitHub) |
| `testes/` · `C:\Windows\Fonts`, `SetCursorPos`, ffmpeg | Letras: `RIFAS_FONTES`, e o `reportlab` traz as suas se não houver as do Windows. `SetCursorPos` e o ffmpeg só servem para **gerar capturas e vídeo do tutorial** (ferramentas de desenvolvimento, não correm no servidor) | `app/testes/` | ⛔ ficam locais, ver abaixo |
| Caminhos absolutos (`C:\Rifas\Exemplo`) | Só texto de demonstração nas capturas | — | ✅ |
| Hardware, COM (Excel/Outlook), impressoras, serviços Windows | **Não existem** na app (§2). Se aparecerem no futuro, entram atrás de uma interface em `src/core` como `Sistema` — sem inventar já | — | — |

**O que não tem substituto razoável (e as opções):**
1. **Cor de destaque e modo escuro «do Windows» do utilizador** — um servidor não vê o sistema do cliente. Isolado em `Sistema.cor_destaque()/modo_escuro()` (devolvem `None` = «o browser decide»). Opções: (a) **CSS do browser** (recomendado: `prefers-color-scheme` + `accent-color`, zero código no servidor); (b) o dono fixa a cor/tema por variável de ambiente; (c) um seletor de tema na página guardado em `localStorage`.
2. **Capturas e vídeo do tutorial** (`fazer_ajuda.py`, `fazer_video.py`: simulam o rato e fotografam a janela Tk no Windows). Não fazem parte do servidor; as imagens/vídeos já feitos servem-se como ficheiros. Opções para o futuro: (a) manter as ferramentas locais e só refazer os assets quando a app Windows mudar (recomendado); (b) refazer as capturas **da webapp** com Playwright (já previsto para os testes e2e), em CI; (c) correr as atuais em Linux com `xvfb` + Tk (trabalho grande, pouco valor).
3. **Otimização de redimensionamento do Tk** — desaparece com o Tk; nada a substituir.
