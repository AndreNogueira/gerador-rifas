# Changelog (Nederlandse samenvatting)

Vertaalde samenvatting van `../CHANGELOG.md`: dezelfde versies, onderdelen en punten, korter. De volledige tekst is in het Portugees.

## 3.24.0 — 2026-11-08

### Verbeterd
- **Tutorial met schermafbeeldingen van de site:** de basisonderwerpen van de tutorial tonen nu de site zelf, in alle 18 talen, in plaats van de Windows-app.

## 3.23.0 — 2026-11-08

### Nieuw
- **Handleiding en video bij elke functie:** de handleiding heeft per functie een onderwerp (series, lijst en controleblad, snijmarkeringen, galerij, eigen merk, QR, trekking, bewaren en delen, installeren als app, thema's), elk met een korte video die in de interface zelf is opgenomen, in het Portugees en Engels.
- **Changelog, Voorwaarden, Privacy en Contact in 18 talen:** de tekst verschijnt in de gekozen taal. De Changelog heeft een vertaalde samenvatting van elke versie (de volledige is Portugees); de juridische teksten zijn vertalingen zonder controle door moedertaalsprekers en bij verschillen geldt de Portugese versie.
- **Windows-app 2.4** met wat de site sinds 3.10 kreeg: menu ‘Extra’s’ met series, voorvoegsels en kleur per serie, overgeslagen nummers, nummerkleur, logo, snijmarkeringen, sjabloongalerij, verifieerbare trekking en export van lijst (CSV) en controleblad; en automatisch kerstthema in december. QR-verificatie en installeren als app blijven alleen op de site.

## 3.22.0 — 2026-11-08

### Verbeterd
- **Contrast van de 9 thema's echt gemeten:** een browsertest meet de tekst tegen de echte achtergrondpixels, licht en donker (WCAG AA), en wat niet slaagde is hersteld.
- De grote decoratieve stapnummers worden niet meer voorgelezen door schermlezers.

## 3.21.0 — 2026-11-08

### Nieuw
- **Verifieerbare trekking** (pagina ‘Trekking’): trekt nummers uit een bereik (met over te slaan nummers) zodat iedereen het kan herhalen en hetzelfde resultaat krijgt, met een openbare startwaarde. Alles gebeurt in de browser en ‘Link kopiëren’ deelt dezelfde trekking.
- De methode is stap voor stap beschreven, met een referentie-implementatie die dezelfde nummers geeft als de site.

## 3.20.0 — 2026-11-08

### Nieuw
- **QR op elk lot:** een verificatie-QR in een hoek van elk lot (sjablonen met één lot), met keuze van hoek en grootte. Scannen opent een pagina die bevestigt dat deze dienst de code voor dat lot heeft uitgegeven. Ondertekend met een sleutel die alleen de server heeft; geen database. Het bewijst geen betaling of winst.
- Verschijnt alleen als de beheerder de sleutel instelt. Opdrachten met QR zijn beperkt tot 10.000 nummers.

## 3.19.0 — 2026-11-08

### Nieuw
- **Eigen merk:** de kleur van de nummers (elk sjabloon; de seriekleur wint) en het **logo** van de vereniging op elk lot (png of jpg tot 2 MB, sjablonen met één lot), met hoek en grootte (10 tot 40 %). Png behoudt de transparantie.
- Het logo blijft alleen in de sessie (wordt gewist met de sessie en met ‘Alles wissen’) en is te zien in het voorbeeld.

## 3.18.0 — 2026-11-08

### Nieuw
- **Sjabloongalerij:** kies een van vier ontwerpen (Bosque, Quermesse, Natal en Gala), schrijf titel, organisatie, maximaal drie prijzen en datum, bekijk het voorbeeld en kies ‘Dit sjabloon gebruiken’: sjabloon en cijfers zijn klaar. Elk ontwerp is een lot met controlestrook.
- De ontwerpen zijn oorspronkelijk voor dit project, in het vrije lettertype Vera. Het lettertype kent alleen het Latijnse alfabet: andere letters geven een melding.

## 3.17.0 — 2026-11-08

### Nieuw
- **Snijmarkeringen:** een vakje in het vel­paneel (sjablonen met één lot) tekent korte streepjes in de marges, in het verlengde van elke snijlijn. Minstens 3 mm marge nodig.
- De **controlestrook** (het nummer tweemaal per lot) werkte al: nu getest en gedocumenteerd.
- De **afloop** wordt al gerespecteerd: heeft de Canva-pdf een kleinere TrimBox dan de pagina, dan is het lot alleen wat daarbinnen valt.

## 3.16.0 — 2026-11-08

### Nieuw
- **Loten­lijst exporteren (CSV):** een bestand voor Excel of Calc, één lot per rij (serie, nummer en lege kolommen Naam, Contact en Betaald), met voorvoegsels, series en overgeslagen nummers.
- **Verkoopcontroleblad (PDF):** een A4-tabel om af te drukken en met de hand in te vullen (36 loten per pagina, met vakje ‘betaald’). In talen waarvan de pdf de letters niet kan schrijven, staan de koppen in het Engels.
- Er wordt niets op de server bewaard: de lijst komt alleen uit het formulier.

## 3.15.0 — 2026-11-08

### Nieuw
- **Series en voorvoegsels:** tekst vóór de cijfers (A- geeft A-0001). Met meerdere series gescheiden door komma's herhaalt elke serie het bereik en krijgt eigen pdf's. Het voorvoegsel mag letters, spatie, punt, streepje en schuine streep bevatten (max. 6 tekens, geen cijfers).
- **Nummers overslaan:** 13, 100-110 haalt die nummers uit de reeks (overzicht, bestanden en controle tellen alleen wat gedrukt wordt).
- **Een kleur voor elke serie.**
- Dit alles zit ook in ‘Link kopiëren’ en in het voorbeeld.

## 3.14.0 — 2026-11-08

### Nieuw
- **Installeren als app (PWA):** installeer de site op telefoon of computer; het app-skelet opent ook offline (genereren heeft nog steeds de server nodig). Een eenvoudige service worker bewaart alleen de pagina, de appbestanden en de interfaceteksten en raakt nooit uw bestanden of generatieverzoeken aan.

## 3.13.0 — 2026-11-08

### Nieuw
- **Cijferbestand onthouden:** wie volgend jaar terugkomt, hoeft het niet te herhalen. Het blijft alleen in uw browser (nooit op de server) en wordt hergebruikt bij een nieuw sjabloon; een ander bestand kiezen vervangt het en ‘Alles wissen’ verwijdert het.
- **Link kopiëren:** een knop die een link met de formulierwaarden kopieert (van, tot, modus, maximum per bestand, papier, marge en naam). Wie hem opent, ziet dezelfde waarden; bestanden zitten nooit in de link.

## 3.12.0 — 2026-11-08

### Nieuw
- Pagina's **Gebruiksvoorwaarden**, **Privacybeleid** en **Contact**, gelinkt in de voettekst. Het zijn voorlopige versies, die met juridische hulp moeten worden nagekeken voordat de dienst iets vraagt.
- **Donatieknop** in de voettekst: verschijnt alleen als de beheerder de link instelt. Het contact-e-mailadres en de naam van de verantwoordelijke komen ook uit de serverconfiguratie, nooit uit de code.

## 3.11.0 — 2026-11-08

### Nieuw
- **Gebruikstrechter** in het beheerpaneel: hoeveel gebeurtenissen er per stap zijn (sessie, sjabloon, cijfers, voorbeeld, generatie, download) en welk deel van de vorige stap de volgende bereikte. Het toont waar mensen afhaken. Het telt gebeurtenissen, geen mensen.

## 3.10.0 — 2026-11-08

### Nieuw
- Deze pagina: de **Changelog**, met alles wat verandert, versie per versie.
- In **december** is het automatische thema **Kerst** (voor wie nooit een thema koos). Een ander thema kiezen blijft onthouden.

### Verbeterd
- Een afhankelijkheid minder op de server (`python-multipart` werd niet meer gebruikt: bestanden komen als ruwe body).

## 3.9.0 — 2026-11-08

### Nieuw
- Indeling voor **grote schermen** (4K, ultrabreed) en **recente telefoons**: compacte kop en knoppen van 44 px.
- Het voorbeeld toont een afbeelding als de browser geen pdf's in de pagina kan tonen (Chrome op Android).
- Het beheerpaneel registreert het **schermtype** (klasse, grootte, familie) zonder iets persoonlijks op te slaan.
- De dienst roept zichzelf elke 10 minuten aan om niet in slaap te vallen.

## 3.8.0 — 2026-11-08

### Nieuw
- **Beheerpaneel** (alleen voor de beheerder, met wachtwoord) met grafieken en uitleg over systeem en gebruik: alleen totalen, nooit persoonsgegevens.

## 3.7.0 — 2026-11-08

### Nieuw
- **SEO**: titel, beschrijving en tekst per pagina, `robots.txt`, `sitemap.xml` en een echte 404 voor pagina's die niet bestaan.

## 3.6.0 — 2026-11-08

### Verbeterd
- De site levert **één JavaScript-bestand**, versluierd en vooraf gecomprimeerd: wat verstuurd wordt is veel kleiner dan eerder.

## 3.5.0 — 2026-11-08

### Nieuw
- Thema **Matrix Gamer**: regen van groene tekens en neonglans.

## 3.4.0 — 2026-11-08

### Verbeterd
- De stijlen gaan over op **Sass** en komen als **één CSS**. De pagina-indeling is in elk thema gelijk: een thema verandert alleen kleuren en opmaak.

## 3.3.0 — 2026-11-07

### Nieuw
- **Thema's**: Premiado (de nieuwe standaardlook) en zeven andere (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala en Natal), elk licht en donker.
- Nieuw app-pictogram.
