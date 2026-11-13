# Observabilidade

Como saber **o que se passa no servidor** sem guardar nada de ninguém. Código: `src/web/observabilidade.py`; painel: secção «Erros» de `/admin`.

## Os dois instrumentos

### 1. Registo estruturado (nos *logs* do Render)
Uma **linha JSON** por pedido da API e por evento das métricas, no stdout (o Render guarda-as e deixa pesquisar):

```json
{"t":"2026-11-13T22:38:32Z","n":"info","ev":"pedido","id":"18cc38a2","m":"POST","r":"/api/sessoes/{id_}/gerar","s":200,"ms":41.2,"v":"3.36.0"}
{"t":"2026-11-13T22:38:33Z","n":"info","ev":"evento","tipo":"geracao","a":"ok","c":"varios","v1":21.4,"v2":5000.0,"v3":5000.0}
{"t":"2026-11-13T22:40:01Z","n":"error","ev":"excecao","id":"a1b2c3d4","m":"GET","r":"/api/x","exc":"ValueError","onde":"motor.py:412:gerar","v":"3.36.0"}
```

- `n` = nível (`info`, `warn` para 4xx e falhas, `error` para 5xx e exceções); `id` = o **identificador do pedido**, que também vai no cabeçalho `X-Request-ID` da resposta e, num erro 500, no texto que o utilizador vê («Erro inesperado: a1b2c3d4»). Quem reportar um erro dá-te o código e procuras `a1b2c3d4` nos logs.
- `/health` e as páginas (HTML, ficheiros estáticos) **não** se registam (o Render e o anti-sono chamam `/health` de 5 em 5 s).
- Desliga-se com `LOG_PEDIDOS=0` (o livro de erros e as métricas continuam).

### 2. Livro de erros (no painel)
As falhas agrupadas por **assinatura** (tipo, rota em modelo, estado, classe da exceção, sítio no código), com contagem e primeira/última vez. `GET /api/admin/erros?intervalo=24h` (também com o `CLAUDE_TOKEN`, só leitura). Vive em memória (desde o último arranque, até 200 assinaturas); o que persiste na base são os **eventos** das métricas (`erro_http`, `geracao`, `motor_reiniciado`).

Tipos: **excecao** (erro não tratado → 500), **http** (resposta 5xx da API), **geracao** (geração que acabou em `erros`/`falhou`, com o motivo: `tempo`, `motor`, a chave da regra do motor), **motor_reiniciado** (OOM, tempo, cancelar tardio). Os 4xx (o utilizador a enganar-se) **não** entram.

## Privacidade (a regra do painel, aplicada também aos logs)
**Nunca** se regista: um IP, um nome de ficheiro, o conteúdo de um ficheiro, o *User-Agent*, a **mensagem** de uma exceção (pode trazer um nome ou um texto do utilizador), nem a rota com os seus valores (usa-se o modelo `/api/sessoes/{id_}/…`, nunca o id da sessão). De uma exceção só se guarda a **classe** e o **sítio** (`ficheiro.py:linha:função`). `tests/test_web_observabilidade.py` verifica-o (inclui uma exceção com um caminho de ficheiro na mensagem).

## Como ler isto a sério
- «O que falha?» → painel → **Erros**; ou `GET /api/admin/erros` com `Authorization: Bearer <CLAUDE_TOKEN>`.
- «O que aconteceu àquele pedido?» → Render → *Logs* → pesquisar o `id`.
- «Está lento?» → painel → **Pedidos** (p50/p95 por rota) e o script `scripts/medir_render.py` (ver `docs/MEDICOES.md`).

## Para quem mexe no código
- Evento novo = `serv.metricas.evento(...)` com **códigos e números** (já vai para o registo sozinho); uma falha nova que deva aparecer no livro: acrescentar o tipo a `_EVENTOS_ERRO` em `observabilidade.py`.
- Nunca meter texto livre do utilizador num campo de `linha(...)`.
