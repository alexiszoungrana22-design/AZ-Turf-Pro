"""AZ TURF PRO — Assistant conversationnel autonome.

Pronostiqueur hippique et analyste local : le module comprend les demandes
naturelles, conserve le contexte de conversation et orchestre les données
PMU, le moteur AZ Turf Pro et ses modules d'accompagnement.

Aucune API Claude/OpenAI n'est nécessaire au fonctionnement de ce module.
"""

import json
import re
from datetime import datetime

# MODE AUTONOME AZ TURF PRO
# Claude et OpenAI sont volontairement désactivés.
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
        f"Réunion/Course : {course.get('reunion', '-')} / "
        f"{course.get('course_numero', '-')} — {course.get('course', '-')}",
        f"Hippodrome : {course.get('hippodrome', '-')}",
        f"Discipline : {course.get('discipline', '-')} sur "
        f"{course.get('distance_course', '-')} m",
        f"Date / heure de départ : {course.get('date', '-')} "
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
            f"N°{cheval.get('numero', '?')} {cheval.get('nom', '?')} "
            f"({cheval.get('age', '-')} ans, {cheval.get('sexe', '-')}) — "
            f"jockey/driver : {driver}, "
            f"entraîneur : {cheval.get('entraineur', '-')} | "
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
                ligne += f", régularité {regularite}/10"
            ligne += ")"
        ligne += (
            f", gains carrière : {cheval.get('gains', cheval.get('gains_carriere_brute', '-'))}, "
            f"corde : {cheval.get('corde', '-')}, "
            f"ferrage : {cheval.get('deferre', '-')}"
        )

        # Statistiques avancées, jusque-là jamais exploitées par le chatbot
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
            extras.append(f"réussite jockey {jockey_pct}%")
        if conf_entraineur is not None:
            extras.append(f"confiance entraîneur {conf_entraineur}")
        if hippo_fav:
            extras.append(f"hippodromes favoris : {hippo_fav}")
        if dist_pref is not None:
            extras.append(f"distance de prédilection {dist_pref}m")
        if jours_repos is not None:
            extras.append(f"{jours_repos}j depuis la dernière course")
        if variation_pct is not None and variation_pct != 0:
            sens = "baisse (argent qui rentre)" if variation_pct < 0 else "hausse (argent qui sort)"
            extras.append(f"cote en {sens} de {abs(variation_pct)}%")
        if extras:
            ligne += " | " + ", ".join(extras)

        if radar:
            ligne += (
                f" | Radar/100 — forme:{radar.get('forme','-')}, "
                f"distance:{radar.get('distance','-')}, jockey:{radar.get('jockey','-')}, "
                f"classe:{radar.get('classe','-')}, fraîcheur:{radar.get('fraicheur','-')}"
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
        "reconnu et confiant, qui échange avec les abonnés d'une "
        "application de pronostics Quinté+. Tu n'es pas un menu de "
        "commandes : tu comprends et réponds naturellement à n'importe "
        "quelle question, même formulée différemment de ce qui est prévu, "
        "et tu maîtrises toutes les statistiques disponibles (cotes, "
        "tendances de cote, indices AZ et Premium, driver/jockey, "
        "entraîneur, musique, forme, régularité, corde, ferrage, gains "
        "carrière).\n\n"
        "Règles :\n"
        "- Réponds en français, avec l'assurance d'un vrai professionnel "
        "du turf qui connaît sa course sur le bout des doigts — direct, "
        "net, sans formules d'hésitation inutiles (\"je pense que\", "
        "\"peut-être\" à éviter sauf incertitude réelle sur la donnée).\n"
        "- Appuie-toi uniquement sur les données de course fournies "
        "ci-dessous. N'invente jamais de cote, de nom de cheval, de "
        "jockey ou de résultat qui n'y figure pas.\n"
        "- Si une information précise demandée n'est pas dans les "
        "données (ex. un historique détaillé non fourni), dis-le "
        "honnêtement plutôt que de l'inventer — mais formule ça comme "
        "une limite ponctuelle, pas comme une excuse générale.\n"
        "- Utilise activement TOUTES les statistiques à ta disposition : "
        "la musique et la forme récente, le driver, l'entraîneur, la "
        "corde, le ferrage, les tendances de cote (argent qui rentre ou "
        "sort) sont autant d'arguments à mobiliser, pas seulement "
        "l'indice AZ brut.\n"
        "- Argumente, compare, nuance, donne un vrai avis tranché "
        "d'analyste — pas seulement réciter des chiffres.\n"
        "- Reste concis (quelques phrases ou un court paragraphe), sauf "
        "si la question demande explicitement plus de détail.\n\n"
        "=== DONNÉES DE LA COURSE ===\n"
        f"{_resume_course(contexte)}\n\n"
        "=== CLASSEMENT AZ TURF PRO (toutes statistiques disponibles) ===\n"
        f"{_resume_classement(contexte)}\n\n"
        "=== TICKETS GÉNÉRÉS ===\n"
        f"{_resume_tickets(contexte)}\n"
    )


