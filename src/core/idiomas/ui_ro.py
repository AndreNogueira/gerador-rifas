T = {
    "m_ficheiro": "Fișier", "m_ver": "Vizualizare", "m_idioma": "Limbă", "m_ajuda": "Ajutor",
    "mi_abrir_template": "Deschide șablonul…", "mi_abrir_alg": "Alege fișierul cu cifre…",
    "mi_destino": "Alege folderul de destinație…", "mi_sair": "Ieșire",
    "mi_zoom_mais": "Mărește", "mi_zoom_menos": "Micșorează", "mi_ajustar": "Potrivește în fereastră",
    "mi_expandir": "Extinde previzualizarea", "mi_reduzir": "Redu previzualizarea",
    "mi_tema": "Temă", "mi_tema_sistema": "Ca în Windows", "mi_tema_claro": "Luminoasă", "mi_tema_escuro": "Întunecată",
    "mi_tutorial": "Tutorial pas cu pas", "mi_sobre": "Despre…",
    "sobre_texto": ("{app}\nVersiunea {versao}\n\nCreează PDF-uri cu bilete de tombolă numerotate dintr-un șablon Canva.\n\n"
                    "Folosește bibliotecile pypdf, pypdfium2, Pillow și CustomTkinter (licențe permisive)."),
    "tip_tema": "Comută între tema luminoasă și cea întunecată",
    "tut_titulo": "Tutorial", "tut_ant": "Înapoi", "tut_seg": "Înainte",
    "tut_t0": "Prezentare generală",
    "tut_b0": ("Acest program preia desenul tombolei făcut în Canva și creează PDF-uri gata de tipărit, cu numerele "
               "dorite.\n\n"
               "Sunt doar 4 pași, în ordinea afișată în stânga:\n\n"
               "• 1 – alege șablonul (PDF-ul din Canva);\n"
               "• 2 – alege fișierul cu cifrele de la 0 la 9;\n"
               "• 3 – spune de la ce număr până la ce număr și dacă vrei mai multe PDF-uri sau unul singur;\n"
               "• 4 – alege folderul și scrie numele fișierelor.\n\n"
               "Apoi apasă „{previa}” ca să vezi o pagină și „{gerar}”. "
               "La final, fiecare PDF este verificat automat."),
    "tut_b1": ("În Canva, desenează tombola și scrie pe fiecare bilet numerele exemplu 0001, 0002, 0003, … "
               "(câte unul pe bilet). Fiecare număr apare de 2 ori: o dată pe taloane și o dată pe partea "
               "principală a biletului (vezi imaginea).\n\n"
               "Descarcă-l ca PDF și alege acel fișier la pasul 1.\n\n"
               "• Programul detectează singur câte bilete sunt pe pagină și orientarea textului de pe talon.\n"
               "• Numerele trebuie să fie text, nu imagine.\n"
               "• Alte numere din desen (an, telefon…) rămân neschimbate.\n"
               "• Se folosește doar prima pagină a PDF-ului."),
    "tut_b3": ("• {de} / {ate}: primul și ultimul număr de generat (de exemplu de la 1 la 1000).\n"
               "• {algarismos}: câte cifre să se scrie (4 → 0001). Implicit este cel din șablon; "
               "dacă ceri mai multe, numerele se micșorează ca să încapă.\n"
               "• {varios}: împarte în fișiere cu cel mult numărul de numere indicat (multiplu al biletelor pe pagină).\n"
               "• {unico}: totul într-un singur fișier.\n\n"
               "Jos vezi rezumatul: câte numere, fișiere și pagini vor fi create."),
    "tut_b4": ("Alege folderul în care se salvează PDF-urile și scrie numele fișierelor (obligatoriu; programul nu "
               "propune niciodată unul). Fișierele se numesc „NUME - 0001 - 0300.pdf”, „NUME - 0301 - 0600.pdf”, … "
               "sau doar „NUME - 0001 - 1000.pdf” la un singur PDF.\n\n"
               "Dacă există deja fișiere cu aceste nume, programul întreabă înainte să le înlocuiască."),
    "tut_t5": "Previzualizare și generare",
    "tut_b5": ("„{previa}” arată prima pagină cu numere reale, ca să verifici fontul, mărimea și poziția înainte de "
               "a genera totul.\n\n"
               "În vizualizator:\n"
               "• − / + sau Ctrl + rotița mouse-ului: zoom;\n"
               "• trage pentru a muta; dublu clic sau „{ajustar}”: vezi toată foaia;\n"
               "• butonul de extindere dă toată fereastra previzualizării; apasă din nou pentru a reveni;\n"
               "• și separatorul dintre setări și vizualizator poate fi tras.\n\n"
               "Apasă „{gerar}”. Bara arată progresul (poți anula). La final, fiecare PDF este verificat automat "
               "(pagini și numere) și apare butonul „{pasta}”."),
    "tut_t6": "Sfaturi și probleme",
    "tut_b6": ("• „Nu am găsit numerele exemplu”: în Canva numerele trebuie să fie text, în formatul 0001, 0002, … "
               "(fiecare de 2 ori).\n"
               "• Numerele ies cu alt font: fișierul cu cifre trebuie să folosească exact același font ca șablonul. "
               "Verifică în previzualizare.\n"
               "• Numere prea mici sau ciudate: la PNG/JPG folosește o imagine mare (≥ 100 px înălțime); PDF este mereu mai bun.\n"
               "• „Nu am putut salva”: închide PDF-ul dacă este deschis în alt program.\n"
               "• Mai multe cifre decât desenul: mărimea se reduce automat (avertisment în jurnal).\n"
               "• Poți schimba limba și tema (luminoasă/întunecată) din meniuri; culorile urmează Windows."),
    'err_folha_varias': 'Pe foaie se poate repeta doar un șablon cu un singur bilet.',
    'err_rifa_grande': 'Biletul ({w} × {h} mm) nu încape pe o foaie {papel} cu margini de {margem} mm.\n\nAlegeți o hârtie mai mare, micșorați marginea sau desenați un bilet mai mic.',
    'log_folha': 'Foaie {papel}: {n} bilete pe foaie ({w} × {h} mm fiecare).',
    'aviso_muitas': '⚠ {n} bilete pe foaie: vor fi foarte mici și greu de tăiat. Verificați dimensiunea biletului.',
    'c1_ok_uma': '✔ Șablon cu 1 bilet · număr-exemplu {primeiro}',
    'lay_info': 'Șablonul are un singur bilet: programul umple foaia cu copii, câte încap.',
    'lay_papel': 'Hârtie',
    'lay_margem': 'Margine (mm)',
    'lay_por_folha': 'Bilete pe foaie',
    'lay_resultado': 'Bilet de {w} × {h} mm → {n} pe foaie {papel} (maxim {max})',
    'lay_recortada': ' · tăiat după desen',
    'lay_rodadas': ' · {r} rotite 90°',
    'lay_acima': 'Pe o foaie încap doar {max}.',
    'conf_muitas': 'Urmează să generați {n} bilete pe foaie ({w} × {h} mm fiecare). Este mult: vor fi mici și greu de tăiat.\n\nContinuați?',
    'mi_video': 'Tutorial video',
    'video_falta': 'Nu am găsit videoclipul ({nome}).',
    'tut_t_uma': 'Un singur bilet în șablon',
    'tut_b_uma': 'Nu trebuie să desenați toată foaia. În Canva, creați o pagină cât un bilet („Dimensiune personalizată”, de exemplu 19 × 5,5 cm) și scrieți un singur număr-exemplu, 0001 (pe taloane și pe partea principală, sau doar într-un loc).\n\nCând alegeți acel PDF, programul vede că e un singur bilet și afișează „{papel}”, „{margem}” și „{porfolha}”: umple foaia cu copii ale biletului, câte încap (rotindu-le 90° dacă așa încap mai multe), și le numerotează în ordine. Previzualizarea arată foaia așa cum va fi tipărită.\n\n• Hârtia (A4, A3, A5, Letter, Legal) și marginea (imprimantele nu tipăresc până la margine) se pot schimba.\n• Dacă pagina PDF e mai mare decât biletul, programul decupează zona desenată.\n• „{porfolha}” începe de la maxim; puteți cere mai puține.\n• Dacă încap multe bilete (peste 24), programul avertizează: sunt mici și greu de tăiat.\n• Dacă PDF-ul dvs. are deja mai multe bilete pe pagină (0001, 0002, …), totul funcționează ca înainte.',
    'tut_video': 'Preferați un video? Deschideți meniul „{ajuda}” › „{video}”.',
    'limpar': 'Șterge tot',
    'tut_limpar': 'La final, „{limpar}” (sau meniul „{ficheiro}” › „{limpar}”) șterge tot — șablonul, cifrele, dosarul, numele, numerele și previzualizarea — ca să puteți începe o altă tombolă.',
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'Descarcă',
    'web_demasiado_grande': 'Fișierul depășește limita ({mb} MB).',
    'web_ocupado': 'O generare este deja în curs. Încercați din nou peste puțin timp.',
    'web_voltar': 'Înapoi',
    'web_ficheiros_gerados': 'PDF-uri generate',
    'web_nova_janela': 'Deschide într-o fereastră nouă',
    'web_tema_auto': 'Automat',
    'web_sessao_expirada': 'Sesiunea a expirat (sau serverul a fost repornit). Încarcă din nou fișierele.',
    'web_erro_rede': 'Nu s-a putut contacta serverul. Verifică conexiunea și încearcă din nou.',
    'web_visual': 'Stil',
})
T.update({'web_demasiados': 'Cel mult {max} de numere per cerere.'})
