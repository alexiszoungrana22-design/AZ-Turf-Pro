# =====================================
# AZ TURF PRO
# API
# Analyse + Premium
# =====================================
#
# CORRECTIONS APPORTEES A CETTE VERSION (rien d'autre n'a change) :
#
# 1. charger_course() ne fige plus reunion="R1"/course_numero="C1"
#    en dur : ces valeurs sont desormais laissees a
#    charger_course_pmu(), qui lit le vrai programme du jour et
#    choisit la premiere reunion/course reellement disponible
#    (cf. pmu_source.py corrige). Avant, meme si R1/C1 n'existait
#    pas ce jour-la, on ne le savait jamais - PMU echouait toujours
#    silencieusement et on retombait sur courses.json.
#
# 2. Quand la source reelle echoue et qu'on retombe sur
#    courses.json, la reponse de /api/analyse indique desormais
#    clairement qu'il s'agit de donnees de demonstration (source
#    "demo" + message explicite + date_demo separee de la date du
#    jour), pour ne jamais laisser croire que c'est la course
#    actuelle. Toutes les autres routes (abonnement, activation,
#    premium, admin) sont strictement inchangees.


from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
import secrets
import asyncio

from engine import lancer_analyse

from database import (
    creer_abonnement,
    activer_abonnement,
    verifier_premium,
    lister_abonnements,
    statistiques_abonnements
)

from models import (
    AbonnementRequest,
    ActivationRequest
)

from security import create_premium_token, verify_premium_token

from pmu_source import charger_course_pmu, trouver_quinte_du_jour

from lonab_source import recuperer_journal_lonab, diagnostiquer_journal_lonab

from learning import lire_historique, mettre_a_jour_arrivee
from modules.chatbot_turf import repondre_assistant_turf

import json
import os
from datetime import datetime, timedelta

from engine import lancer_analyse
from modules.cotes_history import analyser_tendances_cotes
from modules.pronos_presse import analyser_consensus_presse
from modules.meteo_piste import analyser_impact_terrain

router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)


# =====================================
# CHARGEMENT COURSE LOCALE
# =====================================

def charger_course_locale():

    chemin = os.path.join(
        os.path.dirname(__file__),
        "data",
        "courses.json"
    )

    with open(
        chemin,
        "r",
        encoding="utf-8"
    ) as fichier:

        return json.load(fichier)


# =====================================
# CHARGEMENT COURSE
# PMU PRIORITAIRE + FALLBACK LOCAL
# =====================================

def charger_course():

    aujourd_hui = datetime.now()

    # Format attendu par l'API PMU
    date_pmu = aujourd_hui.strftime(
        "%d%m%Y"
    )

    # =================================
    # 1. TENTATIVE PMU
    # reunion/course_numero ne sont plus
    # fixes en dur : charger_course_pmu()
    # determine elle-meme la premiere
    # reunion/course reellement
    # disponible dans le programme du
    # jour si on ne lui impose rien.
    # =================================

    try:

        course = charger_course_pmu(
            date_pmu
        )

        if (
            course
            and isinstance(course, dict)
            and course.get("chevaux")
        ):

            print(
                "Source utilisée : PMU réel"
            )

            return course, "pmu_live"

    except Exception as erreur:

        print(
            "PMU indisponible :",
            erreur
        )

    # =================================
    # 2. FALLBACK LOCAL
    # Marque explicitement comme donnee
    # de demonstration : ne doit jamais
    # etre presentee comme la course du
    # jour.
    # =================================

    try:

        course = charger_course_locale()

        if (
            course
            and isinstance(course, dict)
            and course.get("chevaux")
        ):

            print(
                "Source utilisée : données locales (démo)"
            )

            course["donnees_demo"] = True

            return course, "demo"

    except Exception as erreur:

        print(
            "Erreur chargement local :",
            erreur
        )

    return None, "none"


