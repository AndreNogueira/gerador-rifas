# Changelog

Tudo o que mudou no Gerador de Rifas, da versão mais recente para a mais antiga. Este ficheiro é a única fonte: a página «Changelog» do site lê-o tal como está.

Formato (para quem o edita): `## <versão> — <data>`, depois secções `### Novo`, `### Melhorado` ou `### Corrigido` com itens `- texto`. A primeira versão tem de ser igual a `VERSAO` em `src/web/__init__.py` (um teste verifica-o).

## 3.91.0 — 2026-11-26

### Melhorado
- **A galeria de desenhos ganha o mesmo destaque do envio do template**: na página inicial, escolher um desenho já feito (sem precisar do Canva) deixa de ser um link secundário escondido por baixo do envio do PDF — fica agora numa caixa com o mesmo peso visual.
- **Mais ligações entre as páginas**: os guias do sorteio e do preçário passam a ligar à sua própria ferramenta (`/sorteio`, `/precario`) em vez de ao gerador de rifas, e a página inicial passa a ligar também ao índice de guias «Como fazer» (`/como-fazer`).

## 3.90.0 — 2026-11-26

### Corrigido
- **Página em português já não troca de língua sozinha**: ao visitar um endereço sem prefixo (`/`, `/tutorial`, as páginas «Como fazer», …) sem dizer ao browser que a língua preferida é português — o caso de muitos motores de busca e de alguns browsers — o site reescrevia sozinho o URL e todo o conteúdo para inglês. O português sem prefixo passa a ser sempre português, como sempre esteve definido (`rota.tsx`); as 21 línguas com prefixo no URL continuam a funcionar como antes. O `robots.txt` deixa também de bloquear por completo os pedidos que o site faz a si mesmo para montar a página (`/api/linguas`, `/api/textos`, `/api/guia(s)`) e a documentação da API pública (`/api/v1/docs`), para os motores de busca conseguirem desenhar e indexar bem o site.

### Melhorado
- **Seletor de língua mais rápido**: os nomes nativos das línguas no seletor (como «Tiếng Việt» ou «Čeština») passam a usar a letra do sistema em vez da letra da marca — a página deixa de ter de ir buscar glifos extra só para os mostrar, o que atrasava a letra principal e por vezes empurrava o texto por baixo.

## 3.89.0 — 2026-11-26

### Melhorado
- **Mais três bibliotecas de imagens no preçário, de contorno: Tabler Icons, Lucide e Material Symbols** (todas sem exigir crédito): mais de 100 artigos ganharam alternativas destas bibliotecas, escolhidas uma a uma para representarem mesmo o artigo (não há forma automática de as encontrar, ao contrário das anteriores). Ao contrário das imagens coloridas, estas pintam-se da cor do texto do momento — do site, da app Windows ou do papel escolhido no PDF — para nunca ficarem invisíveis num tema escuro ou num papel escuro.

## 3.88.0 — 2026-11-21

### Melhorado
- **Mais duas bibliotecas de imagens no preçário: Twemoji e OpenMoji**: juntam-se ao Noto Emoji e ao Fluent Emoji 3D, sem trocar nenhuma imagem já existente — o seletor agrupa agora as imagens por biblioteca, com o nome de cada uma. O Twemoji (CC BY 4.0) e o OpenMoji (CC BY-SA 4.0) pedem crédito aos autores, que aparece na Política de privacidade e, só quando se usa mesmo uma dessas imagens, no rodapé do PDF e das etiquetas de levantamento gerados.

## 3.87.0 — 2026-11-21

### Melhorado
- **Mais imagens à escolha no preçário, do Fluent Emoji 3D da Microsoft (licença MIT, sem exigir crédito)**: os 93 artigos do catálogo ganharam, além das imagens Noto Emoji de sempre, uma alternativa no estilo 3D — sempre que exista para esse código — sem trocar nenhuma das imagens já lá estavam.

## 3.86.0 — 2026-11-21

### Melhorado
- **Espaço entre as rifas e marcas de corte entre cada uma**: ao ativar as marcas de corte (opções da folha), a folga que antes virava só margem extra passa a espaço entre cada rifa — a margem fica mesmo pequena, como pedida — e as marcas de corte (antes só nas margens da folha) aparecem agora também entre cada rifa, dos dois lados de cada corte.

