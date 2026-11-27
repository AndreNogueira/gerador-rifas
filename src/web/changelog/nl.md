# Changelog (Nederlandse samenvatting)

Vertaalde samenvatting van `../CHANGELOG.md`: dezelfde versies, onderdelen en punten, korter. De volledige tekst is in het Portugees.

## 3.96.0 — 2026-11-27

### Verbeterd
- **De gidsen voor de club en het buurtfeest hebben nu eigen inhoud**: `/rifas-para-clubes` en `/rifas-para-festas` herhalen niet langer bijna dezelfde tekst als de andere gidsen per doelgroep; ze gaan nu over wat voor elk specifiek is — het bestuur en de kleuren van de club, sponsors; het buurtcomité (of gewoon een groep buren, zonder formele vereniging) en wie verantwoordelijk is voor het geld tot de trekking.

## 3.95.0 — 2026-11-27

### Opgelost
- **Titel van de startpagina na het laden**: toonde alleen «Gerador de Rifas» in plaats van de volledige titel die de server al stuurt naar wie geen JavaScript uitvoert; React herstelt nu de juiste titel.
- **Visuele sprong in de koptekst**: meten wat naast de appnaam past, kon de koptekst even naar twee regels laten omslaan en de rest van de pagina omlaag duwen; de echte oorzaak is gevonden (niet de advertenties) en opgelost.

### Verbeterd
- **Startpagina verliest de uitleg en de gidsen niet meer na het monteren**: «Hoe het werkt», de tutorial, de video, «Over ons» en de «Zo doe je het»-gidsen staan nu ook in de pagina zelf, niet alleen in het menu «Hulp».
- **Talen laden parallel**: de interfaceteksten ophalen wacht niet meer op de talenlijst alleen om de paginataal te bepalen, wat de eerste inhoud versnelt op telefoons en trage verbindingen.
- **Gids «Zo organiseert u een parochieloterij» met eigener stem**: beslissen met de parochieraad, de controleerbare trekking als antwoord op het vertrouwen van kopers, en geen specifieke lokale instantie meer genoemd (dat verschilt per regio).

## 3.94.0 — 2026-11-26

### Opgelost
- **Kleine letters in de ontwerpgalerij, op de telefoon**: in het paneel «Geen sjabloon? Kies een uit de galerij» toonden de lijst «Hoeveel prijzen», de datumindeling en het veld «tekst voor de datum» tekst van 14 px, net als de drie velden die in de vorige versie al zijn verbeterd. Nu minstens 16 px.
- **Stap 2 zegt alleen «(verplicht)» als het echt nog moet**: bij het kiezen van een galerijontwerp (dat de cijfers al meelevert) toont de titel van stap 2 geen «(verplicht)» meer zolang het veld is ingevuld.

### Verbeterd
- **Beschrijving van de startpagina vereist geen Canva meer**: de beschrijving in zoekmachines noemde alleen de Canva-sjabloon; nu staat er ook dat je in plaats daarvan een kant-en-klaar ontwerp uit de galerij kunt kiezen.

## 3.93.0 — 2026-11-26

### Opgelost
- **Kleine letters in drie velden op de telefoon**: de velden voor het maximum per bestand, de kleur van de nummers en de bestandsnaam toonden tekst onder 16 px, waardoor iOS Safari automatisch inzoomt bij focus. Ze hebben nu dezelfde grootte als de velden ernaast.

### Verbeterd
- **"Over" zegt nu wie de Lotenmaker maakt**: als de beheerder van de dienst zich identificeert (dezelfde instelling als bij Voorwaarden en Privacy), vermeldt de pagina "Over" nu wie hem gemaakt heeft en onderhoudt, en dat de Windows-app er eerst was.

## 3.92.0 — 2026-11-26

### Opgelost
- **Tekst van stap 4 („Bestemming”) op de site**: de tutorial en de homepage zeiden „kies de map waarin de PDF's worden opgeslagen”, wat alleen klopt voor de Windows-app — op de site worden de bestanden automatisch via de browser gedownload. De tekst van de site noemt nu geen map meer.

## 3.91.0 — 2026-11-26

### Verbeterd
- **De sjablonengalerij heeft nu hetzelfde visuele gewicht als het uploaden van het sjabloon**: op de startpagina is het kiezen van een al gemaakt ontwerp (zonder Canva) niet langer een secundaire link onder de pdf-upload — het heeft nu een even opvallend vak.
- **Meer koppelingen tussen pagina's**: de stappenplannen voor de trekking en de prijslijst verwijzen nu naar hun eigen tool (`/sorteio`, `/precario`) in plaats van naar de tombolagenerator, en de startpagina verwijst nu ook naar het overzicht van stappenplannen "Hoe werkt het" (`/como-fazer`).

