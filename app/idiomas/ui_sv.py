T = {
    "m_ficheiro": "Arkiv", "m_ver": "Visa", "m_idioma": "Språk", "m_ajuda": "Hjälp",
    "mi_abrir_template": "Öppna mall…", "mi_abrir_alg": "Välj siffrofil…",
    "mi_destino": "Välj målmapp…", "mi_sair": "Avsluta",
    "mi_zoom_mais": "Zooma in", "mi_zoom_menos": "Zooma ut", "mi_ajustar": "Anpassa till fönstret",
    "mi_expandir": "Utöka förhandsgranskningen", "mi_reduzir": "Förminska förhandsgranskningen",
    "mi_tema": "Tema", "mi_tema_sistema": "Som Windows", "mi_tema_claro": "Ljust", "mi_tema_escuro": "Mörkt",
    "mi_tutorial": "Steg-för-steg-guide", "mi_sobre": "Om…",
    "sobre_texto": ("{app}\nVersion {versao}\n\nSkapar numrerade lotter som PDF från en Canva-mall.\n\n"
                    "Använder pypdf, pypdfium2, Pillow och CustomTkinter (fria licenser)."),
    "tip_tema": "Växla mellan ljust och mörkt tema",
    "tut_titulo": "Guide", "tut_ant": "Föregående", "tut_seg": "Nästa",
    "tut_t0": "Översikt",
    "tut_b0": ("Programmet tar din lottdesign från Canva och skapar utskriftsklara PDF-filer med de nummer du "
               "vill ha.\n\n"
               "Det är bara 4 steg, i den ordning som visas till vänster:\n\n"
               "• 1 – välj mallen (PDF-filen från Canva);\n"
               "• 2 – välj filen med siffrorna 0 till 9;\n"
               "• 3 – ange från vilket nummer till vilket, och om du vill ha flera PDF-filer eller en;\n"
               "• 4 – välj mapp och skriv filnamnet.\n\n"
               "Klicka sedan på ”{previa}” för att se en sida och på ”{gerar}”. "
               "Till sist kontrolleras varje PDF automatiskt."),
    "tut_b1": ("Designa lotten i Canva och skriv exempelnumren 0001, 0002, 0003, … på lotterna (ett per lott). "
               "Varje nummer förekommer 2 gånger: en gång på talongen och en gång på lottens huvuddel "
               "(se bilden).\n\n"
               "Ladda ner som PDF och välj filen i steg 1.\n\n"
               "• Programmet upptäcker själv hur många lotter det är per sida och riktningen på talongens text.\n"
               "• Numren måste vara text, inte en bild.\n"
               "• Andra siffror i designen (år, telefon …) lämnas orörda.\n"
               "• Bara PDF-filens första sida används."),
    "tut_b3": ("• {de} / {ate}: det första och sista numret som ska skapas (till exempel 1 till 1000).\n"
               "• {algarismos}: hur många siffror som skrivs (4 → 0001). Som standard samma som i mallen; "
               "begär du fler krymper numren så att de ryms.\n"
               "• {varios}: delar upp i filer med högst det antal nummer du anger (en multipel av lotter per sida).\n"
               "• {unico}: allt i en fil.\n\n"
               "Nedanför ser du sammanfattningen: hur många nummer, filer och sidor som skapas."),
    "tut_b4": ("Välj mappen där PDF-filerna sparas och skriv filnamnet (obligatoriskt; programmet föreslår aldrig "
               "något). Filerna heter ”NAMN - 0001 - 0300.pdf”, ”NAMN - 0301 - 0600.pdf”, … eller bara "
               "”NAMN - 0001 - 1000.pdf” med en enda PDF.\n\n"
               "Om filer med de namnen redan finns frågar programmet innan de ersätts."),
    "tut_t5": "Förhandsgranska och skapa",
    "tut_b5": ("”{previa}” visar sida 1 med riktiga nummer så att du kan kontrollera typsnitt, storlek och "
               "placering innan allt skapas.\n\n"
               "I visaren:\n"
               "• − / + eller Ctrl + mushjul: zoom;\n"
               "• dra för att flytta; dubbelklicka eller ”{ajustar}”: se hela arket;\n"
               "• utökningsknappen ger hela fönstret åt förhandsgranskningen; klicka igen för att gå tillbaka;\n"
               "• avdelaren mellan inställningarna och visaren kan också dras.\n\n"
               "Klicka på ”{gerar}”. Fältet visar förloppet (du kan avbryta). Till sist kontrolleras varje PDF "
               "automatiskt (sidor och nummer) och knappen ”{pasta}” visas."),
    "tut_t6": "Tips och problem",
    "tut_b6": ("• ”Hittade inte exempelnumren”: i Canva måste numren vara text i formatet 0001, 0002, … "
               "(vart och ett 2 gånger).\n"
               "• Numren får ett annat typsnitt: siffrofilen måste använda exakt samma typsnitt som mallen. "
               "Kontrollera i förhandsgranskningen.\n"
               "• Nummer för små eller konstiga: använd en stor bild vid PNG/JPG (≥ 100 px hög); PDF är alltid bättre.\n"
               "• ”Kunde inte spara”: stäng PDF-filen om den är öppen i ett annat program.\n"
               "• Fler siffror än designen: storleken minskas automatiskt (varning i loggen).\n"
               "• Språk och tema (ljust/mörkt) ändrar du i menyerna; färgerna följer Windows."),
    'err_folha_varias': 'Bara en mall med en enda lott kan upprepas på arket.',
    'err_rifa_grande': 'Lotten ({w} × {h} mm) ryms inte på ett {papel}-ark med {margem} mm marginal.\n\nVälj större papper, minska marginalen eller gör lotten mindre.',
    'log_folha': '{papel}-ark: {n} lotter per ark ({w} × {h} mm styck).',
    'aviso_muitas': '⚠ {n} lotter per ark: de blir mycket små och svåra att klippa ut. Kontrollera lottens storlek.',
    'c1_ok_uma': '✔ Mall med 1 lott · exempelnummer {primeiro}',
    'lay_info': 'Mallen har en enda lott: programmet fyller arket med kopior, så många som ryms.',
    'lay_papel': 'Papper',
    'lay_margem': 'Marginal (mm)',
    'lay_por_folha': 'Lotter per ark',
    'lay_resultado': 'Lott på {w} × {h} mm → {n} per {papel}-ark (max {max})',
    'lay_recortada': ' · beskuren till motivet',
    'lay_rodadas': ' · {r} vridna 90°',
    'lay_acima': 'Det ryms bara {max} per ark.',
    'conf_muitas': 'Du ska skapa {n} lotter per ark ({w} × {h} mm styck). Det är mycket: de blir små och svåra att klippa ut.\n\nFortsätta?',
    'mi_video': 'Videohandledning',
    'video_falta': 'Hittade inte videon ({nome}).',
    'tut_t_uma': 'En enda lott i mallen',
    'tut_b_uma': 'Du behöver inte rita hela arket. Skapa i Canva en sida lika stor som en lott („Anpassad storlek”, till exempel 19 × 5,5 cm) och skriv bara ett exempelnummer, 0001 (på talongen och på huvuddelen, eller bara på ett ställe).\n\nNär du väljer den PDF:en ser programmet att det finns en enda lott och visar ”{papel}”, ”{margem}” och ”{porfolha}”: det fyller arket med kopior av lotten, så många som ryms (vridna 90° om det ryms fler), och numrerar dem i ordning. Förhandsgranskningen visar arket som det skrivs ut.\n\n• Papperet (A4, A3, A5, Letter, Legal) och marginalen (skrivare skriver inte ända ut till kanten) kan ändras.\n• Om PDF-sidan är större än lotten beskär programmet det ritade området.\n• ”{porfolha}” börjar på max; du kan välja färre.\n• Om många lotter ryms (fler än 24) varnar programmet: de blir små och svåra att klippa ut.\n• Om din PDF redan har flera lotter per sida (0001, 0002, …) fungerar allt som förut.',
    'tut_video': 'Hellre video? Öppna menyn ”{ajuda}” › ”{video}”.',
    'limpar': 'Rensa allt',
    'tut_limpar': 'När det är klart återställer ”{limpar}” (eller menyn ”{ficheiro}” › ”{limpar}”) allt — mall, siffror, mapp, namn, nummer och förhandsgranskning — så att du kan börja på en ny lottdragning.',
}
