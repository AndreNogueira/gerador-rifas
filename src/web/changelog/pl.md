# Changelog (streszczenie po polsku)

Przetłumaczone streszczenie `../CHANGELOG.md`: te same wersje, sekcje i punkty, krótsze. Pełny tekst jest po portugalsku.

## 3.92.0 — 2026-11-26

### Naprawione
- **Tekst kroku 4 („Cel”) na stronie**: samouczek i strona główna mówiły „wybierz folder, w którym zapisać pliki PDF”, co jest prawdą tylko w aplikacji Windows — na stronie pliki pobierają się automatycznie przez przeglądarkę. Tekst strony nie mówi już o żadnym folderze.

## 3.91.0 — 2026-11-26

### Ulepszono
- **Galeria szablonów ma teraz taką samą wagę wizualną jak wgrywanie szablonu**: na stronie głównej wybranie już gotowego wzoru (bez Canvy) nie jest już pomniejszym linkiem pod przesyłaniem PDF — ma teraz równie wyróżnione pole.
- **Więcej odnośników między stronami**: poradniki o losowaniu i o cenniku odsyłają teraz do swojego własnego narzędzia (`/sorteio`, `/precario`) zamiast do generatora losów, a strona główna odsyła teraz też do spisu poradników „Jak to zrobić” (`/como-fazer`).

## 3.90.0 — 2026-11-26

### Naprawione
- **Strona po portugalsku nie zmienia już sama języka**: wejście na adres bez prefiksu (`/`, `/tutorial`, …), gdy przeglądarka nie zgłasza portugalskiego jako języka — co dotyczy wielu robotów wyszukiwarek i niektórych przeglądarek — powodowało, że strona sama przepisywała adres URL i całą treść na angielski. Brak prefiksu oznacza teraz zawsze portugalski, jak było zaplanowane; 21 języków z prefiksem działa jak dotychczas. `robots.txt` też nie blokuje już całkowicie `/api/linguas`, `/api/textos`, `/api/guia(s)` i dokumentacji publicznego API (`/api/v1/docs`), dzięki czemu wyszukiwarki mogą dobrze renderować i indeksować stronę.

### Ulepszono
- **Szybszy wybór języka**: natywne nazwy języków w selektorze (jak «Tiếng Việt» czy «Čeština») używają teraz czcionki systemowej zamiast czcionki marki, więc strona nie musi już ściągać dodatkowych glifów tylko po to, by je pokazać — co wcześniej spowalniało główny tekst i czasem go przesuwało.

## 3.89.0 — 2026-11-26

### Ulepszono
- **Trzy kolejne biblioteki obrazków konturowych w cenniku: Tabler Icons, Lucide i Material Symbols** (bez wymogu podania autora): ponad 100 artykułów zyskało alternatywy z tych bibliotek, dobrane pojedynczo, by naprawdę przedstawiały dany artykuł (w odróżnieniu od poprzednich nie ma automatycznego sposobu ich znalezienia). W odróżnieniu od kolorowych obrazków, te przyjmują kolor aktualnego tekstu — strony, aplikacji Windows albo wybranego papieru w PDF — dzięki czemu nigdy nie stają się niewidoczne w ciemnym motywie ani na ciemnym papierze.

## 3.88.0 — 2026-11-21

### Ulepszono
- **Dwie kolejne biblioteki obrazków w cenniku: Twemoji i OpenMoji**: dołączają do Noto Emoji i Fluent Emoji 3D, nie zastępując żadnego istniejącego obrazka — selektor grupuje teraz obrazki według biblioteki, z nazwą każdej z nich. Twemoji (CC BY 4.0) i OpenMoji (CC BY-SA 4.0) wymagają podania autorów, co pojawia się w Polityce prywatności oraz, tylko gdy faktycznie użyto jednego z tych obrazków, w stopce wygenerowanego PDF i etykiet odbioru.

## 3.87.0 — 2026-11-21

### Ulepszono
- **Więcej obrazków do wyboru w cenniku, z Fluent Emoji 3D od Microsoftu (licencja MIT, bez obowiązku podawania autora)**: wszystkie 93 pozycje katalogu zyskały, obok dotychczasowych obrazków Noto Emoji, alternatywę w stylu 3D wszędzie tam, gdzie istnieje dla danego kodu — żaden z dotychczasowych obrazków nie został zastąpiony.

## 3.86.0 — 2026-11-21

### Ulepszono
- **Odstęp między losami i znaczniki cięcia między każdym z nich**: po włączeniu znaczników cięcia luz, który wcześniej tylko powiększał margines, zamienia się w odstęp między losami, a znaczniki (wcześniej tylko na marginesach arkusza) pojawiają się teraz też między każdym losem.

## 3.85.0 — 2026-11-21

### Naprawione
- **Prawdziwa strona 404**: błędny odnośnik pokazywał generator skryty pod stanem 404. Teraz pojawia się prawdziwa, przetłumaczona strona „Nie znaleziono strony” z odnośnikiem powrotu.
- **Ikona zapasowa (favicon.ico)**: dla starych narzędzi sprawdzających tylko tę ścieżkę.

## 3.84.0 — 2026-11-21

### Nowości
- **Wzór „Urodziny” w galerii i w cenniku**: balony, girlandy flagowe i konfetti w różu, turkusie i żółci — 25. wzór dołączający do istniejących, żeby urodziny miały swój własny styl na losach, w cenniku i na żetonach.

## 3.83.0 — 2026-11-21

