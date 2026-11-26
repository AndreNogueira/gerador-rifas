# Changelog (rezumat în română)

Rezumat tradus al `../CHANGELOG.md`: aceleași versiuni, secțiuni și puncte, mai scurte. Textul complet este în portugheză.

## 3.90.0 — 2026-11-26

### Corectat
- **Pagina în portugheză nu mai schimbă singură limba**: vizitarea unei adrese fără prefix (`/`, `/tutorial`, …) fără ca browserul să indice portugheza — cazul multor roboți de căutare și al unor browsere — făcea ca site-ul să rescrie singur URL-ul și tot conținutul în engleză. Fără prefix înseamnă acum mereu portugheză, așa cum era planul; cele 21 de limbi cu prefix merg la fel ca înainte. `robots.txt` nu mai blochează complet nici `/api/linguas`, `/api/textos`, `/api/guia(s)` și documentația API-ului public (`/api/v1/docs`), ca motoarele de căutare să poată randa și indexa bine site-ul.

### Îmbunătățit
- **Selector de limbă mai rapid**: numele native ale limbilor din selector (precum «Tiếng Việt» sau «Čeština») folosesc acum fontul sistemului în loc de cel al mărcii, așa că pagina nu mai trebuie să descarce glife suplimentare doar pentru a le arăta — lucru care întârzia textul principal și îl deplasa uneori.

## 3.89.0 — 2026-11-26

### Îmbunătățit
- **Încă trei biblioteci de imagini de contur în lista de prețuri: Tabler Icons, Lucide și Material Symbols** (fără a cere mențiune): peste 100 de articole au câștigat alternative din aceste biblioteci, alese una câte una ca să reprezinte chiar articolul (spre deosebire de cele anterioare, nu există o metodă automată de a le găsi). Spre deosebire de imaginile color, acestea se colorează cu culoarea textului din acel moment — a site-ului, a aplicației Windows sau a hârtiei alese în PDF — ca să nu devină niciodată invizibile pe o temă întunecată sau o hârtie întunecată.

## 3.88.0 — 2026-11-21

### Îmbunătățit
- **Încă două biblioteci de imagini în lista de prețuri: Twemoji și OpenMoji**: se alătură lui Noto Emoji și Fluent Emoji 3D, fără a înlocui nicio imagine existentă — selectorul grupează acum imaginile pe biblioteci, cu numele fiecăreia. Twemoji (CC BY 4.0) și OpenMoji (CC BY-SA 4.0) cer menționarea autorilor, care apare în Politica de confidențialitate și, doar atunci când se folosește chiar o astfel de imagine, în subsolul PDF-ului și al etichetelor de ridicare generate.

## 3.87.0 — 2026-11-21

### Îmbunătățit
- **Mai multe imagini la alegere în lista de prețuri, de la Fluent Emoji 3D al Microsoft (licență MIT, fără a cere mențiune)**: toate cele 93 de articole din catalog au câștigat, pe lângă imaginile Noto Emoji de până acum, o alternativă în stil 3D oriunde există pentru acel cod — nicio imagine existentă nu a fost înlocuită.

## 3.86.0 — 2026-11-21

### Îmbunătățit
- **Spațiu între bilete și semne de tăiere între fiecare**: activând semnele de tăiere, spațiul liber care înainte doar mărea marginea devine spațiu între bilete, iar semnele (înainte doar în marginile foii) apar acum și între fiecare bilet.

## 3.85.0 — 2026-11-21

### Corectat
- **Pagină 404 reală**: o legătură greșită arăta generatorul ascuns sub starea 404. Acum apare o pagină reală, tradusă, „Pagina nu a fost găsită”, cu legătură de revenire.
- **Pictogramă de rezervă (favicon.ico)**: pentru instrumentele vechi care verifică doar acea cale.

## 3.84.0 — 2026-11-21

### Noutăți
- **Desenul „Aniversare” în galerie și în lista de prețuri**: baloane, ghirlande și confetti în roz, turcoaz și galben — al 25-lea desen care se alătură celor existente, ca o petrecere de aniversare să aibă propriul stil pe bilete, lista de prețuri și jetoane.

## 3.83.0 — 2026-11-21

### Îmbunătățit
- **Mai multe imagini la alegere pentru un articol din lista de prețuri**: fiecare articol din catalog poate avea acum până la 8 imagini (înainte 5) — toate cele 93 au primit cel puțin o alternativă nouă, aleasă pe potriva lor (apa un val, cafeaua un mate, prăjitura confetti…).

## 3.82.0 — 2026-11-20

### Corectat
- **Margini neuniforme la umplerea foii cu mai puține bilete decât încăpeau**: a cere mai puține bilete pe foaie decât maximul le lăsa lipite în stânga sus, cu tot spațiul liber în dreapta jos — o tăietură dreaptă nu mai separa bine fiecare bilet. Acum sunt mereu centrate, cu aceeași margine pe toate cele patru laturi.

## 3.81.0 — 2026-11-20

