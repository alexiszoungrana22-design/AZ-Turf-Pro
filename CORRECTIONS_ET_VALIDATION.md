# AZ Turf Pro — corrections et validation

Version préparée le 01/09/2026.

## Corrections principales

- Séparation stricte entre `cote` normalisée utilisée par le scoring et `cote_brute` utilisée pour l'affichage, la valeur et les règles Premium.
- Correction du bonus « outsider chaud » Premium : il utilise maintenant la cote brute réelle lorsqu'elle est disponible.
- Conservation des gains bruts dans `gains_carriere_brute` pour éviter d'afficher un score normalisé comme des gains.
- Le chatbot affiche les cotes et gains dans leur forme brute lorsqu'elle est disponible.
- Correction du routage conversationnel : salutations, Quinté Premium, duo/couplé, champ réduit et fiche d'un cheval ont priorité sur une intention générique.
- Amélioration de la fiche cheval avec une lecture experte déterministe basée uniquement sur les données présentes.
- Le vocabulaire utilisateur privilégie « analyse autonome » plutôt que « IA » dans les réponses locales.
- Ajout de la provenance/qualité des données dans la réponse du moteur.
- Ajout d'une indication explicite : la « confiance » AZ est une proximité de l'indice au leader, pas une probabilité de victoire.
- Correction du message de journalisation PMU qui pouvait produire `RR1` au lieu de `R1`.
- Ajout de tests de régression pour moteur, tickets, non-partants, chatbot et séparation cote brute/score.

## Règles de tickets conservées

- Quinté gratuit : 7 chevaux.
- Quinté Premium : 6 chevaux.
- Quarté Premium : 5 chevaux.
- Trio Premium : 3 chevaux.
- Champ réduit Premium : structure calculée par le moteur.
- Dernière minute : sélection indépendante du classement Premium.

## Enrichissement par spécialité (Plat / Attelé / Monté / Obstacle)

Auparavant, Attelé et Monté étaient confondus sous un seul bucket de pondération "TROT", et deux bonus existaient dans le code (corde au Plat, déferrage au Trot) sans jamais recevoir de valeur : `pmu_source.py` n'extrayait ni `placeCorde` ni `deferre` depuis les données PMU brutes.

- **`pmu_source.py`** : extraction réelle de `corde` (champ PMU `placeCorde`) et `deferre` (champ PMU `deferre`, normalisé en `D4`/`DA`/`DP`/vide via une nouvelle fonction `normaliser_deferrage()`, tolérante aux formats string ou booléen). `obtenir_discipline()` combine désormais `discipline` + `specialite` (deux champs PMU distincts) pour permettre de différencier Attelé de Monté.
- **`scoring.py`** : nouvelle fonction `classifier_discipline()` partagée, 4 jeux de coefficients désormais distincts (Plat / Attelé / Monté / Obstacle) — Monté valorise davantage le jockey (coef. 5.0 contre 3.5 à l'Attelé). Les bonus corde et déferrage, jusqu'ici du code mort, sont maintenant réellement atteignables.
- **`engine.py`** : aucune modification nécessaire — son bonus déferrage Premium utilisait déjà des codes compatibles (`D4`/`DA`/`DP`), il était simplement privé de données comme le reste.
- **6 nouveaux tests de régression** ajoutés à `tests/test_regression.py` : classification des 4 disciplines, différenciation Attelé/Monté, et circuit complet extraction PMU → bonus corde/déferrage.

## Validation effectuée (2e passe)

1. Compilation de tous les modules Python : OK.
2. Validation locale sans réseau ni clé IA : OK.
3. 5 tests de régression : OK.
4. Import de `backend.main` : OK.
5. Démarrage Uvicorn local : OK.
6. `GET /` : HTTP 200.
7. `GET /api/analyse` : HTTP 200.
8. Vérification syntaxique JavaScript avec Node.js : OK pour les fichiers JS du projet.

1. Compilation de tous les modules Python (dont `scoring.py`, `pmu_source.py`, `engine.py` modifiés) : OK.
2. Import de tous les fichiers `backend/modules/*.py` + fichiers racine : 0 erreur.
3. 8 tests de régression (5 précédents + 3 nouveaux sur les spécialités) : OK.
4. `validate_project.py` (bout en bout, sans réseau ni clé IA) : OK.
5. Vérifications manuelles ciblées : classification des 4 disciplines, différenciation de score Attelé/Monté sur un même cheval, bonus corde/déferrage effectivement déclenchés via une extraction PMU simulée réaliste (champs `placeCorde`/`deferre` confirmés par recherche sur la structure réelle de l'API PMU).

## Limites volontairement conservées

Le moteur ne fabrique pas de données manquantes. Les statistiques jockey/driver, terrain individuel, distance individuelle, variations de cote, presse, météo et historique réel restent dépendantes des sources effectivement disponibles au moment de l'analyse.

Le ZIP contient donc un système renforcé, mais ne transforme pas les données absentes en faux chiffres.
