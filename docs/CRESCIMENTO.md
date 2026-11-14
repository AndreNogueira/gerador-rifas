# Como o site chega a mais pessoas, sem pagar nada

**Ideia central:** as pessoas que precisam disto procuram «rifas numeradas», «template de rifa Canva», «talão de rifa» ou perguntam num grupo («alguém sabe numerar rifas?»). O produto já resolve isso em 22 línguas, de graça e sem registo. O que falta é **estar nos sítios onde elas perguntam** e **deixar que cada rifa impressa faça publicidade**. Tudo abaixo é gratuito; está por ordem de retorno por hora de trabalho.

## O que o site já faz por ti (não repetir)
Um URL por língua com `hreflang`, sitemap (16 páginas × 22 línguas), Open Graph com imagem, JSON-LD, 6 guias «Como fazer» (escolas, associações, clubes, bombeiros, festas, paróquias), instalável como app, vídeos por funcionalidade, e a verificação do Google Search Console. Ver `docs/SEO.md`.

## Semana 1: ser encontrado (≈ 2 h, uma vez)
1. **Search Console**: enviar o `sitemap.xml` e pedir a indexação (*Inspeção de URL → Pedir indexação*) da página inicial e dos 6 guias em português. Importar o site no **Bing Webmaster Tools** (um clique, a partir da Search Console): o Bing alimenta também o DuckDuckGo e o Copilot.
2. **YouTube (grátis, e a 2.ª maior pesquisa do mundo):** os vídeos de `app/assets/video/` (`web_*_pt.mp4`, ≈ 100–450 KB) são tutoriais curtos prontos. Carregar 4 ou 5 com títulos que as pessoas pesquisam («Como numerar rifas no Canva», «Rifas numeradas em PDF em 2 minutos», «Séries por equipa», «Sorteio verificável») e a ligação do site na 1.ª linha da descrição. Os mesmos ficheiros servem para *Shorts*, Instagram *Reels* e TikTok.
3. **Pinterest (grátis, procura de «modelos»):** os 24 desenhos da galeria dão 24 imagens de bilhetes. Um quadro «Modelos de rifa para imprimir» com um *pin* por desenho, ligado ao guia certo (`/rifas-para-clubes`, `-festas`…). É dos canais que mais trazem tráfego a quem vende templates.
4. **LinkedIn:** um *post* de lançamento (o Google Business não serve: não é um negócio local).

## Semanas 2–4: ir ter com quem pergunta (≈ 1 h por semana)
Responder (sem *spam*: ajudar primeiro, ligação no fim, e só onde é permitido) a perguntas sobre rifas:
- **Grupos de Facebook** de pais e encarregados de educação, associações de pais, **comissões de festas**, bombeiros voluntários, escuteiros, clubes de bairro, «Associativismo em Portugal», paróquias e grupos do **Canva** em português. Procurar por «rifas», «bilhetes numerados», «sorteio angariação».
- **Reddit** (`r/portugal` para perguntas gerais; `r/canva`, `r/nonprofit`, `r/Teachers` e `r/volunteer`, em inglês, onde as outras línguas contam), **Quora** e fóruns de professores.
- **Comunidade do Canva** (a pergunta «como numerar vários bilhetes» aparece todos os meses). O site é feito precisamente para esse template.
- **Entidades que aconselham associações** (e-mail curto, ver texto abaixo): serviços de **associativismo das câmaras municipais**, **juntas de freguesia**, a **CPCCRD** (Confederação Portuguesa das Coletividades de Cultura, Recreio e Desporto), federações de associações de pais (**CONFAP**), **Liga dos Bombeiros Portugueses**, **CNIS** e uniões de IPSS, as **misericórdias**, dioceses (boletins). Pedir apenas que **divulguem a ligação** aos associados; nenhuma pede dinheiro por isso.
- **Escolas e agrupamentos**: uma mensagem ao diretor/coordenador de associação de pais antes do Natal e do fim de ano letivo (as épocas das rifas).

