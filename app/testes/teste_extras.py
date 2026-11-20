"""Testa a interface real das funcionalidades «Extras» da app Windows (v2.4; o editor de templates é da 2.5): séries/cor/logótipo/marcas de corte, galeria, editor, sorteio e
exportar a lista. Abre a janela de verdade (precisa de ecrã) e comanda-a como um utilizador; sai com código 1 se algo falhar.

Uso: python testes/teste_extras.py <pasta_saida>     (capturas de ecrã em <pasta_saida>; usa os exemplos de app/exemplos)
A lógica por baixo (séries, CSV, sorteio, logótipo) tem os testes sem janela em ..\\tests (pytest); aqui verifica-se a ligação à interface.
"""
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ambiente  # noqa: F401,E402  (poe ..\src no sys.path)
sys.setswitchinterval(0.0005)
from tkinter import filedialog, messagebox

mensagens: list = []
messagebox.showwarning = messagebox.showerror = lambda *a, **k: mensagens.append(str(a[1]).replace("\n", " / ")[:120])
messagebox.askyesno = lambda *a, **k: True
from PIL import Image, ImageGrab

import app as A
import extras
import core
from core import galeria, i18n

SAIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="teste-extras-"))
SAIDA.mkdir(parents=True, exist_ok=True)
falhas: list = []


def ok(cond, msg: str) -> None:
    print(("ok    " if cond else "FALHA ") + msg)
    if not cond:
        falhas.append(msg)


a = A.App(usar_config=False)
a.geometry("1240x880+30+10")


def pump(seg: float, ate=None) -> None:
    t0 = time.time()
    while time.time() - t0 < seg:
        a.update()
        time.sleep(0.03)
        if ate and ate():
            break


def foto(janela, nome: str) -> None:
    janela.update()
    x, y, w, h = janela.winfo_rootx(), janela.winfo_rooty(), janela.winfo_width(), janela.winfo_height()
    ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(SAIDA / nome)


pump(0.5)
i18n.definir("pt")

# --- exportar a lista sem template, com series e saltos (os campos da janela principal + as opcoes)
a.v_inicio.set("1"); a.v_fim.set("6"); a.v_digitos.set("3"); a.v_nome.set("Rifa de Natal")
a.v_prefixos.set("A-, B-"); a.v_saltar.set("2-3")
destino = SAIDA / "lista.csv"
filedialog.asksaveasfilename = lambda **k: str(destino)
r = a._exportar_csv()
ok(r == destino and destino.exists(), "exportar CSV escreve o ficheiro escolhido")
linhas = destino.read_bytes().decode("utf-8-sig").split("\r\n")
ok(linhas[0] == "Série;Número;Nome;Contacto;Pago" and linhas[1:4] == ["A;A-001;;;", "A;A-004;;;", "A;A-005;;;"] and "B;B-006;;;" in linhas,
   f"CSV com series e numeros saltados ({linhas[:3]})")
destino2 = SAIDA / "controlo.pdf"
filedialog.asksaveasfilename = lambda **k: str(destino2)
ok(a._exportar_folha() == destino2 and destino2.read_bytes().startswith(b"%PDF"), "folha de controlo em PDF")
a.v_fim.set("1")
a.v_inicio.set("5")
mensagens.clear()
ok(a._exportar_csv() is None and mensagens, "intervalo invalido avisa e nao escreve")
a.v_inicio.set("1"); a.v_fim.set("20")

