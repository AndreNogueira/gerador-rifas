"""Cria um PDF de algarismos igual aos do Canva: fonte Type0 / Identity-H, CIDFontType2, subconjunto com os glifos
originais (retain_gids) e ToUnicode. So para testes (usa fontTools, licenca MIT; nao faz parte da app).

Uso: python fazer_digitos_type0.py <fonte.ttf> <saida.pdf> [texto]
"""
import io
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from pypdf import PdfWriter
from pypdf.generic import (ArrayObject, DecodedStreamObject, DictionaryObject, FloatObject, NameObject, NumberObject,
                           TextStringObject)

ttf, saida = Path(sys.argv[1]), Path(sys.argv[2])
texto = sys.argv[3] if len(sys.argv) > 3 else "0123456789"

fonte = TTFont(str(ttf))
cmap = fonte.getBestCmap()
upem = fonte["head"].unitsPerEm
gids = {ch: fonte.getGlyphID(cmap[ord(ch)]) for ch in set(texto)}

# subconjunto que mantem os numeros dos glifos (como o Canva)
opt = subset.Options()
opt.retain_gids = True
opt.layout_features = []
opt.name_IDs = []
opt.notdef_outline = True
sub = subset.Subsetter(opt)
sub.populate(unicodes=[ord(c) for c in set(texto)])
f2 = TTFont(str(ttf))
sub.subset(f2)
buf = io.BytesIO()
f2.save(buf)
dados = buf.getvalue()

w = PdfWriter()
pg = w.add_blank_page(width=520, height=110)

ff = DecodedStreamObject()
ff.set_data(dados)
ff[NameObject("/Length1")] = NumberObject(len(dados))
ff_ref = w._add_object(ff.flate_encode())
nome = "AAAAAA+" + ttf.stem.replace(" ", "")
desc = DictionaryObject({NameObject("/Type"): NameObject("/FontDescriptor"), NameObject("/FontName"): NameObject("/" + nome),
                         NameObject("/Flags"): NumberObject(4), NameObject("/ItalicAngle"): NumberObject(0),
                         NameObject("/Ascent"): NumberObject(900), NameObject("/Descent"): NumberObject(-200),
                         NameObject("/CapHeight"): NumberObject(700), NameObject("/StemV"): NumberObject(80),
                         NameObject("/FontBBox"): ArrayObject([NumberObject(x) for x in (-200, -250, 1200, 950)]),
                         NameObject("/FontFile2"): ff_ref})
larguras = ArrayObject()
for ch, g in sorted(gids.items(), key=lambda kv: kv[1]):
    larguras.append(NumberObject(g))
    larguras.append(ArrayObject([NumberObject(round(fonte["hmtx"][cmap[ord(ch)]][0] * 1000 / upem))]))
cid = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/CIDFontType2"),
                        NameObject("/BaseFont"): NameObject("/" + nome),
                        NameObject("/CIDSystemInfo"): DictionaryObject({NameObject("/Registry"): TextStringObject("Adobe"),
                                                                        NameObject("/Ordering"): TextStringObject("Identity"),
                                                                        NameObject("/Supplement"): NumberObject(0)}),
                        NameObject("/FontDescriptor"): w._add_object(desc), NameObject("/CIDToGIDMap"): NameObject("/Identity"),
                        NameObject("/DW"): NumberObject(1000), NameObject("/W"): larguras})
linhas = ["/CIDInit /ProcSet findresource begin 12 dict begin begincmap /CMapName /Adobe-Identity-UCS def /CMapType 2 def",
          "1 begincodespacerange <0000> <FFFF> endcodespacerange", f"{len(gids)} beginbfchar"]
for ch, g in sorted(gids.items(), key=lambda kv: kv[1]):
    linhas.append(f"<{g:04X}> <{ord(ch):04X}>")
linhas += ["endbfchar endcmap CMapName currentdict /CMap defineresource pop end end"]
tu = DecodedStreamObject()
tu.set_data("\n".join(linhas).encode())
tipo0 = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type0"),
                          NameObject("/BaseFont"): NameObject("/" + nome), NameObject("/Encoding"): NameObject("/Identity-H"),
                          NameObject("/DescendantFonts"): ArrayObject([w._add_object(cid)]),
                          NameObject("/ToUnicode"): w._add_object(tu.flate_encode())})
pg[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): w._add_object(tipo0)})})
hexa = "".join(f"{gids[c]:04X}" for c in texto)
cont = DecodedStreamObject()
cont.set_data(f"BT /F1 54 Tf 20 35 Td <{hexa}> Tj ET".encode())
pg[NameObject("/Contents")] = w._add_object(cont)
with open(saida, "wb") as f:
    w.write(f)
print("ok", saida, len(dados), "bytes de letra")
