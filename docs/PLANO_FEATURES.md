# Plano de implementação das novas funcionalidades, por dificuldade

Escrito para o dono do projeto, que escolhe quais fazer já. Junta as ideias de [`PLANO_PRODUTO.md`](PLANO_PRODUTO.md) e de [`ROADMAP.md`](ROADMAP.md) e ordena-as por **dificuldade** (esforço, risco e dependências), não por valor. As estimativas são minhas e servem para escolher, não são promessas.

**Como ler:** cada linha é **um PR** (ou dois), com o fluxo de `CONTRIBUTING.md` (`scripts/verificar.ps1` verde, testes, versão em `src/web/__init__.py`). **Tam.:** XS = uma tarde, S = um dia, M = uns dias, L = semanas, XL = um mês ou mais. **BD** = precisa da [base de dados](BASE_DE_DADOS.md). **Tu** = o que só tu podes dar ou decidir.

## Estado (2026-11-08)

Feitos todos os itens dos níveis 1 e 2 **exceto F8 e M9**, cada um num PR e com entrada no [Changelog](../src/web/CHANGELOG.md) do site.

| ID | Funcionalidade | Estado | Versão | PR | O que falta fazer a quem gere o serviço |
|---|---|---|---|---|---|
| F1 | Tema automático por época | feito | 3.10.0 | #15 | — |
| F2 | Remover `python-multipart` | feito | 3.10.0 | #15 | — |
| F3 | Funil no painel | feito | 3.11.0 | #16 | `ADMIN_TOKEN` (sem ele não há painel) |
| F4 | Lembrar os algarismos e o pedido | feito | 3.13.0 | #18 | — |
| F5 | Partilhar a configuração por ligação | feito | 3.13.0 | #18 | — |
| F6 | Instalar como app (PWA) | feito | 3.14.0 | #19 | — |
| F7 | Termos, Privacidade, Contacto e donativo | feito (textos **provisórios**) | 3.12.0 | #17 | `DONATIVO_URL`, `CONTACTO_EMAIL`, `RESPONSAVEL`; rever os textos com um advogado |
| F8 | Confirmar o proxy e o anti-sono no Render | **por fazer** | — | — | precisa do `ADMIN_TOKEN` e de 30 min sem visitas (ver `docs/ONLINE.md`) |
| M1 | Séries, prefixos e saltar números | feito | 3.15.0 | #20 | — |
| M2 | Exportar a lista (CSV) e folha de controlo | feito | 3.16.0 | #21 | — |
| M3 | Talão, marcas de corte e sangria | feito (talão e sangria já existiam; marcas novas) | 3.17.0 | #22 | — |
| M4 | Galeria de templates | feito (4 desenhos originais) | 3.18.0 | #23 | — |
| M5 | Marca própria (logótipo e cor) | feito | 3.19.0 | #24 | — |
| M6 | QR por bilhete | feito | 3.20.0 | #25 | `VERIFICACAO_CHAVE` (sem ela não há QR) e `PUBLIC_URL` certo |
| M7 | Sorteio verificável | feito | 3.21.0 | #26 | — |
| M8 | Testes e2e no CI | feito | — | #27 | — |
| M9 | Métricas persistentes | **por fazer** (espera a escolha da base de dados) | — | — | decidir (`BASE_DE_DADOS.md`) |
| M10 | Contraste dos temas | feito (medido, 9 temas × claro/escuro) | 3.22.0 | #28 | — |

**Depois (3.23.0 e app Windows 2.4.0, 2026-11-08):** cada funcionalidade de utilizador passou a ter **tópico no tutorial nas 18 línguas e vídeo em pt/en** (regra em `CLAUDE.md`, verificada por `tests/test_funcionalidades.py`);
o Changelog, os Termos, a Privacidade e o Contacto estão nas 18 línguas; e a app Windows ganhou o menu «Extras» com as funcionalidades M1–M5 e M7, a lista (CSV) e a folha de controlo (M2) e o visual Natal automático (F1).
Ficam só no site: o QR de verificação (M6: a chave que o assina não pode estar num `.exe` público), guardar/partilhar o pedido (F4/F5) e instalar como app (F6).

**Depois (3.24–3.25, 2026-11-08):** capturas do tutorial do site nas 18 línguas (`pnpm capturas`), **D4 feito** (SEO por língua: um URL por língua, `hreflang`, sitemap × 18), pré-visualização por PR (etiqueta `preview`, `docs/PREVIEW.md`), verificação do Google Search Console e monitor externo (`docs/ONLINE.md`).

**Ainda por fazer:** F8 (falta a prova dos 30 min), M9, o nível 3 sem D4 (D1–D3: contas, packs com Stripe, API para gráficas) e o nível 4. Fora do código: revisão **por falantes nativos** das traduções `web_*`, das de SEO e dos textos novos (≈ 100 chaves), mais volume por pedido.

