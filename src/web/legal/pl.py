"""Regulamin, prywatność i kontakt po polsku: tłumaczenie `pt.py` (te same strony, sekcje, akapity i {znaczniki}). Bez weryfikacji przez native speakerów; obowiązuje wersja portugalska."""
FRASES = {
    "responsavel_com": "Serwis prowadzi {nome}.",
    "responsavel_sem": "Serwis prowadzi jego autor, osoba, która udostępnia go w internecie.",
    "contacto_com": "Możesz się z nami skontaktować pod adresem {email}.",
    "contacto_sem": "Na razie nie ma publicznego kontaktu.",
    "contacto_pagina_com": "W razie pytań, błędów lub sugestii napisz na {email}.",
    "contacto_pagina_sem": "Na razie nie ma publicznego kontaktu. Wróć na tę stronę później.",
    "atualizado": "8 listopada 2026",
}

AVISO = ("Wersja tymczasowa, do sprawdzenia z pomocą prawną. Jeśli coś tutaj różni się od tego, co robi serwis, poproś nas o poprawkę. "
         "To tłumaczenie bez weryfikacji przez native speakerów: w razie różnic obowiązuje wersja portugalska.")

TEXTOS = {
    "termos": {
        "titulo": "Regulamin korzystania",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Czym jest ten serwis",
             "paragrafos": ["Generator losów tworzy z szablonu PDF ponumerowane losy loterii, gotowe do wydruku. Robi tylko to: nie sprzedaje losów, "
                            "nie przyjmuje pieniędzy, nie przechowuje list uczestników i nie przeprowadza losowań o skutku prawnym.",
                            "{responsavel}"]},
            {"titulo": "Organizator loterii za nią odpowiada",
             "paragrafos": ["Loterie, tombole i losowania podlegają przepisom prawa (na przykład zezwoleniom urzędu gminy i zasadom dla stowarzyszeń), które zależą od przypadku. "
                            "Organizator loterii jako jedyny odpowiada za przestrzeganie prawa, pobieranie opłat i wydanie nagród. Serwis nie udziela porad prawnych."]},
            {"titulo": "Dozwolone użycie",
             "paragrafos": ["Serwis jest bezpłatny i przeznaczony do rozsądnego użytku. Nie wolno go używać do tworzenia losów do oszustw ani do przeciążania serwera: obowiązują limity rozmiaru plików, "
                            "liczby numerów w zamówieniu ({max_numeros}) i zamówień na minutę, a generowanie odbywa się po jednym naraz."]},
            {"titulo": "Twoje pliki",
             "paragrafos": ["Szablon i cyfry służą tylko do wygenerowania Twoich losów i są usuwane z serwera po {validade} minutach bez aktywności lub po kliknięciu „Wyczyść wszystko”. "
                            "Nie używamy ich do niczego innego. Pozostają Twoje: musisz tylko mieć prawo do używania tego, co wgrywasz (obrazów, czcionek, logo)."]},
            {"titulo": "Brak gwarancji",
             "paragrafos": ["Serwis jest udostępniany „tak, jak jest”, bez gwarancji stałej dostępności ani braku błędów. Zawsze sprawdź pliki PDF przed drukiem (serwis weryfikuje "
                            "wygenerowane numery, ale ostateczna kontrola należy do Ciebie). W zakresie dozwolonym prawem nie odpowiadamy za straty związane z korzystaniem z serwisu."]},
            {"titulo": "Zmiany",
             "paragrafos": ["Regulamin może się zmieniać; data ostatniej aktualizacji to {atualizado}. Jeśli serwis kiedyś stanie się płatny, zostanie to jasno powiedziane przed pobraniem opłat."]},
            {"titulo": "Kontakt", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Polityka prywatności",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Podsumowanie",
             "paragrafos": ["Nie ma kont, reklam ani narzędzi śledzących osób trzecich. Twoje pliki są usuwane z serwera w ciągu {validade} minut. "
                            "Statystyki użycia to tylko zbiorcze liczby."]},
            {"titulo": "Jakie dane przetwarzamy",
             "paragrafos": ["Pliki, które wgrywasz (szablon i cyfry), są przetwarzane tylko do wygenerowania losów, leżą w tymczasowym folderze na serwerze i są usuwane po {validade} minutach "
                            "bez aktywności lub po kliknięciu „Wyczyść wszystko”.",
                            "Aby wiedzieć, jak serwis jest używany, zapisujemy liczniki: ile wizyt, generowań i pobrań, wybrany język i motyw oraz typ ekranu. "
                            "Nigdy nie zapisujemy adresów IP, nazw plików, zawartości plików ani pełnego identyfikatora przeglądarki.",
                            "Adres IP jest używany tylko w pamięci, przez chwilę, do ograniczenia liczby zamówień na minutę i nie jest przez nas przechowywany. Dostawca hostingu "
                            "(Render, we Frankfurcie, w Unii Europejskiej) może zapisywać adresy IP w swoich dziennikach technicznych."]},
            {"titulo": "W Twojej przeglądarce",
             "paragrafos": ["W Twojej przeglądarce (pamięć lokalna) zapisujemy Twoje preferencje: język, motyw, tryb jasny lub ciemny i ostatnie wartości formularza. "
                            "Aby nie powtarzać pracy z roku na rok, plik z cyframi może też zostać w Twojej przeglądarce (nigdy na naszym serwerze); „Wyczyść wszystko” go usuwa. "
                            "Nie używamy plików cookie reklamowych ani śledzących."]},
            {"titulo": "Podstawa prawna i przechowywanie",
             "paragrafos": ["Przetwarzamy te dane na podstawie prawnie uzasadnionego interesu w świadczeniu usługi i jej zabezpieczeniu (RODO, art. 6 ust. 1 lit. f). Pliki żyją minuty; "
                            "zbiorcze liczniki nikogo nie identyfikują."]},
            {"titulo": "Twoje prawa",
             "paragrafos": ["Masz prawo dostępu, sprostowania, usunięcia i sprzeciwu oraz prawo wniesienia skargi do organu ochrony danych (w Portugalii CNPD, cnpd.pt). "
                            "Ponieważ nie przechowujemy danych, które Cię identyfikują, w praktyce jest mało do wglądu lub usunięcia; w razie wątpliwości skontaktuj się z nami."]},
            {"titulo": "Kto odpowiada", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Aktualizacja", "paragrafos": ["Ostatnia aktualizacja: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Kontakt",
        "aviso": "",
        "seccoes": [
            {"titulo": "Napisz do nas",
             "paragrafos": ["{contacto_pagina}",
                            "Jeśli znajdziesz błąd, napisz, co zrobiłeś i czego oczekiwałeś; nie wysyłaj szablonu, jeśli zawiera dane osobowe."]},
        ],
    },
}
