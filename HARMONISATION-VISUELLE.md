# Harmonisation visuelle AZ Turf Pro

Cette livraison ajoute `harmonisation.css` comme couche de présentation commune et le référence depuis les 20 pages HTML du dépôt.

## Principes
- Palette claire : vert, blanc, or discret et gris clair.
- Typographie, navigation, boutons, formulaires, tableaux et surfaces harmonisés.
- Barre de navigation commune ajoutée aux pages qui n'en possédaient pas.
- Adaptation mobile avec navigation horizontale défilante.
- Les scripts métier, routes API, moteur de pronostics, tickets, paiements et stockage PostgreSQL ne sont pas modifiés.

## Fichiers
- Nouveau : `harmonisation.css`, `HARMONISATION-VISUELLE.md`.
- Modifiés : les 20 fichiers HTML présents à la racine du projet.

## Vérifications locales
- Archive source contrôlée avant modification.
- 33 tests Python réussis.
- Compilation Python réussie.
- Vérification syntaxique Node des fichiers JavaScript réussie.
- Contrôle structurel des 20 pages HTML réussi.

Les tests locaux ne remplacent pas un essai sur le site déployé. Aucune modification n'a été publiée sur GitHub ou Render.


## Correction de navigation mobile
Sur écran mobile, la navigation haute est masquée lorsque la barre basse mobile est présente. La barre basse devient la navigation principale. Sur ordinateur, la barre basse est masquée et la navigation haute reste disponible. Aucun fichier Python, JavaScript ou aucune donnée de base n’a été modifié pour cette correction.
