"""AZ TURF PRO â€” Assistant conversationnel autonome.

Pronostiqueur hippique et analyste local : le module comprend les demandes
naturelles, conserve le contexte de conversation et orchestre les donnÃ©es
PMU, le moteur AZ Turf Pro et ses modules d'accompagnement.

Aucune API Claude/OpenAI n'est nÃ©cessaire au fonctionnement de ce module.
"""

import json
import re
from datetime import datetime

# MODE AUTONOME AZ TURF PRO
# Claude et OpenAI sont volontairement dÃ©sactivÃ©s.
AI_PROVIDER = "local"
ANTHROPIC_API_KEY = ""
OPENAI_API_KEY = ""
CLAUDE_MODEL = ""
OPENAI_MODEL = ""
TIMEOUT_SECONDES = 0


# =====================================
# CONSTRUCTION DU CONTEXTE COURSE
# =====================================

def _resume_course(contexte: dict) -> str:
    course = (contexte or {}).get("course", {}) or {}
    lignes = [
        f"RÃ©union/Course : {course.get('reunion', '-')} / "
        f"{course.get('course_numero', '-')} â€” {course.get('course', '-')}",
        f"Hippodrome : {course.get('hippodrome', '-')}",
        f"Discipline : {course.get('discipline', '-')} sur "
        f"{course.get('distance_course', '-')} m",
        f"Date / heure de dÃ©part : {course.get('date', '-')} "
        f"{course.get('heure_depart', '-')}",
        f"Allocation : {course.get('allocation', '-')}",
    ]
    non_partants = course.get("non_partants") or []
    if non_partants:
        lignes.append(f"Non-partants : {', '.join(str(n) for n in non_partants)}")

    complement_galop = (contexte or {}).get("complement_france_galop")
    if complement_galop:
        lignes.append(str(complement_galop))

    return "\n".join(lignes)


def _resume_classement(contexte: dict, limite: int = 20) -> str:
    moteur = (contexte or {}).get("moteur", {}) or {}
    classement = moteur.get("classement", []) or []
    lignes = []
    for cheval in classement[:limite]:
        if not isinstance(cheval, dict):
            continue
        driver = cheval.get("driver") or cheval.get("conducteur") or cheval.get("pilote") or cheval.get("jockey") or "-"
        tendance = cheval.get("tendance_cote") or cheval.get("tendance") or "-"
        forme = cheval.get("forme")
        regularite = cheval.get("regularite")
        confiance = cheval.get("confiance")

        ligne = (
            f"NÂ°{cheval.get('numero', '?')} {cheval.get('nom', '?')} "
            f"({cheval.get('age', '-')} ans, {cheval.get('sexe', '-')}) â€” "
            f"jockey/driver : {driver}, "
            f"entraÃ®neur : {cheval.get('entraineur', '-')} | "
            f"cote {cheval.get('cote', '-')} (tendance {tendance}), "
            f"indice AZ {cheval.get('indice_az', '-')}, "
            f"indice Premium {cheval.get('indice_premium', '-')}"
        )
        if confiance is not None:
            ligne += f", confiance {confiance}%"
        ligne += (
            f" | musique : {cheval.get('musique_brute', '-')}"
        )
        if forme is not None:
            ligne += f" (forme {forme}/10"
            if regularite is not None:
                ligne += f", rÃ©gularitÃ© {regularite}/10"
            ligne += ")"
        ligne += (
            f", gains carriÃ¨re : {cheval.get('gains', cheval.get('gains_carriere_brute', '-'))}, "
            f"corde : {cheval.get('corde', '-')}, "
            f"ferrage : {cheval.get('deferre', '-')}"
        )

        # Statistiques avancÃ©es, jusque-lÃ  jamais exploitÃ©es par le chatbot
        jockey_pct = cheval.get("reussite_jockey")
        conf_entraineur = cheval.get("confiance_entraineur")
        hippo_fav = cheval.get("hippodromes_favoris")
        dist_pref = cheval.get("distance_predilection")
        jours_repos = cheval.get("jours_depuis_derniere_course")
        variation_pct = cheval.get("variation_cote_pct")
        radar = cheval.get("radar") if isinstance(cheval.get("radar"), dict) else {}
        badges = cheval.get("badges") if isinstance(cheval.get("badges"), list) else []

        extras = []
        if jockey_pct is not None:
            extras.append(f"rÃ©ussite jockey {jockey_pct}%")
        if conf_entraineur is not None:
            extras.append(f"confiance entraÃ®neur {conf_entraineur}")
        if hippo_fav:
            extras.append(f"hippodromes favoris : {hippo_fav}")
        if dist_pref is not None:
            extras.append(f"distance de prÃ©dilection {dist_pref}m")
        if jours_repos is not None:
            extras.append(f"{jours_repos}j depuis la derniÃ¨re course")
        if variation_pct is not None and variation_pct != 0:
            sens = "baisse (argent qui rentre)" if variation_pct < 0 else "hausse (argent qui sort)"
            extras.append(f"cote en {sens} de {abs(variation_pct)}%")
        if extras:
            ligne += " | " + ", ".join(extras)

        if radar:
            ligne += (
                f" | Radar/100 â€” forme:{radar.get('forme','-')}, "
                f"distance:{radar.get('distance','-')}, jockey:{radar.get('jockey','-')}, "
                f"classe:{radar.get('classe','-')}, fraÃ®cheur:{radar.get('fraicheur','-')}"
            )
        if badges:
            libelles = [b.get("libelle") for b in badges if isinstance(b, dict) and b.get("libelle")]
            if libelles:
                ligne += f" | Badges : {', '.join(libelles)}"

        lignes.append(ligne)
    return "\n".join(lignes) if lignes else "Aucun classement disponible."


