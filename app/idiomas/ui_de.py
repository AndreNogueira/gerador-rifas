T = {
    "m_ficheiro": "Datei", "m_ver": "Ansicht", "m_idioma": "Sprache", "m_ajuda": "Hilfe",
    "mi_abrir_template": "Vorlage öffnen…", "mi_abrir_alg": "Ziffern-Datei wählen…",
    "mi_destino": "Zielordner wählen…", "mi_sair": "Beenden",
    "mi_zoom_mais": "Vergrößern", "mi_zoom_menos": "Verkleinern", "mi_ajustar": "An Fenster anpassen",
    "mi_expandir": "Vorschau erweitern", "mi_reduzir": "Vorschau verkleinern",
    "mi_tema": "Design", "mi_tema_sistema": "Wie Windows", "mi_tema_claro": "Hell", "mi_tema_escuro": "Dunkel",
    "mi_tutorial": "Anleitung Schritt für Schritt", "mi_sobre": "Info…",
    "sobre_texto": ("{app}\nVersion {versao}\n\nErstellt nummerierte Lose als PDF aus einer Canva-Vorlage.\n\n"
                    "Verwendet pypdf, pypdfium2, Pillow und CustomTkinter (freizügige Lizenzen)."),
    "tip_tema": "Zwischen hellem und dunklem Design wechseln",
    "tut_titulo": "Anleitung", "tut_ant": "Zurück", "tut_seg": "Weiter",
    "tut_t0": "Überblick",
    "tut_b0": ("Dieses Programm nimmt Ihr in Canva gestaltetes Los und erstellt druckfertige PDFs mit den Nummern, "
               "die Sie möchten.\n\n"
               "Es sind nur 4 Schritte, in der Reihenfolge links:\n\n"
               "• 1 – die Vorlage wählen (das PDF aus Canva);\n"
               "• 2 – die Datei mit den Ziffern 0 bis 9 wählen;\n"
               "• 3 – angeben, von welcher bis zu welcher Nummer, und ob mehrere PDFs oder eines;\n"
               "• 4 – den Ordner wählen und den Dateinamen eingeben.\n\n"
               "Klicken Sie dann auf „{previa}“, um eine Seite zu sehen, und auf „{gerar}“. "
               "Am Ende wird jedes PDF automatisch geprüft."),
    "tut_b1": ("Gestalten Sie das Los in Canva und schreiben Sie auf jedes Los die Beispielnummern 0001, 0002, "
               "0003, … (eine pro Los). Jede Nummer erscheint 2-mal: einmal auf dem Abschnitt und einmal im "
               "Hauptteil des Loses (siehe Bild).\n\n"
               "Laden Sie es als PDF herunter und wählen Sie diese Datei in Schritt 1.\n\n"
               "• Das Programm erkennt selbst, wie viele Lose pro Seite sind und wie der Text des Abschnitts ausgerichtet ist.\n"
               "• Die Nummern müssen Text sein, kein Bild.\n"
               "• Andere Zahlen im Entwurf (Jahr, Telefon …) bleiben unverändert.\n"
               "• Nur die 1. Seite des PDFs wird verwendet."),
    "tut_b3": ("• {de} / {ate}: die erste und die letzte zu erzeugende Nummer (z. B. 1 bis 1000).\n"
               "• {algarismos}: mit wie vielen Ziffern geschrieben wird (4 → 0001). Standard ist die Zahl aus der "
               "Vorlage; bei mehr Ziffern werden die Nummern verkleinert, damit sie passen.\n"
               "• {varios}: teilt in Dateien mit höchstens der angegebenen Anzahl Nummern (ein Vielfaches der Lose "
               "pro Seite).\n"
               "• {unico}: alles in einer Datei.\n\n"
               "Unten sehen Sie die Zusammenfassung: wie viele Nummern, Dateien und Seiten entstehen."),
    "tut_b4": ("Wählen Sie den Ordner, in dem die PDFs gespeichert werden, und geben Sie den Dateinamen ein "
               "(Pflicht; das Programm schlägt nie einen vor). Die Dateien heißen „NAME - 0001 - 0300.pdf“, "
               "„NAME - 0301 - 0600.pdf“, … oder nur „NAME - 0001 - 1000.pdf“ bei einem einzigen PDF.\n\n"
               "Existieren Dateien mit diesen Namen schon, fragt das Programm vor dem Ersetzen."),
    "tut_t5": "Vorschau und Erzeugen",
    "tut_b5": ("„{previa}“ zeigt die 1. Seite mit echten Nummern, damit Sie Schrift, Größe und Position prüfen "
               "können, bevor alles erzeugt wird.\n\n"
               "Im Betrachter:\n"
               "• − / + oder Strg + Mausrad: Zoom;\n"
               "• ziehen zum Verschieben; Doppelklick oder „{ajustar}“: ganzes Blatt sehen;\n"
               "• die Schaltfläche zum Erweitern gibt der Vorschau das ganze Fenster; erneut klicken, um zurückzukehren;\n"
               "• auch die Trennlinie zwischen Einstellungen und Betrachter lässt sich ziehen.\n\n"
               "Klicken Sie auf „{gerar}“. Der Balken zeigt den Fortschritt (Abbrechen möglich). Am Ende wird jedes "
               "PDF automatisch geprüft (Seiten und Nummern) und die Schaltfläche „{pasta}“ erscheint."),
    "tut_t6": "Tipps und Probleme",
    "tut_b6": ("• „Beispielnummern nicht gefunden“: In Canva müssen die Nummern Text sein, im Format 0001, 0002, … "
               "(jede 2-mal).\n"
               "• Die Nummern erscheinen in einer anderen Schrift: Die Ziffern-Datei muss genau dieselbe Schrift "
               "wie die Vorlage verwenden. Prüfen Sie es in der Vorschau.\n"
               "• Nummern zu klein oder seltsam: Bei PNG/JPG ein großes Bild verwenden (≥ 100 px hoch); PDF ist immer besser.\n"
               "• „Speichern nicht möglich“: PDF schließen, falls es in einem anderen Programm geöffnet ist.\n"
               "• Mehr Ziffern als im Entwurf: Die Größe wird automatisch verringert (Hinweis im Protokoll).\n"
               "• Sprache und Design (hell/dunkel) lassen sich in den Menüs ändern; die Farben folgen Windows."),
    'err_folha_varias': 'Nur eine Vorlage mit einem einzigen Los kann auf dem Blatt wiederholt werden.',
    'err_rifa_grande': 'Das Los ({w} × {h} mm) passt nicht auf ein {papel}-Blatt mit {margem} mm Rand.\n\nWählen Sie ein größeres Papier, verkleinern Sie den Rand oder gestalten Sie ein kleineres Los.',
    'log_folha': '{papel}-Blatt: {n} Lose pro Blatt (je {w} × {h} mm).',
    'aviso_muitas': '⚠ {n} Lose pro Blatt: sie werden sehr klein und schwer auszuschneiden. Prüfen Sie die Losgröße.',
    'c1_ok_uma': '✔ Vorlage mit 1 Los · Beispielnummer {primeiro}',
    'lay_info': 'Die Vorlage enthält ein einziges Los: Das Programm füllt das Blatt mit Kopien, so viele wie passen.',
    'lay_papel': 'Papier',
    'lay_margem': 'Rand (mm)',
    'lay_por_folha': 'Lose pro Blatt',
    'lay_resultado': 'Los mit {w} × {h} mm → {n} pro {papel}-Blatt (maximal {max})',
    'lay_recortada': ' · auf die Gestaltung zugeschnitten',
    'lay_rodadas': ' · {r} um 90° gedreht',
    'lay_acima': 'Es passen nur {max} auf ein Blatt.',
    'conf_muitas': 'Sie erzeugen {n} Lose pro Blatt (je {w} × {h} mm). Das ist sehr viel: Sie werden klein und schwer auszuschneiden.\n\nFortfahren?',
    'mi_video': 'Video-Anleitung',
    'video_falta': 'Das Video wurde nicht gefunden ({nome}).',
    'tut_t_uma': 'Ein einziges Los in der Vorlage',
    'tut_b_uma': 'Sie müssen nicht das ganze Blatt gestalten. Erstellen Sie in Canva eine Seite in der Größe eines Loses („Benutzerdefinierte Größe“, z. B. 19 × 5,5 cm) und schreiben Sie nur eine Beispielnummer, 0001 (auf dem Abschnitt und auf dem Hauptteil oder nur an einer Stelle).\n\nWenn Sie dieses PDF wählen, erkennt das Programm, dass es nur ein Los gibt, und zeigt „{papel}“, „{margem}“ und „{porfolha}“: Es füllt das Blatt mit Kopien des Loses, so viele wie passen (um 90° gedreht, wenn dann mehr passen), und nummeriert sie der Reihe nach. Die Vorschau zeigt das Blatt so, wie es gedruckt wird.\n\n• Papier (A4, A3, A5, Letter, Legal) und Rand (Drucker drucken nicht bis zum Rand) lassen sich ändern.\n• Ist die PDF-Seite größer als das Los, schneidet das Programm den gezeichneten Bereich zu.\n• „{porfolha}“ beginnt beim Maximum; Sie können weniger wählen.\n• Passen viele Lose (mehr als 24), warnt das Programm: Sie sind klein und schwer auszuschneiden.\n• Hat Ihr PDF schon mehrere Lose pro Seite (0001, 0002, …), funktioniert alles wie bisher.',
    'tut_video': 'Lieber als Video? Öffnen Sie das Menü „{ajuda}“ › „{video}“.',
    'limpar': 'Alles zurücksetzen',
    'tut_limpar': 'Wenn alles fertig ist, setzt „{limpar}“ (oder Menü „{ficheiro}“ › „{limpar}“) alles zurück – Vorlage, Ziffern, Ordner, Name, Nummern und Vorschau –, damit Sie eine neue Verlosung beginnen können.',
}
