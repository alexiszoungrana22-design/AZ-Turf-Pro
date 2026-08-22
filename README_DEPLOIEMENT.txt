AZ Turf Pro v24.5 - correctif de structure backend

IMPORTANT : ton Render lance : uvicorn main:app ... depuis le dossier backend.
Le fichier api.py importe chatbot_turf depuis le même dossier backend.

Remplacer dans le dépôt :
  backend/api.py
  backend/chatbot_turf.py
  chatbot.js (si tu veux appliquer aussi le correctif interface)

NE PAS mettre chatbot_turf.py à la racine du dépôt.

Après commit/push, Render doit pouvoir importer :
  from api import router
  from chatbot_turf import repondre_assistant_turf

Contrôle attendu au démarrage : aucune erreur ModuleNotFoundError: No module named 'chatbot_turf'.