def _resume_tickets(contexte: dict) -> str:
    moteur = (contexte or {}).get("moteur", {}) or {}
    tickets = moteur.get("tickets", {}) or {}
    try:
        return json.dumps(tickets, ensure_ascii=False, default=str)
    except Exception:
        return "Tickets indisponibles."


def _construire_system_prompt(contexte: dict) -> str:
    return (
        "Tu es AZ Turf Pro, un pronostiqueur hippique professionnel, "
        "reconnu et confiant, qui Ã©change avec les abonnÃ©s d'une "
        "application de pronostics QuintÃ©+. Tu n'es pas un menu de "
        "commandes : tu comprends et rÃ©ponds naturellement Ã  n'importe "
        "quelle question, mÃªme formulÃ©e diffÃ©remment de ce qui est prÃ©vu, "
        "et tu maÃ®trises toutes les statistiques disponibles (cotes, "
        "tendances de cote, indices AZ et Premium, driver/jockey, "
        "entraÃ®neur, musique, forme, rÃ©gularitÃ©, corde, ferrage, gains "
        "carriÃ¨re).\n\n"
        "RÃ¨gles :\n"
        "- RÃ©ponds en franÃ§ais, avec l'assurance d'un vrai professionnel "
        "du turf qui connaÃ®t sa course sur le bout des doigts â€” direct, "
        "net, sans formules d'hÃ©sitation inutiles (\"je pense que\", "
        "\"peut-Ãªtre\" Ã  Ã©viter sauf incertitude rÃ©elle sur la donnÃ©e).\n"
        "- Appuie-toi uniquement sur les donnÃ©es de course fournies "
        "ci-dessous. N'invente jamais de cote, de nom de cheval, de "
        "jockey ou de rÃ©sultat qui n'y figure pas.\n"
        "- Si une information prÃ©cise demandÃ©e n'est pas dans les "
        "donnÃ©es (ex. un historique dÃ©taillÃ© non fourni), dis-le "
        "honnÃªtement plutÃ´t que de l'inventer â€” mais formule Ã§a comme "
        "une limite ponctuelle, pas comme une excuse gÃ©nÃ©rale.\n"
        "- Utilise activement TOUTES les statistiques Ã  ta disposition : "
        "la musique et la forme rÃ©cente, le driver, l'entraÃ®neur, la "
        "corde, le ferrage, les tendances de cote (argent qui rentre ou "
        "sort) sont autant d'arguments Ã  mobiliser, pas seulement "
        "l'indice AZ brut.\n"
        "- Argumente, compare, nuance, donne un vrai avis tranchÃ© "
        "d'analyste â€” pas seulement rÃ©citer des chiffres.\n"
        "- Reste concis (quelques phrases ou un court paragraphe), sauf "
        "si la question demande explicitement plus de dÃ©tail.\n\n"
        "=== DONNÃ‰ES DE LA COURSE ===\n"
        f"{_resume_course(contexte)}\n\n"
        "=== CLASSEMENT AZ TURF PRO (toutes statistiques disponibles) ===\n"
        f"{_resume_classement(contexte)}\n\n"
        "=== TICKETS GÃ‰NÃ‰RÃ‰S ===\n"
        f"{_resume_tickets(contexte)}\n"
    )


