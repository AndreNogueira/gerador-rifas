# Changelog

Tudo o que mudou no Gerador de Rifas, da versão mais recente para a mais antiga. Este ficheiro é a única fonte: a página «Changelog» do site lê-o tal como está.

Formato (para quem o edita): `## <versão> — <data>`, depois secções `### Novo`, `### Melhorado` ou `### Corrigido` com itens `- texto`. A primeira versão tem de ser igual a `VERSAO` em `src/web/__init__.py` (um teste verifica-o).

## 3.27.0 — 2026-11-12

### Novo
- **Editor de templates:** em vez de usar um template do Canva, desenhe a rifa no site (página «Editor de templates», ligada a partir do passo 1): junte textos, retângulos, linhas e o número 0001 (uma vez, ou duas se tiver talão), arraste cada elemento para o sítio com o rato ou as setas, mude cores, tamanhos e o fundo, e carregue em «Usar este template». O ecrã usa a letra Vera, a mesma do PDF, por isso o que se vê é o que sai; o rascunho fica só no browser. Os textos não podem ter sequências como 0123, que o programa confundiria com o número do bilhete (o ecrã e o servidor avisam).

## 3.26.0 — 2026-11-12

### Novo
- **Cinco temas novos:** Halloween, Praia, Jornal antigo, Terminal verde e Cartaz de circo, cada um com claro e escuro. O site passa a ter 14 temas; a estrutura continua igual em todos (só mudam cores e formatação).

## 3.25.0 — 2026-11-08

### Novo
- **Um endereço por língua para os motores de pesquisa:** cada língua tem o seu endereço (/en, /ja/tutorial…) com título, descrição e texto nessa língua, e o site diz ao Google quais as versões equivalentes (hreflang). O português continua em /. A língua escolhida passa a aparecer na barra de endereço.

## 3.24.1 — 2026-11-08

### Melhorado
- **Caixas de seleção alinhadas:** «Uma cor para cada série» e as outras caixas ficam junto ao texto, em vez de no extremo do cartão.

## 3.24.0 — 2026-11-08

### Melhorado
- **Tutorial com capturas do site:** os tópicos de base do tutorial mostram agora o próprio site, nas 18 línguas, em vez da app Windows.

## 3.23.0 — 2026-11-08

### Novo
- **Tutorial e vídeo de cada funcionalidade:** o tutorial ganha um tópico por funcionalidade (séries, lista e folha de controlo, marcas de corte, galeria, marca própria, QR, sorteio, guardar e partilhar o pedido, instalar como app e temas), cada um com um vídeo curto, gravado na própria interface, em português e em inglês.
- **Changelog, Termos, Privacidade e Contacto nas 18 línguas:** o texto aparece na língua escolhida. O Changelog tem um resumo traduzido de cada versão (o completo é o português); os textos legais são traduções sem revisão nativa e, em caso de divergência, vale a versão portuguesa.
- **App Windows 2.4** com o que o site ganhou desde a 3.10: menu «Extras» com séries, prefixos e cor por série, números a saltar, cor dos números, logótipo, marcas de corte, galeria de templates, sorteio verificável e exportação da lista (CSV) e da folha de controlo; e o visual Natal automático em dezembro. O QR de verificação e instalar como app ficam só no site.

## 3.22.0 — 2026-11-08

### Melhorado
- **Contraste dos 9 temas medido de verdade:** um teste num browser renderiza as páginas em claro e em escuro, em cada tema, e mede o contraste do texto contra os pixéis reais do fundo (WCAG AA: 4,5 para texto normal e 3 para texto grande). Corrigido o que não passava: o texto de exemplo dos campos (agora na cor suave do tema), o texto do rodapé do tema Janela 98, os botões em gradiente dos temas Quermesse e Matrix Gamer, e o cor-de-rosa do passo 2 nos temas Arcade, Brutalista e Risografia, além de uma cor do Janela 98 escuro.
- O grande número decorativo de cada passo deixa de ser lido pelos leitores de ecrã (o título já diz o passo).

