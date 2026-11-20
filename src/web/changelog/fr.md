# Changelog (résumé en français)

Résumé traduit de `../CHANGELOG.md` : mêmes versions, sections et points, plus courts. Le texte complet est en portugais.

## 3.71.0 — 2026-11-20

### Nouveautés
- **Bons de jetons numérotés** (dans la liste de prix, avec une monnaie inventée ; et «Extras → Liste de prix… → Bons numérotés…» dans l'appli Windows) : choisissez combien de jetons vaut chaque bon, le titre et une note, voyez le bon au modèle de la liste et créez-les. On continue dans le générateur de tombolas, qui numérote les bons avec séries, QR de vérification et feuilles prêtes à imprimer.

## 3.70.0 — 2026-11-20

### Nouveautés
- **Générateur de listes de prix pour fêtes** (`/precario`, et «Extras → Liste de prix…» dans l'appli Windows) : choisissez l'occasion (celle de la période est suggérée) et les articles d'un catalogue illustré, saisissez les prix dans la monnaie de votre pays ou dans une monnaie inventée (jetons…) et téléchargez le PDF (ou une image) prêt à imprimer, en A5, A4 ou A3 et avec les 24 modèles de la galerie. Il y a aussi un nouveau guide : «Comment faire la liste de prix d'une fête».

## 3.69.0 — 2026-11-19

### Nouveautés
- **Portugais du Brésil** (`/pt-br`) : le site, les guides et les pages légales existent aussi en portugais du Brésil, avec son vocabulaire, une Politique de confidentialité adaptée à la LGPD brésilienne et la langue choisie toute seule quand le navigateur est en pt-BR. Le portugais du Portugal reste le même, sans préfixe dans l'adresse.

## 3.68.0 — 2026-11-19

### Nouveautés
- **Trois nouveaux guides, par thème** (et non par public) : comment numéroter les billets d'une tombola, comment faire un tirage vérifiable (il renvoie à la page «Tirage») et combien de billets faire et à quel prix. Ils sont dans «Tous les guides» (`/como-fazer`), en 22 langues.

## 3.67.0 — 2026-11-19

### Nouveautés
- **Index des guides «Comment faire»** (`/como-fazer`) : une page qui liste tous les guides avec un résumé, et chaque guide se termine par des liens vers les autres. Aussi dans le menu «Aide» («Tous les guides»).
- Les guides et l'index indiquent à Google leur chemin (Accueil › Comment faire › guide) pour l'afficher dans les résultats.

## 3.66.0 — 2026-11-19

### Nouveautés
- **Invitation à laisser un commentaire :** après le téléchargement de vos tombolas, un avis discret apparaît (une seule fois par appareil) pour vous inviter à laisser un commentaire, anonyme si vous le souhaitez. Vous pouvez le fermer avec « Pas maintenant ».

## 3.65.0 — 2026-11-19

### Amélioré
- **Un site plus léger et plus sûr :** si vous ne faites que générer des tombolas, vous téléchargez 24 % de code en moins (le panneau d'administration, l'éditeur de modèles et le tirage ne se chargent qu'à l'ouverture de la page). Le site envoie aussi désormais des en-têtes de sécurité et répond aux vérificateurs de liens et aux aperçus de partage.

## 3.64.0 — 2026-11-19

### Nouveautés
- **Sauvegarde hebdomadaire des données du panneau d'administration :** chaque lundi le service enregistre, dans le stockage du même fournisseur que la base de données, une copie de l'historique, des objectifs, du journal des actions, des commentaires et des textes SEO (8 dernières semaines), avec un script pour la restaurer.

## 3.63.0 — 2026-11-19

### Nouveautés
- **Performances réelles du site dans les statistiques :** le panneau d'administration montre, par jour, le temps d'affichage de la page, le mouvement du contenu et le temps de réponse à un clic, mesurés dans les navigateurs des visiteurs (mobile et ordinateur). Seulement trois nombres anonymes par visite ; la Politique de confidentialité a été mise à jour.

## 3.62.0 — 2026-11-19

### Nouveautés
- **Origine des visites dans les statistiques :** le panneau d'administration montre désormais d'où viennent les visites, en catégories générales (recherche, réseaux sociaux, e-mail, autres sites ou directes) et par campagne (utm_source), pour mesurer une diffusion. L'adresse de la page d'origine et l'IP ne sont jamais conservées ; la Politique de confidentialité a été mise à jour.

## 3.61.0 — 2026-11-19

### Nouveautés
- **Journal des actions dans le panneau d'administration :** qui a fait quoi et quand dans le panneau est conservé 400 jours (connexions, commentaires supprimés ou masqués, clés d'API, textes SEO, objectifs), sans données de visiteurs ni mots de passe.

## 3.60.0 — 2026-11-19

### Nouveautés
- **Objectifs quotidiens dans le panneau d'administration :** le responsable fixe une cible par jour (sessions, générations, numéros générés, téléchargements…) et voit si le dernier jour l'a atteinte, la moyenne des 7 derniers jours et sur combien elle l'a été ; le rapport quotidien par e-mail contient la même section.

## 3.59.0 — 2026-11-19

### Nouveautés
- **Commentaires avec statut dans le panneau d'administration :** le responsable peut marquer chaque commentaire comme lu, favori ou masqué (un commentaire masqué disparaît de la page publique mais n'est pas perdu), filtrer par statut et voir combien restent à lire.