## 3.90.0 — 2026-11-26

### Opgelost
- **De Portugese pagina wisselt niet meer zelf van taal**: het bezoeken van een adres zonder voorvoegsel (`/`, `/tutorial`, …) zonder dat de browser Portugees als taal doorgeeft — het geval bij veel zoekmachine-crawlers en sommige browsers — liet de site zelf de URL en alle inhoud naar Engels herschrijven. Zonder voorvoegsel betekent nu altijd Portugees, zoals bedoeld; de 21 talen met voorvoegsel werken gewoon door. `robots.txt` blokkeert ook niet langer volledig `/api/linguas`, `/api/textos`, `/api/guia(s)` en de documentatie van de publieke API (`/api/v1/docs`), zodat zoekmachines de site goed kunnen renderen en indexeren.

### Verbeterd
- **Snellere taalkiezer**: de eigen namen van de talen in de kiezer (zoals «Tiếng Việt» of «Čeština») gebruiken nu het systeemlettertype in plaats van het merklettertype, waardoor de pagina geen extra glyphs meer moet downloaden om ze te tonen — dat vertraagde eerder de hoofdtekst en verschoof die soms.

## 3.89.0 — 2026-11-26

### Verbeterd
- **Drie contourafbeeldingenbibliotheken meer in de prijslijst: Tabler Icons, Lucide en Material Symbols** (zonder vermelding te vereisen): meer dan 100 artikelen kregen alternatieven uit deze bibliotheken, één voor één gekozen om het artikel echt weer te geven (in tegenstelling tot de vorige is er geen automatische manier om ze te vinden). In tegenstelling tot de kleurenafbeeldingen krijgen deze de kleur van de tekst op dat moment — van de site, de Windows-app of het gekozen PDF-papier — zodat ze nooit onzichtbaar worden op een donker thema of donker papier.

## 3.88.0 — 2026-11-21

### Verbeterd
- **Nog twee afbeeldingenverzamelingen in de prijslijst: Twemoji en OpenMoji**: ze voegen zich bij Noto Emoji en Fluent Emoji 3D, zonder enige bestaande afbeelding te vervangen — de kiezer groepeert de afbeeldingen nu per verzameling, met de naam van elke verzameling. Twemoji (CC BY 4.0) en OpenMoji (CC BY-SA 4.0) vereisen vermelding van de makers, die in het Privacybeleid staat en, alleen wanneer zo'n afbeelding echt wordt gebruikt, in de voettekst van de gegenereerde PDF en afhaaletiketten.

## 3.87.0 — 2026-11-21

### Verbeterd
- **Meer afbeeldingen om uit te kiezen in de prijslijst, van Microsofts Fluent Emoji 3D (MIT-licentie, geen vermelding verplicht)**: alle 93 catalogusartikelen kregen, naast de gebruikelijke Noto Emoji-afbeeldingen, een alternatief in 3D-stijl waar dat voor die code bestaat — geen van de bestaande afbeeldingen is vervangen.

## 3.86.0 — 2026-11-21

### Verbeterd
- **Ruimte tussen de loten en snijmarkeringen tussen elk lot**: door de snijmarkeringen aan te zetten wordt de speling die vroeger alleen de marge vergrootte nu ruimte tussen de loten, en de markeringen (vroeger alleen in de marges van het vel) verschijnen nu ook tussen elk lot.

## 3.85.0 — 2026-11-21

### Opgelost
- **Echte 404-pagina**: een verkeerde link toonde de generator verborgen onder de 404-status. Nu verschijnt een echte, vertaalde pagina «Pagina niet gevonden» met een link terug.
- **Reserve-icoon (favicon.ico)**: voor oude tools die alleen dat pad controleren.

## 3.84.0 — 2026-11-21

### Nieuw
- **Ontwerp «Verjaardag» in de galerij en de prijslijst**: ballonnen, vlaggenlijnen en confetti in roze, turkoois en geel — het 25e ontwerp naast de bestaande, zodat een verjaardagsfeest zijn eigen stijl krijgt op de loten, de prijslijst en de munten.

## 3.83.0 — 2026-11-21

### Verbeterd
- **Meer afbeeldingen om uit te kiezen per artikel op de prijslijst**: elk catalogusartikel kan nu tot 8 afbeeldingen hebben (was 5) — alle 93 kregen minstens één nieuw, passend alternatief (water een golf, koffie een mate, taart confetti…).

## 3.82.0 — 2026-11-20

