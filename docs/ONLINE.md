# Manter o serviço no ar e acordado (Render)

## O problema

Segundo a [documentação do Render](https://render.com/docs/free) (consultada em 2026-11-07), um serviço web **gratuito**:

- **adormece** quando passa **15 minutos sem receber tráfego de entrada** (pedidos HTTP ou mensagens WebSocket); o primeiro pedido seguinte espera cerca de **1 minuto** (o Render mostra uma página de «a carregar»);
- gasta **750 horas gratuitas por mês, por conta (*workspace*)** enquanto está a correr (os serviços adormecidos não gastam); passadas as 750 horas, o Render **suspende** os serviços gratuitos até ao mês seguinte;
- perde o disco (sistema de ficheiros efémero) quando reinicia, é atualizado ou adormece, e **o Render pode reiniciar um serviço gratuito a qualquer momento**;
- enquanto está adormecido, **`/robots.txt` responde «Disallow: /»** sem chegar ao serviço: um motor de pesquisa que passe nessa altura vê o site fechado;
- «não se deve usar para aplicações em produção» (palavras do próprio Render).

## O que está feito: o serviço chama-se a si próprio

`src/web/manter_acordado.py`: de **10 em 10 minutos** o serviço faz um `GET <URL público>/health`. Esse pedido atravessa o proxy do Render, por isso conta como tráfego de entrada e o contador dos 15 minutos volta a zero. O `/health` não conta nas métricas nem como visita.

- **Liga-se sozinho no Render** (usa o `RENDER_EXTERNAL_URL` que o Render define); fora do Render não faz nada.
- Variáveis (todas opcionais): `KEEPALIVE=0` desliga; `KEEPALIVE_URL` escolhe outro URL (p.ex. o domínio próprio); `KEEPALIVE_MIN` muda o intervalo (1 a 14 minutos, nunca ≥ 15).
- O painel `/admin` mostra o cartão **Anti-sono** (se está ativo e quando foi o último pedido, e se falhou).
- É tráfego minúsculo (144 pedidos por dia) e quase só de saída para o próprio Render: nada que se aproxime do «limiar de tráfego iniciado pelo serviço».

### O que NÃO resolve (honestidade)

1. **Não acorda um serviço que já adormeceu**: só um pedido de fora o faz. Depois de cada *deploy* o serviço arranca acordado e o ciclo toma conta; se o Render o reiniciar, volta a arrancar acordado. Mas se por qualquer razão adormecer, fica a dormir até alguém (ou um monitor externo) o acordar. Por isso há a camada 2.
2. **Consome horas gratuitas**: acordado sempre = 24 h × 31 dias = **744 horas**, de um total de **750** por conta. Chega para **um único** serviço gratuito sempre ligado; **se houver outro serviço gratuito na mesma conta, as horas acabam antes do fim do mês e o Render suspende-os todos.** Confirma na página de *Billing* do Render, em «Monthly Included Usage».
3. **Não dá disco persistente**: continua a perder os ficheiros e as métricas em cada *deploy* ou reinício (ver `docs/ADMIN.md`).
4. **Isto só se confirma em produção**, depois de o serviço correr mais de 20 minutos sem visitas: ainda não foi visto no Render a sério.
5. É uma prática comum, mas **vai contra o espírito** do plano gratuito («não usar em produção»). Para um serviço que vai cobrar dinheiro, a solução certa é a camada 3.

## Camadas, por esta ordem

| # | Camada | Custo | Quem a faz | Notas |
|---|---|---|---|---|
| 1 | **O serviço chama-se a si** (já feito) | 0 | já está | Cobre o caso normal; gasta 744 das 750 horas |
| 2 | **Monitor externo** a chamar `https://<site>/health` de 5 em 5 min | 0 | **tu** | É a rede de segurança: acorda o serviço se adormecer e avisa-te por e-mail se cair. Ferramentas com plano gratuito: UptimeRobot, Better Stack, cron-job.org (**confirma os termos de cada uma**: algumas limitam o gratuito a uso não comercial) |
| 3 | **Plano pago do Render** (*Starter*, sem adormecer) | pago por mês (ver o preço em render.com/pricing) | **tu**, no painel | A solução a sério: nunca adormece, sem o limite das 750 horas, e permite **disco persistente** (que resolve também as métricas). Não se mexe no código |
| ✗ | GitHub Actions agendado | — | — | **Não recomendado**: os agendamentos atrasam-se muito (10–20 min), e a cada 10 min gastariam as ~2000 min/mês do plano gratuito num repositório privado |

**Configurar o UptimeRobot:** *Add New Monitor* → tipo **HTTP(s)**, URL `https://gerador-rifas.onrender.com/health`, intervalo **5 minutos** (o mínimo do plano gratuito, abaixo dos 15 do Render), contacto de alerta = o teu e-mail. O `/health` aceita `GET` e `HEAD` (o método por omissão do UptimeRobot). Para também detetar um site "vivo mas avariado", usa um monitor de palavra-chave com `"estado":"ok"`.

**Recomendação:** deixar a camada 1 e juntar já a 2 (cinco minutos no UptimeRobot). Quando o serviço começar a **cobrar**, passar à 3 no mesmo dia: um serviço pago não pode adormecer nem perder os ficheiros dos clientes (ver `docs/PLANO_PRODUTO.md`).

## Como confirmar que funciona

1. Faz *deploy* e deixa o serviço **sem visitas durante 30 minutos**.
2. Abre `https://<site>/admin` → cartão **Anti-sono**: deve dizer «ativo (10 min)» e «último pedido ok há N min» com N < 10.
3. Abre o site: deve responder logo (sem a página de «a carregar» de ~1 minuto).
4. Se o cartão disser «FALHOU», o `RENDER_EXTERNAL_URL` pode não ser o público: define `KEEPALIVE_URL` com o endereço certo.

## Rodapé: donativo, contacto e responsável

O rodapé tem sempre Changelog, Termos e Privacidade. Três variáveis do **Render** (Environment; nada disto vai para o repositório) completam-no:

| Variável | Efeito |
|---|---|
| `DONATIVO_URL` | ligação `https://…` (MB Way, PayPal, Ko-fi…): aparece o botão «Donativo» (no cabeçalho, no fim da geração e no rodapé). Outra coisa que não `https://` é ignorada. |
| `RESEND_API_KEY`, `RELATORIO_EMAIL_PARA`, `RELATORIO_EMAIL_DE`, `RELATORIO_FUSO` | o relatório diário das métricas por e-mail à meia-noite (`relatorio.py`, `docs/ADMIN.md`): chave do Resend (palavra-passe, só no Render), o teu e-mail, o remetente (por omissão `onboarding@resend.dev`, que só entrega ao e-mail da conta do Resend) e o fuso dos «dias» (`Europe/Lisbon`). O Render gratuito bloqueia o SMTP: por isso é uma API HTTPS. Sem eles não se envia nada. |
| `GITHUB_ISSUES_TOKEN`, `GITHUB_REPO` | liga «Reportar problema» ao GitHub: token fine-grained só com «Issues: read and write» e `dono/nome` do repositório (`docs/OPINIAO.md`). Sem eles a página avisa que não está ativa. |
| `CONTACTO_EMAIL` | e-mail público: aparece a ligação «Contacto» e o endereço nas páginas Contacto, Termos e Privacidade. |
| `RESPONSAVEL` | nome de quem gere o serviço, nas páginas Termos e Privacidade. |
| `LOG_PEDIDOS` | `0` desliga o registo estruturado (uma linha JSON por pedido da API e por evento, nos logs do Render; ver `docs/OBSERVABILIDADE.md`). Ligado por omissão. |

Os textos das páginas estão em `src/web/textos_legais.py`: são **provisórios** e têm de ser revistos por um advogado antes de o serviço cobrar (`docs/PLANO_PRODUTO.md` §5).

## QR de verificação nos bilhetes

Com a variável `VERIFICACAO_CHAVE` no **Render** (Environment; pelo menos 16 caracteres, **nunca** no repositório) o gerador oferece um QR em cada bilhete dos templates de uma só rifa. Ler o QR abre `<site>/V/<código>`, uma página que confirma que o código foi emitido por este serviço para aquele bilhete (assinatura HMAC; não há base de dados). **Não prova que o bilhete foi pago nem que ganhou.** `PUBLIC_URL` tem de ser o endereço real do site (o QR leva-o). Se se trocar a chave, os QR já impressos deixam de validar: não a mudes depois de imprimir. `MAX_NUMEROS_QR` (10 000 por omissão) é o teto de números de um pedido com QR.

## Monitores do UptimeRobot (conta gratuita: 50 monitores, verificação de 5 em 5 minutos)

Criados em 2026-11-12, com o aviso por e-mail para o dono:

| Monitor | O que verifica |
|---|---|
| Gerador Rifas | `/health` (o original; também ajuda a manter o Render acordado) |
| página inicial (texto) | a página `/` tem a frase «Gerador de Rifas» (apanha uma página em branco ou um erro do frontend) |
| sitemap.xml | `/sitemap.xml` tem `sitemaps.org` (o SEO depende dele) |
| vídeos do tutorial | `HEAD /videos/tutorial_pt.mp4` (confirma que os vídeos foram descarregados do armazenamento, ver `docs/ASSETS.md`) |
| Armazenamento de ficheiros | `HEAD` do `.zip` no bucket do Neon (se falhar, o site arranca sem vídeos) |
| ads.txt | `/ads.txt` tem `f08c47fec0942fa0`; **em pausa** até a AdSense estar ligada (sem `ADSENSE_CLIENTE` o `/ads.txt` dá 404): retomar nessa altura |

Página de estado pública (sem texto de SEO: o `noIndex` e os avisos de SSL e de domínio são do plano pago): <https://stats.uptimerobot.com/U1cH2J3Enj>. Quando se publica um `.zip` novo dos assets, trocar o URL do monitor «Armazenamento de ficheiros».
