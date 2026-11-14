# Roteiro: incrementos para fazer em PRs pequenos

**O plano comercial e as funcionalidades pensadas por valor (galeria de templates, séries, QR, sorteio verificável, contas, packs pagos) estão em [`PLANO_PRODUTO.md`](PLANO_PRODUTO.md).** Cada linha é um PR (ou dois). **Tamanho:** XS = uma tarde, S = um dia, M = uns dias, L = semanas. Escolhe uma, abre uma issue com o [modelo](../.github/ISSUE_TEMPLATE/funcionalidade.yml) e segue o [fluxo](../CONTRIBUTING.md). Está ordenado por valor a dividir pelo esforço, não por obrigação.

## Para o utilizador

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 1 | ~~**Lembrar o ficheiro dos algarismos**~~ (feito, 3.13) entre sessões | S | A app Windows lembra-o; aqui a sessão perde-o. Guardar no browser (IndexedDB) e reenviar ao servidor ao retomar. Nada fica no servidor. |
| 2 | ~~**Capturas do tutorial da web**~~ (feito, 3.24) | M | As atuais são da app Windows. Gerar com Playwright nas 18 línguas (`/api/tutorial/recorte`) e trocar `rotas_ajuda`. |
| 4 | ~~**Mais temas**~~ (feito, 3.26: Halloween, Praia, Jornal antigo, Terminal verde, Cartaz de circo) | S cada | `docs/TEMAS.md` tem a receita. |
| 5 | ~~**SEO por língua**~~ (feito, 3.25; páginas de «como fazer»: escolas e associações (3.30), clubes, bombeiros e festas de bairro (3.34), paróquias (3.36); faltam outras, p.ex. misericórdias, IPSS e juntas de freguesia) | L | Um URL por língua (`/en/`, `/es/`…) com o texto traduzido no HTML e `hreflang`: hoje só o português se posiciona (`docs/SEO.md`). Antes disso: páginas de «como fazer» (rifas para a escola, a associação…). |
| 6 | ~~**Instalar como app (PWA)**~~ (feito, 3.14) | S | O `manifest.webmanifest` e os ícones já existem; falta um *service worker* que guarde só a «casca» (a geração precisa sempre do servidor). |
| 7 | ~~**Partilhar a configuração por link**~~ (feito, 3.13) | S | Os campos (de, até, modo…) no URL; nunca os ficheiros. |

## Qualidade e segurança

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 10 | **Confirmar o proxy e o anti-sono no Render** | XS | O painel (`/admin`) diz se os IPs reais chegam («Proxy e limite por IP») e se o serviço está a chamar-se («Anti-sono»); falta olhá-los com visitantes e 30 min sem visitas. Se der «problema», definir `FORWARDED_ALLOW_IPS=*`. |
| 11 | ~~**Métricas que sobrevivem**~~ (feito: Postgres na Neon, confirmado em produção em 2026-11-13) | M | O disco do Render gratuito é efémero: disco persistente (pago) ou base externa para o histórico do painel (`docs/ADMIN.md`). |
| 12 | ~~**Medir no Render a sério**~~ (feito em 2026-11-13: `docs/MEDICOES.md`, `scripts/medir_render.py`) | S | Os tempos e o `MAX_NUMEROS` (30 000) partiram de um contentor com 0,1 CPU assumido; repetir no Render e ajustar. |
| 13 | **Revisão nativa das traduções `web_*`** | S por língua | Foram escritas sem falante nativo (11 chaves). |

## Plataforma

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 15 | ~~**Pré-visualização por PR**~~ (feito: etiqueta `preview`, `docs/PREVIEW.md`) | M | Um deploy efémero por PR (Render *Preview Environments* ou imagem `pr-<n>`). |
| 16 | ~~**Subir a app Windows para Python 3.15**~~ (feito na 2.5: `--selftest` igual, GUI testada em Tk 9; o `.exe` compilado: ver `app/README.md`) | M | |
| 17 | **Contas e pagamento** | L | O serviço será pago mais tarde. Desenhar antes os planos (limites por conta), a faturação e a proteção da privacidade dos ficheiros. |
| 18 | ~~**Observabilidade**~~ (feito: `docs/OBSERVABILIDADE.md`) | S | Registo estruturado dos pedidos e um painel de erros/tempos, sem guardar conteúdo dos ficheiros. |
| 19 | **Crescimento sem custo** | S | Plano em [`CRESCIMENTO.md`](CRESCIMENTO.md): Search Console/Bing, vídeos no YouTube, Pinterest, grupos e entidades; no código, o botão «Partilhar» (feito, 3.38), a ligação na página do QR e a assinatura opcional no bilhete (cada um com as 22 traduções). |