## 3.58.0 — 2026-11-19

### Nouveautés
- **Quotas de l'hébergement gratuit dans le panneau d'administration :** on voit combien des 750 heures mensuelles de Render le service a consommées (avec la projection jusqu'à la fin du mois) et l'espace occupé par la base de données sur le plan gratuit de Neon, avec un avertissement dans le rapport quotidien par e-mail avant épuisement.

## 3.57.0 — 2026-11-19

### Nouveautés
- **Repères de version sur les graphiques du panneau d'administration :** chaque graphique quotidien signale le jour où une nouvelle version de l'application est arrivée (et le rapport quotidien dit laquelle), pour relier une hausse d'erreurs ou de temps de réponse à la mise à jour qui l'a causée.

## 3.56.0 — 2026-11-19

### Nouveautés
- **Résumé hebdomadaire et mensuel par e-mail pour le responsable du site :** le lundi arrive le résumé de la semaine et le 1er celui du mois, avec les totaux comparés à la période précédente et une miniature de chaque jour. Ils lisent l'historique permanent. Uniquement des comptages.

## 3.55.0 — 2026-11-19

### Nouveautés
- **Alertes immédiates par e-mail pour le responsable du site :** en cas de série d'erreurs serveur, de redémarrages du moteur, de mémoire proche de la limite ou de base de données muette, un avertissement arrive aussitôt (sans attendre le rapport quotidien et sans se répéter pendant 6 heures). Uniquement des comptages.

## 3.54.0 — 2026-11-19

### Nouveautés
- **Historique permanent dans le panneau d'administration :** un résumé de chaque jour est enregistré après minuit, l'évolution quotidienne montre donc des mois et jusqu'à 2 ans (avant, seulement 90 jours). Uniquement des comptages, comme le reste du panneau.

## 3.53.0 — 2026-11-19

### Nouveautés
- **Rapport quotidien par e-mail pour le responsable du site :** chaque jour, juste après minuit, un e-mail arrive avec tout ce qui a été enregistré pendant la journée qui vient de se terminer (utilisation, public, erreurs et ressources du serveur), comparé à la moyenne des 7 jours précédents, pour suivre l'application sans ouvrir le panneau. Uniquement des comptages : jamais de données des visiteurs.

## 3.52.0 — 2026-11-19

### Amélioré
- **Commentaires sans adresse IP :** à la place de l'IP, seul le pays d'où le commentaire a été envoyé est conservé (seul le responsable du site le voit). L'adresse IP n'est plus conservée : celles des commentaires précédents ont été supprimées et la Politique de confidentialité a été mise à jour.

## 3.51.0 — 2026-11-19

### Nouveautés
- **Commentaires :** une page « Commentaires » où chacun voit ce que les autres pensent du générateur, et une page pour laisser le sien : vous pouvez rester anonyme ou afficher un nom (sans nom, « Visiteur n° … » apparaît). L'adresse IP n'est conservée que pour le responsable du site, pour limiter les abus, n'est jamais affichée et est supprimée au bout de 90 jours.
- **Signaler un problème :** nouvelle page où vous décrivez un bug et, en cliquant sur « Ouvrir », il est créé directement sur le GitHub du projet, sans compte (votre IP n'est pas envoyée et les informations techniques du navigateur ne partent que si vous les ajoutez).
- Les deux pages et les boutons « Commentaires » et « Signaler un problème » sont bien visibles dans l'en-tête, le menu et le pied de page ; la Politique de confidentialité (22 langues) explique ce qui est conservé.

## 3.50.0 — 2026-11-18

### Amélioré
- **Un en-tête qui s'adapte à l'écran :** toutes les options sont alignées à droite, sur une seule ligne et sans trous, et à mesure que l'écran rétrécit elles passent une à une dans un menu « hamburger » (d'abord le mode clair/sombre et le style, le don en dernier). Sur téléphone, il ne reste que le nom de l'application et le bouton du menu, qui s'ouvre avec les pages, l'aide, le partage et les réglages.

## 3.49.0 — 2026-11-18

### Nouveautés
- **Tableau de bord avec l'évolution jour par jour :** une nouvelle vue « Évolution quotidienne » montre, sur jusqu'à 90 jours, tout ce que le serveur enregistre en base (sessions, générations, numéros générés, langues, pays, styles, galerie, éditeur, API, requêtes, temps de réponse, CPU et mémoire…), avec la tendance de chaque indicateur et le téléchargement de l'ensemble en CSV. C'est une fonction du tableau de bord du propriétaire : les visiteurs ne voient aucune différence.

## 3.48.0 — 2026-11-18

### Amélioré
- **Menu « Aide » dans l'en-tête :** le tutoriel, la vidéo et les guides « Comment faire » sont regroupés dans un seul onglet, « Aide ». L'en-tête est plus court et le nom de l'application s'affiche toujours en entier sur une seule ligne, dans toutes les langues et tailles d'écran.

## 3.47.0 — 2026-11-15

### Amélioré
- **Galerie de modèles :** la liste des dessins n'est plus coupée ni mal placée dans certains thèmes ; chaque lot a son numéro ; chaque zone de texte affiche sa limite de caractères (par exemple 12/50) ; et le bouton « Utiliser ce modèle » n'est plus collé à la dernière zone.
- **Date du tirage dans un calendrier à part :** au lieu du champ du navigateur (qui affichait « jj/mm/aaaa » et un sélecteur dans une autre langue que celle du site), il y a un calendrier dans les 22 langues, avec les mois et les jours de la semaine dans la langue choisie, la date écrite comme cette langue l'écrit, le bon premier jour de la semaine et les boutons « Aujourd'hui » et « Effacer ». Il fonctionne au clavier (flèches, Page préc./suiv., Début/Fin, Entrée et Échap).
- **Un « À propos » plus complet :** le texte a été réécrit, dans les 22 langues, et explique à qui s'adresse le générateur, ce qu'il fait, quoi faire après l'impression, comment il protège la vie privée et où l'utiliser.

## 3.46.0 — 2026-11-15

### Amélioré
- **Don plus visible :** quand le service a un lien de don, le bouton apparaît maintenant dans l'en-tête (à côté de « Partager ») et, après la génération des fichiers, avec une courte invitation. Il reste aussi dans le pied de page.

## 3.45.0 — 2026-11-14

### Amélioré
- **Galerie de modèles sur une seule ligne :** les 24 dessins se choisissent maintenant dans une zone d'une ligne où chaque option montre une miniature du modèle, au lieu d'une longue liste de boutons. Elle fonctionne à la souris, au toucher et au clavier (flèches, Début/Fin, une lettre, Entrée et Échap).

## 3.44.0 — 2026-11-14

### Amélioré
- **Confidentialité :** les comptages d'utilisation incluent désormais le pays de la visite (seulement le code, déduit par le réseau de l'hébergeur ; l'adresse IP n'est toujours pas conservée). La Politique de confidentialité l'explique dans les 22 langues.

