"""Textos da interface e das mensagens, uma lingua por ficheiro (cada um define NOME e T).

Cada lingua tem dois ficheiros: <codigo>.py (mensagens e passos) e ui_<codigo>.py (menus e tutorial);
os dois dicionarios juntam-se em TEXTOS[<codigo>].
Para acrescentar uma lingua: copiar pt.py e ui_pt.py, traduzir, e juntar o codigo a ORDEM e aos imports abaixo.
"""
from . import cs, de, el, en, es, fr, hi, it, ja, ko, nl, pl, pt, ro, ru, sv, textos_novos, tr, tutoriais, web_extra, zh
from . import (ui_cs, ui_de, ui_el, ui_en, ui_es, ui_fr, ui_hi, ui_it, ui_ja, ui_ko, ui_nl, ui_pl, ui_pt, ui_ro,
               ui_ru, ui_sv, ui_tr, ui_zh)

ORDEM = ["pt", "en", "es", "fr", "de", "it", "nl", "pl", "sv", "cs", "ro", "el", "ru", "tr", "zh", "ja", "ko", "hi"]
_MODULOS = {"pt": pt, "en": en, "es": es, "fr": fr, "de": de, "it": it, "nl": nl, "pl": pl, "sv": sv, "cs": cs,
            "ro": ro, "el": el, "ru": ru, "tr": tr, "zh": zh, "ja": ja, "ko": ko, "hi": hi}
_UI = {"pt": ui_pt, "en": ui_en, "es": ui_es, "fr": ui_fr, "de": ui_de, "it": ui_it, "nl": ui_nl, "pl": ui_pl,
       "sv": ui_sv, "cs": ui_cs, "ro": ui_ro, "el": ui_el, "ru": ui_ru, "tr": ui_tr, "zh": ui_zh, "ja": ui_ja,
       "ko": ui_ko, "hi": ui_hi}
NOMES = {c: _MODULOS[c].NOME for c in ORDEM}
TEXTOS = {c: {**_MODULOS[c].T, **_UI[c].T, **web_extra.para(c), **textos_novos.para(c), **tutoriais.para(c)} for c in ORDEM}
