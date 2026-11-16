CORRECTION AZ TURF PRO — ROUTE DE VALIDATION APPRENTISSAGE

Cause confirmée dans le ZIP reçu :
- backend/api.py importait `modules.learning_validation`
- le fichier réel est `backend/learning_validation.py`
- il n'existait pas de `backend/modules/learning_validation.py`

Correction :
- l'import dans backend/api.py utilise maintenant `from learning_validation import ...`
  ce qui correspond au chemin d'exécution de backend/main.py, qui ajoute le dossier
  backend à sys.path avant de charger api.
- la fonction `lire_archive_pour_validation` dans backend/archive_store.py ne lance
  plus `_init(conn)` : elle effectue uniquement le SELECT, sans création de table
  ni commit. Cela respecte le mode lecture seule de cette route.

Aucune modification des coefficients, des archives, des abonnements ou des tickets.
La route demeure protégée par `_require_admin` et reste sous le préfixe /api.

Tests locaux :
- 30 tests de régression existants : réussis.
- 2 tests ciblés ajoutés : réussis.
- compilation Python des fichiers backend : réussie.
- import du module dans l'environnement de lancement backend : réussi.
- présence de la route vérifiée : /api/archive/validation-apprentissage.

Limite :
- aucune connexion à la base PostgreSQL de Render n'a été effectuée.
- ce ZIP n'est pas déployé. Il doit être vérifié avant remplacement de la version
  en production.


AJOUT — CALIBRATION AUTOMATIQUE PRUDENTE

- Après l'enregistrement d'une nouvelle arrivée officielle, les routes existantes `/api/historique` et `/api/archive/synchroniser` déclenchent désormais une vérification automatique.
- Le déclencheur est isolé et protégé par `try/except` : une erreur de calibration ne bloque jamais la mise à jour de l'historique ou de l'arrivée.
- Aucune activation avant 50 courses terminées, dont au moins 15 courses de test hors-échantillon.
- Une nouvelle validation est faite après 5 nouvelles courses terminées.
- Les facteurs ne sont enregistrés que si la couverture moyenne du Top 5 progresse d'au moins 1 point et si les deux autres indicateurs ne baissent pas de plus d'un point. Sinon, la calibration existante reste active.
- Un verrou PostgreSQL évite deux calibrations simultanées. La table d'état `az_auto_calibration_state` est ajoutée avec `CREATE TABLE IF NOT EXISTS`, sans supprimer ni modifier les tables existantes.
- La route manuelle `/api/archive/calibrer` et la route de validation admin restent disponibles et inchangées.

Vérifications locales après cet ajout : compilation Python réussie ; 40 tests automatisés réussis ; import API réussi et présence des routes historiques/calibration vérifiée. Aucune connexion à PostgreSQL Render ni aucun déploiement Render n'a été effectué.