# --- guardar e abrir o pedido (2.6): um ficheiro .rifas com os campos; abrir repoe-os, e um ficheiro alheio avisa
a.v_inicio.set("10"); a.v_fim.set("99"); a.v_digitos.set("3"); a.v_max.set("150"); a.v_nome.set("Rifa de Natal")
a.v_prefixos.set("A-, B-"); a.v_saltar.set("13"); a.v_cor_serie.set(True); a.v_marcas.set(True); a.v_cor_numeros.set("#c2410c"); a._set_modo("unico")
pedido = SAIDA / "pedido.rifas"
filedialog.asksaveasfilename = lambda **k: str(pedido)
ok(a._guardar_pedido() == pedido and pedido.read_bytes().startswith(b"{"), "«Guardar pedido» escreve o ficheiro .rifas")
ok(b"Users" not in pedido.read_bytes() and b"template" not in pedido.read_bytes(), "o ficheiro não leva caminhos nem template")
a.v_inicio.set("1"); a.v_fim.set("5"); a.v_nome.set(""); a.e_nome.delete(0, "end"); a.v_prefixos.set(""); a.v_saltar.set(""); a.v_cor_serie.set(False)
a.v_marcas.set(False); a.v_cor_numeros.set(""); a._set_modo("varios")
ok(a._abrir_pedido(str(pedido)), "«Abrir pedido» lê o ficheiro")
ok((a.v_inicio.get(), a.v_fim.get(), a.v_digitos.get(), a.v_max.get(), a.v_nome.get(), a.e_nome.get()) == ("10", "99", "3", "150", "Rifa de Natal", "Rifa de Natal")
   and a.v_prefixos.get() == "A-, B-" and a.v_saltar.get() == "13" and a.v_cor_serie.get() and a.v_marcas.get() and a.v_cor_numeros.get() == "#c2410c" and a.modo == "unico",
   "abrir repõe os números, o nome, as séries, as cores, as marcas e o modo")
lixo = SAIDA / "lixo.rifas"
lixo.write_bytes(b"isto nao e um pedido")
mensagens.clear()
ok(not a._abrir_pedido(str(lixo)) and mensagens and a.v_fim.get() == "99", "um ficheiro alheio avisa e não mexe nos campos")
a.v_inicio.set("1"); a.v_fim.set("20"); a.v_digitos.set("4"); a.v_max.set("300"); a.v_nome.set(""); a.e_nome.delete(0, "end")
a.v_prefixos.set(""); a.v_saltar.set(""); a.v_cor_serie.set(False); a.v_marcas.set(False); a.v_cor_numeros.set(""); a._set_modo("varios")

# --- janela das opcoes
a._abrir_extra("opcoes", extras.Opcoes)
pump(0.6)
op = a.w_extras["opcoes"]
foto(op, "opcoes.png")
a.v_cor_numeros.set("#C9183A")
pump(0.1)
ok(op.amostra.cget("fg_color") == "#c9183a", "a amostra da cor acompanha o campo")
op.destroy()

# --- galeria: pre-visualiza no worker e «Usar» cria o template e os algarismos
a._abrir_extra("galeria", extras.Galeria)
g = a.w_extras["galeria"]
g.v["titulo"].set("Rifa de Natal")
g.v["organizacao"].set("Associação Exemplo")
g.v["p1"].set("1.º Prémio: Cabaz")
pump(6, lambda: g._foto is not None and g.token >= 1 and not g._espera and g.previa.cget("text") == "")
foto(g, "galeria.png")
ok(g._foto is not None, "a galeria mostra a pre-visualizacao")
g.v["titulo"].set("हिन्दी")
pump(3, lambda: g.l_erro.cget("text") != "")
ok(g.l_erro.cget("text") != "", "texto que nenhuma letra tem (hindi) mostra um aviso em vez de uma imagem")
for titulo in ("Κλήρωση Ω", "Лотерея", "Bốc thăm", "抽奖 São", "抽選会", "추첨"):                       # 2.7: grego, cirilico, vietnamita, chines, japones e coreano
    g.v["titulo"].set(titulo)
    pump(3, lambda: g.l_erro.cget("text") == "" and g._foto is not None and not g._espera)
    ok(g.l_erro.cget("text") == "", f"a galeria aceita «{titulo}» (2.7)")
g.v["titulo"].set("Rifa de Natal")
ok(g._n_premios() == 3 and sum(1 for e in g.e_premios if e.winfo_manager()) == 3, "a galeria começa com 3 premios (o minimo)")
g.v_n.set("10")
g._mostrar_premios()
for i in range(1, 11):
    g.v[f"p{i}"].set(f"{i}.º Prémio: Cabaz")
