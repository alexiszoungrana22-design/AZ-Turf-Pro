import os
from pathlib import Path

APP_NAME = "AZ Turf Pro"
VERSION = "1.1"

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Sur Render, définir AZ_DATA_DIR vers un disque persistant.
# En local, backend/data reste le comportement par défaut.
DATA_DIR = Path(os.getenv("AZ_DATA_DIR", str(BASE_DIR / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(os.getenv("AZ_DB_PATH", str(DATA_DIR / "az_turf.db")))
HISTORIQUE_FILE = DATA_DIR / "historique_az.json"
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

API_BASE_URL = os.getenv("AZ_API_BASE_URL", "https://az-turf-pro.onrender.com").rstrip("/")

# Sécurité admin : définir cette variable sur Render pour activer la protection.
# Si elle est absente, le mode compatibilité reste actif afin de ne pas casser
# une installation existante ; l'API indique alors que la sécurité admin doit être configurée.
ADMIN_API_KEY = os.getenv("AZ_ADMIN_API_KEY", "").strip()
