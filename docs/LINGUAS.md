# Acrescentar uma língua

O site e a app Windows têm **22 línguas** (`core.i18n.LINGUAS`). As 18 primeiras vivem espalhadas por vários ficheiros «um texto com todas as línguas lado a lado»; as quatro mais
recentes (**catalão `ca`, ucraniano `uk`, indonésio `id`, vietnamita `vi`**) foram feitas de outra maneira, mais simples, e é a que se usa daqui em diante: **um ficheiro por língua**.
Sem revisão por falantes nativos (o aviso das páginas legais diz que, havendo divergência, vale o português).

## Lista (por esta ordem)

1. **Interface e tutoriais** — `src/core/idiomas/<lg>.py` com `NOME` (o nome da língua nela própria) e `T` com **todas** as chaves de `i18n.TEXTOS["en"]` (hoje 293), mesmos `{parâmetros}` e mesmo
   número de linhas nos textos longos. Copiar `ca.py` e traduzir; registar em `idiomas/__init__.py` (`import`, `ORDEM`, `_MODULOS`). `tests/test_i18n.py` verifica chaves e parâmetros.
   (`id` importa-se como `id_`: o nome do módulo esconde o `id` do Python.)
2. **Páginas legais** — `src/web/legal/<lg>.py`: `FRASES`, `AVISO`, `TEXTOS` (Termos, Privacidade, Contacto, mesmas secções e parágrafos que `pt.py`), mais `ANUNCIOS` (texto da privacidade quando há
   anúncios) e `PARTILHAS` (secção dos desenhos partilhados quando há base de dados). Juntar o código a `LINGUAS_NOVAS` em `legal/__init__.py`.
3. **Changelog** — `src/web/changelog/<lg>.md`: um resumo de **todas** as versões, com as mesmas versões, secções e nº de itens que o `CHANGELOG.md` (o teste falha se faltar algo).
   A cada versão nova, escreve-se o resumo em todas as línguas.
4. **SEO** — `src/web/seo_textos_novas.py` (título e descrições de cada página, `intro`, etc., e `LOCALE_OG`) e `src/web/guias/novas.py` (os cinco guias «como fazer»: `ESCOLAS`, `ASSOCIACOES`, `CLUBES`, `BOMBEIROS`, `FESTAS`). Larguras: título (já com « | nome da app») ≤ 66, descrição entre 50 e
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

- **Galeria e editor de templates** desenham com a letra Vera (a que vem com o reportlab): só tem o alfabeto latino básico, por isso textos em ucraniano (cirílico) e várias letras do vietnamita
  (ạ, ế, ữ…) não se podem escrever nos desenhos: o site e a app avisam (`err_galeria_texto`, `err_editor_letra`). A interface, o tutorial e os PDFs gerados não dependem disso.
- A folha de controlo de vendas (PDF) usa Helvetica (WinAnsi): em línguas com letras fora dela (ucraniano, vietnamita…) os títulos saem em inglês (`controlo.texto_cabe`).
- Nenhum falante nativo reviu estes textos: pedir revisão antes de divulgar numa comunidade.