pump(6, lambda: g._foto is not None and not g._espera and g.l_erro.cget("text") == "")
ok(sum(1 for e in g.e_premios if e.winfo_manager()) == 10 and len(g._textos().premios) == 10, "escolhendo 10, as 10 caixas aparecem e os 10 premios entram na rifa")
g.v_n.set("4")
g._mostrar_premios()
ok(len(g._textos().premios) == 4, "voltando a 4, so os 4 primeiros premios contam")
pump(1.5)
print('pendentes no worker:', a.pool._work_queue.qsize(), 'token', g.token)
g._usar()
t0 = time.time()
pump(40, lambda: a.prep is not None)
print(f'(template analisado em {time.time() - t0:.1f} s)')
ok(a.prep is not None and a.prep.info.n_campos == 1, "«Usar este template» deixa o template analisado (1 rifa com talao)")
ok(not g.winfo_exists() if hasattr(g, "winfo_exists") else True, "a janela da galeria fecha")
ok(Path(a.v_template.get()).exists() and Path(a.v_alg.get()).exists(), "template e algarismos criados")
pasta_galeria = a._pasta_galeria

# --- preçário: a janela pre-visualiza no worker, os precos entram, a moeda muda, guarda PDF/imagem/ficheiro e volta a abrir o ficheiro
a._abrir_extra("precario", extras.Precario)
pr = a.w_extras["precario"]
pump(8, lambda: pr._foto is not None and not pr._espera and pr.previa.cget("text") == "")
foto(pr, "precario.png")
ok(pr._foto is not None and len(pr.linhas) >= 5, "o preçário abre com a ocasião da época e mostra a pre-visualizacao")
ok(pr.v_titulo.get() != "" and pr.v_ocasiao.get() in extras.precario_catalogo.OCASIOES, "o titulo e a ocasião vem da época")
pr._escolher_ocasiao(pr._nome_ocasiao(extras.precario_catalogo.OCASIOES["festa_popular"]))
ok(pr.v_titulo.get() == "Festa popular" and pr.v_desenho.get() == "arraial" and any(ln["artigo"] == "agua" for ln in pr.linhas), "escolher a ocasião muda o titulo, o desenho e os artigos")
pr.v_artigo["sumo"].set(True)
pr._alternar("sumo")
ok(any(ln["artigo"] == "sumo" for ln in pr.linhas) and "sumo" in pr.v_preco, "marcar um artigo acrescenta a sua linha de preço")
pr.v_preco["agua"].set("1,5")
pr.v_preco["sumo"].set("2")
pr.v_meu.set("Bolo da avó")
pr._juntar()
ok(any(ln["nome"] == "Bolo da avó" for ln in pr.linhas), "«+» acrescenta um artigo meu")
p = pr.precario()
ok(p.moeda.codigo == "EUR" and [ln.preco for ln in p.linhas if ln.artigo in ("agua", "sumo")] == [1500, 2000], "os precos escritos na lingua leem-se (1,5 → 1500) e a moeda é a do país da lingua")
pr.m_moeda.set("BRL (R$)")
pr.v_inventada.set(True)
pr.v_inv_nome.set("fichas")
pr.v_inv_casas.set("0")
pump(4, lambda: not pr._espera and pr.l_erro.cget("text") == "")
p = pr.precario()
ok(isinstance(p.moeda, extras.moeda.MoedaInventada) and p.moeda.nome == "fichas", "a moeda inventada ganha à da lista quando tem nome")
pr.v_inventada.set(False)
pr.v_preco["agua"].set("abc")
pump(2, lambda: pr.l_erro.cget("text") != "")
ok(pr.l_erro.cget("text") != "", "um preço que não se lê mostra um aviso")
pr.v_preco["agua"].set("1,5")
pump(8, lambda: pr._foto is not None and not pr._espera and pr.l_erro.cget("text") == "")
ok(pr.l_erro.cget("text") == "", "corrigido o preço, o aviso desaparece")
pr.v_titulo.set("हिन्दी")
pump(4, lambda: pr.l_erro.cget("text") != "")
ok(pr.l_erro.cget("text") != "", "um título que o PDF não escreve (hindi) mostra um aviso em vez de uma imagem estragada")
pr.v_titulo.set("Festa da escola")
pump(6, lambda: not pr._espera and pr.l_erro.cget("text") == "")
tmp = Path(tempfile.mkdtemp(prefix="precario-"))
pdf = pr._guardar_pdf(str(tmp / "p.pdf"))
png = pr._guardar_imagem(str(tmp / "p.png"))
fich = pr._guardar_ficheiro(str(tmp / "p.precario"))
ok(pdf and pdf.read_bytes().startswith(b"%PDF") and png and png.read_bytes()[:4] == b"\x89PNG" and fich and fich.stat().st_size > 200, "guarda o PDF, a imagem e o ficheiro .precario")
guardado = extras.precario.de_bytes(fich.read_bytes())
pr.v_preco["agua"].set("9")
pr.linhas = [ln for ln in pr.linhas if ln["artigo"] != "pizza"]
ok(pr._abrir_ficheiro(str(fich)), "abre o ficheiro guardado")
ok(pr.precario() == guardado and pr.v_titulo.get() == "Festa da escola", "abrir o ficheiro repõe exatamente o preçário (titulo, linhas, precos e moeda)")
(tmp / "mau.precario").write_text("lixo", encoding="utf-8")
mensagens.clear()
ok(not pr._abrir_ficheiro(str(tmp / "mau.precario")) and mensagens, "um ficheiro que não é nosso é recusado com um aviso")