## 3.85.0 — 2026-11-21

### Corrigido
- **Página 404 a sério**: uma ligação errada mostrava o gerador escondido por baixo do estado 404 (certo no servidor, mas o React tapava-o). Agora aparece mesmo uma página «Página não encontrada», nas 22 línguas, com a ligação para voltar.
- **Ícone de reserva (`favicon.ico`)**: browsers e ferramentas antigas que só olham para `/favicon.ico`, ignorando o ícone SVG, já têm um.

## 3.84.0 — 2026-11-21

### Novo
- **Desenho «Aniversário» na galeria e no preçário**: balões, bandeirinhas e confetis em rosa, turquesa e amarelo — o 25.º desenho a juntar-se aos já existentes, para a festa de aniversário ter o seu próprio estilo nas rifas, no preçário e nos vales.

## 3.83.0 — 2026-11-21

### Melhorado
- **Mais imagens à escolha por artigo do preçário**: cada artigo do catálogo pode agora ter até 8 imagens (antes 5) — todos os 93 ganharam pelo menos uma alternativa nova, escolhida a condizer (a água ganhou uma onda, o café um mate, o bolo confetis…).

## 3.82.0 — 2026-11-20

### Corrigido
- **Margens desiguais ao encher a folha com menos rifas do que cabiam**: quando se pedia menos rifas por folha do que o máximo, ficavam encostadas ao topo/esquerda e toda a folga ia para o fundo/direita — a guilhotina a direito já não separava bem cada rifa. Agora ficam sempre centradas, com a mesma margem nos quatro lados.

## 3.81.0 — 2026-11-20

### Novo
- **Etiquetas de levantamento**: paga-se num sítio e levanta-se noutro? Na página do preçário, cada artigo vira uma etiqueta com a imagem, o nome, o preço (se quiser) e a zona onde se levanta (o bar, a cozinha…), com as cópias que escolher, 24 por folha A4 com guias de corte e uma cor por zona. Um combo dá uma etiqueta por artigo, cada uma na zona da sua secção (site e app Windows; tutorial e vídeos incluídos).

## 3.80.0 — 2026-11-20

### Novo
- **Combos entre secções no preçário**: junte 2 a 4 artigos do catálogo, mesmo de secções diferentes (por exemplo, uma bifana e uma bebida), num só preço. O combo aparece numa secção nova, «Menus e combos», com as imagens dos artigos lado a lado, e pode ter um nome próprio (site e app Windows).

## 3.79.0 — 2026-11-20

### Novo
- **Cores e logótipo no preçário**: pode mudar a cor principal, a de destaque e a do papel do desenho (os preços ajustam-se sozinhos para se lerem sempre) e pôr o logótipo da sua associação (PNG ou JPG) no cabeçalho, à esquerda ou à direita, ou no rodapé (site e app Windows). As cores e o sítio ficam no ficheiro do preçário e na ligação partilhada; o logótipo só serve para desenhar a pré-visualização e o PDF e nunca se guarda.

## 3.78.0 — 2026-11-20

### Novo
- **Até 5 imagens à escolha por artigo**: no preçário, carregue na imagem de um artigo do catálogo e escolha a que mais gosta entre até 5 (a água pode ser uma gota, uma torneira, gelo, um copo…). A escolha vê-se no PDF e fica no ficheiro do preçário e na ligação partilhada (site e app Windows).

## 3.77.0 — 2026-11-20

### Melhorado
- **Listas e linhas do preçário mais arrumadas**: todas as listas de escolha do site têm agora o aspeto dos restantes campos, com uma seta que acompanha o tema (claro e escuro). No preçário, o × de tirar um artigo e o botão da foto ocupam muito menos espaço, os preços já não saltam para uma segunda linha e, no telemóvel, o nome fica em cima e os campos por baixo.

## 3.76.0 — 2026-11-20

