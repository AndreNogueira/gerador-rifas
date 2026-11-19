"""Condicions, privadesa i contacte en català: traducció de `pt.py` (mateixes pàgines, seccions, paràgrafs i {marcadors}). Sense revisió nativa; preval el portuguès."""
FRASES = {
    "responsavel_com": "El servei el gestiona {nome}.",
    "responsavel_sem": "El servei el gestiona el seu autor, la persona que el posa en línia.",
    "contacto_com": "Podeu contactar-nos a {email}.",
    "contacto_sem": "De moment no hi ha cap contacte públic.",
    "contacto_pagina_com": "Per a dubtes, errors o suggeriments, escriviu a {email}.",
    "contacto_pagina_sem": "De moment no hi ha cap contacte públic. Torneu a visitar aquesta pàgina més endavant.",
    "atualizado": "8 de novembre de 2026",
}

AVISO = ("Versió provisional, pendent de revisar amb suport jurídic. Si alguna cosa d'aquí difereix del que fa el servei, demaneu-nos que ho corregim. "
         "Aquesta és una traducció sense revisió nativa: si les versions difereixen, preval la portuguesa.")

TEXTOS = {
    "termos": {
        "titulo": "Condicions d'ús",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Què és aquest servei",
             "paragrafos": ["El Generador de Rifes crea, a partir d'una plantilla en PDF, butlletes de rifa numerades llestes per imprimir. Fa només això: no ven butlletes, "
                            "no rep diners, no guarda llistes de participants ni fa sortejos amb valor legal.",
                            "{responsavel}"]},
            {"titulo": "Qui organitza la rifa n'és responsable",
             "paragrafos": ["Les rifes, les tómboles i els sortejos estan subjectes a normes legals (per exemple, llicències de l'ajuntament i regles per a associacions) que varien "
                            "segons el cas. Qui organitza la rifa és l'únic responsable de complir la llei, de cobrar els pagaments i de lliurar els premis. "
                            "Aquest servei no dona assessorament jurídic."]},
            {"titulo": "Ús permès",
             "paragrafos": ["El servei és gratuït i per a un ús raonable. No es pot fer servir per produir butlletes per a estafes ni per sobrecarregar el servidor: hi ha límits a la mida dels fitxers, "
                            "als números per sol·licitud ({max_numeros}) i a les sol·licituds per minut, i només es fa una generació alhora."]},
            {"titulo": "Els vostres fitxers",
             "paragrafos": ["La plantilla i les xifres només es fan servir per generar les butlletes i s'esborren del servidor passats {validade} minuts sense activitat, "
                            "o quan premeu «Neteja-ho tot». No les fem servir per a res més. Continuen sent vostres: només us cal tenir dret a fer servir el que pugeu "
                            "(imatges, lletres, logotips)."]},
            {"titulo": "Sense garanties",
             "paragrafos": ["El servei s'ofereix «tal com és», sense garantia que sempre estigui disponible ni lliure d'errors. Reviseu sempre els PDF abans d'imprimir (el servei "
                            "verifica els números generats, però la revisió final és vostra). En la mesura que la llei ho permeti, no ens fem responsables de pèrdues lligades a l'ús del servei."]},
            {"titulo": "Canvis",
             "paragrafos": ["Aquestes condicions poden canviar; la data de l'última actualització és {atualizado}. Si algun dia el servei passa a ser de pagament, s'indicarà amb claredat abans de cobrar."]},
            {"titulo": "Contacte", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Política de privadesa",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Resum",
             "paragrafos": ["No hi ha comptes, ni anuncis, ni eines de seguiment de tercers. Els vostres fitxers s'esborren del servidor en {validade} minuts. "
                            "Les estadístiques d'ús són només xifres agregades."]},
            {"titulo": "Quines dades tractem",
             "paragrafos": ["Els fitxers que pugeu (plantilla i xifres) només es tracten per generar les butlletes, es queden en una carpeta temporal del servidor i s'esborren "
                            "passats {validade} minuts sense activitat o quan premeu «Neteja-ho tot».",
                            "Per saber com es fa servir el servei, enregistrem recomptes: quantes visites, generacions i baixades, la llengua i el tema triats i el tipus de pantalla. "
                            "També enregistrem el país de la visita (només el codi, per exemple «PT»), que la xarxa de l'allotjament dedueix de l'adreça IP; la IP en si no la guardem. Mai no enregistrem adreces IP, noms de fitxers, continguts dels fitxers ni la identificació completa del navegador.",
                            "L'adreça IP només es fa servir a la memòria, durant uns instants, per limitar el nombre de sol·licituds per minut, i no la desem. L'empresa d'allotjament "
                            "(Render, a Frankfurt, a la Unió Europea) pot registrar adreces IP als seus registres tècnics."]},
            {"titulo": "Al vostre navegador",
             "paragrafos": ["Desem les vostres preferències al navegador (emmagatzematge local): la llengua, el tema visual, el mode clar o fosc i els últims valors del formulari. Perquè no "
                            "hàgiu de repetir la feina d'un any a l'altre, el fitxer de xifres també es pot conservar al navegador (mai al nostre servidor); «Neteja-ho tot» l'esborra. "
                            "No fem servir galetes de publicitat ni de seguiment."]},
            {"titulo": "Base jurídica i conservació",
             "paragrafos": ["Tractem aquestes dades sobre la base del nostre interès legítim a oferir el servei i mantenir-lo segur (RGPD, article 6.1.f). "
                            "Els fitxers duren minuts; els recomptes agregats no identifiquen ningú."]},
            {"titulo": "Els vostres drets",
             "paragrafos": ["Teniu dret d'accés, rectificació, supressió i oposició, i a presentar una reclamació davant de la vostra autoritat de protecció de dades (a Portugal, la "
                            "CNPD, cnpd.pt). Com que no conservem dades que us identifiquin, a la pràctica hi ha poc per consultar o esborrar; en cas de dubte, parleu amb nosaltres."]},
            {"titulo": "Qui n'és el responsable", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Actualització", "paragrafos": ["Última actualització: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Contacte",
        "aviso": "",
        "seccoes": [
            {"titulo": "Poseu-vos en contacte",
             "paragrafos": ["{contacto_pagina}",
                            "Si trobeu un error, expliqueu-nos què heu fet i què esperàveu; no ens envieu la plantilla si conté dades personals."]},
        ],
    },
}

