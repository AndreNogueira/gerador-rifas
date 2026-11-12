# Changelog (deutsche Zusammenfassung)

Übersetzte Zusammenfassung von `../CHANGELOG.md`: gleiche Versionen, Abschnitte und Punkte, kürzer. Der vollständige Text ist auf Portugiesisch.

## 3.30.0 — 2026-11-12

### Neu
- **„So geht’s“-Seiten:** zwei geschriebene Anleitungen, „Für Schulen“ und „Für Vereine“ (Links in der Fußzeile), mit der Schritt-für-Schritt-Anleitung für eine Tombola: Los gestalten, eine Serie pro Klasse oder Verkäufer, mit Schnittmarken drucken, Verkäufe kontrollieren und eine nachprüfbare Ziehung durchführen. Sie gibt es in allen 18 Sprachen, mit dem Hinweis, bei der Gemeinde zu klären, ob eine Genehmigung nötig ist.

## 3.29.0 — 2026-11-12

### Verbessert
- **Anzeigen an den Seiten:** Wenn Anzeigen aktiv sind (derzeit nicht), erscheinen sie auf breiten Bildschirmen links und rechts neben dem Inhalt, je eine pro Seite, fest und ohne die Seite zu verschieben; auf anderen Bildschirmen gibt es einen einzigen Block am Seitenende. Sie erscheinen weiterhin nie im Editor, in den erzeugten Dateien oder in der Windows-App.

## 3.28.0 — 2026-11-12

### Neu
- **Google-Anzeigen (vorbereitet, ausgeschaltet):** Die Website kann am Ende der Startseite, des Tutorials, von „Über“, der Ziehung und des Changelogs einen Block mit Google-Anzeigen (AdSense) zeigen. Sie erscheinen nie im Editor, in den erzeugten Dateien, bei der Losprüfung, im Dashboard oder in der Windows-App, und im Europäischen Wirtschaftsraum und im Vereinigten Königreich erst nach Ihrer Wahl in der Einwilligungsmeldung von Google. Die Datenschutzerklärung sagt das in allen 18 Sprachen, wenn Anzeigen aktiv sind; derzeit sind sie aus, bis der Betreiber sie einrichtet.

## 3.27.0 — 2026-11-12

### Neu
- **Vorlageneditor:** Statt einer Canva-Vorlage gestalten Sie das Los auf der Website (Seite „Vorlageneditor“, verlinkt ab Schritt 1): Fügen Sie Texte, Rechtecke, Linien und die Nummer 0001 hinzu (einmal, mit Abschnitt zweimal), ziehen Sie jedes Element mit Maus oder Pfeiltasten an seinen Platz, ändern Sie Farben, Größen und Hintergrund und klicken Sie auf „Diese Vorlage verwenden“. Der Bildschirm nutzt die Schrift Vera wie das PDF: Was Sie sehen, bekommen Sie; der Entwurf bleibt nur im Browser. Texte dürfen keine Folgen wie 0123 enthalten, die das Programm mit der Losnummer verwechseln würde (Bildschirm und Server warnen).

## 3.26.0 — 2026-11-12

### Neu
- **Fünf neue Designs:** Halloween, Strand, Alte Zeitung, Grünes Terminal und Zirkusplakat, jeweils hell und dunkel. Die Website hat jetzt 14 Designs; der Aufbau ist überall gleich (nur Farben und Aussehen ändern sich).

## 3.25.0 — 2026-11-08

### Neu
- **Eine Adresse pro Sprache für Suchmaschinen:** Jede Sprache hat eine eigene Adresse (/en, /ja/tutorial…) mit Titel, Beschreibung und Text in dieser Sprache, und die Seite sagt Google, welche Versionen gleichwertig sind (hreflang). Portugiesisch bleibt unter /. Die gewählte Sprache steht jetzt in der Adressleiste.

## 3.24.1 — 2026-11-08

### Verbessert
- **Kontrollkästchen ausgerichtet:** „Eine Farbe pro Serie“ und die anderen Kästchen stehen jetzt neben ihrem Text statt am anderen Ende der Karte.

## 3.24.0 — 2026-11-08

### Verbessert
- **Tutorial mit Screenshots der Website:** Die Grundthemen des Tutorials zeigen jetzt die Website selbst, in allen 18 Sprachen, statt der Windows-App.

## 3.23.0 — 2026-11-08

