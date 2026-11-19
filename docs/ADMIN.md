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
3. Quem a tem pode: **entrar** em `/admin` com ela (o painel mostra «Só de leitura»), ou, sem cookie, pôr `Authorization: Bearer <CLAUDE_TOKEN>` num pedido **GET** (`/api/admin/estado`, `/dados`, `/erros`, `/chaves`, `/seo`, `/comentarios`).
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
| **Utilização** | sessões, pré-visualizações, gerações (ok, com erros, canceladas, falhadas), números e páginas gerados, duração das gerações, descargas, e distribuições por língua, **país**, tema, dispositivo, páginas vistas, erros devolvidos e motivos de falha |
| **Ecrãs e dispositivos** | tipo de ecrã (telemóvel, tablet, computador Full HD/QHD/4K/ultra-wide), tamanhos de ecrã mais comuns (p.ex. `393×852 @3x`), família ou modelo do aparelho, largura da janela e se há toque |
| **Proxy e limite por IP** | verifica se os IPs reais dos visitantes chegam ao servidor (ver abaixo) |
| **Limites em vigor** | os valores que o servidor está a aplicar |

### Evolução diária (`/admin` → «Evolução diária»)

Uma segunda vista, ao lado da «Visão geral», com **tudo o que está na base dia a dia** (7, 14, 30, 60 ou 90 dias; `GET /api/admin/evolucao?dias=&fuso=`, também de leitura para o `CLAUDE_TOKEN`). Os dias são os do fuso do browser (`fuso` = minutos local − UTC) e o último, hoje, está incompleto. Cada painel traz o total (ou a média/o pico), a **tendência** (2.ª metade do período face à 1.ª) e um gráfico de barras empilhadas ou de linhas com balão por dia. «Descarregar CSV» exporta todas as séries (`;`, vírgula decimal, BOM: abre direto no Excel em português).

| Grupo | Painéis (de onde vêm) |
|---|---|
| **Utilização** | sessões, páginas vistas (pessoas e robôs), pré-visualizações, templates e algarismos (certos/recusados), gerações por estado, números e páginas gerados, descargas, duração das gerações (mediana e 95 %), funil sessão → geração → descarga (tabela `eventos`) |
| **Funcionalidades** | galeria por desenho, editor, logótipo, verificação de QR, API pública, limites atingidos (`eventos`) |
| **Público** | línguas, visuais, dispositivos, países, tipos de ecrã, largura da janela, páginas mais vistas (`eventos`) |
| **Saúde** | pedidos certos/4xx/5xx e tempo de resposta (tabela `pedidos`), erros por código, falhas por motivo, arranques e reinícios do motor, acessos ao painel (`eventos`) |
| **Sistema** | CPU (média e pico), memória (servidor, motor, contentor), disco, sessões e gerações em simultâneo (tabela `sistema`) |
| **API e partilhas** | números e lotes gastos pela API pública (`api_uso`, dias UTC) e desenhos do editor partilhados (`partilhas`, só com Postgres) |

Os limites são os da retenção (eventos 90 dias, pedidos e sistema 35): os dias mais antigos aparecem vazios. As categorias mostram as 8 mais usadas e juntam o resto em «Outros». Um evento novo aparece aqui acrescentando-o a `Metricas.evolucao` (e ao teste `test_a_evolucao_cobre_todos_os_tipos_de_evento_que_se_gravam`).

**Marcas de versão:** cada gráfico diário leva uma linha tracejada e um triângulo ▲ no dia em que chegou uma versão nova da app (o evento `arranque` guarda a `VERSAO`; conta a primeira vez que cada versão arrancou, não os reinícios; `Metricas.evolucao` devolve `versoes: [{dia, versao}]`). Passando o rato vê-se qual. Na vista de mais de 90 dias vêm do histórico (`_versoes` na linha do dia). O relatório diário diz «Chegou a versão X neste dia». As versões que arrancaram antes da retenção dos eventos (90 dias) não aparecem.

A aba **Comentários** mostra os comentários dos visitantes só com o **país** (de onde vieram; nunca o IP, que não se guarda), o **texto** e o **estado** que o dono lhe dá: *novo* (até o marcar), *lido*, *favorito* ou *escondido* (deixa de aparecer na página pública, mas não se perde; o dono continua a vê-lo). Há filtros por estado, a contagem de «por ler», «Marcar todos como lidos» e apagar (só o dono: `PATCH /api/admin/comentarios/{id}`, `POST /api/admin/comentarios/lidos`; a leitura vê mas recebe 403). Ver `docs/OPINIAO.md`.

A aba **Relatório diário** mostra o estado do e-mail diário (ligado ou não, para onde vai, último dia enviado, último erro), **pré-visualiza** o relatório de qualquer dia e manda **um e-mail de teste** (só o dono; assunto «[Teste]», não conta como o envio do dia).

