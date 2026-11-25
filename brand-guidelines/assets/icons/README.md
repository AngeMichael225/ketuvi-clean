# Icônes Ketuvi — formes pleines, version 2

Six SVG duotone sur une grille 24 × 24, adaptés de Phosphor Icons (MIT).
La silhouette améthyste **#B35CFF** domine. Le turquoise **#17C3B2** souligne
un détail : annexe, porte, manche, attache, message ou fermoir.

- Utiliser à 24, 32, 48 ou 64 px, avec un libellé visible pour les choix de service.
- Chemins fermés et remplis : aucun trait, dégradé, ombre ni fond intégré.
- Conserver les couleurs et proportions. Ne pas ajouter de contour.
- Chaque fichier possède un titre accessible. Pour un SVG décoratif inline,
  retirer le titre et aria-labelledby, puis ajouter aria-hidden="true".
- Animer brièvement le détail turquoise au survol ou au focus, sans boucle.
  La réduction des mouvements conserve la version fixe.
- Les SVG et le PDF partagent exactement les mêmes données de chemins.

Sources et licence : [NOTICE.md](NOTICE.md), [LICENSE-Phosphor.txt](LICENSE-Phosphor.txt).
Planche locale : ../../review/icons-v2.html.

Génération : export_icon_assets(folder), depuis brandkit/ketuvi_icons.py.
L’API PDF reste draw_pdf_icon(c, height, kind, x, top, size, primary).