## 3.43.1 — 2026-11-14

### Amélioré
- **Pied de page plus propre :** les guides « Comment faire » n'apparaissent plus que dans le groupe de l'en-tête ; ils ne se répètent plus en bas de page.

## 3.43.0 — 2026-11-14

### Amélioré
- **Date du tirage dans un calendrier :** dans la galerie de modèles, vous choisissez la date dans un calendrier puis la façon dont elle apparaît sur le billet (31/12/2026, 31 déc. 2026, 31 décembre 2026 ou avec le jour de la semaine), écrite dans la langue du site. On peut toujours la saisir à la main, désormais jusqu'à 60 caractères.
- **Textes plus larges :** les pages de texte (guides, tutoriel, conditions…) occupent maintenant toute la largeur de la page, avec moins de lignes et de paragraphes.

## 3.42.0 — 2026-11-14

### Amélioré
- **En-tête :** le nouveau groupe « Comment faire », à côté du tutoriel, réunit les guides (écoles, associations, clubs, pompiers, fêtes de quartier et paroisses). Le bouton « Partager » est passé du pied de page à l'en-tête, mis en avant, et sa liste montre les icônes de WhatsApp, Telegram, Facebook, e-mail et « Copier le lien ».

## 3.41.0 — 2026-11-14

### Amélioré
- **Aperçu automatique :** quand vous changez le modèle, les chiffres, le logo ou tout champ qui modifie la page finale (numéros, chiffres, feuille, séries, couleurs, QR…), l'aperçu avec de vrais numéros se refait tout seul, sans cliquer sur « Aperçu ». En cas de problème, la raison s'affiche près de la visionneuse, sans fenêtre.

