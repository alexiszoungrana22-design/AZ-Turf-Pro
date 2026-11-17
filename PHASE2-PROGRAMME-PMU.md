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
- Suite de tests backend : 45 tests réussis après ajout de la route des partants.
- Deux tests ajoutés pour la nouvelle route (normalisation/extraction et indisponibilité).
- Le test de la route utilise une réponse PMU simulée ; la disponibilité du service PMU en production n'a pas été vérifiée depuis cet environnement.

## À faire ensuite

- Le lien vers les partants par course est désormais réalisé par la route additive décrite ci-dessous.
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

- Backend : 45 tests réussis après ajout de la route des partants.
- Compilation Python : réussie.
- Syntaxe JavaScript de `programme.js` : vérifiée avec `node --check`.
- Archive ZIP : contrôlée avec testzip ; aucune erreur d’intégrité.
- Le flux PMU réel et le rendu sur Render/GitHub Pages ne peuvent pas être certifiés depuis cet environnement.


## Extension — consultation des partants par course

- Ajout de la route additive `GET /api/programme/partants?date=YYYY-MM-DD&reunion=R1&course=C1`.
- La route utilise le chargeur PMU existant `charger_course_pmu` pour demander les participants de la réunion et de la course choisies.
- Elle retourne uniquement les chevaux fournis par la source PMU, avec les informations effectivement disponibles : numéro, nom, âge, sexe, jockey, entraîneur, musique, cote brute et statut partant/non-partant.
- En cas d'indisponibilité des participants, la route renvoie une erreur explicite ; aucune liste de démonstration n'est substituée.
- La page `programme.html` propose désormais « Voir les partants » sur chaque course et affiche la réponse de cette route.
- Les routes historiques `/api/partants` et `/api/analyse` n'ont pas été modifiées. Aucun fichier du moteur, de la base PostgreSQL, des paiements ou des abonnements n'a été modifié.
- Vérifications locales : compilation Python, `node --check programme.js` et `PYTHONPATH=. pytest -q` depuis `backend` : 45 tests réussis. La disponibilité effective du fournisseur PMU depuis Render reste à confirmer en production.

## Analyse d'une course choisie

La page `programme.html` permet maintenant de demander les partants d'une course puis de lancer son analyse AZ depuis cette même fiche.

- Nouvelle route additive : `GET /api/analyse/course?date=YYYY-MM-DD&reunion=R2&course=C5`.
- La route charge la course précise depuis la source PMU, puis appelle le moteur existant `lancer_analyse`.
- La réponse conserve les champs principaux attendus par les écrans d'analyse (`classement`, `chevaux`, `favori`, `tickets`, informations de course) et indique explicitement `source: pmu_live` et `donnees_demo: false`.
- Si les données PMU de la course ne sont pas disponibles, la route renvoie une erreur explicite. Aucun repli sur `courses.json` n'est effectué pour une course choisie.
- Dans la page Programme, le classement AZ et les tickets gratuits calculés pour cette course sont affichés sous les partants. Les tickets Premium ne sont pas exposés dans cet écran.
- La route historique `GET /api/analyse` n'est pas modifiée. Aucun changement de schéma PostgreSQL, de paiement ou d'abonnement.
