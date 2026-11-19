# Comentários e problemas reportados

Três páginas dos visitantes, **bem à vista** (cabeçalho, rodapé e menu «hambúrguer»), mais uma aba no painel do dono:

| Página | Para quê |
|---|---|
| `/comentarios` | A lista dos comentários, mais recentes primeiro (20 de cada vez, «Ver mais»). Anónimos aparecem sem nome. Nunca mostra IPs. |
| `/opiniao` | O formulário: o texto (5–1000 letras) e **ficar anónimo(a)** ou **mostrar um nome** (até 40 letras; sem nome aparece «Visitante n.º ####», um número tirado do id do comentário). |
| `/reportar-problema` | Resumo, o que aconteceu, como repetir (opcional) e, se a pessoa marcar, a informação técnica (navegador, ecrã e janela). **«Abrir»** cria um *issue* no GitHub do projeto, sem conta. |
| `/admin` → aba **Comentários** | O dono vê só o **país**, o **texto** e o **estado** (novo, lido, favorito, escondido; quem escreveu não interessa), filtra por estado, marca como lidos, **esconde** um comentário da página pública sem o apagar e apaga (spam, abuso). O acesso só de leitura (`CLAUDE_TOKEN`) vê mas não muda nada. |

As três páginas dos visitantes estão em `seo.SEM_INDICE`: existem em todas as línguas mas ficam **fora do Google e do sitemap** (o texto é de terceiros).

## Ligar «Reportar problema» ao GitHub (o que SÓ tu podes fazer)

Sem isto a página existe mas diz «esta função ainda não está ativa» e o botão **Abrir** fica desligado.

1. No GitHub: **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
   - *Resource owner*: a tua conta. *Repository access*: **Only select repositories → `gerador-rifas`** (só esse).
   - *Permissions → Repository permissions*: **Issues: Read and write** (e mais nada).
   - Validade: a que preferires (anota quando expira: a função pára nesse dia).
2. No Render → o serviço → **Environment**: `GITHUB_ISSUES_TOKEN` = o token (**é uma palavra-passe**: nunca no repositório, no chat nem num ficheiro) e `GITHUB_REPO` = `AndreNogueira/gerador-rifas` (`dono/nome`).
3. Cada problema vira um issue com a etiqueta **`bug-do-site`** (o GitHub cria-a à primeira vez).

O texto do visitante vai **sempre dentro de blocos de código** (nada de @menções que notificam gente, #referências, imagens ou ligações), o título é uma linha limpa e o **IP nunca é enviado** (`github_issues.py`). Um erro do GitHub nunca chega ao visitante tal e qual.

## Privacidade (o que fica guardado)

- **Comentário** (tabela `comentarios`, no Neon com `DATABASE_URL`, senão SQLite local e efémero): texto, data, nome a mostrar (vazio se anónimo) e o **país** de onde veio (o código de duas letras do cabeçalho `CF-IPCountry` da rede do alojamento, como nas estatísticas; `??` se não vier). **O endereço IP não se guarda.** O país só o dono o vê e fica com o comentário.
- O limite de comentários por hora e por pessoa conta-se **em memória** (`LimiteHorario`) e esquece-se: o IP vive na RAM durante uma hora, como no resto do site, e nunca vai para a base.
- **Migração:** a 1.ª versão (3.51.0) guardava o IP. Ao abrir uma tabela dessa versão, `Comentarios` acrescenta a coluna `pais` e **apaga a coluna `ip`** (e os IPs que tinha); os comentários antigos ficam com país «??» (`tests/test_web_opiniao.py`, em SQLite e Postgres).
- A API pública (`GET /api/comentarios`) devolve só id, data, nome, número de visitante e texto. Nunca o país nem o IP.
- As métricas só contam «houve um comentário» (anónimo / com nome / «Visitante») e «um problema → GitHub / falhou»; **nunca o texto**. Ver o painel «Evolução diária» → Funcionalidades.
- A **Política de privacidade** das 22 línguas tem uma secção «Comentários e problemas reportados» (`legal_opiniao.py`, no fim da página) que diz tudo isto. Mudar o prazo ou o que se guarda obriga a mudar esse texto.

## Defesas

- Campo-isco escondido (`site`): um robô que o preencha recebe «ok» e nada se guarda.
- Comentários: 3 por IP e hora e 5 por IP e minuto (em memória), 100 no site todo por hora (contados na base, sem IP). Problemas: 3 por IP e hora, 20 no site todo por hora (em memória, recomeçam com o servidor).
- Limpeza do texto (`opiniao.limpar_texto`): sem caracteres de controlo nem marcas que invertem o texto; corpos enormes recusados antes.
- O React escreve o texto como texto (nunca HTML).

## Para quem mexe no código

`src/web/opiniao.py` (base e limites), `rotas_opiniao.py` (a API), `github_issues.py` (o issue), `admin.py` (`/api/admin/comentarios`), `legal_opiniao.py` (privacidade); no frontend `Comentarios.tsx` (lista e formulário), `Problema.tsx`, `AdminComentarios.tsx`. Testes: `tests/test_web_opiniao.py` (o GitHub nunca é chamado: `Servico.criar_issue` troca-se por uma função falsa), `Opiniao.test.tsx`, `AdminComentarios.test.tsx`. Textos: `web_op_*`, `web_com_*`, `web_bug_*` (22 línguas) e os tópicos `tut_f_comentarios_*`/`tut_f_problema_*`.