### Novo
- **Fotos próprias no preçário**: em cada artigo pode carregar em «Foto» e pôr uma imagem sua (PNG ou JPG) no lugar do ícone (até 20 por preçário; site e app Windows). A foto é reduzida no seu computador e só serve para desenhar a pré-visualização e o PDF: não se guarda no servidor, nem no ficheiro do preçário, nem na ligação partilhada.

## 3.75.0 — 2026-11-20

### Novo
- **Partilhar o preçário por ligação** (no site, quando o serviço tem base de dados): «Partilhar por ligação» na página do preçário cria uma ligação que qualquer pessoa pode abrir para ver e continuar o seu preçário (textos, artigos, preços e aspeto). Fica guardado 90 dias depois do último acesso, sem nada sobre quem o partilha; a Política de privacidade foi atualizada.

## 3.74.0 — 2026-11-20

### Novo
- **Dois tamanhos no preçário**: ligue «Dois tamanhos (dois preços por artigo)» (site e app Windows) para escrever dois preços em cada artigo (por exemplo, o pequeno e o grande, ou o artigo e o menu). As duas colunas saem alinhadas, com os nomes que escolher por cima (por omissão «Pequeno» e «Grande»), e ficam guardadas no ficheiro do preçário.

## 3.73.0 — 2026-11-20

### Novo
- **Cartões de mesa**: no formato do preçário escolha «Cartões de mesa (4 por folha A4)» (site e app Windows) e o preçário sai em cartões A6, quatro numa folha A4 com guias de corte a tracejado, prontos a imprimir e cortar para pôr nas mesas (até 12 artigos).

## 3.72.0 — 2026-11-20

### Novo
- **Preçário em «quadro negro»**: um novo desenho na lista «Ocasião e tema» (e na app Windows): fundo verde-escuro de quadro de escola, moldura de madeira e texto a giz (branco e amarelo), ideal para a tasquinha, a esplanada ou a sala de aula.

## 3.71.0 — 2026-11-20

### Novo
- **Vales de fichas numerados** (no preçário, com uma moeda inventada; e «Extras → Preçário… → Vales numerados…» na app Windows): escolha quantas fichas vale cada vale, o título e uma nota, veja o vale com o desenho do preçário e crie-os. Continua no gerador de rifas, que numera os vales com séries, QR de verificação e folhas prontas a imprimir.

## 3.70.0 — 2026-11-20

### Novo
- **Gerador de preçários para festas** (`/precario`, e «Extras → Preçário…» na app Windows): escolha a ocasião (a da época vem sugerida) e os artigos de um catálogo com imagens, escreva os preços na moeda do seu país ou numa moeda inventada (fichas…) e descarregue o PDF (ou uma imagem) pronto a imprimir, em A5, A4 ou A3 e com os 24 desenhos da galeria. Há também um guia novo: «Como fazer o preçário de uma festa».

## 3.69.0 — 2026-11-19

### Novo
- **Português do Brasil** (`/pt-br`): o site, os guias e as páginas legais passam a existir também em português do Brasil, com o vocabulário de lá (arquivo, baixar, tela, link…), a Política de privacidade adaptada à LGPD e a língua escolhida sozinha quando o navegador está em pt-BR. O português de Portugal continua o mesmo, sem prefixo no endereço.

## 3.68.0 — 2026-11-19

### Novo
- **Três guias novos, por tema** (não por público): como numerar os bilhetes de uma rifa, como fazer um sorteio verificável (liga à página «Sorteio») e quantos bilhetes fazer e a que preço. Estão em «Todos os guias» (`/como-fazer`), nas 22 línguas.

## 3.67.0 — 2026-11-19

### Novo
- **Índice dos guias «Como fazer»** (`/como-fazer`): uma página que lista todos os guias com um resumo de cada, e cada guia passa a terminar com ligações para os outros. Também está no menu «Ajuda» («Todos os guias»).
- Os guias e o índice indicam ao Google o caminho em que estão (Início › Como fazer › guia), para o mostrar nos resultados da pesquisa.

## 3.66.0 — 2026-11-19

### Novo
- **Convite para deixar um comentário:** depois de descarregar as rifas, aparece (uma só vez por aparelho) um aviso discreto a convidar a deixar um comentário, anónimo se quiser. Pode dispensá-lo com «Agora não».

