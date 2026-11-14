# Changelog (resum en català)

Resum traduït de `../CHANGELOG.md`: les mateixes versions, seccions i punts, més curts. El text complet és en portuguès.

## 3.40.0 — 2026-11-14

### Novetats
- **De 3 a 10 premis a la galeria:** als 24 dissenys de la galeria triau quants premis té la rifa (de 3 a 10; abans, 3 com a màxim). A partir de 6 passen a dues columnes. També a l'app de Windows.

## 3.39.0 — 2026-11-13

### Novetats
- **App de Windows 2.7:** la galeria i l'editor de plantilles accepten ara llatí estès, vietnamita, grec, ciríl·lic, xinès, japonès i coreà, com el lloc des de la 3.37 (el hindi, l'àrab i l'hebreu encara no hi són). Es descarrega des de la pàgina del Changelog.

## 3.38.0 — 2026-11-13

### Novetats
- **Botó «Comparteix»:** al peu i, després de generar els fitxers, a la targeta de lliurament. Obre una llista curta (compartir del mòbil o de l'ordinador, WhatsApp, Telegram, Facebook, correu i «Copia l'enllaç») per donar a conèixer el generador a altres associacions, escoles i comissions de festes. Els enllaços porten només l'adreça del lloc en l'idioma en què esteu: sense rastreig i sense desar res. Té tema al tutorial i vídeo.

## 3.37.0 — 2026-11-13

### Novetats
- **Més lletres a la galeria i a l'editor de plantilles:** els textos poden usar ara llatí estès (polonès, txec, romanès, turc…), **vietnamita, grec, ciríl·lic (rus, ucraïnès)**, **xinès, japonès i coreà**. El hindi, l'àrab i l'hebreu encara no hi són (necessiten una tecnologia d'escriptura que el generador de PDF no té) i donen un avís en lloc d'una imatge malmesa. Als PDF només canvia el text escrit per qui fa servir l'eina; el que ja sortia igual continua igual.

## 3.36.0 — 2026-11-13

### Novetats
- **Guia «Com fer» per a parròquies:** «Per a parròquies» (enllaç al peu), amb el pas a pas per fer una rifa parroquial: festes del patró, fires, obres, cistelles de Nadal i catequesi. És a les 22 llengües i recorda consultar a l'ajuntament si la rifa necessita llicència.

## 3.35.0 — 2026-11-13

### Novetats
- **App de Windows 2.6:** el menú «Extras» guanya «Desa la sol·licitud…» i «Obre una sol·licitud…» (un fitxer .rifas amb els números, el nom, les sèries, els colors i les marques de tall, sense plantilla ni camins), l'editor de plantilles pot afegir imatges (PNG o JPG) i «Visualitza → Visual» passa de 2 als 14 temes del lloc (només els colors). Inclou també el que ha arribat des de la 2.4: l'editor, els 24 dissenys de la galeria i les 22 llengües.

## 3.34.0 — 2026-11-13

### Novetats
- **Tres guies «Com fer» noves:** «Per a clubs», «Per als bombers» i «Per a festes de barri» (enllaços al peu), amb el pas a pas per fer una rifa en cada cas. Són a les 22 llengües i recorden consultar a l'ajuntament si la rifa necessita llicència.

## 3.33.0 — 2026-11-13

### Novetats
- **API pública per lots** (`/api/v1`, amb Swagger a `/api/v1/docs`): permet que altres programes generin diverses comandes de rifes a partir d'una sola plantilla, amb clau, quotes diàries i límits. Qui fa servir el lloc passa sempre primer.
- **Quatre llengües noves:** català, ucraïnès, indonesi i vietnamita. El lloc i l'aplicació per a Windows passen a tenir 22 llengües, amb tutorial, condicions, privadesa, guies «com fer-ho» i captures.
- **Textos per als cercadors editables per llengua:** el propietari edita al tauler d'administració els títols, les descripcions i les guies de cada llengua, desats a la base de dades i sense nou desplegament.

## 3.32.0 — 2026-11-13

### Novetats
- **20 plantilles noves a la galeria (24 en total):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Totes dibuixades des de zero per a aquest projecte, amb taló, al lloc web i a l'aplicació per a Windows (on la galeria passa a ser una llista desplegable).

## 3.31.0 — 2026-11-13

