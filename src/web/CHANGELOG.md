# Changelog

Tudo o que mudou no Gerador de Rifas, da versão mais recente para a mais antiga. Este ficheiro é a única fonte: a página «Changelog» do site lê-o tal como está.

Formato (para quem o edita): `## <versão> — <data>`, depois secções `### Novo`, `### Melhorado` ou `### Corrigido` com itens `- texto`. A primeira versão tem de ser igual a `VERSAO` em `src/web/__init__.py` (um teste verifica-o).

## 3.15.0 — 2026-11-08

### Novo
- **Séries e prefixos:** um texto antes dos algarismos (`A-` dá A-0001). Com várias séries separadas por vírgulas (`A-, B-, C-`) cada uma repete o intervalo e tem os seus próprios PDFs (`Rifa - A - 0001 - 0300.pdf`); com «Um único PDF», sai um por série. O prefixo aceita letras, espaço, ponto, hífen e barra (até 6 caracteres, sem algarismos) e desenha-se em Helvetica-Bold, do tamanho e da cor dos algarismos.
- **Saltar números:** `13, 100-110` tira esses números da sequência (o resumo, os ficheiros e a verificação contam só os que se imprimem).
- **Uma cor para cada série:** cada série fica com a sua cor (no prefixo e nos algarismos).
- Tudo isto também vai na ligação de «Copiar ligação» e na pré-visualização.

## 3.14.0 — 2026-11-08

### Novo
- **Instalar como app (PWA):** o Gerador de Rifas pode ser instalado no telemóvel e no computador e a casca da app abre mesmo sem rede (gerar continua a precisar do servidor). Um *service worker* simples guarda só a página, os ficheiros da app e os textos da interface; nunca toca nos teus ficheiros nem nos pedidos de geração.

## 3.13.0 — 2026-11-08

### Novo
- **Lembrar o ficheiro dos algarismos:** quem volta no ano seguinte já não o repete. Fica guardado só no seu browser (nunca no servidor) e é reutilizado quando carrega um template novo; escolher outro troca-o e «Limpar tudo» apaga-o.
- **Copiar ligação:** um botão que copia uma ligação com os valores do formulário (de, até, modo, máximo por ficheiro, papel, margem e nome). Quem a abrir vê os mesmos valores; os ficheiros nunca vão na ligação.

## 3.12.0 — 2026-11-08

### Novo
- Páginas **Termos de utilização**, **Política de privacidade** e **Contacto**, com ligações no rodapé. São versões provisórias, a rever com apoio jurídico antes de o serviço cobrar.
- **Botão de donativo** no rodapé: só aparece quando o dono configura a ligação (`DONATIVO_URL`). O contacto (`CONTACTO_EMAIL`) e o nome do responsável (`RESPONSAVEL`) também vêm da configuração do servidor, nunca do código.

## 3.11.0 — 2026-11-08

### Novo
- **Funil de utilização** no painel de administração: quantos eventos há em cada etapa (sessão, template, algarismos, pré-visualização, geração, descarga) e que parte da etapa anterior chegou à seguinte. Mostra onde as pessoas desistem. Conta eventos, não pessoas.

## 3.10.0 — 2026-11-08

### Novo
- Esta página: o **Changelog** com tudo o que muda, versão a versão.
- Em **dezembro** o tema visual automático é o **Natal** (para quem nunca escolheu um). Escolher outro tema continua a ficar guardado.

### Melhorado
- Menos uma dependência no servidor (`python-multipart` já não era usada: os ficheiros chegam em corpo cru).

## 3.9.0 — 2026-11-08

### Novo
- Layout pensado para **ecrãs grandes** (4K, ultra-wide) e para **telemóveis recentes**: cabeçalho compacto e botões de 44 px.
- A pré-visualização mostra uma imagem quando o browser não consegue mostrar PDFs dentro da página (Chrome do Android).
- O painel de administração regista o **tipo de ecrã** (classe, tamanho, família) sem guardar nada pessoal.
- O serviço chama-se a si próprio de 10 em 10 minutos para não adormecer.

## 3.8.0 — 2026-11-08

### Novo
- **Painel de administração** (só para o dono, com palavra-passe) com gráficos e explicações de sistema e de utilização: só agregados, nunca dados pessoais.

## 3.7.0 — 2026-11-08

### Novo
- **SEO**: título, descrição e texto por página, `robots.txt`, `sitemap.xml` e erro 404 a sério nas páginas que não existem.

## 3.6.0 — 2026-11-08

### Melhorado
- O site entrega **um só ficheiro de JavaScript**, ofuscado e pré-comprimido: o que viaja é bastante menor do que antes.

## 3.5.0 — 2026-11-08

### Novo
- Tema visual **Matrix Gamer**: chuva de caracteres verdes e brilho de neon.

## 3.4.0 — 2026-11-08

### Melhorado
- Os estilos passam a **Sass** e saem num **único CSS**. A estrutura da página é igual em todos os temas: um tema só muda cores e formatação.

## 3.3.0 — 2026-11-07

### Novo
- **Temas visuais**: Premiado (o novo aspeto por omissão) e mais sete (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala e Natal), cada um com claro e escuro.
- Novo ícone da aplicação.