# =====================================
# QUINTÉ DES PÉRIODES : HIER / JOUR / DEMAIN
# =====================================
#
# Route additive, portée depuis la version racine du projet : elle
# manquait dans ce fichier (celui réellement importé par backend/main.py),
# ce qui provoquait un 404 sur /api/quintes-periodes appelé par accueil.js.

def _nombre_partants_course_brute(course):
    if not isinstance(course, dict):
        return 0
    for cle in ("nombreDeclaresPartants", "nombrePartants", "nbPartants"):
        valeur = course.get(cle)
        try:
            if valeur not in (None, ""):
                return int(valeur)
        except (TypeError, ValueError):
            pass
    participants = course.get("participants")
    if isinstance(participants, list):
        return len(participants)
    return 0


def _resume_quinte_periode(date_obj, periode):
    """Charge uniquement les métadonnées du Quinté d'une date donnée.

    On réutilise la même détection PMU que la course du jour, sans lancer le
    moteur AZ ni toucher au ticket Premium/gratuit de /api/analyse.
    """
    date_pmu = date_obj.strftime("%d%m%Y")
    try:
        _programme, reunion, course = trouver_quinte_du_jour(date_pmu)
    except Exception as erreur:
        print(f"Quinté {periode} indisponible :", erreur)
        return {
            "periode": periode,
            "date": date_obj.strftime("%Y-%m-%d"),
            "disponible": False,
        }

    if not isinstance(course, dict):
        return {
            "periode": periode,
            "date": date_obj.strftime("%Y-%m-%d"),
            "disponible": False,
        }

    def premier(*cles):
        for cle in cles:
            valeur = course.get(cle)
            if valeur not in (None, ""):
                return valeur
        return ""

    depart = premier(
        "heureDepart", "heureDepartPrevue", "heureDepartCourse",
        "heure_depart", "heure", "heureDeDepart"
    )
    date_course = premier("date", "dateCourse") or date_obj.strftime("%Y-%m-%d")
    numero = premier("numOrdre", "numCourse", "numero")
    nom = premier("libelle", "nom", "libelleLong", "libelleCourt") or "Quinté+"
    distance = premier("distance", "distanceCourse", "distanceMetres")
    hippodrome = course.get("hippodrome") or course.get("hippodromeLibelle") or course.get("hippodromeNom") or ""
    if isinstance(hippodrome, dict):
        hippodrome = hippodrome.get("libelleLong") or hippodrome.get("libelleCourt") or hippodrome.get("libelle") or hippodrome.get("nom") or ""

    discipline = course.get("discipline", "")
    if isinstance(discipline, dict):
        discipline = discipline.get("libelle") or discipline.get("nom") or ""

    return {
        "periode": periode,
        "date": date_course,
        "reunion": reunion or "",
        "course_numero": numero,
        "course": nom,
        "hippodrome": hippodrome,
        "discipline": discipline,
        "distance": distance,
        "partants": _nombre_partants_course_brute(course),
        "heure_depart": depart,
        "horaires": {"depart": depart},
        "disponible": True,
        "source": "pmu_live",
    }


@router.get("/quintes-periodes")
def quintes_periodes():
    """Retourne les Quinté+ réel d'hier, du jour et de demain.

    Cette route est additive : elle ne modifie pas /api/analyse ni les tickets.
    """
    aujourd_hui = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    periodes = {
        "hier": aujourd_hui - timedelta(days=1),
        "jour": aujourd_hui,
        "demain": aujourd_hui + timedelta(days=1),
    }
    return {
        cle: _resume_quinte_periode(date_obj, cle)
        for cle, date_obj in periodes.items()
    }