### Neu
- **Anleitung und Video zu jeder Funktion:** Die Anleitung hat je Funktion ein Thema (Serien, Liste und Kontrollblatt, Schnittmarken, Galerie, eigene Marke, QR, Ziehung, Speichern und Teilen, als App installieren, Designs), jeweils mit einem kurzen, in der Oberfläche selbst aufgenommenen Video auf Portugiesisch und Englisch.
- **Changelog, Nutzungsbedingungen, Datenschutz und Kontakt in 18 Sprachen:** Der Text erscheint in der gewählten Sprache. Der Changelog hat eine übersetzte Zusammenfassung jeder Version (die vollständige ist portugiesisch); die Rechtstexte sind Übersetzungen ohne muttersprachliche Prüfung, bei Abweichungen gilt die portugiesische Fassung.
- **Windows-App 2.4** mit dem, was die Website seit 3.10 bekam: Menü „Extras“ mit Serien, Präfixen und Farbe je Serie, übersprungenen Nummern, Nummernfarbe, Logo, Schnittmarken, Vorlagengalerie, überprüfbarer Ziehung und Export von Liste (CSV) und Kontrollblatt; dazu das automatische Weihnachtsdesign im Dezember. QR-Prüfung und App-Installation gibt es nur auf der Website.

## 3.22.0 — 2026-11-08

### Verbessert
- **Kontrast der 9 Designs wirklich gemessen:** Ein Browsertest misst den Text gegen die echten Hintergrundpixel, hell und dunkel (WCAG AA); was durchfiel, wurde behoben.
- Die großen dekorativen Schrittnummern werden von Screenreadern nicht mehr vorgelesen.

## 3.21.0 — 2026-11-08

### Neu
- **Überprüfbare Ziehung** (Seite „Ziehung“): zieht Nummern aus einem Bereich (mit auszulassenden Nummern), sodass jeder sie wiederholen und dasselbe Ergebnis erhalten kann, mit einem öffentlichen Startwert. Alles läuft im Browser; „Link kopieren“ teilt dieselbe Ziehung.
- Das Verfahren ist Schritt für Schritt beschrieben, mit einer Referenzimplementierung, die dieselben Nummern wie die Website liefert.

## 3.20.0 — 2026-11-08

### Neu
- **QR auf jedem Los:** ein Prüf-QR-Code in einer Ecke jedes Loses (Vorlagen mit einem Los), mit Wahl von Ecke und Größe. Beim Scannen öffnet sich eine Seite, die bestätigt, dass dieser Dienst den Code für dieses Los ausgestellt hat. Signiert mit einem Schlüssel, den nur der Server kennt; keine Datenbank. Er beweist weder Zahlung noch Gewinn.
- Er erscheint nur, wenn der Betreiber den Schlüssel einrichtet. Aufträge mit QR sind auf 10 000 Nummern begrenzt.

## 3.19.0 — 2026-11-08

### Neu
- **Eigene Marke:** die Farbe der Nummern (jede Vorlage; die Serienfarbe hat Vorrang) und das **Logo** des Vereins auf jedem Los (PNG oder JPG bis 2 MB, Vorlagen mit einem Los), mit Ecke und Größe (10 bis 40 %). PNG behält die Transparenz.
- Das Logo bleibt nur in der Sitzung (wird mit ihr und mit „Alles löschen“ entfernt) und erscheint in der Vorschau.

## 3.18.0 — 2026-11-08

### Neu
- **Vorlagengalerie:** eines von vier Designs wählen (Bosque, Quermesse, Natal und Gala), Titel, Organisation, bis zu drei Preise und Datum schreiben, Vorschau prüfen und „Diese Vorlage verwenden“ klicken: Vorlage und Ziffern sind fertig. Jedes Design ist ein Los mit Abschnitt.
- Die Designs sind Originale dieses Projekts, in der freien Schrift Vera. Die Schrift kennt nur das lateinische Alphabet: bei anderen Buchstaben erscheint ein Hinweis.

## 3.17.0 — 2026-11-08

### Neu
- **Schnittmarken:** ein Kästchen im Blattbereich (Vorlagen mit einem Los) zeichnet kurze Striche in die Ränder, die jede Schnittlinie verlängern. Es braucht mindestens 3 mm Rand.
- Der **Abschnitt** (die Nummer doppelt pro Los) funktionierte schon: jetzt ist er getestet und dokumentiert.
- Der **Beschnitt** wird schon beachtet: Hat das Canva-PDF eine kleinere TrimBox als die Seite, ist das Los nur das, was darin liegt.

## 3.16.0 — 2026-11-08

### Neu
- **Losliste exportieren (CSV):** eine Datei für Excel oder Calc, ein Los pro Zeile (Serie, Nummer und leere Spalten Name, Kontakt, Bezahlt), mit Präfixen, Serien und übersprungenen Nummern.
- **Kontrollblatt für Verkäufe (PDF):** eine A4-Tabelle zum Ausdrucken und Ausfüllen (36 Lose pro Seite, mit „bezahlt“-Kästchen). In Sprachen, deren Buchstaben das PDF nicht schreiben kann, erscheinen die Überschriften auf Englisch.
- Nichts wird auf dem Server gespeichert: Die Liste entsteht nur aus dem Formular.

## 3.15.0 — 2026-11-08