## 3.65.0 — 2026-11-19

### Melhorado
- **Site mais leve e mais seguro:** quem só gera rifas descarrega menos 24 % de código (o painel de administração, o editor de templates e o sorteio só se carregam quando se abre a página). O site passou também a enviar cabeçalhos de segurança e a responder a verificadores de ligações e a pré-visualizações de partilha.

## 3.64.0 — 2026-11-19

### Novo
- **Cópia de segurança semanal dos dados do painel de administração:** todas as segundas-feiras o serviço grava, no armazenamento do mesmo fornecedor da base de dados, uma cópia do histórico, dos objetivos, do registo de ações, dos comentários e dos textos de SEO (últimas 8 semanas), com um script para restaurar.

## 3.63.0 — 2026-11-19

### Novo
- **Desempenho real do site nas estatísticas:** o painel de administração mostra, por dia, quanto demora a página a aparecer, quanto o conteúdo se mexe e quanto demora a responder a um clique, medido nos browsers dos visitantes (telemóvel e computador). São só três números anónimos por visita; a Política de privacidade foi atualizada.

## 3.62.0 — 2026-11-19

### Novo
- **Origem das visitas nas estatísticas:** o painel de administração passa a mostrar de onde vêm as visitas, em categorias gerais (pesquisa, redes sociais, e-mail, outros sites ou diretas) e por campanha (utm_source), para medir uma divulgação. Nunca se guarda o endereço da página de origem nem o IP; a Política de privacidade foi atualizada.

## 3.61.0 — 2026-11-19

### Novo
- **Registo de ações no painel de administração:** fica guardado (400 dias) quem fez o quê e quando no painel (entradas, comentários apagados ou escondidos, chaves da API, textos de SEO, objetivos), sem dados de visitantes nem palavras-passe.

## 3.60.0 — 2026-11-19

### Novo
- **Objetivos diários no painel de administração:** o responsável define uma meta por dia (sessões, gerações, números gerados, descargas…) e vê se o último dia a cumpriu, a média dos últimos 7 dias e em quantos deles foi atingida; o relatório diário por e-mail leva a mesma secção.

## 3.59.0 — 2026-11-19

### Novo
- **Comentários com estado no painel de administração:** o responsável pode marcar cada comentário como lido, favorito ou escondido (um comentário escondido deixa de aparecer na página pública, mas não se perde), filtrar por estado e ver quantos há por ler.

## 3.58.0 — 2026-11-19

### Novo
- **Quotas do alojamento gratuito no painel de administração:** vê-se quantas das 750 horas mensais do Render o serviço já gastou (com a projeção até ao fim do mês) e quanto espaço a base de dados ocupa no plano grátis do Neon, com aviso por e-mail no relatório diário antes de as quotas acabarem.

## 3.57.0 — 2026-11-19

### Novo
- **Marcas de versão nos gráficos do painel de administração:** cada gráfico diário assinala o dia em que chegou uma versão nova da app (e o relatório diário diz qual), para ligar uma subida de erros ou de tempo de resposta à atualização que a causou.

## 3.56.0 — 2026-11-19

### Novo
- **Resumo semanal e mensal por e-mail para o responsável do site:** às segundas-feiras chega o resumo da semana e no dia 1 o do mês, com os totais comparados com o período anterior e uma miniatura de cada dia. Lêem do histórico permanente. Só contagens.

## 3.55.0 — 2026-11-19

### Novo
- **Alertas imediatos por e-mail para o responsável do site:** se houver uma sequência de erros do servidor, reinícios do motor, memória perto do limite ou a base de dados sem resposta, chega logo um aviso (sem esperar pelo relatório diário e sem repetir durante 6 horas). Só contagens.

## 3.54.0 — 2026-11-19

### Novo
- **Histórico permanente no painel de administração:** depois da meia-noite grava-se um resumo de cada dia, por isso a «Evolução diária» passa a mostrar meses e até 2 anos (antes só 90 dias). Só contagens, como o resto do painel.

## 3.53.0 — 2026-11-19