### Ulepszono
- **Więcej obrazków do wyboru dla pozycji cennika**: każda pozycja katalogu może mieć teraz do 8 obrazków (wcześniej 5) — wszystkie 93 zyskały co najmniej jedną nową, dopasowaną alternatywę (woda falę, kawa mate, tort konfetti…).

## 3.82.0 — 2026-11-20

### Naprawione
- **Nierówne marginesy przy wypełnianiu arkusza mniejszą liczbą losów niż maksymalna**: prośba o mniej losów na arkusz niż maksimum zostawiała je przy górnym lewym rogu, a cały luz zostawał w prawym dolnym — prosty cios gilotyny już nie rozdzielał ich dobrze. Teraz są zawsze wyśrodkowane, z takim samym marginesem po wszystkich czterech stronach.

## 3.81.0 — 2026-11-20

### Nowości
- **Etykiety odbioru**: płaci się w jednym miejscu, a odbiera w innym? Na stronie cennika każda pozycja staje się etykietą z obrazkiem, nazwą, ceną (jeśli chcesz) i strefą odbioru (bar, kuchnia…), w wybranej liczbie kopii, po 24 na kartce A4 z liniami cięcia i jednym kolorem na strefę. Zestaw daje jedną etykietę na pozycję, każdą w strefie jej działu (strona i aplikacja na Windows; z samouczkiem i filmami).

## 3.80.0 — 2026-11-20

### Nowości
- **Zestawy z różnych działów w cenniku**: połącz od 2 do 4 pozycji z katalogu, także z różnych działów (na przykład kanapkę i napój), w jednej cenie. Zestaw pojawia się w nowym dziale «Zestawy i menu», z obrazkami pozycji obok siebie, i może mieć własną nazwę (strona i aplikacja na Windows).

## 3.79.0 — 2026-11-20

### Nowości
- **Kolory i logo w cenniku**: możesz zmienić kolor główny, akcentu i papieru motywu (ceny dostosowują się same, by zawsze były czytelne) oraz umieścić logo swojego stowarzyszenia (PNG lub JPG) w nagłówku, po lewej lub prawej, albo w stopce (strona i aplikacja na Windows). Kolory i miejsce zostają w pliku cennika i w udostępnionym linku; logo służy tylko do narysowania podglądu i PDF i nigdy nie jest zapisywane.

## 3.78.0 — 2026-11-20

### Nowości
- **Do 5 obrazków do wyboru przy każdej pozycji**: w cenniku kliknij obraz pozycji z katalogu i wybierz ten, który najbardziej ci się podoba, spośród maksymalnie 5 (woda może być kroplą, kranem, lodem, szklanką…). Wybór widać w PDF, a zostaje też w pliku cennika i w udostępnionym linku (strona i aplikacja na Windows).

## 3.77.0 — 2026-11-20

### Ulepszono
- **Porządniejsze listy i wiersze cennika**: wszystkie listy rozwijane na stronie wyglądają teraz jak pozostałe pola, ze strzałką dopasowaną do motywu (jasnego i ciemnego). W cenniku × do usuwania pozycji i przycisk zdjęcia zajmują dużo mniej miejsca, ceny nie przeskakują do drugiego wiersza, a na telefonie nazwa jest u góry, a pola pod nią.

## 3.76.0 — 2026-11-20

### Nowości
- **Własne zdjęcia w cenniku**: przy każdej pozycji możesz kliknąć «Zdjęcie» i wstawić własny obraz (PNG lub JPG) zamiast ikony (do 20 na cennik; strona i aplikacja na Windows). Zdjęcie jest zmniejszane na twoim komputerze i służy tylko do narysowania podglądu i PDF: nie jest zapisywane na serwerze, w pliku cennika ani w udostępnionym linku.

## 3.75.0 — 2026-11-20

### Nowości
- **Udostępnianie cennika linkiem** (na stronie, gdy usługa ma bazę danych): «Udostępnij linkiem» na stronie cennika tworzy link, który każdy może otworzyć, by zobaczyć i kontynuować twój cennik (teksty, pozycje, ceny i motyw). Cennik jest przechowywany 90 dni od ostatniego dostępu, bez niczego o osobie udostępniającej; zaktualizowano Politykę prywatności.

## 3.74.0 — 2026-11-20

### Nowości
- **Dwa rozmiary w cenniku**: włącz «Dwa rozmiary (dwie ceny przy pozycji)» (strona i aplikacja na Windows), aby wpisać dwie ceny przy każdej pozycji (na przykład mały i duży albo pozycja i zestaw). Obie kolumny wychodzą wyrównane, z nazwami, które wybierzesz, nad nimi (domyślnie «Mały» i «Duży»), i zapisują się w pliku cennika.

## 3.73.0 — 2026-11-20

### Nowości
- **Karty na stół**: w formacie cennika wybierz «Karty na stół (4 na arkuszu A4)» (strona i aplikacja na Windows), a cennik wyjdzie jako karty A6, cztery na arkuszu A4 z przerywanymi liniami cięcia, gotowe do wydruku i wycięcia na stoły (do 12 pozycji).

## 3.72.0 — 2026-11-20

### Nowości
- **Cennik «tablica»**: nowy motyw na liście «Okazja i motyw» (i w aplikacji na Windows): ciemnozielone tło szkolnej tablicy, drewniana rama i tekst pisany kredą (biały i żółty), idealny na budkę z jedzeniem, ogródek lub do klasy.

## 3.71.0 — 2026-11-20

