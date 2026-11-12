# Changelog (sammanfattning på svenska)

Översatt sammanfattning av `../CHANGELOG.md`: samma versioner, avsnitt och punkter, kortare. Hela texten finns på portugisiska.

## 3.28.0 — 2026-11-12

### Nytt
- **Google-annonser (förberedda, avstängda):** webbplatsen kan visa ett block med Google-annonser (AdSense) längst ned på startsidan, i handledningen, under ”Om”, vid dragningen och i changeloggen. De visas aldrig i redigeraren, i de skapade filerna, vid lottkontrollen, i panelen eller i Windows-appen, och i Europeiska ekonomiska samarbetsområdet och Storbritannien först efter ditt val i Googles samtyckesmeddelande. Integritetspolicyn säger det, på alla 18 språk, när annonser är på; just nu är de avstängda tills tjänstens ägare ställer in dem.

## 3.27.0 — 2026-11-12

### Nytt
- **Mallredigerare:** i stället för en Canva-mall gör du lotten på webbplatsen (sidan ”Mallredigerare”, länkad från steg 1): lägg till texter, rektanglar, linjer och numret 0001 (en gång, eller två med talong), dra varje element på plats med musen eller piltangenterna, ändra färger, storlekar och bakgrund och tryck på ”Använd den här mallen”. Skärmen använder typsnittet Vera, samma som PDF:en, så det du ser är det du får; utkastet finns bara i webbläsaren. Texter får inte innehålla sekvenser som 0123, som programmet skulle förväxla med lottnumret (skärmen och servern varnar).

## 3.26.0 — 2026-11-12

### Nytt
- **Fem nya teman:** Halloween, Strand, Gammal tidning, Grön terminal och Cirkusaffisch, alla i ljust och mörkt. Webbplatsen har nu 14 teman; layouten är densamma i alla (bara färger och utseende ändras).

## 3.25.0 — 2026-11-08

### Nytt
- **En adress per språk för sökmotorer:** varje språk har sin egen adress (/en, /ja/tutorial…) med titel, beskrivning och text på det språket, och webbplatsen talar om för Google vilka versioner som motsvarar varandra (hreflang). Portugisiska ligger kvar på /. Det valda språket syns nu i adressfältet.

## 3.24.1 — 2026-11-08

### Förbättrat
- **Kryssrutor justerade:** ”En färg per serie” och de andra rutorna sitter nu bredvid sin text i stället för i andra änden av kortet.

## 3.24.0 — 2026-11-08

### Förbättrat
- **Handledning med skärmbilder av webbplatsen:** handledningens grundämnen visar nu själva webbplatsen, på alla 18 språk, i stället för Windows-appen.

## 3.23.0 — 2026-11-08

### Nytt
- **Handledning och video för varje funktion:** handledningen har ett ämne per funktion (serier, lista och kontrollblad, skärmärken, galleri, eget varumärke, QR, dragning, spara och dela, installera som app, teman), vart och ett med en kort video inspelad i själva gränssnittet, på portugisiska och engelska.
- **Changelog, Villkor, Integritet och Kontakt på 18 språk:** texten visas på valt språk. Changelog har en översatt sammanfattning av varje version (den fullständiga är portugisisk); de juridiska texterna är översättningar utan granskning av modersmålstalare och vid skillnader gäller den portugisiska versionen.
- **Windows-app 2.4** med det sajten fått sedan 3.10: menyn ”Extra” med serier, prefix och färg per serie, hoppade nummer, sifferfärg, logotyp, skärmärken, mallgalleri, verifierbar dragning och export av lista (CSV) och kontrollblad; samt automatiskt julutseende i december. QR-verifiering och installation som app finns bara på sajten.

## 3.22.0 — 2026-11-08

### Förbättrat
- **Kontrasten i de 9 teman uppmätt på riktigt:** ett webbläsartest mäter texten mot bakgrundens verkliga pixlar, ljust och mörkt (WCAG AA), och det som föll igenom rättades.
- De stora dekorativa stegnumren läses inte längre upp av skärmläsare.

## 3.21.0 — 2026-11-08

### Nytt
- **Verifierbar dragning** (sidan ”Dragning”): drar nummer ur ett intervall (med nummer att hoppa över) så att vem som helst kan upprepa den och få samma resultat, med ett offentligt startvärde. Allt sker i webbläsaren och ”Kopiera länk” delar samma dragning.
- Metoden är beskriven steg för steg, med en referensimplementation som ger samma nummer som sajten.

## 3.20.0 — 2026-11-08

### Nytt
- **QR på varje lott:** en verifierings-QR i ett hörn på varje lott (mallar med ett lott), med val av hörn och storlek. Skannar man den öppnas en sida som bekräftar att tjänsten utfärdat koden för just det lottet. Signerad med en nyckel som bara servern har; ingen databas. Den bevisar varken betalning eller vinst.
- Den visas bara när tjänstens ägare ställt in nyckeln. Beställningar med QR har ett tak på 10 000 nummer.

## 3.19.0 — 2026-11-08

### Nytt
- **Eget varumärke:** sifferfärgen (valfri mall; seriens färg går före) och föreningens **logotyp** på varje lott (PNG eller JPG upp till 2 MB, mallar med ett lott), med hörn och storlek (10 till 40 %). PNG behåller genomskinligheten.
- Logotypen finns bara kvar i sessionen (raderas med den och med ”Rensa allt”) och syns i förhandsvisningen.

## 3.18.0 — 2026-11-08