## Histórico permanente (`/admin` → «Evolução diária» → 180 dias, 1 ano, 2 anos)

Os eventos brutos apagam-se aos 90 dias e os pedidos/sistema aos 35. Por isso, depois das 00:05 (`RELATORIO_FUSO`) o servidor grava **uma linha-resumo por dia** na tabela `historico_diario` (o que a «Evolução diária» mostra desse dia, só o que não é zero; ≈ 3 KB por dia, ≈ 1 MB por ano) e, na primeira vez, também os dias que ainda estão na base (até 90). A vista com mais de 90 dias (`GET /api/admin/evolucao?dias=365`, até 730) lê daí (`historico.py`): os dias são os do fuso do relatório (não os do browser), o dia em curso não aparece e os dias anteriores ao histórico aparecem vazios («sem dados», não zero). Funciona sem o e-mail. Sem `DATABASE_URL` vive no disco efémero (perde-se ao reiniciar).

## Origem das visitas e campanhas

O browser diz, uma vez por separador e junto com o tipo de ecrã (`ecra.ts` → `POST /api/ecra`), **só o nome do servidor** de onde veio (`document.referrer`, nunca o caminho nem os parâmetros) e o `utm_source` do endereço, se tiver. O servidor reduz isso a uma **categoria** (`metricas.categoria_de_origem`): *direta* (sem origem, ou o próprio site), *pesquisa* (Google, Bing, DuckDuckGo…), *redes sociais* (Facebook, Instagram, X, LinkedIn, WhatsApp, YouTube…), *e-mail* ou *outros sites*, e guarda o evento `origem` com a categoria e o nome da campanha (só letras minúsculas, algarismos, `_` e `-`, até 30). **O nome do servidor de origem nunca se guarda**, nem o endereço completo, nem o IP; os robôs não contam. Na «Evolução diária», grupo «Público», há os painéis «Origem das visitas» e «Campanhas (utm_source)». Para medir uma divulgação, partilhe o site com `?utm_source=nome-da-campanha` (por exemplo `https://…/?utm_source=cartaz-escola`). A Política de privacidade (22 línguas) tem a secção «Origem das visitas» (`legal_medicoes.py`; mudar o que se guarda obriga a mudar esse texto).

## Registo de ações (`/admin` → «Registo de ações»)

Guarda **quem fez o quê e quando** no painel durante 400 dias (`auditoria.py`, tabela `auditoria`, `GET /api/admin/auditoria`, também de leitura): entradas (do dono e da leitura), comentários apagados, escondidos ou marcados, chaves da API criadas e revogadas, textos de SEO editados ou repostos, objetivos e e-mails de teste. Cada linha: hora, papel (dono ou só leitura), a ação em português e um detalhe curto (o id aleatório do comentário, o nome e id da chave, a chave do texto de SEO e a língua…). **Nunca** leva o texto dos visitantes, a palavra-passe, a chave da API em claro nem IPs. As **palavras-passe erradas e os bloqueios não se guardam aqui** (um ataque encheria a tabela): contam-se nas métricas, em «Acessos ao painel». Uma base em baixo nunca impede a ação em si. Sem `DATABASE_URL` o registo vive no disco temporário. Ação nova no painel = `_registar(serv, "codigo", detalhe=…)` em `admin.py` e o texto em `auditoria.ACOES` (um teste verifica-o).

## Objetivos diários (`/admin` → «Evolução diária»)

O cartão «Objetivos diários» (`objetivos.py`, `GET`/`PUT /api/admin/objetivos`) deixa o dono pôr uma **meta por dia** (pelo menos) em sessões, gerações pedidas, números gerados, descargas, páginas vistas por pessoas e comentários (só contagens; não há metas para erros). Mostra, do **último dia completo**, se a meta foi atingida e a percentagem, a média dos últimos 7 dias e em quantos desses dias foi cumprida. Campo vazio = sem meta. As metas guardam-se na tabela `objetivos` (Neon; SQLite local sem `DATABASE_URL`); só o dono as muda (a leitura vê). O **relatório diário por e-mail** leva a secção «Objetivos do dia» (✔/✘) e uma linha «Abaixo do objetivo…» nos avisos; se a base das metas estiver em baixo o relatório sai na mesma, sem essa secção.

## Quotas do alojamento gratuito (`/admin` → «Visão geral»)

