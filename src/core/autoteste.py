"""A parte do auto-teste (app --selftest) que nao precisa de janela: gerar os PDFs de exemplo e confirma-los.

Extraido de app.py::selftest. As linhas de resultado e a ordem sao exatamente as do auto-teste original.
"""
from __future__ import annotations

from pathlib import Path

from .motor import Trabalho, gerar, preparar


def gerar_exemplos(exemplos: Path, destino: Path) -> tuple:
    """Gera os exemplos com os dois ficheiros de algarismos (imagem e PDF): template de 5 rifas por pagina e, com uma so rifa,
    folha A4 (margem 5 e 12) e A3. Devolve (linhas de resultado, codigo) com codigo 0 = tudo ok, 1 = alguma falha."""
    exemplos, destino = Path(exemplos), Path(destino)
    linhas, codigo = [], 0
    tpl = exemplos / "template_exemplo.pdf"
    for nome in ("digitos_exemplo.png", "digitos_exemplo.pdf"):
        prep = preparar(tpl, exemplos / nome)
        res = gerar(Trabalho(saida=destino / nome.split(".")[0], nome="TESTE", inicio=1, fim=65), prep)
        ok = all(r.ok for r in res)
        linhas.append(f"{nome}: {'ok' if ok else 'ERRO'} ({sum(r.paginas for r in res)} paginas)")
        codigo |= 0 if ok else 1
    # uma so rifa no template: a folha A4 e enchida com copias (PDF e imagem de algarismos; 0, 90 graus e A3)
    for nome in ("digitos_exemplo.png", "digitos_exemplo.pdf"):
        prep = preparar(exemplos / "template_exemplo_1_rifa.pdf", exemplos / nome)
        for papel, margem in (("A4", 5), ("A3", 5), ("A4", 12)):
            p = prep.com_folha(papel, margem)
            res = gerar(Trabalho(saida=destino / "folha", nome=f"UMA-{papel}-{margem}-{nome[-3:]}", inicio=1, fim=23), p)
            ok = all(r.ok for r in res) and p.disp.n >= 3
            linhas.append(f"1 rifa, {papel}, margem {margem}, {nome}: {'ok' if ok else 'ERRO'} "
                          f"({p.disp.n} por folha, {sum(r.paginas for r in res)} paginas)")
            codigo |= 0 if ok else 1
    return linhas, codigo


def gerar_galeria(destino: Path) -> tuple:
    """Os 4 desenhos da galeria: cada um vira template + algarismos, prepara-se, e gera-se uma folha com serie («A-»), cor, saltos e marcas de corte
    (o que a app Windows faz em «Extras»). Sem o reportlab (so a webapp e o .exe o trazem) a linha diz que se ignorou. Devolve (linhas, codigo)."""
    try:
        import reportlab  # noqa: F401
    except ImportError:
        return ["galeria: ignorada (sem reportlab)"], 0
    from . import galeria
    from .escolha_folha import escolher_folha, preparado_com_folha
    destino = Path(destino) / "galeria"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "algarismos.pdf").write_bytes(galeria.criar_algarismos())
    linhas, codigo = [], 0
    for d in galeria.DESENHOS:
        (destino / f"{d.id}.pdf").write_bytes(galeria.criar_template(d.id, galeria.Textos("Rifa", "Organizacao", ("1.o Premio",), "")))
        prep = preparar(destino / f"{d.id}.pdf", destino / "algarismos.pdf")
        esc = escolher_folha(prep.info, "A4", "8", "", marcas=True)
        p = preparado_com_folha(prep, esc.disp)
        res = gerar(Trabalho(saida=destino, nome=f"G-{d.id}", inicio=1, fim=12, digitos=3, prefixos=("A-",), saltar=((2, 3),),
                             cor_numeros=(0.78, 0.1, 0.12)), p)
        ok = all(r.ok for r in res) and p.disp.marcas
        linhas.append(f"galeria {d.id}: {'ok' if ok else 'ERRO'} ({p.disp.n} por folha, {sum(r.paginas for r in res)} paginas)")
        codigo |= 0 if ok else 1
    return linhas, codigo


def main(argv: list | None = None) -> int:
    """Auto-teste sem janela para CI/Linux (substitui `GeradorRifas.exe --selftest` fora do Windows):
    `python -m core <pasta_de_exemplos> <pasta_de_saida>`. Verifica as traducoes e gera os exemplos. Devolve 0 se tudo ok."""
    import sys
    from . import i18n
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("uso: python -m core <pasta_de_exemplos> <pasta_de_saida>", file=sys.stderr)
        return 2
    exemplos, destino = Path(args[0]), Path(args[1])
    destino.mkdir(parents=True, exist_ok=True)
    probs = i18n.verificar_traducoes()
    linhas = [f"traducoes ({len(i18n.LINGUAS)} linguas): {'ok' if not probs else probs}"]
    codigo = int(bool(probs))
    for gerar_ in (gerar_exemplos, lambda e, d: gerar_galeria(d)):
        extra, cod = gerar_(exemplos, destino)
        linhas += extra
        codigo |= cod
    linhas.append("RESULTADO: " + ("OK" if codigo == 0 else "FALHOU"))
    print("\n".join(linhas))
    return int(codigo)
