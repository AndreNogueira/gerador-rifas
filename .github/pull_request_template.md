## O quê
<!-- Uma ou duas frases: o que muda para quem usa a app. -->

## Porquê
<!-- O problema ou a ideia. Liga a issue, se houver: Closes #123 -->

## Como testei
<!-- Comandos e/ou passos no browser. Se mexe na interface, junta uma captura de ecrã (claro e escuro, se for caso disso). -->

## Lista de verificação
- [ ] `scripts/verificar.ps1` (ou `.sh`) passa em local
- [ ] Testes novos ou atualizados para o que mudou
- [ ] Se há **texto novo**: as 18 línguas em `src/core/idiomas/` e a contagem em `tests/test_i18n.py` (indica abaixo as que precisam de revisão nativa)
- [ ] Se mexe em **`src/core`**: os testes do `core` passam e a app Windows continua a funcionar
- [ ] Se afeta o **serviço público**: pensei nos limites (memória, 1 geração de cada vez, por IP)
- [ ] Sem segredos, e versões novas **fixadas exatamente**
- [ ] `VERSAO` em `src/web/__init__.py` atualizada **e uma entrada em `src/web/CHANGELOG.md`** (a página «Changelog» do site), se a mudança é visível ao utilizador
- [ ] Documentação (`CLAUDE.md`, `README.md`, `docs/`) atualizada, se for caso disso

## Notas para quem revê
<!-- Decisões difíceis, o que ficou de fora, riscos. -->