O cartão «Quotas do alojamento» (`quotas.py`, `GET /api/admin/quotas`, também de leitura) mostra:
- **Horas do Render no mês (750 por conta, mês civil UTC):** conta as horas distintas do mês com pelo menos uma amostra do sistema (de 30 em 30 s, só com o serviço acordado), com a **projeção** ao ritmo atual e um aviso a 90 % (`RENDER_HORAS_LIMITE` muda os 750). É uma estimativa **deste** serviço: o limite é da conta, outros serviços também gastam. Sem `DATABASE_URL` só conta desde o último reinício; se a base só existe desde meio do mês, o cartão diz desde quando. Um serviço sempre acordado (anti-sono ligado) gasta ≈ 744 h por mês.
- **Espaço do Neon (0,5 GB no plano grátis):** `pg_database_size` e as 8 tabelas maiores, com aviso a 80 % (`NEON_LIMITE_MB` muda os 512). Só com `DATABASE_URL`. As horas de computação do Neon (191,9 h/mês) só se veem no painel do Neon.
Os avisos (90 % das horas, 80 % do espaço) vão também no **relatório diário**; a «Evolução diária» tem o painel «Horas acordado (estimativa)» por dia (e fica no histórico).

## Os ciclos e o Neon gratuito

O Neon adormece a base ao fim de uns 5 minutos sem consultas (é assim que poupa as horas de computação do plano grátis). Por isso os ciclos do histórico, do relatório diário, dos resumos e dos alertas **lembram-se em memória do que já trataram** (`HistoricoDiario.feito_ate`, `EstadoRelatorio.dia_tratado`/`periodicos_tratados`, `EstadoAlertas.avisados`): depois de tratado o dia, só voltam a consultar a base depois da meia-noite seguinte (e um alerta que continua mau só pergunta uma vez por espera de 6 horas). Um arranque novo pergunta uma vez e lembra-se. `tests/test_web_sem_consultas.py` conta as consultas.

## Resumo semanal e mensal por e-mail

O mesmo e-mail, somado por **semana** (segunda a domingo; chega à segunda-feira) e por **mês** (chega no dia 1), depois das 00:05 e com o **período anterior** ao lado (`relatorio_periodo.py`). Lêem do **histórico permanente** (`historico.py`), por isso precisam de o último dia do período já estar gravado e de pelo menos metade dos dias (o histórico só existe desde que foi ligado; se faltarem dias o e-mail avisa). As contagens somam-se; as séries de média ou pico (CPU, memória, tempos) mostram a média ou o pico dos dias. Se o serviço dormia, a semana ainda sai até à segunda seguinte e o mês nos primeiros 7 dias. A reserva usa a mesma tabela `relatorios` (chaves `semana:…`, `mes:…`): nunca duplicam. `RELATORIOS_PERIODICOS=0` desliga-os. Na aba «Relatório diário» escolhes **Diário / Resumo semanal / Resumo mensal** para pré-visualizar ou enviar um teste de qualquer período dos últimos 2 anos.

## Alertas imediatos por e-mail

Sem esperar pela meia-noite, o servidor avisa por e-mail (o mesmo Resend e o mesmo destino do relatório; `alertas.py`) quando, nos **últimos 15 minutos**, se verifica: **5 ou mais erros 5xx**; **2 ou mais reinícios do motor**; a **memória do contentor acima de 460 MB** (o Render gratuito tem 512); ou a **base de dados sem resposta** em 2 verificações seguidas. As verificações são de minuto a minuto, sobre o que o servidor viu desde o arranque (em memória: não dependem da base). Cada condição só volta a avisar passadas **6 horas** (a reserva está na tabela `alertas`: um arranque novo não repete) e as que aparecem juntas vão num só e-mail. Se o envio falha, desfaz-se a reserva e tenta-se passados 15 minutos. `ALERTAS_EMAIL=0` desliga-os. Na aba «Relatório diário» vêm as regras, o último aviso de cada uma e o botão «Enviar um alerta de teste». Só contagens e a hora, nunca IPs nem textos de erro.

## Relatório diário por e-mail

Todos os dias, um pouco depois da meia-noite (`RELATORIO_FUSO`, por omissão `Europe/Lisbon`), o servidor envia um e-mail HTML com **tudo o que se gravou no dia que acabou**: os números grandes (sessões, gerações, números gerados, descargas, páginas vistas, comentários, problemas, erros 5xx), **avisos** (erros 5xx, gerações falhadas, reinícios do motor, memória perto de 512 MB, resposta lenta, dados incompletos) e, por grupo, cada série com o **dia, a média dos 7 dias anteriores, a variação e uma miniatura dos 8 dias** (`relatorio.py`, a mesma base da «Evolução diária»). Só contagens e códigos de país: nunca IPs, nomes, ficheiros nem o texto dos comentários.