## 3.21.0 — 2026-11-08

### Novo
- **Sorteio verificável** (página «Sorteio»): sorteia números de um intervalo (com números a saltar) de forma que qualquer pessoa possa repetir o sorteio e obter o mesmo resultado. O resultado só depende dos números, de quantos se sorteiam e de uma **semente pública** (por exemplo o resultado de uma lotaria, ou a aleatoriedade pública do drand, que um botão vai buscar). Faz-se tudo no browser, nada vai ao servidor, e «Copiar ligação» partilha um endereço que repete o mesmo sorteio.
- O método está descrito passo a passo na documentação e há uma implementação de referência: o site e a referência dão os mesmos números nos mesmos testes.

## 3.20.0 — 2026-11-08

### Novo
- **QR em cada bilhete:** um código QR de verificação num canto de cada rifa (templates de uma só rifa, escolhendo o canto e o tamanho). Ler o QR abre uma página que confirma que o código foi emitido por este serviço para aquele bilhete, na língua de quem lê. É assinado com uma chave que só o servidor tem: não há nada guardado numa base de dados. A página diz que isto **não prova** que o bilhete foi pago nem que ganhou: isso é com quem organiza a rifa.
- Só aparece quando o dono do serviço configura a chave (`VERIFICACAO_CHAVE`). Os pedidos com QR têm um teto próprio de 10 000 números (`MAX_NUMEROS_QR`): cada QR custa tempo de CPU.

## 3.19.0 — 2026-11-08

### Novo
- **Marca própria:** a **cor dos números** (um seletor de cor; vale para qualquer template e, com várias séries coloridas, a cor da série ganha) e o **logótipo da associação** em cada rifa (PNG ou JPG até 2 MB, nos templates de uma só rifa que a folha repete): escolhe-se o canto (↖ ↗ ↙ ↘) e o tamanho (10 a 40 % da altura da rifa). O PNG mantém a transparência.
- O logótipo fica só na sessão (apaga-se com ela e com «Limpar tudo») e vê-se logo na pré-visualização.

## 3.18.0 — 2026-11-08

### Novo
- **Galeria de templates:** quem não sabe fazer o template no Canva escolhe um de quatro desenhos (Bosque, Quermesse, Natal e Gala), escreve o título, a organização, até três prémios e a data do sorteio, vê a pré-visualização e carrega em «Usar este template»: o template e os algarismos ficam prontos e só falta escolher os números. Cada desenho é uma rifa com talão (o número duas vezes) que o programa repete na folha A4.
- Os desenhos são originais deste projeto, na letra Vera (livre). A letra só tem o alfabeto latino: com outras letras aparece um aviso em vez de uma imagem.

## 3.17.0 — 2026-11-08

### Novo
- **Marcas de corte:** uma caixa no painel da folha (templates de uma só rifa repetida na folha) que desenha traços curtos nas margens, a prolongar cada linha de corte da grelha, para cortar a direito. Pedem pelo menos 3 mm de margem.
- O **talão e o canhoto** (o número duas vezes em cada bilhete) já funcionavam: o template leva o número no canhoto e na parte principal e os dois saem iguais. Agora está testado e documentado.
- A **sangria** já é respeitada: se o PDF do Canva tem uma caixa de corte (TrimBox) menor do que a página, a rifa é só o que está dentro dela.

## 3.16.0 — 2026-11-08

### Novo
- **Exportar a lista de bilhetes (CSV):** um ficheiro que abre no Excel ou no Calc, com um bilhete por linha (série, número, e as colunas Nome, Contacto e Pago em branco). Respeita prefixos, séries e números saltados.
- **Folha de controlo de vendas (PDF):** uma tabela A4 para imprimir e preencher à mão (36 bilhetes por página, com caixa de «pago»). Nas línguas cujas letras o PDF não escreve (grego, russo, chinês, polaco…) os cabeçalhos saem em inglês.
- Nada fica guardado no servidor: a lista sai só do que está no formulário.

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
