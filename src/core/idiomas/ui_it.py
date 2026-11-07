T = {
    "m_ficheiro": "File", "m_ver": "Visualizza", "m_idioma": "Lingua", "m_ajuda": "Aiuto",
    "mi_abrir_template": "Apri modello…", "mi_abrir_alg": "Scegli il file delle cifre…",
    "mi_destino": "Scegli la cartella di destinazione…", "mi_sair": "Esci",
    "mi_zoom_mais": "Ingrandisci", "mi_zoom_menos": "Riduci", "mi_ajustar": "Adatta alla finestra",
    "mi_expandir": "Espandi l’anteprima", "mi_reduzir": "Riduci l’anteprima",
    "mi_tema": "Tema", "mi_tema_sistema": "Come Windows", "mi_tema_claro": "Chiaro", "mi_tema_escuro": "Scuro",
    "mi_tutorial": "Tutorial passo passo", "mi_sobre": "Informazioni…",
    "sobre_texto": ("{app}\nVersione {versao}\n\nCrea PDF di biglietti della lotteria numerati da un modello Canva.\n\n"
                    "Usa le librerie pypdf, pypdfium2, Pillow e CustomTkinter (licenze permissive)."),
    "tip_tema": "Passa dal tema chiaro a quello scuro",
    "tut_titulo": "Tutorial", "tut_ant": "Indietro", "tut_seg": "Avanti",
    "tut_t0": "Panoramica",
    "tut_b0": ("Questo programma prende il tuo disegno della lotteria fatto in Canva e crea PDF pronti da stampare "
               "con i numeri che vuoi.\n\n"
               "Bastano 4 passi, nell’ordine mostrato a sinistra:\n\n"
               "• 1 – scegli il modello (il PDF di Canva);\n"
               "• 2 – scegli il file con le cifre da 0 a 9;\n"
               "• 3 – indica da quale a quale numero, e se vuoi più PDF o uno solo;\n"
               "• 4 – scegli la cartella e scrivi il nome dei file.\n\n"
               "Poi fai clic su «{previa}» per vedere una pagina e su «{gerar}». "
               "Alla fine ogni PDF viene controllato automaticamente."),
    "tut_b1": ("In Canva disegna la lotteria e scrivi su ogni biglietto i numeri di esempio 0001, 0002, 0003, … "
               "(uno per biglietto). Ogni numero compare 2 volte: una sulla matrice e una sulla parte principale "
               "del biglietto (vedi l’immagine).\n\n"
               "Scaricalo in PDF e scegli quel file al passo 1.\n\n"
               "• Il programma rileva da solo quanti biglietti ci sono per pagina e l’orientamento del testo della matrice.\n"
               "• I numeri devono essere testo, non immagine.\n"
               "• Gli altri numeri del disegno (anno, telefono…) restano come sono.\n"
               "• Viene usata solo la 1ª pagina del PDF."),
    "tut_b3": ("• {de} / {ate}: il primo e l’ultimo numero da generare (ad esempio da 1 a 1000).\n"
               "• {algarismos}: con quante cifre scrivere (4 → 0001). Per impostazione predefinita è quello del "
               "modello; se ne chiedi di più, i numeri si rimpiccioliscono per starci.\n"
               "• {varios}: divide in file con al massimo il numero di biglietti indicato (multiplo dei biglietti "
               "per pagina).\n"
               "• {unico}: tutto in un solo file.\n\n"
               "Sotto vedi il riepilogo: quanti numeri, file e pagine verranno creati."),
    "tut_b4": ("Scegli la cartella dove salvare i PDF e scrivi il nome dei file (obbligatorio; il programma non ne "
               "suggerisce mai uno). I file diventano «NOME - 0001 - 0300.pdf», «NOME - 0301 - 0600.pdf», … "
               "oppure solo «NOME - 0001 - 1000.pdf» con un unico PDF.\n\n"
               "Se esistono già file con quei nomi, il programma chiede prima di sostituirli."),
    "tut_t5": "Anteprima e generazione",
    "tut_b5": ("«{previa}» mostra la 1ª pagina con numeri veri, per controllare carattere, dimensione e posizione "
               "prima di generare tutto.\n\n"
               "Nel visualizzatore:\n"
               "• − / + oppure Ctrl + rotellina: zoom;\n"
               "• trascina per spostare; doppio clic o «{ajustar}»: vedi tutto il foglio;\n"
               "• il pulsante di espansione dà tutta la finestra all’anteprima; fai di nuovo clic per tornare;\n"
               "• anche il divisore tra le impostazioni e il visualizzatore si può trascinare.\n\n"
               "Fai clic su «{gerar}». La barra mostra l’avanzamento (puoi annullare). Alla fine ogni PDF viene "
               "controllato automaticamente (pagine e numeri) e compare il pulsante «{pasta}»."),
    "tut_t6": "Consigli e problemi",
    "tut_b6": ("• «Non ho trovato i numeri di esempio»: in Canva i numeri devono essere testo, nel formato 0001, 0002, … "
               "(ciascuno 2 volte).\n"
               "• I numeri escono con un altro carattere: il file delle cifre deve usare esattamente lo stesso "
               "carattere del modello. Controlla nell’anteprima.\n"
               "• Numeri troppo piccoli o strani: con PNG/JPG usa un’immagine grande (≥ 100 px di altezza); il PDF è sempre meglio.\n"
               "• «Impossibile salvare»: chiudi il PDF se è aperto in un altro programma.\n"
               "• Più cifre del disegno: la dimensione si riduce automaticamente (avviso nel registro).\n"
               "• Puoi cambiare lingua e tema (chiaro/scuro) nei menu; i colori seguono Windows."),
    'err_folha_varias': 'Solo un template con un unico biglietto può essere ripetuto sul foglio.',
    'err_rifa_grande': 'Il biglietto ({w} × {h} mm) non entra in un foglio {papel} con margini di {margem} mm.\n\nScelga una carta più grande, riduca il margine o disegni un biglietto più piccolo.',
    'log_folha': 'Foglio {papel}: {n} biglietti per foglio ({w} × {h} mm ciascuno).',
    'aviso_muitas': '⚠ {n} biglietti per foglio: saranno molto piccoli e difficili da ritagliare. Controlli la dimensione del biglietto.',
    'c1_ok_uma': '✔ Template con 1 biglietto · numero di esempio {primeiro}',
    'lay_info': 'Il template ha un solo biglietto: il programma riempie il foglio di copie, quante ne entrano.',
    'lay_papel': 'Carta',
    'lay_margem': 'Margine (mm)',
    'lay_por_folha': 'Biglietti per foglio',
    'lay_resultado': 'Biglietto di {w} × {h} mm → {n} per foglio {papel} (massimo {max})',
    'lay_recortada': ' · ritagliato sul disegno',
    'lay_rodadas': ' · {r} ruotati di 90°',
    'lay_acima': 'Su un foglio ne entrano solo {max}.',
    'conf_muitas': 'Sta per generare {n} biglietti per foglio ({w} × {h} mm ciascuno). Sono molti: saranno piccoli e difficili da ritagliare.\n\nContinuare?',
    'mi_video': 'Video tutorial',
    'video_falta': 'Non ho trovato il video ({nome}).',
    'tut_t_uma': 'Un solo biglietto nel template',
    'tut_b_uma': "Non serve disegnare tutto il foglio. In Canva crei una pagina grande quanto un biglietto («Dimensioni personalizzate», ad esempio 19 × 5,5 cm) e scriva un solo numero di esempio, 0001 (sulla matrice e sulla parte principale, o in un solo punto).\n\nScegliendo quel PDF, il programma vede che c'è un solo biglietto e mostra «{papel}», «{margem}» e «{porfolha}»: riempie il foglio di copie del biglietto, quante ne entrano (ruotandole di 90° se così ne entrano di più), e le numera in ordine. L'anteprima mostra il foglio come verrà stampato.\n\n• La carta (A4, A3, A5, Letter, Legal) e il margine (le stampanti non stampano fino al bordo) si possono cambiare.\n• Se la pagina del PDF è più grande del biglietto, il programma ritaglia la zona disegnata.\n• «{porfolha}» parte dal massimo; può chiederne meno.\n• Se ne entrano molti (più di 24), il programma avvisa: sono piccoli e difficili da ritagliare.\n• Se il suo PDF ha già più biglietti per pagina (0001, 0002, …), tutto funziona come prima.",
    'tut_video': 'Preferisce un video? Apra il menu «{ajuda}» › «{video}».',
    'limpar': 'Cancella tutto',
    'tut_limpar': "Al termine, «{limpar}» (o menu «{ficheiro}» › «{limpar}») azzera tutto — template, cifre, cartella, nome, numeri e anteprima — per iniziare un'altra lotteria.",
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'Scarica',
    'web_senha': 'Password',
    'web_entrar': 'Accedi',
    'web_senha_errada': 'Password errata.',
    'web_demasiado_grande': 'Il file supera il limite ({mb} MB).',
    'web_ocupado': 'È già in corso una generazione. Riprova tra poco.',
    'web_voltar': 'Indietro',
    'web_ficheiros_gerados': 'PDF generati',
    'web_nova_janela': 'Apri in una nuova finestra',
    'web_tema_auto': 'Automatico',
})
T.update({'web_demasiados': 'Al massimo {max} numeri per richiesta.'})
