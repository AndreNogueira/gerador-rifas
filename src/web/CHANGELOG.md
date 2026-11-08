# Changelog

Tudo o que mudou no Gerador de Rifas, da versão mais recente para a mais antiga. Este ficheiro é a única fonte: a página «Changelog» do site lê-o tal como está.

Formato (para quem o edita): `## <versão> — <data>`, depois secções `### Novo`, `### Melhorado` ou `### Corrigido` com itens `- texto`. A primeira versão tem de ser igual a `VERSAO` em `src/web/__init__.py` (um teste verifica-o).

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
