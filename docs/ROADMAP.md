# Roteiro: incrementos para fazer em PRs pequenos

Cada linha é um PR (ou dois). **Tamanho:** XS = uma tarde, S = um dia, M = uns dias, L = semanas. Escolhe uma, abre uma issue com o [modelo](../.github/ISSUE_TEMPLATE/funcionalidade.yml) e segue o [fluxo](../CONTRIBUTING.md). Está ordenado por valor a dividir pelo esforço, não por obrigação.

## Para o utilizador

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 1 | **Lembrar o ficheiro dos algarismos** entre sessões | S | A app Windows lembra-o; aqui a sessão perde-o. Guardar no browser (IndexedDB) e reenviar ao servidor ao retomar. Nada fica no servidor. |
| 2 | **Capturas do tutorial da web** | M | As atuais são da app Windows. Gerar com Playwright nas 18 línguas (`/api/tutorial/recorte`) e trocar `rotas_ajuda`. |
| 3 | **Instalar como app (PWA)** | S | O `manifest.webmanifest` e os ícones já existem; falta um *service worker* que guarde só a «casca» (a geração precisa sempre do servidor). |
| 4 | **Partilhar a configuração por link** | S | Os campos (de, até, modo…) no URL; nunca os ficheiros. |

## Qualidade e segurança

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 5 | **Testes e2e com Playwright no CI** | M | O fluxo completo (template → pré-visualizar → gerar → descarregar) com as fixtures de `tests/fixtures/`. Hoje só se faz à mão. |
| 6 | **Rever o limite por IP atrás do Render** | S | Confirmar nos logs que o IP real chega (`FORWARDED_ALLOW_IPS`); senão o limite fica global. |
| 7 | **Medir no Render a sério** | S | Os tempos e o `MAX_NUMEROS` (30 000) partiram de um contentor com 0,1 CPU assumido; repetir no Render e ajustar. |
| 8 | **Revisão nativa das traduções `web_*`** | S por língua | Foram escritas sem falante nativo (11 chaves). |
| 9 | **Remover `python-multipart`** | XS | Já não é usada (uploads em corpo cru). |

## Plataforma

| # | Incremento | Tam. | Notas |
|---|---|---|---|
| 10 | **Pré-visualização por PR** | M | Um deploy efémero por PR (Render *Preview Environments* ou imagem `pr-<n>`). |
| 11 | **Subir a app Windows para Python 3.15** | M | Hoje fica na 3.13 (Nuitka demora 10–20 min e o `--selftest` tem de dar igual). Decisão em aberto. |
| 12 | **Contas e pagamento** | L | O serviço será pago mais tarde. Desenhar antes os planos (limites por conta), a faturação e a proteção da privacidade dos ficheiros. |
| 13 | **Observabilidade** | S | Registo estruturado dos pedidos e um painel de erros/tempos, sem guardar conteúdo dos ficheiros. |
