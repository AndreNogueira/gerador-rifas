T = {
    "m_ficheiro": "Soubor", "m_ver": "Zobrazení", "m_idioma": "Jazyk", "m_ajuda": "Nápověda",
    "mi_abrir_template": "Otevřít šablonu…", "mi_abrir_alg": "Vybrat soubor s číslicemi…",
    "mi_destino": "Vybrat cílovou složku…", "mi_sair": "Konec",
    "mi_zoom_mais": "Přiblížit", "mi_zoom_menos": "Oddálit", "mi_ajustar": "Přizpůsobit oknu",
    "mi_expandir": "Zvětšit náhled", "mi_reduzir": "Zmenšit náhled",
    "mi_tema": "Motiv", "mi_tema_sistema": "Jako Windows", "mi_tema_claro": "Světlý", "mi_tema_escuro": "Tmavý",
    "mi_tutorial": "Návod krok za krokem", "mi_sobre": "O programu…",
    "sobre_texto": ("{app}\nVerze {versao}\n\nVytváří číslované losy ve formátu PDF ze šablony z Canvy.\n\n"
                    "Používá knihovny pypdf, pypdfium2, Pillow a CustomTkinter (volné licence)."),
    "tip_tema": "Přepnout světlý / tmavý motiv",
    "tut_titulo": "Návod", "tut_ant": "Zpět", "tut_seg": "Další",
    "tut_t0": "Přehled",
    "tut_b0": ("Program vezme váš návrh losů z Canvy a vytvoří PDF připravená k tisku s čísly, která chcete.\n\n"
               "Jsou to jen 4 kroky, v pořadí zleva:\n\n"
               "• 1 – vyberte šablonu (PDF z Canvy);\n"
               "• 2 – vyberte soubor s číslicemi 0 až 9;\n"
               "• 3 – zadejte, od kterého do kterého čísla, a zda chcete více PDF, nebo jedno;\n"
               "• 4 – vyberte složku a napište název souborů.\n\n"
               "Pak klikněte na „{previa}“ pro zobrazení stránky a na „{gerar}“. "
               "Na konci se každé PDF automaticky zkontroluje."),
    "tut_b1": ("V Canvě navrhněte los a na každý los napište ukázková čísla 0001, 0002, 0003, … "
               "(jedno na los). Každé číslo se objeví 2×: jednou na útržku a jednou na hlavní části losu "
               "(viz obrázek).\n\n"
               "Stáhněte jako PDF a v kroku 1 vyberte tento soubor.\n\n"
               "• Program sám pozná, kolik losů je na stránce a jak je otočený text na útržku.\n"
               "• Čísla musí být text, ne obrázek.\n"
               "• Ostatní čísla v návrhu (rok, telefon…) zůstanou beze změny.\n"
               "• Používá se jen 1. stránka PDF."),
    "tut_b3": ("• {de} / {ate}: první a poslední číslo k vytvoření (např. 1 až 1000).\n"
               "• {algarismos}: kolika číslicemi psát (4 → 0001). Výchozí je hodnota ze šablony; "
               "pokud zadáte víc, čísla se zmenší, aby se vešla.\n"
               "• {varios}: rozdělí na soubory s nejvýše zadaným počtem čísel (násobek počtu losů na stránce).\n"
               "• {unico}: vše v jednom souboru.\n\n"
               "Dole vidíte souhrn: kolik čísel, souborů a stránek vznikne."),
    "tut_b4": ("Vyberte složku, kam se PDF uloží, a napište název souborů (povinné; program žádný nenavrhuje). "
               "Soubory se jmenují „NÁZEV - 0001 - 0300.pdf“, „NÁZEV - 0301 - 0600.pdf“, … nebo jen "
               "„NÁZEV - 0001 - 1000.pdf“ u jediného PDF.\n\n"
               "Pokud soubory s těmito názvy už existují, program se před nahrazením zeptá."),
    "tut_t5": "Náhled a vytvoření",
    "tut_b5": ("„{previa}“ ukáže 1. stránku se skutečnými čísly, abyste před vytvořením všeho zkontrolovali písmo, "
               "velikost a polohu.\n\n"
               "V prohlížeči:\n"
               "• − / + nebo Ctrl + kolečko myši: zoom;\n"
               "• tažením posouváte; dvojklik nebo „{ajustar}“: celý list;\n"
               "• tlačítko zvětšení dá náhledu celé okno; dalším kliknutím se vrátíte;\n"
               "• dělicí lištu mezi nastavením a prohlížečem lze také táhnout.\n\n"
               "Klikněte na „{gerar}“. Ukazatel zobrazuje průběh (lze zrušit). Na konci se každé PDF automaticky "
               "zkontroluje (stránky a čísla) a objeví se tlačítko „{pasta}“."),
    "tut_t6": "Tipy a problémy",
    "tut_b6": ("• „Nenašel jsem ukázková čísla“: v Canvě musí být čísla text ve tvaru 0001, 0002, … "
               "(každé 2×).\n"
               "• Čísla mají jiné písmo: soubor s číslicemi musí používat přesně stejné písmo jako šablona. "
               "Zkontrolujte v náhledu.\n"
               "• Čísla příliš malá nebo divná: u PNG/JPG použijte velký obrázek (≥ 100 px na výšku); PDF je vždy lepší.\n"
               "• „Nepodařilo se uložit“: zavřete PDF, pokud je otevřené v jiném programu.\n"
               "• Víc číslic než v návrhu: velikost se automaticky zmenší (upozornění v záznamu).\n"
               "• Jazyk a motiv (světlý/tmavý) změníte v nabídkách; barvy sledují Windows."),
    'err_folha_varias': 'Na list lze opakovat jen šablonu s jediným losem.',
    'err_rifa_grande': 'Los ({w} × {h} mm) se nevejde na list {papel} s okraji {margem} mm.\n\nZvolte větší papír, zmenšete okraj nebo navrhněte menší los.',
    'log_folha': 'List {papel}: {n} losů na list (každý {w} × {h} mm).',
    'aviso_muitas': '⚠ {n} losů na list: budou velmi malé a těžko se vystřihují. Zkontrolujte velikost losu.',
    'c1_ok_uma': '✔ Šablona s 1 losem · vzorové číslo {primeiro}',
    'lay_info': 'Šablona obsahuje jediný los: program zaplní list kopiemi, kolik se jich vejde.',
    'lay_papel': 'Papír',
    'lay_margem': 'Okraj (mm)',
    'lay_por_folha': 'Losů na list',
    'lay_resultado': 'Los {w} × {h} mm → {n} na list {papel} (maximum {max})',
    'lay_recortada': ' · oříznutý podle návrhu',
    'lay_rodadas': ' · {r} otočených o 90°',
    'lay_acima': 'Na list se vejde jen {max}.',
    'conf_muitas': 'Chystáte se vytvořit {n} losů na list (každý {w} × {h} mm). To je hodně: budou malé a těžko se vystřihují.\n\nPokračovat?',
    'mi_video': 'Video návod',
    'video_falta': 'Video se nepodařilo najít ({nome}).',
    'tut_t_uma': 'Jediný los v šabloně',
    'tut_b_uma': 'Nemusíte navrhovat celý list. V Canvě vytvořte stránku velikosti jednoho losu („Vlastní rozměr“, například 19 × 5,5 cm) a napište jen jedno vzorové číslo, 0001 (na útržku i na hlavní části, nebo jen na jednom místě).\n\nKdyž vyberete toto PDF, program zjistí, že je tam jediný los, a zobrazí „{papel}“, „{margem}“ a „{porfolha}“: zaplní list kopiemi losu, kolik se jich vejde (otočí je o 90°, vejde-li se tak víc), a očísluje je popořadě. Náhled ukazuje list tak, jak se vytiskne.\n\n• Papír (A4, A3, A5, Letter, Legal) a okraj (tiskárny netisknou až po kraj) lze změnit.\n• Je-li stránka PDF větší než los, program ořízne nakreslenou oblast.\n• „{porfolha}“ začíná na maximu; můžete chtít méně.\n• Vejde-li se mnoho losů (více než 24), program upozorní: jsou malé a těžko se vystřihují.\n• Má-li vaše PDF už několik losů na stránce (0001, 0002, …), vše funguje jako dřív.',
    'tut_video': 'Raději video? Otevřete nabídku „{ajuda}“ › „{video}“.',
    'limpar': 'Vymazat vše',
    'tut_limpar': 'Po dokončení „{limpar}“ (nebo nabídka „{ficheiro}“ › „{limpar}“) vše vyčistí — šablonu, číslice, složku, název, čísla i náhled — a můžete začít další tombolu.',
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'Stáhnout',
    'web_demasiado_grande': 'Soubor je větší než limit ({mb} MB).',
    'web_ocupado': 'Generování již probíhá. Zkuste to za chvíli znovu.',
    'web_voltar': 'Zpět',
    'web_ficheiros_gerados': 'Vygenerované PDF',
    'web_nova_janela': 'Otevřít v novém okně',
    'web_tema_auto': 'Automaticky',
    'web_sessao_expirada': 'Relace vypršela (nebo se server restartoval). Nahrajte soubory znovu.',
    'web_erro_rede': 'Server není dostupný. Zkontrolujte připojení a zkuste to znovu.',
    'web_visual': 'Styl',
})
T.update({'web_demasiados': 'Nejvýše {max} čísel na jednu zakázku.'})
