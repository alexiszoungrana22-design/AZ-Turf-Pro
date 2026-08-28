"""AZ TURF PRO — Assistant conversationnel autonome (Version Intégrale).

Pronostiqueur hippique et analyste local : comprend les demandes naturelles,
conserve le contexte de conversation et orchestre de façon autonome les données
PMU (hier, aujourd'hui, demain), le moteur AZ Turf Pro et ses modules.

Aucune API distante n'est requise. Le système s'appuie sur les variables
prédictives internes pour générer son argumentaire textuel.
"""

import json
import re
import math
import unicodedata
from datetime import datetime, timedelta

# =====================================
# CONFIGURATION & MODE AUTONOME
# =====================================
AI_PROVIDER = "local"
TIMEOUT_SECONDES = 5

# =====================================
# GESTION DU DIALOGUE & MÉMOIRE
# =====================================
_ETAT_DIALOGUE = {
    "etat": "ACCUEIL",
    "dernier_intent": None,
    "derniers_numeros": [],
    "dernier_cheval": None,
    "derniere_question": ""
}

def _normaliser_texte(texte: str) -> str:
    """Normalise la chaîne pour faciliter l'analyse sémantique."""
    s = str(texte or '').strip().lower().replace('’', "'").replace('`', "'")
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r"[^a-z0-9\s'#-]", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def _extraire_numeros(question: str) -> list:
    """Extrait tous les numéros de chevaux valides de la requête."""
    nums = [int(x) for x in re.findall(r"\b(\d{1,2})\b", _normaliser_texte(question))]
    return list(dict.fromkeys(nums))[:10]

def _resoudre_references(question: str) -> str:
    """Résout les anaphores ("ce cheval", "les deux", etc.) grâce au contexte local."""
    q = _normaliser_texte(question)
    p = _ETAT_DIALOGUE.get('derniers_numeros', [])
    if not p:
        return question

    if any(x in q for x in ('eux', 'les deux', 'ces deux', 'entre eux', 'lequel')) and len(p) >= 2:
        return f"{question} [référence : chevaux {p[-2]} et {p[-1]}]"
    if any(x in q for x in ('ce cheval', 'celui ci', 'celui-ci', 'lui')):
        return f"{question} [référence : cheval {_ETAT_DIALOGUE.get('dernier_cheval')}]"
    if 'le premier' in q and p:
        return f"{question} [référence : cheval {p[0]}]"
    return question

# =====================================
# MOTEUR D'ANALYSE EXPERT AZ TURF PRO
# =====================================
def _cote(cheval: dict) -> float:
    try:
        return float(cheval.get("cote") or 0)
    except (TypeError, ValueError):
        return 0.0

def _score_expert_independant(cheval: dict) -> float:
    """
    Calcule un score sur 100 basé sur les variables prédictives profondes.
    Utilisé par le chatbot pour justifier ses choix face à l'utilisateur.
    """
    score = 0.0
    
    # 1. Variables de Forme et Régularité (Base 30 pts)
    forme = float(cheval.get("forme") or 5.0)
    regularite = float(cheval.get("regularite") or 5.0)
    score += (forme * 1.5) + (regularite * 1.5)
    
    # 2. Variables Entourage (Base 20 pts)
    reussite_jockey = float(cheval.get("reussite_jockey") or 5.0)
    confiance_ent = float(cheval.get("confiance_entraineur") or 5.0)
    score += (reussite_jockey * 1.0) + (confiance_ent * 1.0)
    
    # 3. Variables d'Équipement (Base 10 pts)
    deferre = str(cheval.get("deferre") or "").upper()
    if deferre in ["D4", "DP", "DA"]:
        score += 10.0 if deferre == "D4" else 5.0
        
    oeilleres = str(cheval.get("oeilleres") or "").upper()
    if oeilleres in ["O", "OA"]:
        score += 3.0 # Léger bonus de concentration
        
    # 4. Variables d'Aptitude (Base 20 pts)
    dist_pred = float(cheval.get("distance_predilection") or 5.0)
    hippo_fav = float(cheval.get("hippodromes_favoris") or 5.0)
    corde = float(cheval.get("corde") or 5.0) # Utile pour le plat
    score += (dist_pred * 0.8) + (hippo_fav * 0.8) + (corde * 0.4)
    
    # 5. Variable de Fraîcheur (Base 10 pts)
    jours_repos = float(cheval.get("jours_depuis_derniere_course") or 21.0)
    if 15 <= jours_repos <= 45:
        score += 10.0 # Fraîcheur optimale
    elif jours_repos < 15:
        score += 5.0  # Rapproché
    elif 45 < jours_repos <= 90:
        score += 2.0  # Rentrée correcte
    else:
        score += 0.0  # Grosse rentrée (> 90 jours)

    # 6. Variable de Marché / Confiance Parieurs (Base 10 pts)
    c = _cote(cheval)
    if c > 0:
        score += max(0.0, min(10.0, 15.0 - (c * 0.5)))
        
    return round(max(0.0, min(100.0, score)), 2)

