"""Voorwaarden, privacy en contact in het Nederlands: vertaling van `pt.py` (dezelfde pagina's, onderdelen, alinea's en {plaatshouders}). Zonder controle door moedertaalsprekers; het Portugees geldt."""
FRASES = {
    "responsavel_com": "De dienst wordt beheerd door {nome}.",
    "responsavel_sem": "De dienst wordt beheerd door de maker, de persoon die hem online aanbiedt.",
    "contacto_com": "U kunt ons bereiken op {email}.",
    "contacto_sem": "Er is op dit moment geen openbaar contact.",
    "contacto_pagina_com": "Voor vragen, fouten of suggesties kunt u mailen naar {email}.",
    "contacto_pagina_sem": "Er is op dit moment geen openbaar contact. Kom later nog eens terug.",
    "atualizado": "21 november 2026",
}

AVISO = ("Voorlopige versie, nog na te kijken met juridische hulp. Wijkt iets hier af van wat de dienst doet, vraag ons dan het te corrigeren. "
         "Dit is een vertaling zonder controle door moedertaalsprekers: bij verschillen geldt de Portugese versie.")

TEXTOS = {
    "termos": {
        "titulo": "Gebruiksvoorwaarden",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Wat deze dienst is",
             "paragrafos": ["De Loten­generator maakt uit een pdf-sjabloon genummerde loten voor een verloting, klaar om te printen. Meer doet hij niet: hij verkoopt geen loten, "
                            "ontvangt geen geld, bewaart geen deelnemerslijsten en houdt geen trekkingen met juridische waarde.",
                            "{responsavel}"]},
            {"titulo": "Wie de verloting organiseert, is er verantwoordelijk voor",
             "paragrafos": ["Verlotingen, tombola's en trekkingen vallen onder wettelijke regels (bijvoorbeeld vergunningen van de gemeente en regels voor verenigingen) die per geval verschillen. "
                            "Wie de verloting organiseert, is als enige verantwoordelijk voor het naleven van de wet, het innen van betalingen en het uitreiken van de prijzen. Deze dienst geeft geen juridisch advies."]},
            {"titulo": "Toegestaan gebruik",
             "paragrafos": ["De dienst is gratis en voor redelijk gebruik. Hij mag niet worden gebruikt om loten voor fraude te maken of om de server te overbelasten: er zijn grenzen aan de "
                            "bestandsgrootte, aan nummers per opdracht ({max_numeros}) en aan opdrachten per minuut, en slechts één generatie tegelijk."]},
            {"titulo": "Uw bestanden",
             "paragrafos": ["Het sjabloon en de cijfers dienen alleen om uw loten te maken en worden na {validade} minuten zonder activiteit van de server verwijderd, of als u op ‘Alles wissen’ drukt. "
                            "We gebruiken ze nergens anders voor. Ze blijven van u: u hoeft alleen het recht te hebben te gebruiken wat u uploadt (afbeeldingen, lettertypen, logo's)."]},
            {"titulo": "Geen garanties",
             "paragrafos": ["De dienst wordt geleverd ‘zoals hij is’, zonder garantie dat hij altijd beschikbaar of foutloos is. Controleer de pdf's altijd voor het printen (de dienst controleert "
                            "de gemaakte nummers, maar de eindcontrole is van u). Voor zover de wet het toestaat, zijn wij niet aansprakelijk voor verlies door het gebruik van de dienst."]},
            {"titulo": "Wijzigingen",
             "paragrafos": ["Deze voorwaarden kunnen veranderen; de datum van de laatste wijziging is {atualizado}. Als de dienst ooit betaald wordt, wordt dat duidelijk gezegd voordat er iets wordt gerekend."]},
            {"titulo": "Contact", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Privacybeleid",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Samenvatting",
             "paragrafos": ["Er zijn geen accounts, geen advertenties en geen volgtools van derden. Uw bestanden worden binnen {validade} minuten van de server verwijderd. "
                            "De gebruiksstatistieken zijn alleen totalen."]},
            {"titulo": "Welke gegevens we verwerken",
             "paragrafos": ["De bestanden die u uploadt (sjabloon en cijfers) worden alleen verwerkt om de loten te maken, staan in een tijdelijke map op de server en worden na {validade} minuten "
                            "zonder activiteit verwijderd, of als u op ‘Alles wissen’ drukt.",
                            "Om te weten hoe de dienst wordt gebruikt, registreren we tellingen: hoeveel bezoeken, generaties en downloads, de gekozen taal en het gekozen thema en het schermtype. "
                            "We registreren ook het land van het bezoek (alleen de code, bijvoorbeeld «PT»), dat het hostingnetwerk afleidt uit het IP-adres; het IP zelf bewaren we niet. We registreren nooit IP-adressen, bestandsnamen, de inhoud van bestanden of de volledige browseraanduiding.",
                            "Het IP-adres wordt alleen kortstondig in het geheugen gebruikt om het aantal opdrachten per minuut te beperken en wordt door ons niet bewaard. De hostingaanbieder "
                            "(Render, in Frankfurt, Europese Unie) kan IP-adressen in zijn technische logboeken vastleggen."]},
            {"titulo": "In uw browser",
             "paragrafos": ["We bewaren in uw browser (lokale opslag) uw voorkeuren: de taal, het thema, de lichte of donkere modus en de laatste formulierwaarden. "
                            "Om het werk van jaar tot jaar niet te herhalen kan ook het cijferbestand in uw browser blijven (nooit op onze server); ‘Alles wissen’ verwijdert het. "
                            "We gebruiken geen advertentie- of volgcookies."]},
            {"titulo": "Rechtsgrond en bewaartermijn",
             "paragrafos": ["We verwerken deze gegevens op grond van ons gerechtvaardigd belang om de dienst te leveren en veilig te houden (AVG, artikel 6, lid 1, onder f). Bestanden duren minuten; "
                            "de samengevoegde tellingen identificeren niemand."]},
            {"titulo": "Uw rechten",
             "paragrafos": ["U hebt recht op inzage, rectificatie, wissing en bezwaar, en het recht een klacht in te dienen bij uw gegevensbeschermingsautoriteit (in Portugal de CNPD, cnpd.pt). "
                            "Omdat we geen gegevens bewaren die u identificeren, valt er in de praktijk weinig in te zien of te wissen; bij vragen kunt u contact met ons opnemen."]},
            {"titulo": "Wie verantwoordelijk is", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Actualisering", "paragrafos": ["Laatst bijgewerkt: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Contact",
        "aviso": "",
        "seccoes": [
            {"titulo": "Neem contact op",
             "paragrafos": ["{contacto_pagina}",
                            "Vindt u een fout, vertel ons dan wat u deed en wat u verwachtte; stuur uw sjabloon niet mee als het persoonsgegevens bevat."]},
        ],
    },
}
