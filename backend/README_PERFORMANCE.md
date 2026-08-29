# AZ Turf Pro — performances de l'archive

Ajout préparé sans suppression de routes.

## Fichiers
- `archive_performance.py` : calcul des performances uniquement sur les courses avec arrivée officielle.
- `archive_store.py` : ajout de `lire_archive_performance()` pour lire les données PostgreSQL nécessaires.

## Indicateurs
- nombre de courses terminées et exploitables ;
- nombre/taux de favoris gagnants ;
- nombre/taux de courses où le gagnant figure dans la sélection AZ ;
- nombre/taux de courses où au moins un cheval de la sélection AZ figure dans l'arrivée.

Aucune performance n'est calculée pour une course sans arrivée officielle.