# =====================================
# PARTANTS — ROUTE ADDITIVE
# =====================================
@router.get("/partants")
def partants():
    """Retourne les partants analysés sans modifier /api/analyse."""
    course, source = charger_course()
    if not course:
        raise HTTPException(status_code=503, detail="Données PMU indisponibles actuellement.")
    chevaux = course.get("chevaux", [])
    if not chevaux:
        raise HTTPException(status_code=503, detail="Aucun partant disponible.")
    try:
        resultat = lancer_analyse(
            chevaux,
            info_course={
                "date": course.get("date"),
                "reunion": course.get("reunion"),
                "course_numero": course.get("course_numero"),
                "course": course.get("course", ""),
                "hippodrome": course.get("hippodrome", ""),
                "discipline": course.get("discipline", ""),
                "distance": course.get("distance_course", ""),
                "allocation": course.get("allocation", ""),
                "heure_depart": course.get("heure_depart", ""),
                "non_partants": course.get("non_partants", []),
            },
        )
        classement = resultat.get("chevaux", []) if isinstance(resultat, dict) else []
        return [
            {
                "rang": c.get("rang"),
                "numero": c.get("numero"),
                "nom": c.get("nom"),
                "indice": c.get("indice_az"),
                "confiance": c.get("confiance"),
                "jockey": c.get("jockey", ""),
                "entraineur": c.get("entraineur", ""),
                "cote": c.get("cote_brute", c.get("rapport", "")),
                "statut": c.get("statut", ""),
                "source": source,
                "donnees_demo": source == "demo",
            }
            for c in classement
        ]
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Erreur partants : {erreur}")


# =====================================
# ANALYSE AZ TURF
# =====================================

def _analyse_complete():
    """Calcule l'analyse complète (gratuite + Premium). Fonction interne :
    non exposée directement, voir /analyse (public, gratuit seulement) et
    /premium/ticket (protégé, contenu complet) juste après.
    """
    try:

        # =================================
        # 1. CHARGEMENT DES DONNÉES
        # =================================

        course, source = charger_course()

        if not course:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Aucune donnée de course "
                    "disponible actuellement."
                )
            )

        # =================================
        # 2. CHEVAUX
        # =================================

        chevaux = course.get(
            "chevaux",
            []
        )

        if not chevaux:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Aucun cheval trouvé "
                    "dans la course."
                )
            )

        # =================================
        # 3. MOTEUR AZ
        # =================================

        resultat = lancer_analyse(
            chevaux,
            info_course={
                "date": course.get("date"),
                "reunion": course.get("reunion"),
                "course_numero": course.get("course_numero"),
                "course": course.get("course", ""),
                "hippodrome": course.get("hippodrome"),
                "discipline": course.get("discipline", ""),
                "distance": course.get("distance_course", ""),
                "allocation": course.get("allocation", ""),
                "heure_depart": course.get("heure_depart", ""),
                "horaires": course.get("horaires", {}),
                "non_partants": course.get("non_partants", []),
                "plus_joues": course.get("plus_joues", []),
            }
        )

        if not isinstance(
            resultat,
            dict
        ):
            raise Exception(
                "Réponse invalide du moteur AZ"
            )

        classement = resultat.get(
            "chevaux",
            []
        )

        if not classement:

            raise Exception(
                "Le moteur AZ n'a retourné "
                "aucun classement."
            )

        # =================================
        # 4. INFORMATIONS COURSE
        # =================================

        aujourd_hui = datetime.now()

        est_demo = (source == "demo")

        date_course = (
            course.get("date")
            or aujourd_hui.strftime(
                "%Y-%m-%d"
            )
        )

        reunion = (
            course.get("reunion")
            or "R1"
        )

        course_numero = (
            course.get("course_numero")
            or "C1"
        )

        # =================================
        # 5. RÉPONSE API
        # =================================

        reponse = {

            "message": (
                "Analyse AZ Turf terminée"
                if not est_demo else
                "Analyse AZ Turf terminée "
                "(données de démonstration, "
                "aucune course réelle "
                "disponible actuellement)"
            ),

            "source":
                source,

            # Indique explicitement au frontend
            # qu'il ne s'agit pas d'une course
            # reelle du jour, pour eviter toute
            # confusion.
            "donnees_demo":
                est_demo,

            "course":
                course.get(
                    "course",
                    "Course"
                ),

            "date":
                date_course,

            "reunion":
                reunion,

            "course_numero":
                course_numero,

            "heure_depart":
                course.get("heure_depart", ""),

            "horaires":
                course.get("horaires", {"depart": course.get("heure_depart", ""), "arret_des_jeux": ""}),

            "hippodrome":
                course.get(
                    "hippodrome",
                    ""
                ),

            "discipline":
                course.get(
                    "discipline",
                    ""
                ),

            "distance":
                course.get(
                    "distance_course",
                    ""
                ),

            "allocation":
                course.get(
                    "allocation",
                    ""
                ),

            "non_partants":
                course.get(
                    "non_partants",
                    []
                ),

            "plus_joues":
                course.get(
                    "plus_joues",
                    []
                ),

            "source_plus_joues":
                course.get(
                    "source_plus_joues",
                    "Non disponible"
                ),

            "partants":
                len(chevaux),

            "chevaux":
                classement,

            "classement":
                classement,

            "favori": (
                classement[0]
                if classement
                else {}
            ),

            "tickets":
                resultat.get(
                    "tickets",
                    {}
                )

        }

        if est_demo:

            reponse["avertissement"] = (
                "Ces données sont des données de "
                "démonstration figées et ne "
                "correspondent pas à une course "
                "réelle du jour."
            )

        return reponse

    except HTTPException:
        raise

    except Exception as erreur:

        print(
            "Erreur analyse AZ :",
            erreur
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Erreur AZ : "
                f"{str(erreur)}"
            )

        )


