APP_NAME = "AZ Turf Pro"

VERSION = "1.0"

# Dossier utilisÃ© par le module export_pdf.py pour enregistrer les PDF gÃ©nÃ©rÃ©s.
# Le chemin est relatif au dossier backend, quel que soit le rÃ©pertoire
# depuis lequel Uvicorn dÃ©marre l'application.
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / "exports"