# --- dois tamanhos: a segunda caixa de preço aparece, os rótulos entram e o ficheiro .precario guarda tudo
pr.v_inventada.set(False)
pr.v_tamanhos.set(True)
pr._precos()
pr.v_rotulo1.set("Peq.")
pr.v_rotulo2.set("Gde.")
pr.v_preco["agua"].set("1")
pr.v_preco2["agua"].set("1,8")
pump(6, lambda: not pr._espera and pr.l_erro.cget("text") == "")
p2 = pr.precario()
ok(p2.tamanhos and p2.rotulos == ("Peq.", "Gde.") and next(ln for ln in p2.linhas if ln.artigo == "agua").preco2 == 1800, "dois tamanhos: os dois preços e os rótulos chegam ao preçário")
foto(pr, "precario_tamanhos.png")
fich2 = pr._guardar_ficheiro(str(tmp / "t.precario"))
pr.v_tamanhos.set(False)
pr._precos()
ok(not pr.precario().tamanhos, "desligados, o preçário volta a um só preço")
ok(pr._abrir_ficheiro(str(fich2)) and pr.v_tamanhos.get() and pr.precario() == p2, "abrir o ficheiro repõe os dois tamanhos, os rótulos e o segundo preço")
pr.v_preco2["agua"].set("abc")
pump(3, lambda: pr.l_erro.cget("text") != "")
ok(pr.l_erro.cget("text") != "", "um segundo preço que não se lê mostra um aviso")
pr.v_tamanhos.set(False)
pr._precos()
pr.v_inventada.set(False)

