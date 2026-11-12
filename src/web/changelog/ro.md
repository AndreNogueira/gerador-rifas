# Changelog (rezumat în română)

Rezumat tradus al `../CHANGELOG.md`: aceleași versiuni, secțiuni și puncte, mai scurte. Textul complet este în portugheză.

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
