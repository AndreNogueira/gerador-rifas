# SEO

A webapp é uma SPA (React): sem cuidados, o HTML que o servidor entrega estaria vazio e só os robôs que correm JavaScript veriam alguma coisa. O que está feito, e como se verifica:

## O que o servidor entrega

`src/web/seo.py` + `src/web/app.py`. Para cada página conhecida (`/`, `/tutorial`, `/video`, `/sobre`) o servidor monta o `index.html` compilado com:

- **`<head>` próprio**: `<title>` (≤ 65 caracteres) e `description` (60–160) distintos por página, `robots`, **canónico**, **Open Graph** e **Twitter Card** (imagem 1200×630, `public/og-imagem.png`) e, na página inicial, **JSON-LD** `WebApplication` (grátis, 18 línguas, categoria utilitários).
- **Texto real no corpo** (`<div class="seo-estatico">` dentro de `#raiz`): um `h1` por página, os passos, e no `/tutorial` os 8 tópicos completos. O React substitui-o ao arrancar e o CSS esconde-o até lá (não se vê, mas redes sociais e robôs sem JS leem-no). Há também um `<noscript>`.
- **`/robots.txt`**: tudo aberto (incluindo o JS e o CSS, de que o Google precisa para desenhar a página), menos `/api/` e `/admin`, e a linha `Sitemap:`.
- **`/sitemap.xml`**: só as páginas públicas.
- **404 a sério**: qualquer rota que não exista devolve **404** (com `noindex` e sem canónico), em vez de uma página inicial com 200 («soft 404»). `/tutorial/` redireciona (301) para `/tutorial`, `/index.html` é a página inicial, e a query (`?p=3`) não conta.
- **`X-Robots-Tag: noindex`** na API e no `/health`.

No browser, `App.tsx` põe o `document.title` certo em cada página e língua (com os textos já traduzidos), e `<html lang>` acompanha a língua da interface. As imagens do tutorial têm `alt`.

## O URL público

O canónico, o Open Graph e o sitemap precisam do URL certo. Ordem: variável **`PUBLIC_URL`** (ex.: `https://gerador-rifas.onrender.com`; é só um URL, não um segredo) → no Render, o **`RENDER_EXTERNAL_URL`** que o próprio Render define → o do pedido (só em desenvolvimento: o cabeçalho `Host` vem do cliente, e `tests/test_web_seo.py` garante que com `PUBLIC_URL` um `Host` falso não passa para o HTML). **Se puseres um domínio próprio, define `PUBLIC_URL` com ele.**

## O que SÓ tu podes fazer

1. **Google Search Console**: adiciona o site (verificação por DNS ou por ficheiro/meta), submete `…/sitemap.xml` e pede a indexação da página inicial. Sem isto o Google demora (muito) a encontrar um site novo.
2. **Bing Webmaster Tools**: importa o site da Search Console.
3. Se o serviço **adormece** (plano gratuito do Render, 15 min), o primeiro pedido de um robô pode demorar ~1 min e dar *timeout*: ver «Para depois» abaixo.

## Como verificar

```
curl -s https://<o-teu-site>/ | head -40            # o <head> com título, descrição, canónico, og:*, JSON-LD
curl -s https://<o-teu-site>/robots.txt ; curl -s https://<o-teu-site>/sitemap.xml
curl -s -o /dev/null -w "%{http_code}\n" https://<o-teu-site>/nao-existe        # 404
```
Ferramentas: o *Rich Results Test* do Google (JSON-LD), o *URL Inspection* da Search Console (o que o Googlebot vê) e o depurador de partilha do Facebook/LinkedIn (a imagem). `uv run pytest tests/test_web_seo.py` cobre tudo o que é do servidor.

## Limites e para depois

- **Só há HTML em português** para os robôs (a língua da interface escolhe-se no browser, não no URL), por isso não há `hreflang` e o site compete em pesquisas em português. Para posicionar as outras 17 línguas fazia falta um URL por língua (`/en/`, `/es/`…) com o texto traduzido no HTML: é um incremento grande (ver `docs/ROADMAP.md`).
- **Conteúdo**: um motor de pesquisa premeia páginas com texto útil. Páginas de «como fazer» (rifas para a escola, para a associação, como imprimir) trariam tráfego; não estão feitas.
- **O arranque a frio** do plano gratuito (≈ 1 min) prejudica a pesquisa (o Google mede o tempo de resposta). Um pedido periódico externo ao `/health` mantém-no acordado, ou o plano pago.
- Os **Core Web Vitals** não foram medidos com o Lighthouse; o que ajuda já está feito (um só JS e CSS comprimidos, letras `font-display: swap`, ficheiros com cache de um ano).