## 3.40.0 — 2026-11-14

### Nouveautés
- **De 3 à 10 lots dans la galerie :** dans les 24 dessins de la galerie, vous choisissez combien de lots porte le billet (3 à 10 ; avant, 3 au maximum). À partir de 6, ils passent sur deux colonnes. Aussi dans l'appli Windows.

## 3.39.0 — 2026-11-13

### Nouveautés
- **Appli Windows 2.7 :** la galerie et l'éditeur de modèles acceptent désormais le latin étendu, le vietnamien, le grec, le cyrillique, le chinois, le japonais et le coréen, comme le site depuis la 3.37 (l'hindi, l'arabe et l'hébreu manquent encore). À télécharger depuis la page du Changelog.

## 3.38.0 — 2026-11-13

### Nouveautés
- **Bouton « Partager » :** en bas de page et, après la génération des fichiers, sur la carte de livraison. Il ouvre une courte liste (partage du téléphone ou de l'ordinateur, WhatsApp, Telegram, Facebook, e-mail et « Copier le lien ») pour faire connaître le générateur à d'autres associations, écoles et comités des fêtes. Les liens ne portent que l'adresse du site dans la langue utilisée : aucun suivi, rien n'est conservé. Il a un sujet dans le tutoriel et une vidéo.

## 3.37.0 — 2026-11-13

### Nouveautés
- **Plus de lettres dans la galerie et l'éditeur de modèles :** les textes peuvent désormais utiliser le latin étendu (polonais, tchèque, roumain, turc…), le **vietnamien, le grec, le cyrillique (russe, ukrainien)**, le **chinois, le japonais et le coréen**. L'hindi, l'arabe et l'hébreu manquent encore (ils demandent une technologie d'écriture que le générateur de PDF n'a pas) et affichent un avertissement au lieu d'une image abîmée. Dans les PDF, seul le texte saisi change ; ce qui sortait déjà pareil reste pareil.

## 3.36.0 — 2026-11-13

### Nouveautés
- **Guide « Comment faire » pour les paroisses :** « Pour les paroisses » (lien en bas de page), avec la marche à suivre pour organiser une tombola paroissiale : fêtes patronales, kermesses, travaux, paniers de Noël et catéchisme. Il existe en 22 langues et rappelle de vérifier auprès de la mairie si la tombola exige une autorisation.

## 3.35.0 — 2026-11-13

### Nouveautés
- **Appli Windows 2.6 :** le menu « Extras » gagne « Enregistrer la demande… » et « Ouvrir une demande… » (un fichier .rifas avec les numéros, le nom, les séries, les couleurs et les traits de coupe, sans modèle ni chemins), l'éditeur de modèles peut ajouter des images (PNG ou JPG) et « Affichage → Visuel » passe de 2 aux 14 thèmes du site (les couleurs seulement). Elle apporte aussi ce qui est venu depuis la 2.4 : l'éditeur, les 24 modèles de la galerie et les 22 langues.

## 3.34.0 — 2026-11-13

### Nouveautés
- **Trois nouveaux guides « Comment faire » :** « Pour les clubs », « Pour les pompiers » et « Pour les fêtes de quartier » (liens en bas de page), avec la marche à suivre pour organiser une tombola dans chaque cas. Ils existent en 22 langues et rappellent de vérifier auprès de la mairie si la tombola exige une autorisation.

## 3.33.0 — 2026-11-13

### Nouveautés
- **API publique par lots** (`/api/v1`, avec Swagger sur `/api/v1/docs`) : elle permet à d'autres programmes de générer plusieurs demandes de tickets à partir d'un seul modèle, avec une clé, des quotas quotidiens et des limites. Les utilisateurs du site passent toujours en premier.
- **Quatre nouvelles langues :** catalan, ukrainien, indonésien et vietnamien. Le site et l'appli Windows passent à 22 langues, avec tutoriel, conditions, confidentialité, guides pratiques et captures.
- **Textes pour les moteurs de recherche modifiables par langue :** le propriétaire modifie dans le panneau d'administration les titres, descriptions et guides de chaque langue, stockés en base de données et sans nouveau déploiement.

## 3.32.0 — 2026-11-13

### Nouveautés
- **20 nouveaux modèles dans la galerie (24 au total) :** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Tous dessinés de zéro pour ce projet, avec talon, sur le site et dans l'appli Windows (où la galerie devient une liste déroulante).

## 3.31.0 — 2026-11-13

### Nouveautés
- **Éditeur de modèles v2 :** annuler et rétablir (Ctrl+Z, Ctrl+Y), dupliquer (Ctrl+D), changer l'ordre de superposition, ajouter le logo (PNG ou JPG) et **partager le dessin par lien** : il est conservé 90 jours après le dernier accès, sans images et sans données sur qui partage (il n'apparaît que si le service a une base de données). La politique de confidentialité le dit.
- **Appli Windows 2.5 :** reçoit l'éditeur de modèles (menu Extras) et passe à Python 3.15.

