T = {
    "m_ficheiro": "Bestand", "m_ver": "Beeld", "m_idioma": "Taal", "m_ajuda": "Help",
    "mi_abrir_template": "Sjabloon openen…", "mi_abrir_alg": "Cijferbestand kiezen…",
    "mi_destino": "Doelmap kiezen…", "mi_sair": "Afsluiten",
    "mi_zoom_mais": "Inzoomen", "mi_zoom_menos": "Uitzoomen", "mi_ajustar": "Aan venster aanpassen",
    "mi_expandir": "Voorbeeld uitbreiden", "mi_reduzir": "Voorbeeld verkleinen",
    "mi_tema": "Thema", "mi_tema_sistema": "Zoals Windows", "mi_tema_claro": "Licht", "mi_tema_escuro": "Donker",
    "mi_tutorial": "Stapsgewijze handleiding", "mi_sobre": "Info…",
    "sobre_texto": ("{app}\nVersie {versao}\n\nMaakt genummerde loten als PDF op basis van een Canva-sjabloon.\n\n"
                    "Gebruikt pypdf, pypdfium2, Pillow en CustomTkinter (ruime licenties)."),
    "tip_tema": "Wisselen tussen licht en donker thema",
    "tut_titulo": "Handleiding", "tut_ant": "Vorige", "tut_seg": "Volgende",
    "tut_t0": "Overzicht",
    "tut_b0": ("Dit programma neemt jouw lotenontwerp uit Canva en maakt afdrukklare PDF’s met de nummers die je "
               "wilt.\n\n"
               "Het zijn maar 4 stappen, in de volgorde links:\n\n"
               "• 1 – kies het sjabloon (de PDF uit Canva);\n"
               "• 2 – kies het bestand met de cijfers 0 tot 9;\n"
               "• 3 – geef aan van welk nummer tot welk nummer, en of je meerdere PDF’s of één wilt;\n"
               "• 4 – kies de map en typ de naam van de bestanden.\n\n"
               "Klik daarna op “{previa}” om een pagina te zien en op “{gerar}”. "
               "Aan het eind wordt elke PDF automatisch gecontroleerd."),
    "tut_b1": ("Ontwerp het lot in Canva en schrijf op elk lot de voorbeeldnummers 0001, 0002, 0003, … "
               "(één per lot). Elk nummer komt 2 keer voor: één keer op het controlestrookje en één keer op het "
               "hoofddeel van het lot (zie de afbeelding).\n\n"
               "Download het als PDF en kies dat bestand bij stap 1.\n\n"
               "• Het programma ziet zelf hoeveel loten er per pagina zijn en de richting van de tekst op het strookje.\n"
               "• De nummers moeten tekst zijn, geen afbeelding.\n"
               "• Andere getallen in het ontwerp (jaar, telefoon…) blijven ongewijzigd.\n"
               "• Alleen de 1e pagina van de PDF wordt gebruikt."),
    "tut_b3": ("• {de} / {ate}: het eerste en laatste nummer dat wordt gemaakt (bijvoorbeeld 1 tot 1000).\n"
               "• {algarismos}: met hoeveel cijfers wordt geschreven (4 → 0001). Standaard is dat het aantal uit het "
               "sjabloon; vraag je meer, dan worden de nummers kleiner zodat ze passen.\n"
               "• {varios}: splitst in bestanden met hooguit het aantal opgegeven nummers (een veelvoud van het "
               "aantal loten per pagina).\n"
               "• {unico}: alles in één bestand.\n\n"
               "Onderaan zie je de samenvatting: hoeveel nummers, bestanden en pagina’s er komen."),
    "tut_b4": ("Kies de map waarin de PDF’s worden opgeslagen en typ de naam van de bestanden (verplicht; het "
               "programma stelt nooit een naam voor). De bestanden heten “NAAM - 0001 - 0300.pdf”, "
               "“NAAM - 0301 - 0600.pdf”, … of alleen “NAAM - 0001 - 1000.pdf” bij één PDF.\n\n"
               "Bestaan er al bestanden met die namen, dan vraagt het programma eerst of ze vervangen mogen worden."),
    "tut_t5": "Voorbeeld en maken",
    "tut_b5": ("“{previa}” toont de 1e pagina met echte nummers, zodat je lettertype, grootte en positie kunt "
               "controleren voordat alles wordt gemaakt.\n\n"
               "In de viewer:\n"
               "• − / + of Ctrl + muiswiel: zoomen;\n"
               "• sleep om te verschuiven; dubbelklik of “{ajustar}”: het hele vel zien;\n"
               "• de uitbreidknop geeft het hele venster aan het voorbeeld; klik nogmaals om terug te gaan;\n"
               "• ook de scheidingslijn tussen instellingen en viewer kun je slepen.\n\n"
               "Klik op “{gerar}”. De balk toont de voortgang (annuleren kan). Aan het eind wordt elke PDF "
               "automatisch gecontroleerd (pagina’s en nummers) en verschijnt de knop “{pasta}”."),
    "tut_t6": "Tips en problemen",
    "tut_b6": ("• “Voorbeeldnummers niet gevonden”: in Canva moeten de nummers tekst zijn, in de vorm 0001, 0002, … "
               "(elk 2 keer).\n"
               "• De nummers komen in een ander lettertype: het cijferbestand moet precies hetzelfde lettertype "
               "gebruiken als het sjabloon. Controleer het in het voorbeeld.\n"
               "• Nummers te klein of vreemd: gebruik bij PNG/JPG een grote afbeelding (≥ 100 px hoog); PDF is altijd beter.\n"
               "• “Opslaan mislukt”: sluit de PDF als die in een ander programma openstaat.\n"
               "• Meer cijfers dan het ontwerp: de grootte wordt automatisch verkleind (melding in het logboek).\n"
               "• Taal en thema (licht/donker) wijzig je in de menu’s; de kleuren volgen Windows."),
    'err_folha_varias': 'Alleen een template met één los kan op het vel worden herhaald.',
    'err_rifa_grande': 'Het lot ({w} × {h} mm) past niet op een {papel}-vel met {margem} mm marge.\n\nKies groter papier, verklein de marge of ontwerp een kleiner lot.',
    'log_folha': '{papel}-vel: {n} loten per vel (elk {w} × {h} mm).',
    'aviso_muitas': '⚠ {n} loten per vel: ze worden erg klein en lastig uit te knippen. Controleer het formaat van het lot.',
    'c1_ok_uma': '✔ Template met 1 lot · voorbeeldnummer {primeiro}',
    'lay_info': 'De template heeft één lot: het programma vult het vel met kopieën, zoveel als er passen.',
    'lay_papel': 'Papier',
    'lay_margem': 'Marge (mm)',
    'lay_por_folha': 'Loten per vel',
    'lay_resultado': 'Lot van {w} × {h} mm → {n} per {papel}-vel (maximum {max})',
    'lay_recortada': ' · bijgesneden op het ontwerp',
    'lay_rodadas': ' · {r} 90° gedraaid',
    'lay_acima': 'Er passen maar {max} op een vel.',
    'conf_muitas': 'U gaat {n} loten per vel maken (elk {w} × {h} mm). Dat is veel: ze worden klein en lastig uit te knippen.\n\nDoorgaan?',
    'mi_video': 'Videohandleiding',
    'video_falta': 'Ik kon de video niet vinden ({nome}).',
    'tut_t_uma': 'Eén los in de template',
    'tut_b_uma': 'U hoeft niet het hele vel te ontwerpen. Maak in Canva een pagina met het formaat van één lot (‘Aangepast formaat’, bijvoorbeeld 19 × 5,5 cm) en schrijf slechts één voorbeeldnummer, 0001 (op de strook en op het hoofddeel, of op één plek).\n\nAls u die pdf kiest, ziet het programma dat er één lot is en toont ‘{papel}’, ‘{margem}’ en ‘{porfolha}’: het vult het vel met kopieën van het lot, zoveel als er passen (90° gedraaid als er dan meer passen), en nummert ze op volgorde. Het voorbeeld toont het vel zoals het wordt afgedrukt.\n\n• Het papier (A4, A3, A5, Letter, Legal) en de marge (printers printen niet tot de rand) kunnen worden gewijzigd.\n• Is de pdf-pagina groter dan het lot, dan snijdt het programma het getekende gebied bij.\n• ‘{porfolha}’ begint bij het maximum; u kunt minder vragen.\n• Passen er veel loten (meer dan 24), dan waarschuwt het programma: ze zijn klein en lastig uit te knippen.\n• Heeft uw pdf al meerdere loten per pagina (0001, 0002, …), dan werkt alles zoals voorheen.',
    'tut_video': 'Liever een video? Open het menu ‘{ajuda}’ › ‘{video}’.',
    'limpar': 'Alles wissen',
    'tut_limpar': 'Als alles klaar is, zet ‘{limpar}’ (of menu ‘{ficheiro}’ › ‘{limpar}’) alles terug — template, cijfers, map, naam, nummers en voorbeeld — zodat u een nieuwe loterij kunt beginnen.',
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'Downloaden',
    'web_senha': 'Wachtwoord',
    'web_entrar': 'Aanmelden',
    'web_senha_errada': 'Onjuist wachtwoord.',
    'web_demasiado_grande': 'Het bestand is groter dan de limiet ({mb} MB).',
    'web_ocupado': 'Er is al een generatie bezig. Probeer het zo opnieuw.',
    'web_voltar': 'Terug',
    'web_ficheiros_gerados': "Gegenereerde pdf's",
    'web_nova_janela': 'Openen in een nieuw venster',
    'web_tema_auto': 'Automatisch',
})
T.update({'web_demasiados': 'Maximaal {max} nummers per opdracht.'})