### Noutăți
- **Etichete de ridicare**: se plătește într-un loc și se ridică din altul? Pe pagina listei de prețuri, fiecare articol devine o etichetă cu imaginea, numele, prețul (dacă vrei) și zona de ridicare (barul, bucătăria…), cu copiile pe care le alegi, 24 pe foaie A4 cu ghidaje de tăiere și o culoare pe zonă. Un combo dă o etichetă pe articol, fiecare în zona secțiunii sale (site și aplicația Windows; cu tutorial și videoclipuri).

## 3.80.0 — 2026-11-20

### Noutăți
- **Combo-uri între secțiuni în lista de prețuri**: reunește 2 până la 4 articole din catalog, chiar din secțiuni diferite (de exemplu un sandviș și o băutură), la un singur preț. Combo-ul apare într-o secțiune nouă, «Combo-uri și meniuri», cu imaginile articolelor alăturate, și poate avea un nume propriu (site și aplicația Windows).

## 3.79.0 — 2026-11-20

### Noutăți
- **Culori și logo în lista de prețuri**: poți schimba culoarea principală, cea de accent și cea a hârtiei desenului (prețurile se ajustează singure ca să rămână mereu lizibile) și poți pune logo-ul asociației tale (PNG sau JPG) în antet, la stânga sau la dreapta, ori în subsol (site și aplicația Windows). Culorile și locul rămân în fișierul listei și în linkul partajat; logo-ul servește doar la desenarea previzualizării și a PDF-ului și nu se păstrează niciodată.

## 3.78.0 — 2026-11-20

### Noutăți
- **Până la 5 imagini la alegere pentru fiecare articol**: în lista de prețuri, apasă pe imaginea unui articol din catalog și alege-o pe cea care îți place cel mai mult dintre cel mult 5 (apa poate fi o picătură, un robinet, gheață, un pahar…). Alegerea se vede în PDF și rămâne în fișierul listei și în linkul partajat (site și aplicația Windows).

## 3.77.0 — 2026-11-20

### Îmbunătățit
- **Liste și rânduri mai ordonate în lista de prețuri**: toate listele derulante de pe site arată acum ca restul câmpurilor, cu o săgeată care urmează tema (deschisă și închisă). În lista de prețuri, × pentru a scoate un articol și butonul pentru poză ocupă mult mai puțin loc, prețurile nu mai sar pe al doilea rând, iar pe telefon numele stă sus și câmpurile dedesubt.

## 3.76.0 — 2026-11-20

### Noutăți
- **Poze proprii în lista de prețuri**: la fiecare articol poți apăsa «Poză» și pune propria imagine (PNG sau JPG) în locul pictogramei (până la 20 pe listă; site și aplicația Windows). Poza este micșorată pe calculatorul tău și servește doar la desenarea previzualizării și a PDF-ului: nu se păstrează pe server, în fișierul listei și nici în linkul partajat.

## 3.75.0 — 2026-11-20

### Noutăți
- **Partajarea listei de prețuri prin link** (pe site, când serviciul are bază de date): «Partajează prin link» pe pagina listei creează un link pe care îl poate deschide oricine ca să vadă și să continue lista ta (texte, articole, prețuri și desen). Se păstrează 90 de zile de la ultimul acces, fără nimic despre cine o partajează; Politica de confidențialitate a fost actualizată.

## 3.74.0 — 2026-11-20

### Noutăți
- **Două mărimi în lista de prețuri**: activează «Două mărimi (două prețuri pe articol)» (site și aplicația Windows) ca să scrii două prețuri la fiecare articol (de exemplu mic și mare, sau articolul și meniul). Cele două coloane ies aliniate, cu numele alese de tine deasupra (implicit «Mic» și «Mare»), și se salvează în fișierul listei.

## 3.73.0 — 2026-11-20

### Noutăți
- **Cartonașe de masă**: la formatul listei de prețuri alege «Cartonașe de masă (4 pe coala A4)» (site și aplicația Windows), iar lista iese ca cartonașe A6, patru pe o coală A4 cu ghidaje de tăiere punctate, gata de tipărit și tăiat pentru mese (până la 12 articole).

## 3.72.0 — 2026-11-20

### Noutăți
- **Listă de prețuri «tablă»**: un desen nou în lista «Ocazie și temă» (și în aplicația Windows): fundal verde închis de tablă școlară, ramă de lemn și text cu cretă (alb și galben), ideal pentru stand, terasă sau clasă.

## 3.71.0 — 2026-11-20

### Noutăți
- **Bonuri de jetoane numerotate** (în lista de prețuri, cu o monedă inventată; și «Extras → Listă de prețuri… → Bonuri numerotate…» în aplicația Windows): alege câte jetoane valorează fiecare bon, titlul și o notă, vezi bonul în desenul listei și creează-le. Se continuă în generatorul de tombole, care numerotează bonurile cu serii, coduri QR de verificare și coli gata de tipărit.

## 3.70.0 — 2026-11-20

