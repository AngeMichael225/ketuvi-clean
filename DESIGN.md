---
name: "KetuviClean — Crystal Clean"
description: "Un système lumineux, photographique et attentif au soin des espaces."
colors:
  primary: "#B35CFF"
  secondary: "#17C3B2"
  forest: "#104543"
  ink: "#0D1B1E"
  slate: "#374345"
  white: "#FFFFFF"
  mist: "#F3F8F7"
  line: "#D5E2DF"
  violet-text: "#683197"
  primary-hover: "#B86EFA"
  primary-pressed: "#AE57FA"
  amethyst-soft: "#F3EBFC"
  teal-text: "#10675F"
  teal-soft: "#E4F7F3"
  control-line: "#74837F"
  error-text: "#902C43"
  error-soft: "#FFF0F2"
  glass: "rgb(18 33 32 / .70)"
  header: "rgb(255 255 255 / .96)"
typography:
  display: {fontFamily: '"Ketuvi Sans", Helvetica, Arial, sans-serif', fontSize: "clamp(82px, 8.5vw, 150px)", fontWeight: 400, lineHeight: 0.94, letterSpacing: "-0.056em"}
  headline: {fontFamily: '"Ketuvi Sans", Helvetica, Arial, sans-serif', fontSize: "clamp(2rem, 3.45vw, 3.4rem)", fontWeight: 500, lineHeight: 1.1, letterSpacing: "-0.035em"}
  title: {fontFamily: '"Ketuvi Sans", Helvetica, Arial, sans-serif', fontSize: "1.65rem", fontWeight: 500, lineHeight: 1.2, letterSpacing: "-0.02em"}
  body: {fontFamily: '"Ketuvi Sans", Helvetica, Arial, sans-serif', fontSize: "18px", fontWeight: 400, lineHeight: 1.55}
  label: {fontFamily: '"Ketuvi Sans", Helvetica, Arial, sans-serif', fontSize: "17px", fontWeight: 500, lineHeight: 1.3}
rounded:
  field: "12px"
  control: "16px"
  navigation: "0px"
  cover: "24px"
  pill: "100px"
spacing:
  compact: "16px"
  group: "24px"
  section-mobile: "72px"
  section: "116px"
components:
  button-primary: {backgroundColor: "{colors.primary}", textColor: "{colors.ink}", typography: "{typography.label}", rounded: "{rounded.pill}", padding: "15px 22px 15px 26px", height: "56px"}
  button-primary-hover: {backgroundColor: "{colors.primary-hover}"}
  button-secondary: {backgroundColor: "{colors.ink}", textColor: "{colors.white}", typography: "{typography.label}", rounded: "{rounded.pill}", padding: "15px 22px 15px 26px", height: "56px"}
  button-secondary-hover: {backgroundColor: "{colors.forest}"}
  input: {backgroundColor: "{colors.white}", textColor: "{colors.ink}", rounded: "{rounded.field}", padding: "13px 15px", height: "53px"}
  navigation: {backgroundColor: "{colors.header}", textColor: "{colors.ink}", rounded: "{rounded.navigation}", padding: "0 clamp(6px, 2vw, 38px)", height: "78px"}
  service-image: {backgroundColor: "{colors.forest}", rounded: "17px", height: "clamp(248px, 23vw, 372px)"}
  icon-filled-duotone: {textColor: "{colors.primary}", width: "36px", height: "36px"}
---

# Design System: KetuviClean — Crystal Clean

## Overview

**Creative North Star: "Crystal Clean"**

Crystal Clean traduit le soin des espaces par des photographies lumineuses, une typographie nette et des surfaces claires. Le symbole officiel signe la navigation. L’améthyste conduit les actions et le turquoise souligne les détails.

Les photos 4K montrent les espaces, les professionnels et leurs gestes. Chaque photo utilisée est réservée à un seul emplacement. La couverture en pleine image ouvre le parcours. Les cartes présentent les trois services, puis le reportage montre deux gestes d’entretien.

**Key Characteristics:**
- Photographie lumineuse et matières crédibles.
- Améthyste prioritaire, turquoise en soutien.
- Verre sombre réservé aux commandes de galerie et transitions brèves à la demande.

## Colors

L’améthyste porte les actions principales. Sa teinte pâle met en évidence les choix et éclaire les introductions photographiques. Le turquoise signe les détails des icônes. Sa variante foncée identifie la référence de demande et confirme la copie. Le violet profond marque les liens et le focus sur fond clair. L’ardoise sert au texte courant et l’encre aux titres et aux libellés des boutons améthyste. Les bordures des champs sont plus foncées que les séparateurs décoratifs.

## Typography

Helvetica Neue est auto-hébergée sous l’alias « Ketuvi Sans » : Roman (400), Medium (500), Light (300). Les replis sont Helvetica, Arial et sans-serif.
Le titre de couverture se compose en Roman sur deux lignes, avec un interligne de 0,94 sur ordinateur et de 0,95 sur téléphone. Les titres des pages intérieures utilisent un interligne de 1,03. Les titres éditoriaux et les fiches de service alignent le texte à gauche. La graisse Light distingue « Clean » dans la signature.

## Layout

