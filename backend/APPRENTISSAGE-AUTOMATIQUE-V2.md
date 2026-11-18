# AZ Turf Pro — apprentissage automatique V2

## Corrections apportées

- Le scheduler démarre avec l'application FastAPI et vérifie les arrivées archivées toutes les 30 minutes.
- Les arrivées récupérées auprès de la source PMU sont limitées aux cinq premiers chevaux.
- Une erreur de synchronisation ou de calibration reste non bloquante pour l'API.
- Les dates d'archives sont normalisées lors de la lecture de validation, y compris les formats historiques courants.
- Les facteurs candidats sont calculés séparément par spécialité : Plat, Attelé, Monté et Obstacle.
- Le moteur AZ et l'indice Premium savent lire ces facteurs par spécialité.
- La validation hors-échantillon compare désormais les résultats AZ et Premium.
- L'activation automatique exige une amélioration de couverture sur les deux évaluations, sans régression excessive sur le gagnant ni sur le top 5 complet.
- La route historique `/api/archive/calibrer` conserve son URL, mais déclenche maintenant le cycle sécurisé plutôt qu'une activation directe non validée.

## Protection des données et compatibilité

- Aucune table métier existante n'est supprimée.
- Aucune ligne de l'archive PostgreSQL n'est modifiée par la validation.
- Les anciennes calibrations au format plat restent lisibles.
- Les routes API existantes sont conservées.
- Les coefficients de base ne sont pas modifiés ; seuls des multiplicateurs validés peuvent être activés.

## Vérifications locales

`python -m compileall -q backend`

`cd backend && python -m unittest discover -q`

Résultat : 35 tests réussis.

## Limites de validation

Les tests ont été exécutés localement sans connexion à la base PostgreSQL de production. Le démarrage du scheduler et la synchronisation réelle PMU doivent donc être confirmés après déploiement dans les journaux Render. Aucune modification n'a été déployée automatiquement.