def _historique_pour_ia(historique: list, limite: int = 12) -> list:
    """Normalise l'historique envoyÃ© par le frontend (chatbot.js) vers un
    format role/content compatible avec les deux API."""
    messages = []
    for entree in (historique or [])[-limite:]:
        if not isinstance(entree, dict):
            continue
        role = entree.get("role") or ("user" if entree.get("question") else "assistant")
        contenu = entree.get("content") or entree.get("question") or entree.get("reponse") or ""
        if not contenu:
            continue
        role = "assistant" if role in ("assistant", "bot", "ia") else "user"
        messages.append({"role": role, "content": str(contenu)})
    return messages


# =====================================
# APPELS AUX MODÃˆLES
# =====================================

def _appeler_claude(system_prompt: str, messages: list, question: str) -> str:
    raise RuntimeError("Claude est dÃ©sactivÃ© : mode autonome AZ Turf Pro.")


def _appeler_openai(system_prompt: str, messages: list, question: str) -> str:
    raise RuntimeError("OpenAI est dÃ©sactivÃ© : mode autonome AZ Turf Pro.")

# =====================================
# REPLI SANS IA (aucune clÃ© configurÃ©e / Ã©chec des deux appels)
# =====================================

# =====================================
# MOTEUR D'ANALYSE RÃ‰EL (raisonnement sur les donnÃ©es, sans IA externe)
# =====================================

def _indice(cheval: dict) -> float:
    try:
        return float(cheval.get("indice_az") or cheval.get("indice_premium") or 0)
    except (TypeError, ValueError):
        return 0.0


def _cote(cheval: dict) -> float:
    try:
        return float(cheval.get("cote") or 0)
    except (TypeError, ValueError):
        return 0.0


def _score_expert_independant(cheval: dict) -> float:
    """Score IA 0-10 VOLONTAIREMENT INDÃ‰PENDANT de l'indice AZ/Premium
    (n'utilise jamais indice_az ni indice_premium). Recalcule sa propre
    opinion Ã  partir des statistiques brutes, pour offrir une vraie
    seconde lecture â€” c'est ce qui permet une comparaison "Ticket IA"
    vs "Ticket AZ Turf Pro" qui ait un sens (deux calculs distincts).
    """
    import math as _math

    forme = float(cheval.get("forme") or 5.0)
    regularite = float(cheval.get("regularite") or 5.0)

    nb_courses = cheval.get("nombre_courses")
    experience = min(10.0, float(nb_courses) / 5.0) if nb_courses else 5.0

    gains_bruts = cheval.get("gains_carriere") or cheval.get("gains") or 0
    try:
        gains_par_course = float(gains_bruts) / max(1, int(nb_courses or 1))
        gains_score = min(10.0, max(0.0, gains_par_course / 1000.0))
    except (TypeError, ValueError):
        gains_score = 5.0

    reussite = cheval.get("reussite_jockey")
    jockey_score = min(10.0, float(reussite) / 4.0) if reussite is not None else 5.0

    radar = cheval.get("radar") if isinstance(cheval.get("radar"), dict) else {}
    distance_score = float(radar.get("distance")) / 10.0 if radar.get("distance") is not None else 5.0
    terrain_score = 5.0  # pas de donnÃ©e terrain fiable et systÃ©matique disponible

    cote = _cote(cheval)
    cote_confiance = 5.0 if cote <= 1 else max(0.0, min(10.0, 10.0 / (1.0 + _math.log(cote))))

    score = (
        forme * 0.25 + regularite * 0.20 + distance_score * 0.12 + terrain_score * 0.08 +
        jockey_score * 0.10 + experience * 0.07 + gains_score * 0.08 + cote_confiance * 0.10
    )
    return round(max(0.0, min(10.0, score)), 2)


# Alias de compatibilitÃ© avec les anciennes versions du module.
_score_ia_independant = _score_expert_independant


def _trouver_cheval(classement: list, numero: str):
    return next((c for c in classement if str(c.get("numero")) == str(numero)), None)


