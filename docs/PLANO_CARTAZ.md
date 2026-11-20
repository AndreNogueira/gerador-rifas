# Plano: cartaz da festa (anúncio do evento em PDF)

> **Estado (2026-11-20): proposta, por aprovar pelo dono.** Pedido do dono: depois de ter o preçário, as etiquetas de levantamento e os vales, falta
> o cartaz que anuncia a festa em si — o papel que se cola à porta, no placard da junta de freguesia ou da escola, com o nome do evento, a data, a
> hora e o local, no mesmo estilo visual do preçário (cores, logótipo, tema da época).

## 1. Porquê encaixa bem neste projeto

- **Mesmo público, um passo antes.** Quem usa o preçário e as etiquetas de levantamento (associações, escolas, bombeiros, paróquias, festas de bairro)
  precisa primeiro de anunciar o evento. É o mesmo cliente, só que mais a montante no calendário.
- **Quase tudo já existe.** Os 24 desenhos da galeria com cores por tema (`core/galeria.py`, `galeria_enfeites.py`), o logótipo (`core/marca.py`,
  reduzido a 480 px, já usado no preçário), as cores à escolha e o contraste automático (`precario._cor_realce`, `_cores`), as letras que cobrem as 23
  línguas (`core/letras.py`), o QR vetorial (`core/qr.py`, usa `segno`), o padrão de rota sem sessão (`rotas_precario.py`/`rotas_listas.py`) e o padrão
  de janela da app Windows (`app/extras.py`).
- **Liga as outras três funcionalidades da festa.** O cartaz pode trazer um QR para a ligação partilhada do preçário (`/precario?p=<id>`) ou para
  qualquer outro endereço (a página do evento, o Instagram, o grupo de WhatsApp) — dá-lhes uma razão a mais para usar o preçário com partilha.
- **SEO novo.** «Cartaz para festa de aldeira/escola/associação para imprimir» é uma pesquisa com volume que hoje o site não apanha; soma-se aos
  guias «como fazer» já existentes.
- **Sem contas, sem guardar nada.** Como o preçário e a galeria: só o que entra no PDF que se desenha; rascunho no browser.

## 2. O que é (e o que NÃO é)

É um **anúncio de uma só página** (não um folheto de várias páginas, não um programa detalhado como as etiquetas de levantamento ou os vales).
Pensado para se imprimir em A4 ou A3 e pregar numa porta, num placard, numa vitrine. **Não** substitui o preçário (que lista artigos e preços) nem as
etiquetas (que organizam o levantamento durante o evento): anuncia que o evento existe, quando e onde é.

## 3. O que o utilizador vê (fluxo)

1. **Ocasião e tema.** Os mesmos cartões de tema do preçário (reutilizam os 24 desenhos da galeria); o da época aparece primeiro e destacado.
2. **Texto do cartaz.** Título (nome da festa, obrigatório), subtítulo opcional (p. ex. «Festa de Verão da Associação X»), data, hora (ou um intervalo,
   «a partir das 20h»), local (texto livre — endereço ou só o nome do lugar), e um bloco de **até 4 linhas livres** para o que mais interessar
   («Entrada livre», «Música em direto», «Haverá rifa e tômbola», «Traga a sua cadeira»). Tudo opcional menos o título.
3. **Cores e logótipo.** O mesmo seletor de cores e logótipo do preçário (`CoresELogo.tsx`): cor principal, de destaque, papel; logótipo no
   cabeçalho ou no rodapé. Reaproveita-se o componente, não se escreve de novo.
4. **Ligação (opcional).** Um QR com um endereço à escolha — o do preçário partilhado (um botão «usar a ligação do meu preçário» quando já exista
   uma), ou qualquer outro `https://` que o utilizador escreva — com uma legenda curta por baixo («preçário e lista de preços», «mais informações»…).
5. **Formato.** A4 ou A3, vertical (o cartaz é sempre vertical — vd. D4).
6. **Pré-visualização a cada alteração** e **descarregar PDF** (e PNG para partilhar no WhatsApp/Facebook, como as etiquetas).

## 4. Decisões que quero que reveja (com a minha recomendação)

