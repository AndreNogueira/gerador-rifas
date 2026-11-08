# Changelog (riassunto in italiano)

Riassunto tradotto di `../CHANGELOG.md`: stesse versioni, sezioni e punti, più brevi. Il testo completo è in portoghese.

## 3.23.0 — 2026-11-08

### Novità
- **Tutorial e video per ogni funzione:** il tutorial ha un argomento per funzione (serie, elenco e foglio di controllo, segni di taglio, galleria, marchio proprio, QR, estrazione, salvare e condividere, installare come app, temi), ciascuno con un breve video registrato nell'interfaccia stessa, in portoghese e inglese.
- **Changelog, Termini, Privacy e Contatti in 18 lingue:** il testo appare nella lingua scelta. Il Changelog ha un riassunto tradotto di ogni versione (quello completo è in portoghese); i testi legali sono traduzioni senza revisione madrelingua e, in caso di differenze, prevale la versione portoghese.
- **App Windows 2.4** con ciò che il sito ha ottenuto dalla 3.10: menu «Extra» con serie, prefissi e colore per serie, numeri esclusi, colore dei numeri, logo, segni di taglio, galleria di modelli, estrazione verificabile ed esportazione dell'elenco (CSV) e del foglio di controllo; e l'aspetto natalizio automatico a dicembre. Il QR di verifica e l'installazione come app restano solo sul sito.

## 3.22.0 — 2026-11-08

### Migliorato
- **Contrasto dei 9 temi misurato davvero:** un test in un browser misura il testo contro i pixel reali dello sfondo, in chiaro e scuro (WCAG AA), e ciò che non passava è stato corretto.
- I grandi numeri decorativi dei passi non sono più letti dagli screen reader.

## 3.21.0 — 2026-11-08

### Novità
- **Estrazione verificabile** (pagina «Estrazione»): estrae numeri da un intervallo (con numeri da escludere) in modo che chiunque possa ripeterla e ottenere lo stesso risultato, con un seme pubblico. Avviene nel browser e «Copia collegamento» condivide la stessa estrazione.
- Il metodo è descritto passo per passo, con un'implementazione di riferimento che dà gli stessi numeri del sito.

## 3.20.0 — 2026-11-08

### Novità
- **QR su ogni biglietto:** un QR di verifica in un angolo di ogni biglietto (modelli con un solo biglietto), con scelta di angolo e dimensione. Leggerlo apre una pagina che conferma che questo servizio ha emesso il codice per quel biglietto. È firmato con una chiave che ha solo il server; nessun database. Non prova pagamento né vincita.
- Compare solo se il gestore del servizio configura la chiave. Le richieste con QR hanno un tetto di 10 000 numeri.

## 3.19.0 — 2026-11-08

### Novità
- **Marchio proprio:** il colore dei numeri (qualsiasi modello; il colore della serie prevale) e il **logo** dell'associazione su ogni biglietto (PNG o JPG fino a 2 MB, modelli con un solo biglietto), con angolo e dimensione (dal 10 al 40 %). Il PNG mantiene la trasparenza.
- Il logo resta solo nella sessione (si cancella con essa e con «Cancella tutto») e si vede nell'anteprima.

## 3.18.0 — 2026-11-08

### Novità
- **Galleria di modelli:** scelga uno di quattro disegni (Bosque, Quermesse, Natal e Gala), scriva titolo, organizzazione, fino a tre premi e data, guardi l'anteprima e prema «Usa questo modello»: modello e cifre sono pronti. Ogni disegno è un biglietto con matrice.
- I disegni sono originali di questo progetto, nel carattere libero Vera. Il carattere ha solo l'alfabeto latino: con altre lettere compare un avviso.

## 3.17.0 — 2026-11-08

### Novità
- **Segni di taglio:** una casella nel pannello del foglio (modelli con un solo biglietto) disegna brevi tratti nei margini, a prolungare ogni linea di taglio. Servono almeno 3 mm di margine.
- La **matrice** (il numero due volte su ogni biglietto) già funzionava: ora è testata e documentata.
- La **rifilatura** è già rispettata: se il PDF di Canva ha una TrimBox più piccola della pagina, il biglietto è solo ciò che sta dentro.

## 3.16.0 — 2026-11-08

### Novità
- **Esportare l'elenco dei biglietti (CSV):** un file per Excel o Calc, un biglietto per riga (serie, numero e colonne Nome, Contatto e Pagato vuote), con prefissi, serie e numeri esclusi.
- **Foglio di controllo vendite (PDF):** una tabella A4 da stampare e compilare a mano (36 biglietti per pagina, con casella «pagato»). Nelle lingue le cui lettere il PDF non sa scrivere, le intestazioni escono in inglese.
- Nulla viene conservato sul server: l'elenco nasce solo dal modulo.