### Novo
- **Relatório diário por e-mail para o responsável do site:** todos os dias, logo depois da meia-noite, chega um e-mail com tudo o que se gravou no dia que acabou (utilização, público, erros e recursos do servidor), comparado com a média dos 7 dias anteriores, para acompanhar a app sem abrir o painel. Só contagens: nunca dados dos visitantes.

## 3.52.0 — 2026-11-19

### Melhorado
- **Comentários sem endereço IP:** em vez do IP, passa a guardar-se apenas o país de onde o comentário foi enviado (só o responsável do site o vê). O endereço IP já não se guarda: os dos comentários anteriores foram apagados, e a Política de privacidade foi atualizada.

## 3.51.0 — 2026-11-19

### Novo
- **Comentários:** há uma página «Comentários» onde toda a gente vê o que as outras pessoas acham do gerador, e uma página para deixar o seu: pode ficar anónimo(a) ou mostrar um nome (sem nome, aparece «Visitante n.º …»). O endereço IP fica guardado só para o responsável do site, para travar abusos, nunca é mostrado e apaga-se ao fim de 90 dias.
- **Reportar problema:** nova página onde descreve um erro e, ao carregar em «Abrir», ele é criado diretamente no GitHub do projeto, sem precisar de conta (o seu IP não é enviado e a informação técnica do navegador só vai se a juntar).
- As duas páginas e os botões «Comentários» e «Reportar problema» estão à vista no cabeçalho, no menu e no rodapé; a Política de privacidade (22 línguas) explica o que se guarda.

## 3.50.0 — 2026-11-18

### Melhorado
- **Cabeçalho que se adapta ao ecrã:** as opções ficam todas encostadas à direita, numa só fileira e sem buracos, e à medida que o ecrã diminui vão passando, uma a uma, para um menu «hambúrguer» (primeiro o modo claro/escuro e o visual, por fim o donativo). Em telemóveis fica só o nome da aplicação e o botão do menu, que abre com as páginas, a ajuda, o partilhar e as definições.

## 3.49.0 — 2026-11-18

### Novo
- **Painel com a evolução dia a dia:** uma nova vista «Evolução diária» mostra, ao longo de até 90 dias, tudo o que o servidor guarda na base de dados (sessões, gerações, números gerados, línguas, países, visuais, galeria, editor, API, pedidos, tempos de resposta, CPU e memória…), com a tendência de cada indicador e a possibilidade de descarregar tudo em CSV. É uma funcionalidade do painel do dono: os visitantes não notam diferença.

## 3.48.0 — 2026-11-18

### Melhorado
- **Menu «Ajuda» no cabeçalho:** o tutorial, o vídeo e os guias «Como fazer» passaram para um só separador, «Ajuda». O cabeçalho fica mais curto e o nome da aplicação aparece sempre inteiro e numa só linha, em qualquer língua e tamanho de ecrã (antes podia ficar cortado ou partido em duas linhas).

## 3.47.0 — 2026-11-15

### Melhorado
- **Galeria de templates:** a lista dos desenhos já não fica cortada nem fora do sítio nalguns temas; cada prémio tem o seu número; todas as caixas de texto mostram o limite de caracteres (por exemplo 12/50); e o botão «Usar este template» já não fica colado à última caixa.
- **Data do sorteio num calendário próprio:** em vez do campo do browser (que mostrava «dd/mm/aaaa» e o seletor numa língua diferente da do site), há um calendário nas 22 línguas, com os meses e os dias da semana na língua escolhida, a data escrita como essa língua a escreve, o primeiro dia da semana certo e os botões «Hoje» e «Limpar». Funciona com o teclado (setas, Page Up/Down, Home/End, Enter e Esc).
- **«Acerca de» mais completo:** o texto foi reescrito, nas 22 línguas, e explica para quem é o gerador, o que faz, o que fazer depois de imprimir, como protege a privacidade e onde se pode usar.

## 3.46.0 — 2026-11-15

### Melhorado
- **Donativo mais à vista:** quando o serviço tem uma ligação de donativo, o botão aparece agora no cabeçalho (ao lado de «Partilhar») e, depois de gerar os ficheiros, com uma frase a convidar. Continua também no rodapé.