### Novetats
- **Editor de plantilles v2:** desfer i refer (Ctrl+Z, Ctrl+Y), duplicar (Ctrl+D), canviar l'ordre de dibuix, afegir el vostre logotip (PNG o JPG) i **compartir el disseny per enllaç**: es guarda 90 dies després de l'últim accés, sense imatges i sense dades de qui el comparteix (només apareix quan el servei té base de dades). La Política de privadesa ho diu.
- **Aplicació per a Windows 2.5:** rep l'editor de plantilles (menú Extres) i passa a Python 3.15.

### Millores
- El Changelog té un enllaç per baixar l'aplicació per a Windows.

## 3.30.0 — 2026-11-12

### Novetats
- **Pàgines «com fer-ho»:** dues guies escrites, «Per a escoles» i «Per a associacions» (enllaços al peu de pàgina), amb el pas a pas per fer una rifa: dissenyar la butlleta, una sèrie per classe o venedor, imprimir amb marques de tall, controlar les vendes i fer un sorteig verificable. Són en les 18 llengües i recorden de consultar amb l'autoritat local si la rifa necessita llicència.

## 3.29.0 — 2026-11-12

### Millores
- **Anuncis als costats:** quan els anuncis són activats (ara no ho són), en pantalles amples apareixen a banda i banda del contingut, un a cada costat, fixos i sense moure la pàgina; en les altres pantalles hi ha un sol bloc al final de la pàgina. Continuen sense aparèixer mai a l'editor, als fitxers generats ni a l'aplicació per a Windows.

## 3.28.0 — 2026-11-12

### Novetats
- **Anuncis de Google (preparats, desactivats):** el lloc pot mostrar un bloc d'anuncis de Google (AdSense) al final de la pàgina inicial, del tutorial, de «Quant a», del sorteig i del changelog. Mai no apareixen a l'editor, als fitxers generats, a la verificació de butlletes, al tauler d'administració ni a l'aplicació per a Windows, i a l'Espai Econòmic Europeu i al Regne Unit només després que trieu al missatge de consentiment de Google. La Política de privadesa ho diu, en les 18 llengües, quan els anuncis són activats; de moment són desactivats fins que el propietari del servei els configuri.

## 3.27.0 — 2026-11-12

### Novetats
- **Editor de plantilles:** en lloc d'una plantilla de Canva, dissenyeu la butlleta al lloc web (la pàgina «Editor de plantilles», enllaçada des del pas 1): afegiu textos, rectangles, línies i el número 0001 (una vegada, o dues si té taló), arrossegueu cada element al seu lloc amb el ratolí o les fletxes, canvieu colors, mides i el fons, i premeu «Fes servir aquesta plantilla». La pantalla fa servir la lletra Vera, la mateixa del PDF, de manera que el que veieu és el que obteniu; l'esborrany només es queda al navegador. Els textos no poden contenir seqüències com 0123, que el programa confondria amb el número de la butlleta (la pantalla i el servidor us avisen).

## 3.26.0 — 2026-11-12

### Novetats
- **Cinc temes nous:** Halloween, Platja, Diari antic, Terminal verd i Cartell de circ, cadascun clar i fosc. El lloc ara té 14 temes; la disposició és la mateixa en tots (només canvien els colors i la presentació).

## 3.25.0 — 2026-11-08

### Novetats
- **Una adreça per llengua per als cercadors:** cada llengua té la seva pròpia adreça (/en, /ja/tutorial…) amb títol, descripció i text en aquesta llengua, i el lloc diu a Google quines versions són equivalents (hreflang). El portuguès es queda a /. La llengua triada ara es veu a la barra d'adreces.

## 3.24.1 — 2026-11-08

### Millores
- **Caselles alineades:** «Un color per sèrie» i les altres caselles ara són al costat del seu text en lloc de ser a l'extrem de la targeta.

## 3.24.0 — 2026-11-08

### Millores
- **Tutorial amb captures del lloc web:** els temes bàsics del tutorial ara mostren el mateix lloc web, en les 18 llengües, en lloc de l'aplicació per a Windows.

## 3.23.0 — 2026-11-08

