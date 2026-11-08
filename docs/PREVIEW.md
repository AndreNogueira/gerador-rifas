# Pré-visualização de um PR

Para ver a app de um PR a funcionar **antes** do merge, sem tocar no serviço do Render:

1. Põe a etiqueta **`preview`** no PR (no GitHub, ou `gh pr edit <n> --add-label preview`).
2. Em ~3 minutos o robô comenta no PR com um endereço `https://….trycloudflare.com`. É a app desse ramo, com o frontend compilado, sem painel de administração (`ADMIN_TOKEN` não existe) e com uma chave de QR de teste.
3. Fica no ar **40 minutos**; um push novo no PR reinicia-a com o código novo; no fim o robô comenta «terminada» e tira a etiqueta (para outra, põe-na de novo).

**Como funciona** (`.github/workflows/preview.yml`): o próprio GitHub Actions compila o frontend, arranca `python -m src.web` e abre um túnel de Cloudflare (*quick tunnel*, sem conta nem chave; o `cloudflared` vem de uma versão fixa e o *workflow* confere o SHA-256). `PUBLIC_URL` é o endereço do túnel, por isso o canónico, o sitemap e o QR apontam para ele.

**Porque não no Render:** o serviço é uma *imagem* (ghcr.io + *deploy hook*) e o Render só cria pré-visualizações de serviços ligados ao Git; um segundo serviço gratuito gastaria as mesmas 750 horas por mês. Aqui o custo são os minutos do Actions (≈ 45 por pré-visualização; o repositório privado tem 2000 por mês).

**Limites e cuidados**
- Só para PRs **do próprio repositório** (um *fork* não corre o *workflow*) e quem põe etiquetas tem de ter escrita.
- O endereço é público a quem o tiver: não ponhas segredos num PR com esta etiqueta. Os ficheiros que carregares na pré-visualização ficam num disco temporário que desaparece no fim.
- Corre uma só pré-visualização por PR; é mais lenta que o Render (CPU partilhada do Actions) e o túnel gratuito não garante disponibilidade.
- Para testar o próprio *workflow*: abre um PR que o altere e põe-lhe a etiqueta (o evento usa o ficheiro do PR).