| # | Decisão | Opções | Recomendação |
|---|---|---|---|
| D1 | **Temas** | (a) os 24 da galeria/preçário tal como estão; (b) um conjunto próprio, mais "cartaz", com composições maiores (faixas largas, fundo cheio) | **(a) para a 1.ª versão**, reaproveitando `_desenho`/cores do preçário (o cartaz é uma folha só, cabe bem na mesma linguagem visual); um motivo «cartaz» por tema (faixa larga do título, moldura) fica para depois, só se o aspeto da 1.ª versão não convencer. |
| D2 | **QR** | (a) só a ligação do preçário partilhado; (b) qualquer URL `https://` à escolha; (c) sem QR nesta 1.ª versão | **(b)**, com (a) como atalho: um botão preenche automaticamente a ligação do preçário partilhado mais recente (se existir no `localStorage`), mas o campo aceita qualquer `https://`. Gera-se com `segno` diretamente (como a verificação, mas **sem** a assinatura HMAC: não há nada a verificar, é só um QR normal para abrir um endereço). |
| D3 | **Tamanho** | A4, A3, A2 | **A4 e A3** só (A2 pouco comum nas impressoras de casa/escritório; quem precisar de maior amplia na fotocopiadora, como hoje acontece com os outros PDFs). |
| D4 | **Orientação** | vertical / horizontal / as duas | **Vertical só.** Um cartaz de porta é sempre vertical; simplifica o motor de disposição (sem ramificação a testar) e evita um 2.º layout a manter. |
| D5 | **Programa/horário** (lista «20h abertura · 21h jantar · 23h sorteio da rifa») | já / depois | **Depois.** A 1.ª versão tem só o bloco de 4 linhas livres (D3 do fluxo), que já serve este caso escrito à mão; uma lista estruturada com horas fica para uma 2.ª fase se pedirem. |
| D6 | **Sem sessão, rascunho no browser** | como o preçário / sessão como as rifas | **Sem sessão**, rascunho em `localStorage` (`rifas.cartaz`), exatamente como o preçário e o editor. |

## 5. Desenho técnico

### 5.1 Núcleo (`src/core`, sem UI, partilhado pelas duas apps)

- **`cartaz.py`** (novo) — modelo `Cartaz(titulo, subtitulo, data_hora, local, linhas, desenho, cores, logo, logo_lugar, link, link_legenda, formato)`.
  - `titulo` (obrigatório, até ~60 letras — encolhe a letra até um mínimo e depois corta com reticências, como os nomes compridos do preçário/etiquetas).
  - `data_hora`, `local`: texto livre curto (até ~80 letras cada); **não validamos datas nem endereços a sério** (como o resto do projeto, nada se afirma).
  - `linhas`: até 4 linhas livres (até ~60 letras cada).
  - `desenho`: um dos 24 da galeria (reaproveita `precario.DESENHOS`/`POR_ID` ou o equivalente da galeria).
  - `cores`, `logo`, `logo_lugar`: **exatamente os mesmos tipos e regras do preçário** (`precario.Precario.cores`/`.logo`/`.logo_lugar`, `_cor_realce`,
    `_desenho` com o `replace`); não se duplica a lógica, importa-se de `precario.py` ou extrai-se para um módulo comum (`core/aspeto.py`?) se o preçário
    e o cartaz passarem a precisar dos dois da mesma forma — decidir ao implementar, conforme o quanto realmente se partilha.
  - `link` (URL `https://`, opcional) + `link_legenda` (texto curto); `validar` recusa um `link` que não seja `https://` bem formado.
  - `formato`: `A4` | `A3`.
  - `de_dict`/`para_dict`: formato da API e do rascunho, como o preçário.
  - **Nada disto se guarda no servidor** além do que entra no PDF desenhado nessa chamada (como o preçário e a galeria); o logótipo nunca vai para o
    `.cartaz` nem para a ligação partilhada, tal como no preçário.
  - Desenho de uma só página: título em letra grande (a maior do projeto, a encolher até caber em 1–2 linhas), faixa decorativa do tema por cima e/ou
    por baixo (reaproveita `galeria_enfeites`), data/hora/local destacados a meio, bloco das linhas livres, QR num canto inferior com a legenda, logótipo
    no cabeçalho ou no rodapé.
- **QR genérico**: `core/qr.py` ganha uma função `modulos_url(url: str) -> list` (ou equivalente) que chama `segno` diretamente com a URL, sem o HMAC
  da verificação de bilhetes — **um módulo novo pequeno**, não se reaproveita `qr.url`/`qr.codigo` (que são especificamente para a verificação de rifas).

### 5.2 Web (`src/web`)

- `rotas_cartaz.py` (novo, prefixo `/api/cartaz`): `POST /previa.png` (`leve`, desenhado no processo do motor como a pré-visualização do preçário/galeria),
  `POST /pdf` e `/png` (descarga, `pesado`). Corpo em JSON (`PedidoCartaz`), limites de tamanho como `rotas_precario.py`.
  - Partilha por ligação: **não na 1.ª versão** (o cartaz raramente precisa de ser reaberto por outra pessoa; o PNG/PDF descarregado já é a partilha).
    Reconsiderar só se pedirem.
- **Métricas só agregadas** (evento `cartaz`): tema, formato, com/sem QR, com/sem logótipo. **Nunca** o título, a data, o local nem a ligação do QR;
  teste de privacidade como nos outros eventos (`tests/test_web_metricas_privacidade...`).