# --- vales de fichas numerados: só com moeda inventada com nome; pre-visualiza no worker; «Criar» passa o template e os algarismos à janela principal
pr.v_inventada.set(False)
pr._vales()
ok(pr.app.w_extras.get("vales") is None and pr.l_erro.cget("text") != "", "sem moeda inventada os vales não abrem e o aviso explica porquê")
pr.v_inventada.set(True)
pr.v_inv_nome.set("fichas")
pr.v_titulo.set("Festa da escola")
pump(4, lambda: not pr._espera)
pr._vales()
va = a.w_extras["vales"]
pump(8, lambda: va._foto is not None and not va._espera)
foto(va, "vales.png")
ok(va._foto is not None and va.l_erro.cget("text") == "", "a janela dos vales pre-visualiza o vale no worker")
ok(va.vale().moeda == "ficha" and va.vale().moeda_plural == "fichas" and va.vale().quantidade == 1, "o singular propõe-se a partir do plural da moeda do preçário")
va.v["quantidade"].set("0")
pump(4, lambda: va.l_erro.cget("text") != "")
ok(va.l_erro.cget("text") != "", "uma quantidade fora de 1 a 99 mostra o aviso traduzido")
va.v["quantidade"].set("3")
va.v["nota"].set("Só na festa")
pump(6, lambda: not va._espera and va.l_erro.cget("text") == "")
ok(va.vale().valor_texto() == "3 fichas", "o valor usa o plural quando a quantidade não é 1")
a.v_prefixos.set("")
va._usar()
pump(8, lambda: a.info is not None)
ok(a.info is not None and a.info.n_campos == 1 and a.info.primeiro == "0001" and "vales-" in a.v_template.get(), "«Criar vales numerados» deixa o template do vale e os algarismos na janela principal, que o analisa")
ok(not (a.w_extras.get("vales") and a.w_extras["vales"].winfo_exists()), "a janela dos vales fecha-se")
pr.destroy()

# --- com o template da galeria (uma rifa): marcas de corte, cor, prefixo e pre-visualizacao
a.v_prefixos.set("A-"); a.v_saltar.set(""); a.v_inicio.set("1"); a.v_fim.set("30"); a.v_digitos.set("4")
a.v_marcas.set(True)
a.v_cor_numeros.set("#C9183A")
pump(0.5)
ok(a.disp is not None and a.disp.marcas, "as marcas de corte chegam a disposicao da folha")
a._previa()
pump(30, lambda: a.st_titulo[0] == "previa_titulo_n")
foto(a, "previa.png")
ok(a.st_titulo[0] == "previa_titulo_n", "a pre-visualizacao com prefixo, cor e marcas corre")
logo = SAIDA / "logo.png"
Image.new("RGBA", (200, 100), (30, 140, 90, 255)).save(logo)
a.v_logo.set(str(logo))
tr = a._trabalho(com_logotipo=True)
ok(tr.marca is not None and tr.prefixos == ("A-",) and tr.cor_numeros is not None, "o pedido leva o logotipo, o prefixo e a cor")
a.v_logo.set(str(SAIDA / "nao-existe.png"))
try:
    a._trabalho(com_logotipo=True)
    ok(False, "logotipo inexistente devia dar erro")
except core.ErroRifas:
    ok(True, "logotipo inexistente da erro traduzido")
a.v_logo.set(str(logo))

# --- gerar uma serie curta e verificar o prefixo nos ficheiros
a.v_saida.set(str(SAIDA / "pdfs")); a.v_fim.set("12"); a.v_nome.set("Teste")
a.modo = "unico"
a._gerar()
pump(60, lambda: not a.a_gerar and a.prog >= 1.0)
ficheiros = sorted(p.name for p in (SAIDA / "pdfs").glob("*.pdf"))
ok(len(ficheiros) == 1, f"gera um PDF ({ficheiros})")
ok(a.st_estado is not None and a.st_estado[0] == "est_ok", "geracao com prefixo, cor, logotipo e marcas termina sem erros")

# --- sorteio verificavel (a mesma resposta que o site)
a.v_inicio.set("1"); a.v_fim.set("100"); a.v_saltar.set("13")
a._abrir_extra("sorteio", extras.Sorteio)
s = a.w_extras["sorteio"]
s.v_quantos.set("3"); s.v_semente.set("lotaria-2026-12-22")
esperado = core.sorteio.sortear(1, 100, 3, "lotaria-2026-12-22", ((13, 13),))
ok(s.sortear() == esperado and 13 not in esperado, f"sorteio igual a referencia ({esperado})")
foto(s, "sorteio.png")
s.v_semente.set("")
ok(s.sortear() is None and "200" in s.l_estado.cget("text"), "sem semente mostra o erro")
s.destroy()