## Quadro geral

| Nível | O que é | Itens | Precisa de BD? |
|---|---|---|---|
| **1. Fácil** | uma tarde a um dia, sem decisões externas, risco baixo | F1–F8 | não |
| **2. Média** | uns dias; mexe no motor ou em assets; testes novos | M1–M10 | só M9 (métricas persistentes) |
| **3. Difícil** | semanas; precisa de BD, de decisões de produto e de segurança | D1–D4 | **sim** |
| **4. Muito difícil / com risco** | produto novo ou risco legal | X1–X3 | sim |

## Nível 1 — Fácil (sem BD)

| ID | Funcionalidade | Tam. | Toca em | Notas e como se testa | Tu |
|---|---|---|---|---|---|
| F1 | **Tema automático por época** («Natal» em dezembro, se nunca escolheram um) | XS | `tema.ts`, `index.html` | só quando não há escolha guardada; teste com datas falsas | — |
| F2 | **Remover `python-multipart`** e limpar dependências | XS | `pyproject.toml`, `uv.lock` | `uv run pytest` verde | — |
| F3 | **Funil no painel** (sessão → template → pré-visualização → geração → descarga) | S | `metricas.py`, `Painel`, `graficos.tsx` | os eventos já existem; teste de privacidade mantém-se (só códigos e números) | — |
| F4 | **Lembrar o ficheiro dos algarismos e o último pedido** no browser | S | `sessao.tsx`, novo módulo IndexedDB | nada fica no servidor; Vitest com IndexedDB falso | — |
| F5 | **Partilhar a configuração por link** (campos no URL, nunca ficheiros) | S | `formulario.ts`, `rota.tsx` | ler/escrever os campos do pedido; validar com os mesmos limites | — |
| F6 | **Instalar como app (PWA)** | S | `service worker` novo, `index.html` | só guarda a «casca»; a geração precisa sempre do servidor | — |
| F7 | **Termos, Privacidade, Contacto e botão de donativo** | S | `paginas.tsx`, `seo.py` (`ROTAS`), 18 línguas | texto novo = 18 traduções e a contagem de chaves; páginas entram no sitemap | **o texto legal e o link do donativo** (MB Way/PayPal) |
| F8 | **Confirmar o proxy e o anti-sono no Render** | XS | só leitura do `/admin` | `FORWARDED_ALLOW_IPS=*` se o painel disser «problema» | **o `ADMIN_TOKEN` e 30 min sem visitas** |

## Nível 2 — Média

| ID | Funcionalidade | Tam. | Toca em | Notas e como se testa | Tu |
|---|---|---|---|---|---|
| M1 | **Séries, prefixos e saltar números** (A-0001, B-0001; cor por série) | M | `src/core` (`pedido.py`, `motor.py`), formulário | **mexe no core** (testes antes e depois, ver `CLAUDE.md`); a numeração é sequencial **por bloco** | — |
| M2 | **Exportar a lista de números** (CSV) e **folha de controlo de vendas** | M | `core`, `saida.py`, nova rota | CSV gerado a partir do mesmo `Trabalho`; verificar contra o PDF | — |
| M3 | **Talão e canhoto** (numeração dupla) e marcas de corte/sangria | M | `motor.py` (análise do template) | precisa de templates de teste do Canva com talão; risco de regressões na arrumação da folha | **um template com talão** |
| M4 | **Galeria de templates prontos** (3 a 5) | M | `core/galeria.py`, `rotas_galeria.py`, `Galeria.tsx` | **feito (3.18.0):** 4 desenhos originais criados com o reportlab, com os textos de quem usa; não precisou de templates do Canva nem de licenças | — |
| M5 | **Marca própria** (logótipo e cores da associação em todas as rifas) | M | `motor.py`, formulário | o logótipo é um upload como os outros (validar tipo real, tamanho); nada guardado | — |
| M6 | **QR por bilhete**, sem base de dados (o QR leva um código assinado) | M | `core`, biblioteca de QR, rota `/v/<código>` | verificação sem guardar nada: assina-se «série+número+evento» com uma chave do servidor; **⚠ escolher a biblioteca** | — |
| M7 | **Sorteio verificável** (semente pública, resultado partilhável) | M | nova página, rota | versão sem BD: o resultado vai no próprio link (assinado); com BD (D1) fica registado | **decidir a fonte da semente** (p.ex. drand) |
| M8 | **Testes e2e no CI** (Playwright: template → gerar → descarregar) | M | `.github/workflows/ci.yml`, `tests/e2e` | demora mais no CI; fixtures já existem | — |
| M9 | **Métricas persistentes** (as do painel sobrevivem ao adormecer) | M | `metricas.py` (SQLite → Postgres se houver `DATABASE_URL`) | **primeiro uso da BD**; sem `DATABASE_URL` tudo igual a hoje; testes contra Postgres no CI | **criar a conta e o `DATABASE_URL`** (ver `BASE_DE_DADOS.md`) |
| M10 | **Auditoria de contraste dos temas** (axe/Lighthouse) e acertar cores | M | `estilos/temas/_*.scss` | só variáveis (o teste de estrutura mantém-se); medir claro **e** escuro | — |