## 3.45.0 — 2026-11-14

### Melhorado
- **Galeria de templates numa só linha:** os 24 desenhos escolhem-se agora numa caixa de uma linha em que cada opção mostra um mini desenho do template, em vez de uma lista comprida de botões. Funciona com o rato, o toque e o teclado (setas, Home/End, uma letra, Enter e Esc).

## 3.44.0 — 2026-11-14

### Melhorado
- **Privacidade:** as contagens de utilização passam a incluir o país da visita (só o código, deduzido pela rede do alojamento; o endereço IP continua a não ser guardado). A Política de privacidade explica-o nas 22 línguas.

## 3.43.1 — 2026-11-14

### Melhorado
- **Rodapé mais limpo:** os guias «Como fazer» já só aparecem no grupo do cabeçalho; deixaram de se repetir no fundo da página.

## 3.43.0 — 2026-11-14

### Melhorado
- **Data do sorteio num calendário:** na galeria de templates escolhe-se a data num calendário e depois como aparece na rifa (31/12/2026, 31 de dez. de 2026, 31 de dezembro de 2026 ou com o dia da semana), escrita na língua do site. Também se pode escrever à mão, agora até 60 letras.
- **Textos mais largos:** as páginas de texto (guias, tutorial, termos…) passam a ocupar a largura da página, com menos linhas e menos parágrafos.

## 3.42.0 — 2026-11-14

### Melhorado
- **Cabeçalho:** o novo grupo «Como fazer», ao lado do tutorial, reúne os guias (escolas, associações, clubes, bombeiros, festas de bairro e paróquias). O botão «Partilhar» passou do rodapé para o cabeçalho, em destaque, e a lista mostra os ícones do WhatsApp, Telegram, Facebook, e-mail e «Copiar ligação».

## 3.41.0 — 2026-11-14

### Melhorado
- **Pré-visualização automática:** quando muda o template, os algarismos, o logótipo ou qualquer campo que altera a página final (números, algarismos, folha, séries, cores, QR…), a pré-visualização com números reais refaz-se sozinha, sem carregar em «Pré-visualizar». Se algo estiver errado, o motivo aparece junto ao visor, sem janelas.

## 3.40.0 — 2026-11-14

### Novo
- **De 3 a 10 prémios na galeria:** nos 24 desenhos da galeria de templates escolhe-se quantos prémios a rifa tem (3 a 10; antes eram no máximo 3). A partir de 6 passam a duas colunas, sem apertar o número nem a data. Também na app Windows.

## 3.39.0 — 2026-11-13

### Novo
- **App Windows 2.7:** a galeria e o editor de templates passam a aceitar latim estendido, vietnamita, grego, cirílico, chinês, japonês e coreano, como o site desde a 3.37 (o hindi, o árabe e o hebraico continuam por fazer). Descarrega-se na página do Changelog.

## 3.38.0 — 2026-11-13

### Novo
- **Botão «Partilhar»:** no rodapé e, depois de gerar os ficheiros, no cartão da entrega. Abre uma lista curta (a partilha do telemóvel ou do computador, WhatsApp, Telegram, Facebook, e-mail e «Copiar ligação») para dar a conhecer o gerador a outras associações, escolas e comissões de festas. As ligações levam só o endereço do site na língua em que está: sem rastreio e sem guardar nada. Tem tópico no tutorial e vídeo.

## 3.37.0 — 2026-11-13

### Novo
- **Mais letras na galeria e no editor de templates:** os textos podem agora ter latim estendido (polaco, checo, romeno, turco…), **vietnamita, grego, cirílico (russo, ucraniano)**, **chinês, japonês e coreano**. O hindi, o árabe e o hebraico continuam por fazer (precisam de uma tecnologia de escrita que o gerador de PDF não tem) e dão um aviso em vez de uma imagem estragada. Nos PDF só muda o texto escrito por quem usa; o que já saía igual continua igual.

## 3.36.0 — 2026-11-13