### Noutăți
- **Generator de liste de prețuri pentru petreceri** (`/precario`, și «Extras → Listă de prețuri…» în aplicația Windows): alege ocazia (este sugerată cea din perioada anului) și articolele dintr-un catalog cu imagini, scrie prețurile în moneda țării tale sau într-una inventată (jetoane…) și descarcă PDF-ul (sau o imagine) gata de tipărit, în A5, A4 sau A3 și cu cele 24 de desene din galerie. Există și un ghid nou: «Cum faci lista de prețuri a unei petreceri».

## 3.69.0 — 2026-11-19

### Noutăți
- **Portugheza braziliană** (`/pt-br`): site-ul, ghidurile și paginile juridice există acum și în portugheza braziliană, cu vocabularul ei, o Politică de confidențialitate adaptată LGPD din Brazilia și limba aleasă automat când browserul este setat pe pt-BR. Portugheza din Portugalia rămâne la fel, fără prefix în adresă.

## 3.68.0 — 2026-11-19

### Noutăți
- **Trei ghiduri noi, pe teme** (nu pe public): cum numerotezi biletele, cum faci o tragere verificabilă (trimite la pagina «Tragere») și câte bilete faci și la ce preț. Sunt în «Toate ghidurile» (`/como-fazer`), în 22 de limbi.

## 3.67.0 — 2026-11-19

### Noutăți
- **Index al ghidurilor «Cum faci»** (`/como-fazer`): o pagină cu toate ghidurile și un rezumat al fiecăruia; fiecare ghid se încheie cu linkuri către celelalte. Și în meniul «Ajutor» («Toate ghidurile»).
- Ghidurile și indexul spun Google pe ce cale se află (Acasă › Cum faci › ghid), ca să poată apărea în rezultate.

## 3.66.0 — 2026-11-19

### Noutăți
- **Invitație de a lăsa un comentariu:** după ce descărcați biletele, apare (o singură dată pe dispozitiv) un mesaj discret care vă invită să lăsați un comentariu, anonim dacă doriți. Îl puteți închide cu „Nu acum”.

## 3.65.0 — 2026-11-19

### Îmbunătățit
- **Un site mai ușor și mai sigur:** cine doar generează bilete descarcă cu 24 % mai puțin cod (panoul de administrare, editorul de șabloane și tragerea se încarcă doar când deschideți pagina). Site-ul trimite acum și antete de securitate și răspunde verificatoarelor de linkuri și previzualizărilor de partajare.

## 3.64.0 — 2026-11-19

### Noutăți
- **Copie de siguranță săptămânală a datelor panoului de administrare:** în fiecare luni serviciul salvează, în stocarea aceluiași furnizor ca baza de date, o copie a istoricului, obiectivelor, jurnalului de acțiuni, comentariilor și textelor SEO (ultimele 8 săptămâni), cu un script de restaurare.

## 3.63.0 — 2026-11-19

### Noutăți
- **Performanța reală a site-ului în statistici:** panoul de administrare arată, pe zile, cât durează să apară pagina, cât se mișcă conținutul și cât durează să răspundă la un clic, măsurat în browserele vizitatorilor (telefon și computer). Doar trei numere anonime pe vizită; Politica de confidențialitate a fost actualizată.

## 3.62.0 — 2026-11-19

### Noutăți
- **Proveniența vizitelor în statistici:** panoul de administrare arată acum de unde vin vizitele, în categorii generale (căutare, rețele sociale, e-mail, alte site-uri sau directe) și pe campanii (utm_source), pentru a măsura o promovare. Adresa paginii de origine și IP-ul nu se păstrează niciodată; Politica de confidențialitate a fost actualizată.

## 3.61.0 — 2026-11-19

### Noutăți
- **Jurnal de acțiuni în panoul de administrare:** cine ce a făcut și când în panou se păstrează 400 de zile (autentificări, comentarii șterse sau ascunse, chei API, texte SEO, obiective), fără date ale vizitatorilor sau parole.

## 3.60.0 — 2026-11-19

### Noutăți
- **Obiective zilnice în panoul de administrare:** responsabilul stabilește o țintă pe zi (sesiuni, generări, numere generate, descărcări…) și vede dacă ultima zi a atins-o, media ultimelor 7 zile și în câte a fost atinsă; raportul zilnic prin e-mail conține aceeași secțiune.

## 3.59.0 — 2026-11-19

### Noutăți
- **Stări ale comentariilor în panoul de administrare:** responsabilul poate marca fiecare comentariu ca citit, favorit sau ascuns (un comentariu ascuns dispare de pe pagina publică, dar nu se pierde), poate filtra după stare și vedea câte sunt necitite.

## 3.58.0 — 2026-11-19

### Noutăți
- **Cotele găzduirii gratuite în panoul de administrare:** se vede câte din cele 750 de ore lunare Render a consumat serviciul (cu proiecția până la sfârșitul lunii) și cât spațiu ocupă baza de date în planul gratuit Neon, cu avertisment în raportul zilnic prin e-mail înainte să se epuizeze cotele.

## 3.57.0 — 2026-11-19

### Noutăți
- **Marcaje de versiune în graficele panoului de administrare:** fiecare grafic zilnic marchează ziua în care a venit o versiune nouă a aplicației (iar raportul zilnic spune care), pentru a lega o creștere a erorilor sau a timpului de răspuns de actualizarea care a cauzat-o.