### Neu
- **Serien und Präfixe:** ein Text vor den Ziffern (A- ergibt A-0001). Bei mehreren, durch Kommas getrennten Serien wiederholt jede den Bereich und hat eigene PDFs. Das Präfix erlaubt Buchstaben, Leerzeichen, Punkt, Bindestrich und Schrägstrich (bis 6 Zeichen, keine Ziffern).
- **Nummern überspringen:** 13, 100-110 streicht diese Nummern aus der Folge (Zusammenfassung, Dateien und Prüfung zählen nur das Gedruckte).
- **Eine Farbe für jede Serie.**
- All das steckt auch in „Link kopieren“ und in der Vorschau.

## 3.14.0 — 2026-11-08

### Neu
- **Als App installieren (PWA):** Die Website lässt sich auf Handy oder Computer installieren; die App-Hülle öffnet sich auch offline (das Erzeugen braucht weiter den Server). Ein einfacher Service Worker speichert nur die Seite, die App-Dateien und die Oberflächentexte und berührt nie Ihre Dateien oder Erzeugungsanfragen.

## 3.13.0 — 2026-11-08

### Neu
- **Ziffern-Datei merken:** Wer im nächsten Jahr wiederkommt, muss sie nicht wiederholen. Sie bleibt nur in Ihrem Browser (nie auf dem Server) und wird mit einer neuen Vorlage wiederverwendet; eine andere Datei ersetzt sie, „Alles löschen“ entfernt sie.
- **Link kopieren:** Ein Knopf kopiert einen Link mit den Formularwerten (von, bis, Modus, Maximum pro Datei, Papier, Rand und Name). Wer ihn öffnet, sieht dieselben Werte; Dateien stecken nie im Link.

## 3.12.0 — 2026-11-08

### Neu
- Seiten **Nutzungsbedingungen**, **Datenschutzerklärung** und **Kontakt**, im Fuß verlinkt. Es sind vorläufige Fassungen, die vor einer Bezahlung des Dienstes juristisch zu prüfen sind.
- **Spenden-Knopf** im Fuß: Er erscheint nur, wenn der Betreiber den Link einrichtet. Kontakt-E-Mail und Name des Verantwortlichen stammen ebenfalls aus der Serverkonfiguration, nie aus dem Code.

## 3.11.0 — 2026-11-08

### Neu
- **Nutzungstrichter** im Admin-Bereich: wie viele Ereignisse es je Stufe gibt (Sitzung, Vorlage, Ziffern, Vorschau, Erzeugung, Download) und welcher Anteil der vorigen Stufe die nächste erreichte. Er zeigt, wo Leute abbrechen. Gezählt werden Ereignisse, nicht Personen.

## 3.10.0 — 2026-11-08

### Neu
- Diese Seite: der **Changelog** mit allem, was sich ändert, Version für Version.
- Im **Dezember** ist das automatische Design **Weihnachten** (für alle, die nie eines gewählt haben). Ein anderes Design bleibt weiter gespeichert.

### Verbessert
- Eine Abhängigkeit weniger auf dem Server (`python-multipart` wurde nicht mehr gebraucht: Dateien kommen als roher Body).

## 3.9.0 — 2026-11-08

### Neu
- Layout für **große Bildschirme** (4K, Ultrabreit) und **aktuelle Handys**: kompakte Kopfzeile und 44-px-Schaltflächen.
- Die Vorschau zeigt ein Bild, wenn der Browser PDFs nicht in der Seite anzeigen kann (Chrome auf Android).
- Der Admin-Bereich erfasst den **Bildschirmtyp** (Klasse, Größe, Familie), ohne Persönliches zu speichern.
- Der Dienst ruft sich alle 10 Minuten selbst auf, um nicht einzuschlafen.

## 3.8.0 — 2026-11-08

### Neu
- **Admin-Bereich** (nur für den Betreiber, mit Passwort) mit Diagrammen und Erklärungen zu System und Nutzung: nur Summen, nie personenbezogene Daten.

## 3.7.0 — 2026-11-08

### Neu
- **SEO**: Titel, Beschreibung und Text je Seite, `robots.txt`, `sitemap.xml` und ein echtes 404 für nicht vorhandene Seiten.

## 3.6.0 — 2026-11-08

### Verbessert
- Die Website liefert **eine einzige JavaScript-Datei**, verschleiert und vorkomprimiert: Das Übertragene ist deutlich kleiner als zuvor.

## 3.5.0 — 2026-11-08

### Neu
- Design **Matrix Gamer**: Regen grüner Zeichen und Neonglühen.

## 3.4.0 — 2026-11-08

### Verbessert
- Die Stile wechseln zu **Sass** und erscheinen als **ein einziges CSS**. Der Seitenaufbau ist in jedem Design gleich: Ein Design ändert nur Farben und Formatierung.

## 3.3.0 — 2026-11-07

### Neu
- **Designs**: Premiado (das neue Standardaussehen) und sieben weitere (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala und Natal), jeweils hell und dunkel.
- Neues App-Symbol.