### Novetats
- **Tutorial i vídeo per a cada funcionalitat:** el tutorial rep un tema per funcionalitat (sèries, llista i full de control, marques de tall, galeria, la vostra marca, QR, sorteig, desar i compartir, instal·lar com a aplicació, temes), cadascun amb un vídeo curt gravat a la mateixa interfície, en portuguès i anglès.
- **Changelog, Condicions, Privadesa i Contacte en 18 llengües:** el text apareix en la llengua triada. El Changelog té un resum traduït de cada versió (el complet és en portuguès); els textos legals són traduccions sense revisió nativa i preval la versió portuguesa en cas de diferència.
- **Aplicació per a Windows 2.4** amb el que el lloc web ha guanyat des de la 3.10: un menú «Extres» amb sèries, prefixos i color per sèrie, números omesos, color dels números, logotip, marques de tall, galeria de plantilles, sorteig verificable i exportació de la llista (CSV) i del full de control; a més de l'aspecte de Nadal automàtic al desembre. El QR de verificació i la instal·lació com a aplicació només són al lloc web.

## 3.22.0 — 2026-11-08

### Millores
- **Contrast dels 9 temes mesurat de debò:** una prova al navegador mesura el text contra els píxels reals del fons, en clar i fosc (WCAG AA), i s'ha corregit el que fallava.
- Els números grans decoratius dels passos ja no els llegeixen els lectors de pantalla.

## 3.21.0 — 2026-11-08

### Novetats
- **Sorteig verificable** (pàgina «Sorteig»): sorteja números d'un interval (amb números que cal ometre) de manera que qualsevol persona pugui repetir-lo i obtenir el mateix resultat, amb una llavor pública. Funciona al vostre navegador i «Copia l'enllaç» comparteix el mateix sorteig.
- El mètode està documentat pas a pas, amb una implementació de referència que dona els mateixos números que el lloc web.

## 3.20.0 — 2026-11-08