def _trouver_cheval(classement: list, numero: str):
    return next((c for c in classement if str(c.get("numero")) == str(numero)), None)

def _generer_argumentaire(cheval: dict) -> str:
    """Génère un texte explicatif naturel basé sur les points forts du cheval."""
    points_forts = []
    
    if str(cheval.get("deferre", "")).upper() == "D4":
        points_forts.append("Il est déferré des 4 pieds pour cet objectif.")
    if float(cheval.get("reussite_jockey") or 0) >= 7.0:
        points_forts.append("Son tandem avec le driver/jockey est très performant.")
    if float(cheval.get("distance_predilection") or 0) >= 7.0:
        points_forts.append("Il évolue sur sa distance de prédilection.")
        
    jours = float(cheval.get("jours_depuis_derniere_course") or 0)
    if 15 <= jours <= 45:
        points_forts.append(f"Avec {int(jours)} jours de repos, il se présente avec une fraîcheur optimale.")
        
    if not points_forts:
        return "C'est un cheval qui s'annonce compétitif, bien que sans avantage statistique majeur."
        
    return " ".join(points_forts)

# =====================================
# GESTION TEMPORELLE (HIER & DEMAIN)
# =====================================
def _analyser_course_passee(question: str) -> str | None:
    """Consulte l'historique local pour la course d'hier."""
    q = _normaliser_texte(question)
    if not any(k in q for k in ["hier", "passee", "derniere", "resultat", "arrivee"]):
        return None

    try:
        # Importation dynamique pour éviter les dépendances circulaires
        from learning import lire_historique
        historique = lire_historique() or []
    except ImportError:
        return "Le module d'historique (learning.py) n'est pas accessible."
    except Exception as e:
        return f"Erreur de lecture de l'historique : {str(e)}"

    courses = [e for e in historique if isinstance(e, dict) and e.get("arrivee")]
    if not courses:
        return "Aucune course avec une arrivée validée n'est présente dans la base AZ Turf Pro."

    derniere = courses[-1]
    arrivee = [str(n) for n in derniere.get("arrivee", [])]
    selection = [str(n) for n in (derniere.get("selection_az") or [])]
    
    touches = [n for n in selection if n in arrivee]
    date_str = derniere.get("date", "Date inconnue")
    
    return (
        f"📋 **Bilan de la dernière course enregistrée ({date_str})**\n"
        f"🏁 **Arrivée officielle** : {' - '.join(arrivee)}\n"
        f"🎯 **Pronostic AZ Turf Pro** : {' - '.join(selection)}\n"
        f"✨ **Chevaux trouvés** : {', '.join(touches) if touches else 'Aucun'} "
        f"({len(touches)} sur les {len(arrivee)} de l'arrivée)."
    )

def _analyser_course_demain(question: str) -> str | None:
    """Interroge pmu_source pour les données du lendemain."""
    q = _normaliser_texte(question)
    if "demain" not in q:
        return None

    try:
        from pmu_source import charger_course_pmu
        date_demain = (datetime.now() + timedelta(days=1)).strftime("%d%m%Y")
        course = charger_course_pmu(date_demain)

        if not course or not course.get("chevaux"):
            return "📅 Le programme de demain n'est pas encore totalement disponible dans la base PMU."

        nb = len(course.get("chevaux", []))
        hippo = course.get("hippodrome", "-")
        return (
            f"📅 **Aperçu du programme de Demain ({hippo})**\n"
            f"La course compte {nb} partants officiels.\n"
            f"L'analyse complète sera générée par le moteur dès que les cotes matinales seront stabilisées."
        )
    except Exception as e:
        return f"Impossible de récupérer la course de demain. L'API source est peut-être inaccessible : {str(e)}"