Le conteneur principal est limité à 1 280 px et occupe la largeur moins 112 px. À 1 100 px, les marges latérales passent à 36 px ; à 700 px, elles passent à 22 px.
La couverture s’étend jusqu’à 1 800 px et l’intérieur de l’en-tête jusqu’à 1 600 px. Les services forment une grille de trois photos, la première plus large sur ordinateur. À 960 px, les colonnes s’égalisent et le menu compact apparaît. À 700 px, services, compositions éditoriales et formulaires passent en une colonne. Sur téléphone, les pages Contact et Carrières placent la photo d’accompagnement après le formulaire.
Les formulaires utilisent deux colonnes avec des écarts de 24 px × 20 px ; les champs deviennent une colonne sur mobile.

## Elevation & Depth

Un filet sépare le header blanc de la page. Un dégradé sombre assure le contraste du texte blanc sur la couverture. La commande des photos utilise un verre sombre avec un flou fixe de 14 px. Le menu des services déployé reçoit une ombre de 0 18px 50px, encre à 15 %.

## Shapes

Les boutons d’action sont des capsules. Les champs du formulaire ont un rayon de 12 px. Le rayon de la couverture passe de 24 à 17 px sur téléphone. Les cartes photographiques ont des coins de 17 px.
Les photographies sont recadrées avec object-fit: cover, sans déformation. Le portrait garde son sujet vers la droite. Les cartes n’ajoutent ni bordure ni ombre autour du contenu.

## Components

**Boutons.** Le libellé utilise la graisse Medium. La hauteur minimale est de 56 px pour un bouton standard et de 47 px pour le bouton de couverture sur téléphone. À la souris, la flèche avance de 3 px. À l’appui, le bouton s’assombrit et se contracte de 2 %. Le focus clavier est visible sur les fonds clairs comme sur les photos. Pendant l’envoi, le bouton conserve sa largeur et indique l’opération en cours.
**Champs.** Fond blanc, filet de séparation, texte de 17 px, interligne de 1,45 et hauteur minimale de 53 px. Le focus emploie une bordure améthyste et un contour améthyste à 20 %. Les erreurs se lisent dans un message explicite ; le contenu saisi est conservé.
**Cartes de services.** L’image porte le titre blanc, l’icône duotone et une flèche oblique en médaillon. Un dégradé fonce le bas de chaque photo. La description suit sous la carte.
**Icônes.** Six silhouettes Phosphor Fill adaptées en duotone : masse améthyste et détail structurel turquoise, sans contour fin ni fond intégré. Les mêmes tracés servent au SVG et au PDF ; la licence MIT et l’attribution accompagnent les fichiers.
**Pied de page.** La signature blanche, le courriel et les liens de navigation se lisent sur fond encre. Le titre « Parlons de vos espaces » et le bouton de soumission apparaissent au premier passage dans l’écran. Depuis une fiche de service, ce bouton transmet les choix en cours au formulaire. Après le premier écran, une flèche fixe en bas à droite ramène en haut de la page. Elle monte légèrement au survol.
**Guide des services.** Chaque ligne associe une situation à une photographie et au nom du service. Toute la ligne ouvre la fiche. Sur téléphone, le nom du service se place sous la description.
**Navigation.** L’en-tête blanc reste en haut de l’écran. Il associe la signature, les services, « À propos », « Carrières » et la soumission. Sur la page Carrières, l’action principale devient « Postuler » et mène au formulaire de candidature. Sur téléphone, l’action principale reste visible près du menu compact. Échap ferme ce menu.
**FAQ.** Un signe plus repère chaque question. La réponse s’ouvre au clic ou au clavier et reste dans le flux de lecture.

**Cartes de services.** Au survol ou au focus clavier, la photo se rapproche, le titre se souligne en turquoise et la flèche s’oriente vers la fiche. Sur écran tactile, un appui ouvre directement le service. En mouvement réduit, la couleur et le soulignement restent perceptibles.
**Couverture photographique.** Le titre « Le propre, ça se voit. » et le bouton de soumission restent sur la photo. Les trois images se parcourent par les boutons précédent et suivant, au clavier ou par balayage horizontal. La légende cliquable mène à l’entretien résidentiel, à l’entretien commercial ou au reportage sur les gestes. Sur téléphone, les commandes passent en haut à gauche et le texte en bas. Le lien blanc souligné « Quel service choisir ? » se place sous le bouton de soumission. Sur grand écran, ce lien accompagne le titre « Nos services. ».
**Reportage.** Dans « Le travail de près », deux photographies légendées montrent l’entretien des cloisons vitrées et la préparation des microfibres. Elles occupent deux colonnes de largeurs différentes sur ordinateur et se suivent sur téléphone.
**Mouvement.** Le changement de photo choisi par le visiteur utilise un fondu de 380 ms une fois la nouvelle image prête. Un léger déplacement dans le sens de navigation se stabilise en 900 ms. Les menus et les réponses de la FAQ apparaissent en 160 ms. La préférence de mouvement réduit donne un changement de photo immédiat et conserve les indications de couleur, le focus et les libellés des actions.

## Do's and Don'ts

- Do préserver le symbole officiel et la famille Helvetica Neue fournie.
- Do garder l’encre sur les actions améthyste et la lecture nette sur le verre.
- Do conserver le polo améthyste, le logo blanc et le pantalon ardoise dans les photographies de personnes.
- Do proposer une image fixe avec la préférence de réduction des mouvements.
- Don't recréer le symbole par une forme approchante ou déformer le logo.
- Don't réutiliser les anciennes photographies ni remplacer les scènes par un rendu CGI.
- Don't employer le turquoise comme couleur principale ou le blanc pour du texte courant sur améthyste.
- Don't ajouter de mouvements en boucle ou masquer le contenu initial derrière une animation.

