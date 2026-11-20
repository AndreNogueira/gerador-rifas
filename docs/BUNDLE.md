# O JS e o CSS que a app entrega

**Cache HTTP** (confirmado em produção, 2026-11-20): tudo em `dist/assets` (JS, CSS, letras dos temas) sai com `Cache-Control: public, max-age=31536000, immutable` — seguro porque o nome tem hash (o Vite muda-o se o conteúdo mudar). Os ficheiros de nome fixo que não vêm do Vite (miniaturas da galeria, ícones do preçário, `icone.svg`, `manifest.webmanifest`, as capturas e os vídeos do tutorial em `/ajuda`/`/videos`) saem com `Cache-Control: public, max-age=86400` (1 dia): nunca `immutable`, porque podem ser substituídos noutro deploy (p. ex. `gerar_miniaturas_galeria.py`, um vídeo regravado), mas já evitam o pedido inteiro a quem volta a ver a página no mesmo dia (antes de 2026-11-20 não tinham `Cache-Control` nenhum, só `ETag`/`Last-Modified`, que obrigava sempre a um pedido condicional). `index.html` e `/sw.js` continuam sem cache (`no-cache`), por desenho.

A app entrega ao browser **um só CSS e um só script ligado no `index.html`** (`dist/assets/index-*.js`, `style-*.css`), sem mapas, mais **três páginas que se carregam à parte, só quando se abre a página** (`Admin-*.js`, o painel do dono; `Editor-*.js`, o editor de templates; `Sorteio-*.js`, o sorteio: `src/preguicoso.ts`, `React.lazy`) e um pedaço pequeno que o principal partilha com elas (`jsx-runtime-*.js`, ligado no `index.html` com `modulepreload` para se pedir em paralelo). Quem só gera rifas não descarrega o código dessas três páginas: **o primeiro carregamento (JS + CSS, em brotli) passou de 151 KB para 115 KB (−24 %)**; o painel pesa 32 KB, o editor 8 KB e o sorteio 4 KB em brotli. Cada ficheiro vem e cada um já comprimido (`.br`, `.gz`). (Há ainda `dist/sw.js`, o *service worker* da PWA: um ficheiro à parte, legível, que as páginas não carregam como script, só registam com `?v=<versão>`; guarda a «casca» da app para abrir sem rede e **nunca** toca em `/api` (exceto os textos), `/health`, `/admin`, `/ajuda` e `/videos`. O servidor entrega-o com `Cache-Control: no-cache`.)
`pnpm build` encadeia: `tsc` → `vite build` → `scripts/comprimir-dist.mjs` → `scripts/verificar-dist.mjs`, que **falha** se:

- não houver exatamente 1 `.js` principal e 1 `.css` em `dist/assets`, ou o `index.html` não ligar 1 script e 1 folha de estilos, ou faltar um dos ficheiros das partes preguiçosas (`PARTES` em `verificar-dist.mjs`: uma parte nova tem de se acrescentar ali de propósito) ou o `index.html` ligar algum deles;
- houver um mapa (`.map`), um `<style>` embutido ou um `modulepreload` que não seja o do pedaço partilhado;
- faltar a versão `.br` ou `.gz` de algum JS/CSS, ou ela não descomprimir para o original;
- algum JS não estiver ofuscado (a chave `rifas.sessao` do nosso código aparece em claro).

**Armadilhas das páginas à parte:** (1) o ofuscador não pode esconder os caminhos dos `import("./Admin")` na tabela de cadeias, senão o empacotador deixa de os resolver e a página nem entra no `dist` (`reservedStrings` em `ofuscar.ts`; o verificador falha se faltar uma parte); (2) depois de um deploy os ficheiros com o nome antigo desaparecem: um separador já aberto falha ao carregar a página e `preguicoso.ts` recarrega-o UMA vez (marca na sessão, sem ciclos; `e2e/leve.spec.ts` simula-o); (3) a página inicial não pode pedir nenhuma das partes (o mesmo e2e verifica-o).

O CI e o `Dockerfile` correm o mesmo `pnpm build`. O servidor (`src/web/app.py`) escolhe a versão comprimida pelo `Accept-Encoding` e nunca serve `.map`, `.br` ou `.gz` como ficheiros soltos (`tests/test_web_estaticos.py`).

## Números (medidos em 2026-11-07, React 19.3, Vite 8)

| | JS bruto | JS na rede | CSS bruto | CSS na rede |
|---|---|---|---|---|
| **Antes** (3.5.0): sem compressão, com mapa de 1,1 MB publicado | 247,0 KB | 247,0 KB | 58,7 KB | 58,7 KB |
| **Agora** (3.8.0): ofuscado (`medio`), brotli | 299,2 KB | **83,4 KB** | 62,7 KB | **12,0 KB** |

O ficheiro **bruto** cresce 21 % (8 pontos são o código novo, como o painel de administração, e 12 a ofuscação: 268 → 299 KB); o que **viaja** cai 66 % (JS) e 80 % (CSS) porque antes não havia compressão nenhuma (nem o Render a faz por nós). O mapa deixou de existir: era publicado pela rota estática e mostrava o código-fonte todo, o que desfazia qualquer ofuscação.

### Quanto custa cada nível de ofuscação

Código atual (3.8.0), só se ofusca o código da app (`src/`):

| Nível | O que faz | JS bruto | gzip | brotli |
|---|---|---|---|---|
| `nenhum` | só minificado | 268,0 KB | 83,0 KB | 72,3 KB |
| `leve` | tabela de textos (a 75 % das cadeias) | 283,9 KB | 91,5 KB | 79,1 KB |
| **`medio`** (por omissão) | **todas** as cadeias numa tabela em base64, com rotação | 299,2 KB | 96,7 KB | 83,4 KB |

Se se ofuscasse **tudo, React incluído** (medido na 3.6.0, com menos código): `leve` +28 % (307 KB), `medio` +66 % (400 KB) e `forte` ×3,5 (833 KB). Por isso ofusca-se **só o código da app**: o React é público e ofuscá-lo só engorda o ficheiro. O nível «forte» (achatamento do fluxo e código morto) nem compila com o Rolldown (reatribui `const`). Para trocar o nível: `OFUSCAR_NIVEL=leve|nenhum pnpm build` (`pnpm medir` mede o `dist`).

O `medio` usa o limiar 1 (todas as cadeias): com 0,9 uma ou outra ficava em claro de build para build, e a verificação do `dist` falhava ao acaso.

## O que a ofuscação NÃO faz

Não esconde nada de quem queira ver o que o browser faz: as chamadas à API, os cabeçalhos e o comportamento são visíveis no separador *Rede*. A segurança está no servidor (limites, validação dos ficheiros, isolamento do motor); a ofuscação só dá trabalho a quem copia a interface.

## Para pesar ainda menos

O grosso do JS (≈ 190 KB) é o `react-dom`. Trocá-lo por **Preact** (`preact/compat`) pouparia mais de metade, mas deixa de ser React; ficou de fora por decisão do projeto (ver `CLAUDE.md`). As letras (ficheiros `.woff2`) só se descarregam as dos temas em uso.
