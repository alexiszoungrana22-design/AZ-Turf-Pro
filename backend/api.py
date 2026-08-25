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


from fastapi import APIRouter, HTTPException, Request

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

from pmu_source import charger_course_pmu

from lonab_source import recuperer_journal_lonab, diagnostiquer_journal_lonab

from learning import lire_historique, mettre_a_jour_arrivee

import json
import os
import base64
import hashlib
import hmac
from datetime import datetime, timedelta, timezone

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
                "Source utilisÃ©e : PMU rÃ©el"
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
                "Source utilisÃ©e : donnÃ©es locales (dÃ©mo)"
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

@router.get("/analyse")
def analyse():

    try:

        # =================================
        # 1. CHARGEMENT DES DONNÃ‰ES
        # =================================

        course, source = charger_course()

        if not course:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Aucune donnÃ©e de course "
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
                    "Aucun cheval trouvÃ© "
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
                "RÃ©ponse invalide du moteur AZ"
            )

        classement = resultat.get(
            "chevaux",
            []
        )

        if not classement:

            raise Exception(
                "Le moteur AZ n'a retournÃ© "
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
        # 5. RÃ‰PONSE API
        # =================================

        reponse = {

            "message": (
                "Analyse AZ Turf terminÃ©e"
                if not est_demo else
                "Analyse AZ Turf terminÃ©e "
                "(donnÃ©es de dÃ©monstration, "
                "aucune course rÃ©elle "
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
                "Ces donnÃ©es sont des donnÃ©es de "
                "dÃ©monstration figÃ©es et ne "
                "correspondent pas Ã   une course "
                "rÃ©elle du jour."
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
                "Abonnement enregistrÃ©",

            "abonnement":
                resultat

        }

    except Exception as erreur:

        raise HTTPException(

            status_code=500,

            detail=str(erreur)

        )


# =====================================
# ACTIVATION PREMIUM ADMIN
# =====================================

@router.post("/activation")
def activation_premium(
    activation: ActivationRequest
):

    abonnement = activer_abonnement(

        activation.telephone,

        activation.reference

    )

    if abonnement is None:

        raise HTTPException(

            status_code=404,

            detail=
                "Aucun abonnement trouvÃ©"

        )

    abonnement["date_fin"] = (

        datetime.now()

        +

        timedelta(

            days=int(

                abonnement.get(
                    "duree",
                    30
                )

            )

        )

    ).isoformat()

    access_token = _creer_token_premium(
        activation.telephone,
        abonnement["date_fin"],
    )

    return {
        "message": "Premium activé",
        "statut": "ACTIF",
        "date_fin": abonnement["date_fin"],
        "access_token": access_token,
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
# ADMIN - VERIFICATION DE LA CLE
# =====================================

@router.get("/admin/verification")
def admin_verification(request: Request):
    """Vérifie la clé administrateur utilisée par le tableau de bord.

    La route existe explicitement pour éviter le 404 du frontend.
    La clé n'est jamais renvoyée dans la réponse.
    """
    configured_admin = _secret_admin()
    supplied_key = request.headers.get("X-Admin-Key", "").strip()

    if not configured_admin:
        raise HTTPException(
            status_code=503,
            detail="AZ_ADMIN_API_KEY n'est pas configurée sur le serveur."
        )

    if not supplied_key or not hmac.compare_digest(supplied_key, configured_admin):
        raise HTTPException(
            status_code=401,
            detail="Clé administrateur invalide ou absente."
        )

    return {
        "authorized": True,
        "admin": True,
        "statut": "ACTIF",
        "message": "Clé administrateur vérifiée."
    }


# =====================================
# ADMIN - ABONNEMENTS
# =====================================

@router.get("/admin/abonnements")
def admin_abonnements():

    return {

        "abonnements":
            lister_abonnements()

    }


# =====================================
# ADMIN - STATISTIQUES
# =====================================

@router.get("/admin/statistiques")
def admin_statistiques():

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

# =====================================
# AUTHENTIFICATION ASSISTANT
# =====================================


def _secret_admin():
    return os.getenv("AZ_ADMIN_API_KEY", "").strip()


def _secret_token():
    return os.getenv("AZ_PREMIUM_TOKEN_SECRET", "").strip() or _secret_admin()


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _creer_token_premium(telephone: str, date_fin: str) -> str:
    secret = _secret_token()
    if not secret:
        raise HTTPException(
            status_code=500,
            detail="AZ_ADMIN_API_KEY doit être configurée sur le serveur pour sécuriser l'accès Premium.",
        )
    payload = {
        "telephone": str(telephone),
        "exp": date_fin,
        "iat": datetime.now(timezone.utc).isoformat(),
    }
    raw = _b64url_encode(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(secret.encode("utf-8"), raw.encode("ascii"), hashlib.sha256).digest()
    return raw + "." + _b64url_encode(sig)


def _verifier_token_premium(token: str) -> bool:
    try:
        secret = _secret_token()
        if not secret or "." not in token:
            return False
        raw, signature = token.split(".", 1)
        expected = hmac.new(secret.encode("utf-8"), raw.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_encode(expected), signature):
            return False
        payload = json.loads(_b64url_decode(raw).decode("utf-8"))
        exp = datetime.fromisoformat(str(payload.get("exp")).replace("Z", "+00:00"))
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < exp
    except Exception:
        return False


def _assistant_auth(request: Request) -> bool:
    admin_key = request.headers.get("X-Admin-Key", "").strip()
    configured_admin = _secret_admin()
    if configured_admin and admin_key and hmac.compare_digest(admin_key, configured_admin):
        return True

    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return _verifier_token_premium(auth[7:].strip())

    return False


def _is_public_conversation(question: str) -> bool:
    q = str(question or "").lower().strip()
    q = q.replace("’", "'")
    return q in {
        "bonjour", "bonsoir", "salut", "hello", "coucou", "hey",
        "ça va", "ca va", "je vais bien", "je vais bien merci",
        "bien merci", "merci", "ok", "d'accord", "daccord", "super",
    }


# =====================================
# ASSISTANT CHATBOT PMU AUTONOME v24.4
# =====================================
from fastapi.responses import StreamingResponse
from chatbot_turf import repondre_assistant_turf


def _assistant_course_context():
    course, source = charger_course()
    if not course:
        return {"source": source, "chevaux": []}
    chevaux = course.get("chevaux", [])
    try:
        moteur = lancer_analyse(
            chevaux,
            {
                "date": course.get("date"),
                "reunion": course.get("reunion"),
                "course_numero": course.get("course_numero"),
                "course": course.get("course", ""),
                "hippodrome": course.get("hippodrome", ""),
                "discipline": course.get("discipline", ""),
                "distance": course.get("distance_course", ""),
                "heure_depart": course.get("heure_depart", ""),
            },
        )
    except Exception:
        moteur = {}
    return {
        "source": source,
        "course": course,
        "chevaux": chevaux,
        "moteur": moteur,
    }


def _assistant_historique():
    try:
        return list(reversed(lire_historique()))[-20:]
    except Exception:
        return []


@router.post("/assistant/chat")
def assistant_chat_v241(payload: dict, request: Request):
    """Assistant conversationnel PMU avec analyse IA indépendante."""
    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question obligatoire.")
    if not _is_public_conversation(question) and not _assistant_auth(request):
        raise HTTPException(status_code=401, detail="Accès réservé aux abonnés Premium ou à l'administrateur.")

    contexte = _assistant_course_context()
    contexte["historique_pmu"] = _assistant_historique()
    contexte["historique_conversation"] = payload.get("historique") or []
    contexte["prenom"] = payload.get("prenom") or payload.get("nom_utilisateur") or ""

    # Recherche automatique du Quinté d'une date future lorsque l'utilisateur le demande.
    q = question.lower()
    # Résultat demandé : tenter de récupérer l'arrivée officielle du Quinté de la veille.
    if any(k in q for k in ["arrivée d'hier", "arrivee d'hier", "résultat d'hier", "resultat d'hier"]):
        try:
            from pmu_source import trouver_quinte_du_jour, recuperer_arrivee_pmu, normaliser_date
            from datetime import datetime, timedelta
            date_hier = normaliser_date(datetime.now() - timedelta(days=1))
            _, r_hier, c_hier = trouver_quinte_du_jour(date_hier)
            if c_hier:
                numero_hier = c_hier.get("numOrdre") or c_hier.get("numCourse") or c_hier.get("numero")
                arrivee = recuperer_arrivee_pmu(date_hier, r_hier, numero_hier)
                if arrivee:
                    contexte["arrivee_recherchee"] = (
                        f"🏁 **Arrivée officielle PMU du {date_hier}**\\n\\n"
                        f"Course : **{r_hier}C{numero_hier}**\\n\\n"
                        f"**{' - '.join(map(str, arrivee))}**"
                    )
        except Exception as erreur:
            print("Assistant arrivée hier :", erreur)
    if any(k in q for k in ["demain", "à venir", "a venir", "prochaine course", "prochain quinté", "quinté de demain", "quinte de demain"]):
        from pmu_source import trouver_quinte_du_jour, normaliser_date
        from datetime import datetime, timedelta
        target_date = datetime.now() + timedelta(days=1)
        programme, reunion, course = trouver_quinte_du_jour(normaliser_date(target_date))
        if course:
            try:
                from pmu_source import charger_course_pmu
                future_course = charger_course_pmu(normaliser_date(target_date), reunion, course.get("numOrdre") or course.get("numCourse") or course.get("numero"))
                if future_course:
                    contexte["course"] = future_course
                    contexte["chevaux"] = future_course.get("chevaux", [])
                    contexte["source"] = "pmu_live_future"
            except Exception:
                pass

    resultat = repondre_assistant_turf(question, contexte)
    return resultat


@router.post("/assistant/chat/stream")
def assistant_chat_stream_v241(payload: dict, request: Request):
    """Version SSE du chatbot : un bloc de texte puis un événement final."""
    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question obligatoire.")
    if not _is_public_conversation(question) and not _assistant_auth(request):
        raise HTTPException(status_code=401, detail="Accès réservé aux abonnés Premium ou à l'administrateur.")

    contexte = _assistant_course_context()
    contexte["historique_pmu"] = _assistant_historique()
    contexte["historique_conversation"] = payload.get("historique") or []
    contexte["prenom"] = payload.get("prenom") or payload.get("nom_utilisateur") or ""

    q = question.lower()
    # Résultat demandé : tenter de récupérer l'arrivée officielle du Quinté de la veille.
    if any(k in q for k in ["arrivée d'hier", "arrivee d'hier", "résultat d'hier", "resultat d'hier"]):
        try:
            from pmu_source import trouver_quinte_du_jour, recuperer_arrivee_pmu, normaliser_date
            from datetime import datetime, timedelta
            date_hier = normaliser_date(datetime.now() - timedelta(days=1))
            _, r_hier, c_hier = trouver_quinte_du_jour(date_hier)
            if c_hier:
                numero_hier = c_hier.get("numOrdre") or c_hier.get("numCourse") or c_hier.get("numero")
                arrivee = recuperer_arrivee_pmu(date_hier, r_hier, numero_hier)
                if arrivee:
                    contexte["arrivee_recherchee"] = (
                        f"🏁 **Arrivée officielle PMU du {date_hier}**\\n\\n"
                        f"Course : **{r_hier}C{numero_hier}**\\n\\n"
                        f"**{' - '.join(map(str, arrivee))}**"
                    )
        except Exception as erreur:
            print("Assistant arrivée hier :", erreur)
    if any(k in q for k in ["demain", "à venir", "a venir", "prochaine course", "prochain quinté", "quinté de demain", "quinte de demain"]):
        try:
            from pmu_source import trouver_quinte_du_jour, charger_course_pmu, normaliser_date
            from datetime import datetime, timedelta
            date_future = normaliser_date(datetime.now() + timedelta(days=1))
            _, reunion, course = trouver_quinte_du_jour(date_future)
            if course:
                future_course = charger_course_pmu(date_future, reunion, course.get("numOrdre") or course.get("numCourse") or course.get("numero"))
                if future_course:
                    contexte["course"] = future_course
                    contexte["chevaux"] = future_course.get("chevaux", [])
                    contexte["source"] = "pmu_live_future"
        except Exception as erreur:
            print("Assistant future course :", erreur)

    resultat = repondre_assistant_turf(question, contexte)
    texte = resultat.get("reponse", "")

    def generate():
        import json
        yield "data: " + json.dumps({"type": "token", "text": texte}, ensure_ascii=False) + "\n\n"
        yield "data: " + json.dumps({"type": "done"}, ensure_ascii=False) + "\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