# =====================================
# FONCTIONS DE RÉPONSE ET PRONOSTIC
# =====================================
def _analyser_favori(classement: list) -> str:
    if not classement:
        return "Aucune donnée de course n'est chargée actuellement."
    top = classement[0]
    arg = _generer_argumentaire(top)
    return (
        f"🎯 **La Base Absolue** : N°{top.get('numero')} **{top.get('nom')}**\n"
        f"Cote : {top.get('cote', '-')} | Indice AZ : {top.get('indice_az', '-')}\n"
        f"💡 *Avis de l'expert* : {arg}"
    )

def _analyser_vulnerables(classement: list) -> str:
    if len(classement) < 2:
        return "Il n'y a pas assez de partants pour faire un tri des vulnérabilités."
    
    vulnerables = []
    # Cherche les chevaux bien classés (top 5) mais avec un mauvais score expert
    for c in classement[:5]:
        score = _score_expert_independant(c)
        if score < 50.0:
            vulnerables.append(f"• N°{c.get('numero')} **{c.get('nom')}** (Score Expert : {score}/100 - Trop de facteurs contre lui aujourd'hui)")
            
    if not vulnerables:
        return "Les favoris actuels de la course semblent solides. Aucune fausse note majeure détectée par l'algorithme."
    return "⚠️ **Faux favoris / Chevaux à surveiller** :\n" + "\n".join(vulnerables)

def _generer_ticket_autonome(classement: list, profil: str = "mixte") -> str:
    if len(classement) < 5:
        return "Pas assez de partants pour générer un ticket complet."

    chevaux_scores = [(c, _score_expert_independant(c)) for c in classement]
    
    if profil == "prudent":
        surs = sorted(chevaux_scores, key=lambda x: -x[1])[:5]
        nums = [str(x[0].get("numero")) for x in surs]
        return "🛡️ **Ticket Prudent (Basé sur la Régularité & Forme)** : " + " - ".join(nums)

    elif profil == "speculatif":
        outsiders = [x for x in chevaux_scores if _cote(x[0]) >= 12.0]
        meilleurs_outsiders = sorted(outsiders, key=lambda x: -x[1])[:2]
        bases = sorted(chevaux_scores, key=lambda x: -x[1])[:3]
        
        selection = bases + meilleurs_outsiders
        # Trier par numéro pour faire propre
        nums = [str(x[0].get("numero")) for x in selection]
        return "🎲 **Ticket Spéculatif (Recherche de Rapports)** : " + " - ".join(nums)

    else:
        nums = [str(c.get("numero")) for c in classement[:5]]
        return "⚖️ **Ticket Officiel AZ Turf Pro** : " + " - ".join(nums)

