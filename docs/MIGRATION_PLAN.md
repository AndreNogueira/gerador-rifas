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
| Dois códigos (desktop e web) a divergir | Média / Médio | Pacote `rifas_core` partilhado e testes comuns |
| Sessões em memória (se NiceGUI) vs escala | Média / Médio | Preferir API sem estado por ligação (opção B) |
| Experiência de «escolher pasta» não existe no browser | Certa / Baixo | Nome do ficheiro + descarregar ZIP |

### 6.2 Estimativa (1 programador, dias úteis)
| Fase | Conteúdo | **B** FastAPI + React/Vite | **A** NiceGUI |
|---|---|---|---|
| 0 | Extrair `rifas_core`: língua por pedido, log estruturado, bytes/temp em vez de `Path`, cancelamento; testes existentes a passar em Linux | 3 | 3 |
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
4. Mantém o motor testável isoladamente e a app Windows a funcionar com o mesmo pacote `rifas_core`.

**Porquê React + Vite (e o que custa):** o visor com zoom/pan, o painel da folha (recálculo ao vivo), o progresso em tempo real e o
tutorial com 8 páginas ganham com componentes e estado no cliente. Custo face ao HTMX: ≈ +1 dia na interface, ≈ +1 dia no CI
(build do frontend, imagem multi-stage) e uma cadeia Node (pnpm) a manter; em troca, a UI pode crescer (ex.: mais modos de folha) sem reescrever.

**Arquitetura-alvo:**
- `backend/` FastAPI (Python 3.13, uv) + pacote `rifas_core` (motor) + processo(s) de trabalho para o PDFium.
- `frontend/` React + Vite + TypeScript (pnpm); estado local (React) e *fetch*/SSE para a API; textos das 18 línguas servidos pela API em JSON.
- Uma imagem Docker multi-stage: *stage* Node faz `pnpm build`, *stage* Python serve a API **e** o frontend estático; contentor sem root.

**Quando A teria sido melhor:** ferramenta **estritamente interna** (poucos utilizadores, rede fechada, sem uploads de terceiros) — poupava ≈ 6 dias.

### Próximo passo sugerido
Fase 0 numa pasta nova (`webapp/` ou pacote `rifas_core` na raiz), **sem tocar em `app/`** até os testes do motor passarem em Linux (Docker/Rancher). Detalhe em `webapp/PLANO.md`.

---

## 7. Decisões tomadas e alojamento gratuito

| Tema | Decisão |
|---|---|
| Abordagem | B: FastAPI + React/Vite/TypeScript |
| Alojamento | Serviço **gratuito** (por escolher, abaixo) |
| Utilizadores | **Só o dono**: sem contas; acesso protegido por palavra-passe/token (ou espaço privado) |
| Repositório | GitHub **privado** `AndreNogueira/gerador-rifas` com `app/`, `webapp/`, `docs/` (criado) |
| Motor | **Partilhado** (`rifas_core`) entre a app Windows e a webapp |
| Pré-visualização | **PDF.js** no browser; o servidor devolve um PDF de 1 página (não PNG) |

**Opções gratuitas para uma imagem Docker (uso individual):**
| Serviço | Grátis | Prós | Contras |
|---|---|---|---|
| **Hugging Face Spaces (Docker)** | CPU 2 vCPU / 16 GB RAM; Spaces privados | Muita RAM, sem cartão, deploy por git; privado = só tu | Adormece após inatividade; URL do Hugging Face; limites de armazenamento efémero |
| **Render (Web Service free)** | 512 MB RAM, deploy do GitHub | Sem cartão, CI/CD automático a cada *push* | Adormece após 15 min (arranque ≈ 1 min); 512 MB limita pedidos grandes |
| **Google Cloud Run** | Quota mensal gratuita, escala a zero | Docker puro, robusto, deploy via GitHub Actions | Exige conta de faturação (cartão); risco de custos se mal configurado |
| Fly.io / Railway | Sem *free tier* real para contas novas | — | Pagos / créditos de teste |

**Recomendação:** Hugging Face Spaces (Docker, privado) pela RAM e por não precisar de cartão; alternativa: Render, se preferires
integração direta com o repositório GitHub. Qualquer escolha implica: ficheiros temporários só em disco efémero, limites de RAM/tempo
nos pedidos, e arranque a frio tolerado (é uso individual).