### Novo
- **Guia «Como fazer» para paróquias:** «Para paróquias» (ligação no rodapé), com o passo a passo para fazer uma rifa para a paróquia: festas do padroeiro, quermesses, obras, cabazes de Natal e catequese. Está nas 22 línguas e lembra de confirmar na câmara municipal se a rifa precisa de licença.

## 3.35.0 — 2026-11-13

### Novo
- **App Windows 2.6:** o menu «Extras» ganha «Guardar pedido…» e «Abrir pedido…» (um ficheiro .rifas com os números, o nome, as séries, as cores e as marcas de corte, sem template nem caminhos), o editor de templates passa a juntar imagens (PNG ou JPG) e «Ver → Visual» passa de 2 para os 14 temas do site (só as cores). Junta ainda o que veio desde a 2.4: o editor, os 24 desenhos da galeria e as 22 línguas.

## 3.34.0 — 2026-11-13

### Novo
- **Três guias «Como fazer» novos:** «Para clubes», «Para bombeiros» e «Para festas de bairro» (ligações no rodapé), com o passo a passo para fazer uma rifa em cada caso. Estão nas 22 línguas e lembram de confirmar na câmara municipal se a rifa precisa de licença.

## 3.33.0 — 2026-11-13

### Novo
- **API pública em lote** (`/api/v1`, com Swagger em `/api/v1/docs`): permite a outros programas gerar vários pedidos de rifas a partir de um só template, com chave, quotas diárias e limites. Quem usa o site passa sempre à frente.
- **Quatro línguas novas:** catalão, ucraniano, indonésio e vietnamita. O site e a app Windows passam a ter 22 línguas, com tutorial, termos, privacidade, guias «como fazer» e capturas.
- **Textos para os motores de pesquisa editáveis por língua:** o dono edita no painel de administração os títulos, as descrições e os guias de cada língua, guardados na base de dados e sem novo deploy.

## 3.32.0 — 2026-11-13

### Novo
- **20 templates novos na galeria (24 no total):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Todos desenhados de raiz neste projeto, com talão, no site e na app Windows (onde a galeria passa a ser uma lista suspensa).

## 3.31.0 — 2026-11-13

### Novo
- **Editor de templates v2:** desfazer e refazer (Ctrl+Z, Ctrl+Y), duplicar (Ctrl+D), mudar a ordem de desenho, juntar o logótipo (PNG ou JPG) e **partilhar o desenho por uma ligação**: fica guardado 90 dias depois do último acesso, sem imagens e sem dados de quem partilha (só aparece quando o serviço tem base de dados). A Política de privacidade passa a dizê-lo.
- **App Windows 2.5:** ganha o editor de templates (menu Extras) e passa a Python 3.15.

### Melhorado
- O Changelog tem uma ligação para descarregar a app Windows.

## 3.30.0 — 2026-11-12

### Novo
- **Páginas «Como fazer»:** dois guias escritos, «Para escolas» e «Para associações» (ligações no rodapé), com o passo a passo para fazer uma rifa: desenhar o bilhete, uma série por turma ou vendedor, imprimir com marcas de corte, controlar as vendas e fazer um sorteio verificável. Estão nas 18 línguas e lembram de confirmar na câmara municipal se a rifa precisa de licença.

## 3.29.0 — 2026-11-12

### Melhorado
- **Anúncios nas laterais:** quando os anúncios estão ligados (por agora não estão), em ecrãs largos aparecem nas duas laterais do conteúdo, um de cada lado, fixos e sem mexer na página; nos outros ecrãs fica um só bloco no fim da página. Continuam a não aparecer no editor, nos ficheiros gerados nem na app Windows.

## 3.28.0 — 2026-11-12

### Novo
- **Anúncios da Google (preparados, desligados):** o site pode mostrar um bloco de anúncios da Google (AdSense) no fim da página inicial, do tutorial, do «Acerca de», do sorteio e do changelog. Nunca aparecem no editor, nos ficheiros gerados, na verificação de bilhetes, no painel nem na app Windows, e no Espaço Económico Europeu e no Reino Unido só depois de escolher na mensagem de consentimento da Google. A Política de privacidade passa a dizê-lo, nas 18 línguas, quando os anúncios estão ligados; por agora estão desligados, até o dono do serviço os configurar.

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
