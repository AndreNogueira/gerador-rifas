# Changelog (riassunto in italiano)

Riassunto tradotto di `../CHANGELOG.md`: stesse versioni, sezioni e punti, più brevi. Il testo completo è in portoghese.

## 3.71.0 — 2026-11-20

### Novità
- **Buoni di gettoni numerati** (nel listino, con una valuta inventata; e «Extras → Listino prezzi… → Buoni numerati…» nell'app Windows): scegli quanti gettoni vale ogni buono, il titolo e una nota, guarda il buono con il disegno del listino e crealo. Si continua nel generatore di lotterie, che numera i buoni con serie, QR di verifica e fogli pronti da stampare.

## 3.70.0 — 2026-11-20

### Novità
- **Generatore di listini prezzi per feste** (`/precario`, e «Extras → Listino prezzi…» nell'app Windows): scegli l'occasione (viene suggerita quella del periodo) e gli articoli da un catalogo con immagini, scrivi i prezzi nella valuta del tuo paese o in una inventata (gettoni…) e scarica il PDF (o un'immagine) pronto da stampare, in A5, A4 o A3 e con i 24 disegni della galleria. C'è anche una nuova guida: «Come fare il listino prezzi di una festa».

## 3.69.0 — 2026-11-19

### Novità
- **Portoghese del Brasile** (`/pt-br`): il sito, le guide e le pagine legali esistono anche in portoghese del Brasile, con il suo vocabolario, un'Informativa sulla privacy adattata alla LGPD brasiliana e la lingua scelta da sola quando il browser è in pt-BR. Il portoghese del Portogallo resta uguale, senza prefisso nell'indirizzo.

## 3.68.0 — 2026-11-19

### Novità
- **Tre nuove guide, per tema** (non per pubblico): come numerare i biglietti di una lotteria, come fare un'estrazione verificabile (rimanda alla pagina «Estrazione») e quanti biglietti fare e a che prezzo. Sono in «Tutte le guide» (`/como-fazer`), in 22 lingue.

## 3.67.0 — 2026-11-19

### Novità
- **Indice delle guide «Come fare»** (`/como-fazer`): una pagina con tutte le guide e un riepilogo di ciascuna; ogni guida termina con link alle altre. Anche nel menu «Aiuto» («Tutte le guide»).
- Le guide e l'indice indicano a Google il loro percorso (Home › Come fare › guida) per mostrarlo nei risultati.

## 3.66.0 — 2026-11-19

### Novità
- **Invito a lasciare un commento:** dopo aver scaricato i biglietti compare (una sola volta per dispositivo) un avviso discreto che invita a lasciare un commento, anonimo se vuoi. Puoi chiuderlo con «Non ora».

## 3.65.0 — 2026-11-19

### Migliorato
- **Un sito più leggero e più sicuro:** chi genera solo biglietti scarica il 24 % di codice in meno (il pannello di amministrazione, l'editor dei modelli e l'estrazione si caricano solo quando si apre la pagina). Il sito ora invia anche intestazioni di sicurezza e risponde ai verificatori di link e alle anteprime di condivisione.

## 3.64.0 — 2026-11-19

### Novità
- **Copia di sicurezza settimanale dei dati del pannello di amministrazione:** ogni lunedì il servizio salva, nell'archiviazione dello stesso fornitore del database, una copia di storico, obiettivi, registro delle azioni, commenti e testi SEO (ultime 8 settimane), con uno script per ripristinarla.

## 3.63.0 — 2026-11-19

### Novità
- **Prestazioni reali del sito nelle statistiche:** il pannello di amministrazione mostra, per giorno, quanto impiega la pagina ad apparire, quanto si sposta il contenuto e quanto impiega a rispondere a un clic, misurato nei browser dei visitatori (cellulare e computer). Solo tre numeri anonimi per visita; l'Informativa sulla privacy è stata aggiornata.

## 3.62.0 — 2026-11-19

### Novità
- **Provenienza delle visite nelle statistiche:** il pannello di amministrazione mostra ora da dove arrivano le visite, in categorie generali (ricerca, social network, e-mail, altri siti o dirette) e per campagna (utm_source), per misurare una diffusione. L'indirizzo della pagina di origine e l'IP non vengono mai conservati; l'Informativa sulla privacy è stata aggiornata.

## 3.61.0 — 2026-11-19

### Novità
- **Registro delle azioni nel pannello di amministrazione:** chi ha fatto cosa e quando nel pannello viene conservato per 400 giorni (accessi, commenti eliminati o nascosti, chiavi API, testi SEO, obiettivi), senza dati dei visitatori né password.

## 3.60.0 — 2026-11-19

### Novità
- **Obiettivi giornalieri nel pannello di amministrazione:** il responsabile fissa un traguardo al giorno (sessioni, generazioni, numeri generati, download…) e vede se l'ultimo giorno l'ha raggiunto, la media degli ultimi 7 giorni e in quanti è stato raggiunto; il rapporto giornaliero via e-mail ha la stessa sezione.

## 3.59.0 — 2026-11-19

### Novità
- **Commenti con stato nel pannello di amministrazione:** il responsabile può segnare ogni commento come letto, preferito o nascosto (un commento nascosto scompare dalla pagina pubblica ma non si perde), filtrare per stato e vedere quanti restano da leggere.

## 3.58.0 — 2026-11-19

### Novità
- **Quote dell'hosting gratuito nel pannello di amministrazione:** si vede quante delle 750 ore mensili di Render il servizio ha usato (con la proiezione a fine mese) e quanto spazio occupa il database nel piano gratuito di Neon, con avviso nel rapporto giornaliero via e-mail prima che le quote finiscano.

## 3.57.0 — 2026-11-19

### Novità
- **Indicatori di versione nei grafici del pannello di amministrazione:** ogni grafico giornaliero segnala il giorno in cui è arrivata una nuova versione dell'app (e il rapporto giornaliero dice quale), per collegare un aumento di errori o dei tempi di risposta all'aggiornamento che lo ha causato.

## 3.56.0 — 2026-11-19

### Novità
- **Riepilogo settimanale e mensile via e-mail per il responsabile del sito:** il lunedì arriva il riepilogo della settimana e il giorno 1 quello del mese, con i totali confrontati con il periodo precedente e una miniatura di ogni giorno. Leggono dallo storico permanente. Solo conteggi.

## 3.55.0 — 2026-11-19

### Novità
- **Avvisi immediati via e-mail per il responsabile del sito:** se c'è una serie di errori del server, riavvii del motore, memoria vicina al limite o database che non risponde, arriva subito un avviso (senza attendere il rapporto giornaliero e senza ripetersi per 6 ore). Solo conteggi.

## 3.54.0 — 2026-11-19

### Novità
- **Storico permanente nel pannello di amministrazione:** dopo la mezzanotte si salva un riepilogo di ogni giorno, quindi l'evoluzione giornaliera mostra mesi e fino a 2 anni (prima solo 90 giorni). Solo conteggi, come il resto del pannello.

## 3.53.0 — 2026-11-19

### Novità
- **Rapporto giornaliero via e-mail per il responsabile del sito:** ogni giorno, subito dopo la mezzanotte, arriva un'e-mail con tutto ciò che è stato registrato nel giorno appena finito (utilizzo, pubblico, errori e risorse del server), confrontato con la media dei 7 giorni precedenti, per seguire l'app senza aprire il pannello. Solo conteggi: mai dati dei visitatori.

## 3.52.0 — 2026-11-19

### Migliorato
- **Commenti senza indirizzo IP:** al posto dell'IP si conserva solo il paese da cui è stato inviato il commento (lo vede solo il responsabile del sito). L'indirizzo IP non viene più conservato: quelli dei commenti precedenti sono stati eliminati e l'Informativa sulla privacy è stata aggiornata.

## 3.51.0 — 2026-11-19

### Novità
- **Commenti:** una pagina «Commenti» dove tutti vedono cosa pensano gli altri del generatore, e una pagina per lasciare il proprio: si può restare anonimi o mostrare un nome (senza nome compare «Visitatore n. …»). L'indirizzo IP è conservato solo per il responsabile del sito, per limitare gli abusi, non viene mai mostrato e si elimina dopo 90 giorni.
- **Segnala un problema:** nuova pagina dove descrive un errore e, premendo «Apri», viene creato direttamente sul GitHub del progetto, senza account (il suo IP non viene inviato e le informazioni tecniche del browser solo se le aggiunge).
- Le due pagine e i pulsanti «Commenti» e «Segnala un problema» sono ben visibili nell'intestazione, nel menu e a piè di pagina; l'Informativa sulla privacy (22 lingue) spiega cosa viene conservato.

## 3.50.0 — 2026-11-18

### Migliorato
- **Un'intestazione che si adatta allo schermo:** tutte le opzioni stanno a destra, su una sola riga e senza vuoti, e mentre lo schermo si restringe passano una a una in un menu «hamburger» (prima la modalità chiaro/scuro e lo stile, per ultima la donazione). Sul telefono restano solo il nome dell'app e il pulsante del menu, che apre pagine, aiuto, condivisione e impostazioni.

## 3.49.0 — 2026-11-18

### Novità
- **Pannello con l'evoluzione giorno per giorno:** una nuova vista «Evoluzione giornaliera» mostra, fino a 90 giorni, tutto ciò che il server salva nel database (sessioni, generazioni, numeri generati, lingue, paesi, stili, galleria, editor, API, richieste, tempi di risposta, CPU e memoria…), con la tendenza di ogni indicatore e il download di tutto in CSV. È una funzione del pannello del proprietario: i visitatori non notano differenze.

## 3.48.0 — 2026-11-18

### Migliorato
- **Menu «Aiuto» nell'intestazione:** il tutorial, il video e le guide «Come fare» sono riuniti in un'unica scheda, «Aiuto». L'intestazione è più corta e il nome dell'app compare sempre per intero su una sola riga, in qualsiasi lingua e dimensione dello schermo.

## 3.47.0 — 2026-11-15

### Migliorato
- **Galleria di modelli:** l'elenco dei disegni non viene più tagliato né messo fuori posto in alcuni temi; ogni premio ha il suo numero; ogni casella di testo mostra il limite di caratteri (ad esempio 12/50); e il pulsante «Usa questo modello» non resta più attaccato all'ultima casella.
- **Data dell'estrazione in un calendario proprio:** al posto del campo del browser (che mostrava «gg/mm/aaaa» e un selettore in una lingua diversa da quella del sito) c'è un calendario nelle 22 lingue, con mesi e giorni della settimana nella lingua scelta, la data scritta come la scrive quella lingua, il giusto primo giorno della settimana e i pulsanti «Oggi» e «Cancella». Funziona con la tastiera (frecce, Pag su/giù, Home/Fine, Invio ed Esc).
- **Un «Informazioni» più completo:** il testo è stato riscritto, nelle 22 lingue, e spiega a chi è destinato il generatore, cosa fa, cosa fare dopo la stampa, come protegge la privacy e dove si può usare.

## 3.46.0 — 2026-11-15

### Migliorato
- **Donazione più visibile:** quando il servizio ha un link per le donazioni, il pulsante compare ora nell'intestazione (accanto a «Condividi») e, dopo aver generato i file, con un breve invito. Resta anche a piè di pagina.

## 3.45.0 — 2026-11-14

### Migliorato
- **Galleria di modelli su una sola riga:** i 24 disegni si scelgono ora in una casella di una riga in cui ogni opzione mostra una miniatura del modello, invece di una lunga lista di pulsanti. Funziona con mouse, tocco e tastiera (frecce, Home/Fine, una lettera, Invio ed Esc).

## 3.44.0 — 2026-11-14

### Migliorato
- **Privacy:** i conteggi d'uso includono ora il paese della visita (solo il codice, ricavato dalla rete dell'hosting; l'indirizzo IP continua a non essere conservato). L'informativa sulla privacy lo spiega in tutte le 22 lingue.

## 3.43.1 — 2026-11-14

### Migliorato
- **Piè di pagina più pulito:** le guide «Come fare» compaiono ormai solo nel gruppo dell'intestazione; non si ripetono più in fondo alla pagina.

## 3.43.0 — 2026-11-14

### Migliorato
- **Data dell'estrazione in un calendario:** nella galleria dei modelli si sceglie la data in un calendario e poi come appare sul biglietto (31/12/2026, 31 dic 2026, 31 dicembre 2026 o con il giorno della settimana), scritta nella lingua del sito. Si può ancora scrivere a mano, ora fino a 60 caratteri.
- **Testi più larghi:** le pagine di testo (guide, tutorial, termini…) ora occupano tutta la larghezza della pagina, con meno righe e paragrafi.

## 3.42.0 — 2026-11-14

### Migliorato
- **Intestazione:** il nuovo gruppo «Come fare», accanto al tutorial, raccoglie le guide (scuole, associazioni, club, vigili del fuoco, feste di quartiere e parrocchie). Il pulsante «Condividi» è passato dal piè di pagina all'intestazione, in evidenza, e il suo elenco mostra le icone di WhatsApp, Telegram, Facebook, e-mail e «Copia link».

## 3.41.0 — 2026-11-14

### Migliorato
- **Anteprima automatica:** quando cambia il modello, le cifre, il logo o qualsiasi campo che modifica la pagina finale (numeri, cifre, foglio, serie, colori, QR…), l'anteprima con numeri reali si rifà da sola, senza premere «Anteprima». Se qualcosa non va, il motivo compare accanto al visore, senza finestre.

## 3.40.0 — 2026-11-14

### Novità
- **Da 3 a 10 premi nella galleria:** nei 24 disegni della galleria si sceglie quanti premi ha il biglietto (da 3 a 10; prima al massimo 3). Da 6 in su vanno su due colonne. Anche nell'app Windows.

## 3.39.0 — 2026-11-13

### Novità
- **App Windows 2.7:** la galleria e l'editor di modelli accettano ora latino esteso, vietnamita, greco, cirillico, cinese, giapponese e coreano, come il sito dalla 3.37 (l'hindi, l'arabo e l'ebraico mancano ancora). Si scarica dalla pagina del Changelog.

## 3.38.0 — 2026-11-13

### Novità
- **Pulsante «Condividi»:** a piè di pagina e, dopo aver generato i file, nella scheda della consegna. Apre un breve elenco (condivisione del telefono o del computer, WhatsApp, Telegram, Facebook, e-mail e «Copia link») per far conoscere il generatore ad altre associazioni, scuole e comitati di feste. I link contengono solo l'indirizzo del sito nella lingua in uso: nessun tracciamento, nulla viene conservato. Ha un argomento nel tutorial e un video.

## 3.37.0 — 2026-11-13

### Novità
- **Più lettere nella galleria e nell'editor di modelli:** i testi possono ora usare il latino esteso (polacco, ceco, rumeno, turco…), il **vietnamita, il greco, il cirillico (russo, ucraino)**, il **cinese, il giapponese e il coreano**. L'hindi, l'arabo e l'ebraico mancano ancora (richiedono una tecnologia di scrittura che il generatore di PDF non ha) e mostrano un avviso invece di un'immagine rovinata. Nei PDF cambia solo il testo scritto da chi usa; ciò che usciva già uguale resta uguale.

## 3.36.0 — 2026-11-13

### Novità
- **Guida «Come fare» per le parrocchie:** «Per le parrocchie» (link a piè di pagina), con il passo passo per fare una lotteria parrocchiale: feste del patrono, sagre, lavori, cesti di Natale e catechismo. È in tutte le 22 lingue e ricorda di verificare in Comune se la lotteria richiede un'autorizzazione.

## 3.35.0 — 2026-11-13

### Novità
- **App Windows 2.6:** il menu «Extras» guadagna «Salva richiesta…» e «Apri richiesta…» (un file .rifas con i numeri, il nome, le serie, i colori e i segni di taglio, senza modello né percorsi), l'editor di modelli può aggiungere immagini (PNG o JPG) e «Vista → Visuale» passa da 2 ai 14 temi del sito (solo i colori). Porta anche ciò che è arrivato dalla 2.4: l'editor, i 24 disegni della galleria e le 22 lingue.

## 3.34.0 — 2026-11-13

### Novità
- **Tre nuove guide «Come fare»:** «Per i club», «Per i vigili del fuoco» e «Per le feste di quartiere» (link a piè di pagina), con il passo passo per fare una lotteria in ogni caso. Sono in tutte le 22 lingue e ricordano di verificare in Comune se la lotteria richiede un'autorizzazione.

## 3.33.0 — 2026-11-13

### Novità
- **API pubblica per lotti** (`/api/v1`, con Swagger su `/api/v1/docs`): permette ad altri programmi di generare più richieste di biglietti da un solo modello, con chiave, quote giornaliere e limiti. Chi usa il sito passa sempre per primo.
- **Quattro nuove lingue:** catalano, ucraino, indonesiano e vietnamita. Il sito e l'app Windows passano a 22 lingue, con tutorial, termini, privacy, guide pratiche e schermate.
- **Testi per i motori di ricerca modificabili per lingua:** il proprietario modifica nel pannello di amministrazione titoli, descrizioni e guide di ogni lingua, salvati nel database e senza nuovo deploy.

## 3.32.0 — 2026-11-13

### Novità
- **20 nuovi modelli nella galleria (24 in totale):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Tutti disegnati da zero per questo progetto, con matrice, sul sito e nell'app Windows (dove la galleria diventa un elenco a discesa).

## 3.31.0 — 2026-11-13

### Novità
- **Editor di modelli v2:** annulla e ripeti (Ctrl+Z, Ctrl+Y), duplica (Ctrl+D), cambia l'ordine di disegno, aggiungi il logo (PNG o JPG) e **condividi il disegno con un link**: resta salvato 90 giorni dall'ultimo accesso, senza immagini e senza dati su chi condivide (compare solo se il servizio ha un database). L'informativa sulla privacy lo dice.
- **App Windows 2.5:** riceve l'editor di modelli (menu Extra) e passa a Python 3.15.

### Migliorato
- Il Changelog ha un link per scaricare l'app Windows.

## 3.30.0 — 2026-11-12

### Novità
- **Pagine «Come fare»:** due guide scritte, «Per le scuole» e «Per le associazioni» (link nel piè di pagina), con il passo passo per fare una lotteria: disegnare il biglietto, una serie per classe o venditore, stampare con segni di taglio, controllare le vendite e fare un'estrazione verificabile. Sono nelle 18 lingue e ricordano di verificare in comune se la lotteria richiede un'autorizzazione.

## 3.29.0 — 2026-11-12

### Migliorato
- **Annunci ai lati:** quando gli annunci sono attivi (per ora non lo sono), sugli schermi larghi compaiono ai due lati del contenuto, uno per lato, fissi e senza spostare la pagina; sugli altri schermi c'è un solo blocco in fondo alla pagina. Continuano a non comparire nell'editor, nei file generati né nell'app Windows.

## 3.28.0 — 2026-11-12

### Novità
- **Annunci di Google (predisposti, disattivati):** il sito può mostrare un blocco di annunci di Google (AdSense) in fondo alla pagina iniziale, al tutorial, a «Informazioni», all'estrazione e al changelog. Non compaiono mai nell'editor, nei file generati, nella verifica dei biglietti, nel pannello né nell'app Windows, e nello Spazio economico europeo e nel Regno Unito solo dopo la sua scelta nel messaggio di consenso di Google. L'informativa sulla privacy lo dice, nelle 18 lingue, quando gli annunci sono attivi; per ora sono disattivati finché il titolare del servizio non li configura.

## 3.27.0 — 2026-11-12

### Novità
- **Editor di modelli:** invece di un modello di Canva, disegni il biglietto sul sito (pagina «Editor di modelli», collegata dal passo 1): aggiunga testi, rettangoli, linee e il numero 0001 (una volta, o due con la matrice), trascini ogni elemento con il mouse o le frecce, cambi colori, dimensioni e sfondo e prema «Usa questo modello». Lo schermo usa il carattere Vera, lo stesso del PDF: ciò che vede è ciò che ottiene; la bozza resta solo nel browser. I testi non possono contenere sequenze come 0123, che il programma confonderebbe con il numero del biglietto (lo schermo e il server avvisano).

## 3.26.0 — 2026-11-12

### Novità
- **Cinque nuovi temi:** Halloween, Spiaggia, Giornale antico, Terminale verde e Manifesto del circo, ciascuno in chiaro e scuro. Il sito ha ora 14 temi; la struttura è uguale in tutti (cambiano solo colori e aspetto).

## 3.25.0 — 2026-11-08

### Novità
- **Un indirizzo per lingua per i motori di ricerca:** ogni lingua ha il proprio indirizzo (/en, /ja/tutorial…) con titolo, descrizione e testo in quella lingua, e il sito indica a Google quali versioni sono equivalenti (hreflang). Il portoghese resta su /. La lingua scelta compare ora nella barra degli indirizzi.

## 3.24.1 — 2026-11-08

### Migliorato
- **Caselle allineate:** «Un colore per serie» e le altre caselle ora stanno accanto al loro testo, non all'estremità opposta della scheda.

## 3.24.0 — 2026-11-08

### Migliorato
- **Tutorial con schermate del sito:** gli argomenti di base del tutorial mostrano ora il sito stesso, in tutte le 18 lingue, invece dell'app Windows.

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
