AZ TURF PRO v31 — CORRECTION DÉFINITIVE DE L'ACCÈS ADMIN

Problème constaté :
L'interface affiche « Clé administrateur refusée ».

Cause identifiée dans la version actuelle :
le backend ne vérifiait que la variable Render AZ_ADMIN_API_KEY.

Correction :
le backend accepte désormais les variables Render suivantes :
- AZ_ADMIN_API_KEY
- AZ_TURF_ADMIN_API_KEY
- AZ_TURF_ADMIN_KEY
- ADMIN_API_KEY
- ADMIN_KEY

La route /api/admin/verification accepte également :
- X-Admin-Key
- X-Admin-Api-Key
- Admin-Key
- Authorization: Bearer <clé-admin>

Sécurité :
- aucune clé n'est inscrite dans le code ;
- la comparaison utilise secrets.compare_digest ;
- une clé inconnue reste refusée ;
- si aucune clé serveur n'est configurée, l'API renvoie 503 au lieu d'un faux refus.

Routes assistant :
les mêmes variantes d'en-tête sont acceptées par /api/assistant/chat et
/api/assistant/chat/stream.

Fichier à remplacer :
backend/api.py

IMPORTANT :
Dans Render, il faut toujours conserver UNE vraie valeur secrète dans une
des variables ci-dessus. Ce correctif ne rend pas une clé arbitraire valide.