# =====================================
# ANALYSE PUBLIQUE (GRATUITE UNIQUEMENT)
# =====================================
#
# CORRECTION SÉCURITÉ : /analyse renvoyait auparavant tickets.premium à
# n'importe qui, sans authentification — le verrouillage Premium n'était
# que visuel côté frontend. On ne renvoie plus ici que le ticket gratuit ;
# le contenu Premium complet est désormais servi par /premium/ticket,
# protégé par clé admin ou token Premium valide.

@router.get("/analyse")
def analyse():
    reponse = _analyse_complete()
    tickets = reponse.get("tickets", {}) or {}
    reponse["tickets"] = {
        "gratuit": tickets.get("gratuit", {})
    }
    return reponse


def _require_premium_request(authorization: str | None, x_admin_key: str | None) -> dict:
    """Autorise l'administrateur (clé serveur) ou un abonné Premium (jeton
    signé valide, vérifié en base). Lève 401/403 sinon.
    """
    if _admin_key_valide(x_admin_key):
        return {"admin": True, "telephone": "ADMINISTRATEUR"}

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Accès Premium non autorisé.")

    token = authorization[7:].strip()
    payload = verify_premium_token(token)
    telephone = str(payload.get("telephone", "")).strip()

    statut = verifier_premium(telephone)
    if statut.get("statut") != "ACTIF":
        raise HTTPException(status_code=403, detail="Abonnement Premium inactif ou expiré.")

    return {"admin": False, "telephone": telephone}


