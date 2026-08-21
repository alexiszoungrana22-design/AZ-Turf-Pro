# AZ Turf Pro — Assistant Chatbot autonome PMU v24

Cette version conserve l'interface existante et renforce le moteur du chatbot.

## Fichiers
- `api.py` : endpoints assistant, recherche de courses futures, authentification admin/Premium.
- `chatbot_turf.py` : moteur conversationnel PMU, tickets IA indépendants, scoring multi-critères, connaissances PMU, mémoire de courses.
- `chatbot.js` : mémoire conversationnelle, accueil personnalisé, prénom si disponible, streaming existant conservé.

## Variables Render
- `AZ_ADMIN_API_KEY` : clé administrateur déjà utilisée par AZ Turf Pro.
- `AZ_TURF_PREMIUM_TOKEN` : token Premium serveur si ce mécanisme est utilisé.

## Capacités ajoutées
- conversation naturelle : bonjour / merci / ça va / d'accord ;
- questions générales PMU ;
- ticket IA indépendant d'AZ Turf Pro ;
- modes prudent / équilibré / spéculatif / Value ;
- scoring forme, régularité, aptitude, jockey, gains, expérience et cote ;
- recherche de courses à venir via le programme PMU ;
- rappel d'une course mémorisée et de son arrivée si disponible ;
- réponses sans invention lorsqu'une donnée PMU n'est pas disponible ;
- streaming SSE conservé.

## Déploiement
Remplacer les fichiers correspondants dans le projet. Ne pas remplacer le HTML de l'interface actuelle.
