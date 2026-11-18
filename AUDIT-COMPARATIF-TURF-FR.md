# Audit comparatif — AZ Turf Pro / TURF FR

Date de consultation : 17 novembre 2026

## 1. Périmètre et limites

Cet audit s'appuie sur les pages publiquement accessibles de TURF FR et sur l'archive AZ Turf Pro `AZ-Turf-Pro-AUDIT-VISUEL-PHASE1.zip` fournie dans cette conversation. Il ne prétend pas accéder au code serveur privé, aux scripts propriétaires ou aux données internes de TURF FR.

Aucune fonctionnalité, route API, donnée PostgreSQL ou logique de pronostic n'est modifiée par ce document.

## 2. Fonctionnalités observées sur TURF FR

La page d'accueil publique expose notamment :
- un Quinté+ du jour avec hippodrome, réunion/course, heure de départ, discipline, distance et nombre de partants ;
- un programme des réunions et courses, avec heures, discipline, prix, distance, partants et non-partants ;
- des statistiques contextualisées sur la course du Quinté ;
- des informations de pronostics et les résultats de ces pronostics ;
- un espace communautaire/direct et un concours ;
- des outils de préparation des paris, dont comparateur de cotes, systèmes réducteurs, tris de combinaisons et répartition des mises.

La page de présentation de l'application mobile mentionne aussi les fiches partants (chevaux, jockeys/drivers, entraîneurs, musiques et cotes), la navigation entre courses, les alertes avant départ et le comparateur de cotes.

## 3. État constaté dans AZ Turf Pro (archive Phase 1)

- `index.html` affiche un bloc Quinté hier/aujourd'hui/demain, un résumé de course, le compte à rebours, les indicateurs Favori AZ / Outsider AZ, un indice de confiance, les partants, les chevaux les plus joués et la tendance.
- `accueil.js` appelle actuellement `GET https://az-turf-pro.onrender.com/api/analyse` sans paramètre de date ou de course. La page d'accueil est donc centrée sur la réponse d'analyse renvoyée par cette route ; le HTML seul ne démontre pas l'existence d'un programme complet multi-réunions/multi-courses.
- Le tableau de partants affiche numéro, cheval, jockey/driver, entraîneur, cote, indice AZ, confiance et tendance.
- L'historique local du navigateur est alimenté depuis les analyses reçues, mais il ne remplace pas une archive serveur officielle.
- `style-ameliorations-turf.css` est une couche visuelle ajoutée à la fin du `<head>`. Elle conserve les identifiants DOM et les scripts de la page d'accueil.

## 4. Écarts et améliorations recommandées

### Priorité 1 — Programme multi-réunions et multi-courses

Ajouter une navigation date → réunion → course, avec état vide/chargement/erreur et affichage explicite de la source. Avant tout développement, vérifier quelles routes et quelles sources existantes fournissent déjà le programme complet afin de les réutiliser plutôt que créer une seconde source.

### Priorité 2 — Fiche détaillée d'un partant

Afficher, lorsque les données existent réellement : musique, gains, âge, poids, jockey/driver, entraîneur, cote et statut non-partant. Ne pas afficher de valeur fictive lorsqu'un champ manque.

### Priorité 3 — Analyse AZ explicable

Présenter séparément les facteurs réellement utilisés par le moteur, leur disponibilité et la raison du classement. Ne pas transformer un indice interne en probabilité de victoire sans calibration statistique validée.

### Priorité 4 — Résultats et bilan des pronostics

Rapprocher les sélections archivées avant course des arrivées officielles et publier des indicateurs définis précisément : gagnant dans la sélection, couverture du Top 5, ticket complet, et nombre de courses évaluées. Séparer résultats réels et données de démonstration.

### Priorité 5 — Outils de tickets

Étudier des outils de réduction et de tri des combinaisons uniquement après vérification des règles de tickets déjà en production. Conserver les formats gratuits et Premium actuels.

### Priorité 6 — Mobile, performance et sécurité d'affichage

Tester les tableaux sur petit écran, limiter les rechargements inutiles et vérifier l'échappement des champs dynamiques avant insertion dans `innerHTML`. Les données de noms/chevaux provenant d'une source externe doivent être traitées comme non fiables.

## 5. Ordre de réalisation sûr

1. Cartographier les routes et les formats JSON déjà disponibles.
2. Faire correspondre chaque écran aux données existantes.
3. Implémenter le programme multi-courses en réutilisant les routes actuelles, sans changer les contrats existants.
4. Ajouter les fiches détaillées et les bilans en lecture seule.
5. Tester sur données réelles et sur cas de données absentes/non-partants.
6. Livrer un ZIP avec uniquement les fichiers strictement nécessaires et un relevé exact des changements.

## 6. Sources publiques consultées

- TURF FR — page d'accueil : https://www.turf-fr.com/
- TURF FR — présentation du site : https://www.turf-fr.com/qui-sommes-nous/
- TURF FR — application mobile : https://www.turf-fr.com/application-mobile-turf/
- TURF FR — centre d'aide : https://www.turf-fr.com/aide/

Les fonctionnalités listées dans la section 2 sont des éléments présentés publiquement par TURF FR. Les priorités de la section 4 sont des recommandations d'audit, pas des fonctionnalités prétendument déjà présentes dans AZ Turf Pro.
