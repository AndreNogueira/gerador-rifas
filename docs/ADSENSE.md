# Anúncios (Google AdSense)

**Estado: desligado.** Nada da Google é carregado, nenhum bloco aparece e o `/ads.txt` dá 404 até o dono do serviço pôr as variáveis abaixo no Render.

> **AdSense ≠ Google Ads.** O *AdSense* é onde o site **ganha** dinheiro a mostrar anúncios de outros (é este). O *Google Ads* é onde se **paga** para promover o site: não leva código nenhum.

## O que se liga (variáveis do serviço no Render, nunca no repositório)

| Variável | Valor | O que faz |
|---|---|---|
| `ADSENSE_CLIENTE` | `ca-pub-1234567890123456` (o teu ID de editor) | Põe o script da Google no `<head>` das páginas públicas (verificação do site **e** mensagem de consentimento do EEE), serve o `/ads.txt` e muda o texto da Política de privacidade (18 línguas). Sem ela, nada disto existe. |
| `ADSENSE_SLOT` | só os algarismos do `data-ad-slot` (ex. `9876543210`) | Mostra o bloco de anúncios nas páginas da lista abaixo. Sem ele o site fica «ligado à Google» mas sem blocos (é o que se quer durante a aprovação). |

Valores inválidos são ignorados (`config.adsense_cliente()` / `adsense_slot()`), por isso um erro de escrita nunca estraga o site.

## Onde aparecem

**Um só bloco por página, no fim do conteúdo, por cima do rodapé** (largura total, até 960 px, com a palavra «Publicidade» por cima e 140 px de altura reservada: não há saltos, e some se a Google não tiver anúncio).

```
┌──────────────────────────────────────────────────────────────┐
│ ▓▓▓ cabeçalho / faixa do tema ▓▓▓                            │
├────────────────────────────┬─────────────────────────────────┤
│ 1 Template (PDF)           │ Pré-visualização                │
│ 2 Algarismos               │ (PDF.js)                        │
│ 3 Números                  │                                 │
│ 4 Gerar e descarregar      │                                 │
├────────────────────────────┴─────────────────────────────────┤
│                         PUBLICIDADE                          │   ← o único bloco
│  ┌────────────────────────────────────────────────────────┐  │     (página inicial)
│  │               anúncio responsivo da Google             │  │
│  └────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│ v3.28.0   Changelog · Termos · Privacidade · Contacto        │
└──────────────────────────────────────────────────────────────┘
```

| Página | Anúncio? | Porquê |
|---|---|---|
| `/` (o gerador) | **sim**, no fim da página (abaixo dos 4 passos e da pré-visualização) | é a página com mais visitas; fica longe de «Gerar» e «Descarregar» (a Google proíbe anúncios junto de botões, para não haver cliques por engano) |
| `/tutorial`, `/sobre`, `/sorteio`, `/changelog` | **sim**, no fim | páginas de leitura, com texto à volta |
| `/editor` | não | é uma ferramenta de arrastar: um anúncio ao lado da tela provocava cliques por engano |
| `/video`, `/termos`, `/privacidade`, `/contacto` | não | pouco conteúdo ou páginas legais |
| `/admin`, a página do QR (`/v/…`), o 404 | **nunca** | o painel é privado; a verificação e o 404 não têm conteúdo (a Google recusa anúncios assim); o script nem é carregado |
| PDFs/ZIP gerados, app Windows | **nunca** | os anúncios só existem no site |

As páginas estão em `PAGINAS_COM_ANUNCIO` (`Anuncio.tsx`); o script no `<head>` vem de `seo.cabecalho` (só páginas indexáveis, por isso nunca no painel nem no 404).

## Como preparar tudo com a Google (por esta ordem)

Nada disto se pode fazer por ti: a conta é tua, tem os teus dados fiscais e de pagamento.

