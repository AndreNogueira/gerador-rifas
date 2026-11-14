# Gerador de Rifas (app para Windows)

Programa com interface gráfica que pega num **template em PDF** (exportado do Canva), apaga os números de exemplo
(0001, 0002, …) e escreve os números que quiser, uma página de cada vez. O template pode ter **vários bilhetes por
página** (5, 12, …) ou **uma só rifa**: nesse caso o programa enche a folha (A4, A3, …) com cópias, o máximo que
couber. Gera vários PDFs ou **um único PDF com tudo**.

**Executável:** `dist\GeradorRifas.exe` (compilado para código nativo; não precisa de instalar nada).
**Antes de cada release:** `uv run python scripts/verificar_repo_publico.py` confirma que o repositório público só tem o `README.md` e releases com o `.exe` (sem código-fonte).
**Descarregar:** na página de *Releases* do repositório público <https://github.com/AndreNogueira/gerador-rifas-windows>
(só tem o programa, **sem código-fonte**; etiquetas `windows-vX.Y.Z`), junto com o `.sha256` para conferir o ficheiro. A versão atual é a 2.6.0: **guardar e abrir o pedido** (ficheiro `.rifas`), **imagens no editor de templates** e os **14 visuais** do site (só as cores); a 2.5.0 trouxe o **editor de templates** (menu Extras), a galeria de 24 desenhos, 22 línguas e Python 3.15; a 2.4.0 trouxe o que o site ganhou desde a 3.10 (menu **Extras**, abaixo); a 2.3.0 trouxe o visual novo (faixa com o gradiente violeta → magenta e o ícone da
marca, passos numerados com cores próprias, botão «Gerar» em magenta), as mesmas cores da webapp.

## Extras (v2.4)

O menu **Extras** abre janelas à parte (a janela principal e as capturas do tutorial ficam como estavam); tudo vale só para a sessão e «Limpar tudo» repõe-no:

- **Séries, cor e logótipo…**: prefixos (`A-, B-, C-`: cada série tem os seus PDFs), números a saltar (`13, 100-110`), uma cor para cada série, a **cor dos números**, o **logótipo** da associação
  (PNG ou JPG até 2 MB, num canto de cada rifa, só em templates de uma rifa) e as **marcas de corte** nas margens da folha (margem de pelo menos 3 mm).
- **Galeria de templates…**: quatro desenhos prontos (Bosque, Quermesse, Natal, Gala) com título, organização, prémios e data; «Usar este template» cria o template e os algarismos.
- **Sorteio…**: sorteio verificável (a mesma resposta que a página do site) com semente pública; há um botão para a aleatoriedade do drand (precisa de internet).
- **Exportar lista (CSV)** e **Folha de controlo (PDF)**: a lista dos bilhetes do pedido (com prefixos e saltos) para o Excel, e uma tabela A4 para marcar quem pagou. Não precisam de template.
- **Editor de templates…**: desenha-se a rifa (textos, retângulos, linhas, o número 0001 e **imagens** PNG ou JPG) com o rato e o teclado; desfazer/refazer (Ctrl+Z, Ctrl+Y), duplicar (Ctrl+D), ordem de desenho; «Usar este template» cria o template e os algarismos.
- **Guardar pedido…** e **Abrir pedido…**: um ficheiro `.rifas` com os números, o modo, o papel, a margem, o nome dos ficheiros, as séries, os números a saltar, as cores, as marcas de corte e o canto/tamanho do logótipo. Nunca leva o template, os algarismos, a pasta de destino nem o logótipo (são caminhos do seu computador). É o equivalente do «Copiar ligação» do site.
- **Ver → Visual**: Automático (o **Natal** em dezembro) ou um dos **14 visuais** do site (Premiado, Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala, Matrix Gamer, Natal, Halloween, Praia, Jornal antigo, Terminal verde, Cartaz de circo): só mudam as cores (a faixa, as letras e os fundos do site não passam para o Tk); claro e escuro são independentes.

O **QR de verificação**, a partilha do desenho do editor por ligação e o instalar como app só existem no site (o QR é assinado com uma chave do servidor, que não pode estar num `.exe` público; a partilha do desenho precisa da base de dados do servidor).
Cada funcionalidade tem o seu tópico no tutorial (F1) com um vídeo gravado da própria app.

## Como usar

