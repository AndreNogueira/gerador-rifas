"""Termeni, confidențialitate și contact în română: traducere a `pt.py` (aceleași pagini, secțiuni, paragrafe și {marcatori}). Fără revizuire nativă; prevalează portugheza."""
FRASES = {
    "responsavel_com": "Serviciul este administrat de {nome}.",
    "responsavel_sem": "Serviciul este administrat de autorul său, persoana care îl pune la dispoziție online.",
    "contacto_com": "Ne puteți contacta la {email}.",
    "contacto_sem": "Momentan nu există un contact public.",
    "contacto_pagina_com": "Pentru întrebări, erori sau sugestii, scrieți la {email}.",
    "contacto_pagina_sem": "Momentan nu există un contact public. Reveniți pe această pagină mai târziu.",
    "atualizado": "8 noiembrie 2026",
}

AVISO = ("Versiune provizorie, de revizuit cu sprijin juridic. Dacă ceva de aici diferă de ceea ce face serviciul, cereți-ne să corectăm. "
         "Este o traducere fără revizuire nativă: în caz de diferențe prevalează versiunea portugheză.")

TEXTOS = {
    "termos": {
        "titulo": "Termeni de utilizare",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Ce este acest serviciu",
             "paragrafos": ["Generatorul de bilete creează, dintr-un șablon PDF, biletele numerotate ale unei tombole, gata de tipărit. Atât face: nu vinde bilete, "
                            "nu primește bani, nu păstrează liste de participanți și nu face extrageri cu valoare legală.",
                            "{responsavel}"]},
            {"titulo": "Cine organizează tombola răspunde de ea",
             "paragrafos": ["Tombolele, loteriile și extragerile sunt supuse unor reguli legale (de exemplu, autorizații ale primăriei și reguli pentru asociații) care diferă de la caz la caz. "
                            "Cine organizează tombola este singurul răspunzător pentru respectarea legii, pentru încasare și pentru predarea premiilor. Acest serviciu nu oferă consultanță juridică."]},
            {"titulo": "Utilizare permisă",
             "paragrafos": ["Serviciul este gratuit și pentru utilizare rezonabilă. Nu poate fi folosit pentru a produce bilete pentru fraude și nici pentru a supraîncărca serverul: există limite pentru "
                            "mărimea fișierelor, pentru numerele dintr-o cerere ({max_numeros}) și pentru cererile pe minut, și o singură generare o dată."]},
            {"titulo": "Fișierele dvs.",
             "paragrafos": ["Șablonul și cifrele servesc doar la generarea biletelor dvs. și sunt șterse de pe server după {validade} minute fără activitate sau când apăsați „Șterge tot”. "
                            "Nu le folosim pentru altceva. Rămân ale dvs.: trebuie doar să aveți dreptul de a folosi ce încărcați (imagini, fonturi, sigle)."]},
            {"titulo": "Fără garanții",
             "paragrafos": ["Serviciul este oferit „ca atare”, fără garanția că este mereu disponibil sau fără erori. Verificați întotdeauna PDF-urile înainte de tipărire (serviciul verifică "
                            "numerele generate, dar verificarea finală vă aparține). În măsura permisă de lege, nu răspundem pentru pierderi legate de utilizarea serviciului."]},
            {"titulo": "Modificări",
             "paragrafos": ["Acești termeni se pot schimba; data ultimei actualizări este {atualizado}. Dacă într-o zi serviciul va fi plătit, se va spune clar înainte de a taxa."]},
            {"titulo": "Contact", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Politica de confidențialitate",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Rezumat",
             "paragrafos": ["Nu există conturi, nici reclame, nici instrumente de urmărire ale terților. Fișierele dvs. sunt șterse de pe server în {validade} minute. "
                            "Statisticile de utilizare sunt doar numere agregate."]},
            {"titulo": "Ce date prelucrăm",
             "paragrafos": ["Fișierele pe care le încărcați (șablon și cifre) sunt prelucrate doar pentru a genera biletele, stau într-un dosar temporar pe server și sunt șterse după {validade} minute "
                            "fără activitate sau când apăsați „Șterge tot”.",
                            "Pentru a ști cum este folosit serviciul, înregistrăm contorizări: câte vizite, generări și descărcări, limba și tema alese și tipul de ecran. "
                            "Nu înregistrăm niciodată adrese IP, nume de fișiere, conținutul fișierelor și nici identificarea completă a browserului.",
                            "Adresa IP este folosită doar în memorie, pentru câteva clipe, ca să limiteze numărul de cereri pe minut, și nu este păstrată de noi. Furnizorul de găzduire "
                            "(Render, la Frankfurt, în Uniunea Europeană) poate înregistra adrese IP în jurnalele sale tehnice."]},
            {"titulo": "În browserul dvs.",
             "paragrafos": ["Păstrăm în browserul dvs. (stocare locală) preferințele: limba, tema vizuală, modul luminos sau întunecat și ultimele valori ale formularului. "
                            "Ca să nu repetați munca de la un an la altul, și fișierul cu cifre poate rămâne în browserul dvs. (niciodată pe serverul nostru); „Șterge tot” îl elimină. "
                            "Nu folosim cookie-uri publicitare sau de urmărire."]},
            {"titulo": "Temei legal și păstrare",
             "paragrafos": ["Prelucrăm aceste date în baza interesului legitim de a furniza serviciul și de a-l menține sigur (RGPD, articolul 6 alineatul 1 litera f). Fișierele durează minute; "
                            "contorizările agregate nu identifică pe nimeni."]},
            {"titulo": "Drepturile dvs.",
             "paragrafos": ["Aveți dreptul de acces, rectificare, ștergere și opoziție și de a depune o plângere la autoritatea dvs. pentru protecția datelor (în Portugalia, CNPD, cnpd.pt). "
                            "Deoarece nu păstrăm date care să vă identifice, în practică este puțin de consultat sau de șters; dacă aveți întrebări, contactați-ne."]},
            {"titulo": "Cine răspunde", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Actualizare", "paragrafos": ["Ultima actualizare: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Contact",
        "aviso": "",
        "seccoes": [
            {"titulo": "Scrieți-ne",
             "paragrafos": ["{contacto_pagina}",
                            "Dacă găsiți o eroare, spuneți-ne ce ați făcut și ce vă așteptați; nu trimiteți șablonul dacă are date personale."]},
        ],
    },
}
