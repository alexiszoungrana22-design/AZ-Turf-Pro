"""AI Race Analyst - analyse hippique indépendante du moteur AZ Turf Pro.

Le modèle reçoit les données PMU normalisées de la course et construit son propre
raisonnement et ses propres tickets. Le ticket AZ n'est injecté que si l'utilisateur
demande explicitement une comparaison.
"""
from __future__ import annotations

import json
import os
from typing import Any, AsyncIterator

try:
    from openai import AsyncOpenAI
except ImportError:  # permet au reste du backend de démarrer avant installation
    AsyncOpenAI = None

MODEL = os.getenv("OPENAI_RACE_MODEL", "gpt-5.6-terra").strip() or "gpt-5.6-terra"
MAX_HISTORY = 12

SYSTEM_PROMPT = """
Tu es AZ Turf Pro AI Race Analyst, un analyste hippique professionnel indépendant.
Ta mission est de lire LA COURSE avant de lire les chevaux. Tu dois raisonner sur les
conditions réelles fournies par PMU et produire, lorsque demandé, des tickets qui ne
sont PAS des copies du moteur AZ Turf Pro.

REGLES ABSOLUES
1. Les faits doivent venir du dossier PMU fourni. N'invente jamais une statistique,
   une cote, une performance, un engagement, une météo ou une information d'entourage.
2. Si une information manque, dis "non documenté" et réduis ta confiance.
3. Ne transforme jamais la musique seule en prédiction. Cherche les interactions entre
   parcours, distance, départ, position, aptitude, rythme, engagement, forme, entourage,
   ferrure, marché et scénario.
4. Le marché est un signal, pas une vérité : distingue probabilité et valeur.
5. Le ticket IA doit être construit indépendamment du ticket AZ Turf Pro. Ne consulte
   aucune donnée AZ sauf si le dossier contient explicitement une section de comparaison
   demandée par l'utilisateur.
6. Ne promets jamais un gain certain. Donne une confiance qualitative (faible/moyenne/
   forte) liée à la qualité des données et au scénario, pas une garantie de résultat.
7. Pour un Quinté, donne une sélection ordonnée, puis explique la construction : base(s),
   chevaux de complément, profils de couverture, outsider(s), cheval à écarter et ticket.
8. Si le départ est autostart, analyse les numéros et la position. Si c'est un départ
   volté, analyse le comportement au départ et les risques de faute si les données le
   permettent. En obstacle, distingue haies/steeple et intègre distance, poids, terrain,
   saut et expérience lorsqu'ils sont documentés. En plat, intègre corde, poids, terrain,
   distance, rythme et aptitude lorsqu'ils sont documentés. En trot, distingue attelé/monté,
   départ, ferrure, gains, vitesse et risques de faute lorsqu'ils sont documentés.
9. Ne considère jamais un déferrage comme une preuve d'objectif : c'est un signal parmi
   d'autres.
10. Un outsider doit être réellement défendable par le dossier, pas seulement avoir une
    grosse cote.

METHODE DE LECTURE
A. Identifie discipline, hippodrome, distance, type de départ, nombre de partants,
   conditions, allocation, heure et toute contrainte de course disponible.
B. Décris le profil du parcours et les avantages/inconvénients structurels connus.
C. Évalue le rythme/scénario : chevaux susceptibles d'animer, chevaux dépendants du
   parcours, profils de finisseurs, risques de trafic/placement lorsque documentés.
D. Pour chaque candidat important, croise au minimum : musique/performance, régularité,
   distance, terrain, départ/numéro/corde, ferrure, jockey/driver, entraîneur, expérience,
   gains/conditions, cote actuelle et évolution de cote si disponible.
E. Cherche les contradictions : favori fragile, cheval mal coté, cheval régulier mais
   dépendant du scénario, outsider possédant plusieurs leviers favorables.
F. Construis au moins deux scénarios lorsque la course est suffisamment documentée.
G. Produis le ticket demandé sans copier AZ.

FORMAT CONSEILLE
## Lecture de course
## Scénario principal
## Scénario alternatif
## Chevaux clés
## Favori : solide ou vulnérable ?
## Outsiders / value
## Ticket IA indépendant
## Risques et niveau de confiance
""".strip()


def _clean(value: Any, depth: int = 0) -> Any:
    if depth > 3:
        return str(value)[:500]
    if isinstance(value, dict):
        return {str(k): _clean(v, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(v, depth + 1) for v in value[:80]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def build_pmu_dossier(course: dict) -> dict:
    """Dossier compact mais riche, construit uniquement à partir de la course PMU."""
    course = course if isinstance(course, dict) else {}
    horses = course.get("chevaux") if isinstance(course.get("chevaux"), list) else []
    fields_course = {
        k: course.get(k) for k in (
            "course", "date", "reunion", "course_numero", "heure_depart", "horaires",
            "hippodrome", "discipline", "distance_course", "allocation", "type_depart",
            "conditions", "non_partants", "source"
        ) if course.get(k) not in (None, "", [])
    }
    normalized = []
    for h in horses:
        if not isinstance(h, dict):
            continue
        # Tous les champs utiles de la transformation PMU sont conservés.
        normalized.append(_clean(h))
    return {"course": fields_course, "partants": normalized}


def wants_az_comparison(question: str) -> bool:
    q = (question or "").lower()
    return any(x in q for x in ("az turf", "ticket az", "compare az", "vs az", "versus az", "comparaison az"))


def build_input(question: str, dossier_pmu: dict, history: list[dict] | None = None, az_context: dict | None = None) -> str:
    history = history if isinstance(history, list) else []
    payload = {
        "question": question,
        "historique_recent": history[-MAX_HISTORY:],
        "dossier_pmu_reel": dossier_pmu,
    }
    if az_context is not None:
        payload["comparaison_az_explicitement_demandee"] = _clean(az_context)
    else:
        payload["consigne_independance"] = "Ne pas utiliser ni reproduire le ticket AZ Turf Pro."
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


async def stream_ai_answer(question: str, dossier_pmu: dict, history: list[dict] | None = None, az_context: dict | None = None) -> AsyncIterator[str]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or AsyncOpenAI is None:
        raise RuntimeError("IA générative non configurée : OPENAI_API_KEY est absente du serveur.")

    client = AsyncOpenAI(api_key=api_key)
    prompt = build_input(question, dossier_pmu, history, az_context)
    try:
        stream = await client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=prompt,
            stream=True,
        )
        async for event in stream:
            if getattr(event, "type", "") == "response.output_text.delta":
                delta = getattr(event, "delta", "")
                if delta:
                    yield delta
    finally:
        await client.close()
