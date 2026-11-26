"""Nutzungsbedingungen, Datenschutz und Kontakt auf Deutsch: Übersetzung von `pt.py` (gleiche Seiten, Abschnitte, Absätze und {Platzhalter}). Ohne muttersprachliche Prüfung; das Portugiesische gilt."""
FRASES = {
    "responsavel_com": "Der Dienst wird von {nome} betrieben.",
    "responsavel_sem": "Der Dienst wird von seinem Autor betrieben, der Person, die ihn online anbietet.",
    "contacto_com": "Sie erreichen uns unter {email}.",
    "contacto_sem": "Derzeit gibt es keinen öffentlichen Kontakt.",
    "contacto_pagina_com": "Bei Fragen, Fehlern oder Vorschlägen schreiben Sie an {email}.",
    "contacto_pagina_sem": "Derzeit gibt es keinen öffentlichen Kontakt. Schauen Sie später wieder vorbei.",
    "atualizado": "21. November 2026",
}

AVISO = ("Vorläufige Fassung, noch mit juristischer Unterstützung zu prüfen. Weicht etwas hier von dem ab, was der Dienst tut, bitten Sie uns, es zu berichtigen. "
         "Dies ist eine Übersetzung ohne muttersprachliche Prüfung: Bei Abweichungen gilt die portugiesische Fassung.")

TEXTOS = {
    "termos": {
        "titulo": "Nutzungsbedingungen",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Was dieser Dienst ist",
             "paragrafos": ["Der Los-Generator erstellt aus einer PDF-Vorlage nummerierte, druckfertige Lose für eine Tombola. Mehr tut er nicht: Er verkauft keine Lose, "
                            "nimmt kein Geld an, speichert keine Teilnehmerlisten und führt keine Ziehungen mit rechtlicher Wirkung durch.",
                            "{responsavel}"]},
            {"titulo": "Wer die Tombola veranstaltet, ist dafür verantwortlich",
             "paragrafos": ["Tombolas, Verlosungen und Ziehungen unterliegen gesetzlichen Regeln (zum Beispiel Genehmigungen der Gemeinde und Vorschriften für Vereine), die je nach Fall verschieden sind. "
                            "Wer die Tombola veranstaltet, ist allein dafür verantwortlich, das Gesetz einzuhalten, zu kassieren und die Preise auszuhändigen. Dieser Dienst bietet keine Rechtsberatung."]},
            {"titulo": "Erlaubte Nutzung",
             "paragrafos": ["Der Dienst ist kostenlos und für vernünftige Nutzung gedacht. Er darf weder für betrügerische Lose noch zur Überlastung des Servers verwendet werden: Es gibt Grenzen für die "
                            "Dateigröße, die Nummern pro Auftrag ({max_numeros}) und die Aufträge pro Minute, und es läuft jeweils nur eine Erzeugung."]},
            {"titulo": "Ihre Dateien",
             "paragrafos": ["Vorlage und Ziffern dienen nur dazu, Ihre Lose zu erzeugen, und werden nach {validade} Minuten ohne Aktivität oder bei „Alles löschen“ vom Server entfernt. "
                            "Wir verwenden sie für nichts anderes. Sie bleiben Ihre: Sie müssen nur das Recht haben, zu nutzen, was Sie hochladen (Bilder, Schriften, Logos)."]},
            {"titulo": "Keine Gewähr",
             "paragrafos": ["Der Dienst wird „wie besehen“ bereitgestellt, ohne Gewähr für ständige Verfügbarkeit oder Fehlerfreiheit. Prüfen Sie die PDFs vor dem Druck immer (der Dienst überprüft "
                            "die erzeugten Nummern, die Endkontrolle liegt aber bei Ihnen). Soweit gesetzlich zulässig, haften wir nicht für Verluste im Zusammenhang mit der Nutzung."]},
            {"titulo": "Änderungen",
             "paragrafos": ["Diese Bedingungen können sich ändern; das Datum der letzten Aktualisierung ist der {atualizado}. Sollte der Dienst einmal kostenpflichtig werden, wird das vor dem Abrechnen klar gesagt."]},
            {"titulo": "Kontakt", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Datenschutzerklärung",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Zusammenfassung",
             "paragrafos": ["Es gibt keine Konten, keine Werbung und keine Tracking-Werkzeuge Dritter. Ihre Dateien werden binnen {validade} Minuten vom Server gelöscht. "
                            "Die Nutzungsstatistiken sind nur zusammengefasste Zahlen."]},
            {"titulo": "Welche Daten wir verarbeiten",
             "paragrafos": ["Die Dateien, die Sie hochladen (Vorlage und Ziffern), werden nur zum Erzeugen der Lose verarbeitet, liegen in einem temporären Ordner auf dem Server und werden nach "
                            "{validade} Minuten ohne Aktivität oder bei „Alles löschen“ gelöscht.",
                            "Um zu wissen, wie der Dienst genutzt wird, zählen wir: wie viele Besuche, Erzeugungen und Downloads, die gewählte Sprache und das Design sowie den Bildschirmtyp. "
                            "Wir erfassen außerdem das Land des Besuchs (nur den Code, z. B. „PT“), das das Hosting-Netzwerk aus der IP-Adresse ableitet; die IP selbst speichern wir nicht. Wir erfassen nie IP-Adressen, Dateinamen, Dateiinhalte oder die vollständige Browserkennung.",
                            "Die IP-Adresse wird nur kurz im Arbeitsspeicher verwendet, um die Zahl der Aufträge pro Minute zu begrenzen, und von uns nicht gespeichert. Der Hosting-Anbieter "
                            "(Render, in Frankfurt, Europäische Union) kann IP-Adressen in seinen technischen Protokollen erfassen."]},
            {"titulo": "In Ihrem Browser",
             "paragrafos": ["Wir speichern in Ihrem Browser (lokaler Speicher) Ihre Einstellungen: Sprache, Design, hellen oder dunklen Modus und die letzten Formularwerte. "
                            "Damit Sie die Arbeit von Jahr zu Jahr nicht wiederholen, kann auch die Ziffern-Datei in Ihrem Browser bleiben (nie auf unserem Server); „Alles löschen“ entfernt sie. "
                            "Wir verwenden keine Werbe- oder Tracking-Cookies."]},
            {"titulo": "Rechtsgrundlage und Speicherdauer",
             "paragrafos": ["Wir verarbeiten diese Daten aufgrund unseres berechtigten Interesses, den Dienst zu erbringen und sicher zu halten (DSGVO, Art. 6 Abs. 1 Buchst. f). Dateien bestehen Minuten; "
                            "die zusammengefassten Zahlen identifizieren niemanden."]},
            {"titulo": "Ihre Rechte",
             "paragrafos": ["Sie haben das Recht auf Auskunft, Berichtigung, Löschung und Widerspruch sowie auf Beschwerde bei Ihrer Datenschutzbehörde (in Portugal die CNPD, cnpd.pt). "
                            "Da wir keine Daten speichern, die Sie identifizieren, gibt es praktisch wenig einzusehen oder zu löschen; bei Fragen sprechen Sie uns an."]},
            {"titulo": "Wer verantwortlich ist", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Aktualisierung", "paragrafos": ["Zuletzt aktualisiert: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Kontakt",
        "aviso": "",
        "seccoes": [
            {"titulo": "Schreiben Sie uns",
             "paragrafos": ["{contacto_pagina}",
                            "Wenn Sie einen Fehler finden, sagen Sie uns, was Sie getan und was Sie erwartet haben; senden Sie Ihre Vorlage nicht, wenn sie personenbezogene Daten enthält."]},
        ],
    },
}
