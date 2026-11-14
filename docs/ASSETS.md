# Vídeos e capturas do site fora da imagem Docker

Os ~20 MB de `app/assets` (vídeos do tutorial e capturas) **já não vão na imagem Docker do site**: ficam num `.zip` no **armazenamento de objetos do Neon** (S3, bucket `site-assets`, `public_read`, região de Frankfurt, a mesma do projeto). A app Windows continua a usar `app/assets` inteira.

## Como funciona

1. `scripts/publicar_assets.py` junta o subconjunto que o **site** usa (`video/` sem os `windows_*.mp4`, e `ajuda/` sem as capturas `<lg>_a|b|c.png`: ~15 MB) num `.zip` determinístico, `saida/assets-web-<sha12>.zip`, e diz que variáveis pôr.
2. O `.zip` está no bucket; o nome leva o SHA-256, por isso cada versão tem o seu URL (sem cache velha).
3. O serviço tem `ASSETS_URL` (o URL do `.zip`) e `ASSETS_SHA256` (por omissão os do Dockerfile). No arranque descarrega-o **em segundo plano** (o `/health` responde logo), confere o SHA-256, extrai `ajuda/` e `video/` para uma pasta temporária (`config.pasta_assets()`) e serve-os como sempre (`/videos`, `/ajuda`, recortes do tutorial). Código: `src/web/assets_remotos.py`.
4. Se o armazenamento falhar, o site funciona sem vídeos nem capturas e volta a tentar passado um minuto, quando alguém abre o tutorial. Só se extraem `ajuda/<nome>` e `video/<nome>` com nomes simples e tamanhos limitados.
5. Sem `ASSETS_URL` (desenvolvimento, testes) usa `app/assets` como antes. A imagem de testes (`--target testes`) mantém os assets, porque os testes verificam que existem.

## Quando mudam os vídeos ou as capturas (regravar, novo tópico, nova língua)

```
uv run python scripts/publicar_assets.py              # cria saida/assets-web-<sha12>.zip e imprime ASSETS_URL e ASSETS_SHA256
```

Enviar o `.zip` para o bucket `site-assets` (qualquer uma):
- com credenciais do Neon (`neon env pull`, ou uma credencial `storage:write`): `uv run --with boto3 python scripts/publicar_assets.py --enviar`;
- sem credenciais: um URL pré-assinado (`presign_storage_object`, no MCP do Neon) e `curl -X PUT -H "Content-Type: application/zip" --data-binary @saida/assets-web-….zip "<url>"`.

Depois, troca os dois `ARG` do estágio `web` do **Dockerfile** (`ASSETS_URL` e `ASSETS_SHA256`) pelos valores impressos e faz o PR: um teste (`tests/test_assets_publicados.py`) **falha** enquanto o SHA-256 do Dockerfile não for o dos ficheiros do repositório, por isso é impossível publicar um vídeo regravado sem o `.zip` correspondente. (No Render podes sobrepor os dois valores nas variáveis do serviço, sem novo deploy da imagem.) Os `.zip` antigos podem apagar-se do bucket quando já ninguém os usa.

## Notas

- O bucket é `public_read` (leitura anónima, escrita autenticada); o `.zip` só tem coisas que o site já mostra a toda a gente.
- Um CDN à frente do bucket não é preciso: o `.zip` descarrega-se uma vez por arranque (15 MB), não por visita.
- O Render gratuito tem disco efémero: a cada reinício volta a descarregar (alguns segundos, em segundo plano).
