# Licenças das bibliotecas

O **Gerador de Rifas** só usa bibliotecas com licenças permissivas (sem *copyleft*): podem ser usadas, copiadas e
distribuídas dentro de um programa fechado, mantendo apenas os avisos de autoria.

## O que vai dentro do `.exe`

| Componente | Para quê | Licença |
|---|---|---|
| [pypdf](https://github.com/py-pdf/pypdf) 7 | ler/escrever PDF | BSD-3-Clause |
| [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) 5 + [PDFium](https://pdfium.googlesource.com/pdfium/) | desenhar páginas (pré-visualização, medições) e extrair texto (verificação) | BSD-3-Clause ou Apache-2.0 (PDFium: BSD-3-Clause) |
| ↳ bibliotecas do PDFium: FreeType (FTL), HarfBuzz (MIT), ICU (Unicode), lcms2 (MIT), libjpeg-turbo (BSD/IJG/zlib), OpenJPEG (BSD-2), libpng, libtiff, zlib, Abseil, Highway, simdutf, fast_float, dragonbox, AGG | internas do PDFium | todas permissivas (textos em `pypdfium2-*.dist-info/licenses`) |
| [Pillow](https://python-pillow.org/) 13 | imagens | MIT-CMU (HPND) |
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 6 | interface | MIT (CC0 no pacote) |
| darkdetect, packaging | tema do sistema / versões | BSD-3-Clause; Apache-2.0 ou BSD-2 |
| Python / Tcl/Tk | interpretador e janelas | PSF; licença tipo BSD do Tcl/Tk |
| Tipos de letra do CustomTkinter (Roboto) | texto da interface | Apache-2.0 |

**Não é usado** o PyMuPDF/MuPDF (AGPL-3.0 ou licença comercial), que era a única biblioteca com *copyleft* forte da
versão anterior.

## Ferramentas de construção (não fazem parte do programa)

| Ferramenta | Licença | Nota |
|---|---|---|
| [Nuitka](https://nuitka.net/) | AGPL-3.0 (a ferramenta) | Compila o Python para C. **O programa gerado não herda a AGPL**: o código compilado é do autor e o código C de execução que o Nuitka junta é Apache-2.0 (ver a documentação do Nuitka, «License»). |
| zig (compilador de C que o Nuitka descarrega) | MIT | só compila; não fica no `.exe` |
| reportlab (BSD) | permissiva | na app: a galeria de templates (desenha os PDFs; traz a letra Vera) |
| fontTools (MIT), psutil (BSD-3) | permissivas | só nos testes (`testes\`) e para criar os exemplos |
| Letra Vera (Bitstream Vera, vem com o reportlab) | licença livre (permite usar e embutir) | na galeria de templates e nos ficheiros de exemplo (`exemplos\`) |
| [ffmpeg](https://ffmpeg.org/) + x264 (via `imageio-ffmpeg`) | GPL (o ffmpeg usado) | **só para gravar os vídeos do tutorial** (`testes\fazer_video.py`); não faz parte do programa nem vai no `.exe`. O que fica é o ficheiro `.mp4`, gerado por nós. |

Se preferir não usar nem uma ferramenta AGPL só para construir, a alternativa é distribuir o código em Python
(sem ofuscação) — o programa em si continua livre de *copyleft*.

## Fora desta pasta

`..\final\` (scripts de linha de comandos da fase anterior) ainda usa o PyMuPDF (AGPL). Não faz parte da app.
