# KetuviClean — site local

Site français de neuf pages. Les légendes des trois photos de couverture mènent aux services résidentiel et commercial et au reportage sur les gestes d’entretien. Chaque fiche de service permet de préparer une demande avec des choix facultatifs. Les particuliers choisissent les pièces, les gestionnaires indiquent les espaces et le créneau souhaité, et les visiteurs qui déménagent peuvent préciser la date de remise des clés. Ces choix restent modifiables dans le formulaire de soumission.

## Démarrer

Depuis `C:/Dev/web`, exécuter `npm start`, puis ouvrir http://127.0.0.1:4173.
Node 20 ou plus récent suffit au fonctionnement du site. Aucune installation npm n’est nécessaire.

## Modifier et reconstruire

- Pages et contenu : `scripts/build_site.py`.
- `site/public/assets/styles.css` fournit les styles de base. `site/public/assets/hero.css` habille le header, la couverture, les cartes et les sections photographiques.
- `site/public/assets/footer.css` habille la signature, les coordonnées et les liens du pied de page.
- `site/public/assets/service-guide.css` habille la page « Quel entretien vous faut-il ? ». Chaque situation mène à sa fiche et propose deux exemples de soumission préremplie sous « Partir d’un exemple ».
- `site/public/assets/service-planner.css` habille les sélecteurs commercial et ponctuel. Sur les trois fiches, `service-planner.js` reprend la sélection dans les liens de soumission de l’en-tête et du pied de page. Il adapte aussi la date au motif des travaux ponctuels.
- `site/public/assets/app.js` gère la navigation et les formulaires. `site/public/assets/hero.js` active la galerie manuelle avec boutons, flèches du clavier et balayage.
- Serveur et réception locale : `site/server.mjs`.
- Reconstruire les pages et variantes WebP : `npm run build`. Le script utilise le Python/Pillow du runtime Codex actuel ; `KETUVI_PYTHON` peut désigner un autre interpréteur disposant de Pillow.
- Vérifier les liens : `npm run check`.
- Tester la réception : `npm test`. Le contrôle de boucle locale peut nécessiter les permissions réseau du poste.

## Formulaires

Sur Vercel, les formulaires de soumission et de candidature préparent un courriel sur l’appareil du visiteur. Le brouillon reprend les coordonnées, les choix de service ou les disponibilités, les précisions et le consentement. Le visiteur peut le relire, le copier ou l’ouvrir dans sa messagerie pour l’envoyer à **info@ketuvi.com**. Le site statique ne reçoit pas les champs et ne crée pas de référence de réception. Sans JavaScript, le lien de contact reste disponible.

L’aperçu enregistre les demandes validées dans `site/.data/requests.ndjson` et propose un courriel préparé à transmettre à **info@ketuvi.com**. Les fichiers de réception sont privés et exclus de Git.

Après une soumission, « Ma demande » permet de relire les coordonnées, le service, les choix et les précisions. « Copier ma demande et sa référence » conserve ces renseignements et le statut de transmission dans le presse-papiers. Si le navigateur bloque la copie, le texte est sélectionné pour permettre une copie manuelle.

Pour activer l’envoi direct, renseigner dans l’environnement du serveur les deux variables suivantes, puis redémarrer le serveur. Le destinataire des soumissions et des candidatures est **info@ketuvi.com**.

- `KETUVI_RESEND_API_KEY` contient une clé ayant l’autorisation d’envoyer des courriels dans le compte Resend de Ketuvi.
- `KETUVI_MAIL_FROM` contient l’adresse expéditrice sur un domaine vérifié auprès de Resend. L’adresse du visiteur est utilisée pour les réponses.

En mode courriel, le serveur conserve une fiche privée par demande dans `site/.data/mail/`. Il y inscrit l’identifiant du fournisseur et confirme la transmission au visiteur après acceptation par la messagerie. Le navigateur réutilise la même clé pour réessayer une demande identique. En cas de résultat incertain après 24 heures, la référence permet de rapprocher la fiche du journal de messagerie. Les tests utilisent un serveur de courriel simulé en boucle locale et un répertoire temporaire.

## Médias et marque

Les originaux 4K sont conservés dans `brand-guidelines/assets/photos/`. Chaque photo utilisée sur le site est réservée à un seul emplacement. Le contrôle des pages suit la provenance des images, y compris les scènes de galerie chargées à la demande. Le navigateur choisit parmi les WebP de 480, 768, 1024, 1440, 2304 et 3840 px selon la place occupée et la densité de l’écran. Sur téléphone, la galerie dispose également d’un recadrage portrait pouvant atteindre sa résolution native de 1728 × 2160 px. Le générateur limite chaque variante aux dimensions disponibles dans le fichier source.

Les polices et le symbole proviennent des fichiers du client. La nouvelle signature est composée en texte natif et utilise le symbole officiel. Les photographies sont des illustrations générées, pas des références clients.

Les six icônes pleines duotone adaptent Phosphor Fill. Leur attribution et la licence MIT sont dans `brand-guidelines/assets/icons/NOTICE.md` et `LICENSE-Phosphor.txt`, et sont incluses dans le kit. Flaticon et LottieFiles ont servi de références de finition.

## Avant publication

### Hébergement statique Vercel

Choisir la racine du dépôt pour le projet Vercel. `vercel.json` exécute `npm run build:vercel` et publie le dossier `dist/`. Ce build utilise Node et la bibliothèque standard de Python 3. Il laisse `site/public/` disponible pour le serveur local. Pour vérifier la sortie sur le poste Windows, la même commande utilise le Python installé ou celui indiqué par `KETUVI_PYTHON`.

La version publique reprend les WebP référencés dans les pages, les deux symboles Ketuvi et les notices de Phosphor. Elle utilise les polices système Helvetica Neue, Helvetica ou Arial. Le fichier `scripts/site-photos.json`, actualisé par le build local des médias, fournit les descriptions et dimensions nécessaires. Après avoir remplacé une photo source, exécuter `npm run build` sur le poste de production des visuels avant de republier.

### Domaine public, recherche et liens partagés

Pour la compilation de production, définir `KETUVI_PUBLIC_ORIGIN` dans l’environnement qui exécute `npm run build`. Sa valeur est l’origine HTTPS du domaine confirmé de Ketuvi, sans chemin, paramètres ou fragment. Reconstruire les pages après tout changement de domaine.

Le build ajoute une adresse canonique par page, les aperçus de partage en français canadien avec une image locale, et un `sitemap.xml` référencé dans `robots.txt`. Les demandes préremplies partagent l’adresse canonique de la page Contact. La page 404 reste hors du plan de site.

En production Vercel, l’origine prend par défaut la valeur HTTPS de `VERCEL_PROJECT_PRODUCTION_URL`. Les déploiements de prévisualisation Vercel portent toujours la directive `noindex`. Sans origine publique, le build local applique également `noindex`. Ces builds retirent tout plan de site issu d’une compilation de production précédente.

Le build statique sélectionne automatiquement le mode de formulaire par messagerie. Pour l’essayer sur un autre hébergement statique avec le build classique, définir `KETUVI_FORM_MODE=mailto`. Le serveur d’aperçu écoute sur `127.0.0.1`. Les variables Resend et le stockage privé concernent l’hébergement avec envoi direct.
