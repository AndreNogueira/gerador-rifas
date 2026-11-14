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

### Um segundo acesso, só de leitura: `CLAUDE_TOKEN`

Para um assistente (o Claude) poder **ver** o painel sem partilhar a palavra-passe do dono e sem poder mudar nada:

1. Gera outra palavra-passe (mínimo **24** caracteres, **diferente** do `ADMIN_TOKEN`; se for igual, ou curta, fica desligada): `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
2. No Render → **Environment**: **`CLAUDE_TOKEN`** = essa palavra-passe (como o `ADMIN_TOKEN`: variável do serviço, nunca no repositório). O Render reinicia o serviço.
3. Quem a tem pode: **entrar** em `/admin` com ela (o painel mostra «Só de leitura»), ou, sem cookie, pôr `Authorization: Bearer <CLAUDE_TOKEN>` num pedido **GET** (`/api/admin/estado`, `/dados`, `/erros`, `/chaves`, `/seo`).
4. Não pode: criar ou revogar chaves da API, nem editar ou repor textos de SEO (responde **403**); nem usar o `ADMIN_TOKEN` como *bearer* (o do dono só entra por cookie). As credenciais certas por cabeçalho não gastam tentativas; **10 erradas por minuto e por IP** travam o acesso por cabeçalho até passar o minuto.
5. Com só o `CLAUDE_TOKEN` (sem `ADMIN_TOKEN`) o painel existe **só em leitura**. Mudar qualquer um dos dois tokens fecha todas as sessões abertas. O painel regista só o código `entrou_leitura` (nunca o token).

## Como é protegido

- **Só entra quem sabe a palavra-passe.** Compara-se em tempo constante. **5 tentativas por minuto por IP** (40 no total, para travar quem tenta de muitos sítios) e uma espera extra a cada erro.
- **A palavra-passe nunca fica no browser.** Troca-se por um cookie assinado, **`HttpOnly`** (o JavaScript nem o lê), **`SameSite=Strict`**, só enviado para `/api/admin`, **`Secure`** em HTTPS, com validade de 8 horas. O cookie vale só enquanto o `ADMIN_TOKEN` for o mesmo.
- **Sem sessão, tudo é 404** (a API também), com `Cache-Control: no-store`; a página tem `noindex` e está fora do `sitemap.xml` e do `robots.txt`.
- Nada do painel vai para os motores de pesquisa, e o painel não aparece na documentação da API.

## O que o painel mostra

Tudo com uma explicação em linguagem simples ao lado («Como ler»).

| Secção | O que mostra |
|---|---|
| **Agora** | CPU, o **anti-sono** (ver `docs/ONLINE.md`), memória do servidor, do motor e total face ao limite (512 MB no Render gratuito), disco, sessões ativas, se há uma geração a correr, estado do motor e quantos reinícios teve |
| **Sistema ao longo do tempo** | gráficos de CPU, memória (com a linha do limite) e sessões ativas |
| **Pedidos à API** | pedidos e erros por intervalo, tempo de resposta (típico e dos mais lentos) e uma tabela por tipo de pedido |
| **Erros** | o livro de erros: o que falhou desde o último arranque, por tipo, rota, classe da exceção e sítio no código, com contagem; ver `docs/OBSERVABILIDADE.md` |
| **Utilização** | sessões, pré-visualizações, gerações (ok, com erros, canceladas, falhadas), números e páginas gerados, duração das gerações, descargas, e distribuições por língua, tema, dispositivo, páginas vistas, erros devolvidos e motivos de falha |
| **Ecrãs e dispositivos** | tipo de ecrã (telemóvel, tablet, computador Full HD/QHD/4K/ultra-wide), tamanhos de ecrã mais comuns (p.ex. `393×852 @3x`), família ou modelo do aparelho, largura da janela e se há toque |
| **Proxy e limite por IP** | verifica se os IPs reais dos visitantes chegam ao servidor (ver abaixo) |
| **Limites em vigor** | os valores que o servidor está a aplicar |

Os intervalos são a última hora, 6 horas, 24 horas, 7 dias e 30 dias. Os números de «Agora» atualizam de 10 em 10 segundos; os gráficos de 30 em 30.

## Privacidade: só agregados

**Nunca se guarda** um IP, um nome de ficheiro, o conteúdo de um ficheiro, o *User-Agent*, nem um texto de erro do utilizador. Cada evento leva só **códigos** (a língua, o tema, o tipo de dispositivo: computador, telemóvel ou robô, o estado; e o **tamanho do ecrã e da janela**, a família do aparelho e, nos Chrome de Android que o dizem, o **modelo** do telemóvel, só em agregado) e **números** (quantos números se geraram, quanto tempo demorou). Para o teste do proxy, o IP vira um *hash* com sal aleatório (muda a cada arranque), só em memória e só da última hora. `tests/test_web_metricas.py` e `tests/test_web_admin.py` verificam que não há IPs no disco nem nomes de ficheiros nas respostas.

## Onde ficam as métricas: SQLite (temporário) ou Postgres (persistente)

**Sem `DATABASE_URL`** (o que acontece por omissão) as métricas ficam num ficheiro SQLite (`metricas.sqlite3`, na pasta de armazenamento), com buffer em memória (gravado de 30 em 30 s). **O disco do plano gratuito do Render é efémero**: perde-se quando o serviço adormece (15 min sem visitas) ou é atualizado. O painel avisa-o e diz «dados desde…».

**Com `DATABASE_URL`** (desde o M9) as métricas vão para uma base **Postgres** externa e sobrevivem a reinícios e *deploys*. Retenção: 35 dias (sistema e pedidos) e 90 dias (eventos). O aviso de «dados temporários» desaparece sozinho. O que se guarda é o mesmo de sempre (só agregados, ver a secção da privacidade).

1. Cria o projeto na Neon (região da UE, p.ex. Frankfurt) e copia o endereço de ligação (`postgresql://…`). **É uma palavra-passe**: nunca vai para o Git, para o chat nem para ficheiros.
2. No Render → o serviço → **Environment**: `DATABASE_URL` = esse endereço. Guarda (o Render reinicia o serviço).
3. Em poucos minutos o painel deixa de mostrar o aviso. Para ver se está a gravar: no painel, «Base de dados» diz `postgres` e, passada a primeira gravação, «dados desde…» deixa de mudar quando o serviço reinicia.

