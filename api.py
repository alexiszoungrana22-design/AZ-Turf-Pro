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


from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse

from engine import lancer_analyse

from database import (
    creer_abonnement,
    activer_abonnement,
    valider_reference_paiement,
    verifier_premium,
    lister_abonnements,
    statistiques_abonnements
)

from models import (
    AbonnementRequest,
    ActivationRequest
)

from security import require_admin, is_valid_admin_key, create_premium_token, verify_premium_token

from pmu_source import charger_course_pmu, recuperer_programme, trouver_reunion, trouver_course, trouver_quinte_du_jour

from lonab_source import recuperer_journal_lonab, diagnostiquer_journal_lonab

from learning import lire_historique, mettre_a_jour_arrivee

from modules.chatbot_turf import repondre_assistant_turf
from modules.stats_backtest import calculer_stats_performance, simuler_backtest_filtre

import json
import os
from datetime import datetime, timedelta


router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)


# =====================================
# CHARGEMENT COURSE PMU LIVE
# =====================================

def charger_course():
    """
    Charge uniquement la course rÃ©elle depuis PMU.

    Important : aucune donnÃ©e de demonstration locale n'est utilisÃ©e
    automatiquement. Cela empÃªche une ancienne course de courses.json
    d'Ãªtre prÃ©sentÃ©e comme la course du jour lorsque PMU est indisponible.
    """
    date_pmu = datetime.now().strftime("%d%m%Y")

    try:
        course = charger_course_pmu(date_pmu)
    except Exception as erreur:
        print("PMU indisponible :", erreur)
        return None, "none"

    if not isinstance(course, dict) or not course.get("chevaux"):
        print("PMU : aucune course exploitable pour", date_pmu)
        return None, "none"

    print("Source utilisee : PMU reel")
    return course, "pmu_live"


def _charger_partants_live():
    """Retourne la course et ses partants depuis PMU, sans fallback local."""
    course, source = charger_course()
    if source != "pmu_live" or not course:
        raise HTTPException(
            status_code=503,
            detail="Les donnÃ©es PMU rÃ©elles du jour sont indisponibles actuellement."
        )
    return course



# =====================================
# HORAIRE PMU DE LA COURSE
# =====================================

def _recuperer_horaire_course(course):
    """RÃ©cupÃ¨re l'heure brute de dÃ©part depuis le programme PMU.
    Le module pmu_source reste inchangÃ© ; on enrichit seulement la rÃ©ponse API.
    """
    if not isinstance(course, dict):
        return {"depart": "", "arret_des_jeux": ""}

    date = course.get("date")
    reunion = course.get("reunion")
    numero = course.get("course_numero")
    if not date or not reunion or not numero:
        return {"depart": "", "arret_des_jeux": ""}

    try:
        programme = recuperer_programme(date, reunion)
        reunion_data = trouver_reunion(programme, reunion)
        course_brute = trouver_course(reunion_data, numero)
        if not isinstance(course_brute, dict):
            return {"depart": "", "arret_des_jeux": ""}

        def premier(*cles):
            for cle in cles:
                valeur = course_brute.get(cle)
                if valeur not in (None, ""):
                    return valeur
            return ""

        depart = premier(
            "heureDepart", "heureDepartPrevue", "heureDepartCourse",
            "heure_depart", "heure", "heureDeDepart"
        )
        arret = premier(
            "heureArretDesJeux", "heureArretJeux",
            "arretDesJeux", "arret_des_jeux"
        )
        return {"depart": depart, "arret_des_jeux": arret}
    except Exception as erreur:
        print("Horaire PMU indisponible :", erreur)
        return {"depart": "", "arret_des_jeux": ""}


# =====================================
# QUINTÉ DES PÉRIODES : HIER / JOUR / DEMAIN
# =====================================

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
# ANALYSE AZ TURF
# =====================================