### Nowości
- **Numerowane bony na żetony** (w cenniku, przy wymyślonej walucie; oraz «Extras → Cennik… → Numerowane bony…» w aplikacji na Windows): wybierz, ile żetonów jest wart każdy bon, tytuł i uwagę, zobacz bon w motywie cennika i utwórz je. Dalej w generatorze losów, który numeruje bony z seriami, kodami QR do weryfikacji i arkuszami gotowymi do wydruku.

## 3.70.0 — 2026-11-20

### Nowości
- **Generator cenników na imprezy** (`/precario` oraz «Extras → Cennik…» w aplikacji na Windows): wybierz okazję (podpowiadana jest ta z bieżącej pory roku) i pozycje z katalogu z obrazkami, wpisz ceny w walucie swojego kraju lub wymyślonej (żetony…) i pobierz PDF (lub obraz) gotowy do wydruku, w A5, A4 lub A3 i z 24 motywami galerii. Jest też nowy poradnik: «Jak zrobić cennik na imprezę».

## 3.69.0 — 2026-11-19

### Nowości
- **Portugalski brazylijski** (`/pt-br`): strona, poradniki i strony prawne są teraz także po brazylijsku, z własnym słownictwem, polityką prywatności dostosowaną do brazylijskiej LGPD i automatycznym wyborem języka, gdy przeglądarka ma pt-BR. Portugalski europejski zostaje bez zmian, bez prefiksu w adresie.

## 3.68.0 — 2026-11-19

### Nowości
- **Trzy nowe poradniki, według tematu** (nie odbiorcy): jak numerować losy, jak przeprowadzić weryfikowalne losowanie (odsyła do strony «Losowanie») oraz ile losów zrobić i w jakiej cenie. Są we «Wszystkie poradniki» (`/como-fazer`), w 22 językach.

## 3.67.0 — 2026-11-19

### Nowości
- **Spis poradników «Jak to zrobić»** (`/como-fazer`): jedna strona z wszystkimi poradnikami i krótkim opisem każdego; każdy poradnik kończy się odnośnikami do pozostałych. Także w menu «Pomoc» («Wszystkie poradniki»).
- Poradniki i spis podają Google swoją ścieżkę (Start › Jak to zrobić › poradnik), by mogła się pokazać w wynikach.

## 3.66.0 — 2026-11-19

### Nowości
- **Zaproszenie do zostawienia komentarza:** po pobraniu losów pojawia się (raz na urządzenie) dyskretny komunikat zachęcający do zostawienia komentarza, anonimowo, jeśli wolisz. Możesz go zamknąć przyciskiem „Nie teraz”.

## 3.65.0 — 2026-11-19

### Ulepszono
- **Lżejsza i bezpieczniejsza strona:** kto tylko generuje losy, pobiera o 24 % mniej kodu (panel administracyjny, edytor szablonów i losowanie ładują się dopiero po otwarciu strony). Strona wysyła też teraz nagłówki bezpieczeństwa i odpowiada weryfikatorom linków oraz podglądom udostępniania.

## 3.64.0 — 2026-11-19

### Nowości
- **Tygodniowa kopia zapasowa danych panelu administracyjnego:** w każdy poniedziałek usługa zapisuje w magazynie tego samego dostawcy co baza danych kopię historii, celów, dziennika działań, komentarzy i tekstów SEO (ostatnie 8 tygodni), ze skryptem do przywracania.

## 3.63.0 — 2026-11-19

### Nowości
- **Rzeczywista wydajność strony w statystykach:** panel administracyjny pokazuje dzień po dniu, ile trwa pojawienie się strony, jak bardzo przesuwa się zawartość i ile trwa reakcja na kliknięcie, mierzone w przeglądarkach odwiedzających (telefon i komputer). Tylko trzy anonimowe liczby na wizytę; zaktualizowano Politykę prywatności.

## 3.62.0 — 2026-11-19

### Nowości
- **Źródło wizyt w statystykach:** panel administracyjny pokazuje teraz, skąd przychodzą wizyty, w ogólnych kategoriach (wyszukiwarka, sieci społecznościowe, e-mail, inne strony lub bezpośrednio) i według kampanii (utm_source), aby mierzyć promocję. Adres strony źródłowej i IP nigdy nie są zapisywane; zaktualizowano Politykę prywatności.

## 3.61.0 — 2026-11-19

### Nowości
- **Dziennik działań w panelu administracyjnym:** kto, co i kiedy zrobił w panelu, jest przechowywane przez 400 dni (logowania, usunięte lub ukryte komentarze, klucze API, teksty SEO, cele), bez danych odwiedzających i haseł.

## 3.60.0 — 2026-11-19

### Nowości
- **Dzienne cele w panelu administracyjnym:** administrator ustala cel na dzień (sesje, generowania, wygenerowane numery, pobrania…) i widzi, czy ostatni dzień go osiągnął, średnią z 7 dni i w ilu z nich cel zrealizowano; dzienny raport e-mail zawiera tę samą sekcję.

## 3.59.0 — 2026-11-19

### Nowości
- **Statusy komentarzy w panelu administracyjnym:** administrator może oznaczyć każdy komentarz jako przeczytany, ulubiony lub ukryty (ukryty komentarz znika ze strony publicznej, ale nie jest tracony), filtrować po statusie i widzieć, ile jest nieprzeczytanych.

## 3.58.0 — 2026-11-19

