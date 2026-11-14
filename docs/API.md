# API pública v1 (geração em lote)

Para automatizar: um lote de N pedidos de rifas a partir de **um só template**. Swagger em **`/api/v1/docs`** (contrato em `/api/v1/openapi.json`;
o Swagger interno do site, `/api/docs`, é outra coisa). Código: `src/web/api_v1.py`, chaves em `src/web/chaves_api.py`, testes em `tests/test_web_api_v1.py`.
Os nomes e descrições da API são em inglês (contrato público); as mensagens sobre o template e os números saem na língua do cabeçalho `X-Lingua`.

## Como o dono dá acesso

1. No Render: `ADMIN_TOKEN` definido (já é preciso para o painel). Com `DATABASE_URL` as chaves ficam no Neon; sem ela, num SQLite efémero.
2. Criar uma chave (aparece **uma única vez**; só o SHA-256 fica guardado):
   ```
   curl -c c.txt -H "Content-Type: application/json" -d '{"token":"<ADMIN_TOKEN>"}' https://<site>/api/admin/entrar
   curl -b c.txt -H "Content-Type: application/json" -d '{"nome":"Associação X","quota_dia":50000}' https://<site>/api/admin/chaves
   ```
3. Listar (`GET /api/admin/chaves`: prefixo e uso de hoje, nunca o segredo) e revogar (`DELETE /api/admin/chaves/<id>`, vale logo).

## Fluxo de quem usa

```
curl -H "X-API-Key: rk_..." -H "Content-Type: application/json" https://<site>/api/v1/batches -d '{"items":[
   {"name":"Rifa Natal","first":1,"last":500,"digits":4,"per_file":100,"prefixes":["A-","B-"]},
   {"name":"Rifa Páscoa","first":1,"last":300}]}'                      # -> {"id": "...", "state": "waiting_files", ...}
curl -X PUT -H "X-API-Key: rk_..." --data-binary @template.pdf  https://<site>/api/v1/batches/<id>/template
curl -X PUT -H "X-API-Key: rk_..." --data-binary @digitos.png    https://<site>/api/v1/batches/<id>/digits
curl -X POST -H "X-API-Key: rk_..." https://<site>/api/v1/batches/<id>/start          # 202
curl -H "X-API-Key: rk_..." https://<site>/api/v1/batches/<id>                         # até state = done
curl -H "X-API-Key: rk_..." -o tudo.zip https://<site>/api/v1/batches/<id>/download
curl -X DELETE -H "X-API-Key: rk_..." https://<site>/api/v1/batches/<id>
```

Estados do lote: `waiting_files` → `ready` → `running` (`cancelling`) → `done` | `done_with_errors` | `failed` | `cancelled`.
Estados de cada item: `pending`, `queued` (à espera da vez do motor), `running`, `done`, `errors`, `failed`, `cancelled`.
Fica de fora, por agora: logótipo e QR de verificação por item (só no site e na app Windows).

## Limites e defesas (todas por variável de ambiente)

| Variável | Por omissão | O que limita |
|---|---|---|
| `API_PEDIDOS_POR_MIN` | 120 | pedidos por minuto por chave (429) |
| quota da chave | 100 000 | **números por dia** (UTC) por chave, definida ao criar; um `start` que passaria dela é recusado sem gastar nada (429) |
| `API_MAX_ITENS` | 20 | itens por lote |
| `MAX_NUMEROS` | 30 000 | números por item (o mesmo teto do site) |
| `API_MAX_NUMEROS_LOTE` | 3 × `MAX_NUMEROS` | números somados num lote |
| `API_LOTES_ATIVOS` | 3 | lotes por chave (a gerar ou por descarregar) |
| `API_ESPERA_MIN` | 20 | quanto um item espera pela vez do motor antes de falhar |
| `JOB_MAX_MIN`, `JOB_TTL_MIN`, `MAX_UPLOAD_MB` | 10, 30, 25 | tempo de cada item, validade dos ficheiros sem acessos, tamanho dos uploads |

- **Uma geração de cada vez no servidor**: os itens de um lote entram na fila do mesmo motor do site (nunca o travam: quem usa o site passa à frente entre dois itens).
- Falhas de autenticação: 20 por minuto por IP e depois 429. O lote de uma chave é invisível (404) para as outras.
- **Privacidade**: nada do template, dos números ou dos nomes vai para logs ou métricas; as métricas só têm códigos e totais, nunca a chave nem o prefixo.
- Os ficheiros vivem em disco efémero (sessão do lote) e apagam-se ao fim de `JOB_TTL_MIN` sem acessos ou com `DELETE`.
