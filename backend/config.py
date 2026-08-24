import os

APP_NAME = "AZ Turf Pro"
VERSION = "1.0"

# Secret d'administration fourni uniquement par l'environnement serveur.
# Ne jamais mettre cette valeur dans le frontend ou dans Git.
ADMIN_API_KEY = os.getenv("AZ_ADMIN_API_KEY", "").strip()
# Secret de signature des jetons d'accès Premium. Obligatoire côté serveur.
PREMIUM_ACCESS_SECRET = os.getenv("AZ_PREMIUM_ACCESS_SECRET", "").strip()