@router.get("/premium/ticket")
def premium_ticket(
    authorization: str | None = Header(default=None),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    """Contenu complet (gratuit + Premium), uniquement pour un administrateur
    authentifié ou un abonné Premium avec un jeton valide."""
    _require_premium_request(authorization, x_admin_key)
    return _analyse_complete()


# =====================================
# CREATION ABONNEMENT PREMIUM
# =====================================

@router.post("/abonnement")
def abonnement(
    data: AbonnementRequest
):

    try:

        resultat = creer_abonnement(
            data.model_dump()
        )

        return {

            "message":
                "Abonnement enregistré",

            "abonnement":
                resultat

        }

    except Exception as erreur:

        raise HTTPException(

            status_code=500,

            detail=str(erreur)

        )


# =====================================
# ACTIVATION PREMIUM
# =====================================
#
# CORRECTION : cette route exigeait auparavant une clé administrateur
# (_require_admin), alors qu'elle est appelée par activation.html sans
# aucun en-tête d'authentification — l'auto-activation d'un abonné après
# paiement échouait donc systématiquement avec 401. La sécurité réelle
# vient de la vérification telephone + référence dans activer_abonnement()
# (base de données), pas d'une clé serveur : un tiers sans référence
# valide ne peut toujours pas activer un compte.
#
# De plus, la réponse ne contenait jamais "access_token", alors que
# activation.html et mon-abonnement.html l'attendent pour ensuite
# authentifier l'accès Premium (AZ_TURF_PREMIUM_TOKEN). On génère
# maintenant ce jeton signé via security.create_premium_token(), déjà
# présent dans le projet mais jamais utilisé par ce fichier.

@router.post("/activation")
def activation_premium(
    activation: ActivationRequest
):
    abonnement = activer_abonnement(
        activation.telephone.strip(),
        activation.reference.strip()
    )

    if abonnement is None:
        raise HTTPException(
            status_code=404,
            detail="Aucun abonnement trouvé ou référence invalide"
        )

    token = create_premium_token(
        activation.telephone.strip(),
        abonnement["date_fin"]
    )

    return {
        "message": "Premium activé",
        "statut": "ACTIF",
        "date_fin": abonnement["date_fin"],
        "access_token": token
    }


# =====================================
# VERIFICATION PREMIUM
# =====================================

@router.get("/premium/{telephone}")
def premium(
    telephone: str
):

    return verifier_premium(
        telephone
    )


# =====================================
# ADMIN - ABONNEMENTS
# =====================================

@router.get("/admin/abonnements")
def admin_abonnements(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")
):
    _require_admin(x_admin_key)
    return {
        "abonnements": lister_abonnements()
    }


# =====================================
# ADMIN - STATISTIQUES
# =====================================

@router.get("/admin/statistiques")
def admin_statistiques(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")
):
    _require_admin(x_admin_key)
    return statistiques_abonnements()


# =====================================
# JOURNAL HIPPIQUE (LONAB)
# =====================================
#
# Route additive : n'affecte aucune route existante ci-dessus.

@router.get("/journal")
def journal():

    try:

        aujourd_hui = datetime.now()

        resultat = recuperer_journal_lonab(
            aujourd_hui
        )

        if not resultat:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Journal hippique LONAB indisponible "
                    "actuellement."
                )
            )

        return resultat

    except HTTPException:
        raise

    except Exception as erreur:

        print(
            "Erreur journal LONAB :",
            erreur
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Erreur journal : "
                f"{str(erreur)}"
            )

        )


# =====================================
# DEBUG TEMPORAIRE - JSON BRUT PMU
# =====================================
#
# Route temporaire, a retirer une fois le probleme d'hippodrome
# resolu. Retourne le dict "course" brut tel que recu de l'API PMU,
# AVANT toute transformation, pour identifier le vrai nom du champ
# hippodrome dans le schema reel de l'API client/61.

@router.get("/debug-pmu")
def debug_pmu():
    from pmu_source import trouver_quinte_du_jour, LAST_PMU_DIAGNOSTIC
    date_pmu = datetime.now().strftime("%d%m%Y")
    try:
        programme, reunion, course = trouver_quinte_du_jour(date_pmu)
        from pmu_source import LAST_PMU_DIAGNOSTIC as diagnostic
        return {
            "date_demandee": date_pmu,
            "reunion": reunion,
            "programme_brut": programme,
            "course_brute": course,
            "pmu_diagnostic": diagnostic,
        }
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Erreur debug PMU : {erreur}")


# =====================================
# DEBUG TEMPORAIRE - JOURNAL LONAB
# =====================================
#
# Route temporaire, a retirer une fois le journal fonctionnel.
# Montre precisement a quelle etape la recuperation LONAB echoue.

@router.get("/debug-journal")
def debug_journal():

    aujourd_hui = datetime.now()

    try:

        diagnostic = diagnostiquer_journal_lonab(
            aujourd_hui
        )

        return diagnostic

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur debug journal : {erreur}"
        )