ANUNCIOS = {
    "resumo": "No hi ha comptes. El lloc mostra anuncis de Google (AdSense), que poden fer servir galetes; a part d'això, no fem servir eines de seguiment de tercers.",
    "cookies": "Les úniques galetes de publicitat són les dels anuncis (vegeu «Publicitat»).",
    "seccao": {
        "titulo": "Publicitat",
        "paragrafos": [
            "Aquest lloc mostra anuncis de Google (AdSense) per finançar-se. Google i els seus socis poden fer servir galetes i identificadors per mostrar anuncis, personalitzats o no, i mesurar-ne els resultats; nosaltres no rebem aquestes dades ni les vinculem a cap fitxer vostre.",
            "Els anuncis només apareixen després que trieu al missatge de consentiment que Google mostra en obrir el lloc (obligatori a l'Espai Econòmic Europeu i al Regne Unit); la base jurídica de les galetes de publicitat és el vostre consentiment (RGPD, article 6.1.a), i podeu revisar l'elecció a les opcions de privadesa d'aquest missatge. Els anuncis no apareixen mai als fitxers generats, al tauler d'administració ni a l'aplicació per a Windows.",
            "Consulteu com Google fa servir les dades a policies.google.com/technologies/partner-sites i gestioneu els anuncis personalitzats a adssettings.google.com.",
        ],
    },
}

PARTILHAS = {"titulo": "Dissenys compartits", "paragrafos": [
    "Si premeu «Comparteix per enllaç» a l'Editor de plantilles, el disseny (formes, textos i colors, sense imatges) es guarda al nostre servidor, amb una adreça difícil d'endevinar, durant 90 dies des de l'últim accés, i qualsevol persona amb l'enllaç el pot obrir. No desem la vostra adreça IP ni altres dades de qui comparteix: no escriviu dades personals ni secrets al disseny. Un disseny que no compartiu només s'envia al servidor per crear la plantilla i s'esborra amb la sessió."]}

OPINIAO = {"titulo": "Comentaris i problemes comunicats", "paragrafos": [
    "Si deixeu un comentari a la pàgina «Comentaris», desem el text, la data, el país des d'on s'envia (per exemple PT, indicat per la xarxa d'allotjament; no desem l'adreça IP) i el nom que trieu mostrar (cap, si preferiu romandre anònim/a; si demaneu mostrar un nom i no l'escriviu, apareix «Visitant núm. …»). El text i el nom són visibles per a tothom; el país només el veu el responsable del lloc. Per frenar abusos el servidor compta en memòria, durant una hora, quants comentaris arriben de cada adreça, sense desar-los. No escriviu dades personals al comentari; si voleu que s'esborri, escriviu-nos (vegeu Contacte).",
    "Si informeu d'un problema, el text que escriviu (i, si marqueu aquesta opció, la versió de l'aplicació, l'idioma, el navegador i la pantalla) s'envia al GitHub del projecte, on queda registrat i visible per a l'equip. La vostra adreça IP no s'envia. No escriviu dades personals ni contrasenyes.",
]}
