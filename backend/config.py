APP_NAME = "AZ Turf Pro"

VERSION = "1.0"

# Dossier utilisé par le module export_pdf.py pour enregistrer les PDF générés.
# Le chemin est relatif au dossier backend, quel que soit le répertoire
# depuis lequel Uvicorn démarre l'application.
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / "exports"
