# Acrescentar uma língua

O site e a app Windows têm **22 línguas** (`core.i18n.LINGUAS`). As 18 primeiras vivem espalhadas por vários ficheiros «um texto com todas as línguas lado a lado»; as quatro mais
recentes (**catalão `ca`, ucraniano `uk`, indonésio `id`, vietnamita `vi`**) foram feitas de outra maneira, mais simples, e é a que se usa daqui em diante: **um ficheiro por língua**.
Sem revisão por falantes nativos (o aviso das páginas legais diz que, havendo divergência, vale o português).

## Uma língua DERIVADA: o português do Brasil (`pt-br`)

A 23.ª entrada do seletor (a seguir ao português de Portugal) **não é uma tradução à mão**: deriva-se do `pt` por `core/ptbr.py` (glossário: ficheiro→arquivo, descarregar→baixar, ecrã→tela, ligação→link com o artigo no género certo,
«carregue em»→«clique em», «a gerar»→«gerando», câmara municipal→prefeitura, RGPD→LGPD…), por isso **um texto novo em `pt` já sai em `pt-br`** sem nada a fazer. Onde fica cada coisa:
`idiomas/pt_br.py` (nome e `OVERRIDES` por chave), `legal/pt_br.py` (páginas legais derivadas + as frases que citam a lei), e uma linha `["pt-br"] = derivar…` no fim de `seo_textos.py`, `guias/__init__.py`,
`legal_anuncios.py`, `legal_opiniao.py`, `legal_partilhas.py` e `legal_medicoes.py`; o changelog deriva-se do `CHANGELOG.md` ao ler (sem ficheiro nem resumo a escrever). As capturas e os vídeos do tutorial são os do português
(`tutorial.SEM_CAPTURAS_PROPRIAS`). O URL tem prefixo `/pt-br/`, o `hreflang` e o `<html lang>` levam `pt-BR` (`i18n.bcp47`) e o `Accept-Language: pt-BR` escolhe-o (`pt-PT` e `pt` continuam a dar o de Portugal).
**Quando uma frase de Portugal sai mal no Brasil:** acrescentar uma regra a `ptbr.FRASES`/`PALAVRAS` (vale para tudo) ou, só para uma chave, a `OVERRIDES`; `tests/test_ptbr.py` tem a lista negra de palavras de Portugal
(`ptbr.LISTA_NEGRA`) que nenhum texto derivado pode ter. Sem revisão por brasileiros nem jurídica das páginas legais: ver `PLANO_PTBR.md`.

## Lista (por esta ordem)

1. **Interface e tutoriais** — `src/core/idiomas/<lg>.py` com `NOME` (o nome da língua nela própria) e `T` com **todas** as chaves de `i18n.TEXTOS["en"]` (hoje 293), mesmos `{parâmetros}` e mesmo
   número de linhas nos textos longos. Copiar `ca.py` e traduzir; registar em `idiomas/__init__.py` (`import`, `ORDEM`, `_MODULOS`). `tests/test_i18n.py` verifica chaves e parâmetros.
   (`id` importa-se como `id_`: o nome do módulo esconde o `id` do Python.)
2. **Páginas legais** — `src/web/legal/<lg>.py`: `FRASES`, `AVISO`, `TEXTOS` (Termos, Privacidade, Contacto, mesmas secções e parágrafos que `pt.py`), mais `ANUNCIOS` (texto da privacidade quando há
   anúncios) e `PARTILHAS` (secção dos desenhos partilhados quando há base de dados). Juntar o código a `LINGUAS_NOVAS` em `legal/__init__.py`.
3. **Changelog** — `src/web/changelog/<lg>.md`: um resumo de **todas** as versões, com as mesmas versões, secções e nº de itens que o `CHANGELOG.md` (o teste falha se faltar algo).
   A cada versão nova, escreve-se o resumo em todas as línguas.
4. **SEO** — `src/web/seo_textos_novas.py` (título e descrições de cada página, `intro`, etc., e `LOCALE_OG`) e `src/web/guias/novas.py` (os seis guias «como fazer»: `ESCOLAS`, `ASSOCIACOES`, `CLUBES`, `BOMBEIROS`, `FESTAS`, `IGREJAS`). Larguras: título (já com « | nome da app») ≤ 66, descrição entre 50 e
   158 (carateres chineses/japoneses/coreanos contam dobro): `tests/test_web_seo_linguas.py`. Depois do deploy os textos podem ser afinados no painel (**SEO por língua**), sem tocar no código.
5. **Frontend** — a língua em `LINGUAS_COM_PREFIXO` de `src/web/frontend/src/rota.tsx` (mesma ordem que `core.i18n.LINGUAS`; um teste confere com o servidor) e em `e2e/capturas.spec.ts`.
6. **Capturas do tutorial** — do site: `pnpm build && pnpm capturas <lg>` (`<lg>_wa|wb|wc.png` + zonas em `app/assets/ajuda/ajuda.json`); da app Windows (precisa de ecrã, não mexer no rato):
   `cd app && .venv\Scripts\python.exe testes\fazer_ajuda.py <lg>` (`<lg>_a|b|c.png`). Os vídeos continuam só em pt e en.
7. **Texto «N línguas»**: `seo_textos` (`intro`), README, CLAUDE.md, changelog (nunca nas versões antigas: eram verdade na altura) e o número em `tests/test_web_api.py`.

## Verificar

```
uv run python -c "import sys; sys.path.insert(0,'src'); from core import i18n; print(len(i18n.LINGUAS))"
uv run pytest tests/test_i18n.py tests/test_traducoes_paginas.py tests/test_web_seo_linguas.py tests/test_web_guias.py tests/test_tutorial_e_autoteste.py -q
```

## Limites conhecidos

- **Galeria e editor de templates** desenham com as letras de `core.letras` (`docs/LETRAS.md`): Vera, DejaVu (latim estendido, vietnamita, grego, cirílico) e Noto Sans de chinês, japonês e coreano. Falta o **hindi** (devanágari precisa de «shaping») e o árabe/hebraico: um texto com essas letras dá aviso em vez de uma imagem estragada. A interface, as páginas e os PDFs gerados a partir de templates do Canva não dependem disto.
  (ạ, ế, ữ…) não se podem escrever nos desenhos: o site e a app avisam (`err_galeria_texto`, `err_editor_letra`). A interface, o tutorial e os PDFs gerados não dependem disso.
- A folha de controlo de vendas (PDF) usa Helvetica (WinAnsi): em línguas com letras fora dela (ucraniano, vietnamita…) os títulos saem em inglês (`controlo.texto_cabe`).
- Nenhum falante nativo reviu estes textos: pedir revisão antes de divulgar numa comunidade.