### Nowości
- **Limity darmowego hostingu w panelu administracyjnym:** widać, ile z 750 miesięcznych godzin Render usługa już zużyła (z prognozą do końca miesiąca) i ile miejsca zajmuje baza danych w darmowym planie Neon, z ostrzeżeniem w dziennym raporcie e-mail, zanim limity się skończą.

## 3.57.0 — 2026-11-19

### Nowości
- **Znaczniki wersji na wykresach panelu administracyjnego:** każdy wykres dzienny oznacza dzień, w którym pojawiła się nowa wersja aplikacji (a raport dzienny podaje którą), aby powiązać wzrost błędów lub czasu odpowiedzi z aktualizacją, która go spowodowała.

## 3.56.0 — 2026-11-19

### Nowości
- **Tygodniowe i miesięczne podsumowanie e-mailem dla administratora serwisu:** w poniedziałki przychodzi podsumowanie tygodnia, a 1. dnia miesiąca — miesiąca, z sumami porównanymi z poprzednim okresem i miniaturą każdego dnia. Czytają z trwałej historii. Tylko liczby.

## 3.55.0 — 2026-11-19

### Nowości
- **Natychmiastowe alerty e-mail dla administratora serwisu:** przy serii błędów serwera, restartach silnika, pamięci blisko limitu lub bazie danych bez odpowiedzi ostrzeżenie przychodzi od razu (bez czekania na raport dzienny i bez powtórzeń przez 6 godzin). Tylko liczby.

## 3.54.0 — 2026-11-19

### Nowości
- **Trwała historia w panelu administracyjnym:** po północy zapisywane jest podsumowanie każdego dnia, więc dzienny przebieg pokazuje teraz miesiące i do 2 lat (wcześniej tylko 90 dni). Tylko liczby, jak reszta panelu.

## 3.53.0 — 2026-11-19

### Nowości
- **Dzienny raport e-mailem dla administratora serwisu:** codziennie tuż po północy przychodzi e-mail ze wszystkim, co zapisano w minionym dniu (użycie, odbiorcy, błędy i zasoby serwera), w porównaniu ze średnią z 7 poprzednich dni, aby śledzić aplikację bez otwierania panelu. Tylko liczby: nigdy dane odwiedzających.

## 3.52.0 — 2026-11-19

### Ulepszono
- **Komentarze bez adresu IP:** zamiast IP przechowywany jest tylko kraj, z którego wysłano komentarz (widzi go tylko administrator serwisu). Adres IP nie jest już przechowywany: te z wcześniejszych komentarzy usunięto, a Politykę prywatności zaktualizowano.

## 3.51.0 — 2026-11-19

### Nowości
- **Komentarze:** strona «Komentarze», na której każdy widzi, co inni sądzą o generatorze, oraz strona do dodania własnego: można pozostać anonimowym lub pokazać imię (bez imienia pojawia się «Gość nr …»). Adres IP jest przechowywany tylko dla administratora, by ograniczać nadużycia, nigdy nie jest pokazywany i jest usuwany po 90 dniach.
- **Zgłoś problem:** nowa strona, na której opisujesz błąd; po kliknięciu «Otwórz» powstaje on bezpośrednio w GitHubie projektu, bez konta (twój IP nie jest wysyłany, a dane techniczne przeglądarki tylko jeśli je dodasz).
- Obie strony i przyciski «Komentarze» i «Zgłoś problem» są dobrze widoczne w nagłówku, menu i stopce; Polityka prywatności (22 języki) wyjaśnia, co jest przechowywane.

## 3.50.0 — 2026-11-18

### Ulepszono
- **Nagłówek dopasowany do ekranu:** wszystkie opcje są wyrównane do prawej, w jednym rzędzie i bez luk, a gdy ekran się zmniejsza, przechodzą jedna po drugiej do menu «hamburger» (najpierw tryb jasny/ciemny i styl, na końcu darowizna). Na telefonach zostaje tylko nazwa aplikacji i przycisk menu, które otwiera strony, pomoc, udostępnianie i ustawienia.

## 3.49.0 — 2026-11-18

### Nowości
- **Panel z ewolucją dzień po dniu:** nowy widok «Ewolucja dzienna» pokazuje, do 90 dni wstecz, wszystko, co serwer zapisuje w bazie danych (sesje, generowania, wygenerowane numery, języki, kraje, style, galeria, edytor, API, żądania, czasy odpowiedzi, CPU i pamięć…), z trendem każdego wskaźnika i pobraniem wszystkiego w CSV. To funkcja panelu właściciela: odwiedzający nie zauważą różnicy.

## 3.48.0 — 2026-11-18

### Ulepszono
- **Menu «Pomoc» w nagłówku:** samouczek, wideo i poradniki «Jak to zrobić» są teraz w jednej zakładce, «Pomoc». Nagłówek jest krótszy, a nazwa aplikacji zawsze widnieje w całości w jednym wierszu, w każdym języku i na każdym ekranie.

## 3.47.0 — 2026-11-15

### Ulepszono
- **Galeria szablonów:** lista wzorów nie jest już ucinana ani przesunięta w niektórych motywach; każda nagroda ma swój numer; każde pole tekstowe pokazuje limit znaków (np. 12/50); a przycisk «Użyj tego szablonu» nie jest już przyklejony do ostatniego pola.
- **Data losowania we własnym kalendarzu:** zamiast pola przeglądarki (które pokazywało «dd.mm.rrrr» i wybór w innym języku niż strona) jest kalendarz w 22 językach, z miesiącami i dniami tygodnia w wybranym języku, datą zapisaną tak, jak zapisuje ją ten język, właściwym pierwszym dniem tygodnia i przyciskami «Dzisiaj» i «Wyczyść». Działa z klawiaturą (strzałki, Page Up/Down, Home/End, Enter i Esc).
- **Pełniejsze «O programie»:** tekst został napisany od nowa, w 22 językach, i wyjaśnia, dla kogo jest generator, co robi, co zrobić po wydruku, jak chroni prywatność i gdzie można go używać.

