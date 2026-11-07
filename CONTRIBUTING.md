# Como contribuir

O trabalho faz-se **em pull requests pequenos**: cada PR traz uma funcionalidade (ou uma correção) que se percebe e se testa sozinha. Quando o PR entra em `main`, o site público atualiza-se sozinho (ver [`README.md`](README.md#cicd)), por isso `main` tem de estar sempre verde.

## O fluxo

1. **Ideia → issue** (opcional para coisas pequenas). Há modelos para [funcionalidade](.github/ISSUE_TEMPLATE/funcionalidade.yml) e [erro](.github/ISSUE_TEMPLATE/erro.yml). Ideias já pensadas: [`docs/ROADMAP.md`](docs/ROADMAP.md).
2. **Branch a partir de `main` atualizada**, com um nome que diz o tipo e o assunto:
   `feat/guardar-algarismos`, `fix/cancelar-na-verificacao`, `tema/halloween`, `docs/…`, `chore/…`.
   ```
   git switch main && git pull && git switch -c feat/guardar-algarismos
   ```
3. **Commits curtos, em português**, no mesmo tom do histórico («Guardar os algarismos no browser entre sessões»). Um commit = uma ideia; nada de «wip» em `main` (o PR é junto num só commit, ver passo 6).
4. **Antes de abrir o PR** corre tudo o que o CI corre:
   ```
   powershell -File scripts/verificar.ps1        # Windows (junta -Docker para construir também a imagem)
   sh scripts/verificar.sh                       # Linux/macOS
   ```
5. **Abre o PR** contra `main` e preenche o [modelo](.github/pull_request_template.md): o quê, porquê, como testaste e (se mexe na interface) uma captura de ecrã. O [CI](.github/workflows/ci.yml) corre sozinho no PR.
6. **Merge só com o CI verde**, em *Squash and merge* (fica um commit por PR em `main`) e a branch é apagada. O `main` verde dispara o `deploy.yml`.

> O GitHub gratuito não deixa **proteger a branch** `main` num repositório privado, por isso «PR + CI verde» é uma regra de equipa, não uma trava técnica. Se o repositório passar a público ou a plano pago, ativa em *Settings → Branches* (ou *Rulesets*): exigir PR, exigir os *checks* do CI e proibir *force-push*.

## Regras que não se negociam

Estão explicadas em [`CLAUDE.md`](CLAUDE.md); em resumo:

- **`src/core` é só lógica**: nada de Tkinter, Windows ou FastAPI. Qualquer alteração ao `core` só entra com os testes a passar (antes e depois) e **tem de continuar a funcionar para a app Windows**.
- **Textos da interface**: todos vêm do servidor, já traduzidos. Uma chave nova custa **18 traduções** (`src/core/idiomas/ui_*.py`) e muda a contagem em `tests/test_i18n.py`. Se não souberes uma língua, escreve a tua melhor tradução e diz no PR que precisa de revisão nativa.
- **Versões**: sempre as últimas estáveis, **fixadas exatamente** (`uv.lock`, `pnpm-lock.yaml`, tags do Docker). Nada de intervalos flutuantes. O Dependabot propõe as atualizações em PRs.
- **Sem segredos** no repositório. Credenciais só como *secrets* do GitHub / variáveis do Render.
- **Uploads são território hostil**: validar o tipo real, limites de tamanho/números/tempo, nunca usar nomes do cliente.
- **Serviço público**: qualquer funcionalidade nova tem de pensar nos limites (memória 512 MB, 1 geração de cada vez, por IP).

## Receitas

| Quero… | Onde mexer | Atenção |
|---|---|---|
| Mudar a interface | `src/web/frontend/src` | Biome (`pnpm lint`), `tsc` (`pnpm tipos`), Vitest (`pnpm teste`); atualiza o `servidor-falso.ts` se a API mudar |
| Adicionar um endpoint | `src/web/rotas.py` (+ `modelos.py`) | testa em `tests/test_web_api.py`; erros por `ErroApi`; respeita os limites de `limites.py` |
| Adicionar um texto | os 18 `src/core/idiomas/ui_*.py` + `servidor-falso.ts` | `tests/test_i18n.py` conta as chaves |
| Mexer no motor | `src/core` | os testes do `core`, `teste_folha`/`teste_canva` e a app Windows (ver `CLAUDE.md`) |
| Mudar o deploy | `.github/workflows`, `Dockerfile`, `render.yaml` | só se testa de verdade em `main`; faz PRs pequenos |

## Versão e *rollback*

- Uma mudança visível ao utilizador sobe `VERSAO` em `src/web/__init__.py` (minor para funcionalidades, patch para correções). O `/health` mostra-a, e serve para confirmar que o deploy chegou.
- Para voltar atrás, **reverte o PR** (`git revert`) e faz outro PR: o deploy segue o fluxo normal. A imagem de cada commit continua publicada em `ghcr.io/<dono>/<repo>:sha-<commit>`, caso precises de a inspecionar.

## Dependências

O [Dependabot](.github/dependabot.yml) abre PRs semanais (agrupados) para Python (`uv`), frontend (`npm`/pnpm) e GitHub Actions. O CI valida-os como a qualquer PR. As tags do `Dockerfile` (`PYTHON`, `NODE`, `UV`) atualizam-se à mão, com o mesmo cuidado de as fixar exatamente.