def _analyser_favori(classement: list) -> str:
    if not classement:
        return "Aucune analyse de course n'est disponible pour le moment."
    top = classement[0]
    ecart = None
    if len(classement) >= 2:
        ecart = round(_indice(top) - _indice(classement[1]), 2)

    if ecart is not None and ecart >= 5:
        confiance = "Il se dÃ©tache nettement du reste du peloton â€” un favori solide."
    elif ecart is not None and ecart >= 1.5:
        confiance = "Il devance ses poursuivants avec une marge correcte, mais sans Ãªtre hors de portÃ©e."
    elif ecart is not None:
        confiance = f"L'Ã©cart avec le NÂ°{classement[1].get('numero')} n'est que de {ecart} points â€” course ouverte, ce favori peut Ãªtre renversÃ©."
    else:
        confiance = "Seul cheval rÃ©ellement analysÃ© sur cette course."

    badges = top.get("badges") if isinstance(top.get("badges"), list) else []
    libelles = [b.get("libelle") for b in badges if isinstance(b, dict) and b.get("libelle")]
    argument_badges = f" Arguments supplÃ©mentaires : {', '.join(libelles)}." if libelles else ""

    jours_repos = top.get("jours_depuis_derniere_course")
    note_repos = ""
    if isinstance(jours_repos, (int, float)):
        if jours_repos > 90:
            note_repos = f" Attention : {int(jours_repos)} jours sans courir, la fraÃ®cheur est incertaine."
        elif jours_repos <= 30:
            note_repos = f" Repos idÃ©al ({int(jours_repos)}j) pour Ãªtre au top."

    return (
        f"ðŸŽ¯ **Favori AZ Turf Pro** : NÂ°{top.get('numero')} **{top.get('nom')}** "
        f"(Indice AZ {top.get('indice_az', '-')}, cote {top.get('cote', '-')}). {confiance}"
        f"{argument_badges}{note_repos}"
    )


def _analyser_vulnerables(classement: list) -> str:
    if len(classement) < 2:
        return "Pas assez de chevaux analysÃ©s pour juger d'une vulnÃ©rabilitÃ©."

    vulnerables = []
    for i, cheval in enumerate(classement[:5]):
        if i == len(classement) - 1:
            continue
        suivant = classement[i + 1]
        ecart = _indice(cheval) - _indice(suivant)
        cote_elevee = _cote(cheval) >= 6
        if ecart < 1.5 or cote_elevee:
            raisons = []
            if ecart < 1.5:
                raisons.append(f"talonnÃ© de prÃ¨s par le NÂ°{suivant.get('numero')} (Ã©cart de {round(ecart, 2)} pts)")
            if cote_elevee:
                raisons.append(f"une cote qui reste Ã©levÃ©e ({cheval.get('cote')})")
            vulnerables.append(f"- NÂ°{cheval.get('numero')} **{cheval.get('nom')}** : {', '.join(raisons)}.")

    if not vulnerables:
        return "Aucun favori ne semble particuliÃ¨rement vulnÃ©rable sur cette course â€” le classement paraÃ®t net."
    return "âš ï¸ **Favoris Ã  surveiller** :\n" + "\n".join(vulnerables)


def _comparer_chevaux(classement: list, num_a: str, num_b: str) -> str:
    a = _trouver_cheval(classement, num_a)
    b = _trouver_cheval(classement, num_b)
    if not a or not b:
        manquant = num_a if not a else num_b
        return f"Je ne trouve pas le numÃ©ro {manquant} dans le classement de cette course."

    rang_a = classement.index(a) + 1
    rang_b = classement.index(b) + 1
    diff = round(_indice(a) - _indice(b), 2)

    if diff > 0:
        verdict = f"NÂ°{num_a} **{a.get('nom')}** ressort devant, avec {abs(diff)} points d'indice AZ de plus (rang {rang_a} vs {rang_b})."
    elif diff < 0:
        verdict = f"NÂ°{num_b} **{b.get('nom')}** ressort devant, avec {abs(diff)} points d'indice AZ de plus (rang {rang_b} vs {rang_a})."
    else:
        verdict = "Les deux chevaux sont Ã  Ã©galitÃ© d'indice â€” un vrai coin de table."

    return (
        f"**NÂ°{num_a} {a.get('nom')}** (indice {a.get('indice_az', '-')}, cote {a.get('cote', '-')}) "
        f"vs **NÂ°{num_b} {b.get('nom')}** (indice {b.get('indice_az', '-')}, cote {b.get('cote', '-')}) : {verdict}"
    )


def _classement_ia(classement: list) -> list:
    """Reclasse les chevaux selon le score expert indÃ©pendant (pas
    l'indice AZ) â€” c'est ce classement que les tickets IA utilisent."""
    copie = [dict(c) for c in classement]
    for c in copie:
        c["_expert_score"] = _score_expert_independant(c)
    return sorted(copie, key=lambda c: c["_expert_score"], reverse=True)


