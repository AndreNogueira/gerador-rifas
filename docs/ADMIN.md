# Painel de administração (`/admin`)

Um painel só para o dono do serviço, com **gráficos e explicações** do estado do servidor e da utilização. Está em `https://<o-teu-site>/admin`. Não tem ligação em nenhum menu e **não existe** enquanto não definires a palavra-passe.

## Ligar o painel (o que SÓ tu podes fazer)

1. Gera uma palavra-passe longa e aleatória (mínimo 12 caracteres; o servidor ignora as mais curtas):
   ```
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. No **Render** → o serviço `gerador-rifas` → **Environment** → *Add Environment Variable*: nome **`ADMIN_TOKEN`**, valor a palavra-passe. Guarda: o Render reinicia o serviço.
   - **Não é um *secret* do GitHub** e não vai para o repositório. É uma variável do próprio serviço. (O `render.yaml` só declara o nome, com `sync: false`; o valor nunca está nos ficheiros.)
3. Abre `/admin` e entra. Guarda a palavra-passe num gestor de palavras-passe: não há «recuperar»; para a trocar, muda a variável (isso fecha todas as sessões abertas).

Sem `ADMIN_TOKEN` (ou com menos de 12 caracteres) o painel e a sua API respondem **404**, como se não existissem.

## Como é protegido

- **Só entra quem sabe a palavra-passe.** Compara-se em tempo constante. **5 tentativas por minuto por IP** (40 no total, para travar quem tenta de muitos sítios) e uma espera extra a cada erro.
- **A palavra-passe nunca fica no browser.** Troca-se por um cookie assinado, **`HttpOnly`** (o JavaScript nem o lê), **`SameSite=Strict`**, só enviado para `/api/admin`, **`Secure`** em HTTPS, com validade de 8 horas. O cookie vale só enquanto o `ADMIN_TOKEN` for o mesmo.
- **Sem sessão, tudo é 404** (a API também), com `Cache-Control: no-store`; a página tem `noindex` e está fora do `sitemap.xml` e do `robots.txt`.
- Nada do painel vai para os motores de pesquisa, e o painel não aparece na documentação da API.

## O que o painel mostra

Tudo com uma explicação em linguagem simples ao lado («Como ler»).

| Secção | O que mostra |
|---|---|
| **Agora** | CPU, memória do servidor, do motor e total face ao limite (512 MB no Render gratuito), disco, sessões ativas, se há uma geração a correr, estado do motor e quantos reinícios teve |
| **Sistema ao longo do tempo** | gráficos de CPU, memória (com a linha do limite) e sessões ativas |
| **Pedidos à API** | pedidos e erros por intervalo, tempo de resposta (típico e dos mais lentos) e uma tabela por tipo de pedido |
| **Utilização** | sessões, pré-visualizações, gerações (ok, com erros, canceladas, falhadas), números e páginas gerados, duração das gerações, descargas, e distribuições por língua, tema, dispositivo, páginas vistas, erros devolvidos e motivos de falha |
| **Proxy e limite por IP** | verifica se os IPs reais dos visitantes chegam ao servidor (ver abaixo) |
| **Limites em vigor** | os valores que o servidor está a aplicar |

Os intervalos são a última hora, 6 horas, 24 horas, 7 dias e 30 dias. Os números de «Agora» atualizam de 10 em 10 segundos; os gráficos de 30 em 30.

## Privacidade: só agregados

**Nunca se guarda** um IP, um nome de ficheiro, o conteúdo de um ficheiro, o *User-Agent*, nem um texto de erro do utilizador. Cada evento leva só **códigos** (a língua, o tema, o tipo de dispositivo: computador, telemóvel ou robô, o estado) e **números** (quantos números se geraram, quanto tempo demorou). Para o teste do proxy, o IP vira um *hash* com sal aleatório (muda a cada arranque), só em memória e só da última hora. `tests/test_web_metricas.py` e `tests/test_web_admin.py` verificam que não há IPs no disco nem nomes de ficheiros nas respostas.

## Os dados são temporários no Render gratuito (decisão tua)

As métricas ficam num ficheiro SQLite (`metricas.sqlite3`, na pasta de armazenamento), com buffer em memória (gravado de 30 em 30 s) e retenção de 35 dias (sistema e pedidos) e 90 dias (eventos). **O disco do plano gratuito do Render é efémero**: perde-se quando o serviço adormece (15 min sem visitas) ou é atualizado. O painel avisa-o e diz «dados desde…».

Para teres histórico de verdade há três caminhos, por ordem de esforço:

1. **Disco persistente** do Render (plano pago): monta-o (p.ex. em `/data`) e define `RIFAS_METRICAS=/data/metricas.sqlite3`. O aviso de dados temporários desaparece sozinho.
2. **Base de dados externa** (Postgres ou libSQL, há planos gratuitos): é preciso trocar o armazenamento em `src/web/metricas.py` (todo o SQL está nesse ficheiro).
3. **Enviar para uma ferramenta de monitorização** (p.ex. Grafana Cloud): mais trabalho, mas dá-te alertas.

Para já escolhi não pagar nem depender de um serviço externo; diz-me se queres um destes.

## Verificar o proxy (o limite de pedidos por IP)

O servidor limita pedidos por IP. Atrás do Render, o IP real chega no cabeçalho `X-Forwarded-For`, mas o servidor só confia nele se o proxy estiver em `FORWARDED_ALLOW_IPS` (por omissão, as redes privadas `10.x`, `172.16.x`, `192.168.x`). Se não estiver, **todos os visitantes parecem o mesmo** e o limite passa a ser de todos: uma pessoa podia gastá-lo por todos.

A secção «Proxy e limite por IP» olha para a última hora e diz: **«ok»** (vários IPs, públicos), **«problema»** (quase todos os pedidos de 1 ou 2 endereços internos com `X-Forwarded-For`: define `FORWARDED_ALLOW_IPS=*` no serviço) ou **«sem proxy»** (desenvolvimento local). Precisa de uns 20 pedidos para concluir. **Isto fica por confirmar no Render real**: só se vê com visitantes a sério.

## Para quem mexe no código

- `src/web/metricas.py`: o registo (buffer, SQLite, histogramas, proxy); `src/web/sistema.py`: CPU/memória/disco (`psutil`, cgroup); `src/web/admin.py`: autenticação e API; o frontend em `Admin.tsx`, `graficos.tsx` (gráficos em SVG feitos à mão, sem biblioteca), `admin-api.ts` e `estilos/_admin.scss`.
- **Exceção às 18 línguas:** o painel está só em português (é do dono, não da interface pública).
- Um evento novo: `serv.metricas.evento(tipo, a, b, c, v1, v2, v3)` (só códigos e números!) e a consulta em `Metricas.resumo`; atualiza o teste de privacidade.
