# AZ-Turf-Pro

## Consolidation technique — 2026-08

Cette version conserve le moteur AZ (`backend/engine.py`) et le flux PMU existants.
Elle ajoute notamment :

- `/api/partants`
- `/api/premium/analyse/{telephone}`
- `/api/assistant/chat`
- `/api/stats/backtest`
- export PDF réellement généré
- persistance configurable via `AZ_DATA_DIR` / `AZ_DB_PATH`
- protection optionnelle des routes admin via `AZ_ADMIN_API_KEY`
- correction du chargement `live-premium.js`
- suppression de la référence à `scripts.js` inexistant
- page Partants dynamique
- compatibilité avec les anciens champs d'arrivée de l'historique
- routes/alias de navigation manquants.

### Variables Render recommandées

- `AZ_DATA_DIR` : répertoire du disque persistant Render (recommandé pour conserver historique, exports et SQLite).
- `AZ_DB_PATH` : optionnel ; chemin complet de la base SQLite.
- `AZ_ADMIN_API_KEY` : clé secrète obligatoire en production pour protéger l'administration.
- `AZ_API_BASE_URL` : optionnel ; URL publique de l'API.

Le frontend peut enregistrer la clé admin sur l'appareil depuis `admin.html` lorsque `AZ_ADMIN_API_KEY` est activée sur le serveur.

### Important

Sans disque persistant, Render peut toujours perdre les données locales au redéploiement. Pour une conservation durable, attacher un Persistent Disk et pointer `AZ_DATA_DIR` vers ce disque.
