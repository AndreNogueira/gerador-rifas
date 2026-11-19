# SEO

A webapp é uma SPA (React): sem cuidados, o HTML que o servidor entrega estaria vazio e só os robôs que correm JavaScript veriam alguma coisa. O que está feito, e como se verifica:

## Uma página por língua

Cada língua tem o seu URL (`seo.caminho_na_lingua`): o **português sem prefixo** (`/`, `/tutorial`) e as outras 17 com ele (`/en`, `/ja/tutorial`; a inicial é `/en`, sem barra final). O servidor entrega o HTML **na língua do URL**: `<html lang>`, `<title>`, descrição, texto (`h1`, tutorial, Changelog, páginas legais), canónico, `og:locale`, JSON-LD e `Content-Language`, e em todas as páginas `<link rel="alternate" hreflang>` para as 18 línguas mais `x-default` (= português). O `sitemap.xml` lista cada página em cada língua, com as alternativas (`xhtml:link`).

- **Um URL sem prefixo é sempre português**: não se redireciona pelo `Accept-Language` (o robô veria uma língua só). No browser a interface segue o URL (`rota.tsx`: `/ja/tutorial` ganha à língua guardada, que ganha à do browser) e, ao mudar de língua, o URL passa a ter o prefixo certo (sem criar entrada no histórico); o português tira-o.
- `/pt/...` e as barras finais (`/en/`, `/en/tutorial/`) fazem 301 para o URL único; prefixos desconhecidos, `/en/admin` e o resto são 404 a sério. O painel `/admin` nunca tem prefixo.
- Os textos de SEO (título e descrição da inicial, descrições, introdução) estão em `src/web/seo_textos.py`, **fora** de `core.i18n` (só o servidor os usa: não vão para o browser nem mudam a contagem de chaves); o resto vem das chaves normais (`app_nome`, `tut_titulo`…). **Língua nova** = entrada em `seo_textos.CHAVES` (um teste exige as 18) e em `LINGUAS_COM_PREFIXO` de `rota.tsx` (outro teste confere com `seo.LINGUAS_URL`). Testes: `tests/test_web_seo_linguas.py`, `rota.test.tsx`, `i18n.test.tsx` e o e2e «cada língua tem o seu URL».

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

1. **Google Search Console**: adiciona uma propriedade do tipo **Prefixo do URL** (`https://gerador-rifas.onrender.com`; a de «Domínio» pede DNS e o `onrender.com` não é teu), verifica-a com a **etiqueta HTML** (copia só o valor do `content`, ex. `aB3…`, para a variável **`GOOGLE_VERIFICACAO`** do serviço no Render; o servidor escreve a `<meta name="google-site-verification">` na página inicial), submete `sitemap.xml` em *Sitemaps* e pede a indexação da página inicial em *Inspeção de URL*. Sem isto o Google demora (muito) a encontrar um site novo. Não tires a variável depois de verificar: o Google volta a conferir de tempos a tempos.
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

- **Traduções do SEO sem revisão nativa** (`src/web/seo_textos.py`, 15 textos × 18 línguas): títulos e descrições curtos, mas convém uma leitura por falantes. Os textos legais, o Changelog e o tutorial que vão no HTML já vêm das traduções do resto do site.
- **Conteúdo**: um motor de pesquisa premeia páginas com texto útil. Páginas de «como fazer» (rifas para a escola, para a associação, como imprimir) trariam tráfego; não estão feitas.
- **O arranque a frio** do plano gratuito (≈ 1 min) prejudica a pesquisa (o Google mede o tempo de resposta). Um pedido periódico externo ao `/health` mantém-no acordado, ou o plano pago.
- Os **Core Web Vitals** não foram medidos com o Lighthouse; o que ajuda já está feito (um só JS e CSS comprimidos, letras `font-display: swap`, ficheiros com cache de um ano).

## Textos de SEO editáveis na base de dados (por página e por língua)