1. **Conta AdSense** — <https://adsense.google.com>, com a conta Google que vais usar sempre. País: Portugal. Vai pedir o URL do site (o `PUBLIC_URL`, p.ex. `https://gerador-rifas.onrender.com`; **com um domínio próprio a aprovação é bem mais provável**: a Google recusa muitos subdomínios gratuitos), os teus dados e um método de pagamento. Os rendimentos de anúncios contam para o IRS: **fala com o contabilista antes** (`docs/PLANO_PRODUTO.md` §5).
2. **ID de editor** — em AdSense → *Conta* → *Informações da conta*: `pub-1234567890123456`. No Render (serviço → *Environment*), cria `ADSENSE_CLIENTE = ca-pub-1234567890123456` (o prefixo `ca-` é do nosso lado). O serviço reinicia e o site passa a ter o script e o `/ads.txt`.
3. **Verificar o site** — no AdSense, em *Sites*, adiciona o URL e escolhe *Fragmento de código AdSense* (já está no `<head>` desde o passo 2: carrega só em «Verificar»). Confirma em `https://<o-teu-site>/ads.txt` que aparece `google.com, pub-…, DIRECT, f08c47fec0942fa0`.
4. **Mensagem de consentimento (obrigatória em Portugal)** — AdSense → *Privacidade e mensagens* → *Consentimento europeu*: cria e **publica** a mensagem para o EEE, o Reino Unido e a Suíça (é a ferramenta de consentimento certificada da Google; escolhe «Consentir / Gerir opções» e ativa a ligação para reabrir as opções). Sem ela, a Google não serve anúncios a visitantes da UE. **Não escrevas um banner de cookies nosso**: o da Google é que conta.
5. **Esperar a revisão** (de dias a semanas). A Google exige conteúdo próprio e útil e navegação clara; o tutorial, os textos de SEO nas 18 línguas, a política de privacidade e os termos ajudam. Se recusarem por «pouco conteúdo», acrescenta páginas de «como fazer» (ver `docs/ROADMAP.md` #5).
6. **Criar o bloco** (depois de aprovado): AdSense → *Anúncios* → *Por unidade de anúncio* → *Anúncios de display* → nome «Fim de página», tipo **responsivo**. Do código que mostra, copia **só os algarismos** do `data-ad-slot`. No Render: `ADSENSE_SLOT = 9876543210`. Em 1–2 minutos os blocos aparecem nas páginas da tabela.
7. **Ver se funciona** — abre o site num browser **sem bloqueador de anúncios**: a mensagem de consentimento aparece (na UE), e depois do «Consentir» o bloco «Publicidade». Os primeiros dias podem mostrar o bloco vazio (e some sozinho, `unfilled`). O estado do `ads.txt` fica «Autorizado» em até 24 h.
8. **Regras que não se podem quebrar** (a conta é fechada): não cliques nos teus anúncios nem peças cliques; não ponhas anúncios junto de «Gerar»/«Descarregar»; não mudes o código do bloco; não ponhas mais blocos sem ler as políticas do programa.

**Para desligar:** apaga `ADSENSE_SLOT` (some o bloco) e `ADSENSE_CLIENTE` (some tudo, incluindo o texto de anúncios da privacidade).

## Privacidade e RGPD

Com `ADSENSE_CLIENTE` definida, `textos_legais.pagina("privacidade")` troca a 1.ª frase do Resumo («sem anúncios…»), a última frase do parágrafo «No seu browser» («sem cookies de publicidade…») e acrescenta a secção «Publicidade» (base legal: consentimento), nas 18 línguas (`legal_anuncios.py`; sem revisão nativa nem jurídica, como o resto dos textos legais). Sem a variável, os textos são os de sempre e continuam verdadeiros.

## Para quem mexe no código

- `config.adsense_cliente()` / `adsense_slot()`, `app.py` (`/ads.txt`, `Publico.anuncios_*`), `seo.cabecalho` (o `<script>`), `legal_anuncios.py`, `Anuncio.tsx` + `.anuncio` em `_cabecalho.scss`, `web_publicidade` (a palavra «Publicidade», 18 línguas).
- O bloco usa `--rodape-texto` para o rótulo (texto sobre o fundo da página, medido no teste de contraste dos temas) e não muda a estrutura com o tema.
- Testes: `tests/test_web_anuncios.py` (desligado por omissão, valores inválidos, script só nas páginas públicas, `/ads.txt`, privacidade nas 18 línguas) e `Anuncio.test.tsx`.
- O service worker nunca guarda nada da Google (só a «casca» do site).