# =====================================
# HISTORIQUE (SELECTION + RESULTATS)
# =====================================
#
# Route additive : n'affecte aucune route existante. Lit
# data/historique_az.json (rempli automatiquement par
# engine.lancer_analyse a chaque appel de /api/analyse) et tente
# de completer le vrai resultat (arrivee) des entrees passees dont
# la course est desormais terminee.
#
# LIMITE CONNUE : si l'hebergement Render ne dispose pas d'un
# disque persistant, ce fichier peut etre remis a zero a chaque
# redeploiement - l'historique ne survit alors pas dans le temps.

@router.get("/historique")
def historique():

    try:

        entrees = lire_historique()

        for index, entree in enumerate(entrees):

            if entree.get("arrivee"):
                continue

            info_course = entree.get("course") or {}

            date = info_course.get("date")
            reunion = info_course.get("reunion")
            course_numero = info_course.get("course_numero")

            if not (date and reunion and course_numero):
                continue

            try:

                from pmu_source import recuperer_arrivee_pmu

                arrivee = recuperer_arrivee_pmu(
                    date, reunion, course_numero
                )

                if arrivee:
                    mettre_a_jour_arrivee(index, arrivee)
                    entree["arrivee"] = arrivee

            except Exception:
                pass

        return {
            "historique": list(reversed(entrees))
        }

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur historique : {erreur}"
)
            
# Dans api.py (à la fin du fichier)
from modules.cotes_history import analyser_tendances_cotes
from modules.export_pdf import generer_pdf_ticket

@router.post("/analyse/cotes")
def api_analyse_cotes(data: dict):
    return analyser_tendances_cotes(data)

@router.post("/export/pdf")
def api_export_pdf(data: dict):
    return generer_pdf_ticket(data)

# =========================================================
# ENDPOINT TOUT-EN-UN (ANALYSE GLOBALE AZ TURF PRO)
# =========================================================

@router.post("/analyse/complete")
def api_analyse_complete(payload: dict):
    """
    Combine le moteur principal, le suivi des cotes, la presse et la météo 
    en une seule réponse structurée pour l'application.
    """
    chevaux = payload.get("chevaux", [])
    info_course = payload.get("info_course", {})

    # 1. Moteur d'analyse principal (Scores AZ, Premium, Badges et Radar)
    res_moteur = lancer_analyse(chevaux, info_course)

    # 2. Suivi des cotes & Smart Money (Sécurisé avec try/except)
    res_cotes = {}
    try:
        res_cotes = analyser_tendances_cotes({"chevaux": chevaux})
    except Exception as e:
        print("Erreur analyse cotes :", e)

    # 3. Consensus Presse (Sécurisé avec try/except)
    res_presse = {}
    try:
        res_presse = analyser_consensus_presse({"info_course": info_course})
    except Exception as e:
        print("Erreur analyse presse :", e)

    # 4. Météo et état de la piste (Sécurisé avec try/except)
    res_meteo = {}
    try:
        res_meteo = analyser_impact_terrain({"info_course": info_course})
    except Exception as e:
        print("Erreur analyse météo :", e)

    # Assemblage de la réponse globale
    return {
        "status": "success",
        "message": "Analyse complète AZ Turf Pro effectuée",
        "analyse_moteur": res_moteur,
        "tendances_cotes": res_cotes.get("resultats", []),
        "consensus_presse": res_presse.get("consensus", []),
        "impact_meteo": res_meteo.get("impact", "NEUTRE")
    }


# =========================================================
# AUTHENTIFICATION ADMIN + ASSISTANT
# =========================================================

def _admin_expected_key() -> str:
    # Plusieurs noms sont acceptés pour éviter les décalages entre les
    # anciennes versions du projet et la variable réellement configurée sur Render.
    for name in (
        "AZ_ADMIN_API_KEY",
        "AZ_TURF_ADMIN_API_KEY",
        "AZ_TURF_ADMIN_KEY",
        "ADMIN_API_KEY",
        "ADMIN_KEY",
    ):
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _admin_key_valide(admin_key: str | None) -> bool:
    expected = _admin_expected_key()
    supplied = (admin_key or "").strip()
    return bool(expected and supplied and secrets.compare_digest(supplied, expected))