## 3.56.0 — 2026-11-19

### Noutăți
- **Rezumat săptămânal și lunar prin e-mail pentru responsabilul site-ului:** luni sosește rezumatul săptămânii, iar pe 1 cel al lunii, cu totalurile comparate cu perioada anterioară și o miniatură a fiecărei zile. Citesc din istoricul permanent. Doar numărători.

## 3.55.0 — 2026-11-19

### Noutăți
- **Alerte imediate prin e-mail pentru responsabilul site-ului:** la o serie de erori de server, reporniri ale motorului, memorie aproape de limită sau bază de date fără răspuns, vine imediat un avertisment (fără a aștepta raportul zilnic și fără repetare timp de 6 ore). Doar numărători.

## 3.54.0 — 2026-11-19

### Noutăți
- **Istoric permanent în panoul de administrare:** după miezul nopții se salvează un rezumat al fiecărei zile, deci evoluția zilnică arată acum luni și până la 2 ani (înainte doar 90 de zile). Doar numărători, ca restul panoului.

## 3.53.0 — 2026-11-19

### Noutăți
- **Raport zilnic prin e-mail pentru responsabilul site-ului:** în fiecare zi, imediat după miezul nopții, sosește un e-mail cu tot ce s-a înregistrat în ziua care tocmai s-a încheiat (utilizare, public, erori și resursele serverului), comparat cu media celor 7 zile anterioare, pentru a urmări aplicația fără a deschide panoul. Doar numărători: niciodată datele vizitatorilor.

## 3.52.0 — 2026-11-19

### Îmbunătățit
- **Comentarii fără adresă IP:** în loc de IP se păstrează doar țara din care a fost trimis comentariul (o vede doar responsabilul site-ului). Adresa IP nu se mai păstrează: cele ale comentariilor anterioare au fost șterse, iar Politica de confidențialitate a fost actualizată.

## 3.51.0 — 2026-11-19

### Noutăți
- **Comentarii:** o pagină «Comentarii» unde oricine vede ce cred alții despre generator și o pagină pentru a-l lăsa pe al tău: poți rămâne anonim sau poți arăta un nume (fără nume apare «Vizitator nr. …»). Adresa IP este păstrată doar pentru responsabilul site-ului, contra abuzurilor, nu este afișată niciodată și se șterge după 90 de zile.
- **Raportează o problemă:** pagină nouă în care descrii o eroare; la apăsarea «Deschide» ea este creată direct pe GitHub-ul proiectului, fără cont (IP-ul tău nu este trimis, iar informațiile tehnice ale browserului doar dacă le adaugi).
- Ambele pagini și butoanele «Comentarii» și «Raportează o problemă» sunt la vedere în antet, meniu și subsol; Politica de confidențialitate (22 de limbi) explică ce se păstrează.

## 3.50.0 — 2026-11-18

### Îmbunătățit
- **Un antet care se adaptează ecranului:** toate opțiunile sunt aliniate la dreapta, pe un singur rând și fără goluri, iar pe măsură ce ecranul se micșorează trec pe rând într-un meniu «hamburger» (întâi modul luminos/întunecat și stilul, la urmă donația). Pe telefon rămân doar numele aplicației și butonul meniului, care deschide paginile, ajutorul, distribuirea și setările.

## 3.49.0 — 2026-11-18

### Noutăți
- **Panou cu evoluția zi cu zi:** o nouă vizualizare «Evoluție zilnică» arată, pe până la 90 de zile, tot ce salvează serverul în baza de date (sesiuni, generări, numere generate, limbi, țări, stiluri, galerie, editor, API, cereri, timpi de răspuns, CPU și memorie…), cu tendința fiecărui indicator și descărcarea tuturor în CSV. Este o funcție a panoului proprietarului: vizitatorii nu observă nicio diferență.

## 3.48.0 — 2026-11-18

### Îmbunătățit
- **Meniul «Ajutor» în antet:** tutorialul, videoclipul și ghidurile «Cum se face» sunt acum într-o singură filă, «Ajutor». Antetul este mai scurt, iar numele aplicației apare mereu întreg, pe un singur rând, în orice limbă și la orice dimensiune a ecranului.

## 3.47.0 — 2026-11-15

### Îmbunătățit
- **Galeria de șabloane:** lista modelelor nu mai este tăiată sau pusă greșit în unele teme; fiecare premiu are numărul lui; fiecare casetă de text arată limita de caractere (de exemplu 12/50); iar butonul «Folosește acest șablon» nu mai stă lipit de ultima casetă.
- **Data tragerii într-un calendar propriu:** în locul câmpului browserului (care arăta «zz.ll.aaaa» și un selector într-o limbă diferită de cea a site-ului) există un calendar în cele 22 de limbi, cu lunile și zilele săptămânii în limba aleasă, data scrisă așa cum o scrie acea limbă, prima zi a săptămânii corectă și butoanele «Astăzi» și «Șterge». Funcționează cu tastatura (săgeți, Page Up/Down, Home/End, Enter și Esc).
- **Un «Despre» mai complet:** textul a fost rescris, în cele 22 de limbi, și explică pentru cine este generatorul, ce face, ce faceți după tipărire, cum protejează confidențialitatea și unde poate fi folosit.

