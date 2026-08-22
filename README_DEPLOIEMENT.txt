AZ Turf Pro — correction réelle du chatbot v24.4

Fichiers à remplacer :
1. api.py
2. chatbot_turf.py
3. chatbot.js

Corrections :
- ajout réel des routes POST /api/assistant/chat et /api/assistant/chat/stream
- accès administrateur via X-Admin-Key avec AZ_ADMIN_API_KEY côté Render
- génération et vérification d'un access_token Premium lors de l'activation
- salutations accessibles sans Premium
- analyse ciblée d'un cheval (ex. « Comment tu trouves le 8 ? »)
- historique de conversation transmis au moteur
- récupération PMU conservée

Important : sur Render, définir AZ_ADMIN_API_KEY avec la même clé que celle saisie dans l'administration.
Après remplacement, redéployer le service backend.