## 3.46.0 — 2026-11-15

### Ulepszono
- **Darowizna lepiej widoczna:** gdy usługa ma link do darowizn, przycisk pojawia się teraz w nagłówku (obok «Udostępnij») oraz, po wygenerowaniu plików, z krótkim zaproszeniem. Nadal jest też w stopce.

## 3.45.0 — 2026-11-14

### Ulepszono
- **Galeria szablonów w jednej linii:** 24 wzory wybiera się teraz w jednowierszowym polu, w którym każda opcja pokazuje miniaturę szablonu, zamiast długiej listy przycisków. Działa z myszą, dotykiem i klawiaturą (strzałki, Home/End, litera, Enter i Esc).

## 3.44.0 — 2026-11-14

### Ulepszono
- **Prywatność:** liczniki użycia obejmują teraz kraj wizyty (tylko kod, ustalany przez sieć hostingu; adres IP nadal nie jest zapisywany). Polityka prywatności wyjaśnia to we wszystkich 22 językach.

## 3.43.1 — 2026-11-14

### Ulepszono
- **Czystsza stopka:** poradniki «Jak to zrobić» pojawiają się teraz tylko w grupie w nagłówku; nie powtarzają się już na dole strony.

## 3.43.0 — 2026-11-14

### Ulepszono
- **Data losowania w kalendarzu:** w galerii szablonów wybierasz datę w kalendarzu, a potem jak ma wyglądać na losie (31.12.2026, 31 gru 2026, 31 grudnia 2026 lub z dniem tygodnia), w języku strony. Nadal można ją wpisać ręcznie, teraz do 60 znaków.
- **Szersze teksty:** strony z tekstem (poradniki, samouczek, regulaminy…) zajmują teraz całą szerokość strony, z mniejszą liczbą wierszy i akapitów.

## 3.42.0 — 2026-11-14

### Ulepszono
- **Nagłówek:** nowa grupa «Jak to zrobić», obok samouczka, zbiera poradniki (szkoły, stowarzyszenia, kluby, strażacy, festyny osiedlowe i parafie). Przycisk «Udostępnij» przeniesiono ze stopki do nagłówka, wyróżniony, a jego lista pokazuje ikony WhatsApp, Telegram, Facebook, e-mail i «Kopiuj link».

## 3.41.0 — 2026-11-14

### Ulepszono
- **Automatyczny podgląd:** gdy zmienisz szablon, cyfry, logo lub dowolne pole wpływające na gotową stronę (numery, cyfry, arkusz, serie, kolory, QR…), podgląd z prawdziwymi numerami odświeża się sam, bez klikania „Podgląd”. Jeśli coś jest nie tak, powód pojawia się obok podglądu, bez okienek.

## 3.40.0 — 2026-11-14

### Nowości
- **Od 3 do 10 nagród w galerii:** we wszystkich 24 wzorach z galerii wybierasz, ile nagród ma los (od 3 do 10; wcześniej najwyżej 3). Od 6 w górę są w dwóch kolumnach. Także w aplikacji Windows.

## 3.39.0 — 2026-11-13

### Nowości
- **Aplikacja Windows 2.7:** galeria i edytor szablonów akceptują teraz rozszerzoną łacinkę, wietnamski, grecki, cyrylicę, chiński, japoński i koreański, tak jak strona od wersji 3.37 (hindi, arabski i hebrajski nadal nie działają). Do pobrania ze strony Changelog.

## 3.38.0 — 2026-11-13

### Nowości
- **Przycisk «Udostępnij»:** w stopce i, po wygenerowaniu plików, na karcie pobierania. Otwiera krótką listę (udostępnianie telefonu lub komputera, WhatsApp, Telegram, Facebook, e-mail i «Kopiuj link»), by poznały generator inne stowarzyszenia, szkoły i komitety festynów. Linki zawierają tylko adres strony w używanym języku: bez śledzenia i bez zapisywania czegokolwiek. Ma temat w samouczku i wideo.

## 3.37.0 — 2026-11-13

### Nowości
- **Więcej liter w galerii i edytorze szablonów:** teksty mogą teraz zawierać rozszerzoną łacinkę (polski, czeski, rumuński, turecki…), **wietnamski, grecki, cyrylicę (rosyjski, ukraiński)**, **chiński, japoński i koreański**. Hindi, arabski i hebrajski nadal nie działają (wymagają techniki pisma, której generator PDF nie ma) i pokazują ostrzeżenie zamiast zepsutego obrazu. W plikach PDF zmienia się tylko wpisany tekst; to, co wyglądało tak samo, wygląda tak samo.

## 3.36.0 — 2026-11-13

### Nowości
- **Poradnik «Jak to zrobić» dla parafii:** «Dla parafii» (link w stopce), z instrukcją krok po kroku, jak zorganizować loterię parafialną: odpusty, festyny, remonty, paczki świąteczne i katecheza. Jest w 22 językach i przypomina, by sprawdzić w urzędzie gminy, czy loteria wymaga zezwolenia.