## Que cada rifa impressa traga novos utilizadores (sem custo, a longo prazo)
Um pacote de bilhetes passa pelas mãos de centenas de compradores. Hoje o bilhete **não diz** de onde veio. Três formas de o dizer, da menos para a mais intrusiva (cada uma custa só desenvolvimento, e nunca é obrigatória):
1. **Ligação na página de verificação do QR** (`/v/…`): quem lê o QR vê «Feito com o Gerador de Rifas: faça as suas, grátis». É a mais discreta; precisa do QR (`VERIFICACAO_CHAVE`).
2. **Assinatura opcional no bilhete** (uma caixa «mostrar o endereço do gerador no rodapé do bilhete», desligada por omissão): uma linha pequena com o endereço, numa margem. As associações que gostam do serviço costumam deixá-la ligada.
3. **Botão «Partilhar»** no fim da geração e no rodapé (partilha nativa do telemóvel, WhatsApp, Telegram, Facebook, e-mail e copiar ligação): é onde as comissões de festas e as associações de pais falam entre si. **Feito** (3.38.0, `Partilhar.tsx`).

Regra a manter: **nada de rastreio** (a política de privacidade diz «quase nenhum dado»); os botões são ligações simples, sem *scripts* de terceiros.

## O que medir (já tens o painel)
- **Visitantes novos por semana** e **gerações concluídas** (`/admin` → Utilização e o funil); o que conta é *gerações*, não visitas.
- **Origem:** o Search Console diz as pesquisas e as páginas; as ligações de entrada dizem onde a divulgação funcionou. Para saber que *post* trouxe quem, usa ligações com etiqueta (`/?utm_source=facebook`): o servidor ignora o que não conhece e não guarda a ligação.
- **Línguas:** as visitas por língua (painel → Utilização) mostram onde investir um guia novo.

## Textos prontos (português)

**Mensagem curta para grupos:**
> Se andam a fazer rifas para a escola, a associação ou a festa e perdem tempo a numerar bilhetes à mão: este site faz os bilhetes numerados em PDF (com talão, séries por equipa/vendedor, marcas de corte, lista e folha de controlo e sorteio verificável). É grátis, sem registo e não guarda os ficheiros. Também tem modelos prontos. https://gerador-rifas.onrender.com

**E-mail para entidades (câmaras, federações, juntas):**
> Assunto: Ferramenta gratuita para numerar rifas de associações e escolas
> Bom dia. Criámos uma ferramenta gratuita e sem registo que gera bilhetes de rifa numerados em PDF (a partir de um template do Canva ou de um dos 24 modelos prontos), com séries por vendedor, lista de bilhetes e sorteio verificável. Já tem guias para escolas, associações, clubes, bombeiros, festas e paróquias: https://gerador-rifas.onrender.com. Se achar útil, agradecíamos que a divulgasse junto das associações que apoiam. Obrigado!

(Rever o endereço público e a assinatura antes de enviar. Lembrar a quem lê que as regras de licença de uma rifa dependem da câmara municipal: os guias já o dizem no 1.º passo.)

## Ordem de execução sugerida
1. **Esta semana:** Search Console + sitemap, 3 vídeos no YouTube, quadro no Pinterest. (≈ 2 h)
2. **Semanas 2–4:** 5 respostas úteis por semana em grupos; 10 e-mails a câmaras e federações. (≈ 1 h/semana)
3. **Em paralelo, no código:** o botão «Partilhar» está feito (3.38.0); faltam a ligação na página do QR e a assinatura opcional (1 PR cada). Cada um precisa das 22 traduções e do tópico no tutorial (`CLAUDE.md`).
4. **Todos os meses:** um guia novo (misericórdias, IPSS, juntas de freguesia, escuteiros, associações de pais) e olhar o painel para ver o que funcionou.