### Opgelost
- **Ongelijke marges bij het vullen van het vel met minder loten dan er pasten**: minder loten per vel aanvragen dan het maximum liet ze linksboven staan, met alle ruimte rechtsonder — een rechte snede sneed niet meer goed tussen elk lot. Nu staan ze altijd gecentreerd, met dezelfde marge aan alle vier de zijden.

## 3.81.0 — 2026-11-20

### Nieuw
- **Ophaaletiketten**: betaal je op de ene plek en haal je op een andere op? Op de prijslijstpagina wordt elk artikel een etiket met de afbeelding, de naam, de prijs (als je wilt) en de ophaalzone (de bar, de keuken…), in het aantal exemplaren dat je kiest, 24 per A4-vel met snijlijnen en één kleur per zone. Een combo geeft één etiket per artikel, elk in de zone van zijn rubriek (site en Windows-app; met handleiding en video's).

## 3.80.0 — 2026-11-20

### Nieuw
- **Combo's over rubrieken heen in de prijslijst**: bundel 2 tot 4 catalogusartikelen, ook uit verschillende rubrieken (bijvoorbeeld een broodje en een drankje), tegen één prijs. De combo staat in een nieuwe rubriek, «Combo's en menu's», met de afbeeldingen van de artikelen naast elkaar, en kan een eigen naam krijgen (site en Windows-app).

## 3.79.0 — 2026-11-20

### Nieuw
- **Kleuren en logo in de prijslijst**: u kunt de hoofd-, accent- en papierkleur van het ontwerp wijzigen (de prijzen passen zich vanzelf aan zodat ze leesbaar blijven) en het logo van uw vereniging (PNG of JPG) in de kop, links of rechts, of in de voet plaatsen (site en Windows-app). De kleuren en de plek blijven bewaard in het prijslijstbestand en in de gedeelde link; het logo dient alleen om het voorbeeld en de pdf te tekenen en wordt nooit bewaard.

## 3.78.0 — 2026-11-20

### Nieuw
- **Tot 5 afbeeldingen om uit te kiezen per artikel**: klik in de prijslijst op de afbeelding van een catalogusartikel en kies de afbeelding die u het mooiste vindt uit maximaal 5 (water kan een druppel, een kraan, ijs of een glas zijn…). Uw keuze staat in de pdf en blijft bewaard in het prijslijstbestand en in de gedeelde link (site en Windows-app).

## 3.77.0 — 2026-11-20

### Verbeterd
- **Nettere lijsten en regels in de prijslijst**: alle keuzelijsten op de site zien er nu uit als de andere velden, met een pijltje dat het thema volgt (licht en donker). In de prijslijst nemen de × om een artikel te verwijderen en de fotoknop veel minder ruimte in, springen de prijzen niet meer naar een tweede regel en staat op een telefoon de naam bovenaan met de velden eronder.

## 3.76.0 — 2026-11-20

### Nieuw
- **Eigen foto's in de prijslijst**: bij elk artikel kunt u op «Foto» klikken en een eigen afbeelding (PNG of JPG) in plaats van het pictogram plaatsen (tot 20 per prijslijst; site en Windows-app). De foto wordt op uw computer verkleind en dient alleen om het voorbeeld en de pdf te tekenen: ze wordt niet op de server, in het prijslijstbestand of in de gedeelde link bewaard.

## 3.75.0 — 2026-11-20

### Nieuw
- **De prijslijst delen via een link** (op de site, als de dienst een database heeft): «Delen via link» op de prijslijstpagina maakt een link die iedereen kan openen om uw prijslijst (teksten, artikelen, prijzen en ontwerp) te zien en voort te zetten. Ze wordt 90 dagen na de laatste toegang bewaard, zonder iets over wie ze deelt; het privacybeleid is bijgewerkt.

## 3.74.0 — 2026-11-20

### Nieuw
- **Twee maten in de prijslijst**: zet «Twee maten (twee prijzen per artikel)» aan (site en Windows-app) om bij elk artikel twee prijzen in te vullen (bijvoorbeeld klein en groot, of het artikel en het menu). De twee kolommen staan netjes uitgelijnd, met de namen die u kiest erboven («Klein» en «Groot» standaard), en worden in het prijslijstbestand bewaard.

## 3.73.0 — 2026-11-20

### Nieuw
- **Tafelkaartjes**: kies bij het formaat van de prijslijst «Tafelkaartjes (4 per A4-vel)» (site en Windows-app) en de prijslijst komt als A6-kaartjes, vier op een A4-vel met gestippelde snijlijnen, klaar om te printen en uit te knippen voor de tafels (tot 12 artikelen).

## 3.72.0 — 2026-11-20

### Nieuw
- **Prijslijst als «schoolbord»**: een nieuw ontwerp in de lijst «Gelegenheid en thema» (en in de Windows-app): donkergroene schoolbordachtergrond, een houten lijst en krijtletters (wit en geel), ideaal voor de kraam, het terras of het klaslokaal.

## 3.71.0 — 2026-11-20

### Nieuw
- **Genummerde fiche-bonnen** (in de prijslijst, met een verzonnen munt; en «Extras → Prijslijst… → Genummerde bonnen…» in de Windows-app): kies hoeveel fiches elke bon waard is, de titel en een opmerking, bekijk de bon in het ontwerp van de prijslijst en maak ze. Het gaat verder in de loterijgenerator, die de bonnen nummert met series, controle-QR-codes en printklare vellen.

## 3.70.0 — 2026-11-20

### Nieuw
- **Prijslijstgenerator voor feesten** (`/precario`, en «Extras → Prijslijst…» in de Windows-app): kies de gelegenheid (die van het moment wordt voorgesteld) en de artikelen uit een catalogus met afbeeldingen, vul de prijzen in de munt van uw land of een verzonnen munt (fiches…) in en download de printklare pdf (of een afbeelding), in A5, A4 of A3 en met de 24 ontwerpen van de galerij. Er is ook een nieuw stappenplan: «Zo maak je de prijslijst voor een feest».

## 3.69.0 — 2026-11-19

### Nieuw
- **Braziliaans Portugees** (`/pt-br`): de site, de stappenplannen en de juridische pagina's bestaan nu ook in Braziliaans Portugees, met eigen woordenschat, een privacyverklaring aangepast aan de Braziliaanse LGPD en automatische taalkeuze als de browser op pt-BR staat. Het Europese Portugees blijft hetzelfde, zonder voorvoegsel in het adres.

## 3.68.0 — 2026-11-19

### Nieuw
- **Drie nieuwe stappenplannen, per onderwerp** (niet per doelgroep): loten nummeren, een controleerbare trekking houden (verwijst naar de pagina «Trekking») en hoeveel loten tegen welke prijs. Te vinden onder «Alle stappenplannen» (`/como-fazer`), in 22 talen.

## 3.67.0 — 2026-11-19

### Nieuw
- **Overzicht van de «Hoe doe je het»-stappenplannen** (`/como-fazer`): één pagina met alle stappenplannen en een korte samenvatting; elk stappenplan eindigt met links naar de andere. Ook in het menu «Hulp» («Alle stappenplannen»).
- De stappenplannen en het overzicht geven Google hun pad door (Start › Hoe doe je het › stappenplan), zodat het in de zoekresultaten kan staan.

## 3.66.0 — 2026-11-19

### Nieuw
- **Uitnodiging om een reactie achter te laten:** na het downloaden van uw loten verschijnt (eenmaal per apparaat) een discrete melding die uitnodigt tot een reactie, desgewenst anoniem. U kunt hem sluiten met “Niet nu”.

## 3.65.0 — 2026-11-19

### Verbeterd
- **Een lichtere en veiligere site:** wie alleen loten genereert, downloadt 24 % minder code (het beheerpaneel, de sjablooneditor en de trekking laden pas als je de pagina opent). De site stuurt nu ook beveiligingsheaders en antwoordt linkcontroles en deelvoorbeelden.

## 3.64.0 — 2026-11-19

### Nieuw
- **Wekelijkse back-up van de gegevens van het beheerpaneel:** elke maandag slaat de dienst, in de opslag van dezelfde leverancier als de database, een kopie op van de geschiedenis, doelen, het actielogboek, reacties en SEO-teksten (laatste 8 weken), met een script om te herstellen.

## 3.63.0 — 2026-11-19

### Nieuw
- **Echte sitesprestaties in de statistieken:** het beheerpaneel toont per dag hoe lang de pagina erover doet om te verschijnen, hoeveel de inhoud verschuift en hoe lang het duurt om op een klik te reageren, gemeten in de browsers van bezoekers (mobiel en computer). Slechts drie anonieme getallen per bezoek; het Privacybeleid is bijgewerkt.

## 3.62.0 — 2026-11-19

### Nieuw
- **Herkomst van bezoeken in de statistieken:** het beheerpaneel toont nu waar bezoeken vandaan komen, in algemene categorieën (zoeken, sociale netwerken, e-mail, andere sites of direct) en per campagne (utm_source), om een promotie te meten. Het adres van de herkomstpagina en het IP worden nooit bewaard; het Privacybeleid is bijgewerkt.

## 3.61.0 — 2026-11-19

### Nieuw
- **Actielogboek in het beheerpaneel:** wie wat wanneer in het paneel deed, wordt 400 dagen bewaard (aanmeldingen, verwijderde of verborgen reacties, API-sleutels, SEO-teksten, doelen), zonder bezoekersgegevens of wachtwoorden.

## 3.60.0 — 2026-11-19

### Nieuw
- **Dagdoelen in het beheerpaneel:** de beheerder stelt een doel per dag in (sessies, generaties, gegenereerde nummers, downloads…) en ziet of de laatste dag het haalde, het 7-daagse gemiddelde en op hoeveel dagen het gehaald werd; het dagelijkse e-mailrapport bevat dezelfde sectie.

## 3.59.0 — 2026-11-19

### Nieuw
- **Reactiestatus in het beheerpaneel:** de beheerder kan elke reactie markeren als gelezen, favoriet of verborgen (een verborgen reactie verdwijnt van de openbare pagina maar gaat niet verloren), op status filteren en zien hoeveel er nog ongelezen zijn.

## 3.58.0 — 2026-11-19

### Nieuw
- **Quota van de gratis hosting in het beheerpaneel:** te zien is hoeveel van de 750 Render-uren per maand de dienst heeft verbruikt (met een projectie tot het einde van de maand) en hoeveel ruimte de database inneemt in het gratis plan van Neon, met een waarschuwing in het dagelijkse e-mailrapport voordat de quota op zijn.

## 3.57.0 — 2026-11-19

### Nieuw
- **Versiemarkeringen in de grafieken van het beheerpaneel:** elke dagelijkse grafiek markeert de dag waarop een nieuwe appversie kwam (en het dagrapport zegt welke), zodat een stijging van fouten of reactietijd gekoppeld kan worden aan de update die haar veroorzaakte.

## 3.56.0 — 2026-11-19

### Nieuw
- **Wekelijkse en maandelijkse e-mailsamenvatting voor de beheerder van de site:** op maandag komt de samenvatting van de week en op de 1e die van de maand, met de totalen vergeleken met de vorige periode en een miniatuur van elke dag. Ze lezen uit de permanente geschiedenis. Alleen aantallen.

## 3.55.0 — 2026-11-19

### Nieuw
- **Directe e-mailmeldingen voor de beheerder van de site:** bij een reeks serverfouten, herstarts van de engine, geheugen vlak bij de limiet of een database die niet reageert, komt er meteen een waarschuwing (zonder te wachten op het dagrapport en zonder herhaling gedurende 6 uur). Alleen aantallen.

## 3.54.0 — 2026-11-19

### Nieuw
- **Permanente geschiedenis in het beheerpaneel:** na middernacht wordt een samenvatting van elke dag opgeslagen, zodat de dagelijkse ontwikkeling nu maanden en tot 2 jaar toont (voorheen alleen 90 dagen). Alleen aantallen, zoals de rest van het paneel.

## 3.53.0 — 2026-11-19

### Nieuw
- **Dagelijks e-mailrapport voor de beheerder van de site:** elke dag, vlak na middernacht, komt er een e-mail met alles wat is vastgelegd op de dag die net voorbij is (gebruik, publiek, fouten en serverbronnen), vergeleken met het gemiddelde van de 7 voorgaande dagen, zodat de app te volgen is zonder het paneel te openen. Alleen aantallen: nooit gegevens van bezoekers.

## 3.52.0 — 2026-11-19

### Verbeterd
- **Reacties zonder IP-adres:** in plaats van het IP wordt alleen het land bewaard waaruit de reactie is verstuurd (alleen de beheerder ziet het). Het IP-adres wordt niet meer bewaard: die van eerdere reacties zijn verwijderd en het Privacybeleid is bijgewerkt.

## 3.51.0 — 2026-11-19

### Nieuw
- **Reacties:** een pagina ‘Reacties’ waar iedereen ziet wat anderen van de generator vinden, en een pagina om de uwe achter te laten: anoniem blijven of een naam tonen (zonder naam staat er ‘Bezoeker nr. …’). Het IP-adres wordt alleen voor de beheerder bewaard, tegen misbruik, nooit getoond en na 90 dagen verwijderd.
- **Probleem melden:** nieuwe pagina waar u een fout beschrijft; met ‘Openen’ wordt die direct op de GitHub van het project aangemaakt, zonder account (uw IP wordt niet verstuurd en technische browsergegevens alleen als u ze toevoegt).
- Beide pagina's en de knoppen ‘Reacties’ en ‘Probleem melden’ staan duidelijk in beeld in de kop, het menu en de voettekst; het Privacybeleid (22 talen) legt uit wat wordt bewaard.

## 3.50.0 — 2026-11-18

### Verbeterd
- **Een kop die zich aan het scherm aanpast:** alle opties staan rechts in één rij zonder gaten en worden, naarmate het scherm kleiner wordt, één voor één in een «hamburger»-menu geplaatst (eerst de lichte/donkere modus en de stijl, als laatste de donatie). Op telefoons blijven alleen de naam van de app en de menuknop over; het menu opent met de pagina's, hulp, delen en instellingen.

## 3.49.0 — 2026-11-18

### Nieuw
- **Dashboard met de ontwikkeling dag voor dag:** een nieuwe weergave «Dagelijkse ontwikkeling» toont, tot 90 dagen terug, alles wat de server in de database bewaart (sessies, generaties, gegenereerde nummers, talen, landen, stijlen, galerij, editor, API, verzoeken, responstijden, CPU en geheugen…), met de trend van elke indicator en een CSV-download van alles. Het is een functie van het dashboard van de eigenaar: bezoekers merken er niets van.

## 3.48.0 — 2026-11-18

### Verbeterd
- **Menu «Help» in de kop:** de handleiding, de video en de «Hoe doe je het»-gidsen staan nu in één tabblad, «Help». De kop is korter en de naam van de app staat altijd volledig op één regel, in elke taal en schermgrootte.

## 3.47.0 — 2026-11-15

### Verbeterd
- **Sjabloongalerij:** de lijst met ontwerpen wordt in sommige thema's niet meer afgekapt of verkeerd geplaatst; elke prijs heeft zijn nummer; elk tekstvak toont zijn tekenlimiet (bijvoorbeeld 12/50); en de knop «Dit sjabloon gebruiken» zit niet meer tegen het laatste vak aan.
- **Trekkingsdatum in een eigen kalender:** in plaats van het veld van de browser (dat «dd-mm-jjjj» en een kiezer in een andere taal dan die van de site toonde) is er een kalender in alle 22 talen, met maanden en weekdagen in de gekozen taal, de datum zoals die taal hem schrijft, de juiste eerste dag van de week en de knoppen «Vandaag» en «Wissen». Hij werkt met het toetsenbord (pijlen, Page Up/Down, Home/End, Enter en Esc).
- **Een uitgebreidere «Info»:** de tekst is in alle 22 talen herschreven en legt uit voor wie de generator is, wat hij doet, wat u na het printen doet, hoe hij de privacy beschermt en waar u hem kunt gebruiken.

## 3.46.0 — 2026-11-15

### Verbeterd
- **Donatieknop beter zichtbaar:** als de dienst een donatielink heeft, staat de knop nu in de kop (naast «Delen») en, na het genereren van de bestanden, met een korte uitnodiging. Hij staat ook nog in de voettekst.

## 3.45.0 — 2026-11-14

### Verbeterd
- **Sjabloongalerij op één regel:** de 24 ontwerpen kies je nu in een vak van één regel waarin elke optie een miniatuur van het sjabloon toont, in plaats van een lange lijst knoppen. Het werkt met muis, aanraking en toetsenbord (pijlen, Home/End, een letter, Enter en Esc).

## 3.44.0 — 2026-11-14

### Verbeterd
- **Privacy:** de gebruikstellingen bevatten nu het land van het bezoek (alleen de code, afgeleid door het hostingnetwerk; het IP-adres wordt nog steeds niet bewaard). Het privacybeleid legt het uit in alle 22 talen.

## 3.43.1 — 2026-11-14

### Verbeterd
- **Opgeruimdere voettekst:** de gidsen «Handleidingen» staan nu alleen in de groep in de kop; ze herhalen zich niet meer onderaan de pagina.

## 3.43.0 — 2026-11-14

### Verbeterd
- **Trekkingsdatum in een kalender:** in de sjabloongalerij kies je de datum in een kalender en daarna hoe die op het lot staat (31-12-2026, 31 dec 2026, 31 december 2026 of met weekdag), in de taal van de site. Zelf typen kan nog steeds, nu tot 60 tekens.
- **Bredere teksten:** tekstpagina's (gidsen, tutorial, voorwaarden…) gebruiken nu de volle paginabreedte, met minder regels en alinea's.

## 3.42.0 — 2026-11-14

### Verbeterd
- **Kop:** de nieuwe groep «Handleidingen», naast de tutorial, bundelt de gidsen (scholen, verenigingen, clubs, brandweer, buurtfeesten en parochies). De knop «Delen» is van de voettekst naar de kop verhuisd, opvallend, en de lijst toont de pictogrammen van WhatsApp, Telegram, Facebook, e-mail en «Link kopiëren».

## 3.41.0 — 2026-11-14

### Verbeterd
- **Automatisch voorbeeld:** wanneer je het sjabloon, de cijfers, het logo of een veld wijzigt dat de eindpagina beïnvloedt (nummers, cijfers, vel, series, kleuren, QR…), ververst het voorbeeld met echte nummers zichzelf, zonder op ‘Voorbeeld’ te klikken. Gaat er iets mis, dan staat de reden naast de viewer, zonder pop-ups.

## 3.40.0 — 2026-11-14

### Nieuw
- **3 tot 10 prijzen in de galerij:** in alle 24 ontwerpen van de galerij kies je hoeveel prijzen het lot heeft (3 tot 10; eerder maximaal 3). Vanaf 6 staan ze in twee kolommen. Ook in de Windows-app.

## 3.39.0 — 2026-11-13

### Nieuw
- **Windows-app 2.7:** de galerij en de sjablooneditor accepteren nu uitgebreid Latijn, Vietnamees, Grieks, Cyrillisch, Chinees, Japans en Koreaans, zoals de site sinds 3.37 (Hindi, Arabisch en Hebreeuws ontbreken nog). Te downloaden via de Changelog-pagina.

## 3.38.0 — 2026-11-13

### Nieuw
- **Knop «Delen»:** onderaan de pagina en, na het genereren van de bestanden, op de leveringskaart. Hij opent een korte lijst (het deelmenu van telefoon of computer, WhatsApp, Telegram, Facebook, e-mail en «Link kopiëren») om andere verenigingen, scholen en feestcomités kennis te laten maken met de generator. De links bevatten alleen het adres van de site in de gebruikte taal: geen tracking, er wordt niets bewaard. Met een onderwerp in de tutorial en een video.

## 3.37.0 — 2026-11-13

### Nieuw
- **Meer letters in de galerij en de sjablooneditor:** teksten mogen nu uitgebreid Latijn (Pools, Tsjechisch, Roemeens, Turks…), **Vietnamees, Grieks, Cyrillisch (Russisch, Oekraïens)**, **Chinees, Japans en Koreaans** bevatten. Hindi, Arabisch en Hebreeuws ontbreken nog (ze hebben een schrijftechniek nodig die de PDF-generator niet heeft) en geven een waarschuwing in plaats van een kapot beeld. In de pdf's verandert alleen de ingevoerde tekst; wat al hetzelfde was, blijft hetzelfde.

## 3.36.0 — 2026-11-13

### Nieuw
- **«Zo doet u het»-gids voor parochies:** «Voor parochies» (link onderaan), met de stappen voor een parochieloterij: patroonsfeesten, kermissen, herstellingen, kerstpakketten en catechese. Hij staat in alle 22 talen en herinnert u eraan bij de gemeente na te gaan of de loterij een vergunning nodig heeft.

## 3.35.0 — 2026-11-13

### Nieuw
- **Windows-app 2.6:** het menu «Extras» krijgt «Opdracht bewaren…» en «Opdracht openen…» (een .rifas-bestand met de nummers, de naam, de series, de kleuren en de snijmarkeringen, zonder sjabloon of paden), de sjablooneditor kan afbeeldingen toevoegen (PNG of JPG) en «Beeld → Visueel» gaat van 2 naar de 14 thema's van de site (alleen de kleuren). Ook erbij: wat sinds 2.4 kwam: de editor, de 24 ontwerpen van de galerij en de 22 talen.

## 3.34.0 — 2026-11-13

### Nieuw
- **Drie nieuwe «Zo doet u het»-gidsen:** «Voor clubs», «Voor de brandweer» en «Voor buurtfeesten» (links onderaan), met telkens de stappen voor een loterij. Ze staan in alle 22 talen en herinneren u eraan bij de gemeente na te gaan of de loterij een vergunning nodig heeft.

## 3.33.0 — 2026-11-13

### Nieuw
- **Openbare API voor batches** (`/api/v1`, met Swagger op `/api/v1/docs`): andere programma's kunnen er meerdere loten-opdrachten mee maken uit één sjabloon, met sleutel, dagquota en limieten. Wie de site gebruikt, gaat altijd voor.
- **Vier nieuwe talen:** Catalaans, Oekraïens, Indonesisch en Vietnamees. De site en de Windows-app spreken nu 22 talen, met handleiding, voorwaarden, privacy, stappengidsen en schermafbeeldingen.
- **Teksten voor zoekmachines per taal te bewerken:** de eigenaar bewerkt in het beheerpaneel de titels, beschrijvingen en gidsen van elke taal, opgeslagen in de database en zonder nieuwe deploy.

## 3.32.0 — 2026-11-13

### Nieuw
- **20 nieuwe sjablonen in de galerij (24 in totaal):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Allemaal voor dit project helemaal zelf getekend, met controlestrook, op de site en in de Windows-app (waar de galerij een keuzelijst wordt).

## 3.31.0 — 2026-11-13

### Nieuw
- **Sjablooneditor v2:** ongedaan maken en opnieuw (Ctrl+Z, Ctrl+Y), dupliceren (Ctrl+D), de tekenvolgorde wijzigen, het logo (PNG of JPG) toevoegen en **het ontwerp via een link delen**: het wordt 90 dagen na de laatste toegang bewaard, zonder afbeeldingen en zonder gegevens over wie deelt (verschijnt alleen als de dienst een database heeft). Het privacybeleid zegt dat.
- **Windows-app 2.5:** krijgt de sjablooneditor (menu Extra's) en gaat naar Python 3.15.

### Verbeterd
- De Changelog heeft een link om de Windows-app te downloaden.

## 3.30.0 — 2026-11-12

### Nieuw
- **‘Zo doe je dat’-pagina’s:** twee geschreven gidsen, ‘Voor scholen’ en ‘Voor verenigingen’ (links in de voettekst), met het stappenplan voor een loterij: het lot ontwerpen, een reeks per klas of verkoper, printen met knipmarkeringen, de verkoop bijhouden en een controleerbare trekking houden. Ze staan in alle 18 talen en herinneren u eraan bij de gemeente na te gaan of een vergunning nodig is.

## 3.29.0 — 2026-11-12

### Verbeterd
- **Advertenties aan de zijkanten:** als advertenties aan staan (voorlopig niet), verschijnen ze op brede schermen aan beide kanten van de inhoud, één per kant, vast en zonder de pagina te verschuiven; op andere schermen is er één blok onderaan de pagina. Ze verschijnen nog steeds niet in de editor, in de gegenereerde bestanden of in de Windows-app.

## 3.28.0 — 2026-11-12

### Nieuw
- **Google-advertenties (voorbereid, uitgeschakeld):** de site kan onderaan de startpagina, de handleiding, ‘Over’, de trekking en de changelog een blok Google-advertenties (AdSense) tonen. Ze verschijnen nooit in de editor, in de gegenereerde bestanden, bij de loscontrole, in het dashboard of in de Windows-app, en in de Europese Economische Ruimte en het Verenigd Koninkrijk pas nadat u hebt gekozen in het toestemmingsbericht van Google. Het privacybeleid zegt dat, in alle 18 talen, wanneer advertenties aan staan; voorlopig staan ze uit tot de eigenaar van de dienst ze instelt.

## 3.27.0 — 2026-11-12

### Nieuw
- **Sjablooneditor:** in plaats van een Canva-sjabloon ontwerpt u het lot op de site (pagina ‘Sjablooneditor’, gelinkt vanaf stap 1): voeg teksten, rechthoeken, lijnen en het nummer 0001 toe (eenmaal, of tweemaal met controlestrook), sleep elk element met de muis of de pijltjestoetsen op zijn plek, wijzig kleuren, formaten en achtergrond en klik op ‘Dit sjabloon gebruiken’. Het scherm gebruikt het lettertype Vera, hetzelfde als de pdf: wat u ziet is wat u krijgt; het concept blijft alleen in de browser. Teksten mogen geen reeksen als 0123 bevatten, die het programma met het lotnummer zou verwarren (scherm en server waarschuwen).

## 3.26.0 — 2026-11-12

### Nieuw
- **Vijf nieuwe thema's:** Halloween, Strand, Oude krant, Groene terminal en Circusaffiche, elk in licht en donker. De site heeft nu 14 thema's; de indeling is overal hetzelfde (alleen kleuren en uiterlijk veranderen).

## 3.25.0 — 2026-11-08

### Nieuw
- **Eén adres per taal voor zoekmachines:** elke taal heeft een eigen adres (/en, /ja/tutorial…) met titel, beschrijving en tekst in die taal, en de site vertelt Google welke versies gelijkwaardig zijn (hreflang). Portugees blijft op /. De gekozen taal staat nu in de adresbalk.

## 3.24.1 — 2026-11-08

### Verbeterd
- **Selectievakjes uitgelijnd:** „Eén kleur per serie” en de andere vakjes staan nu naast hun tekst in plaats van aan het andere eind van de kaart.

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