## 3.35.0 — 2026-11-13

### Nowości
- **Aplikacja Windows 2.6:** menu «Extras» zyskuje «Zapisz zamówienie…» i «Otwórz zamówienie…» (plik .rifas z numerami, nazwą, seriami, kolorami i znacznikami cięcia, bez szablonu i ścieżek), edytor szablonów potrafi dodawać obrazy (PNG lub JPG), a «Widok → Wygląd» zmienia się z 2 na 14 motywów strony (tylko kolory). Dochodzi też to, co przyszło od wersji 2.4: edytor, 24 wzory z galerii i 22 języki.

## 3.34.0 — 2026-11-13

### Nowości
- **Trzy nowe poradniki „Jak to zrobić”:** „Dla klubów”, „Dla straży pożarnej” i „Dla festynów” (linki w stopce), z instrukcją krok po kroku, jak zorganizować loterię w każdym z tych przypadków. Są w 22 językach i przypominają, by sprawdzić w urzędzie gminy, czy loteria wymaga zezwolenia.

## 3.33.0 — 2026-11-13

### Nowości
- **Publiczne API do partii** (`/api/v1`, z Swaggerem pod `/api/v1/docs`): pozwala innym programom generować wiele zleceń losów z jednego szablonu, z kluczem, dziennymi limitami i ograniczeniami. Osoby korzystające ze strony zawsze mają pierwszeństwo.
- **Cztery nowe języki:** kataloński, ukraiński, indonezyjski i wietnamski. Strona i aplikacja Windows mówią teraz w 22 językach, z poradnikiem, regulaminem, prywatnością, przewodnikami i zrzutami ekranu.
- **Teksty dla wyszukiwarek edytowalne dla każdego języka:** właściciel edytuje w panelu administracyjnym tytuły, opisy i przewodniki każdego języka, zapisane w bazie danych, bez nowego wdrożenia.

## 3.32.0 — 2026-11-13

### Nowości
- **20 nowych szablonów w galerii (razem 24):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Wszystkie narysowane od zera na potrzeby tego projektu, z odcinkiem, na stronie i w aplikacji Windows (gdzie galeria staje się listą rozwijaną).

## 3.31.0 — 2026-11-13

### Nowości
- **Edytor szablonów v2:** cofnij i ponów (Ctrl+Z, Ctrl+Y), duplikuj (Ctrl+D), zmiana kolejności rysowania, dodawanie logo (PNG lub JPG) i **udostępnianie projektu linkiem**: jest przechowywany 90 dni od ostatniego dostępu, bez obrazów i bez danych o osobie udostępniającej (pojawia się tylko, gdy usługa ma bazę danych). Polityka prywatności o tym mówi.
- **Aplikacja Windows 2.5:** dostaje edytor szablonów (menu Dodatki) i przechodzi na Pythona 3.15.

### Ulepszono
- Changelog ma link do pobrania aplikacji Windows.

## 3.30.0 — 2026-11-12

### Nowości
- **Strony „Jak to zrobić”:** dwa pisane poradniki, „Dla szkół” i „Dla stowarzyszeń” (linki w stopce), z instrukcją krok po kroku, jak zorganizować loterię: zaprojektować los, seria na klasę lub sprzedawcę, wydrukować ze znacznikami cięcia, kontrolować sprzedaż i przeprowadzić weryfikowalne losowanie. Są we wszystkich 18 językach i przypominają, by sprawdzić w urzędzie gminy, czy loteria wymaga zezwolenia.

## 3.29.0 — 2026-11-12

### Ulepszono
- **Reklamy po bokach:** gdy reklamy są włączone (na razie nie są), na szerokich ekranach pojawiają się po obu stronach treści, po jednej z każdej strony, stałe i bez przesuwania strony; na innych ekranach jest jeden blok na końcu strony. Nadal nie pojawiają się w edytorze, w wygenerowanych plikach ani w aplikacji Windows.

## 3.28.0 — 2026-11-12

### Nowości
- **Reklamy Google (przygotowane, wyłączone):** strona może pokazywać blok reklam Google (AdSense) na końcu strony głównej, samouczka, „O programie”, losowania i changeloga. Nigdy nie pojawiają się w edytorze, w wygenerowanych plikach, przy weryfikacji losów, w panelu ani w aplikacji Windows, a w Europejskim Obszarze Gospodarczym i Wielkiej Brytanii dopiero po wyborze w komunikacie o zgodzie Google. Polityka prywatności mówi o tym, we wszystkich 18 językach, gdy reklamy są włączone; na razie są wyłączone, dopóki właściciel usługi ich nie skonfiguruje.

## 3.27.0 — 2026-11-12

### Nowości
- **Edytor szablonów:** zamiast szablonu z Canvy zaprojektuj los na stronie (strona „Edytor szablonów”, z linkiem od kroku 1): dodaj teksty, prostokąty, linie i numer 0001 (raz, a przy odcinku dwa razy), przeciągaj każdy element myszą lub strzałkami, zmieniaj kolory, rozmiary i tło, a potem kliknij „Użyj tego szablonu”. Ekran używa czcionki Vera, tej samej co PDF, więc to, co widzisz, to dostaniesz; szkic zostaje tylko w przeglądarce. Teksty nie mogą zawierać ciągów takich jak 0123, które program pomyliłby z numerem losu (ostrzega ekran i serwer).

## 3.26.0 — 2026-11-12

