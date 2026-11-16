# Calibration automatique — ajout isolé

- Déclenchement après l'enregistrement d'une arrivée officielle dans `/api/historique` ou `/api/archive/synchroniser`.
- Le déclencheur est protégé : une erreur de calibration ne bloque pas l'historique ni la synchronisation.
- Aucun essai d'activation avant 50 courses terminées et au moins 15 courses de test hors-échantillon.
- Une nouvelle évaluation n'est lancée qu'après 5 nouvelles courses terminées depuis la précédente.
- Activation uniquement si la couverture moyenne du Top 5 progresse d'au moins 1 point, sans baisse supérieure à 1 point du taux de gagnant dans le Top 5 ni du Top 5 complet.
- Si les données sont insuffisantes, si les résultats ne progressent pas ou si une erreur survient, la calibration active précédente reste inchangée.
- Un verrou consultatif PostgreSQL évite les exécutions concurrentes. Une table d'état `az_auto_calibration_state` est créée avec `CREATE TABLE IF NOT EXISTS`; aucune table ni donnée existante n'est supprimée ou réinitialisée.
- Les routes publiques, les règles de tickets, les abonnements, le moteur de score et les autres fonctions ne sont pas modifiés. Le déclenchement est additif.

La calibration reste prudente : elle compare les facteurs candidats aux coefficients neutres sur les courses chronologiquement postérieures à l'apprentissage. Ces métriques évaluent la qualité de classement, pas la rentabilité des paris.