**Ligar (o que SÓ tu podes fazer):**
1. Em [resend.com](https://resend.com) cria uma conta gratuita (100 e-mails/dia: sobra) e, em **API Keys**, uma chave só com «Sending access».
2. No Render → o serviço → **Environment**: `RESEND_API_KEY` = a chave (**é uma palavra-passe**: nunca no repositório nem no chat) e `RELATORIO_EMAIL_PARA` = o teu e-mail (até 3 separados por vírgula). Sem domínio próprio o remetente é `onboarding@resend.dev`, que **só entrega ao e-mail da conta do Resend**: usa esse e-mail. Para outro destinatário, verifica um domínio no Resend e define `RELATORIO_EMAIL_DE` (`Nome <endereco@o-teu-dominio>`).
3. Na aba **Relatório diário** do painel carrega em «Enviar um teste agora».

**Porque HTTPS e não SMTP:** o Render gratuito bloqueia as portas de saída do SMTP, por isso o envio usa a API do Resend (`email_envio.py`, só `urllib`).

**Garantias:** o envio do dia é **reservado na base** (tabela `relatorios`, no Neon com `DATABASE_URL`) antes de se mandar: dois arranques sobrepostos ou uma atualização a meio da noite não o duplicam; se o serviço estava a dormir à meia-noite o e-mail sai quando acordar (de 5 em 5 minutos, depois das 00:05); se o envio falha a reserva desfaz-se e tenta-se outra vez de hora a hora (o painel mostra o erro, só a classe e o código HTTP, nunca a chave nem os endereços). Sem `DATABASE_URL` a reserva vive no disco efémero e uma atualização a meio da manhã pode repetir o relatório. Nos dois dias de mudança de hora a janela fica uma hora desfasada. Se a base de dados de métricas estiver em baixo, não se envia um relatório a zeros: tenta-se mais tarde.

**Privacidade:** o Resend (o fornecedor de e-mail) vê o relatório e o teu endereço; é o único terceiro. Não leva dados de visitantes, por isso a Política de privacidade não muda.

Os intervalos são a última hora, 6 horas, 24 horas, 7 dias e 30 dias. Os números de «Agora» atualizam de 10 em 10 segundos; os gráficos de 30 em 30.

## Privacidade: só agregados

**Nunca se guarda** um IP, um nome de ficheiro, o conteúdo de um ficheiro, o *User-Agent*, nem um texto de erro do utilizador. Cada evento leva só **códigos** (a língua, o **país** da visita, o tema, o tipo de dispositivo: computador, telemóvel ou robô, o estado; e o **tamanho do ecrã e da janela**, a família do aparelho e, nos Chrome de Android que o dizem, o **modelo** do telemóvel, só em agregado) e **números** (quantos números se geraram, quanto tempo demorou). O **país** vem do cabeçalho `CF-IPCountry` que a rede do Render (Cloudflare) acrescenta ao pedido, **só se for duas letras maiúsculas** (qualquer outro valor, `XX` ou `T1` incluídos, guarda-se como `??` = «Desconhecido»; o valor bruto nunca é guardado) e conta-se uma vez por sessão aberta. Se o gráfico «Países» só mostrar «Desconhecido», o alojamento não envia o cabeçalho: a secção «Proxy e limite por IP» mostra a percentagem de pedidos que o trazem. A política de privacidade (22 línguas) diz isto. Para o teste do proxy, o IP vira um *hash* com sal aleatório (muda a cada arranque), só em memória e só da última hora. `tests/test_web_metricas.py` e `tests/test_web_admin.py` verificam que não há IPs no disco nem nomes de ficheiros nas respostas.

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

- `src/web/metricas.py`: o registo (buffer, SQLite, histogramas, proxy); `src/web/sistema.py`: CPU/memória/disco (`psutil`, cgroup); `src/web/admin.py`: autenticação e API; o frontend em `Admin.tsx`, `AdminEvolucao.tsx` (a vista dia a dia), `graficos.tsx` (gráficos em SVG feitos à mão, sem biblioteca), `admin-api.ts` e `estilos/_admin.scss`.
- **Exceção às 18 línguas:** o painel está só em português (é do dono, não da interface pública).
- Um evento novo: `serv.metricas.evento(tipo, a, b, c, v1, v2, v3)` (só códigos e números!) e a consulta em `Metricas.resumo`; atualiza o teste de privacidade.

## API pública (Swagger UI)

O painel tem uma secção **«API pública (Swagger UI)»** com ligações para `/api/v1/docs` (a documentação interativa da API pública em lote: pedidos, campos, respostas, e permite experimentá-los com uma chave `X-API-Key`) e para `/api/v1/openapi.json` (a descrição OpenAPI). Abrem noutro separador e estão acessíveis a quem tiver o endereço; as chaves criam-se e revogam-se aqui, no painel (`docs/API.md`).