1. **Template (PDF)** – o PDF exportado do Canva com `0001`, `0002`, … em cada bilhete (cada número 2 vezes: talão +
   parte principal). O programa deteta sozinho quantos bilhetes há por página (testado de 2 a 24) e a orientação do
   texto do talão (a subir, a descer, na horizontal ou invertido). O número de algarismos dos exemplos
   (0001 → 4) passa a ser o valor por defeito do passo 3. **O campo começa sempre vazio**: o template não é
   preenchido sozinho nem guardado entre sessões (cada rifa tem o seu). **Se o template só tiver uma rifa**, aparecem
   o papel, a margem e as rifas por folha (ver «Uma só rifa no template»).
2. **Algarismos 0–9 (obrigatório)** – um ficheiro com os dez algarismos **na mesma letra** dos números do template
   (ver abaixo). O programa não procura letras no computador.
3. **Números** – `De` / `Até`, quantos algarismos, e *Vários PDFs* (máximo por ficheiro, múltiplo dos bilhetes por
   página) ou *Um único PDF*.
4. **Destino** – pasta e **nome dos ficheiros (escrito por si; começa vazio e é obrigatório)**. Os ficheiros ficam
   `NOME - 0001 - 0300.pdf`, …

**Pré-visualizar** mostra a 1.ª página com números verdadeiros. O visor tem **zoom** (botões − / +, Ctrl + roda do rato,
duplo clique ou *Ajustar* para ajustar), **deslocamento** (arrastar ou roda) e **expandir** (esconde as definições e
dá toda a janela à pré-visualização; clicar outra vez volta ao normal). A **divisória** entre as definições e o visor
também se arrasta (mostra uma linha fina e aplica a largura ao largar).

No fim, cada PDF é **verificado automaticamente** (nº de páginas e números de cada página). Quando a geração acaba
aparecem **Abrir pasta** e **Limpar tudo** (também em Ficheiro › Limpar tudo): volta ao estado de um arranque novo — sem
template, algarismos, pasta nem nome, números por defeito, pré-visualização, progresso e registo vazios (a língua, o tema e
o papel/margem das folhas mantêm-se). `testes	este_limpar.py` confere-o.

## Uma só rifa no template (o programa enche a folha)

Não é preciso desenhar a folha toda: no Canva basta uma página com o tamanho da rifa («Tamanho personalizado»,
p. ex. 19 × 5,5 cm) com **um** número de exemplo, `0001` (no talão e na parte principal, ou só num sítio). Ao escolher
esse PDF o programa vê que há uma só rifa e mostra **Papel** (A4, A3, A5, Letter, Legal), **Margem (mm)** e **Rifas por
folha**:

- enche a folha com cópias da rifa, **o máximo que couber** (testa a folha em altura e em largura e a rifa a 0° e a 90°,
  e até misturar as duas orientações), centradas, e numera-as por ordem; só se desenham as rifas que têm número (na
  última folha podem ficar espaços vazios);
- a pré-visualização mostra a folha tal como vai sair; «Rifas por folha» começa no máximo e pode pedir menos;
- se a página do PDF for maior do que a rifa, usa o **TrimBox** do PDF (se houver) ou recorta a **zona desenhada**
  (indicado no resumo, «recortada ao desenho»);
- **avisos:** se a rifa não cabe na folha dá erro com as medidas; se cabem **mais de 24** rifas por folha
  (`core.AVISO_POR_PAGINA`) avisa no ecrã e no registo e pede confirmação antes de gerar (ficam pequenas e difíceis de
  recortar); se pedir mais do que o máximo usa o máximo e diz qual é;
- o máximo por ficheiro («Vários PDFs») tem de ser múltiplo das rifas por folha, como antes.

Um template com **vários bilhetes por página** (0001, 0002, … cada número 2 vezes) funciona exatamente como antes.

## Menus e tutorial

Barra de menus própria (segue o tema claro/escuro):

| Menu | Opções |
|---|---|
| **Ficheiro** | Abrir template (Ctrl+O) · Escolher ficheiro dos algarismos · Escolher pasta de destino (Ctrl+L) · Pré-visualizar (Ctrl+P) · Gerar / Cancelar (Ctrl+G, F5) · Abrir pasta dos PDFs · **Limpar tudo** · Sair |
| **Ver** | Aumentar / diminuir zoom (Ctrl+ + / −) · Ajustar à janela (Ctrl+0) · Expandir / reduzir a pré-visualização (F11) · Tema: igual ao Windows / claro / escuro |
| **Idioma** | as 18 línguas (o seletor 🌐 do canto também fica à mão) |
| **Ajuda** | **Tutorial passo a passo** (F1) · **Vídeo tutorial** · Como criar o ficheiro dos algarismos · Acerca de |

