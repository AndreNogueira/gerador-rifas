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
| `DONATIVO_URL` | ligação `https://…` (MB Way, PayPal, Ko-fi…): aparece o botão «Donativo». Outra coisa que não `https://` é ignorada. |
| `CONTACTO_EMAIL` | e-mail público: aparece a ligação «Contacto» e o endereço nas páginas Contacto, Termos e Privacidade. |
| `RESPONSAVEL` | nome de quem gere o serviço, nas páginas Termos e Privacidade. |

Os textos das páginas estão em `src/web/textos_legais.py`: são **provisórios** e têm de ser revistos por um advogado antes de o serviço cobrar (`docs/PLANO_PRODUTO.md` §5).