- Frontend: `Cartaz.tsx` (+ estilos em `_cartaz.scss`), página `/cartaz` em `seo.ROTAS` (`d_cartaz`, 23 línguas) e `App.tsx`; item no cabeçalho
  (menu «Extras», ao lado do preçário/etiquetas/vales) — regra do `CLAUDE.md`: `ItemId` em `ORDEM`/`SAI_PRIMEIRO` **e** versão no menu hambúrguer.
  Reaproveita `CoresELogo.tsx` tal como está (mesmas props, origem diferente).
  - **Peso**: página preguiçosa (`preguicoso.ts`, `PARTES` em `verificar-dist.mjs`, `e2e/leve.spec.ts`), como o editor/precário/sorteio.

### 5.3 App Windows (`app/`)

- Janela **«Cartaz»** no menu «Extras» (`app/extras.py`, mesmo molde da `Etiquetas`/`Precario`): tema, texto, cores/logótipo (reaproveita os widgets já
  feitos para o preçário), pré-visualização PNG desenhada por `core`, «Guardar PDF…». Rascunho num ficheiro **`.cartaz`** (só os campos, nunca logótipo,
  como o `.precario`).
- Lógica toda em `src/core` (testável sem janelas); testes em `tests/test_cartaz.py` (core) e um bloco em `app/testes/teste_extras.py`.
- **Não publico o `.exe`** sem o seu «sim» (regra do `CLAUDE.md`).

### 5.4 Regras do projeto que isto obriga a cumprir

Funcionalidade de utilizador = **tópico no tutorial** (`FUNCIONALIDADES`, 23 línguas) + **vídeo web e Windows em pt e en** + **entrada no Changelog**
(pt + 21) + chaves de interface nas 23 línguas (contagens em `tests/test_i18n.py`/`tests/test_web_api.py`) + nada de novo na Política de privacidade
além de confirmar que o cartaz não guarda nada (como o preçário).

## 6. Fases (cada uma = um PR, com testes e CI verde)

| Fase | Entrega | Tam. | Critério de «feito» |
|---|---|---|---|
| **0** | Esta página revista; decisões D1–D6 fechadas | — | O dono aprova ou corrige |
| **1** | `core/cartaz.py`: modelo, validação, `de_dict`/`para_dict`, `qr.modulos_url` | S | Testes com título vazio/comprido, link inválido, 0–4 linhas livres |
| **2** | Disposição de 1 página (A4, **um** tema primeiro, p. ex. Quermesse) | M | PDF com título a encolher até caber, QR legível a 300 dpi, abre no PDFium |
| **3** | Estender aos 24 temas + cores/logótipo (reaproveitando `precario._desenho`/`_cor_realce`) | M | Teste por tema e com texto nas 23 línguas (nomes longos, CJK, línguas sem letra → inglês) |
| **4** | API web (`rotas_cartaz.py`) + métricas + teste de privacidade | S | `POST /previa.png`, `/pdf`, `/png`; limites; evento sem texto |
| **5** | Página `/cartaz` (React, rascunho em `localStorage`, página preguiçosa, menu) **e janela «Cartaz» da app Windows** (`.cartaz`), tutorial + vídeos (pt/en, web e Windows) + Changelog (pt + 21) + `CLAUDE.md`/`docs/` | L | Fluxo completo no telemóvel e no ecrã grande; `teste_extras.py` valida o mesmo cartaz na app Windows |
| **6** | SEO: `/cartaz` em `seo.ROTAS`, texto estático, ligação cruzada com o preçário e os guias de rifas existentes | S | Larguras de `test_web_seo_linguas`; sitemap atualizado |

**Ordem de valor:** 1–3 dão o motor e o aspeto (o que mais decide se vale a pena); 4–5 põem-no nas duas plataformas; 6 traz visitas.

## 7. Riscos

- **Aspeto.** Como no preçário: mostro o PDF de **um** tema antes de estender aos 24.
- **Texto que não cabe** (títulos longos em alemão, CJK): encolher a letra até um mínimo, nunca cortar sem reticências; testar com os piores casos.
- **QR para qualquer URL**: validar `https://` bem formado; **não** verificamos se o endereço existe ou é seguro (como os links que já se partilham
  noutros sítios do projeto) — dizer isto no tutorial.
- **Sobreposição com o preçário/etiquetas na cabeça do utilizador**: nomear bem no menu («Cartaz da festa» vs. «Preçário» vs. «Etiquetas de
  levantamento») e, no guia, explicar a ordem (primeiro o cartaz para anunciar, depois o preçário e as etiquetas no próprio dia).

## 8. Decisões já tomadas pelo dono

Nenhuma ainda — secção 4 (D1–D6) está por aprovar.
