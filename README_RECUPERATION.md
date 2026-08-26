# AZ Turf Pro — récupération complémentaire

Fichiers récupérés depuis la bibliothèque :
- backend/main.py
- backend/pmu_source.py
- backend/config.py

Le moteur PMU récupéré conserve notamment `charger_course_pmu()` et la récupération de l'arrivée réelle `recuperer_arrivee_pmu()`.

## Dépendances encore non récupérées
Le projet API importe aussi :
- `backend/engine.py`
- `backend/database.py`
- `backend/models.py`
- `backend/learning.py`
- `backend/lonab_source.py`

Ces fichiers n'ont pas été retrouvés dans la bibliothèque avec les recherches effectuées. Ils ne sont donc pas inventés ni remplacés par des faux modules.

## Vérification
Le ZIP est une récupération complète des sources actuellement disponibles, mais Render ne sera réellement autonome qu'après récupération des dépendances ci-dessus.