### Amélioré
- Le Changelog a un lien pour télécharger l'appli Windows.

## 3.30.0 — 2026-11-12

### Nouveautés
- **Pages « Comment faire » :** deux guides écrits, « Pour les écoles » et « Pour les associations » (liens en bas de page), avec la marche à suivre pour organiser une tombola : dessiner le billet, une série par classe ou vendeur, imprimer avec des repères de coupe, suivre les ventes et faire un tirage vérifiable. Ils sont dans les 18 langues et rappellent de vérifier auprès de la mairie si la tombola exige une autorisation.

## 3.29.0 — 2026-11-12

### Amélioré
- **Publicités sur les côtés :** quand les publicités sont activées (ce n'est pas le cas pour l'instant), sur les grands écrans elles apparaissent de part et d'autre du contenu, une de chaque côté, fixes et sans déplacer la page ; sur les autres écrans, il y a un seul bloc à la fin de la page. Elles n'apparaissent toujours pas dans l'éditeur, dans les fichiers générés ni dans l'appli Windows.

## 3.28.0 — 2026-11-12

### Nouveautés
- **Publicités Google (préparées, désactivées) :** le site peut afficher un bloc de publicités Google (AdSense) à la fin de la page d'accueil, du tutoriel, de « À propos », du tirage et du changelog. Elles n'apparaissent jamais dans l'éditeur, dans les fichiers générés, dans la vérification des billets, dans le tableau de bord ni dans l'appli Windows, et dans l'Espace économique européen et au Royaume-Uni seulement après votre choix dans le message de consentement de Google. La politique de confidentialité le dit, dans les 18 langues, quand les publicités sont activées ; pour l'instant elles sont désactivées jusqu'à ce que le propriétaire du service les configure.