## 3.46.0 — 2026-11-15

### Îmbunătățit
- **Donația, mai vizibilă:** când serviciul are un link de donații, butonul apare acum în antet (lângă «Distribuie») și, după generarea fișierelor, cu o scurtă invitație. Rămâne și în subsol.

## 3.45.0 — 2026-11-14

### Îmbunătățit
- **Galeria de șabloane pe un singur rând:** cele 24 de modele se aleg acum într-o casetă pe un rând în care fiecare opțiune arată o miniatură a șablonului, în loc de o listă lungă de butoane. Funcționează cu mouse-ul, atingerea și tastatura (săgeți, Home/End, o literă, Enter și Esc).

## 3.44.0 — 2026-11-14

### Îmbunătățit
- **Confidențialitate:** contorizările de utilizare includ acum țara vizitei (doar codul, dedus de rețeaua găzduirii; adresa IP tot nu este păstrată). Politica de confidențialitate o explică în toate cele 22 de limbi.

## 3.43.1 — 2026-11-14

### Îmbunătățit
- **Subsol mai curat:** ghidurile «Cum se face» apar acum doar în grupul din antet; nu se mai repetă în josul paginii.

## 3.43.0 — 2026-11-14

### Îmbunătățit
- **Data tragerii într-un calendar:** în galeria de șabloane alegeți data într-un calendar și apoi cum apare pe bilet (31.12.2026, 31 dec. 2026, 31 decembrie 2026 sau cu ziua săptămânii), scrisă în limba site-ului. O puteți scrie și manual, acum până la 60 de caractere.
- **Texte mai late:** paginile de text (ghiduri, tutorial, termeni…) ocupă acum toată lățimea paginii, cu mai puține rânduri și paragrafe.

## 3.42.0 — 2026-11-14

### Îmbunătățit
- **Antet:** noul grup «Cum se face», lângă tutorial, reunește ghidurile (școli, asociații, cluburi, pompieri, sărbători de cartier și parohii). Butonul «Distribuie» s-a mutat din subsol în antet, evidențiat, iar lista lui arată pictogramele WhatsApp, Telegram, Facebook, e-mail și «Copiază linkul».

## 3.41.0 — 2026-11-14

### Îmbunătățit
- **Previzualizare automată:** când schimbați șablonul, cifrele, logoul sau orice câmp care modifică pagina finală (numere, cifre, coală, serii, culori, QR…), previzualizarea cu numere reale se reface singură, fără să apăsați „Previzualizare”. Dacă ceva nu e în regulă, motivul apare lângă vizualizator, fără ferestre.

## 3.40.0 — 2026-11-14

### Noutăți
- **De la 3 la 10 premii în galerie:** în toate cele 24 de modele din galerie alegeți câte premii are biletul (de la 3 la 10; înainte cel mult 3). De la 6 în sus merg pe două coloane. Și în aplicația Windows.

## 3.39.0 — 2026-11-13

### Noutăți
- **Aplicația Windows 2.7:** galeria și editorul de șabloane acceptă acum latina extinsă, vietnameza, greaca, chirilica, chineza, japoneza și coreeana, ca site-ul din versiunea 3.37 (hindi, araba și ebraica încă lipsesc). Se descarcă din pagina Changelog.

## 3.38.0 — 2026-11-13

### Noutăți
- **Butonul «Distribuie»:** în subsol și, după generarea fișierelor, pe cardul de livrare. Deschide o listă scurtă (partajarea telefonului sau a computerului, WhatsApp, Telegram, Facebook, e-mail și «Copiază linkul») ca alte asociații, școli și comitete de sărbători să afle de generator. Linkurile conțin doar adresa site-ului în limba folosită: fără urmărire și fără să se salveze nimic. Are un subiect în tutorial și un videoclip.

## 3.37.0 — 2026-11-13

### Noutăți
- **Mai multe litere în galerie și în editorul de șabloane:** textele pot folosi acum latina extinsă (poloneză, cehă, română, turcă…), **vietnameza, greaca, chirilica (rusă, ucraineană)**, **chineza, japoneza și coreeana**. Hindi, araba și ebraica încă lipsesc (cer o tehnologie de scriere pe care generatorul de PDF nu o are) și dau un avertisment în loc de o imagine stricată. În PDF se schimbă doar textul scris de utilizator; ce ieșea deja la fel rămâne la fel.

## 3.36.0 — 2026-11-13

### Noutăți
- **Ghid «Cum faci» pentru parohii:** «Pentru parohii» (link în subsol), cu pașii pentru a face o tombolă parohială: hramuri, târguri, reparații, pachete de Crăciun și catehism. Este în toate cele 22 de limbi și amintește să verifici la primărie dacă tombola cere autorizație.

## 3.35.0 — 2026-11-13

