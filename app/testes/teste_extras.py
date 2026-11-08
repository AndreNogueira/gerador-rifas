"""Testa a interface real das funcionalidades «Extras» da app Windows (v2.4): séries/cor/logótipo/marcas de corte, galeria, sorteio e
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
g.v["titulo"].set("Título com ŧ letra que a Vera não tem Ω")
pump(3, lambda: g.l_erro.cget("text") != "")
ok(g.l_erro.cget("text") != "", "texto que a letra nao tem mostra um aviso em vez de uma imagem")
g.v["titulo"].set("Rifa de Natal")
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

# --- limpar tudo repoe as opcoes e apaga a pasta da galeria
a._limpar_tudo()
pump(0.3)
ok(a.v_prefixos.get() == "" and a.v_logo.get() == "" and not a.v_marcas.get() and a._pasta_galeria is None, "«Limpar tudo» repoe as opcoes")
ok(pasta_galeria is not None and not pasta_galeria.exists(), "a pasta temporaria da galeria foi apagada")

# --- as 18 linguas: os menus e as janelas abrem sem faltar texto
for lg in i18n.LINGUAS:
    a._mudar_lingua(i18n.LINGUAS[lg])
    pump(0.15)
    for nome, cls in (("opcoes", extras.Opcoes), ("sorteio", extras.Sorteio)):
        a._abrir_extra(nome, cls)
        a.w_extras[nome].update()
        a.w_extras[nome].destroy()
ok(True, "as janelas abrem nas 18 linguas")
print("mensagens:", mensagens)
a.destroy()
print("FALHOU: " + "; ".join(falhas) if falhas else "TUDO OK")
sys.exit(1 if falhas else 0)