### Nytt
- **Mallgalleri:** välj en av fyra designer (Bosque, Quermesse, Natal och Gala), skriv titel, organisation, upp till tre vinster och datum, titta på förhandsvisningen och tryck ”Använd den här mallen”: mall och siffror är klara. Varje design är ett lott med pricka.
- Designerna är originella för projektet, i det fria typsnittet Vera. Typsnittet har bara latinska alfabetet: andra bokstäver ger en varning.

## 3.17.0 — 2026-11-08

### Nytt
- **Skärmärken:** en ruta i arkpanelen (mallar med ett lott) ritar korta streck i marginalerna som förlänger varje skärlinje. Kräver minst 3 mm marginal.
- **Pricken** (numret två gånger på varje lott) fungerade redan: nu är den testad och dokumenterad.
- **Utfallet** respekteras redan: har Canva-PDF:en en TrimBox mindre än sidan är lottet bara det som ligger innanför.

## 3.16.0 — 2026-11-08

### Nytt
- **Exportera lottlistan (CSV):** en fil för Excel eller Calc, ett lott per rad (serie, nummer och tomma kolumner Namn, Kontakt och Betald), med prefix, serier och hoppade nummer.
- **Kontrollblad för försäljning (PDF):** en A4-tabell att skriva ut och fylla i för hand (36 lotter per sida, med ruta för ”betald”). På språk vars bokstäver PDF:en inte kan skriva blir rubrikerna engelska.
- Inget sparas på servern: listan kommer bara från formuläret.

## 3.15.0 — 2026-11-08

### Nytt
- **Serier och prefix:** text före siffrorna (A- ger A-0001). Med flera serier separerade med kommatecken upprepar varje serie intervallet och får egna PDF:er. Prefixet tillåter bokstäver, mellanslag, punkt, bindestreck och snedstreck (högst 6 tecken, inga siffror).
- **Hoppa över nummer:** 13, 100-110 tar bort de numren ur följden (sammanfattning, filer och verifiering räknar bara det som skrivs ut).
- **En färg för varje serie.**
- Allt detta följer också med i ”Kopiera länk” och i förhandsvisningen.

## 3.14.0 — 2026-11-08

### Nytt
- **Installera som app (PWA):** installera sajten på mobil eller dator; appskalet öppnas även offline (att skapa kräver fortfarande servern). En enkel service worker sparar bara sidan, appens filer och gränssnittets texter och rör aldrig dina filer eller skapa-förfrågningar.

## 3.13.0 — 2026-11-08

### Nytt
- **Komma ihåg siffrofilen:** den som kommer tillbaka nästa år slipper upprepa den. Den sparas bara i din webbläsare (aldrig på servern) och återanvänds med en ny mall; väljer du en annan ersätts den och ”Rensa allt” tar bort den.
- **Kopiera länk:** en knapp som kopierar en länk med formulärets värden (från, till, läge, max per fil, papper, marginal och namn). Den som öppnar den ser samma värden; filer följer aldrig med länken.

## 3.12.0 — 2026-11-08

### Nytt
- Sidorna **Användarvillkor**, **Integritetspolicy** och **Kontakt**, länkade i sidfoten. De är preliminära versioner som ska granskas med juridiskt stöd innan tjänsten tar betalt.
- **Donationsknapp** i sidfoten: visas bara när ägaren ställt in länken. Kontakt-e-posten och den ansvariges namn kommer också från serverns konfiguration, aldrig från koden.

## 3.11.0 — 2026-11-08

### Nytt
- **Användningstratt** i adminpanelen: hur många händelser det finns i varje steg (session, mall, siffror, förhandsvisning, skapande, nedladdning) och hur stor del av föregående steg som nådde nästa. Visar var folk ger upp. Den räknar händelser, inte personer.

## 3.10.0 — 2026-11-08

### Nytt
- Den här sidan: **Changelog**, med allt som ändras, version för version.
- I **december** är det automatiska temat **Jul** (för den som aldrig valt ett). Att välja ett annat tema sparas fortfarande.

### Förbättrat
- Ett beroende mindre på servern (`python-multipart` användes inte längre: filerna kommer som rå kropp).

## 3.9.0 — 2026-11-08

### Nytt
- Layout för **stora skärmar** (4K, ultrabred) och **nya mobiler**: kompakt sidhuvud och knappar på 44 px.
- Förhandsvisningen visar en bild när webbläsaren inte kan visa PDF i sidan (Chrome på Android).
- Adminpanelen registrerar **skärmtyp** (klass, storlek, familj) utan att spara något personligt.
- Tjänsten anropar sig själv var 10:e minut för att inte somna.

## 3.8.0 — 2026-11-08

### Nytt
- **Adminpanel** (bara för ägaren, med lösenord) med diagram och förklaringar av system och användning: bara summor, aldrig personuppgifter.

## 3.7.0 — 2026-11-08

### Nytt
- **SEO**: titel, beskrivning och text per sida, `robots.txt`, `sitemap.xml` och ett riktigt 404 för sidor som inte finns.

## 3.6.0 — 2026-11-08

### Förbättrat
- Sajten levererar **en enda JavaScript-fil**, förvirrad och förkomprimerad: det som skickas är mycket mindre än förut.

## 3.5.0 — 2026-11-08

### Nytt
- Temat **Matrix Gamer**: regn av gröna tecken och neonglöd.

## 3.4.0 — 2026-11-08

### Förbättrat
- Stilarna går över till **Sass** och levereras som **en enda CSS**. Sidans struktur är densamma i alla teman: ett tema ändrar bara färger och formatering.

## 3.3.0 — 2026-11-07

### Nytt
- **Teman**: Premiado (det nya standardutseendet) och sju till (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala och Natal), alla i ljust och mörkt.
- Ny appikon.
