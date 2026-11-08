# Roteiro: incrementos para fazer em PRs pequenos

**O plano comercial e as funcionalidades pensadas por valor (galeria de templates, séries, QR, sorteio verificável, contas, packs pagos) estão em [`PLANO_PRODUTO.md`](PLANO_PRODUTO.md).** Cada linha é um PR (ou dois). **Tamanho:** XS = uma tarde, S = um dia, M = uns dias, L = semanas. Escolhe uma, abre uma issue com o [modelo](../.github/ISSUE_TEMPLATE/funcionalidade.yml) e segue o [fluxo](../CONTRIBUTING.md). Está ordenado por valor a dividir pelo esforço, não por obrigação.

## Para o utilizador

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 1 | **Lembrar o ficheiro dos algarismos** entre sessões | S | A app Windows lembra-o; aqui a sessão perde-o. Guardar no browser (IndexedDB) e reenviar ao servidor ao retomar. Nada fica no servidor. |
| 2 | **Capturas do tutorial da web** | M | As atuais são da app Windows. Gerar com Playwright nas 18 línguas (`/api/tutorial/recorte`) e trocar `rotas_ajuda`. |
| 4 | **Mais temas** | S cada | `docs/TEMAS.md` tem a receita. Ideias: Halloween, Verão/Praia, Jornal antigo, Terminal verde, Cartaz de circo. |
| 5 | **SEO por língua** | L | Um URL por língua (`/en/`, `/es/`…) com o texto traduzido no HTML e `hreflang`: hoje só o português se posiciona (`docs/SEO.md`). Antes disso: páginas de «como fazer» (rifas para a escola, a associação…). |
| 6 | **Instalar como app (PWA)** | S | O `manifest.webmanifest` e os ícones já existem; falta um *service worker* que guarde só a «casca» (a geração precisa sempre do servidor). |
| 7 | **Partilhar a configuração por link** | S | Os campos (de, até, modo…) no URL; nunca os ficheiros. |

## Qualidade e segurança

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 8 | **Auditoria de contraste dos temas** | M | Os 8 temas × claro/escuro foram vistos, não medidos. Correr axe/Lighthouse e acertar as cores (Arcade, Brutalista e Natal são os mais arriscados). |
| 9 | **Testes e2e com Playwright no CI** | M | O fluxo completo (template → pré-visualizar → gerar → descarregar) com as fixtures de `tests/fixtures/`. Hoje só se faz à mão. |
| 10 | **Confirmar o proxy e o anti-sono no Render** | XS | O painel (`/admin`) diz se os IPs reais chegam («Proxy e limite por IP») e se o serviço está a chamar-se («Anti-sono»); falta olhá-los com visitantes e 30 min sem visitas. Se der «problema», definir `FORWARDED_ALLOW_IPS=*`. |
| 11 | **Métricas que sobrevivem** | M | O disco do Render gratuito é efémero: disco persistente (pago) ou base externa para o histórico do painel (`docs/ADMIN.md`). |
| 12 | **Medir no Render a sério** | S | Os tempos e o `MAX_NUMEROS` (30 000) partiram de um contentor com 0,1 CPU assumido; repetir no Render e ajustar. |
| 13 | **Revisão nativa das traduções `web_*`** | S por língua | Foram escritas sem falante nativo (11 chaves). |

## Plataforma

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 15 | **Pré-visualização por PR** | M | Um deploy efémero por PR (Render *Preview Environments* ou imagem `pr-<n>`). |
| 16 | **Subir a app Windows para Python 3.15** | M | Hoje fica na 3.13 (Nuitka demora 10–20 min e o `--selftest` tem de dar igual). Decisão em aberto. |
| 17 | **Contas e pagamento** | L | O serviço será pago mais tarde. Desenhar antes os planos (limites por conta), a faturação e a proteção da privacidade dos ficheiros. |
| 18 | **Observabilidade** | S | Registo estruturado dos pedidos e um painel de erros/tempos, sem guardar conteúdo dos ficheiros. |
