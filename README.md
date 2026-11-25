# KetuviClean

Site francophone de Nettoyage Ketuvi Inc. (NEQ 1179475471), avec neuf pages consacrées aux services, aux soumissions, aux carrières et à la confidentialité.

## Aperçu local

Avec Node.js 20 ou une version plus récente, lancer `npm start` et ouvrir [l’aperçu local](http://127.0.0.1:4173). Les données d’essai des formulaires restent dans le dossier privé `site/.data/`.

## Publication

Vercel construit la vitrine depuis la racine avec `npm run build:vercel` et publie `dist/`. Sur la vitrine publique, le formulaire prépare un courriel que le visiteur vérifie et envoie depuis sa messagerie à **info@ketuvi.com**.

Les commandes de développement et les détails des différents modes de réception figurent dans le [guide technique](site/README.md). Les vérifications à faire avec l’entreprise figurent dans la [fiche interne de mise en ligne](site/MISE-EN-LIGNE.md).
