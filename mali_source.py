# =====================================
# AZ TURF PRO
# SOURCE PMU MALI
# =====================================
#
# STATUT : module isole, appele uniquement par les nouvelles routes
# /api/pdf/... de api.py. N'affecte ni pmu_source.py, ni
# lonab_source.py, ni le moteur AZ.
#
# SOURCE VERIFIEE EN DIRECT : https://pmu.malijet.com
# (en partenariat avec Malijet.com - PMU officiel du Mali). Page de
# listing testee avec succes, structure confirmee :
# "detail-du-programme-du-DD_MM_YYYY-<id>.html"
#
# LIMITE ASSUMEE : contrairement a LONAB, cette source ne publie
# pas de PDF telechargeable - ce sont des pages HTML de detail par
# course. Cette fonction retrouve donc le LIEN de la page du jour,
# pas un fichier PDF.


import re
import requests


MALI_LISTING_URL = "https://pmu.malijet.com/liste-programmes-pmu-mali.html"

TIMEOUT = 10

MOIS_FR_NUM = {
    1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06",
    7: "07", 8: "08", 9: "09", 10: "10", 11: "11", 12: "12",
}


def trouver_url_programme_mali_du_jour(date_obj):
    """
    Cherche, sur la page de listing PMU Mali, le lien de la fiche
    de programme correspondant a la date donnee (objet
    datetime.date ou datetime.datetime).

    Retourne l'URL absolue de la page, ou None si non trouvee.
    """

    libelle_date = (
        f"{date_obj.day:02d}_"
        f"{MOIS_FR_NUM[date_obj.month]}_"
        f"{date_obj.year}"
    )

    try:
        reponse = requests.get(
            MALI_LISTING_URL,
            timeout=TIMEOUT,
            headers={"User-Agent": "AZ-Turf-Pro/1.0"},
        )
        reponse.raise_for_status()
        html = reponse.text
    except Exception as erreur:
        print("Erreur page listing PMU Mali :", erreur)
        return None

    motif = re.compile(
        r'href="(https://pmu\.malijet\.com/'
        r"detail-du-programme-du-"
        + re.escape(libelle_date)
        + r'-\d+\.html)"'
    )

    trouve = motif.search(html)

    if not trouve:
        return None

    return trouve.group(1)