def _analyse_complete():

    try:

        # =================================
        # 1. CHARGEMENT DES DONNÃƒâ€°ES
        # =================================

        course, source = charger_course()

        if not course:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Aucune donnÃƒÂ©e de course "
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
                    "Aucun cheval trouvÃƒÂ© "
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
                "hippodrome": course.get("hippodrome"),
                "discipline": course.get("discipline"),
                "distance_course": course.get("distance_course"),
                "allocation": course.get("allocation"),
                "type_depart": course.get("type_depart"),
                "conditions": course.get("conditions"),
                "non_partants": course.get("non_partants", []),
            }
        )

        if not isinstance(
            resultat,
            dict
        ):
            raise Exception(
                "RÃƒÂ©ponse invalide du moteur AZ"
            )

        classement = resultat.get(
            "chevaux",
            []
        )

        if not classement:

            raise Exception(
                "Le moteur AZ n'a retournÃƒÂ© "
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
        # 5. RÃƒâ€°PONSE API
        # =================================

        reponse = {

            "message": (
                "Analyse AZ Turf terminÃƒÂ©e"
                if not est_demo else
                "Analyse AZ Turf terminÃƒÂ©e "
                "(donnÃƒÂ©es de dÃƒÂ©monstration, "
                "aucune course rÃƒÂ©elle "
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

            "horaires":
                _recuperer_horaire_course(course),

            "heure_depart":
                _recuperer_horaire_course(course).get("depart", ""),

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
                "Ces donnÃƒÂ©es sont des donnÃƒÂ©es de "
                "dÃƒÂ©monstration figÃƒÂ©es et ne "
                "correspondent pas Ãƒ  une course "
                "rÃƒÂ©elle du jour."
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
# ANALYSE PUBLIQUE / PREMIUM SECURISEE
# =====================================

@router.get("/analyse")
def analyse():
    """Analyse publique : uniquement les données gratuites."""
    reponse = _analyse_complete()
    tickets = reponse.get("tickets", {}) or {}
    reponse["tickets"] = {
        "gratuit": tickets.get("gratuit", {})
    }
    return reponse


def _require_premium_request(authorization: str | None, x_admin_key: str | None) -> dict:
    # Administrateur : accès Premium autorisé avec la clé serveur.
    if is_valid_admin_key(x_admin_key):
        return {"admin": True, "telephone": "ADMINISTRATEUR"}

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Accès Premium non autorisé.")

    token = authorization[7:].strip()
    payload = verify_premium_token(token)
    telephone = payload.get("telephone", "").strip()

    statut = verifier_premium(telephone)
    if statut.get("statut") != "ACTIF":
        raise HTTPException(status_code=403, detail="Abonnement Premium inactif ou expiré.")

    return {"admin": False, "telephone": telephone}


@router.get("/premium/ticket")
def premium_ticket(
    authorization: str | None = Header(default=None),
    x_admin_key: str | None = Header(default=None),
):
    """Endpoint Premium : tickets complets uniquement après authentification serveur."""
    _require_premium_request(authorization, x_admin_key)
    return _analyse_complete()


# =====================================
# PARTANTS PMU LIVE
# =====================================

@router.get("/partants")
def partants():
    """Retourne les partants de la course PMU rÃ©elle du jour."""
    try:
        course = _charger_partants_live()
        chevaux = course.get("chevaux", [])

        return {
            "source": "pmu_live",
            "donnees_demo": False,
            "course": course.get("course", ""),
            "date": course.get("date") or datetime.now().strftime("%d%m%Y"),
            "reunion": course.get("reunion", ""),
            "course_numero": course.get("course_numero", ""),
            "hippodrome": course.get("hippodrome", ""),
            "discipline": course.get("discipline", ""),
            "distance": course.get("distance_course", ""),
            "allocation": course.get("allocation", ""),
            "horaires": _recuperer_horaire_course(course),
            "heure_depart": _recuperer_horaire_course(course).get("depart", ""),
            "non_partants": course.get("non_partants", []),
            "partants": len(chevaux),
            "chevaux": chevaux,
        }
    except HTTPException:
        raise
    except Exception as erreur:
        print("Erreur partants PMU :", erreur)
        raise HTTPException(status_code=500, detail=f"Erreur partants : {erreur}")


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
                "Abonnement enregistrÃƒÂ©",

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
        activation.telephone.strip(),
        activation.reference.strip()
    )

    if abonnement is None:
        raise HTTPException(
            status_code=403,
            detail="Référence non validée ou abonnement introuvable."
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
    telephone: str,
    authorization: str | None = Header(default=None),
    x_admin_key: str | None = Header(default=None),
):
    """Statut Premium protégé : impossible de sonder arbitrairement un numéro."""
    acces = _require_premium_request(authorization, x_admin_key)
    if not acces.get("admin") and acces.get("telephone") != telephone.strip():
        raise HTTPException(status_code=403, detail="Accès Premium non autorisé pour ce compte.")
    return verifier_premium(telephone.strip())


# =====================================
# ADMIN - ABONNEMENTS
# =====================================

@router.post("/admin/valider-reference")
def admin_valider_reference(
    activation: ActivationRequest,
    _: bool = Depends(require_admin)
):
    abonnement = valider_reference_paiement(
        activation.telephone.strip(),
        activation.reference.strip()
    )

    if abonnement is None:
        raise HTTPException(status_code=404, detail="Abonnement introuvable.")

    return {
        "message": "Référence de paiement validée. Le client peut maintenant activer son Premium.",
        "statut": abonnement["statut"]
    }


@router.get("/admin/verification")
def admin_verification(_: bool = Depends(require_admin)):
    return {"authenticated": True}


@router.get("/admin/abonnements")
def admin_abonnements(_: bool = Depends(require_admin)):
    return {"abonnements": lister_abonnements()}


@router.get("/admin/statistiques")
def admin_statistiques(_: bool = Depends(require_admin)):
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

    from pmu_source import trouver_quinte_du_jour

    aujourd_hui = datetime.now()
    date_pmu = aujourd_hui.strftime("%d%m%Y")

    try:

        programme, reunion, course = trouver_quinte_du_jour(
            date_pmu
        )

        return {
            "reunion": reunion,
            "programme_brut": programme,
            "course_brute": course,
        }

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur debug PMU : {erreur}"
        )



# =====================================
# ASSISTANT TURF
# =====================================

@router.post("/assistant/chat")
def assistant_chat(payload: dict):
    """RÃ©pond aux questions Ã  partir de l'analyse courante."""
    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question obligatoire.")

    contexte = payload.get("contexte") or {}
    moteur = contexte.get("moteur")

    if not moteur:
        base, source = charger_course()
        if not base:
            raise HTTPException(
                status_code=503,
                detail="Aucune analyse PMU rÃ©elle disponible actuellement."
            )
        info_course = dict(base)
        # Ne transmettre au chatbot que le contexte de course déjà fourni par la source.
        resultat = lancer_analyse(
            base.get("chevaux", []),
            info_course=info_course,
        )
        moteur = {
            "classement": resultat.get("classement", []),
            "chevaux": resultat.get("chevaux", []),
            "tickets": resultat.get("tickets", {}),
            "lecture_course": (resultat.get("tickets", {}).get("premium", {}) or {}).get("lecture_course", {}),
            "course": info_course,
        }

    return repondre_assistant_turf(question, {"moteur": moteur})


@router.post("/assistant/chat/stream")
def assistant_chat_stream(payload: dict):
    """Compatibilité streaming : réutilise le moteur assistant existant et expose une réponse SSE."""
    resultat = assistant_chat(payload)
    texte = str(resultat.get("reponse", ""))

    def generate():
        yield "event: message\n"
        yield f"data: {json.dumps({"reponse": texte}, ensure_ascii=False)}\n\n"
        yield "event: done\n"
        yield "data: {}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})


# =====================================
# STATISTIQUES / BACKTEST
# =====================================

@router.post("/stats/backtest")
def stats_backtest(payload: dict):
    """Calcule les performances et le backtest sur l'historique fourni ou local."""
    historique = payload.get("historique")
    if not isinstance(historique, list) or not historique:
        historique = lire_historique()

    filtres = payload.get("filtres") or {}
    resultat = simuler_backtest_filtre(historique, filtres)
    resultat["performance"] = calculer_stats_performance(historique)
    return resultat


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

            if entree.get("arrivee") is not None:
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