## 3.15.0 — 2026-11-08

### Novità
- **Serie e prefissi:** un testo prima delle cifre (A- dà A-0001). Con più serie separate da virgole, ognuna ripete l'intervallo e ha i propri PDF. Il prefisso accetta lettere, spazio, punto, trattino e barra (fino a 6 caratteri, senza cifre).
- **Saltare numeri:** 13, 100-110 toglie quei numeri dalla sequenza (riepilogo, file e verifica contano solo ciò che si stampa).
- **Un colore per ogni serie.**
- Tutto questo va anche in «Copia collegamento» e nell'anteprima.

## 3.14.0 — 2026-11-08

### Novità
- **Installare come app (PWA):** installi il sito su telefono o computer; il guscio dell'app si apre anche senza rete (generare richiede ancora il server). Un semplice service worker conserva solo la pagina, i file dell'app e i testi dell'interfaccia, e non tocca mai i suoi file né le richieste di generazione.

## 3.13.0 — 2026-11-08

### Novità
- **Ricordare il file delle cifre:** chi torna l'anno dopo non lo ripete. Resta solo nel suo browser (mai sul server) e si riusa con un modello nuovo; sceglierne un altro lo sostituisce e «Cancella tutto» lo elimina.
- **Copia collegamento:** un pulsante che copia un collegamento con i valori del modulo (da, a, modo, massimo per file, carta, margine e nome). Chi lo apre vede gli stessi valori; i file non viaggiano mai nel collegamento.

## 3.12.0 — 2026-11-08

### Novità
- Pagine **Termini di utilizzo**, **Informativa sulla privacy** e **Contatti**, collegate a piè di pagina. Sono versioni provvisorie, da rivedere con supporto legale prima che il servizio sia a pagamento.
- **Pulsante di donazione** a piè di pagina: compare solo se il proprietario configura il collegamento. L'e-mail di contatto e il nome del responsabile vengono anch'essi dalla configurazione del server, mai dal codice.

## 3.11.0 — 2026-11-08

### Novità
- **Imbuto di utilizzo** nel pannello di amministrazione: quanti eventi ci sono a ogni fase (sessione, modello, cifre, anteprima, generazione, download) e quale parte della fase precedente è arrivata alla successiva. Mostra dove le persone rinunciano. Conta eventi, non persone.

## 3.10.0 — 2026-11-08

### Novità
- Questa pagina: il **Changelog**, con tutto ciò che cambia, versione per versione.
- A **dicembre** il tema visivo automatico è il **Natale** (per chi non ne ha mai scelto uno). Scegliere un altro tema resta memorizzato.

### Migliorato
- Una dipendenza in meno sul server (`python-multipart` non era più usato: i file arrivano come corpo grezzo).

## 3.9.0 — 2026-11-08

### Novità
- Layout pensato per **schermi grandi** (4K, ultra-wide) e **telefoni recenti**: intestazione compatta e pulsanti da 44 px.
- L'anteprima mostra un'immagine quando il browser non può mostrare PDF nella pagina (Chrome su Android).
- Il pannello di amministrazione registra il **tipo di schermo** (classe, dimensione, famiglia) senza conservare nulla di personale.
- Il servizio si richiama ogni 10 minuti per non addormentarsi.

## 3.8.0 — 2026-11-08

### Novità
- **Pannello di amministrazione** (solo per il proprietario, con password) con grafici e spiegazioni su sistema e uso: solo aggregati, mai dati personali.

## 3.7.0 — 2026-11-08

### Novità
- **SEO**: titolo, descrizione e testo per pagina, `robots.txt`, `sitemap.xml` e un vero 404 per le pagine inesistenti.

## 3.6.0 — 2026-11-08

### Migliorato
- Il sito consegna **un solo file JavaScript**, offuscato e precompresso: ciò che viaggia è molto più piccolo di prima.

## 3.5.0 — 2026-11-08

### Novità
- Tema visivo **Matrix Gamer**: pioggia di caratteri verdi e bagliore neon.

## 3.4.0 — 2026-11-08

### Migliorato
- Gli stili passano a **Sass** e escono in **un solo CSS**. La struttura della pagina è uguale in tutti i temi: un tema cambia solo colori e formattazione.

## 3.3.0 — 2026-11-07

### Novità
- **Temi visivi**: Premiado (il nuovo aspetto predefinito) e altri sette (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala e Natal), ciascuno in chiaro e scuro.
- Nuova icona dell'applicazione.