def _historique_pour_ia(historique: list, limite: int = 12) -> list:
    """Normalise l'historique envoyé par le frontend (chatbot.js) vers un
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
# APPELS AUX MODÈLES
# =====================================

def _appeler_claude(system_prompt: str, messages: list, question: str) -> str:
    raise RuntimeError("Claude est désactivé : mode autonome AZ Turf Pro.")


def _appeler_openai(system_prompt: str, messages: list, question: str) -> str:
    raise RuntimeError("OpenAI est désactivé : mode autonome AZ Turf Pro.")

# =====================================
# REPLI SANS IA (aucune clé configurée / échec des deux appels)
# =====================================

# =====================================
# MOTEUR D'ANALYSE RÉEL (raisonnement sur les données, sans IA externe)
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
    """Score IA 0-10 VOLONTAIREMENT INDÉPENDANT de l'indice AZ/Premium
    (n'utilise jamais indice_az ni indice_premium). Recalcule sa propre
    opinion à partir des statistiques brutes, pour offrir une vraie
    seconde lecture — c'est ce qui permet une comparaison "Ticket IA"
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
    terrain_score = 5.0  # pas de donnée terrain fiable et systématique disponible

    cote = _cote(cheval)
    cote_confiance = 5.0 if cote <= 1 else max(0.0, min(10.0, 10.0 / (1.0 + _math.log(cote))))

    score = (
        forme * 0.25 + regularite * 0.20 + distance_score * 0.12 + terrain_score * 0.08 +
        jockey_score * 0.10 + experience * 0.07 + gains_score * 0.08 + cote_confiance * 0.10
    )
    return round(max(0.0, min(10.0, score)), 2)


# Alias de compatibilité avec les anciennes versions du module.
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
        confiance = "Il se détache nettement du reste du peloton — un favori solide."
    elif ecart is not None and ecart >= 1.5:
        confiance = "Il devance ses poursuivants avec une marge correcte, mais sans être hors de portée."
    elif ecart is not None:
        confiance = f"L'écart avec le N°{classement[1].get('numero')} n'est que de {ecart} points — course ouverte, ce favori peut être renversé."
    else:
        confiance = "Seul cheval réellement analysé sur cette course."

    badges = top.get("badges") if isinstance(top.get("badges"), list) else []
    libelles = [b.get("libelle") for b in badges if isinstance(b, dict) and b.get("libelle")]
    argument_badges = f" Arguments supplémentaires : {', '.join(libelles)}." if libelles else ""

    jours_repos = top.get("jours_depuis_derniere_course")
    note_repos = ""
    if isinstance(jours_repos, (int, float)):
        if jours_repos > 90:
            note_repos = f" Attention : {int(jours_repos)} jours sans courir, la fraîcheur est incertaine."
        elif jours_repos <= 30:
            note_repos = f" Repos idéal ({int(jours_repos)}j) pour être au top."

    return (
        f"🎯 **Favori AZ Turf Pro** : N°{top.get('numero')} **{top.get('nom')}** "
        f"(Indice AZ {top.get('indice_az', '-')}, cote {top.get('cote', '-')}). {confiance}"
        f"{argument_badges}{note_repos}"
    )


def _analyser_vulnerables(classement: list) -> str:
    if len(classement) < 2:
        return "Pas assez de chevaux analysés pour juger d'une vulnérabilité."

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
                raisons.append(f"talonné de près par le N°{suivant.get('numero')} (écart de {round(ecart, 2)} pts)")
            if cote_elevee:
                raisons.append(f"une cote qui reste élevée ({cheval.get('cote')})")
            vulnerables.append(f"- N°{cheval.get('numero')} **{cheval.get('nom')}** : {', '.join(raisons)}.")

    if not vulnerables:
        return "Aucun favori ne semble particulièrement vulnérable sur cette course — le classement paraît net."
    return "⚠️ **Favoris à surveiller** :\n" + "\n".join(vulnerables)


def _comparer_chevaux(classement: list, num_a: str, num_b: str) -> str:
    a = _trouver_cheval(classement, num_a)
    b = _trouver_cheval(classement, num_b)
    if not a or not b:
        manquant = num_a if not a else num_b
        return f"Je ne trouve pas le numéro {manquant} dans le classement de cette course."

    rang_a = classement.index(a) + 1
    rang_b = classement.index(b) + 1
    diff = round(_indice(a) - _indice(b), 2)

    if diff > 0:
        verdict = f"N°{num_a} **{a.get('nom')}** ressort devant, avec {abs(diff)} points d'indice AZ de plus (rang {rang_a} vs {rang_b})."
    elif diff < 0:
        verdict = f"N°{num_b} **{b.get('nom')}** ressort devant, avec {abs(diff)} points d'indice AZ de plus (rang {rang_b} vs {rang_a})."
    else:
        verdict = "Les deux chevaux sont à égalité d'indice — un vrai coin de table."

    return (
        f"**N°{num_a} {a.get('nom')}** (indice {a.get('indice_az', '-')}, cote {a.get('cote', '-')}) "
        f"vs **N°{num_b} {b.get('nom')}** (indice {b.get('indice_az', '-')}, cote {b.get('cote', '-')}) : {verdict}"
    )


def _classement_ia(classement: list) -> list:
    """Reclasse les chevaux selon le score expert indépendant (pas
    l'indice AZ) — c'est ce classement que les tickets IA utilisent."""
    copie = [dict(c) for c in classement]
    for c in copie:
        c["_expert_score"] = _score_expert_independant(c)
    return sorted(copie, key=lambda c: c["_expert_score"], reverse=True)


def _ticket_prudent(classement: list) -> str:
    """Ne retient que les valeurs sûres selon le score expert indépendant :
    les mieux notés ET les plus réguliers, sans aucun outsider."""
    if len(classement) < 3:
        return "Pas assez de chevaux analysés pour construire un ticket prudent."
    classe = _classement_ia(classement)
    surs = sorted(classe, key=lambda c: (-c["_expert_score"], -float(c.get("regularite") or 0), _cote(c)))[:5]
    nums = [str(c.get("numero")) for c in surs]
    return (
        "🛡️ **Ticket expert autonome (prudent)** : " + " - ".join(nums) + "\n"
        f"Base expert : N°{surs[0].get('numero')} {surs[0].get('nom', '')} (score expert {surs[0]['_expert_score']}/10).\n"
        "Priorité : forme, régularité — aucun outsider, calcul séparé de l'indice AZ."
    )


def _ticket_speculatif(classement: list) -> str:
    """Privilégie les outsiders à cote élevée dont le score IA
    indépendant reste correct — recherche du gros rapport."""
    if len(classement) < 3:
        return "Pas assez de chevaux analysés pour construire un ticket spéculatif."
    classe = _classement_ia(classement)
    outsiders = [c for c in classe if _cote(c) >= 12]
    outsiders = sorted(outsiders, key=lambda c: -c["_expert_score"])[:3]
    solides = [c for c in classe if c not in outsiders][:2]
    combinaison = (outsiders + solides)[:5]
    nums = [str(c.get("numero")) for c in combinaison]
    outsiders_txt = (
        "\n".join(f"• N°{c.get('numero')} {c.get('nom','')} — cote {_cote(c)} — score expert {c['_expert_score']}/10" for c in outsiders)
        if outsiders else "• Aucun outsider à cote ≥ 12 avec des données suffisantes."
    )
    return (
        "🎲 **Ticket expert autonome (spéculatif, risqué)** : " + " - ".join(nums) + "\n\n"
        f"Outsiders réellement retenus :\n{outsiders_txt}\n\n"
        "Accepte davantage de risque — ne recopie pas le ticket AZ Turf Pro."
    )


def _ticket_mix(classement: list) -> str:
    """Équilibre selon le score expert indépendant : les meilleures valeurs
    sûres + 1-2 outsiders, sans tout miser sur un seul profil."""
    if len(classement) < 4:
        return "Pas assez de chevaux analysés pour construire un ticket mixte."
    classe = _classement_ia(classement)
    surs = classe[:3]
    surs_numeros = {c.get("numero") for c in surs}
    outsiders = [c for c in classe if _cote(c) >= 8 and c.get("numero") not in surs_numeros][:2]
    if not outsiders:
        outsiders = [c for c in classe if c.get("numero") not in surs_numeros][-2:]
    combinaison = surs + outsiders
    nums = [str(c.get("numero")) for c in combinaison]
    return (
        "⚖️ **Ticket expert autonome (mix équilibré)** : " + " - ".join(nums) + "\n"
        "Combine les meilleures valeurs sûres (score IA) et 1 à 2 outsiders "
        "pour doser risque et régularité — calcul séparé de l'indice AZ."
    )


def _generer_scenarios(classement: list) -> str:
    if len(classement) < 3:
        return "Pas assez de chevaux analysés pour construire des scénarios."

    favori, second, troisieme = classement[0], classement[1], classement[2]
    outsiders = [c for c in classement if _cote(c) >= 10]
    outsider = outsiders[0] if outsiders else classement[-1]

    return (
        "🛤️ **Deux scénarios possibles** :\n\n"
        f"**Scénario logique** : le favori N°{favori.get('numero')} **{favori.get('nom')}** confirme sa "
        f"place, devant N°{second.get('numero')} **{second.get('nom')}** et N°{troisieme.get('numero')} "
        f"**{troisieme.get('nom')}** — un ordre proche du classement AZ Turf Pro.\n\n"
        f"**Scénario surprise** : N°{outsider.get('numero')} **{outsider.get('nom')}** "
        f"(cote {outsider.get('cote', '-')}) crée la sensation et vient bousculer le favori, "
        "profitant d'un faux rythme ou d'une méforme du leader."
    )


def _fiche_cheval(cheval: dict) -> str:
    driver = cheval.get("driver") or cheval.get("conducteur") or cheval.get("pilote") or cheval.get("jockey") or "-"
    forme = cheval.get("forme")
    regularite = cheval.get("regularite")
    tendance = cheval.get("tendance_cote") or cheval.get("tendance") or "-"

    fiche = (
        f"**N°{cheval.get('numero')} {cheval.get('nom')}** — "
        f"{cheval.get('age', '-')} ans, {cheval.get('sexe', '-')}\n"
        f"- Jockey/Driver : {driver} (réussite {cheval.get('reussite_jockey', '-')}%)\n"
        f"- Entraîneur : {cheval.get('entraineur', '-')} (confiance {cheval.get('confiance_entraineur', '-')})\n"
        f"- Cote : {cheval.get('cote', '-')} (tendance {tendance}) | Indice AZ : {cheval.get('indice_az', '-')} | "
        f"Indice Premium : {cheval.get('indice_premium', '-')}\n"
        f"- Musique (forme récente) : {cheval.get('musique_brute', '-')}"
    )
    if forme is not None:
        fiche += f" — forme {forme}/10"
        if regularite is not None:
            fiche += f", régularité {regularite}/10"
    fiche += (
        f"\n- Gains de carrière : {cheval.get('gains', cheval.get('gains_carriere_brute', '-'))} | "
        f"Nombre de courses : {cheval.get('nombre_courses', '-')}\n"
        f"- Corde : {cheval.get('corde', '-')} | Ferrage : {cheval.get('deferre', '-')}\n"
        f"- Distance de prédilection : {cheval.get('distance_predilection', '-')}m | "
        f"Repos : {cheval.get('jours_depuis_derniere_course', '-')} jours\n"
        f"- Hippodromes favoris : {cheval.get('hippodromes_favoris', '-')}"
    )

    radar = cheval.get("radar") if isinstance(cheval.get("radar"), dict) else {}
    if radar:
        fiche += (
            f"\n- Radar/100 : forme {radar.get('forme', '-')}, distance {radar.get('distance', '-')}, "
            f"jockey {radar.get('jockey', '-')}, classe {radar.get('classe', '-')}, "
            f"fraîcheur {radar.get('fraicheur', '-')}"
        )

    badges = cheval.get("badges") if isinstance(cheval.get("badges"), list) else []
    libelles = [b.get("libelle") for b in badges if isinstance(b, dict) and b.get("libelle")]
    if libelles:
        fiche += f"\n- Badges : {', '.join(libelles)}"

    return fiche


def _points_forts_faibles(cheval: dict) -> str:
    """Analyse réelle des points forts/faibles à partir du radar 5
    axes déjà calculé par le moteur — pas de texte générique."""
    radar = cheval.get("radar") if isinstance(cheval.get("radar"), dict) else {}
    if not radar:
        return (f"N°{cheval.get('numero')} **{cheval.get('nom')}** : pas de radar "
                f"détaillé disponible pour cette course.")

    libelles = {
        "forme": "la forme récente", "distance": "l'aptitude à la distance du jour",
        "jockey": "le duo jockey/entraîneur", "classe": "le niveau de classe",
        "fraicheur": "la fraîcheur (repos)",
    }
    valides = {k: v for k, v in radar.items() if isinstance(v, (int, float))}
    if not valides:
        return f"N°{cheval.get('numero')} **{cheval.get('nom')}** : radar incomplet."

    meilleur = max(valides, key=valides.get)
    pire = min(valides, key=valides.get)

    return (
        f"N°{cheval.get('numero')} **{cheval.get('nom')}** :\n"
        f"✅ Point fort : {libelles.get(meilleur, meilleur)} ({valides[meilleur]}/100)\n"
        f"⚠️ Point faible : {libelles.get(pire, pire)} ({valides[pire]}/100)"
    )


# =====================================
# RECHERCHE INDÉPENDANTE EN DIRECT (PMU.fr)
# =====================================
#
# Contrairement au contexte habituel (calculé une fois par le moteur
# AZ au début de la conversation), cette fonction relance un VRAI
# appel réseau vers PMU.fr au moment précis de la question, pour les
# demandes qui portent explicitement sur l'évolution en direct
# (cotes, dernière minute). Best-effort : échec toujours silencieux,
# ne casse jamais la conversation si PMU.fr est indisponible.

# =====================================
# ANALYSE RÉTROSPECTIVE (courses passées + arrivées réelles)
# =====================================
#
# S'appuie sur learning.py / historique_az.json, déjà alimenté
# automatiquement par engine.py à chaque /api/analyse. Permet de
# vraiment expliquer si la sélection AZ a fonctionné ou non, en
# comparant la sélection au classement d'arrivée officiel PMU.
#
# ⚠️ LIMITE CONNUE (déjà documentée dans api.py) : si l'hébergement
# Render ne dispose pas d'un disque persistant, ce fichier peut être
# remis à zéro à chaque redéploiement — l'historique ne survivrait
# alors pas dans le temps. À vérifier concrètement sur ton plan
# Render si cette fonctionnalité te semble incomplète en usage réel.

def _analyser_historique() -> str | None:
    try:
        from learning import lire_historique

        entrees = [e for e in lire_historique() if isinstance(e, dict)]
        avec_arrivee = [e for e in entrees if e.get("arrivee")]
        if not avec_arrivee:
            return None

        derniere = avec_arrivee[-1]
        course = derniere.get("course") or {}
        arrivee = derniere.get("arrivee") or []
        selection_az = derniere.get("selection_az") or []
        favori = derniere.get("favori") or {}

        gagnant_reel = str(arrivee[0]) if arrivee else None
        numero_favori = str(favori.get("numero")) if favori.get("numero") is not None else None

        lignes = [
            f"📋 **Dernière course analysée** : {course.get('hippodrome', '-')} "
            f"({course.get('date', '-')}, {course.get('reunion', '-')}/{course.get('course_numero', '-')})",
            f"Notre sélection : {' - '.join(str(n) for n in selection_az[:7])}",
            f"Arrivée réelle : {' - '.join(str(n) for n in arrivee[:7])}" if arrivee else "Arrivée réelle : non disponible pour le moment.",
        ]

        if gagnant_reel and numero_favori:
            if gagnant_reel == numero_favori:
                lignes.append(
                    f"✅ Notre favori (N°{numero_favori}) a remporté la course — "
                    "sélection gagnante confirmée."
                )
            elif gagnant_reel in [str(n) for n in selection_az[:7]]:
                rang = [str(n) for n in selection_az[:7]].index(gagnant_reel) + 1
                lignes.append(
                    f"⚠️ Le vrai gagnant (N°{gagnant_reel}) figurait dans notre sélection "
                    f"(en position {rang}), mais pas en tête — le favori N°{numero_favori} "
                    "n'a pas confirmé sa cote de sortie."
                )
            else:
                lignes.append(
                    f"❌ Le gagnant réel (N°{gagnant_reel}) ne figurait pas dans notre "
                    f"sélection — notre favori N°{numero_favori} n'était pas le bon choix "
                    "sur cette course, un imprévu (forme du jour, tactique de course, "
                    "terrain) a rebattu les cartes."
                )

        return "\n".join(lignes)
    except Exception:
        return None


def _analyser_course_passee(question: str) -> str | None:
    """Regarde l'historique réel (learning.py) pour répondre sur une
    course passée : sa sélection, et — si l'arrivée officielle a été
    récupérée entre-temps — pourquoi ça a marché ou pas, en comparant
    concrètement les numéros joués aux numéros arrivés."""
    import re as _re
    try:
        from learning import lire_historique
    except Exception:
        return None

    q = question.lower()
    if not any(k in q for k in ["hier", "course passée", "course passee", "dernière course",
                                  "derniere course", "pourquoi ça a marché", "pourquoi ca a marche",
                                  "pourquoi ça n'a pas marché", "résultat", "resultat", "arrivée", "arrivee"]):
        return None

    try:
        historique = lire_historique() or []
    except Exception:
        return None
    if not historique:
        return "Aucun historique de course n'est encore enregistré."

    # "hier" ou pas de date précisée -> la plus récente course TERMINÉE (avec arrivée connue)
    entrees_avec_arrivee = [e for e in historique if isinstance(e, dict) and e.get("arrivee")]
    if not entrees_avec_arrivee:
        return ("Aucune course passée n'a encore d'arrivée officielle enregistrée — "
                "je ne peux pas encore analyser de résultat.")

    entree = entrees_avec_arrivee[-1]  # la plus récente avec arrivée connue
    arrivee = [str(n) for n in entree.get("arrivee", [])]
    selection = [str(n) for n in (entree.get("selection_az") or [])]
    hippodrome = entree.get("hippodrome", "-")
    date = entree.get("date", "-")

    if not selection:
        return f"L'arrivée du {date} à {hippodrome} était {' - '.join(arrivee)}, mais aucune sélection n'a été enregistrée pour comparer."

    touches = [n for n in selection if n in arrivee]
    manques = [n for n in selection if n not in arrivee]
    nb_touches = len(touches)

    if nb_touches >= 3:
        verdict = "Un bon résultat : la sélection a largement recoupé l'arrivée réelle."
    elif nb_touches >= 1:
        verdict = "Un résultat partiel : quelques chevaux de la sélection sont sortis, pas tous."
    else:
        verdict = "Aucun cheval de la sélection n'est sorti dans l'arrivée — la course a déjoué le classement AZ."

    return (
        f"📋 **Course du {date} — {hippodrome}**\n"
        f"Arrivée officielle : {' - '.join(arrivee)}\n"
        f"Sélection AZ jouée : {' - '.join(selection)}\n"
        f"Chevaux sortis parmi la sélection : {', '.join(touches) if touches else 'aucun'} "
        f"({nb_touches}/{len(selection)})\n"
        f"{verdict}"
    )


def _analyser_course_demain(question: str, course_actuelle: dict) -> str | None:
    """Tente de récupérer en direct le programme PMU du lendemain.
    Best-effort : PMU ne publie pas toujours les partants aussi loin
    à l'avance ; échoue silencieusement si l'info n'existe pas encore."""
    q = question.lower()
    if "demain" not in q:
        return None

    try:
        from pmu_source import charger_course_pmu
        from datetime import datetime, timedelta

        demain = (datetime.now() + timedelta(days=1)).strftime("%d%m%Y")
        course_demain = charger_course_pmu(demain)

        if not course_demain or not isinstance(course_demain, dict) or not course_demain.get("chevaux"):
            return ("Le programme PMU de demain n'est pas encore publié ou disponible "
                    "à cet instant — réessayez plus tard, généralement il sort la veille "
                    "au soir.")

        nb = len(course_demain.get("chevaux", []))
        hippodrome = course_demain.get("hippodrome", "-")
        return (
            f"📅 **Programme PMU de demain trouvé** : {hippodrome}, {nb} partants "
            f"annoncés. L'analyse AZ Turf Pro complète (indices, tickets) n'est "
            f"générée qu'au moment où la course devient celle du jour — je peux "
            f"seulement confirmer sa disponibilité pour l'instant."
        )
    except Exception:
        return ("Je n'ai pas pu vérifier le programme de demain à l'instant "
                "(PMU.fr indisponible ou pas encore publié).")


def _rafraichir_cotes_pmu_direct(course_reference: dict) -> str | None:
    try:
        from pmu_source import charger_course_pmu

        date = course_reference.get("date")
        reunion = course_reference.get("reunion")
        course_numero = course_reference.get("course_numero")

        course_fraiche = charger_course_pmu(date, reunion, course_numero)
        if not course_fraiche or not isinstance(course_fraiche, dict):
            return None

        chevaux = course_fraiche.get("chevaux", [])
        if not chevaux:
            return None

        lignes = []
        for cheval in chevaux[:10]:
            if not isinstance(cheval, dict):
                continue
            tendance = cheval.get("tendance_cote") or cheval.get("tendance") or "-"
            lignes.append(
                f"N°{cheval.get('numero', '?')} {cheval.get('nom', '?')} : "
                f"cote actuelle {cheval.get('cote', '-')} (tendance {tendance})"
            )
        if not lignes:
            return None

        return "[Cotes PMU.fr rafraîchies en direct]\n" + "\n".join(lignes)
    except Exception:
        return None


def _extraire_tickets(tickets: dict) -> dict:
    """Normalise la structure RÉELLE de tickets renvoyée par
    quinte.py (generer_tickets_az), documentée ici une bonne fois
    pour toutes pour éviter les erreurs de structure récurrentes :

    tickets = {
      "gratuit": {
        "quinte": [7 numéros],
        "deux_sur_quatre": [4 numéros],
        "couple_place": [2 numéros],
      },
      "premium": {
        "selection_quinte": [8 numéros],
        "quinte": [6 numéros],
        "quarte": [5 numéros],
        "trio": [3 numéros],
        "couple_gagnant_place": [[a,b],[a,c],[b,c]],
        "champ_reduit": {"format", "bases", "complements", "disponible"},
        "ticket_derniere_minute": {"selection", "joker", "format"},
      }
    }
    Tous les numéros sont des CHAÎNES BRUTES (pas des objets/dicts).
    """
    tickets = tickets or {}
    gratuit = tickets.get("gratuit") or {}
    premium = tickets.get("premium") or {}

    def _liste(valeur):
        return valeur if isinstance(valeur, list) else []

    return {
        "quinte_gratuit": _liste(gratuit.get("quinte")),
        "deux_sur_quatre": _liste(gratuit.get("deux_sur_quatre")),
        "couple_place_gratuit": _liste(gratuit.get("couple_place")),
        "selection_quinte_premium": _liste(premium.get("selection_quinte")),
        "quinte_premium": _liste(premium.get("quinte")),
        "quarte_premium": _liste(premium.get("quarte")),
        "trio_premium": _liste(premium.get("trio")),
        "couple_gagnant_place": _liste(premium.get("couple_gagnant_place")),
        "champ_reduit": premium.get("champ_reduit") if isinstance(premium.get("champ_reduit"), dict) else {},
        "derniere_minute": premium.get("ticket_derniere_minute") if isinstance(premium.get("ticket_derniere_minute"), dict) else {},
    }


# =====================================
# COUCHE CONVERSATIONNELLE AUTONOME V17
# =====================================

_CONVERSATION_ETATS = {}


def _normaliser_texte(texte: str) -> str:
    import unicodedata
    texte = str(texte or "").strip().lower()
    texte = "".join(c for c in unicodedata.normalize("NFD", texte) if unicodedata.category(c) != "Mn")
    # Les apostrophes et tirets ne doivent pas empêcher la reconnaissance
    # de formulations comme « qu’on », « veux-tu » ou « comment vas-tu ».
    texte = re.sub(r"[’'\-_/]+", " ", texte)
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()


def _extraire_numeros_question(question: str) -> list:
    return re.findall(r"(?<!\d)(\d{1,2})(?!\d)", str(question or ""))


def _detecter_intention_conversation(question: str) -> str:
    q = _normaliser_texte(question)
    if not q:
        return "vide"
    if re.search(r"\b(bonjour|salut|bonsoir|coucou|hello|bjr|bonne journee)\b", q):
        return "salutation"
    if any(x in q for x in ("comment allez vous", "comment vas tu", "comment va tu", "ca va", "tu vas bien", "vous allez bien")):
        return "bien_etre"
    if any(x in q for x in ("merci", "merci beaucoup", "super merci", "parfait merci")):
        return "remerciement"
    if any(x in q for x in ("qui es tu", "qui etes vous", "que peux tu faire", "que savez vous faire", "aide moi", "comment ca marche")):
        return "aide"
    if any(x in q for x in ("sur quoi travailler", "sur quoi veux tu", "on travaille sur quoi", "que fait on aujourd hui", "quoi faire aujourd hui", "qu est ce qu on fait")):
        return "orientation"
    if any(x in q for x in ("bonne chance", "a bientot", "a plus", "au revoir", "bye")):
        return "au_revoir"
    return "autre"


def _etat_conversation(historique: list) -> dict:
    dernier_user = ""
    dernier_assistant = ""
    for e in reversed(historique or []):
        if not isinstance(e, dict):
            continue
        role = str(e.get("role") or "").lower()
        contenu = e.get("content") or e.get("question") or e.get("reponse") or ""
        if role in ("user", "utilisateur") and not dernier_user:
            dernier_user = str(contenu)
        elif role in ("assistant", "bot", "ia") and not dernier_assistant:
            dernier_assistant = str(contenu)
        if dernier_user and dernier_assistant:
            break
    return {"dernier_user": dernier_user, "dernier_assistant": dernier_assistant, "derniers_numeros": _extraire_numeros_question(dernier_user)}


def _reponse_conversation_naturelle(question: str, contexte: dict, historique: list = None) -> str | None:
    intention = _detecter_intention_conversation(question)
    course = (contexte or {}).get("course") or {}
    moteur = (contexte or {}).get("moteur") or {}
    classement = moteur.get("classement") or []
    nom_course = course.get("course") or "la course du jour"
    hippodrome = course.get("hippodrome")

    if intention == "salutation":
        q_norm = _normaliser_texte(question)
        demande_turf = any(k in q_norm for k in (
            "favori", "quinte", "quinte", "quarté", "trio", "cheval", "cote",
            "course", "analyse", "ticket", "compare", "outsider", "pronostic",
            "terrain", "piste", "presse", "joker", "couple"
        ))
        if demande_turf:
            return None
        lieu = f" à {hippodrome}" if hippodrome else ""
        if classement:
            return ("👋 Bonjour ! Heureux de vous retrouver. "
                    f"Je suis prêt à travailler avec vous{lieu}. "
                    "Nous pouvons étudier la course, un cheval, les cotes ou préparer un ticket. "
                    "**Sur quoi souhaitez-vous qu'on travaille aujourd'hui ?**")
        return ("👋 Bonjour ! Heureux de vous retrouver. "
                "Je suis prêt à travailler avec vous sur les courses. "
                "**Sur quoi souhaitez-vous qu'on travaille aujourd'hui ?**")

    if intention == "bien_etre":
        return ("😊 Je vais très bien, merci ! Et je suis prêt pour l'analyse. "
                "On peut regarder le Quinté, étudier un cheval, comparer deux partants "
                "ou préparer une sélection. **Qu'est-ce qui vous intéresse ?**")

    if intention == "remerciement":
        return ("Avec plaisir ! 👍 On continue quand vous voulez. "
                "On peut maintenant approfondir la course, un cheval ou le ticket.")

    if intention == "aide":
        return ("🏇 **Je suis votre assistant turf AZ Turf Pro.**\n\n"
                "Je peux analyser la course et les partants, donner le favori, repérer les favoris vulnérables, "
                "comparer des chevaux, étudier les cotes, la presse et la piste, proposer des scénarios, "
                "préparer les tickets et revenir sur les résultats passés.\n\n"
                "Parlez-moi simplement : **« que penses-tu du 5 ? »**, **« compare le 5 et le 7 »** "
                "ou **« prépare-moi un Quinté »**.")

    if intention == "orientation":
        if classement:
            top = classement[0]
            return (f"Très bien. Pour **{nom_course}**, les données des partants sont disponibles. "
                    f"Le classement AZ place actuellement le N°{top.get('numero')} **{top.get('nom', 'en tête')}** en première position. "
                    "On peut partir de là ou examiner la course sous un autre angle. "
                    "**Vous préférez : favori, risques, comparaison ou ticket ?**")
        return "Très bien. Je suis prêt. Dès que les données de la course sont disponibles, nous pouvons commencer par le favori, les partants ou le ticket."

    if intention == "au_revoir":
        return "À bientôt ! 👋 Nous pourrons reprendre l'analyse quand vous le souhaitez."

    return None


def _reponse_secours(question: str, contexte: dict) -> str:
    import re as _re

    q = question.lower().strip()
    moteur = (contexte or {}).get("moteur", {})
    classement = moteur.get("classement", [])
    tickets = moteur.get("tickets", {})
    course = (contexte or {}).get("course", {}) or {}

    # --- Comparaison "Expert autonome" vs "Ticket AZ Turf Pro" ---
    if "compar" in q and any(k in q for k in ["az turf", "az", "premium", "ticket ia", "l'ia", "ia et"]):
        classe_ia = _classement_ia(classement)
        ticket_ia = [str(c.get("numero")) for c in classe_ia[:5]]
        tk_tmp = _extraire_tickets(tickets)
        ticket_az = tk_tmp["selection_quinte_premium"] or tk_tmp["quinte_premium"] or tk_tmp["quinte_gratuit"]
        return (
            "⚔️ **Comparaison Expert autonome / Ticket AZ Turf Pro**\n\n"
            f"🤖 Expert autonome : **{' - '.join(ticket_ia)}**\n"
            f"🏆 Ticket AZ Turf Pro : **{' - '.join(ticket_az) if ticket_az else 'non disponible'}**\n\n"
            "Les deux sélections sont calculées séparément : le moteur expert n'utilise jamais "
            "l'indice AZ, elle recalcule sa propre opinion à partir des statistiques brutes."
        )

    # --- Comparaison entre deux profils de ticket (prudent/spéculatif/mix/gratuit) ---
    if "compar" in q and "ticket" in q:
        profils_cites = []
        if any(k in q for k in ["prudent", "sûr", "sécurisé"]):
            profils_cites.append(("Prudent", _ticket_prudent(classement)))
        if any(k in q for k in ["spéculat", "speculat", "risqué", "risque", "audacieux"]):
            profils_cites.append(("Spéculatif", _ticket_speculatif(classement)))
        if any(k in q for k in ["mix", "équilibré", "equilibre"]):
            profils_cites.append(("Mix", _ticket_mix(classement)))
        if "premium" in q:
            tk_tmp = _extraire_tickets(tickets)
            if tk_tmp["quinte_premium"]:
                profils_cites.append(("Quinté Premium", "💎 " + " - ".join(tk_tmp["quinte_premium"])))
        if "gratuit" in q:
            tk_tmp = _extraire_tickets(tickets)
            if tk_tmp["quinte_gratuit"]:
                profils_cites.append(("Quinté Gratuit", "💡 " + " - ".join(tk_tmp["quinte_gratuit"])))

        if len(profils_cites) >= 2:
            texte = "🔍 **Comparaison de tickets**\n\n"
            for nom, contenu in profils_cites[:2]:
                texte += f"**{nom}** :\n{contenu}\n\n"
            return texte.strip()

        return ("Pour comparer, précisez deux profils parmi : prudent, spéculatif, mix, "
                "Quinté gratuit ou Quinté Premium — par exemple \"compare le ticket "
                "prudent et le ticket spéculatif\".")

    # --- Analyse de valeur (probabilité modèle vs cote implicite) ---
    if any(k in q for k in ["value", "valeur", "sous-coté", "sous cote", "sous-cote"]):
        import math as _math
        classe_ia = _classement_ia(classement)
        candidats = []
        for c in classe_ia:
            cote = _cote(c)
            if cote >= 8:
                implicite = 1.0 / cote
                proba_modele = max(0.02, min(0.35, 0.02 + (c["_expert_score"] / 10.0) * 0.22))
                ecart = proba_modele - implicite
                candidats.append((ecart, c, proba_modele, implicite))
        candidats.sort(key=lambda x: x[0], reverse=True)
        if not candidats:
            return "Aucun cheval à cote suffisamment élevée (≥8) pour une analyse de valeur sur cette course."
        lignes = [
            f"• N°{c.get('numero')} {c.get('nom','')} — cote {cote:.1f} — proba. modèle {pm*100:.1f}% — "
            f"implicite {pi*100:.1f}% — écart {ecart*100:+.1f} pts"
            for ecart, c, pm, pi in candidats[:5]
            for cote in [_cote(c)]
        ]
        return (
            "💰 **Meilleures valeurs (probabilité modèle vs cote implicite)**\n" +
            "\n".join(lignes) +
            "\n\n⚠️ L'écart est un indicateur du modèle, pas une probabilité garantie."
        )

    # --- Tickets par profil de risque (prudent / spéculatif / mix) ---
    if any(k in q for k in ["prudent", "sûr", "sur ", "sécurisé", "securise", "sans risque"]):
        return _ticket_prudent(classement)
    if any(k in q for k in ["spéculat", "speculat", "risqué", "risque", "audacieux", "gros rapport"]):
        return _ticket_speculatif(classement)
    if any(k in q for k in ["mix", "équilibré", "equilibre", "équilibre"]):
        return _ticket_mix(classement)

    # --- Course passée : sélection vs arrivée réelle ---
    reponse_passe = _analyser_course_passee(question)
    if reponse_passe:
        return reponse_passe

    # --- Course de demain (best-effort PMU) ---
    reponse_demain = _analyser_course_demain(question, course)
    if reponse_demain:
        return reponse_demain

    # --- Recherche indépendante en direct : cotes/dernière minute ---
    if any(k in q for k in ["cote a boug", "cote a change", "evolution", "évolution", "en direct", "temps réel", "temps reel", "à jour", "a jour", "actualise", "actualisé"]):
        rafraichi = _rafraichir_cotes_pmu_direct(course)
        if rafraichi:
            return "🔄 " + rafraichi
        return ("Je n'ai pas pu récupérer une mise à jour en direct depuis PMU.fr à "
                "l'instant. Voici les dernières données connues à la place.\n\n"
                + _analyser_favori(classement))

    # --- Analyse rétrospective : dernière course, arrivée réelle ---
    if any(k in q for k in ["ça a marché", "ca a marche", "résultat", "resultat", "arrivée", "arrivee", "pourquoi ça n'a pas marché", "pourquoi ca n'a pas marche", "course précédente", "course precedente", "dernière course", "derniere course", "bilan"]):
        analyse = _analyser_historique()
        if analyse:
            return analyse
        return ("Aucune course passée avec une arrivée connue n'est disponible pour "
                "le moment — soit aucune analyse précédente n'a été enregistrée, soit "
                "l'arrivée officielle n'a pas encore pu être récupérée.")

    # --- Limite connue : course de demain ---
    if "demain" in q and any(k in q for k in ["course", "analyse", "analyser"]):
        return ("Je ne peux pas encore analyser la course de demain — cette "
                "fonctionnalité dépend d'une donnée supplémentaire non encore "
                "branchée (le programme PMU du lendemain). Je peux en revanche "
                "analyser la course du jour en cours, ou revenir sur les "
                "précédentes avec leur résultat réel.")

    # --- Recherche indépendante en direct : terrain/piste (France Galop) ---
    if any(k in q for k in ["terrain", "piste", "état du sol", "etat du sol", "souple", "lourd", "bon terrain"]):
        try:
            from france_galop_source import obtenir_complement_france_galop
            complement = obtenir_complement_france_galop(course.get("hippodrome", ""), course.get("discipline", ""))
        except Exception:
            complement = None
        if complement:
            return "🔄 " + complement
        return ("Je n'ai pas d'information à jour sur l'état du terrain pour cette "
                "course pour le moment.")

    # --- Salutations ---
    if any(k in q for k in ["bonjour", "salut", "bonsoir", "hello", "coucou"]):
        return ("👋 Bonjour ! Je suis AZ Turf Pro, votre pronostiqueur hippique. "
                "Je peux analyser le favori, repérer les favoris vulnérables, "
                "comparer deux chevaux, proposer des scénarios de course, "
                "expliquer la position d'un cheval précis, donner le meilleur "
                "duo ou la sélection Quinté. Posez votre question !")

    # --- Comparaison de deux chevaux, ex. "compare le 3 et le 7" ---
    numeros_cites = _re.findall(r"\b(\d{1,2})\b", q)
    if len(numeros_cites) >= 2 and any(k in q for k in ["compar", " ou ", "vs", "mieux que", "contre"]):
        return _comparer_chevaux(classement, numeros_cites[0], numeros_cites[1])

    # --- Favoris vulnérables ---
    if any(k in q for k in ["vulnérable", "vulnerable", "fragile", "battable", "renverser", "se méfier", "se mefier", "méfier"]):
        return _analyser_vulnerables(classement)

    # --- Scénarios de course ---
    if "scénario" in q or "scenario" in q:
        return _generer_scenarios(classement)

    # --- Points forts / points faibles d'un cheval (radar) ---
    if numeros_cites and any(k in q for k in ["point fort", "points fort", "point faible", "points faible", "atout", "faiblesse", "avantage", "handicap de"]):
        cheval = _trouver_cheval(classement, numeros_cites[0])
        if cheval:
            return _points_forts_faibles(cheval)
        return f"Je ne trouve pas le numéro {numeros_cites[0]} dans le classement de cette course."

    # --- Statistiques précises d'un cheval : jockey, musique, gains, corde... ---
    if numeros_cites and any(k in q for k in ["jockey", "driver", "entraineur", "entraîneur", "musique", "forme", "gains", "corde", "ferrage", "déferré", "deferre", "âge", "age", "fiche", "stat", "monte", "pilote", "qui monte"]):
        cheval = _trouver_cheval(classement, numeros_cites[0])
        if cheval:
            return _fiche_cheval(cheval)
        return f"Je ne trouve pas le numéro {numeros_cites[0]} dans le classement de cette course."

    # --- Cheval précis, ex. "pourquoi enlever/exclure le 4 ?" ---
    if numeros_cites and any(k in q for k in ["pourquoi", "enlever", "exclure", "éliminer", "eliminer", "sortir", "numero", "numéro", "cheval", "n°"]):
        numero = numeros_cites[0]
        cheval = _trouver_cheval(classement, numero)
        if cheval:
            rang = classement.index(cheval) + 1
            if rang <= 3:
                jugement = "Il fait partie du trio de tête — un choix cohérent."
            else:
                jugement = "Son indice est nettement en retrait par rapport aux chevaux devant lui, ce qui justifie sa position."
            return (
                f"N°{numero} **{cheval.get('nom')}** est classé **{rang}ᵉ** par AZ Turf Pro "
                f"(Indice AZ {cheval.get('indice_az', '-')}, cote {cheval.get('cote', '-')}). "
                f"{jugement}"
            )
        return f"Je ne trouve pas le numéro {numero} dans le classement de cette course."

    tk = _extraire_tickets(tickets)

    # --- Meilleur duo / couplé gagnant-placé ---
    if any(k in q for k in ["duo", "couple", "couplé", "gagnant placé", "gagnant/placé"]):
        if tk["couple_gagnant_place"]:
            paire = tk["couple_gagnant_place"][0]
            if isinstance(paire, list) and len(paire) >= 2:
                return f"🤝 **Meilleur duo (Couplé Gagnant/Placé Premium)** : N°{paire[0]} - N°{paire[1]}."
        if len(tk["couple_place_gratuit"]) >= 2:
            return f"🤝 **Meilleur duo conseillé** : N°{tk['couple_place_gratuit'][0]} - N°{tk['couple_place_gratuit'][1]}."
        if len(classement) >= 2:
            a, b = classement[0], classement[1]
            return f"🤝 **Meilleur duo (top 2 du classement)** : N°{a.get('numero')} {a.get('nom')} et N°{b.get('numero')} {b.get('nom')}."
        return "Aucun duo ne peut être calculé pour le moment."

    # --- Quarté ---
    if "quarté" in q or "quarte" in q:
        if tk["quarte_premium"]:
            return "🎯 **Quarté Premium conseillé** : " + " - ".join(tk["quarte_premium"])
        return "Aucun Quarté disponible pour le moment."

    # --- Trio ---
    if "trio" in q:
        if tk["trio_premium"]:
            return "🎯 **Trio Premium conseillé** : " + " - ".join(tk["trio_premium"])
        return "Aucun Trio disponible pour le moment."

    # --- Champ réduit ---
    if "champ réduit" in q or "champ reduit" in q:
        champ = tk["champ_reduit"]
        if champ.get("disponible") and champ.get("format"):
            return f"🔒 **Champ réduit Premium** : {champ['format']}"
        return "Le champ réduit n'est pas disponible pour cette course (trop peu de partants analysés)."

    # --- Dernière minute / joker ---
    if any(k in q for k in ["dernière minute", "derniere minute", "joker"]):
        derniere = tk["derniere_minute"]
        if derniere.get("selection"):
            texte = "⚡ **Ticket Dernière Minute** : " + " - ".join(derniere["selection"])
            if derniere.get("joker"):
                texte += f" (Joker : N°{derniere['joker']})"
            return texte
        return "Aucun ticket Dernière Minute disponible pour le moment."

    # --- Avis général sur la course ---
    if any(k in q for k in ["comment tu trouve", "comment tu vois", "avis sur cette course", "ton avis", "que penses-tu", "analyse de la course", "analyse moi", "analyse cette course"]):
        if not classement:
            return "Aucune analyse de course n'est disponible pour le moment."
        nb = len(classement)
        return (
            f"📊 Sur les {nb} partants : {_analyser_favori(classement)}\n\n"
            f"{_analyser_vulnerables(classement)}"
        )

    if any(k in q for k in ["favori", "coup sur", "meilleur", "gagnant", "top"]):
        return _analyser_favori(classement)

    if any(k in q for k in ["quinté", "quinte", "ticket", "combinaison"]):
        if any(k in q for k in ["demain", "hier"]):
            return ("Le choix du Quinté d'un autre jour (hier/demain) n'est pas "
                    "encore disponible — cette fonctionnalité dépend d'une donnée "
                    "supplémentaire non encore branchée. Je peux en revanche vous "
                    "donner le Quinté du jour en cours.")
        if "premium" in q and tk["quinte_premium"]:
            return "💎 **Quinté Premium conseillé** : " + " - ".join(tk["quinte_premium"])
        if tk["quinte_gratuit"]:
            return "💡 **Ticket Quinté Conseillé** : " + " - ".join(tk["quinte_gratuit"])
        return "Aucune combinaison Quinté disponible pour le moment."

    if any(k in q for k in ["outsider", "tocard", "surprise", "pépite", "pepite"]):
        outsiders = [c for c in classement if float(c.get("cote", 0) or 0) >= 10.0]
        if outsiders:
            c = outsiders[0]
            return f"🔥 **Outsider à surveiller** : N°{c.get('numero')} **{c.get('nom')}** (Cote : {c.get('cote')})."
        return "Aucun outsider n'a été repéré avec un niveau de confiance suffisant."

    if "badge" in q or "signification" in q:
        return ("🏷️ **Guide des Badges** :\n- **D4** : Déferré des 4 pieds.\n"
                "- **Duo Chaud 🔥** : Jockey & entraîneur en réussite.\n"
                "- **Spécialiste 🎯** : aptitude détectée.\n"
                "- **Rachat ⚡** : profil à reconsidérer.")

    return ("Je n'ai pas identifié votre demande. Je peux : donner le favori, "
            "repérer les favoris vulnérables, comparer deux chevaux "
            "(ex. \"compare le 3 et le 7\"), proposer des scénarios, "
            "expliquer un cheval précis (fiche complète, jockey, musique, "
            "forme, corde...), donner le meilleur duo, le Quinté, Quarté, "
            "Trio, le champ réduit, le ticket Dernière Minute, les "
            "outsiders ou les badges AZ Turf Pro.")


# =====================================
# V18 — COUCHE CONVERSATIONNELLE ROBUSTE
# =====================================

_ETAT_DIALOGUE = {"etat":"ACCUEIL","dernier_intent":None,"derniers_numeros":[],"dernier_cheval":None,"derniere_question":"","dernier_resultat":None}

_VARIANTES_ACCUEIL = [
    "👋 Bonjour ! Heureux de vous retrouver. Comment allez-vous aujourd'hui ? Sur quoi souhaitez-vous qu'on travaille ?",
    "👋 Bonjour ! AZ Turf Pro est prêt. Comment allez-vous ? On peut regarder la course du jour, un cheval ou préparer un ticket.",
    "Bonjour ! 🏇 Ravi de vous retrouver. Dites-moi ce que vous souhaitez étudier aujourd'hui et nous allons avancer ensemble.",
]
_VARIANTES_BONSOIR = [
    "🌙 Bonsoir ! Comment allez-vous ? Je suis prêt à travailler avec vous sur les courses.",
    "Bonsoir ! 🏇 Tout est prêt. Sur quoi souhaitez-vous qu'on travaille ce soir ?",
]

def _normaliser_conversation(texte: str) -> str:
    import unicodedata
    s=str(texte or '').strip().lower().replace('’', "'").replace('`', "'")
    s=unicodedata.normalize('NFD',s)
    s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    s=re.sub(r"[^a-z0-9\s'#-]",' ',s)
    return re.sub(r'\s+',' ',s).strip()

def _detecter_intention_robuste(question: str) -> str:
    q=_normaliser_conversation(question)
    familles=[
      ('salutation',["bonjour","bjr","salut","coucou","hello","bonsoir","bonne soiree"]),
      ('bien_etre',["ca va","comment vas tu","comment allez vous","tu vas bien","vous allez bien","comment te portes tu"]),
      ('merci',["merci","merci beaucoup","je te remercie"]),
      ('aide',["aide moi","que peux tu faire","tu peux faire quoi","quelles sont tes capacites","comment peux tu m aider"]),
      ('au_revoir',["au revoir","a bientot","bonne nuit","a plus","a demain","je te laisse"]),
      ('comparaison',["compare","comparons","face au","versus","contre","lequel est meilleur","lequel prefere"]),
      ('favori',["favori","base","plus sur","plus fiable","coup sur"]),
      ('ticket',["ticket","quinte","quarte","trio","couple","champ reduit","derniere minute","combinaison"]),
      ('cotes',["cote","cotes","smart money","evolution","baisse de cote","hausse de cote"]),
      ('outsider',["outsider","grosse cote","surprise","toque"]),
      ('presse',["presse","journalistes","pronostics presse","presse hippique"]),
      ('historique',["historique","archives","course precedente","course passee","souviens toi","rappelle"]),
      ('meteo',["meteo","terrain","piste","pluie","lourd","souple","bon terrain"]),
      ('analyse_course',["analyse la course","analyser la course","analyse du quinte","regardons le quinte","fais la selection","donne moi la selection","tes cinq","chevaux a retenir"]),
    ]
    for intent,mots in familles:
        if any(m in q for m in mots): return intent
    if re.search(r"\b(?:numero|n|cheval)\s*#?\s*\d{1,2}\b",q): return 'cheval'
    return 'general'

def _extraire_numeros_robuste(question: str) -> list:
    nums=[int(x) for x in re.findall(r"\b(\d{1,2})\b",_normaliser_conversation(question))]
    return list(dict.fromkeys(nums))[:10]

def _mettre_a_jour_memoire_dialogue(question: str,intent: str,resultats=None):
    global _ETAT_DIALOGUE
    nums=_extraire_numeros_robuste(question)
    if nums:
        _ETAT_DIALOGUE['derniers_numeros']=nums
        _ETAT_DIALOGUE['dernier_cheval']=nums[-1]
    _ETAT_DIALOGUE.update({'dernier_intent':intent,'derniere_question':str(question or ''),'dernier_resultat':resultats})
    transitions={'salutation':'ACCUEIL','bien_etre':'ACCUEIL','aide':'EXPLORATION','analyse_course':'ANALYSE','cheval':'ANALYSE','comparaison':'COMPARAISON','favori':'ANALYSE','cotes':'ANALYSE','outsider':'ANALYSE','presse':'ANALYSE','meteo':'ANALYSE','ticket':'DECISION','historique':'SUIVI','au_revoir':'ACCUEIL'}
    _ETAT_DIALOGUE['etat']=transitions.get(intent,_ETAT_DIALOGUE.get('etat','EXPLORATION'))

def _resoudre_references(question: str) -> str:
    q=_normaliser_conversation(question); p=_ETAT_DIALOGUE.get('derniers_numeros',[]) or []
    if not p: return question
    if any(x in q for x in ('eux','les deux','ces deux','entre eux')) and len(p)>=2: return f"{question} [référence: chevaux {p[-2]} et {p[-1]}]"
    if any(x in q for x in ('ce cheval','celui ci','celui-ci')): return f"{question} [référence: cheval {_ETAT_DIALOGUE.get('dernier_cheval')}]"
    if 'le premier' in q and p: return f"{question} [référence: cheval {p[0]}]"
    if any(x in q for x in ('le suivant','le deuxieme','deuxieme')) and len(p)>=2: return f"{question} [référence: cheval {p[1]}]"
    return question

def _reponse_conversation_naturelle(question: str,intent: str):
    import random
    q=_normaliser_conversation(question)
    if intent=='salutation': return random.choice(_VARIANTES_BONSOIR if ('bonsoir' in q or 'bonne soiree' in q) else _VARIANTES_ACCUEIL)
    if intent=='bien_etre': return "Merci de demander 😊 Je vais bien et je suis prêt à travailler avec vous. On peut regarder la course du jour, étudier un cheval, comparer deux profils ou préparer un ticket. Sur quoi voulez-vous commencer ?"
    if intent=='merci': return random.choice(["Avec plaisir ! 👍 On continue quand vous voulez.","Avec plaisir. 🏇 Je suis prêt pour la suite.","Je vous en prie ! Dites-moi simplement ce qu'on examine ensuite."])
    if intent=='aide': return "Je peux vous accompagner sur l'analyse disponible dans AZ Turf Pro : course, chevaux, favori, outsiders, cotes, presse, terrain, comparaison, scénarios et tickets. Vous pouvez me parler naturellement, par exemple : « analyse le 5 », « compare le 5 et le 7 » ou « donne-moi ton Quinté »."
    if intent=='au_revoir': return random.choice(["À bientôt 👋 ! Nous reprendrons l'analyse quand vous le souhaitez.","À bientôt ! 🏇 Bonne continuation et bonne chance pour vos analyses.","Très bien, à bientôt. Je serai prêt pour la prochaine course !"])
    if intent=='general' and len(q.split())<12: return "Bien sûr. Je vous écoute. Si vous souhaitez travailler sur la course, donnez-moi simplement votre demande, même avec vos propres mots."
    return None

def _evaluer_confiance_reponse(contexte: dict,intent: str) -> str:
    classement=((contexte or {}).get('moteur') or {}).get('classement') or []
    if intent in {'salutation','bien_etre','merci','aide','au_revoir'}: return 'élevée'
    return 'élevée' if classement else 'limitée'

def _construire_reponse_robuste(question: str,contexte: dict,historique=None):
    intent=_detecter_intention_robuste(question)
    question_resolue=_resoudre_references(question)
    _mettre_a_jour_memoire_dialogue(question_resolue,intent)
    naturelle=_reponse_conversation_naturelle(question_resolue,intent)
    if naturelle is not None:
        return {'status':'success','question':question,'reponse':naturelle,'source':'conversation_locale','intent':intent,'etat_dialogue':_ETAT_DIALOGUE['etat'],'confiance':_evaluer_confiance_reponse(contexte,intent)}
    return None

# =====================================
# POINT D'ENTRÉE
# =====================================

# ============================================================
# INTÉGRATION ROBUSTE V16 — PIPELINE AUTONOME RÉEL
# ============================================================
# Cette section est le point d'entrée effectif. Elle conserve le moteur
# historique ci-dessus et orchestre les modules locaux sans dépendance à
# Claude/OpenAI. Les appels externes restent disponibles dans le code
# historique, mais ne sont jamais nécessaires au pronostic autonome.

_V16_SESSIONS = {}


def _v16_safe(fn, default, *args, **kwargs):
    try:
        value = fn(*args, **kwargs)
        return default if value is None else value
    except Exception:
        return default


def _v16_enrichir(contexte, historique=None):
    ctx = dict(contexte or {})
    moteur = dict(ctx.get("moteur") or {})
    chevaux = [c for c in (moteur.get("classement") or moteur.get("chevaux") or []) if isinstance(c, dict)]
    course = dict(ctx.get("course") or {})

    # Cotes : données réelles déjà présentes dans les partants.
    try:
        from .cotes_history import analyser_tendances_cotes
        ctx["tendances_cotes"] = analyser_tendances_cotes({"chevaux": chevaux})
    except Exception:
        ctx["tendances_cotes"] = {"status": "indisponible", "resultats": []}

    # Presse : ne fabrique aucun consensus. Elle ne travaille que sur les
    # pronostics effectivement fournis par la source d'appel.
    try:
        from .pronos_presse import analyser_consensus_presse
        ctx["consensus_presse"] = analyser_consensus_presse({
            "info_course": course,
            "chevaux": chevaux,
            "pronostics": course.get("pronostics_presse") or course.get("presse") or []
        })
    except Exception:
        ctx["consensus_presse"] = {"status": "indisponible", "consensus": []}

    # Météo/piste : même principe, données seulement si réellement présentes.
    try:
        from .meteo_piste import analyser_impact_terrain
        ctx["impact_meteo"] = analyser_impact_terrain({
            "info_course": course,
            "meteo": course.get("meteo"),
            "terrain": course.get("terrain") or course.get("etat_piste")
        })
    except Exception:
        ctx["impact_meteo"] = {"status": "indisponible", "impact": "INCONNU"}

    # Source France Galop pour le galop, best-effort et non bloquante.
    try:
        if "GALOP" in str(course.get("discipline", "")).upper():
            from france_galop_source import obtenir_complement_france_galop
            ctx["complement_france_galop"] = obtenir_complement_france_galop(
                course.get("hippodrome", ""), course.get("discipline", "")
            )
    except Exception:
        ctx["complement_france_galop"] = None

    # Historique : deux modules complémentaires peuvent travailler sur le
    # même historique sans modifier la prédiction courante.
    if isinstance(historique, list) and historique:
        try:
            from .stats_backtest import calculer_stats_performance
            ctx["performance_historique"] = calculer_stats_performance(historique)
        except Exception:
            ctx["performance_historique"] = {"status": "indisponible"}
        try:
            from .performance_expert import statistiques_expert
            ctx["performance_expert"] = statistiques_expert(historique)
        except Exception:
            ctx["performance_expert"] = {"courses": 0, "indice_confiance": 0}

    # Moteur expert indépendant : il reçoit le score indépendant du chatbot,
    # jamais l'indice AZ/Premium comme entrée de son calcul.
    try:
        from .pronostiqueur_engine import analyser_profils_chevaux, generer_synthese
        profils_input = []
        for c in chevaux:
            cc = dict(c)
            cc["score_expert"] = round(_score_expert_independant(c) * 10.0, 2)
            profils_input.append(cc)
        profils = analyser_profils_chevaux(profils_input)
        # Restaurer le score dans les profils pour les modules suivants.
        score_map = {str(c.get("numero")): c.get("score_expert", 0) for c in profils_input}
        for profil in profils:
            profil["score_expert"] = score_map.get(str(profil.get("numero")), 0)
        ctx["expert_profils"] = profils
        ctx["expert_synthese"] = generer_synthese(profils)

        from .decision_engine import analyser_chevaux, generer_ticket
        decision = analyser_chevaux(profils)
        ctx["expert_decision"] = decision
        ctx["expert_ticket"] = generer_ticket(decision, "quinte")

        from .analyse_cheval_engine import comparer_chevaux
        ctx["fiches_expertes"] = comparer_chevaux(profils)
    except Exception:
        ctx["expert_profils"] = []
        ctx["expert_synthese"] = {}
        ctx["expert_decision"] = {}
        ctx["expert_ticket"] = {}
        ctx["fiches_expertes"] = []

    # Tactique + stratégie + simulation : chaque couche est isolée.
    selection = [p.get("numero") for p in ctx.get("expert_profils", []) if p.get("numero") is not None]
    try:
        from .tactique_course_engine import analyser_scenario_course, construire_strategie_quinte
        ctx["tactique"] = analyser_scenario_course(chevaux)
        ctx["strategie_quinte"] = construire_strategie_quinte(selection)
    except Exception:
        ctx["tactique"] = {}
        ctx["strategie_quinte"] = {}
    try:
        from .strategie_pari_engine import construire_ticket_strategique, evaluer_risque_ticket
        ctx["strategies"] = {}
        for mode in ("prudent", "equilibre", "offensif"):
            ticket = construire_ticket_strategique(selection, mode)
            ctx["strategies"][mode] = {**ticket, "risque": evaluer_risque_ticket(ticket)}
    except Exception:
        ctx["strategies"] = {}
    try:
        from .simulation_course_engine import simuler_scenario, evaluer_robustesse_ticket
        favori = chevaux[0] if chevaux else {}
        outsiders = [c.get("numero") for c in chevaux if _cote(c) >= 10][:3]
        simulation = simuler_scenario(favori.get("numero"), outsiders) if favori else {"scenarios": []}
        ctx["simulation"] = simulation
        ctx["robustesse"] = evaluer_robustesse_ticket(ctx.get("expert_ticket") or {}, simulation.get("scenarios", []))
    except Exception:
        ctx["simulation"] = {}
        ctx["robustesse"] = {}

    moteur["accompagnement"] = {
        "cotes": ctx.get("tendances_cotes"),
        "presse": ctx.get("consensus_presse"),
        "meteo": ctx.get("impact_meteo"),
        "expert": ctx.get("expert_synthese"),
        "decision": ctx.get("expert_decision"),
        "ticket_expert": ctx.get("expert_ticket"),
        "fiches_expertes": ctx.get("fiches_expertes"),
        "tactique": ctx.get("tactique"),
        "strategie_quinte": ctx.get("strategie_quinte"),
        "strategies": ctx.get("strategies"),
        "simulation": ctx.get("simulation"),
        "robustesse": ctx.get("robustesse"),
        "performance": ctx.get("performance_historique"),
    }
    ctx["moteur"] = moteur
    return ctx


def _v16_special(question, contexte, historique):
    q = (question or "").lower().strip()
    moteur = contexte.get("moteur") or {}
    classement = moteur.get("classement") or []
    tickets = moteur.get("tickets") or {}

    # Demandes spécialisées : elles utilisent les données réellement branchées.
    if any(k in q for k in ("cote", "côte", "smart money", "argent qui rentre", "délaissé", "tendance")):
        r = contexte.get("tendances_cotes") or {}
        lignes = []
        for x in r.get("resultats", []) or []:
            if isinstance(x, dict):
                lignes.append(f"N°{x.get('numero')} {x.get('nom')}: {x.get('cote_matin')} → {x.get('cote_direct')} ({x.get('variation_pct',0):+.2f}%) — {x.get('signal','NEUTRE')}")
        if lignes:
            return "📈 **Tendances de cotes**\n" + "\n".join(lignes[:12])
        return "📈 Les données de cote sont bien branchées, mais aucune variation exploitable n'est disponible actuellement."

    if any(k in q for k in ("météo", "meteo", "terrain", "piste", "sol")):
        r = contexte.get("impact_meteo") or {}
        return f"🌦️ **Conditions piste : {r.get('impact', 'INCONNU')}**"

    if any(k in q for k in ("presse", "consensus")):
        r = contexte.get("consensus_presse") or {}
        if r.get("consensus"):
            return "📰 **Consensus presse**\n" + str(r["consensus"])
        return "📰 Aucune sélection presse réelle n'est disponible dans les données de cette course."

    if any(k in q for k in ("backtest", "performance", "rentabilité", "rentabilite")):
        return "📊 **Performance**\n" + str(contexte.get("performance_historique") or contexte.get("performance_expert") or {"status":"aucun historique fourni"})

    # Pronostic indépendant explicite : score propre + décision propre.
    if any(k in q for k in ("pronostic indépendant", "pronostic independant", "ton pronostic", "ta sélection", "ta selection", "ticket autonome", "ticket indépendant", "ticket independant")):
        dec = contexte.get("expert_decision") or {}
        classement_expert = dec.get("classement") or contexte.get("expert_profils") or []
        nums = [str(c.get("numero")) for c in classement_expert if c.get("numero") is not None][:5]
        bases = [str(c.get("numero")) for c in dec.get("bases", []) if c.get("numero") is not None]
        outsiders = [str(c.get("numero")) for c in dec.get("outsiders", []) if c.get("numero") is not None]
        if nums:
            return ("🤖 **Pronostic expert autonome du chatbot**\n"
                    f"Sélection : **{' - '.join(nums)}**\n"
                    f"Bases : **{' - '.join(bases) if bases else 'aucune base forte'}**\n"
                    f"Outsiders : **{' - '.join(outsiders) if outsiders else 'aucun outsider détecté'}**\n"
                    f"Confiance du moteur : **{dec.get('confiance', 0)}%**\n"
                    "Calcul séparé de l'indice AZ : ce classement expert est construit à partir des statistiques brutes disponibles.")

    # Profils stratégiques déjà calculés par les modules.
    if "prudent" in q and contexte.get("strategies", {}).get("prudent"):
        return "🛡️ **Ticket prudent**\n" + str(contexte["strategies"]["prudent"])
    if any(k in q for k in ("spéculatif", "speculatif", "gros rapport")) and contexte.get("strategies", {}).get("offensif"):
        return "🔥 **Ticket offensif**\n" + str(contexte["strategies"]["offensif"])
    if any(k in q for k in ("équilibré", "equilibre")) and contexte.get("strategies", {}).get("equilibre"):
        return "⚖️ **Ticket équilibré**\n" + str(contexte["strategies"]["equilibre"])

    return None


def _repondre_assistant_turf_v17(question: str, contexte_analyse: dict = None, historique: list = None) -> dict:
    """Point d'entrée définitif : moteur local + modules réellement branchés.

    Claude/OpenAI ne sont pas nécessaires et ne sont pas appelés ici.
    """
    contexte = _v16_enrichir(contexte_analyse or {}, historique)
    course = contexte.get("course") or {}
    session_key = f"{course.get('date','')}-{course.get('reunion','')}-{course.get('course_numero','')}"
    _V16_SESSIONS[session_key] = {"contexte": contexte, "historique": list(historique or [])[-20:]}

    try:
        conversation = _reponse_conversation_naturelle(question, contexte, historique)
        if conversation:
            return {"status":"success", "question":question, "reponse":conversation, "source":"conversation_locale"}
        special = _v16_special(question, contexte, historique)
        if special:
            return {"status":"success", "question":question, "reponse":special, "source":"moteur_local_modules"}
        texte = _reponse_secours(question, contexte)
    except Exception:
        texte = "Les données sont disponibles, mais je n'ai pas pu finaliser cette réponse locale."
    return {"status":"success", "question":question, "reponse":texte, "source":"moteur_local_autonome"}


# =====================================
# V18 — POINT D'ENTRÉE FINAL ROBUSTE
# =====================================

def repondre_assistant_turf(question: str, contexte_analyse: dict = None, historique: list = None) -> dict:
    """Entrée publique locale : conversation d'abord, moteur turf ensuite."""
    question=str(question or '').strip(); contexte=contexte_analyse or {}
    if not question:
        return {'status':'success','question':'','reponse':'Je suis prêt. 🏇 Dites-moi ce que vous souhaitez analyser et nous allons commencer.','source':'conversation_locale','intent':'general','etat_dialogue':_ETAT_DIALOGUE.get('etat','ACCUEIL'),'confiance':'élevée'}
    try:
        r=_construire_reponse_robuste(question,contexte,historique)
        if r is not None: return r
    except Exception as exc:
        print(f'[CHATBOT V18] couche conversationnelle: {type(exc).__name__}: {exc}')
    resultat=_repondre_assistant_turf_v17(question,contexte_analyse=contexte_analyse,historique=historique)
    if not isinstance(resultat,dict): resultat={'status':'success','question':question,'reponse':str(resultat),'source':'moteur_az_autonome'}
    resultat.setdefault('intent',_ETAT_DIALOGUE.get('dernier_intent'))
    resultat.setdefault('etat_dialogue',_ETAT_DIALOGUE.get('etat','EXPLORATION'))
    resultat.setdefault('confiance',_evaluer_confiance_reponse(contexte,_ETAT_DIALOGUE.get('dernier_intent') or 'general'))
    resultat.setdefault('source','moteur_az_autonome')
    return resultat

def diagnostic_conversation_v18() -> dict:
    return {'version':'V18','mode':'autonome','claude':False,'openai':False,'etat':dict(_ETAT_DIALOGUE)}

# ============================================================
# ORCHESTRATEUR LARGE V19
# ============================================================
# Couche additive : compréhension par familles sémantiques, résolution du
# contexte et réponses spécialisées. Elle est placée devant les anciens
# replis afin de conserver la compatibilité sans dépendre de mots-clés exacts.
try:
    from .orchestrateur_turf import repondre as _orchestrateur_large_repondre
except Exception:
    _orchestrateur_large_repondre = None

_ancienne_repondre_assistant_turf = repondre_assistant_turf


def _v19_enrichir(contexte, question, historique):
    base = _v16_enrichir(contexte, historique)
    try:
        from .orchestrateur_turf import enrichir_modules_accompagnement
        return enrichir_modules_accompagnement(base, question, historique)
    except Exception as exc:
        print(f"[CHATBOT V19] enrichissement accompagnement: {type(exc).__name__}: {exc}")
        return base


def repondre_assistant_turf(question: str, contexte_analyse: dict = None, historique: list = None) -> dict:
    question = str(question or '').strip()
    contexte = contexte_analyse or {}
    historique = historique or []
    if not question:
        return {'status':'success','question':'','reponse':'Je suis prêt. 🏇 Dites-moi ce que vous souhaitez examiner.','source':'conversation_locale','intent':'general','etat_dialogue':_ETAT_DIALOGUE.get('etat','ACCUEIL'),'confiance':'élevée'}

    try:
        # Enrichissement unique avant orchestration : les modules locaux restent
        # la source des données et l'analyse autonome reste indépendante d'AZ.
        contexte_enrichi = _v19_enrichir(contexte, question, historique)
        if _orchestrateur_large_repondre:
            resultat = _orchestrateur_large_repondre(question, contexte_enrichi, historique)
            if resultat:
                resultat.setdefault('question', question)
                resultat.setdefault('confiance', _evaluer_confiance_reponse(contexte_enrichi, resultat.get('intent','general')))
                return resultat
        # Compatibilité : ancien moteur si l'orchestrateur ne couvre pas la demande.
        resultat = _ancienne_repondre_assistant_turf(question, contexte_analyse=contexte_enrichi, historique=historique)
        if isinstance(resultat, dict):
            return resultat
        return {'status':'success','question':question,'reponse':str(resultat),'source':'moteur_az_autonome'}
    except Exception as exc:
        # Ne jamais exposer une exception brute à l'utilisateur. Le moteur
        # historique reste le dernier filet de sécurité.
        print(f'[CHATBOT V19] orchestration: {type(exc).__name__}: {exc}')
        try:
            resultat = _ancienne_repondre_assistant_turf(question, contexte_analyse=contexte, historique=historique)
            if isinstance(resultat, dict):
                return resultat
        except Exception:
            pass
        return {'status':'success','question':question,'reponse':'Je peux traiter cette demande dès que les données de la course nécessaires sont disponibles.','source':'moteur_local','intent':'general','confiance':'limitée'}