# --- visual: Natal e Premiado trocam as cores; o automatico segue a epoca
import tema as TM
a._definir_visual("natal")
pump(0.5)
ok(TM.C["acento"] == ("#0F6B3F", "#6FE3A0") and a.visual == "natal", "o visual Natal muda as cores da janela")
foto(a, "natal.png")
a._definir_visual("premiado")
ok(TM.C["acento"][0] == "#6A35F5", "o visual Premiado repoe as cores")
a._definir_visual("auto")
ok(TM.visual_efetivo() == core.tema.visual_por_epoca(), "o automatico segue a epoca")
for v in core.tema.VISUAIS:                          # os 14 visuais (2.6): cada um refaz a janela com as suas cores, sem erros
    a._definir_visual(v)
    pump(0.15)
    ok(a.visual == v and TM.C["acento"][0].upper() == core.tema.PALETAS_VISUAIS[v][0]["acento"][0].upper(), f"o visual {v} aplica as suas cores")
    if v in ("gala", "terminal"):
        foto(a, f"visual_{v}.png")
a._definir_visual("auto")

# --- limpar tudo repoe as opcoes e apaga a pasta da galeria
a._limpar_tudo()
pump(0.3)
ok(a.v_prefixos.get() == "" and a.v_logo.get() == "" and not a.v_marcas.get() and a._pasta_galeria is None, "«Limpar tudo» repoe as opcoes")
ok(pasta_galeria is not None and not pasta_galeria.exists(), "a pasta temporaria da galeria foi apagada")