### Noutăți
- **Aplicația Windows 2.6:** meniul «Extras» primește «Salvează cererea…» și «Deschide cererea…» (un fișier .rifas cu numerele, numele, seriile, culorile și marcajele de tăiere, fără șablon sau căi), editorul de șabloane poate adăuga imagini (PNG sau JPG), iar «Vizualizare → Vizual» trece de la 2 la cele 14 teme ale site-ului (doar culorile). Aduce și ce a apărut de la 2.4: editorul, cele 24 de modele din galerie și cele 22 de limbi.

## 3.34.0 — 2026-11-13

### Noutăți
- **Trei ghiduri noi «Cum faci»:** «Pentru cluburi», «Pentru pompieri» și «Pentru sărbători de cartier» (linkuri în subsol), cu pașii pentru a face o tombolă în fiecare caz. Sunt în toate cele 22 de limbi și amintesc să verifici la primărie dacă tombola cere autorizație.

## 3.33.0 — 2026-11-13

### Noutăți
- **API public pentru loturi** (`/api/v1`, cu Swagger la `/api/v1/docs`): permite altor programe să genereze mai multe comenzi de bilete dintr-un singur șablon, cu cheie, cote zilnice și limite. Cei care folosesc site-ul au mereu prioritate.
- **Patru limbi noi:** catalană, ucraineană, indoneziană și vietnameză. Site-ul și aplicația Windows vorbesc acum 22 de limbi, cu tutorial, termeni, confidențialitate, ghiduri practice și capturi.
- **Texte pentru motoarele de căutare editabile pe limbă:** proprietarul editează în panoul de administrare titlurile, descrierile și ghidurile fiecărei limbi, salvate în baza de date și fără o nouă implementare.

## 3.32.0 — 2026-11-13

### Noutăți
- **20 de șabloane noi în galerie (24 în total):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Toate desenate de la zero pentru acest proiect, cu cotor, pe site și în aplicația Windows (unde galeria devine o listă derulantă).

## 3.31.0 — 2026-11-13

### Noutăți
- **Editor de șabloane v2:** anulează și refă (Ctrl+Z, Ctrl+Y), duplică (Ctrl+D), schimbă ordinea desenării, adaugă sigla (PNG sau JPG) și **distribuie desenul printr-un link**: se păstrează 90 de zile după ultimul acces, fără imagini și fără date despre cine distribuie (apare doar când serviciul are bază de date). Politica de confidențialitate o spune.
- **Aplicația Windows 2.5:** primește editorul de șabloane (meniul Extra) și trece la Python 3.15.

### Îmbunătățit
- Changelog-ul are un link pentru descărcarea aplicației Windows.

## 3.30.0 — 2026-11-12

### Noutăți
- **Pagini „Cum se face”:** două ghiduri scrise, „Pentru școli” și „Pentru asociații” (linkuri în subsol), cu pașii pentru o tombolă: desenarea biletului, o serie pe clasă sau vânzător, tipărire cu semne de tăiere, controlul vânzărilor și o tragere verificabilă. Sunt în toate cele 18 limbi și amintesc să verifici la primărie dacă tombola cere autorizație.

## 3.29.0 — 2026-11-12

### Îmbunătățit
- **Reclame în lateral:** când reclamele sunt active (deocamdată nu sunt), pe ecranele late apar în ambele părți ale conținutului, câte una pe fiecare parte, fixe și fără a muta pagina; pe celelalte ecrane există un singur bloc la sfârșitul paginii. Tot nu apar în editor, în fișierele generate sau în aplicația Windows.

## 3.28.0 — 2026-11-12

### Noutăți
- **Reclame Google (pregătite, dezactivate):** site-ul poate afișa un bloc de reclame Google (AdSense) la sfârșitul paginii de start, al tutorialului, al „Despre”, al tragerii și al changelog-ului. Nu apar niciodată în editor, în fișierele generate, la verificarea biletelor, în panou sau în aplicația Windows, iar în Spațiul Economic European și în Regatul Unit doar după ce alegeți în mesajul de consimțământ al Google. Politica de confidențialitate o spune, în cele 18 limbi, când reclamele sunt active; deocamdată sunt dezactivate până când proprietarul serviciului le configurează.

## 3.27.0 — 2026-11-12

### Noutăți
- **Editor de șabloane:** în loc de un șablon Canva, proiectați biletul pe site (pagina „Editor de șabloane”, legată de la pasul 1): adăugați texte, dreptunghiuri, linii și numărul 0001 (o dată, sau de două ori cu cotor), trageți fiecare element cu mouse-ul sau cu săgețile, schimbați culorile, dimensiunile și fundalul și apăsați „Folosește acest șablon”. Ecranul folosește fontul Vera, același ca PDF-ul, deci ce vedeți obțineți; ciorna rămâne doar în browser. Textele nu pot conține secvențe ca 0123, pe care programul le-ar confunda cu numărul biletului (avertizează ecranul și serverul).

## 3.26.0 — 2026-11-12

### Noutăți
- **Cinci teme noi:** Halloween, Plajă, Ziar vechi, Terminal verde și Afiș de circ, fiecare în variantă luminoasă și întunecată. Site-ul are acum 14 teme; structura este aceeași în toate (se schimbă doar culorile și aspectul).