### Nowości
- **Pięć nowych motywów:** Halloween, Plaża, Stara gazeta, Zielony terminal i Plakat cyrkowy, każdy w wersji jasnej i ciemnej. Strona ma teraz 14 motywów; układ jest wszędzie taki sam (zmieniają się tylko kolory i wygląd).

## 3.25.0 — 2026-11-08

### Nowości
- **Jeden adres na język dla wyszukiwarek:** każdy język ma własny adres (/en, /ja/tutorial…) z tytułem, opisem i tekstem w tym języku, a strona podaje Google, które wersje są równoważne (hreflang). Portugalski zostaje pod /. Wybrany język widać teraz w pasku adresu.

## 3.24.1 — 2026-11-08

### Ulepszono
- **Wyrównane pola wyboru:** „Jeden kolor na serię” i pozostałe pola stoją teraz obok tekstu, a nie na drugim końcu karty.

## 3.24.0 — 2026-11-08

### Ulepszono
- **Samouczek ze zrzutami ekranu strony:** podstawowe tematy samouczka pokazują teraz samą stronę, we wszystkich 18 językach, zamiast aplikacji Windows.

## 3.23.0 — 2026-11-08

### Nowości
- **Samouczek i film do każdej funkcji:** samouczek ma temat dla każdej funkcji (serie, lista i arkusz kontrolny, znaczniki cięcia, galeria, własna marka, QR, losowanie, zapisywanie i udostępnianie, instalacja jako aplikacja, motywy), każdy z krótkim filmem nagranym w samym interfejsie, po portugalsku i angielsku.
- **Changelog, Regulamin, Prywatność i Kontakt w 18 językach:** tekst pojawia się w wybranym języku. Changelog ma przetłumaczone streszczenie każdej wersji (pełny jest po portugalsku); teksty prawne to tłumaczenia bez weryfikacji przez native speakerów, a w razie różnic obowiązuje wersja portugalska.
- **Aplikacja Windows 2.4** z tym, co strona zyskała od wersji 3.10: menu „Dodatki” z seriami, prefiksami i kolorem serii, pomijanymi numerami, kolorem numerów, logo, znacznikami cięcia, galerią szablonów, weryfikowalnym losowaniem oraz eksportem listy (CSV) i arkusza kontrolnego; do tego automatyczny wygląd świąteczny w grudniu. Weryfikacja QR i instalacja jako aplikacja zostają tylko na stronie.

## 3.22.0 — 2026-11-08

### Ulepszono
- **Kontrast 9 motywów zmierzony naprawdę:** test w przeglądarce mierzy tekst względem rzeczywistych pikseli tła, w trybie jasnym i ciemnym (WCAG AA); to, co nie przechodziło, poprawiono.
- Duże dekoracyjne numery kroków nie są już czytane przez czytniki ekranu.

## 3.21.0 — 2026-11-08

### Nowości
- **Weryfikowalne losowanie** (strona „Losowanie”): losuje numery z zakresu (z numerami do pominięcia) tak, że każdy może je powtórzyć i uzyskać ten sam wynik, dzięki publicznemu ziarnu. Wszystko dzieje się w przeglądarce, a „Kopiuj link” udostępnia to samo losowanie.
- Metodę opisano krok po kroku, wraz z implementacją referencyjną dającą te same numery co strona.

## 3.20.0 — 2026-11-08

### Nowości
- **QR na każdym losie:** kod QR weryfikacji w rogu każdego losu (szablony z jednym losem), z wyborem rogu i rozmiaru. Skan otwiera stronę potwierdzającą, że ten serwis wydał kod dla tego losu. Podpisany kluczem znanym tylko serwerowi; bez bazy danych. Nie dowodzi wpłaty ani wygranej.
- Pojawia się tylko, gdy właściciel serwisu ustawi klucz. Zamówienia z QR mają limit 10 000 numerów.

## 3.19.0 — 2026-11-08

### Nowości
- **Własna marka:** kolor numerów (każdy szablon; kolor serii ma pierwszeństwo) i **logo** stowarzyszenia na każdym losie (PNG lub JPG do 2 MB, szablony z jednym losem), z rogiem i rozmiarem (10–40 %). PNG zachowuje przezroczystość.
- Logo zostaje tylko w sesji (znika z nią i po „Wyczyść wszystko”) i widać je w podglądzie.

## 3.18.0 — 2026-11-08

### Nowości
- **Galeria szablonów:** wybierz jeden z czterech wzorów (Bosque, Quermesse, Natal i Gala), wpisz tytuł, organizację, do trzech nagród i datę, obejrzyj podgląd i kliknij „Użyj tego szablonu”: szablon i cyfry są gotowe. Każdy wzór to los z odcinkiem.
- Wzory są oryginalne dla tego projektu, w wolnej czcionce Vera. Czcionka ma tylko alfabet łaciński: inne litery wywołują ostrzeżenie.

## 3.17.0 — 2026-11-08

### Nowości
- **Znaczniki cięcia:** pole w panelu arkusza (szablony z jednym losem) rysuje krótkie kreski na marginesach, przedłużające każdą linię cięcia. Potrzeba co najmniej 3 mm marginesu.
- **Odcinek** (numer dwa razy na losie) już działał: teraz jest przetestowany i opisany.
- **Spad** jest już uwzględniany: jeśli PDF z Canvy ma TrimBox mniejszy niż strona, los to tylko to, co jest w środku.

## 3.16.0 — 2026-11-08