# --- editor de templates: desenha-se a rifa, edita-se com o rato e o teclado, e «Usar este template» cria o template e os algarismos
a._abrir_extra("editor", extras.EditorTemplates)
ed = a.w_extras["editor"]
ed.update()
pump(8, lambda: ed._foto is not None and not ed._espera)
foto(ed, "editor.png")
ok(ed._foto is not None and len(ed.m.elementos) == 11, "o editor abre com o modelo e mostra o PDF a sério")
ok(str(ed.botoes["desfazer"].cget("state")) == "disabled" and str(ed.b_usar.cget("state")) == "normal", "sem alterações não há o que desfazer; o modelo serve")
# o rato: clicar no título seleciona-o, arrastar move-o, largar refaz a imagem
titulo = next(e for e in ed.m.elementos if e.texto == "TÍTULO DA RIFA")
x0, y0, x1, y1 = ed.m.caixa(titulo.id)
px, py = ed._px((x0 + x1) / 2, (y0 + y1) / 2)
ed.tela.event_generate("<ButtonPress-1>", x=int(px), y=int(py))
ed.update()
ok(ed.sel == titulo.id, "clicar num texto seleciona-o")
x_antes = titulo.x
ed.tela.event_generate("<B1-Motion>", x=int(px) + 60, y=int(py) + 12)
ed.tela.event_generate("<ButtonRelease-1>", x=int(px) + 60, y=int(py) + 12)
ed.update()
ok(ed.m.por_id(titulo.id).x > x_antes + 20 and ed.m.por_id(titulo.id).y > 40, "arrastar move o elemento")
pump(6, lambda: not ed._espera)
x_depois = ed.m.por_id(titulo.id).x
ed._a_desfazer()
ok(ed.m.por_id(titulo.id).x == x_antes and ed.m.pode_refazer(), "desfazer repõe o sítio de antes do arrasto (o arrasto todo é um só passo)")
ed._a_refazer()
ok(ed.m.por_id(titulo.id).x == x_depois, "refazer volta a pô-lo onde estava")
# as setas e o teclado
ed.tela.focus_force()
ed.update()
ed.tela.event_generate("<Shift-Right>")
ed.update()
ok(ed.m.por_id(titulo.id).x == x_depois + 10, "as setas movem o elemento selecionado")
n = len(ed.m.elementos)
ed._a_duplicar()
ok(len(ed.m.elementos) == n + 1 and ed.sel != titulo.id, "duplicar cria uma cópia e seleciona-a")
ed._a_tras()
ok(ed.m.elementos[-2].id == ed.sel, "«Para trás» desce um nível de desenho")
ed._a_apagar()
ok(len(ed.m.elementos) == n and ed.sel is None, "apagar tira o elemento")
# a imagem (2.6): junta-se um PNG ou JPG, entra reduzida e a caber, e um ficheiro que não é imagem avisa
logo_png = SAIDA / "logo_editor.png"
Image.new("RGB", (400, 200), (200, 30, 30)).save(logo_png)
n = len(ed.m.elementos)
ed.acrescentar("imagem", str(logo_png))
ok(len(ed.m.elementos) == n + 1 and ed.m.por_id(ed.sel).tipo == "imagem" and ed.m.por_id(ed.sel).w == 160, "«+ Imagem» junta o PNG, a caber em 160 pt, e seleciona-o")
pump(6, lambda: not ed._espera)
ok(ed.m.sem_problemas() and str(ed.b_usar.cget("state")) == "normal", "com a imagem o desenho continua a servir")
mau = SAIDA / "nao_e_imagem.png"
mau.write_bytes(b"isto nao e uma imagem")
ed.acrescentar("imagem", str(mau))
ok(len(ed.m.elementos) == n + 1 and ed.l_erro.cget("text") != "", "um ficheiro que não é imagem avisa e não entra")
ed._a_apagar()
ed._mudou()
# o texto: escrever atualiza o desenho; algarismos que o motor confundiria avisam e bloqueiam
ed.acrescentar("texto")
ed.entrada_texto.delete(0, "end")
ed.entrada_texto.insert(0, "Ref 0123")
ed.update()
ok(ed.l_erro.cget("text") != "" and str(ed.b_usar.cget("state")) == "disabled", "texto com 0123 avisa e desativa «Usar este template»")
ed.entrada_texto.delete(0, "end")
ed.entrada_texto.insert(0, "Ano 2026")
ed.update()
ok(ed.l_erro.cget("text") == "" and str(ed.b_usar.cget("state")) == "normal", "2026 não é o número do bilhete: serve")
for e in [e for e in ed.m.elementos if e.tipo == "numero"]:
    ed.sel = e.id
    ed._a_apagar()
ok(ed.l_erro.cget("text") != "" and str(ed.b_usar.cget("state")) == "disabled", "sem o número 0001 não se pode usar")
ed._a_modelo()
ok(len(ed.m.elementos) == 11 and ed.m.pode_desfazer(), "«Começar com um modelo» repõe a rifa de partida (e desfaz-se)")
pump(6, lambda: not ed._espera)
foto(ed, "editor2.png")
ed._usar()
t0 = time.time()
pump(40, lambda: a.prep is not None)
print(f"(template do editor analisado em {time.time() - t0:.1f} s)")
ok(a.prep is not None and a.prep.info.n_campos == 1 and a.prep.info.n_numeros == {1: 2}, "«Usar este template» deixa o template do editor analisado (1 rifa com talão)")
ok(not ed.winfo_exists(), "a janela do editor fecha")
a._limpar_tudo()
pump(0.3)

# --- as 22 linguas: os menus e as janelas abrem sem faltar texto
for lg in i18n.LINGUAS:
    a._mudar_lingua(i18n.LINGUAS[lg])
    pump(0.15)
    for nome, cls in (("opcoes", extras.Opcoes), ("editor", extras.EditorTemplates), ("sorteio", extras.Sorteio)):
        a._abrir_extra(nome, cls)
        a.w_extras[nome].update()
        a.w_extras[nome].destroy()
ok(True, "as janelas abrem nas 22 linguas")
print("mensagens:", mensagens)
a.destroy()
print("FALHOU: " + "; ".join(falhas) if falhas else "TUDO OK")
sys.exit(1 if falhas else 0)