O **tutorial** (F1) tem 8 páginas — visão geral, os 4 passos, «uma só rifa no template», pré-visualizar/gerar e dicas —
com imagens: um template de exemplo **inventado** («Rifa de Exemplo», para ficar claro que não é de ninguém) com os
números realçados, os algarismos e **capturas da própria janela na língua escolhida**. As imagens estão em
`assets\ajuda\` e refazem-se com `python testes\fazer_ajuda.py` (abre a janela real, em 18 línguas, e fotografa-a; só
as capturas do passo «uma só rifa»: `python testes\fazer_ajuda.py c`).

O **vídeo tutorial** (Ajuda › Vídeo tutorial; ~1,5 min, sem som, com legendas) mostra os 4 passos, pré-visualizar,
gerar e o modo «uma só rifa». Está em `assets\video\tutorial_pt.mp4` e `tutorial_en.mp4` (a app abre o da língua
escolhida, ou o inglês/português se não houver). Foi gravado com a própria app por `testes\fazer_video.py` (comanda a
janela real, fotografa-a e compõe o painel dos passos, as legendas e um cursor animado; precisa de um `ffmpeg` só para
gravar: variável `FFMPEG` ou `imageio-ffmpeg`; o ffmpeg não vai na app). Refaça-o sempre que a interface mudar:
`python testes\fazer_video.py pt en`.

Os ficheiros de exemplo (`exemplos\`) são todos inventados e gerados por `testes\fazer_exemplos.py`: o template de
5 rifas, o de uma rifa (página do tamanho da rifa), o de uma rifa no meio de uma A4 e os algarismos (letra Vera, livre).

## Línguas e tema

18 línguas, à escolha no cabeçalho (🌐): Português, English, Español, Français, Deutsch, Italiano, Nederlands, Polski,
Svenska, Čeština, Română, Ελληνικά, Русский, Türkçe, 简体中文, 日本語, 한국어, हिन्दी. No 1.º arranque usa a língua do
Windows (ou inglês). As escolhas (língua, tema, ficheiro dos algarismos, pasta, números) ficam em
`%APPDATA%\GeradorRifas\config.json`; **o template e o nome dos ficheiros nunca são guardados**.
Para acrescentar uma língua: copiar `..\src\core\idiomas\pt.py` e `ui_pt.py` para `<codigo>.py` e `ui_<codigo>.py`,
traduzir e juntar o código em `..\src\core\idiomas\__init__.py`; depois `python testes\fazer_ajuda.py` para as capturas do tutorial.

## Cores

- **Por defeito** a app usa as cores da marca («Premiado»: violeta `#6A35F5` e magenta `#D62B8F`), em claro e escuro,
  iguais às da webapp (`tema.py`).
- **Cor de destaque do Windows**: com a variável de ambiente `RIFAS_COR_DESTAQUE=windows` os botões, números dos passos,
  barra de progresso e seleção dos menus seguem as Definições do Windows (Personalização › Cores); com
  `RIFAS_COR_DESTAQUE=#RRGGBB` usam essa cor. Se a mudar com o programa aberto, a janela adapta-se em ~2 s.
- O ícone (`assets\icon.ico`/`icon.png`) sai do desenho da webapp: `python make_icon.py`.
- **Tema** (menu Ver › Tema): *Igual ao Windows* (por defeito, segue o modo claro/escuro do Windows em tempo real),
  *Claro* ou *Escuro*. O botão ☾/☀ no canto alterna.
- Os ícones são desenhados com sobre-amostragem (bordos suaves, sem pixeis) e mudam de cor com o tema.

## O ficheiro dos algarismos 0–9

O PDF do Canva só traz as letras que usa (por exemplo 0–5), por isso é preciso fornecer os dez algarismos:

| Ficheiro | Como criar | Resultado |
|---|---|---|
| **PDF** *(recomendado)* | No Canva escreva `0123456789` com a **mesma letra** dos números e descarregue em PDF | vetorial, idêntico ao original |
| **PNG / JPG** | Só `0 1 2 3 4 5 6 7 8 9` numa linha, esquerda→direita, com um espaço visível entre algarismos, mesma letra do template; ≥ 100 px de altura | imagem de alta resolução |

- Com PDF a letra é **copiada do próprio PDF** (funciona mesmo com as letras reduzidas do Canva).
- Nas imagens a cor não interessa (usa a do template) e o fundo pode ser transparente ou liso.
- Se o PDF não tiver texto utilizável, o programa usa-o como imagem sozinho.
- Com imagem o espaçamento entre algarismos é calculado a partir dos números de exemplo do template: fica a ≤ ~0,5 pt
  do original (imperceptível), mas para o melhor resultado prefira o PDF.