Fora do código mas na mesma categoria: **capturas do tutorial da web** (M, Playwright nas 18 línguas), **pré-visualização por PR** (M), **revisão nativa das traduções `web_*`** (S por língua, precisa de falantes), **mais volume por pedido** (M, mede-se primeiro no Render).

## Nível 3 — Difícil (precisa de BD)

| ID | Funcionalidade | Tam. | Depende de | Risco principal |
|---|---|---|---|---|
| D1 | **Contas e histórico** (guardar e duplicar rifas) | L | M9, `BASE_DE_DADOS.md` | dados pessoais (RGPD), sessões, recuperação de conta; **decidir: contas próprias ou as do Supabase** |
| D2 | **Packs pré-pagos com Stripe Checkout** (sem conta: código por e-mail) | L | M9, F7, conta Stripe | pagamentos, *webhooks* idempotentes, faturação, reembolsos; **parecer legal e contabilista** |
| D3 | **API e geração em lote** para gráficas | L | D1 (chaves de API) | abuso e custo de CPU; limites por chave; documentação |
| D4 | **SEO por língua** (`/en/`, `/es/`…, `hreflang`) | L | — (sem BD, mas muito texto) | 18 línguas de texto estático e sitemap; só vale a pena com tráfego |

## Nível 4 — Muito difícil ou com risco

| ID | Funcionalidade | Tam. | Porque fica para o fim |
|---|---|---|---|
| X1 | **Editor de templates no site** (sem Canva) | XL | produto novo; é um editor de PDF |
| X2 | **Página pública da rifa com reserva e pagamento de números** | XL | **evitar até haver parecer jurídico**: passa de «gerar bilhetes» a «operar a rifa» |
| X3 | **Integração com serviços de impressão** | M–L | depende de parceiros e de comissões |

## Ordem sugerida (ondas)

| Onda | Itens | Porquê | O que desbloqueia |
|---|---|---|---|
| **A. Limpar e medir** | F2, F3, F8, M10 | baratos; dizem onde as pessoas desistem e se o site é legível | decisões com dados |
| **B. Tirar fricção** | F4, F5, F1, F6, M1, M2 | o que traz quem volta todos os anos; M1 e M2 são os pedidos típicos das rifas | mais uso (e mais dados) |
| **C. Crescer** | M4, M5, M3 | a galeria ataca o maior obstáculo (o passo do Canva); marca própria e talão diferenciam | tráfego e boca-a-boca |
| **D. Base para cobrar** | M9, F7, M6, M7 | BD com o menor risco (métricas), páginas legais e funcionalidades que mais tarde se vendem | D1 e D2 |
| **E. Cobrar** | D2, D1, D3 | só com a onda D feita, parecer legal e contabilista | receita |
| **F. Depois** | D4, X1–X3 | só com procura comprovada | — |

**Primeiro passo recomendado:** a **onda A** (uma ou duas semanas de trabalho, quase sem decisões tuas), em paralelo com a **escolha da base de dados**, porque M9 depende dela e desbloqueia o resto.

## Dependências entre itens

- M9 → D1 → D3; M9 + F7 → D2.
- M6 e M7 funcionam **sem BD** (código assinado); com BD (D1) passam a poder registar verificações.
- M1, M2, M3, M5 mexem no `src/core`: **testes do core antes e depois** (`pytest` e `teste_folha`, `teste_canva`, `teste_5000`), em Windows e Linux.
- Qualquer texto novo para o utilizador = 18 línguas + contagem de chaves em `tests/test_i18n.py` e `tests/test_web_api.py`.

## O que preciso que decidas

1. **Que itens fazer já** (diz os IDs; sugiro a onda A, e a B por ordem).
2. **Base de dados** (ver [`BASE_DE_DADOS.md`](BASE_DE_DADOS.md)), para eu poder começar M9.
3. Para M3/M4: **templates** do Canva (com talão; os 3–5 da galeria), e se tens licença para os distribuir.
4. Para F7/D2: o texto legal, o link de donativo e quem emite as faturas (ver `PLANO_PRODUTO.md` §9).
