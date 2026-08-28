AZ Turf-Pro — correction historique/PMU

Fichiers a remplacer dans backend/ :
- api.py
- engine.py
- pmu_source.py

Routes ajoutees/verifiees :
- GET /api/historique/diagnostic
- GET /api/performance/30-courses
- POST /api/historique/synchroniser (conservee)

Le correctif conserve pmu_id/identifiant_pmu lorsqu'il est fourni par la source PMU et utilise date+reunion+course_numero comme cle de secours.

Verification locale effectuee : parsing AST des 3 fichiers et verification statique des routes/champs.