Painel → **SEO por língua** (`/admin`, `src/web/frontend/src/AdminSeo.tsx`; API `GET|PUT|DELETE /api/admin/seo`). Edita-se, em cada língua: o título de cada página (`t_inicio`,
`titulo:<caminho>`), a descrição (`d_*`), os textos de apoio (`intro`, `como`...) e os **guias «como fazer»** (título, introdução, passos, dicas, fim). Sem novo deploy.

- Guarda-se em `seo_textos_bd(chave, lingua, valor)` (`src/web/seo_bd.py`): Postgres com `DATABASE_URL` (Neon), senão SQLite local e efémero (o painel avisa).
- **Lê-se de 15 em 15 minutos** em segundo plano (e no arranque; uma edição feita no painel aplica-se logo, porque `definir`/`repor` voltam a ler; assim o Neon gratuito pode adormecer entre leituras) para `seo_textos.SOBREPOSTOS`; nenhum pedido de página consulta a base. O código (`seo_textos.py`, `guias/`) continua a ser o valor por omissão
  e o recurso: base em baixo, texto editado inválido ou com `{parâmetros}` a mais → usa-se o do código, nunca se parte uma página.
- Valida-se ao gravar **e** ao ler, com as regras de `tests/test_web_seo_linguas.py`: título até 66 de largura (CJK conta dobro), descrição entre 50 e 158 (≤ 160 carateres), os mesmos
  `{parâmetros}` do original, sem quebras de linha (exceto nos textos longos), até 1000 carateres. O HTML escapa tudo.
- Uma língua nova (`docs/LINGUAS.md`) herda os textos do código; edita-se depois no painel. Testes: `tests/test_web_seo_bd.py`, `AdminSeo.test.tsx`.

## Índice dos guias e migalhas de pão

- **`/como-fazer`** (`guias.INDICE`, `seo.ROTAS`, `IndiceGuias.tsx`, `GET /api/guias`): lista todos os guias com título e resumo (a primeira frase da introdução, `guias.resumo`), nas 22 línguas e no HTML estático. Cada guia termina com «Outros guias» (ligações aos outros, nunca a si próprio) e «Todos os guias»: ligações internas para quem lê e para quem indexa. O menu «Ajuda» ganhou «Todos os guias» antes dos seis guias por público.
- **`BreadcrumbList`** (JSON-LD, `seo._migalhas`): Início › Como fazer › guia (e Início › Como fazer no índice), com os URLs de cada língua. Só nas páginas de guias e no índice.
- Guia novo = módulo em `guias/`, entrada em `guias.CAMINHOS`/`NOMES`, `d_guia_<nome>` e a chave `web_guia_<nome>` (o índice e as ligações saem sozinhos da lista; o menu do cabeçalho tem a sua lista em `MENU_COMO_FAZER`).
- **Dois tipos de guia** (`guias.PARA_PUBLICOS` e os de tema): **por público** (`/rifas-para-<nome>`: escolas, associações, clubes, bombeiros, festas, igrejas; o 1.º passo manda confirmar a licença na câmara municipal, testado) e **por tema**, que respondem a uma pergunta concreta, não a um público: `numerar` (`/como-numerar-bilhetes-de-rifa`), `sorteio` (`/sorteio-de-rifa-verificavel`, explica o método da página `/sorteio`) e `quantos` (`/quantos-bilhetes-de-rifa-fazer`). Os de tema têm as 22 línguas no próprio módulo (`guias/numerar.py`…), a frase final comum em `guias/comum.py`, o endereço em `guias.CAMINHOS`, **sem** entrada no menu «Ajuda» (chegam pelo índice, pelas ligações «Outros guias» e pelo sitemap; por isso não têm chave `web_guia_<nome>`) e nada de lei nem de moeda no texto. **Poucas páginas, cada uma com utilidade própria:** o Google desvaloriza muitas páginas quase iguais traduzidas em massa; um guia novo só entra se responder a uma pergunta que ainda não está respondida (o próximo candidato é o do preçário, `PLANO_PRECARIO.md`).

