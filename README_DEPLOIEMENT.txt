AZ TURF PRO v33 — CORRECTION ACCÈS ADMIN

Fichiers à remplacer :
- backend/api.py
- admin.html
- admin.js
- chatbot.js

Cause corrigée : l'interface d'administration utilisait une vérification séparée alors que le backend n'acceptait qu'un seul nom de variable et les routes d'administration n'étaient pas toutes protégées.

Le serveur accepte maintenant, dans cet ordre, une des variables Render :
AZ_ADMIN_API_KEY
AZ_TURF_ADMIN_API_KEY
AZ_TURF_ADMIN_KEY
ADMIN_API_KEY
ADMIN_KEY

La clé saisie dans admin.html est vérifiée par GET /api/admin/verification avec X-Admin-Key.
Les statistiques, abonnements et activation utilisent ensuite la même clé.

IMPORTANT : il faut configurer UNE de ces variables dans Render avec la clé administrateur réelle. Ne pas mettre la clé secrète dans le code source.
Après déploiement, vider le cache navigateur/recharger la page admin.

Résultats attendus :
200 /api/admin/verification si la clé est correcte.
401 si la clé saisie est différente.
503 si aucune clé administrateur n'est configurée sur Render.