## 3.25.0 — 2026-11-08

### Noutăți
- **O adresă pentru fiecare limbă, pentru motoarele de căutare:** fiecare limbă are adresa ei (/en, /ja/tutorial…), cu titlu, descriere și text în acea limbă, iar site-ul spune Google care versiuni sunt echivalente (hreflang). Portugheza rămâne la /. Limba aleasă apare acum în bara de adrese.

## 3.24.1 — 2026-11-08

### Îmbunătățit
- **Căsuțe de bifat aliniate:** «O culoare pentru fiecare serie» și celelalte căsuțe stau acum lângă text, nu la celălalt capăt al cardului.

## 3.24.0 — 2026-11-08

### Îmbunătățit
- **Tutorial cu capturi de ecran ale site-ului:** subiectele de bază ale tutorialului arată acum site-ul în sine, în toate cele 18 limbi, în loc de aplicația Windows.

## 3.23.0 — 2026-11-08

### Noutăți
- **Tutorial și video pentru fiecare funcție:** tutorialul are câte un subiect pentru fiecare funcție (serii, listă și fișă de control, semne de tăiere, galerie, marcă proprie, QR, extragere, salvare și partajare, instalare ca aplicație, teme), fiecare cu un video scurt înregistrat chiar în interfață, în portugheză și engleză.
- **Changelog, Termeni, Confidențialitate și Contact în 18 limbi:** textul apare în limba aleasă. Changelogul are un rezumat tradus al fiecărei versiuni (cel complet este în portugheză); textele juridice sunt traduceri fără revizuire nativă și, în caz de diferențe, prevalează versiunea portugheză.
- **Aplicația Windows 2.4** cu ce a primit site-ul de la 3.10: meniul „Extra” cu serii, prefixe și culoare pe serie, numere sărite, culoarea numerelor, logo, semne de tăiere, galerie de șabloane, extragere verificabilă și export al listei (CSV) și al fișei de control; plus aspectul de Crăciun automat în decembrie. QR-ul de verificare și instalarea ca aplicație rămân doar pe site.

## 3.22.0 — 2026-11-08

### Îmbunătățit
- **Contrastul celor 9 teme măsurat cu adevărat:** un test în browser măsoară textul față de pixelii reali ai fundalului, în mod luminos și întunecat (WCAG AA), iar ce nu trecea a fost corectat.
- Numerele mari decorative ale pașilor nu mai sunt citite de cititoarele de ecran.

## 3.21.0 — 2026-11-08

### Noutăți
- **Extragere verificabilă** (pagina „Extragere”): extrage numere dintr-un interval (cu numere de sărit) astfel încât oricine să o poată repeta și să obțină același rezultat, cu o sămânță publică. Totul se face în browser, iar „Copiază linkul” partajează aceeași extragere.
- Metoda este descrisă pas cu pas, cu o implementare de referință care dă aceleași numere ca site-ul.

## 3.20.0 — 2026-11-08

### Noutăți
- **QR pe fiecare bilet:** un cod QR de verificare într-un colț al fiecărui bilet (șabloane cu un singur bilet), cu alegerea colțului și a mărimii. Scanarea deschide o pagină care confirmă că acest serviciu a emis codul pentru acel bilet. Este semnat cu o cheie pe care o are doar serverul; fără bază de date. Nu dovedește plata sau câștigul.
- Apare doar dacă proprietarul serviciului setează cheia. Cererile cu QR au un plafon de 10 000 de numere.

## 3.19.0 — 2026-11-08

### Noutăți
- **Marcă proprie:** culoarea numerelor (orice șablon; culoarea seriei are prioritate) și **sigla** asociației pe fiecare bilet (PNG sau JPG până la 2 MB, șabloane cu un singur bilet), cu colț și mărime (10–40 %). PNG păstrează transparența.
- Sigla rămâne doar în sesiune (se șterge cu ea și cu „Șterge tot”) și se vede în previzualizare.

## 3.18.0 — 2026-11-08

### Noutăți
- **Galerie de șabloane:** alegeți unul dintre patru modele (Bosque, Quermesse, Natal și Gala), scrieți titlul, organizația, până la trei premii și data, priviți previzualizarea și apăsați „Folosește acest șablon”: șablonul și cifrele sunt gata. Fiecare model este un bilet cu cotor.
- Modelele sunt originale pentru acest proiect, în fontul liber Vera. Fontul are doar alfabetul latin: la alte litere apare un avertisment.

## 3.17.0 — 2026-11-08

### Noutăți
- **Semne de tăiere:** o casetă în panoul foii (șabloane cu un singur bilet) desenează linii scurte în margini, prelungind fiecare linie de tăiere. Cere cel puțin 3 mm de margine.
- **Cotorul** (numărul de două ori pe bilet) funcționa deja: acum este testat și documentat.
- **Surplusul** este deja respectat: dacă PDF-ul din Canva are un TrimBox mai mic decât pagina, biletul este doar ce se află înăuntru.

## 3.16.0 — 2026-11-08

