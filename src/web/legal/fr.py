"""Conditions, confidentialité et contact en français : traduction de `pt.py` (mêmes pages, sections, paragraphes et {marqueurs}). Sans relecture native ; le portugais prévaut."""
FRASES = {
    "responsavel_com": "Le service est géré par {nome}.",
    "responsavel_sem": "Le service est géré par son auteur, la personne qui le met en ligne.",
    "contacto_com": "Vous pouvez nous contacter à {email}.",
    "contacto_sem": "Il n'y a pas de contact public pour le moment.",
    "contacto_pagina_com": "Pour toute question, erreur ou suggestion, écrivez à {email}.",
    "contacto_pagina_sem": "Il n'y a pas de contact public pour le moment. Revenez sur cette page plus tard.",
    "atualizado": "8 novembre 2026",
}

AVISO = ("Version provisoire, à revoir avec un appui juridique. Si quelque chose ici diffère de ce que fait le service, demandez-nous de le corriger. "
         "Il s'agit d'une traduction sans relecture native : en cas de différence, la version portugaise prévaut.")

TEXTOS = {
    "termos": {
        "titulo": "Conditions d'utilisation",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Ce qu'est ce service",
             "paragrafos": ["Le Générateur de tombolas crée, à partir d'un modèle PDF, les billets numérotés d'une tombola, prêts à imprimer. Il ne fait que cela : il ne vend pas de billets, "
                            "ne reçoit pas d'argent, ne conserve pas de listes de participants et ne fait pas de tirages ayant une valeur légale.",
                            "{responsavel}"]},
            {"titulo": "L'organisateur de la tombola en est responsable",
             "paragrafos": ["Les tombolas, loteries et tirages sont soumis à des règles légales (par exemple des autorisations de la mairie et des règles pour les associations) qui varient "
                            "selon les cas. L'organisateur est seul responsable du respect de la loi, de l'encaissement et de la remise des lots. Ce service ne donne pas de conseil juridique."]},
            {"titulo": "Usage autorisé",
             "paragrafos": ["Le service est gratuit et pour un usage raisonnable. Il ne peut pas servir à produire des billets pour des fraudes ni à surcharger le serveur : il y a des limites "
                            "de taille des fichiers, de numéros par demande ({max_numeros}) et de demandes par minute, et une génération à la fois."]},
            {"titulo": "Vos fichiers",
             "paragrafos": ["Le modèle et les chiffres ne servent qu'à générer vos billets et sont effacés du serveur après {validade} minutes d'inactivité, ou quand vous cliquez sur « Tout effacer ». "
                            "Nous ne les utilisons pour rien d'autre. Ils restent à vous : il suffit d'avoir le droit d'utiliser ce que vous envoyez (images, polices, logos)."]},
            {"titulo": "Sans garantie",
             "paragrafos": ["Le service est fourni « tel quel », sans garantie d'être toujours disponible ni exempt d'erreurs. Vérifiez toujours les PDF avant d'imprimer (le service vérifie "
                            "les numéros générés, mais le contrôle final vous revient). Dans la mesure permise par la loi, nous ne répondons pas des pertes liées à l'usage du service."]},
            {"titulo": "Modifications",
             "paragrafos": ["Ces conditions peuvent changer ; la date de la dernière mise à jour est le {atualizado}. Si le service devient un jour payant, ce sera dit clairement avant de facturer."]},
            {"titulo": "Contact", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Politique de confidentialité",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Résumé",
             "paragrafos": ["Il n'y a ni comptes, ni publicités, ni outils de suivi tiers. Vos fichiers sont effacés du serveur en {validade} minutes. "
                            "Les statistiques d'utilisation ne sont que des chiffres agrégés."]},
            {"titulo": "Quelles données nous traitons",
             "paragrafos": ["Les fichiers que vous envoyez (modèle et chiffres) ne sont traités que pour générer les billets, restent dans un dossier temporaire du serveur et sont effacés après "
                            "{validade} minutes d'inactivité ou quand vous cliquez sur « Tout effacer ».",
                            "Pour savoir comment le service est utilisé, nous enregistrons des comptages : combien de visites, générations et téléchargements, la langue et le thème choisis et le type d'écran. "
                            "Nous n'enregistrons jamais d'adresses IP, de noms de fichiers, le contenu des fichiers ni l'identification complète du navigateur.",
                            "L'adresse IP n'est utilisée qu'en mémoire, quelques instants, pour limiter le nombre de demandes par minute, et n'est pas conservée par nous. L'hébergeur "
                            "(Render, à Francfort, dans l'Union européenne) peut enregistrer des adresses IP dans ses journaux techniques."]},
            {"titulo": "Dans votre navigateur",
             "paragrafos": ["Nous conservons dans votre navigateur (stockage local) vos préférences : la langue, le thème visuel, le mode clair ou sombre et les dernières valeurs du formulaire. "
                            "Pour ne pas refaire le travail d'une année à l'autre, le fichier des chiffres peut aussi être gardé dans votre navigateur (jamais sur notre serveur) ; « Tout effacer » le supprime. "
                            "Nous n'utilisons aucun cookie publicitaire ni de suivi."]},
            {"titulo": "Base légale et conservation",
             "paragrafos": ["Nous traitons ces données au titre de l'intérêt légitime de fournir le service et de le sécuriser (RGPD, article 6, paragraphe 1, point f). Les fichiers durent quelques minutes ; "
                            "les comptages agrégés n'identifient personne."]},
            {"titulo": "Vos droits",
             "paragrafos": ["Vous avez un droit d'accès, de rectification, d'effacement et d'opposition, et le droit d'introduire une réclamation auprès de votre autorité de protection des données (au Portugal, la CNPD, cnpd.pt). "
                            "Comme nous ne conservons aucune donnée qui vous identifie, il y a en pratique peu à consulter ou à effacer ; en cas de doute, contactez-nous."]},
            {"titulo": "Qui répond", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Mise à jour", "paragrafos": ["Dernière mise à jour : {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Contact",
        "aviso": "",
        "seccoes": [
            {"titulo": "Écrivez-nous",
             "paragrafos": ["{contacto_pagina}",
                            "Si vous trouvez une erreur, dites-nous ce que vous avez fait et ce que vous attendiez ; n'envoyez pas votre modèle s'il contient des données personnelles."]},
        ],
    },
}
