"""Podmínky, soukromí a kontakt česky: překlad `pt.py` (stejné stránky, oddíly, odstavce a {zástupné značky}). Bez kontroly rodilými mluvčími; platí portugalská verze."""
FRASES = {
    "responsavel_com": "Službu provozuje {nome}.",
    "responsavel_sem": "Službu provozuje její autor, osoba, která ji nabízí online.",
    "contacto_com": "Můžete nás kontaktovat na {email}.",
    "contacto_sem": "Zatím není k dispozici veřejný kontakt.",
    "contacto_pagina_com": "S dotazy, chybami nebo návrhy pište na {email}.",
    "contacto_pagina_sem": "Zatím není k dispozici veřejný kontakt. Vraťte se na tuto stránku později.",
    "atualizado": "8. listopadu 2026",
}

AVISO = ("Předběžná verze, kterou je třeba zkontrolovat s právní pomocí. Pokud se zde něco liší od toho, co služba dělá, požádejte nás o opravu. "
         "Jde o překlad bez kontroly rodilými mluvčími: při rozdílech platí portugalská verze.")

TEXTOS = {
    "termos": {
        "titulo": "Podmínky použití",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Co tato služba je",
             "paragrafos": ["Generátor losů vytvoří z šablony PDF očíslované losy tomboly připravené k tisku. Nic víc: neprodává losy, "
                            "nepřijímá peníze, neukládá seznamy účastníků a neprovádí losování s právní platností.",
                            "{responsavel}"]},
            {"titulo": "Za tombolu odpovídá ten, kdo ji pořádá",
             "paragrafos": ["Tomboly, loterie a losování podléhají zákonným pravidlům (například povolením obce a pravidlům pro spolky), která se liší podle případu. "
                            "Pořadatel tomboly odpovídá sám za dodržování zákona, za výběr peněz a za předání cen. Tato služba neposkytuje právní poradenství."]},
            {"titulo": "Povolené použití",
             "paragrafos": ["Služba je zdarma a pro rozumné použití. Nesmí se používat k výrobě losů pro podvody ani k přetěžování serveru: platí limity velikosti souborů, "
                            "čísel na zakázku ({max_numeros}) a zakázek za minutu, a vždy jen jedno generování."]},
            {"titulo": "Vaše soubory",
             "paragrafos": ["Šablona a číslice slouží jen k vytvoření vašich losů a ze serveru se mažou po {validade} minutách bez aktivity nebo po stisknutí „Vymazat vše“. "
                            "Nepoužíváme je k ničemu jinému. Zůstávají vaše: stačí mít právo používat to, co nahrajete (obrázky, písma, loga)."]},
            {"titulo": "Bez záruk",
             "paragrafos": ["Služba je poskytována „tak, jak je“, bez záruky, že bude vždy dostupná nebo bez chyb. Soubory PDF vždy před tiskem zkontrolujte (služba ověřuje "
                            "vytvořená čísla, ale poslední kontrola je na vás). V rozsahu povoleném zákonem neodpovídáme za ztráty spojené s používáním služby."]},
            {"titulo": "Změny",
             "paragrafos": ["Tyto podmínky se mohou měnit; datum poslední aktualizace je {atualizado}. Pokud se služba někdy stane placenou, bude to jasně řečeno před zpoplatněním."]},
            {"titulo": "Kontakt", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Zásady ochrany soukromí",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Shrnutí",
             "paragrafos": ["Nejsou zde účty, reklamy ani sledovací nástroje třetích stran. Vaše soubory se ze serveru mažou do {validade} minut. "
                            "Statistiky používání jsou jen souhrnná čísla."]},
            {"titulo": "Jaké údaje zpracováváme",
             "paragrafos": ["Soubory, které nahrajete (šablona a číslice), se zpracovávají jen k vytvoření losů, leží v dočasné složce na serveru a mažou se po {validade} minutách "
                            "bez aktivity nebo po stisknutí „Vymazat vše“.",
                            "Abychom věděli, jak se služba používá, zaznamenáváme počty: kolik návštěv, generování a stažení, zvolený jazyk a motiv a typ obrazovky. "
                            "Zaznamenáváme také zemi návštěvy (jen kód, například «PT»), kterou síť hostingu odvodí z IP adresy; samotnou IP adresu neukládáme. Nikdy nezaznamenáváme IP adresy, názvy souborů, obsah souborů ani úplnou identifikaci prohlížeče.",
                            "IP adresa se používá jen v paměti, na okamžik, k omezení počtu zakázek za minutu a my ji neukládáme. Poskytovatel hostingu "
                            "(Render, ve Frankfurtu, v Evropské unii) může IP adresy zaznamenávat ve svých technických protokolech."]},
            {"titulo": "Ve vašem prohlížeči",
             "paragrafos": ["Ve vašem prohlížeči (místní úložiště) ukládáme vaše předvolby: jazyk, motiv, světlý nebo tmavý režim a poslední hodnoty formuláře. "
                            "Abyste nemuseli práci opakovat z roku na rok, může ve vašem prohlížeči zůstat i soubor s číslicemi (nikdy na našem serveru); „Vymazat vše“ ho smaže. "
                            "Nepoužíváme reklamní ani sledovací cookies."]},
            {"titulo": "Právní základ a uchovávání",
             "paragrafos": ["Tyto údaje zpracováváme na základě oprávněného zájmu poskytovat službu a udržovat ji bezpečnou (GDPR, čl. 6 odst. 1 písm. f). Soubory vydrží minuty; "
                            "souhrnné počty nikoho neidentifikují."]},
            {"titulo": "Vaše práva",
             "paragrafos": ["Máte právo na přístup, opravu, výmaz a vznesení námitky a právo podat stížnost u svého úřadu pro ochranu údajů (v Portugalsku CNPD, cnpd.pt). "
                            "Protože neukládáme údaje, které by vás identifikovaly, je prakticky málo, k čemu přistupovat nebo co mazat; máte-li otázky, napište nám."]},
            {"titulo": "Kdo odpovídá", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Aktualizace", "paragrafos": ["Poslední aktualizace: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Kontakt",
        "aviso": "",
        "seccoes": [
            {"titulo": "Napište nám",
             "paragrafos": ["{contacto_pagina}",
                            "Pokud najdete chybu, napište, co jste udělali a co jste čekali; šablonu s osobními údaji neposílejte."]},
        ],
    },
}