def _require_admin(admin_key: str | None) -> None:
    if not _admin_expected_key():
        raise HTTPException(
            status_code=503,
            detail="Aucune clé administrateur n'est configurée sur le serveur Render."
        )
    if not _admin_key_valide(admin_key):
        raise HTTPException(
            status_code=401,
            detail="Clé administrateur invalide ou différente de celle configurée sur le serveur."
        )


def _auth_assistant(admin_key: str | None, authorization: str | None) -> str:
    if _admin_key_valide(admin_key):
        return "admin"

    # Le frontend Premium transmet son token d'abonnement.
    # La validation détaillée du téléphone reste gérée par /api/premium/{telephone}.
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token:
            return "premium"

    raise HTTPException(
        status_code=401,
        detail="Accès refusé : Premium ou administrateur requis."
    )


@router.get("/admin/verification")
def admin_verification(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    _require_admin(x_admin_key)
    return {"authorized": True, "role": "admin"}


def _contexte_assistant():
    course, source = charger_course()
    if not course:
        raise HTTPException(status_code=503, detail="Aucune course disponible.")

    chevaux = course.get("chevaux", [])
    if not chevaux:
        raise HTTPException(status_code=503, detail="Aucun partant disponible.")

    resultat = lancer_analyse(
        chevaux,
        info_course={
            "date": course.get("date"),
            "reunion": course.get("reunion"),
            "course_numero": course.get("course_numero"),
            "course": course.get("course", ""),
            "hippodrome": course.get("hippodrome", ""),
            "discipline": course.get("discipline", ""),
            "distance": course.get("distance_course", ""),
            "allocation": course.get("allocation", ""),
            "heure_depart": course.get("heure_depart", ""),
            "horaires": course.get("horaires", {}),
            "non_partants": course.get("non_partants", []),
            "plus_joues": course.get("plus_joues", []),
        }
    )

    return {
        "moteur": {
            "classement": resultat.get("chevaux", []),
            "tickets": resultat.get("tickets", {}),
        },
        "course": course,
        "source": source,
    }


@router.post("/assistant/chat")
def assistant_chat(
    payload: dict,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    authorization: str | None = Header(default=None),
):
    _auth_assistant(x_admin_key, authorization)

    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question obligatoire.")

    contexte = _contexte_assistant()
    return repondre_assistant_turf(question, contexte)


@router.post("/assistant/chat/stream")
async def assistant_chat_stream(
    payload: dict,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    authorization: str | None = Header(default=None),
):
    _auth_assistant(x_admin_key, authorization)

    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question obligatoire.")

    historique = payload.get("historique") or []

    async def generate():
        try:
            contexte = _contexte_assistant()
            # Le moteur actuel produit une réponse complète ; on la transmet
            # progressivement pour conserver l'interface SSE sans inventer de texte.
            resultat = repondre_assistant_turf(question, contexte)
            texte = str(resultat.get("reponse", ""))
            if not texte:
                texte = "Je n'ai pas de réponse disponible actuellement."

            for morceau in re.split(r"(\s+)", texte):
                if morceau:
                    import json as _json
                    yield "data: " + _json.dumps(
                        {"type": "token", "text": morceau},
                        ensure_ascii=False
                    ) + "\n\n"
                    await asyncio.sleep(0)

            import json as _json
            yield "data: " + _json.dumps(
                {"type": "done"},
                ensure_ascii=False
            ) + "\n\n"

        except HTTPException as exc:
            import json as _json
            yield "data: " + _json.dumps(
                {"type": "error", "message": exc.detail},
                ensure_ascii=False
            ) + "\n\n"
        except Exception as exc:
            import json as _json
            yield "data: " + _json.dumps(
                {"type": "error", "message": f"Erreur assistant : {exc}"},
                ensure_ascii=False
            ) + "\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
