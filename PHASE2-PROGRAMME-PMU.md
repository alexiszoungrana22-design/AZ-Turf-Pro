# Phase 2 — Programme PMU

## Travail effectué

- Ajout de `GET /api/programme?date=YYYY-MM-DD` (date facultative : aujourd'hui).
- Paramètre facultatif `reunion` pour limiter la lecture à une réunion.
- Réutilisation de `recuperer_programme` et `normaliser_date` dans `pmu_source.py` ; aucune deuxième connexion PMU n'a été créée.
- Réponse structurée par réunion et course : numéros, libellés, horaires disponibles, hippodrome, discipline, distance, allocation, nombre déclaré de partants, statut et indicateur Quinté+.
- En cas d'indisponibilité PMU, l'API renvoie une erreur explicite 503 : aucune course de démonstration n'est présentée comme réelle.
- Aucune modification de `/api/analyse`, `/api/partants`, des tickets, de la calibration, des paiements ou du stockage PostgreSQL.

## Vérifications

- Compilation Python de `backend/api.py` et `backend/pmu_source.py` : réussie.
- Suite de tests backend : 42 tests réussis.
- Deux tests ajoutés pour la nouvelle route (normalisation/extraction et indisponibilité).
- Le test de la route utilise une réponse PMU simulée ; la disponibilité du service PMU en production n'a pas été vérifiée depuis cet environnement.

## À faire ensuite

- Relier l'écran Programme à cette route, avec navigation par date, réunion et course.
- Tester le programme réel depuis Render avant de considérer l'affichage comme validé en production.


## Phase 2 — écran Programme (complément)

- Ajout de `programme.html`, `programme.js` et `programme.css`.
- Navigation de date : hier, aujourd'hui, demain et calendrier.
- Affichage des réunions PMU, sélection d'une réunion et liste de ses courses.
- Présentation des horaires, distances, nombres déclarés de partants, disciplines, allocations, statuts et marqueur Quinté+ lorsque présents dans la réponse API.
- Les valeurs absentes restent explicitement indiquées comme non renseignées.
- Ajout d'un accès Programme dans la navigation de l'accueil.
- L'écran appelle uniquement `GET /api/programme`; il ne remplace pas la route d'analyse et n'envoie aucune donnée de démonstration.
- Les erreurs PMU sont affichées sans fabriquer de programme.

## Vérifications complémentaires

- Backend : 42 tests réussis.
- Compilation Python : réussie.
- Syntaxe JavaScript de `programme.js` : vérifiée avec `node --check`.
- Archive ZIP : à vérifier après création.
- Le flux PMU réel et le rendu sur Render/GitHub Pages ne peuvent pas être certifiés depuis cet environnement.
