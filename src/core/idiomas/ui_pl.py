T = {
    "m_ficheiro": "Plik", "m_ver": "Widok", "m_idioma": "Język", "m_ajuda": "Pomoc",
    "mi_abrir_template": "Otwórz szablon…", "mi_abrir_alg": "Wybierz plik z cyframi…",
    "mi_destino": "Wybierz folder docelowy…", "mi_sair": "Zakończ",
    "mi_zoom_mais": "Powiększ", "mi_zoom_menos": "Pomniejsz", "mi_ajustar": "Dopasuj do okna",
    "mi_expandir": "Powiększ podgląd", "mi_reduzir": "Zmniejsz podgląd",
    "mi_tema": "Motyw", "mi_tema_sistema": "Jak w Windows", "mi_tema_claro": "Jasny", "mi_tema_escuro": "Ciemny",
    "mi_tutorial": "Samouczek krok po kroku", "mi_sobre": "Informacje…",
    "sobre_texto": ("{app}\nWersja {versao}\n\nTworzy numerowane losy loterii w PDF na podstawie szablonu z Canva.\n\n"
                    "Używa bibliotek pypdf, pypdfium2, Pillow i CustomTkinter (licencje permisywne)."),
    "tip_tema": "Przełącz motyw jasny / ciemny",
    "tut_titulo": "Samouczek", "tut_ant": "Wstecz", "tut_seg": "Dalej",
    "tut_t0": "Przegląd",
    "tut_b0": ("Ten program bierze Twój projekt losów z Canva i tworzy gotowe do druku pliki PDF z numerami, "
               "jakie chcesz.\n\n"
               "To tylko 4 kroki, w kolejności widocznej po lewej:\n\n"
               "• 1 – wybierz szablon (PDF z Canva);\n"
               "• 2 – wybierz plik z cyframi od 0 do 9;\n"
               "• 3 – podaj, od którego do którego numeru, i czy chcesz kilka plików PDF, czy jeden;\n"
               "• 4 – wybierz folder i wpisz nazwę plików.\n\n"
               "Potem kliknij „{previa}”, aby zobaczyć stronę, i „{gerar}”. "
               "Na końcu każdy PDF jest sprawdzany automatycznie."),
    "tut_b1": ("W Canva zaprojektuj los i wpisz na każdym losie przykładowe numery 0001, 0002, 0003, … "
               "(po jednym na los). Każdy numer występuje 2 razy: raz na odcinku, raz na głównej części losu "
               "(zobacz obraz).\n\n"
               "Pobierz jako PDF i wybierz ten plik w kroku 1.\n\n"
               "• Program sam wykrywa, ile losów mieści się na stronie, i kierunek tekstu na odcinku.\n"
               "• Numery muszą być tekstem, a nie obrazem.\n"
               "• Inne liczby w projekcie (rok, telefon…) pozostają bez zmian.\n"
               "• Używana jest tylko 1. strona PDF."),
    "tut_b3": ("• {de} / {ate}: pierwszy i ostatni numer do wygenerowania (np. od 1 do 1000).\n"
               "• {algarismos}: ile cyfr zapisać (4 → 0001). Domyślnie tyle, ile w szablonie; jeśli podasz więcej, "
               "numery zostaną pomniejszone, aby się zmieściły.\n"
               "• {varios}: dzieli na pliki z co najwyżej podaną liczbą numerów (wielokrotność liczby losów na "
               "stronie).\n"
               "• {unico}: wszystko w jednym pliku.\n\n"
               "Poniżej widzisz podsumowanie: ile powstanie numerów, plików i stron."),
    "tut_b4": ("Wybierz folder, w którym zapisać pliki PDF, i wpisz nazwę plików (wymagane; program nigdy jej nie "
               "podpowiada). Pliki nazywają się „NAZWA - 0001 - 0300.pdf”, „NAZWA - 0301 - 0600.pdf”, … lub tylko "
               "„NAZWA - 0001 - 1000.pdf” przy jednym PDF.\n\n"
               "Jeśli pliki o takich nazwach już istnieją, program zapyta przed ich zastąpieniem."),
    "tut_t5": "Podgląd i generowanie",
    "tut_b5": ("„{previa}” pokazuje 1. stronę z prawdziwymi numerami, abyś mógł sprawdzić czcionkę, rozmiar i "
               "położenie przed wygenerowaniem wszystkiego.\n\n"
               "W przeglądarce:\n"
               "• − / + lub Ctrl + kółko myszy: powiększenie;\n"
               "• przeciągnij, aby przesunąć; dwuklik lub „{ajustar}”: cały arkusz;\n"
               "• przycisk powiększenia oddaje podglądowi całe okno; kliknij ponownie, aby wrócić;\n"
               "• separator między ustawieniami a przeglądarką też można przeciągać.\n\n"
               "Kliknij „{gerar}”. Pasek pokazuje postęp (można anulować). Na końcu każdy PDF jest sprawdzany "
               "automatycznie (strony i numery) i pojawia się przycisk „{pasta}”."),
    "tut_t6": "Wskazówki i problemy",
    "tut_b6": ("• „Nie znaleziono numerów przykładowych”: w Canva numery muszą być tekstem w formacie 0001, 0002, … "
               "(każdy 2 razy).\n"
               "• Numery wychodzą inną czcionką: plik z cyframi musi używać dokładnie tej samej czcionki co "
               "szablon. Sprawdź w podglądzie.\n"
               "• Numery za małe lub dziwne: przy PNG/JPG użyj dużego obrazu (≥ 100 px wysokości); PDF jest zawsze lepszy.\n"
               "• „Nie udało się zapisać”: zamknij PDF, jeśli jest otwarty w innym programie.\n"
               "• Więcej cyfr niż w projekcie: rozmiar zmniejsza się automatycznie (ostrzeżenie w dzienniku).\n"
               "• Język i motyw (jasny/ciemny) zmienisz w menu; kolory podążają za Windows."),
    'err_folha_varias': 'Na arkuszu można powielać tylko template z jednym losem.',
    'err_rifa_grande': 'Los ({w} × {h} mm) nie mieści się na arkuszu {papel} z marginesami {margem} mm.\n\nWybierz większy papier, zmniejsz margines lub zaprojektuj mniejszy los.',
    'log_folha': 'Arkusz {papel}: {n} losów na arkuszu (po {w} × {h} mm).',
    'aviso_muitas': '⚠ {n} losów na arkuszu: będą bardzo małe i trudne do wycięcia. Sprawdź rozmiar losu.',
    'c1_ok_uma': '✔ Template z 1 losem · numer przykładowy {primeiro}',
    'lay_info': 'Template ma jeden los: program wypełnia arkusz kopiami, tyloma, ile się zmieści.',
    'lay_papel': 'Papier',
    'lay_margem': 'Margines (mm)',
    'lay_por_folha': 'Losów na arkuszu',
    'lay_resultado': 'Los {w} × {h} mm → {n} na arkuszu {papel} (maksimum {max})',
    'lay_recortada': ' · przycięty do projektu',
    'lay_rodadas': ' · {r} obróconych o 90°',
    'lay_acima': 'Na arkuszu mieści się tylko {max}.',
    'conf_muitas': 'Za chwilę powstanie {n} losów na arkuszu (po {w} × {h} mm). To bardzo dużo: będą małe i trudne do wycięcia.\n\nKontynuować?',
    'mi_video': 'Wideo-instrukcja',
    'video_falta': 'Nie znaleziono filmu ({nome}).',
    'tut_t_uma': 'Jeden los w template',
    'tut_b_uma': 'Nie trzeba projektować całego arkusza. W Canva utwórz stronę o rozmiarze jednego losu („Rozmiar niestandardowy”, np. 19 × 5,5 cm) i wpisz tylko jeden numer przykładowy, 0001 (na odcinku i na części głównej albo tylko w jednym miejscu).\n\nPo wybraniu tego PDF program widzi, że jest jeden los, i pokazuje „{papel}”, „{margem}” oraz „{porfolha}”: wypełnia arkusz kopiami losu, tyloma, ile się zmieści (obracając je o 90°, jeśli zmieści się więcej), i numeruje je po kolei. Podgląd pokazuje arkusz tak, jak zostanie wydrukowany.\n\n• Papier (A4, A3, A5, Letter, Legal) i margines (drukarki nie drukują do krawędzi) można zmienić.\n• Jeśli strona PDF jest większa niż los, program przycina narysowany obszar.\n• „{porfolha}” zaczyna od maksimum; można poprosić o mniej.\n• Jeśli mieści się dużo losów (więcej niż 24), program ostrzega: są małe i trudne do wycięcia.\n• Jeśli Twój PDF ma już kilka losów na stronie (0001, 0002, …), wszystko działa jak dotąd.',
    'tut_video': 'Wolisz film? Otwórz menu „{ajuda}” › „{video}”.',
    'limpar': 'Wyczyść wszystko',
    'tut_limpar': 'Po zakończeniu „{limpar}” (lub menu „{ficheiro}” › „{limpar}”) czyści wszystko — template, cyfry, folder, nazwę, numery i podgląd — abyś mógł zacząć kolejną loterię.',
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'Pobierz',
    'web_demasiado_grande': 'Plik jest większy niż limit ({mb} MB).',
    'web_ocupado': 'Trwa już generowanie. Spróbuj ponownie za chwilę.',
    'web_voltar': 'Wstecz',
    'web_ficheiros_gerados': 'Wygenerowane pliki PDF',
    'web_nova_janela': 'Otwórz w nowym oknie',
    'web_tema_auto': 'Automatycznie',
    'web_sessao_expirada': 'Sesja wygasła (lub serwer został uruchomiony ponownie). Wczytaj pliki jeszcze raz.',
    'web_erro_rede': 'Nie można połączyć się z serwerem. Sprawdź połączenie i spróbuj ponownie.',
})
T.update({'web_demasiados': 'Maksymalnie {max} numerów na jedno zlecenie.'})
