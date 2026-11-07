T = {
    "m_ficheiro": "Fichier", "m_ver": "Affichage", "m_idioma": "Langue", "m_ajuda": "Aide",
    "mi_abrir_template": "Ouvrir le modèle…", "mi_abrir_alg": "Choisir le fichier des chiffres…",
    "mi_destino": "Choisir le dossier de destination…", "mi_sair": "Quitter",
    "mi_zoom_mais": "Zoom avant", "mi_zoom_menos": "Zoom arrière", "mi_ajustar": "Ajuster à la fenêtre",
    "mi_expandir": "Agrandir l’aperçu", "mi_reduzir": "Réduire l’aperçu",
    "mi_tema": "Thème", "mi_tema_sistema": "Comme Windows", "mi_tema_claro": "Clair", "mi_tema_escuro": "Sombre",
    "mi_tutorial": "Tutoriel pas à pas", "mi_sobre": "À propos…",
    "sobre_texto": ("{app}\nVersion {versao}\n\nCrée des PDF de tickets de tombola numérotés à partir d’un modèle Canva.\n\n"
                    "Utilise les bibliothèques pypdf, pypdfium2, Pillow et CustomTkinter (licences permissives)."),
    "tip_tema": "Basculer entre le thème clair et sombre",
    "tut_titulo": "Tutoriel", "tut_ant": "Précédent", "tut_seg": "Suivant",
    "tut_t0": "Vue d’ensemble",
    "tut_b0": ("Ce programme prend votre tombola dessinée dans Canva et crée des PDF prêts à imprimer avec les "
               "numéros que vous voulez.\n\n"
               "Il n’y a que 4 étapes, dans l’ordre affiché à gauche :\n\n"
               "• 1 – choisissez le modèle (le PDF de Canva) ;\n"
               "• 2 – choisissez le fichier avec les chiffres de 0 à 9 ;\n"
               "• 3 – indiquez de quel numéro à quel numéro, et si vous voulez plusieurs PDF ou un seul ;\n"
               "• 4 – choisissez le dossier et saisissez le nom des fichiers.\n\n"
               "Cliquez ensuite sur « {previa} » pour voir une page, puis sur « {gerar} ». "
               "À la fin, chaque PDF est vérifié automatiquement."),
    "tut_b1": ("Dans Canva, dessinez la tombola et écrivez sur chaque ticket les numéros d’exemple 0001, 0002, "
               "0003, … (un par ticket). Chaque numéro apparaît 2 fois : une sur le talon et une sur la partie "
               "principale du ticket (voir l’image).\n\n"
               "Téléchargez en PDF et choisissez ce fichier à l’étape 1.\n\n"
               "• Le programme détecte seul le nombre de tickets par page et l’orientation du texte du talon.\n"
               "• Les numéros doivent être du texte, pas une image.\n"
               "• Les autres numéros du dessin (année, téléphone…) restent tels quels.\n"
               "• Seule la 1re page du PDF est utilisée."),
    "tut_b3": ("• {de} / {ate} : le premier et le dernier numéro à générer (par exemple de 1 à 1000).\n"
               "• {algarismos} : avec combien de chiffres écrire (4 → 0001). Par défaut, celui du modèle ; "
               "si vous en demandez plus, la taille des numéros diminue pour qu’ils tiennent.\n"
               "• {varios} : découpe en fichiers avec au plus le nombre de numéros indiqué (multiple des tickets "
               "par page).\n"
               "• {unico} : tout dans un seul fichier.\n\n"
               "En dessous, le résumé : combien de numéros, de fichiers et de pages seront créés."),
    "tut_b4": ("Choisissez le dossier où enregistrer les PDF et saisissez le nom des fichiers (obligatoire ; le "
               "programme n’en propose jamais). Les fichiers s’appellent « NOM - 0001 - 0300.pdf », "
               "« NOM - 0301 - 0600.pdf », … ou seulement « NOM - 0001 - 1000.pdf » avec un seul PDF.\n\n"
               "Si des fichiers portent déjà ces noms, le programme demande avant de les remplacer."),
    "tut_t5": "Aperçu et génération",
    "tut_b5": ("« {previa} » montre la 1re page avec de vrais numéros, pour vérifier la police, la taille et la "
               "position avant de tout générer.\n\n"
               "Dans la visionneuse :\n"
               "• − / + ou Ctrl + molette : zoom ;\n"
               "• faites glisser pour déplacer ; double-clic ou « {ajustar} » : voir la feuille entière ;\n"
               "• le bouton d’agrandissement donne toute la fenêtre à l’aperçu ; recliquez pour revenir ;\n"
               "• la séparation entre les réglages et la visionneuse se déplace aussi.\n\n"
               "Cliquez sur « {gerar} ». La barre montre la progression (vous pouvez annuler). À la fin, chaque PDF "
               "est vérifié automatiquement (pages et numéros) et le bouton « {pasta} » apparaît."),
    "tut_t6": "Conseils et problèmes",
    "tut_b6": ("• « Je n’ai pas trouvé les numéros d’exemple » : dans Canva, les numéros doivent être du texte, au "
               "format 0001, 0002, … (chacun 2 fois).\n"
               "• Les numéros sortent dans une autre police : le fichier des chiffres doit utiliser exactement la "
               "même police que le modèle. Vérifiez dans l’aperçu.\n"
               "• Numéros trop petits ou bizarres : avec PNG/JPG, utilisez une grande image (≥ 100 px de haut) ; le PDF est toujours meilleur.\n"
               "• « Impossible d’enregistrer » : fermez le PDF s’il est ouvert dans un autre programme.\n"
               "• Plus de chiffres que le dessin : la taille diminue automatiquement (avertissement dans le journal).\n"
               "• Vous pouvez changer la langue et le thème (clair/sombre) dans les menus ; les couleurs suivent Windows."),
    'err_folha_varias': 'Seul un template avec un seul billet peut être répété sur la feuille.',
    'err_rifa_grande': 'Le billet ({w} × {h} mm) ne tient pas sur une feuille {papel} avec des marges de {margem} mm.\n\nChoisissez un papier plus grand, réduisez la marge ou dessinez un billet plus petit.',
    'log_folha': 'Feuille {papel} : {n} billets par feuille ({w} × {h} mm chacun).',
    'aviso_muitas': '⚠ {n} billets par feuille : ils seront très petits et difficiles à découper. Vérifiez la taille du billet.',
    'c1_ok_uma': "✔ Template avec 1 billet · numéro d'exemple {primeiro}",
    'lay_info': 'Le template contient un seul billet : le programme remplit la feuille de copies, autant que possible.',
    'lay_papel': 'Papier',
    'lay_margem': 'Marge (mm)',
    'lay_por_folha': 'Billets par feuille',
    'lay_resultado': 'Billet de {w} × {h} mm → {n} par feuille {papel} (maximum {max})',
    'lay_recortada': ' · rogné au dessin',
    'lay_rodadas': ' · {r} pivotés de 90°',
    'lay_acima': 'Seuls {max} tiennent sur une feuille.',
    'conf_muitas': "Vous allez générer {n} billets par feuille ({w} × {h} mm chacun). C'est beaucoup : ils seront petits et difficiles à découper.\n\nContinuer ?",
    'mi_video': 'Tutoriel vidéo',
    'video_falta': "Je n'ai pas trouvé la vidéo ({nome}).",
    'tut_t_uma': 'Un seul billet dans le template',
    'tut_b_uma': "Pas besoin de dessiner toute la feuille. Dans Canva, créez une page de la taille d'un billet (« Taille personnalisée », par exemple 19 × 5,5 cm) et écrivez un seul numéro d'exemple, 0001 (sur le talon et sur la partie principale, ou à un seul endroit).\n\nEn choisissant ce PDF, le programme voit qu'il n'y a qu'un billet et affiche « {papel} », « {margem} » et « {porfolha} » : il remplit la feuille de copies du billet, autant que possible (en les pivotant de 90° si cela en fait tenir plus), et les numérote dans l'ordre. L'aperçu montre la feuille telle qu'elle sera imprimée.\n\n• Le papier (A4, A3, A5, Letter, Legal) et la marge (les imprimantes n'impriment pas jusqu'au bord) sont modifiables.\n• Si la page du PDF est plus grande que le billet, le programme rogne la zone dessinée.\n• « {porfolha} » commence au maximum ; vous pouvez en demander moins.\n• Si beaucoup de billets tiennent (plus de 24), le programme vous prévient : ils sont petits et difficiles à découper.\n• Si votre PDF contient déjà plusieurs billets par page (0001, 0002, …), tout fonctionne comme avant.",
    'tut_video': 'Vous préférez une vidéo ? Ouvrez le menu « {ajuda} » › « {video} ».',
    'limpar': 'Tout effacer',
    'tut_limpar': "Quand c'est terminé, « {limpar} » (ou menu « {ficheiro} » › « {limpar} ») remet tout à zéro — template, chiffres, dossier, nom, numéros et aperçu — pour commencer une autre tombola.",
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'Télécharger',
    'web_demasiado_grande': 'Le fichier dépasse la limite ({mb} Mo).',
    'web_ocupado': 'Une génération est déjà en cours. Réessayez dans un instant.',
    'web_voltar': 'Retour',
    'web_ficheiros_gerados': 'PDF générés',
    'web_nova_janela': 'Ouvrir dans une nouvelle fenêtre',
    'web_tema_auto': 'Automatique',
    'web_sessao_expirada': 'La session a expiré (ou le serveur a redémarré). Chargez de nouveau vos fichiers.',
    'web_erro_rede': 'Impossible de joindre le serveur. Vérifiez votre connexion et réessayez.',
    'web_visual': 'Style',
})
T.update({'web_demasiados': 'Au maximum {max} numéros par demande.'})