### Novetats
- **QR a cada butlleta:** un codi QR de verificació en un racó de cada butlleta (plantilles d'una sola butlleta), amb opcions de racó i mida. En escanejar-lo s'obre una pàgina que confirma que aquest servei va emetre el codi per a aquella butlleta. Es signa amb una clau que només té el servidor; no es guarda res en cap base de dades. No demostra el pagament ni un premi.
- Només apareix quan el propietari del servei defineix la clau. Les sol·licituds amb QR tenen un límit de 10.000 números.

## 3.19.0 — 2026-11-08

### Novetats
- **La vostra marca:** el color dels números (qualsevol plantilla; el color de la sèrie guanya) i el **logotip** de la vostra associació a cada butlleta (PNG o JPG fins a 2 MB, plantilles d'una sola butlleta), amb racó i mida (del 10 al 40 %). El PNG manté la transparència.
- El logotip només es queda a la sessió (s'esborra amb ella i amb «Neteja-ho tot») i es veu a la previsualització.

## 3.18.0 — 2026-11-08

### Novetats
- **Galeria de plantilles:** trieu un de quatre dissenys (Bosque, Quermesse, Natal i Gala), escriviu títol, organització, fins a tres premis i la data, mireu la previsualització i premeu «Fes servir aquesta plantilla»: la plantilla i les xifres ja són a punt. Cada disseny és una butlleta amb taló.
- Els dissenys són originals d'aquest projecte, amb la lletra lliure Vera. La lletra només té l'alfabet llatí: les altres lletres mostren un avís.

## 3.17.0 — 2026-11-08

### Novetats
- **Marques de tall:** una casella al quadre del full (plantilles d'una sola butlleta) dibuixa petites línies als marges, allargant cada línia de tall. Necessita almenys 3 mm de marge.
- El **taló** (el número dues vegades a cada butlleta) ja funcionava: ara està provat i documentat.
- El **sagnat** ja es respecta: si el PDF de Canva té una TrimBox més petita que la pàgina, la butlleta és només el que hi ha a dins.

## 3.16.0 — 2026-11-08

### Novetats
- **Exporta la llista de butlletes (CSV):** un fitxer per a Excel o Calc, una butlleta per fila (sèrie, número i columnes buides Nom, Contacte i Pagat), respectant prefixos, sèries i números omesos.
- **Full de control de vendes (PDF):** una taula A4 per imprimir i omplir a mà (36 butlletes per pàgina, amb una casella «pagat»). En llengües les lletres de les quals el PDF no pot escriure, els encapçalaments surten en anglès.
- No es guarda res al servidor: la llista només surt del formulari.

## 3.15.0 — 2026-11-08

### Novetats
- **Sèries i prefixos:** text abans de les xifres (A- dona A-0001). Amb diverses sèries separades per comes, cadascuna repeteix l'interval i té els seus PDF. Un prefix admet lletres, espai, punt, guionet i barra (fins a 6 caràcters, sense xifres).
- **Omet números:** 13, 100-110 treu aquests números de la seqüència (el resum, els fitxers i la verificació només compten el que s'imprimeix).
- **Un color per a cada sèrie.**
- Tot això també va a «Copia l'enllaç» i a la previsualització.

## 3.14.0 — 2026-11-08

### Novetats
- **Instal·la com a aplicació (PWA):** instal·leu el lloc web al mòbil o a l'ordinador; la carcassa de l'aplicació s'obre fins i tot sense connexió (generar continua necessitant el servidor). Un service worker senzill només desa la pàgina, els fitxers de l'aplicació i els textos de la interfície, i mai no toca els vostres fitxers ni les sol·licituds de generació.

## 3.13.0 — 2026-11-08

### Novetats
- **Recorda el fitxer de xifres:** qui torna l'any vinent no ho repeteix. Es queda només al vostre navegador (mai al servidor) i es reutilitza amb una plantilla nova; triar-ne un altre el substitueix i «Neteja-ho tot» l'esborra.
- **Copia l'enllaç:** un botó que copia un enllaç amb els valors del formulari (des de, fins a, mode, màxim per fitxer, paper, marge i nom). Qui l'obre veu els mateixos valors; els fitxers mai no van a l'enllaç.

## 3.12.0 — 2026-11-08

### Novetats
- Pàgines de **Condicions d'ús**, **Política de privadesa** i **Contacte**, enllaçades al peu de pàgina. Són versions provisionals, que cal revisar amb suport jurídic abans que el servei cobri res.
- **Botó de donatiu** al peu de pàgina: només apareix quan el propietari defineix l'enllaç. El correu de contacte i el nom del responsable també vénen de la configuració del servidor, mai del codi.

## 3.11.0 — 2026-11-08

### Novetats
- **Embut d'ús** al tauler d'administració: quants esdeveniments hi ha a cada etapa (sessió, plantilla, xifres, previsualització, generació, baixada) i quina part de l'etapa anterior va arribar a la següent. Mostra on la gent abandona. Compta esdeveniments, no persones.

## 3.10.0 — 2026-11-08

### Novetats
- Aquesta pàgina: el **Changelog**, amb tot el que canvia, versió a versió.
- Al **desembre** el tema visual automàtic és **Nadal** (per a qui no n'ha triat mai cap). Triar un altre tema continua recordant-se.

### Millores
- Una dependència menys al servidor (`python-multipart` ja no es feia servir: els fitxers arriben com a cos en brut).

## 3.9.0 — 2026-11-08

### Novetats
- Disposició pensada per a **pantalles grans** (4K, ultra-amples) i **mòbils recents**: capçalera compacta i botons de 44 px.
- La previsualització mostra una imatge quan el navegador no pot mostrar PDF dins la pàgina (Chrome a l'Android).
- El tauler d'administració registra el **tipus de pantalla** (classe, mida, família) sense desar res de personal.
- El servei es crida a si mateix cada 10 minuts perquè no s'adormi.

## 3.8.0 — 2026-11-08

### Novetats
- **Tauler d'administració** (només per al propietari, amb contrasenya) amb gràfics i explicacions del sistema i de l'ús: només agregats, mai dades personals.

## 3.7.0 — 2026-11-08

### Novetats
- **SEO**: títol, descripció i text per pàgina, `robots.txt`, `sitemap.xml` i un 404 de debò per a les pàgines que no existeixen.

## 3.6.0 — 2026-11-08

### Millores
- El lloc entrega **un sol fitxer JavaScript**, ofuscat i precomprimit: el que viatja és molt més petit que abans.

## 3.5.0 — 2026-11-08

### Novetats
- Tema visual **Matrix Gamer**: caràcters verds que cauen i resplendor de neó.

## 3.4.0 — 2026-11-08

### Millores
- Els estils passen a **Sass** i s'entreguen en **un sol CSS**. L'estructura de la pàgina és la mateixa a tots els temes: un tema només canvia colors i format.

## 3.3.0 — 2026-11-07

### Novetats
- **Temes visuals**: Premiado (el nou aspecte per defecte) i set més (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala i Natal), cadascun clar i fosc.
- Icona nova de l'aplicació.