def _ticket_prudent(classement: list) -> str:
    """Ne retient que les valeurs sÃ»res selon le score expert indÃ©pendant :
    les mieux notÃ©s ET les plus rÃ©guliers, sans aucun outsider."""
    if len(classement) < 3:
        return "Pas assez de chevaux analysÃ©s pour construire un ticket prudent."
    classe = _classement_ia(classement)
    surs = sorted(classe, key=lambda c: (-c["_expert_score"], -float(c.get("regularite") or 0), _cote(c)))[:5]
    nums = [str(c.get("numero")) for c in surs]
    return (
        "ðŸ›¡ï¸ **Ticket expert autonome (prudent)** : " + " - ".join(nums) + "\n"
        f"Base expert : NÂ°{surs[0].get('numero')} {surs[0].get('nom', '')} (score expert {surs[0]['_expert_score']}/10).\n"
        "PrioritÃ© : forme, rÃ©gularitÃ© â€” aucun outsider, calcul sÃ©parÃ© de l'indice AZ."
    )


def _ticket_speculatif(classement: list) -> str:
    """PrivilÃ©gie les outsiders Ã  cote Ã©levÃ©e dont le score IA
    indÃ©pendant reste correct â€” recherche du gros rapport."""
    if len(classement) < 3:
        return "Pas assez de chevaux analysÃ©s pour construire un ticket spÃ©culatif."
    classe = _classement_ia(classement)
    outsiders = [c for c in classe if _cote(c) >= 12]
    outsiders = sorted(outsiders, key=lambda c: -c["_expert_score"])[:3]
    solides = [c for c in classe if c not in outsiders][:2]
    combinaison = (outsiders + solides)[:5]
    nums = [str(c.get("numero")) for c in combinaison]
    outsiders_txt = (
        "\n".join(f"â€¢ NÂ°{c.get('numero')} {c.get('nom','')} â€” cote {_cote(c)} â€” score expert {c['_expert_score']}/10" for c in outsiders)
        if outsiders else "â€¢ Aucun outsider Ã  cote â‰¥ 12 avec des donnÃ©es suffisantes."
    )
    return (
        "ðŸŽ² **Ticket expert autonome (spÃ©culatif, risquÃ©)** : " + " - ".join(nums) + "\n\n"
        f"Outsiders rÃ©ellement retenus :\n{outsiders_txt}\n\n"
        "Accepte davantage de risque â€” ne recopie pas le ticket AZ Turf Pro."
    )


def _ticket_mix(classement: list) -> str:
    """Ã‰quilibre selon le score expert indÃ©pendant : les meilleures valeurs
    sÃ»res + 1-2 outsiders, sans tout miser sur un seul profil."""
    if len(classement) < 4:
        return "Pas assez de chevaux analysÃ©s pour construire un ticket mixte."
    classe = _classement_ia(classement)
    surs = classe[:3]
    surs_numeros = {c.get("numero") for c in surs}
    outsiders = [c for c in classe if _cote(c) >= 8 and c.get("numero") not in surs_numeros][:2]
    if not outsiders:
        outsiders = [c for c in classe if c.get("numero") not in surs_numeros][-2:]
    combinaison = surs + outsiders
    nums = [str(c.get("numero")) for c in combinaison]
    return (
        "âš–ï¸ **Ticket expert autonome (mix Ã©quilibrÃ©)** : " + " - ".join(nums) + "\n"
        "Combine les meilleures valeurs sÃ»res (score IA) et 1 Ã  2 outsiders "
        "pour doser risque et rÃ©gularitÃ© â€” calcul sÃ©parÃ© de l'indice AZ."
    )


def _generer_scenarios(classement: list) -> str:
    if len(classement) < 3:
        return "Pas assez de chevaux analysÃ©s pour construire des scÃ©narios."

    favori, second, troisieme = classement[0], classement[1], classement[2]
    outsiders = [c for c in classement if _cote(c) >= 10]
    outsider = outsiders[0] if outsiders else classement[-1]

    return (
        "ðŸ›¤ï¸ **Deux scÃ©narios possibles** :\n\n"
        f"**ScÃ©nario logique** : le favori NÂ°{favori.get('numero')} **{favori.get('nom')}** confirme sa "
        f"place, devant NÂ°{second.get('numero')} **{second.get('nom')}** et NÂ°{troisieme.get('numero')} "
        f"**{troisieme.get('nom')}** â€” un ordre proche du classement AZ Turf Pro.\n\n"
        f"**ScÃ©nario surprise** : NÂ°{outsider.get('numero')} **{outsider.get('nom')}** "
        f"(cote {outsider.get('cote', '-')}) crÃ©e la sensation et vient bousculer le favori, "
        "profitant d'un faux rythme ou d