## 3.27.0 — 2026-11-12

### Nouveautés
- **Éditeur de modèles :** au lieu d'un modèle Canva, dessinez le billet sur le site (page « Éditeur de modèles », liée depuis l'étape 1) : ajoutez des textes, des rectangles, des lignes et le numéro 0001 (une fois, ou deux avec un talon), faites glisser chaque élément à la souris ou avec les flèches, changez couleurs, tailles et fond, puis cliquez sur « Utiliser ce modèle ». L'écran utilise la police Vera, la même que le PDF : ce que vous voyez est ce que vous obtenez ; le brouillon reste dans le navigateur. Les textes ne peuvent pas contenir de suites comme 0123, que le programme confondrait avec le numéro du billet (l'écran et le serveur vous avertissent).

## 3.26.0 — 2026-11-12

### Nouveautés
- **Cinq nouveaux thèmes :** Halloween, Plage, Vieux journal, Terminal vert et Affiche de cirque, chacun en clair et en sombre. Le site compte désormais 14 thèmes ; la structure est la même partout (seuls les couleurs et l'aspect changent).

## 3.25.0 — 2026-11-08

### Nouveautés
- **Une adresse par langue pour les moteurs de recherche :** chaque langue a sa propre adresse (/en, /ja/tutorial…) avec titre, description et texte dans cette langue, et le site indique à Google quelles versions sont équivalentes (hreflang). Le portugais reste en /. La langue choisie apparaît désormais dans la barre d'adresse.

## 3.24.1 — 2026-11-08

### Amélioré
- **Cases à cocher alignées :** « Une couleur par série » et les autres cases se placent à côté de leur texte, et non plus à l'autre bout de la carte.

## 3.24.0 — 2026-11-08

### Amélioré
- **Tutoriel avec des captures du site :** les sujets de base du tutoriel montrent désormais le site lui-même, dans les 18 langues, au lieu de l'appli Windows.

## 3.23.0 — 2026-11-08

### Nouveautés
- **Tutoriel et vidéo pour chaque fonction :** le tutoriel a un sujet par fonction (séries, liste et feuille de suivi, traits de coupe, galerie, votre marque, QR, tirage, enregistrer et partager, installer comme application, thèmes), chacun avec une courte vidéo enregistrée dans l'interface elle-même, en portugais et en anglais.
- **Changelog, Conditions, Confidentialité et Contact en 18 langues :** le texte s'affiche dans la langue choisie. Le Changelog donne un résumé traduit de chaque version (la version complète est en portugais) ; les textes juridiques sont des traductions sans relecture native et, en cas de différence, la version portugaise prévaut.
- **Appli Windows 2.4** avec ce que le site a gagné depuis la 3.10 : menu « Extras » avec séries, préfixes et couleur par série, numéros ignorés, couleur des numéros, logo, traits de coupe, galerie de modèles, tirage vérifiable et export de la liste (CSV) et de la feuille de suivi ; et l'apparence de Noël automatique en décembre. Le QR de vérification et l'installation comme application restent propres au site.

## 3.22.0 — 2026-11-08

### Amélioré
- **Contraste des 9 thèmes mesuré pour de vrai :** un test dans un navigateur mesure le texte contre les pixels réels du fond, en clair et en sombre (WCAG AA), et ce qui échouait a été corrigé.
- Les grands numéros décoratifs des étapes ne sont plus lus par les lecteurs d'écran.

## 3.21.0 — 2026-11-08

### Nouveautés
- **Tirage vérifiable** (page « Tirage ») : tire des numéros dans une plage (avec des numéros à ignorer) pour que chacun puisse le refaire et obtenir le même résultat, grâce à une graine publique. Tout se passe dans le navigateur et « Copier le lien » partage le même tirage.
- La méthode est décrite pas à pas, avec une implémentation de référence qui donne les mêmes numéros que le site.

## 3.20.0 — 2026-11-08

### Nouveautés
- **QR sur chaque billet :** un QR code de vérification dans un coin de chaque billet (modèles d'un seul billet), avec choix du coin et de la taille. Le scanner ouvre une page qui confirme que ce service a émis le code pour ce billet. Il est signé avec une clé que seul le serveur possède ; aucune base de données. Il ne prouve ni le paiement ni un gain.
- Il n'apparaît que si le propriétaire du service configure la clé. Les demandes avec QR sont plafonnées à 10 000 numéros.

## 3.19.0 — 2026-11-08

### Nouveautés
- **Votre marque :** la couleur des numéros (tout modèle ; la couleur de la série l'emporte) et le **logo** de l'association sur chaque billet (PNG ou JPG jusqu'à 2 Mo, modèles d'un seul billet), avec coin et taille (10 à 40 %). Le PNG garde sa transparence.
- Le logo reste seulement dans la session (effacé avec elle et avec « Tout effacer ») et apparaît dans l'aperçu.

## 3.18.0 — 2026-11-08

### Nouveautés
- **Galerie de modèles :** choisissez l'un des quatre dessins (Bosque, Quermesse, Natal et Gala), saisissez titre, organisation, jusqu'à trois lots et date, regardez l'aperçu et cliquez sur « Utiliser ce modèle » : modèle et chiffres sont prêts. Chaque dessin est un billet avec talon.
- Les dessins sont originaux à ce projet, dans la police libre Vera. La police n'a que l'alphabet latin : avec d'autres lettres, un avertissement s'affiche.

## 3.17.0 — 2026-11-08

### Nouveautés
- **Traits de coupe :** une case dans le panneau de la feuille (modèles d'un seul billet) dessine de courts traits dans les marges, dans le prolongement de chaque ligne de coupe. Il faut au moins 3 mm de marge.
- Le **talon** (le numéro deux fois sur chaque billet) fonctionnait déjà : il est maintenant testé et documenté.
- Le **fond perdu** est déjà respecté : si le PDF de Canva a une TrimBox plus petite que la page, le billet est seulement ce qu'elle contient.

## 3.16.0 — 2026-11-08

### Nouveautés
- **Exporter la liste des billets (CSV) :** un fichier pour Excel ou Calc, un billet par ligne (série, numéro et colonnes Nom, Contact et Payé vides), avec préfixes, séries et numéros ignorés.
- **Feuille de suivi des ventes (PDF) :** un tableau A4 à imprimer et remplir à la main (36 billets par page, avec une case « payé »). Dans les langues dont le PDF ne sait pas écrire les lettres, les titres sortent en anglais.
- Rien n'est conservé sur le serveur : la liste vient seulement du formulaire.

## 3.15.0 — 2026-11-08

### Nouveautés
- **Séries et préfixes :** un texte avant les chiffres (A- donne A-0001). Avec plusieurs séries séparées par des virgules, chacune répète la plage et a ses propres PDF. Le préfixe accepte lettres, espace, point, tiret et barre oblique (6 caractères au plus, sans chiffres).
- **Ignorer des numéros :** 13, 100-110 retire ces numéros de la suite (le résumé, les fichiers et la vérification ne comptent que ce qui est imprimé).
- **Une couleur pour chaque série.**
- Tout cela se retrouve aussi dans « Copier le lien » et dans l'aperçu.

## 3.14.0 — 2026-11-08

### Nouveautés
- **Installer comme application (PWA) :** installez le site sur le téléphone ou l'ordinateur ; la coque de l'appli s'ouvre même hors ligne (générer demande toujours le serveur). Un service worker simple ne garde que la page, les fichiers de l'appli et les textes de l'interface, sans jamais toucher à vos fichiers ni aux demandes de génération.

## 3.13.0 — 2026-11-08

### Nouveautés
- **Se souvenir du fichier des chiffres :** qui revient l'année suivante ne le refait pas. Il reste seulement dans votre navigateur (jamais sur le serveur) et sert avec un nouveau modèle ; en choisir un autre le remplace et « Tout effacer » le supprime.
- **Copier le lien :** un bouton qui copie un lien avec les valeurs du formulaire (de, à, mode, maximum par fichier, papier, marge et nom). Qui l'ouvre voit les mêmes valeurs ; les fichiers ne voyagent jamais dans le lien.

## 3.12.0 — 2026-11-08

### Nouveautés
- Pages **Conditions d'utilisation**, **Politique de confidentialité** et **Contact**, avec des liens en pied de page. Ce sont des versions provisoires, à revoir avec un appui juridique avant que le service ne soit payant.
- **Bouton de don** en pied de page : il n'apparaît que si le propriétaire configure le lien. L'e-mail de contact et le nom du responsable viennent aussi de la configuration du serveur, jamais du code.

## 3.11.0 — 2026-11-08

### Nouveautés
- **Entonnoir d'utilisation** dans le panneau d'administration : combien d'événements à chaque étape (session, modèle, chiffres, aperçu, génération, téléchargement) et quelle part de l'étape précédente est arrivée à la suivante. Il montre où les gens abandonnent. Il compte des événements, pas des personnes.

## 3.10.0 — 2026-11-08

### Nouveautés
- Cette page : le **Changelog**, avec tout ce qui change, version par version.
- En **décembre**, le thème visuel automatique est **Noël** (pour qui n'en a jamais choisi). Choisir un autre thème reste mémorisé.

### Amélioré
- Une dépendance de moins sur le serveur (`python-multipart` n'était plus utilisé : les fichiers arrivent en corps brut).

## 3.9.0 — 2026-11-08

### Nouveautés
- Mise en page pensée pour les **grands écrans** (4K, ultra-large) et les **téléphones récents** : en-tête compact et boutons de 44 px.
- L'aperçu montre une image quand le navigateur ne peut pas afficher les PDF dans la page (Chrome sur Android).
- Le panneau d'administration enregistre le **type d'écran** (classe, taille, famille) sans rien conserver de personnel.
- Le service s'appelle lui-même toutes les 10 minutes pour ne pas s'endormir.

## 3.8.0 — 2026-11-08

### Nouveautés
- **Panneau d'administration** (réservé au propriétaire, avec mot de passe) avec graphiques et explications sur le système et l'usage : uniquement des agrégats, jamais de données personnelles.

## 3.7.0 — 2026-11-08

### Nouveautés
- **SEO** : titre, description et texte par page, `robots.txt`, `sitemap.xml` et un vrai 404 pour les pages qui n'existent pas.

## 3.6.0 — 2026-11-08

### Amélioré
- Le site livre **un seul fichier JavaScript**, obscurci et précompressé : ce qui circule est bien plus léger qu'avant.

## 3.5.0 — 2026-11-08

### Nouveautés
- Thème visuel **Matrix Gamer** : pluie de caractères verts et lueur néon.

## 3.4.0 — 2026-11-08

### Amélioré
- Les styles passent à **Sass** et sortent en **un seul CSS**. La structure de la page est la même dans tous les thèmes : un thème ne change que les couleurs et la mise en forme.

## 3.3.0 — 2026-11-07

### Nouveautés
- **Thèmes visuels** : Premiado (le nouveau look par défaut) et sept autres (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala et Natal), chacun en clair et en sombre.
- Nouvelle icône de l'application.