### Noutăți
- **Exportul listei de bilete (CSV):** un fișier pentru Excel sau Calc, un bilet pe rând (serie, număr și coloanele Nume, Contact și Plătit goale), cu prefixe, serii și numere sărite.
- **Fișă de control al vânzărilor (PDF):** un tabel A4 de tipărit și completat de mână (36 de bilete pe pagină, cu casetă „plătit”). În limbile ale căror litere PDF-ul nu le poate scrie, titlurile apar în engleză.
- Nimic nu se păstrează pe server: lista vine doar din formular.

## 3.15.0 — 2026-11-08

### Noutăți
- **Serii și prefixe:** un text înaintea cifrelor (A- dă A-0001). Cu mai multe serii separate prin virgule, fiecare repetă intervalul și are PDF-urile ei. Prefixul acceptă litere, spațiu, punct, cratimă și bară (până la 6 caractere, fără cifre).
- **Sărirea numerelor:** 13, 100-110 scoate acele numere din șir (rezumatul, fișierele și verificarea numără doar ce se tipărește).
- **O culoare pentru fiecare serie.**
- Toate acestea merg și în „Copiază linkul” și în previzualizare.

## 3.14.0 — 2026-11-08

### Noutăți
- **Instalare ca aplicație (PWA):** instalați site-ul pe telefon sau computer; scheletul aplicației se deschide chiar și fără rețea (generarea cere în continuare serverul). Un service worker simplu păstrează doar pagina, fișierele aplicației și textele interfeței și nu atinge niciodată fișierele dvs. sau cererile de generare.

## 3.13.0 — 2026-11-08

### Noutăți
- **Reținerea fișierului cu cifre:** cine revine anul următor nu-l mai repetă. Rămâne doar în browserul dvs. (niciodată pe server) și se refolosește cu un șablon nou; alegerea altuia îl înlocuiește, iar „Șterge tot” îl elimină.
- **Copiază linkul:** un buton care copiază un link cu valorile formularului (de la, până la, mod, maxim pe fișier, hârtie, margine și nume). Cine îl deschide vede aceleași valori; fișierele nu merg niciodată în link.

## 3.12.0 — 2026-11-08

### Noutăți
- Paginile **Termeni de utilizare**, **Politica de confidențialitate** și **Contact**, cu linkuri în subsol. Sunt versiuni provizorii, de revizuit cu sprijin juridic înainte ca serviciul să se plătească.
- **Buton de donație** în subsol: apare doar dacă proprietarul setează linkul. E-mailul de contact și numele responsabilului vin tot din configurația serverului, niciodată din cod.

## 3.11.0 — 2026-11-08

### Noutăți
- **Pâlnie de utilizare** în panoul de administrare: câte evenimente sunt la fiecare etapă (sesiune, șablon, cifre, previzualizare, generare, descărcare) și ce parte din etapa anterioară a ajuns la următoarea. Arată unde renunță oamenii. Numără evenimente, nu persoane.

## 3.10.0 — 2026-11-08

### Noutăți
- Această pagină: **Changelog**, cu tot ce se schimbă, versiune cu versiune.
- În **decembrie** tema vizuală automată este **Crăciunul** (pentru cine nu a ales niciodată una). Alegerea altei teme rămâne reținută.

### Îmbunătățit
- O dependență mai puțin pe server (`python-multipart` nu mai era folosit: fișierele vin ca trup brut).

## 3.9.0 — 2026-11-08

### Noutăți
- Aspect gândit pentru **ecrane mari** (4K, ultra-wide) și **telefoane recente**: antet compact și butoane de 44 px.
- Previzualizarea arată o imagine când browserul nu poate afișa PDF-uri în pagină (Chrome pe Android).
- Panoul de administrare înregistrează **tipul de ecran** (clasă, mărime, familie) fără a păstra nimic personal.
- Serviciul se apelează singur la fiecare 10 minute ca să nu adoarmă.

## 3.8.0 — 2026-11-08

### Noutăți
- **Panou de administrare** (doar pentru proprietar, cu parolă) cu grafice și explicații despre sistem și utilizare: doar totaluri, niciodată date personale.

## 3.7.0 — 2026-11-08

### Noutăți
- **SEO**: titlu, descriere și text pentru fiecare pagină, `robots.txt`, `sitemap.xml` și un 404 adevărat pentru paginile care nu există.

## 3.6.0 — 2026-11-08

### Îmbunătățit
- Site-ul livrează **un singur fișier JavaScript**, ofuscat și precomprimat: ce se transmite este mult mai mic decât înainte.

## 3.5.0 — 2026-11-08

### Noutăți
- Tema vizuală **Matrix Gamer**: ploaie de caractere verzi și strălucire neon.

## 3.4.0 — 2026-11-08

### Îmbunătățit
- Stilurile trec la **Sass** și ies ca **un singur CSS**. Structura paginii este aceeași în toate temele: o temă schimbă doar culorile și formatarea.

## 3.3.0 — 2026-11-07

### Noutăți
- **Teme vizuale**: Premiado (noul aspect implicit) și încă șapte (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala și Natal), fiecare în mod luminos și întunecat.
- Pictogramă nouă a aplicației.
