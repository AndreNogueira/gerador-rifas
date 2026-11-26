"""Termini, privacy e contatti in italiano: traduzione di `pt.py` (stesse pagine, sezioni, paragrafi e {segnaposto}). Senza revisione madrelingua; prevale il portoghese."""
FRASES = {
    "responsavel_com": "Il servizio è gestito da {nome}.",
    "responsavel_sem": "Il servizio è gestito dal suo autore, la persona che lo rende disponibile online.",
    "contacto_com": "Può contattarci a {email}.",
    "contacto_sem": "Al momento non c'è un contatto pubblico.",
    "contacto_pagina_com": "Per dubbi, errori o suggerimenti scriva a {email}.",
    "contacto_pagina_sem": "Al momento non c'è un contatto pubblico. Torni su questa pagina più tardi.",
    "atualizado": "21 novembre 2026",
}

AVISO = ("Versione provvisoria, da rivedere con supporto legale. Se qualcosa qui differisce da ciò che fa il servizio, ci chieda di correggerlo. "
         "È una traduzione senza revisione madrelingua: in caso di differenze prevale la versione portoghese.")

TEXTOS = {
    "termos": {
        "titulo": "Termini di utilizzo",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Che cos'è questo servizio",
             "paragrafos": ["Il Generatore di rifle crea, a partire da un modello PDF, i biglietti numerati di una lotteria pronti da stampare. Fa solo questo: non vende biglietti, "
                            "non riceve denaro, non conserva elenchi di partecipanti e non fa estrazioni con valore legale.",
                            "{responsavel}"]},
            {"titulo": "Chi organizza la lotteria ne è responsabile",
             "paragrafos": ["Lotterie, tombole ed estrazioni sono soggette a norme di legge (per esempio autorizzazioni del comune e regole per le associazioni) che variano caso per caso. "
                            "Chi organizza la lotteria è l'unico responsabile del rispetto della legge, della riscossione e della consegna dei premi. Questo servizio non fornisce consulenza legale."]},
            {"titulo": "Uso consentito",
             "paragrafos": ["Il servizio è gratuito e per un uso ragionevole. Non può essere usato per produrre biglietti di frodi né per sovraccaricare il server: ci sono limiti alla dimensione "
                            "dei file, ai numeri per richiesta ({max_numeros}) e alle richieste al minuto, e una sola generazione alla volta."]},
            {"titulo": "I suoi file",
             "paragrafos": ["Il modello e le cifre servono solo a generare i suoi biglietti e vengono cancellati dal server dopo {validade} minuti di inattività, o quando preme «Cancella tutto». "
                            "Non li usiamo per altro. Restano suoi: basta avere il diritto di usare ciò che carica (immagini, caratteri, loghi)."]},
            {"titulo": "Nessuna garanzia",
             "paragrafos": ["Il servizio è fornito «così com'è», senza garanzia di essere sempre disponibile o privo di errori. Controlli sempre i PDF prima di stampare (il servizio verifica "
                            "i numeri generati, ma il controllo finale è suo). Nei limiti consentiti dalla legge, non rispondiamo di perdite legate all'uso del servizio."]},
            {"titulo": "Modifiche",
             "paragrafos": ["Questi termini possono cambiare; la data dell'ultimo aggiornamento è {atualizado}. Se un giorno il servizio diventerà a pagamento, verrà detto chiaramente prima di addebitare."]},
            {"titulo": "Contatti", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Informativa sulla privacy",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Riepilogo",
             "paragrafos": ["Non ci sono account, né pubblicità, né strumenti di tracciamento di terzi. I suoi file vengono cancellati dal server entro {validade} minuti. "
                            "Le statistiche d'uso sono solo numeri aggregati."]},
            {"titulo": "Quali dati trattiamo",
             "paragrafos": ["I file che carica (modello e cifre) sono trattati solo per generare i biglietti, restano in una cartella temporanea del server e vengono cancellati dopo {validade} minuti "
                            "di inattività o quando preme «Cancella tutto».",
                            "Per sapere come viene usato il servizio registriamo conteggi: quante visite, generazioni e download, la lingua e il tema scelti e il tipo di schermo. "
                            "Registriamo anche il paese della visita (solo il codice, per esempio «PT»), che la rete dell'hosting ricava dall'indirizzo IP; l'IP in sé non lo conserviamo. Non registriamo mai indirizzi IP, nomi di file, contenuto dei file né l'identificazione completa del browser.",
                            "L'indirizzo IP è usato solo in memoria, per istanti, per limitare il numero di richieste al minuto, e non viene conservato da noi. Il fornitore di hosting "
                            "(Render, a Francoforte, nell'Unione europea) può registrare indirizzi IP nei suoi registri tecnici."]},
            {"titulo": "Nel suo browser",
             "paragrafos": ["Conserviamo nel suo browser (archiviazione locale) le sue preferenze: la lingua, il tema visivo, la modalità chiara o scura e gli ultimi valori del modulo. "
                            "Per non ripetere il lavoro da un anno all'altro, anche il file delle cifre può restare nel suo browser (mai sul nostro server); «Cancella tutto» lo elimina. "
                            "Non usiamo cookie pubblicitari né di tracciamento."]},
            {"titulo": "Base giuridica e conservazione",
             "paragrafos": ["Trattiamo questi dati per legittimo interesse a fornire il servizio e a mantenerlo sicuro (GDPR, articolo 6, paragrafo 1, lettera f). I file durano minuti; "
                            "i conteggi aggregati non identificano nessuno."]},
            {"titulo": "I suoi diritti",
             "paragrafos": ["Ha diritto di accesso, rettifica, cancellazione e opposizione, e di presentare reclamo alla sua autorità per la protezione dei dati (in Portogallo la CNPD, cnpd.pt). "
                            "Poiché non conserviamo dati che la identifichino, in pratica c'è poco da consultare o cancellare; in caso di dubbi, ci contatti."]},
            {"titulo": "Chi risponde", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Aggiornamento", "paragrafos": ["Ultimo aggiornamento: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Contatti",
        "aviso": "",
        "seccoes": [
            {"titulo": "Ci scriva",
             "paragrafos": ["{contacto_pagina}",
                            "Se trova un errore, ci dica cosa ha fatto e cosa si aspettava; non invii il suo modello se contiene dati personali."]},
        ],
    },
}