## Números com mais algarismos

- O template pode ter 3, 4, 6, 8… algarismos nos exemplos (`0001`, `000001`, `00000001`). Aceita-se até 12.
- Se pedir **mais** algarismos do que o desenho prevê (ex.: 8 num desenho de 4), o tamanho dos números é **reduzido
  na mesma proporção** (igual em todos os bilhetes) para caberem no mesmo espaço; fica um aviso no registo.
- Se «Até» tiver mais algarismos do que «Algarismos», alarga automaticamente (999 999 → 6).
- Testado: 1–1 000 000 num único PDF (41 667 páginas, 28 MB, ~1,5 min, ~190 MB de memória).

## Regras do template

- Números de exemplo escritos como **texto** (não como imagem/forma): `0001` … `000N`, cada um 2 vezes (aceita mais de
  9 bilhetes: `0010`, `0011`, …). Exceção: um template com uma só rifa pode ter `0001` uma única vez. Funciona com o texto que o Canva gera (cada carácter num operador separado, dentro
  de formulários aninhados).
- Outros números no template (ano, telefone, mesmo a começar por 0) ficam como estão.
- Só a 1.ª página é usada. Letra, tamanho, cor e orientação são detetados.
- Se o template usar mais do que uma letra nos números, o ficheiro do passo 2 serve para todas.

## Construir o .exe

```
construir.bat
```
Precisa de [uv](https://docs.astral.sh/uv/). Cria `.venv`, instala `requirements.txt`, **compila com o Nuitka** (a
1.ª vez descarrega sozinho o compilador `zig`, ~10–20 min) e assina o resultado.

**Ofuscação:** o Nuitka traduz o Python para C e compila-o. O `.exe` não contém código Python nem *bytecode*
(`.pyc`), só código máquina (sem docstrings nem `assert`), o que torna a engenharia inversa muito mais difícil do que
nos empacotadores comuns (PyInstaller, py2exe), cujo código se recupera com um comando. Verificado no `.exe`
descompactado: 0 ficheiros `.py`, 0 `.pyc`. **Limites:** a lógica não se recupera como Python, mas os *nomes* das
funções e os textos (traduções, mensagens) ficam legíveis no binário (o Nuitka guarda-os); quem analisar o código
máquina com um desassemblador consegue seguir o fluxo, só com muito mais trabalho. Nenhuma ofuscação é impenetrável.
Detalhes e licenças em `LICENCAS.md`.

Para correr sem construir: `.venv\Scripts\python.exe app.py`.

### Publicar uma versão no GitHub

O fluxo `.github/workflows/windows.yml` compila o `.exe` num servidor Windows do GitHub (15–25 min), corre o
`--selftest` e anexa `GeradorRifas.exe` + `GeradorRifas.exe.sha256` a uma *release* **do repositório público
`AndreNogueira/gerador-rifas-windows`** (o GitHub não deixa tirar os arquivos «Source code» de uma release: por isso o
`.exe` vai para um repositório que só tem um README, e o código fica no repositório privado):

```
git tag windows-v2.3.0 && git push origin windows-v2.3.0      # ou Actions › Windows › Run workflow
```
**Uma vez:** criar um *fine-grained personal access token* (GitHub › Settings › Developer settings), só para o repositório
`gerador-rifas-windows`, com *Contents: Read and write*, e guardá-lo como *secret* **`RELEASES_TOKEN`** no repositório
privado (Settings › Secrets and variables › Actions). O `GITHUB_TOKEN` automático só escreve no próprio repositório.
O `.exe` do GitHub sai **sem assinatura** (`SEM_ASSINATURA=1`; um certificado autoassinado criado no servidor não vale
nada). Para publicar um `.exe` assinado, construa em casa e use
`gh release upload windows-v2.3.0 dist\GeradorRifas.exe --clobber --repo AndreNogueira/gerador-rifas-windows`.

## Assinatura digital e SmartScreen

O `.exe` é assinado (Authenticode) por `assinar.ps1`, chamado no fim de `construir.bat`:

- **Autoassinado (por defeito, grátis):** cria um certificado «Gerador de Rifas (autoassinado)» no repositório
  pessoal do Windows e assina. O ficheiro passa a ter editor e integridade verificáveis, mas **o SmartScreen só deixa
  de avisar nos PCs que confiem nesse certificado**: copie `assinatura\GeradorRifas.cer` e `instalar_certificado.ps1`
  para esse PC e execute o script (pede confirmação; instala só para o utilizador atual).