# =====================================
# ROUTEUR PRINCIPAL
# =====================================
def repondre_assistant_turf(question: str, contexte_analyse: dict = None, historique: list = None) -> dict:
    """
    Traite la requête de l'utilisateur, met à jour le contexte local et
    renvoie une réponse experte formatée.
    """
    global _ETAT_DIALOGUE
    
    question_brute = str(question or '').strip()
    if not question_brute:
        return {
            "status": "success",
            "question": "",
            "reponse": "Bonjour, je suis votre assistant AZ Turf Pro. Quel type de pronostic ou d'analyse souhaitez-vous aujourd'hui ?",
            "source": "local"
        }

    question_resolue = _resoudre_references(question_brute)
    nums = _extraire_numeros(question_resolue)
    if nums:
        _ETAT_DIALOGUE["derniers_numeros"] = nums
        _ETAT_DIALOGUE["dernier_cheval"] = nums[-1]
    _ETAT_DIALOGUE["derniere_question"] = question_brute

    q_norm = _normaliser_texte(question_resolue)
    contexte = contexte_analyse or {}
    moteur = contexte.get("moteur", {})
    classement = moteur.get("classement", [])

    # 1. Vérification Temporelle (Hier / Demain)
    reponse_passee = _analyser_course_passee(question_resolue)
    if reponse_passee:
        return {"status": "success", "question": question_brute, "reponse": reponse_passee, "source": "local_history"}

    reponse_demain = _analyser_course_demain(question_resolue)
    if reponse_demain:
        return {"status": "success", "question": question_brute, "reponse": reponse_demain, "source": "local_pmu"}

    # 2. Intentions de Salutation
    if any(k in q_norm for k in ["bonjour", "salut", "hello", "bonsoir"]):
        return {
            "status": "success",
            "question": question_brute,
            "reponse": "👋 Bonjour ! Je suis prêt à analyser le programme hippique. Que puis-je faire pour vous (Ticket, Analyse d'un partant, Bilan de la veille...) ?",
            "source": "local"
        }

    # 3. Traitement des Intentions d'Analyse Turf
    if any(k in q_norm for k in ["favori", "coup sur", "meilleur", "base", "gagnant"]):
        reponse = _analyser_favori(classement)

    elif any(k in q_norm for k in ["vulnerable", "fragile", "mefier", "battable", "piege"]):
        reponse = _analyser_vulnerables(classement)

    elif any(k in q_norm for k in ["prudent", "sur", "securise", "regulier"]):
        reponse = _generer_ticket_autonome(classement, profil="prudent")

    elif any(k in q_norm for k in ["speculatif", "risque", "outsider", "gros rapport", "tocard", "surprise"]):
        reponse = _generer_ticket_autonome(classement, profil="speculatif")

    elif any(k in q_norm for k in ["quinte", "ticket", "combinaison", "pronostic", "jeu"]):
        reponse = _generer_ticket_autonome(classement, profil="mixte")

    # Comparaison de chevaux
    elif len(nums) >= 2 and any(k in q_norm for k in ["compare", "vs", "contre", "mieux", "choisir"]):
        a = _trouver_cheval(classement, str(nums[0]))
        b = _trouver_cheval(classement, str(nums[1]))
        if a and b:
            score_a = _score_expert_independant(a)
            score_b = _score_expert_independant(b)
            gagnant = a if score_a >= score_b else b
            
            reponse = (
                f"📊 **Comparatif N°{a.get('numero')} vs N°{b.get('numero')}** :\n"
                f"• **N°{a.get('numero')} {a.get('nom')}** (Cote: {a.get('cote')}) : Score Expert {score_a}/100\n"
                f"• **N°{b.get('numero')} {b.get('nom')}** (Cote: {b.get('cote')}) : Score Expert {score_b}/100\n\n"
                f"👉 **Mon choix** : Le N°{gagnant.get('numero')}. {_generer_argumentaire(gagnant)}"
            )
        else:
            reponse = "Impossible de comparer. Vérifiez que ces numéros sont bien partants aujourd'hui."

    # Analyse d'un cheval spécifique
    elif len(nums) == 1:
        cheval = _trouver_cheval(classement, str(nums[0]))
        if cheval:
            score = _score_expert_independant(cheval)
            arg = _generer_argumentaire(cheval)
            reponse = (
                f"🐎 **Analyse du N°{cheval.get('numero')} — {cheval.get('nom')}**\n"
                f"• Score Expert AZ : **{score}/100**\n"
                f"• Cote actuelle : {cheval.get('cote', '-')}\n"
                f"• Indice AZ Global : {cheval.get('indice_az', '-')}\n"
                f"• Dernières performances : {cheval.get('musique_brute', '-')}\n\n"
                f"💡 *Le mot de l'algorithme* : {arg}"
            )
        else:
            reponse = f"Le cheval portant le numéro {nums[0]} est introuvable dans la course actuelle."

    else:
        reponse = (
            "Je n'ai pas bien compris votre demande. Vous pouvez par exemple me demander :\n"
            "• « Quel est le grand favori ? »\n"
            "• « Donne-moi un ticket spéculatif pour le Quinté »\n"
            "• « Que penses-tu du 5 et du 8 ? »\n"
            "• « Quels sont les résultats d'hier ? »"
        )

    return {
        "status": "success",
        "question": question_brute,
        "reponse": reponse,
        "source": "moteur_az_local_integral"
    }
