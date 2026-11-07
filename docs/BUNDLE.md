# O JS e o CSS que a app entrega

A app entrega ao browser **um só ficheiro de JS e um só de CSS** (`dist/assets/index-*.js`, `style-*.css`), sem mapas, e cada um já comprimido (`.br`, `.gz`). `pnpm build` encadeia: `tsc` → `vite build` → `scripts/comprimir-dist.mjs` → `scripts/verificar-dist.mjs`, que **falha** se:

- não houver exatamente 1 `.js` e 1 `.css` em `dist/assets`, ou o `index.html` não ligar 1 de cada;
- houver um mapa (`.map`), um `<style>` embutido ou um `modulepreload`;
- faltar a versão `.br` ou `.gz` do JS/CSS, ou ela não descomprimir para o original;
- o JS não estiver ofuscado (a chave `rifas.sessao` do nosso código aparece em claro).

O CI e o `Dockerfile` correm o mesmo `pnpm build`. O servidor (`src/web/app.py`) escolhe a versão comprimida pelo `Accept-Encoding` e nunca serve `.map`, `.br` ou `.gz` como ficheiros soltos (`tests/test_web_estaticos.py`).

## Números (medidos em 2026-11-07, React 19.3, Vite 8)

| | JS bruto | JS na rede | CSS bruto | CSS na rede |
|---|---|---|---|---|
| **Antes** (3.5.0): sem compressão, com mapa de 1,1 MB publicado | 247,0 KB | 247,0 KB | 58,7 KB | 58,7 KB |
| **Agora**: ofuscado (`medio`), brotli | 268,5 KB | **74,0 KB** | 58,7 KB | **11,3 KB** |

O ficheiro **bruto** cresce 9 % com a ofuscação; o que **viaja** cai 70 % (JS) e 81 % (CSS) porque antes não havia compressão nenhuma (nem o Render a faz por nós). O mapa deixou de existir: era publicado pela rota estática e mostrava o código-fonte todo, o que desfazia qualquer ofuscação.

### Quanto custa cada nível de ofuscação

| Nível | O que ofusca | JS bruto | gzip | brotli |
|---|---|---|---|---|
| `nenhum` | — (só minificado) | 240,6 KB | 74,5 KB | 64,6 KB |
| `leve` | o nosso código: tabela de textos | 251,7 KB | 80,1 KB | 69,3 KB |
| **`medio`** (por omissão) | o nosso código: textos em base64, rotação | 262,1 KB | 83,4 KB | 72,1 KB |
| — | tudo, React incluído, `leve` | 307,3 KB | 98,5 KB | 83,5 KB |
| — | tudo, React incluído, `medio` | 400,1 KB | 141,1 KB | 118,9 KB |
| — | tudo, React incluído, `forte` | 832,7 KB | 328,4 KB | 287,6 KB |

Por isso ofusca-se **só o código da app** (`src/`): o React é público e ofuscá-lo só engorda o ficheiro. O nível «forte» (achatamento do fluxo e código morto) nem compila com o Rolldown (reatribui `const`). Para trocar o nível: `OFUSCAR_NIVEL=leve|nenhum pnpm build` (`scripts/medir-js.mjs` mede o `dist`).

## O que a ofuscação NÃO faz

Não esconde nada de quem queira ver o que o browser faz: as chamadas à API, os cabeçalhos e o comportamento são visíveis no separador *Rede*. A segurança está no servidor (limites, validação dos ficheiros, isolamento do motor); a ofuscação só dá trabalho a quem copia a interface.

## Para pesar ainda menos

O grosso do JS (≈ 190 KB) é o `react-dom`. Trocá-lo por **Preact** (`preact/compat`) pouparia mais de metade, mas deixa de ser React; ficou de fora por decisão do projeto (ver `CLAUDE.md`). As letras (ficheiros `.woff2`) só se descarregam as dos temas em uso.