Duas coisas a saber:
- **Grava de hora a hora** (`METRICAS_BD_MIN`, 1 a 720, por omissão 60) e sempre quando o serviço termina, porque a computação gratuita da Neon só suspende ao fim de 5 minutos sem pedidos e o plano tem horas limitadas. Se o serviço for morto sem aviso (falta de memória), perdem-se até 60 minutos de métricas. O painel mostra sempre o que já aconteceu, incluindo o que ainda está no buffer.
- **Se a base estiver em baixo ou o endereço estiver errado**, o gerador funciona na mesma: as métricas ficam em memória (até 50 000 registos), o painel mostra os gráficos vazios e tenta outra vez passados 30 s. Nada disto aparece nos logs com o endereço nem a palavra-passe.

Outras opções, por ordem de esforço: **disco persistente** do Render (plano pago; `RIFAS_METRICAS=/data/metricas.sqlite3`) ou **enviar para uma ferramenta de monitorização** (p.ex. Grafana Cloud).

## Verificar o proxy (o limite de pedidos por IP)

O servidor limita pedidos por IP. Atrás do Render, o IP real chega no cabeçalho `X-Forwarded-For`, mas o servidor só confia nele se o proxy estiver em `FORWARDED_ALLOW_IPS` (por omissão, as redes privadas `10.x`, `172.16.x`, `192.168.x`). Se não estiver, **todos os visitantes parecem o mesmo** e o limite passa a ser de todos: uma pessoa podia gastá-lo por todos.

A secção «Proxy e limite por IP» olha para a última hora e diz: **«ok»** (vários IPs, públicos), **«problema»** (quase todos os pedidos de 1 ou 2 endereços internos com `X-Forwarded-For`: define `FORWARDED_ALLOW_IPS=*` no serviço) ou **«sem proxy»** (desenvolvimento local). Precisa de uns 20 pedidos para concluir. **Isto fica por confirmar no Render real**: só se vê com visitantes a sério.

## Para quem mexe no código

- O SQL de `metricas.py` tem de servir **ao SQLite e ao Postgres** (`?` vira `%s`, upsert com `ON CONFLICT`, `BIGINT`/`DOUBLE PRECISION`). `tests/test_web_metricas.py` corre as mesmas consultas nos dois; para o Postgres precisa de `TEST_DATABASE_URL` (o CI tem o trabalho «metricas em Postgres 17»; localmente qualquer Postgres descartável: **os testes apagam as tabelas `sistema`, `pedidos` e `eventos`**, nunca apontes para a base real).

- `src/web/metricas.py`: o registo (buffer, SQLite, histogramas, proxy); `src/web/sistema.py`: CPU/memória/disco (`psutil`, cgroup); `src/web/admin.py`: autenticação e API; o frontend em `Admin.tsx`, `graficos.tsx` (gráficos em SVG feitos à mão, sem biblioteca), `admin-api.ts` e `estilos/_admin.scss`.
- **Exceção às 18 línguas:** o painel está só em português (é do dono, não da interface pública).
- Um evento novo: `serv.metricas.evento(tipo, a, b, c, v1, v2, v3)` (só códigos e números!) e a consulta em `Metricas.resumo`; atualiza o teste de privacidade.

## API pública (Swagger UI)

O painel tem uma secção **«API pública (Swagger UI)»** com ligações para `/api/v1/docs` (a documentação interativa da API pública em lote: pedidos, campos, respostas, e permite experimentá-los com uma chave `X-API-Key`) e para `/api/v1/openapi.json` (a descrição OpenAPI). Abrem noutro separador e estão acessíveis a quem tiver o endereço; as chaves criam-se e revogam-se aqui, no painel (`docs/API.md`).
