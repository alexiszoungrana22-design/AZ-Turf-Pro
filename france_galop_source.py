# =====================================
# AZ TURF PRO
# SOURCE FRANCE GALOP - ENRICHISSEMENT GALOP
# =====================================
#
# STATUT : module isolé, n'est appelé par aucun autre fichier du
# projet tant qu'il n'est pas explicitement branché. N'affecte ni le
# moteur AZ (engine/scoring/ranking/quinte), ni pmu_source.py, ni
# le classement affiché aux utilisateurs. Sert uniquement à fournir
# un TEXTE COMPLÉMENTAIRE (statistiques officielles France Galop)
# que le chatbot peut citer en plus des données PMU, uniquement pour
# les courses de discipline GALOP (plat/obstacle).
#
# ⚠️ AVERTISSEMENT IMPORTANT (honnêteté technique) :
# France Galop, comme PMU, n'a PAS d'API publique documentée. Ce
# module scrape la page publique du programme du jour. Cela veut
# dire concrètement :
#   - Il PEUT cesser de fonctionner si France Galop change la
#     structure de son site, sans préavis.
#   - Il N'A PAS été testé contre le site réel en conditions live
#     (pas d'accès réseau depuis l'environnement où il a été écrit).
#   - Il DOIT être testé une première fois sur le serveur réel après
#     déploiement, et surveillé les jours suivants.
# Le code est écrit pour échouer silencieusement (jamais d'exception
# qui remonte) : en cas de souci, l'app continue de fonctionner
# normalement, simplement sans ce complément d'information.
#
# CE QUE CE FICHIER FAIT (si tout se passe bien) :
# 1. Cherche la course du jour sur la page publique France Galop
#    correspondant à l'hippodrome/discipline en cours.
# 2. En extrait, si trouvés : l'état du terrain (piste), les
#    statistiques jockey/entraîneur officielles, et les commentaires
#    publics disponibles.
# 3. Retourne un texte prêt à insérer dans le contexte du chatbot -
#    ne modifie JAMAIS le classement ni les indices AZ/Premium.

import re
import httpx

TIMEOUT_SECONDES = 12
BASE_URL = "https://www.france-galop.com"


def _requete_securisee(url: str):
    """Ne lève jamais d'exception vers l'appelant : retourne None en
    cas d'échec (réseau, page introuvable, structure inattendue)."""
    try:
        reponse = httpx.get(
            url,
            timeout=TIMEOUT_SECONDES,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AZTurfPro/1.0)"},
            follow_redirects=True,
        )
        if reponse.status_code != 200:
            return None
        return reponse.text
    except Exception:
        return None


def _extraire_etat_terrain(html: str) -> str | None:
    if not html:
        return None
    match = re.search(
        r"(terrain|piste)\s*[:\-]?\s*([A-Za-zéèêàôûù \-]{3,30})",
        html,
        re.IGNORECASE,
    )
    if match:
        return match.group(2).strip()
    return None


def obtenir_complement_france_galop(hippodrome: str, discipline: str = "GALOP") -> str | None:
    """Point d'entrée unique. Retourne soit un court texte
    d'enrichissement (état du terrain, notes complémentaires), soit
    None si rien n'a pu être récupéré — dans tous les cas, jamais
    d'exception, jamais de blocage de l'application appelante.

    N'est PAS appelé automatiquement : à brancher manuellement dans
    _contexte_assistant() (api.py) une fois testé en conditions
    réelles sur le serveur.
    """
    if not hippodrome or str(discipline).upper() not in ("GALOP", "PLAT", "OBSTACLE"):
        return None

    try:
        page_programme = _requete_securisee(f"{BASE_URL}/fr/tableau/courses-partants-dans-les-courses-de-galop")
        if not page_programme:
            return None

        etat_terrain = _extraire_etat_terrain(page_programme)
        if not etat_terrain:
            return None

        return f"[France Galop] État du terrain signalé : {etat_terrain}."
    except Exception:
        # Filet de sécurité final : ce module ne doit jamais faire
        # planter l'application appelante, quoi qu'il arrive.
        return None