- **Para o aviso desaparecer em qualquer PC** é preciso um certificado de uma autoridade reconhecida (OV/EV,
  ou o serviço Azure Trusted Signing) — o Windows só confia nelas — e um pouco de «reputação» de descargas.
  Quando tiver um: `.\assinar.ps1 -Exe dist\GeradorRifas.exe -Pfx certificado.pfx -Senha "…" -Timestamp`.
- Ficheiros copiados por USB/rede interna, sem passar pela internet, nem chegam a acionar o SmartScreen.
- O `.exe` leva também metadados de versão (empresa, produto, descrição) e ícone, o que reduz alertas de antivírus.

## Testes

- `GeradorRifas.exe --selftest C:\pasta\teste` – sem janela: confere as traduções (mesmas chaves e marcadores nas 18
  línguas), constrói e reconstrói a janela em cada língua e gera PDFs com PDF e com PNG de algarismos
  (`selftest.txt` → `RESULTADO: OK`).
- `testes\gerar_template_aleatorio.py <pasta> <semente> <n> [rotação|-] [algarismos]` – template aleatório (página,
  grelha, letra, cores, fundo, talão) e o seu ficheiro de algarismos. Há 8 em `testes\templates_aleatorios\`
  (2, 3, 4, 5, 8, 12, 14 e 24 por página; 4, 6 e 8 algarismos; talão a 0°, 90°, 180° e 270°).
- `testes\teste_5000.py <pasta> <saída> pdf|png [N]` – gera N (5000) rifas em cada template (1 PDF + vários),
  com verificação; `testes\comparar_rotas.py` compara a rota PDF com a rota imagem; `testes\teste_digitos.py` – mais
  algarismos e 1 milhão de números; `testes\teste_gui.py` – percorre a janela real (zoom, expandir, 18 línguas, nome
  obrigatório, geração).
- `testes\teste_folha.py <exemplos> <saída>` – o modo «uma só rifa»: contas de arrumação feitas à mão, 42 tamanhos de
  rifa (nenhuma sai da folha nem se sobrepõe), A4/A3/Letter com várias margens, algarismos em PDF e em imagem, rifa
  recortada de uma A4, número por folha pedido/acima do máximo, rifa maior que a folha; gera e verifica os PDFs.
- `testes\teste_canva.py <saída>` – templates REAIS do Canva que estão em `testes\` (`RIFA NATAL 2026*.pdf` + o ficheiro
  `… Letras.pdf` com a letra real): 5 por página e uma rifa (A4, A3, Letter), 4 e 5 algarismos, vários PDFs, e confere o PDF
  gerado pela app (`teste - 00001 - 30000.pdf`). Tudo verificado.
- `testes\teste_limpar.py` – o botão «Limpar tudo».
- `testes\teste_redimensionar.py <pasta>` – mede o redimensionamento da janela e da divisória e confirma que não ficam
  artefactos (compara com a repintura completa do Windows). Medido: janela ~30 ms/passo (antes ~220), divisória ~1 ms
  (antes ~300), zoom do visor ~1 ms em qualquer ampliação.
- Resultados: 5000 rifas em cada um dos 8 templates, por PDF e por imagem, em 1–3 s cada, tudo verificado.

**Porque redimensionar é rápido:** o visor só desenha a parte visível da imagem; a divisória própria só desenha uma
linha enquanto se arrasta; e `widgets.repintar_so_o_necessario` retira `CS_HREDRAW/CS_VREDRAW` às classes de janela do
Tk (Windows), que obrigavam a repintar todos os widgets do CustomTkinter a cada passo.

## Ficheiros

- `assets\ajuda\` imagens do tutorial · `assets\video\` vídeos do tutorial
- `app.py` janela principal e menus · `visor.py` pré-visualização · `ajuda.py` tutorial · `widgets.py` painel
  deslocável, barra de menus, dicas e a otimização de redimensionamento · `tema.py` cores do Windows · `icones.py` ícones
- `ambiente.py` põe `..\src` no caminho de importação (e guarda o que é do Windows) · **`..\src\core\`** o motor e toda a lógica sem janela:
  `motor.py`, `pdftexto.py` (leitura/edição do texto dos PDF), `i18n.py` + `idiomas\` (textos), `pedido.py`, `escolha_folha.py`, `config.py`, `tutorial.py`, `autoteste.py`
- `exemplos\` template e algarismos de exemplo · `assets\icon.ico`, `make_icon.py` ícone
- `construir.bat`, `assinar.ps1`, `instalar_certificado.ps1`, `requirements.txt` · `LICENCAS.md`
- `..\final` (scripts de linha de comandos antigos, ainda com PyMuPDF) não faz parte da app.