### Nowości
- **Eksport listy losów (CSV):** plik dla Excela lub Calc, jeden los w wierszu (seria, numer i puste kolumny Imię, Kontakt, Zapłacono), z prefiksami, seriami i pominiętymi numerami.
- **Arkusz kontrolny sprzedaży (PDF):** tabela A4 do wydruku i ręcznego wypełniania (36 losów na stronie, z polem „zapłacono”). W językach, których liter PDF nie umie zapisać, nagłówki są po angielsku.
- Nic nie jest zapisywane na serwerze: lista powstaje tylko z formularza.

## 3.15.0 — 2026-11-08

### Nowości
- **Serie i prefiksy:** tekst przed cyframi (A- daje A-0001). Przy kilku seriach oddzielonych przecinkami każda powtarza zakres i ma własne PDF. Prefiks dopuszcza litery, spację, kropkę, myślnik i ukośnik (do 6 znaków, bez cyfr).
- **Pomijanie numerów:** 13, 100-110 usuwa te numery z ciągu (podsumowanie, pliki i weryfikacja liczą tylko to, co się drukuje).
- **Osobny kolor dla każdej serii.**
- Wszystko to trafia też do „Kopiuj link” i do podglądu.

## 3.14.0 — 2026-11-08

### Nowości
- **Instalacja jako aplikacja (PWA):** zainstaluj stronę na telefonie lub komputerze; powłoka aplikacji otwiera się nawet offline (generowanie nadal wymaga serwera). Prosty service worker zapisuje tylko stronę, pliki aplikacji i teksty interfejsu i nigdy nie dotyka Twoich plików ani żądań generowania.

## 3.13.0 — 2026-11-08

### Nowości
- **Zapamiętanie pliku z cyframi:** kto wróci za rok, nie musi go powtarzać. Zostaje tylko w Twojej przeglądarce (nigdy na serwerze) i jest używany z nowym szablonem; wybór innego go zastępuje, a „Wyczyść wszystko” usuwa.
- **Kopiuj link:** przycisk kopiujący link z wartościami formularza (od, do, tryb, maksimum na plik, papier, margines i nazwa). Kto go otworzy, zobaczy te same wartości; pliki nigdy nie trafiają do linku.

## 3.12.0 — 2026-11-08

### Nowości
- Strony **Regulamin**, **Polityka prywatności** i **Kontakt**, z linkami w stopce. To wersje tymczasowe, do sprawdzenia z pomocą prawną, zanim serwis zacznie pobierać opłaty.
- **Przycisk darowizny** w stopce: pojawia się tylko, gdy właściciel ustawi link. Adres e-mail kontaktowy i nazwa osoby odpowiedzialnej też pochodzą z konfiguracji serwera, nigdy z kodu.

## 3.11.0 — 2026-11-08

### Nowości
- **Lejek użycia** w panelu administracyjnym: ile zdarzeń jest na każdym etapie (sesja, szablon, cyfry, podgląd, generowanie, pobranie) i jaka część poprzedniego etapu dotarła do następnego. Pokazuje, gdzie ludzie rezygnują. Liczy zdarzenia, nie osoby.

## 3.10.0 — 2026-11-08

### Nowości
- Ta strona: **Changelog**, ze wszystkim, co się zmienia, wersja po wersji.
- W **grudniu** automatycznym motywem jest **Boże Narodzenie** (dla tych, którzy nigdy żadnego nie wybrali). Wybór innego motywu nadal jest zapamiętywany.

### Ulepszono
- Jedna zależność mniej na serwerze (`python-multipart` nie był już używany: pliki przychodzą jako surowe ciało).

## 3.9.0 — 2026-11-08

### Nowości
- Układ dla **dużych ekranów** (4K, ultrapanoramiczne) i **nowych telefonów**: zwarty nagłówek i przyciski 44 px.
- Podgląd pokazuje obraz, gdy przeglądarka nie potrafi wyświetlić PDF na stronie (Chrome na Androidzie).
- Panel administracyjny rejestruje **typ ekranu** (klasa, rozmiar, rodzina), nie zapisując nic osobistego.
- Serwis wywołuje sam siebie co 10 minut, żeby nie zasnąć.

## 3.8.0 — 2026-11-08

### Nowości
- **Panel administracyjny** (tylko dla właściciela, z hasłem) z wykresami i objaśnieniami systemu i użycia: tylko sumy, nigdy dane osobowe.

## 3.7.0 — 2026-11-08

### Nowości
- **SEO**: tytuł, opis i tekst dla każdej strony, `robots.txt`, `sitemap.xml` i prawdziwy błąd 404 dla stron, które nie istnieją.

## 3.6.0 — 2026-11-08

### Ulepszono
- Strona dostarcza **jeden plik JavaScript**, zaciemniony i wstępnie skompresowany: to, co jest przesyłane, jest znacznie mniejsze niż wcześniej.

## 3.5.0 — 2026-11-08

### Nowości
- Motyw **Matrix Gamer**: deszcz zielonych znaków i neonowa poświata.

## 3.4.0 — 2026-11-08

### Ulepszono
- Style przechodzą na **Sass** i wychodzą jako **jeden CSS**. Struktura strony jest taka sama w każdym motywie: motyw zmienia tylko kolory i formatowanie.

## 3.3.0 — 2026-11-07

### Nowości
- **Motywy**: Premiado (nowy wygląd domyślny) i siedem kolejnych (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala i Natal), każdy jasny i ciemny.
- Nowa ikona aplikacji.
