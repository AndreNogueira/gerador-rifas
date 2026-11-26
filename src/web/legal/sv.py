"""Villkor, integritet och kontakt på svenska: översättning av `pt.py` (samma sidor, avsnitt, stycken och {platshållare}). Utan granskning av modersmålstalare; den portugisiska gäller."""
FRASES = {
    "responsavel_com": "Tjänsten drivs av {nome}.",
    "responsavel_sem": "Tjänsten drivs av sin upphovsperson, den som gör den tillgänglig på nätet.",
    "contacto_com": "Du kan kontakta oss på {email}.",
    "contacto_sem": "För tillfället finns ingen offentlig kontakt.",
    "contacto_pagina_com": "För frågor, fel eller förslag, skriv till {email}.",
    "contacto_pagina_sem": "För tillfället finns ingen offentlig kontakt. Kom tillbaka till sidan senare.",
    "atualizado": "21 november 2026",
}

AVISO = ("Preliminär version, ska granskas med juridiskt stöd. Om något här skiljer sig från vad tjänsten gör, be oss rätta det. "
         "Detta är en översättning utan granskning av modersmålstalare: vid skillnader gäller den portugisiska versionen.")

TEXTOS = {
    "termos": {
        "titulo": "Användarvillkor",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Vad tjänsten är",
             "paragrafos": ["Lottgeneratorn skapar utifrån en PDF-mall numrerade lotter till ett lotteri, färdiga att skriva ut. Mer gör den inte: den säljer inga lotter, "
                            "tar inte emot pengar, sparar inga deltagarlistor och gör inga dragningar med rättslig verkan.",
                            "{responsavel}"]},
            {"titulo": "Den som anordnar lotteriet ansvarar för det",
             "paragrafos": ["Lotterier, tombolor och dragningar omfattas av lagregler (till exempel tillstånd från kommunen och regler för föreningar) som varierar från fall till fall. "
                            "Den som anordnar lotteriet är ensam ansvarig för att följa lagen, ta betalt och dela ut vinsterna. Tjänsten ger inga juridiska råd."]},
            {"titulo": "Tillåten användning",
             "paragrafos": ["Tjänsten är gratis och för rimlig användning. Den får inte användas för att skapa lotter till bedrägerier eller för att överbelasta servern: det finns gränser för "
                            "filstorlek, nummer per beställning ({max_numeros}) och beställningar per minut, och en skapning i taget."]},
            {"titulo": "Dina filer",
             "paragrafos": ["Mallen och siffrorna används bara för att skapa dina lotter och raderas från servern efter {validade} minuter utan aktivitet, eller när du trycker på ”Rensa allt”. "
                            "Vi använder dem inte till något annat. De förblir dina: du behöver bara ha rätt att använda det du laddar upp (bilder, typsnitt, logotyper)."]},
            {"titulo": "Inga garantier",
             "paragrafos": ["Tjänsten tillhandahålls ”i befintligt skick”, utan garanti för att den alltid är tillgänglig eller felfri. Kontrollera alltid PDF:erna före utskrift (tjänsten kontrollerar "
                            "de skapade numren, men slutkontrollen är din). I den mån lagen tillåter ansvarar vi inte för förluster som hänger ihop med användningen av tjänsten."]},
            {"titulo": "Ändringar",
             "paragrafos": ["Dessa villkor kan ändras; datumet för senaste uppdatering är {atualizado}. Om tjänsten någon gång blir betald sägs det tydligt innan något debiteras."]},
            {"titulo": "Kontakt", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Integritetspolicy",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Sammanfattning",
             "paragrafos": ["Det finns inga konton, inga annonser och inga spårningsverktyg från tredje part. Dina filer raderas från servern inom {validade} minuter. "
                            "Användningsstatistiken är bara sammanlagda tal."]},
            {"titulo": "Vilka uppgifter vi behandlar",
             "paragrafos": ["Filerna du laddar upp (mall och siffror) behandlas bara för att skapa lotterna, ligger i en tillfällig mapp på servern och raderas efter {validade} minuter "
                            "utan aktivitet eller när du trycker på ”Rensa allt”.",
                            "För att veta hur tjänsten används registrerar vi räkningar: hur många besök, skapanden och nedladdningar, valt språk och tema samt skärmtyp. "
                            "Vi registrerar också besökets land (bara koden, till exempel «PT»), som värdnätverket härleder från IP-adressen; själva IP-adressen sparar vi inte. Vi registrerar aldrig IP-adresser, filnamn, filernas innehåll eller webbläsarens fullständiga identifiering.",
                            "IP-adressen används bara i minnet, ett ögonblick, för att begränsa antalet beställningar per minut, och sparas inte av oss. Värdleverantören "
                            "(Render, i Frankfurt, Europeiska unionen) kan registrera IP-adresser i sina tekniska loggar."]},
            {"titulo": "I din webbläsare",
             "paragrafos": ["Vi sparar dina inställningar i din webbläsare (lokal lagring): språk, tema, ljust eller mörkt läge och formulärets senaste värden. "
                            "För att du inte ska upprepa arbetet från år till år kan även siffrofilen finnas kvar i din webbläsare (aldrig på vår server); ”Rensa allt” tar bort den. "
                            "Vi använder inga reklam- eller spårningskakor."]},
            {"titulo": "Rättslig grund och lagring",
             "paragrafos": ["Vi behandlar uppgifterna med stöd av berättigat intresse att tillhandahålla tjänsten och hålla den säker (GDPR, artikel 6.1 f). Filerna finns i minuter; "
                            "de sammanlagda räkningarna identifierar ingen."]},
            {"titulo": "Dina rättigheter",
             "paragrafos": ["Du har rätt till tillgång, rättelse, radering och invändning, och att klaga hos din dataskyddsmyndighet (i Portugal CNPD, cnpd.pt). "
                            "Eftersom vi inte sparar uppgifter som identifierar dig finns i praktiken lite att få del av eller radera; hör av dig om du undrar något."]},
            {"titulo": "Vem som ansvarar", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Uppdatering", "paragrafos": ["Senast uppdaterad: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Kontakt",
        "aviso": "",
        "seccoes": [
            {"titulo": "Hör av dig",
             "paragrafos": ["{contacto_pagina}",
                            "Om du hittar ett fel, berätta vad du gjorde och vad du väntade dig; skicka inte din mall om den innehåller personuppgifter."]},
        ],
    },
}
