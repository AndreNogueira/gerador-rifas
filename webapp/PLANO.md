# Webapp «Gerador de Rifas» — plano (rascunho para aprovar)

Decidido: **backend Python (FastAPI) + frontend React/Vite/TypeScript** (opção B do `docs/MIGRATION_PLAN.md`). Ferramentas: Node 22, pnpm, uv, git, `gh` e Rancher Desktop (docker).

## 1. Ideia
Os mesmos 4 passos da app Windows (template → algarismos → números → destino/nome), mas no browser: o utilizador carrega
o template (PDF do Canva) e o ficheiro dos algarismos, vê a pré-visualização e descarrega os PDFs (ZIP, ou um PDF só).
Inclui os dois modos do template (vários bilhetes por página / uma só rifa que enche a folha), 18 línguas, tutorial e vídeo.

## 2. Arquitetura
```
webapp/
  backend/   FastAPI (Python 3.13, uv)
    rifas/       <- motor copiado da app: core.py, pdftexto.py (sem tkinter), idiomas/ (textos)
    api.py       endpoints
    trabalhos.py fila de trabalhos + limpeza
  frontend/  React + Vite + TypeScript (pnpm)
  Dockerfile (backend + frontend estático), docker-compose.yml
  tests/     reutiliza os testes do motor (templates aleatórios + os do Canva)
```
- **Motor partilhado:** o `core.py` deixa de estar duplicado — extrair para um pacote `rifas_core` usado pela app Windows e
  pela webapp (decidir: pasta partilhada na raiz vs. copiar).
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
1. **Esqueleto** (backend FastAPI + frontend Vite a falar um com o outro, docker-compose a correr no Rancher).
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
- Estimativa revista: ≈ 25 dias úteis (±30 %).

- **Alojamento:** serviço **gratuito** (qual: ver «Em aberto»).
- **Público:** **só o dono** → sem contas de utilizador, mas o serviço fica atrás de uma palavra-passe/token (ou espaço privado do
  serviço); limites de segurança mantêm-se (tamanho, nº de números, tempo), sem *rate limiting* por IP sofisticado.
- **Repositório:** GitHub **privado** `AndreNogueira/gerador-rifas` (criado), com `app/`, `webapp/` e `docs/` (a raiz usa `.gitignore`
  que deixa de fora `final/`, `saida/`, `.venv`, `dist` e caches).
- **Motor:** **partilhado** — pacote `rifas_core` usado pela app Windows e pela webapp (a app passa a importá-lo; testes comuns).
- **Pré-visualização:** **PDF.js no browser**. O servidor gera um PDF de **1 página** com os primeiros números (`Documento` já
  faz isto; novo `pdf_da_previa()` em vez de `pagina_previa()` em PNG) e o browser desenha-o: zoom/pan nativos e nítidos a
  qualquer ampliação, menos carga no servidor. O template carregado vê-se logo no browser (PDF.js lê o ficheiro local, sem upload).
  Consequência: o visor passa a ser um componente React sobre PDF.js (`pdfjs-dist`, Apache-2.0) e o PNG a 200 dpi deixa de existir.

- **Alojamento:** **Render** (Web Service gratuito, Docker). Consequências de desenho:
  - **512 MB de RAM** e CPU partilhada → teto de números por pedido (≈ 100 000), geração em *streaming* para o ZIP, 1 trabalho de cada vez,
    1 processo de trabalho para o PDFium; ficheiros só em disco efémero (apagados após ~30 min; perdem-se ao reiniciar).
  - **Adormece após 15 min** sem uso (arranque ≈ 1 min): a página mostra «a acordar o servidor…» (frontend serve-se de ficheiros estáticos).
  - **Sem autenticação própria** no plano gratuito → a app pede uma **palavra-passe** (variável de ambiente `ACCESS_PASSWORD`, cookie assinado).
  - **Deploy automático:** ligar o repositório no painel do Render (autorizar a app GitHub no repo privado); *Auto-Deploy* a cada *push* para
    `main`, **só depois do CI passar** (GitHub Actions: testes do motor + build do frontend). Dockerfile na **raiz do repo** (contexto vê `app/` e `webapp/`).

## 8. Próximo passo
**Fase 0** (sem tocar no comportamento da app Windows): criar o pacote `rifas_core` (mover `core.py`, `pdftexto.py`, `i18n.py`, `idiomas/`),
com língua por pedido, log estruturado e entrada por bytes/temporários; a app Windows passa a importá-lo; correr `teste_folha`, `teste_canva`,
`teste_5000` em Windows **e** num contentor Linux (Rancher). Só depois a Fase 1 (API).
