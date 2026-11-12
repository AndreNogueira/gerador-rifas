# Changelog (résumé en français)

Résumé traduit de `../CHANGELOG.md` : mêmes versions, sections et points, plus courts. Le texte complet est en portugais.

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
