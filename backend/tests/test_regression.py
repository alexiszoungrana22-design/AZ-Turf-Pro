import unittest
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import lancer_analyse
from modules.chatbot_turf import repondre_assistant_turf


def load_demo():
    return json.loads((ROOT / "data" / "courses.json").read_text(encoding="utf-8"))


class TestAZTurfPro(unittest.TestCase):
    def test_engine_and_ticket_contract(self):
        data = load_demo()
        result = lancer_analyse(data["chevaux"], data)
        assert len(result["classement"]) == 8
        tickets = result["tickets"]
        assert len(tickets["gratuit"]["quinte"]) == 7
        assert len(tickets["premium"]["quinte"]) == 6
        assert len(tickets["premium"]["quarte"]) == 5
        assert len(tickets["premium"]["trio"]) == 3
        assert tickets["premium"]["champ_reduit"]["disponible"] is True


    def test_non_partant_is_excluded(self):
        data = load_demo()
        chevaux = [dict(c) for c in data["chevaux"]]
        chevaux[-1]["statut"] = "NP"
        result = lancer_analyse(chevaux, {**data, "non_partants": [chevaux[-1]["numero"]]})
        assert all(str(c["numero"]) != str(chevaux[-1]["numero"]) for c in result["classement"])
        assert str(chevaux[-1]["numero"]) in [str(x) for x in result["non_partants"]]


    def test_chatbot_priority_routing(self):
        data = load_demo()
        result = lancer_analyse(data["chevaux"], data)
        ctx = {"moteur": result, "course": data}
        assert "Bonjour" in repondre_assistant_turf("bonjour", ctx, [])["reponse"]
        assert "Quinté Premium" in repondre_assistant_turf("donne le quinté premium", ctx, [])["reponse"]
        assert "Meilleur duo" in repondre_assistant_turf("quel est le meilleur duo", ctx, [])["reponse"]
        assert "N°3" in repondre_assistant_turf("explique le cheval 3", ctx, [])["reponse"]


    def test_raw_odds_are_not_confused_with_normalized_score(self):
        from pmu_source import transformer_participant
        p = {
            "numPmu": 1, "nom": "Test", "musique": "2p3p1p",
            "dernierRapportDirect": 15.0,
            "gainsParticipant": {"gainsCarriere": 100000},
            "nombreCourses": 50,
        }
        c = transformer_participant(p, {}, {1: {"score": 1.0, "cote": 15.0}}, {1: 7.0})
        assert c["cote"] == 1.0
        assert c["cote_brute"] == 15.0


    def test_premium_uses_raw_odds_for_outsider_detection(self):
        from engine import calculer_indice_premium
        h = {"indice_az": 100, "forme": 8, "regularite": 8, "cote": 1.0, "cote_brute": 15.0, "experience": 5, "performances": [2,3]}
        score = calculer_indice_premium(h, {"distance": 2000})
        assert score > 100


    def test_discipline_classification(self):
        from scoring import classifier_discipline
        assert classifier_discipline("PLAT") == "PLAT"
        assert classifier_discipline("TROT_ATTELE") == "ATTELE"
        assert classifier_discipline("TROT_MONTE") == "MONTE"
        assert classifier_discipline("HAIES") == "OBSTACLE"
        assert classifier_discipline("STEEPLE-CHASE") == "OBSTACLE"
        # Discipline inconnue/absente : repli neutre, jamais une erreur.
        assert classifier_discipline("") == "ATTELE"


    def test_attele_and_monte_score_differently(self):
        # Attelé et Monté étaient auparavant confondus sous un seul bucket
        # "TROT" : un même cheval doit désormais être noté différemment,
        # le jockey pesant davantage en Monté qu'à l'Attelé (driver).
        from scoring import calculer_score_az
        cheval = {"forme": 7, "regularite": 7, "gains": 6, "jockey_score": 8,
                  "cote": 6, "distance": 5, "terrain": 5, "experience": 5}
        score_attele = calculer_score_az(cheval, "TROT_ATTELE")
        score_monte = calculer_score_az(cheval, "TROT_MONTE")
        assert score_attele != score_monte
        assert score_monte > score_attele


    def test_corde_and_deferrage_bonuses_are_actually_reachable(self):
        # Ces bonus existaient déjà dans le code mais ne recevaient jamais
        # de valeur : pmu_source.py n'extrayait ni "corde" ni "deferre"
        # depuis les données PMU brutes. Vérifie que le circuit complet
        # (extraction -> scoring) fonctionne réellement de bout en bout.
        from pmu_source import transformer_participant, normaliser_deferrage
        from scoring import calculer_score_az

        participant_plat = {
            "numPmu": 1, "nom": "TEST PLAT", "musique": "1p2p3p",
            "placeCorde": 2, "gainsParticipant": {"gainsCarriere": 50000},
            "nombreCourses": 10,
        }
        cheval_plat = transformer_participant(participant_plat, {}, {1: {"score": 5.0, "cote": 10.0}}, {1: 5.0})
        assert cheval_plat["corde"] == 2
        sans_corde = dict(cheval_plat, corde=None)
        assert calculer_score_az(cheval_plat, "PLAT") - calculer_score_az(sans_corde, "PLAT") == 12.0

        participant_trot = {
            "numPmu": 2, "nom": "TEST TROT", "musique": "1p2p3p",
            "deferre": "DEFERRE_ANTERIEURS_POSTERIEURS",
            "gainsParticipant": {"gainsCarriere": 50000}, "nombreCourses": 10,
        }
        cheval_trot = transformer_participant(participant_trot, {}, {2: {"score": 5.0, "cote": 10.0}}, {2: 5.0})
        assert cheval_trot["deferre"] == "D4"
        sans_deferre = dict(cheval_trot, deferre="")
        assert calculer_score_az(cheval_trot, "TROT_ATTELE") - calculer_score_az(sans_deferre, "TROT_ATTELE") == 18.0

        assert normaliser_deferrage(None) == ""
        assert normaliser_deferrage("NON_DEFERRE") == ""
        assert normaliser_deferrage("DEFERRE_ANTERIEURS") == "DA"
        assert normaliser_deferrage("DEFERRE_POSTERIEURS") == "DP"


    def test_scoring_survives_none_values_from_real_pmu_data(self):
        # Bug réel observé en production : certains chevaux PMU ont des
        # champs présents mais explicitement à None (pas absents), ce que
        # dict.get(cle, 0) ne rattrape pas -> "unsupported operand type(s)
        # for *: 'NoneType' and 'float'". Ne doit plus jamais planter.
        from scoring import calculer_score_az
        cheval_incomplet = {
            "forme": None, "regularite": 7, "gains": None, "jockey_score": 8,
            "cote": None, "distance": 5, "terrain": None, "experience": 5,
        }
        for discipline in ("PLAT", "TROT_ATTELE", "TROT_MONTE", "HAIES"):
            score = calculer_score_az(cheval_incomplet, discipline)
            assert isinstance(score, float)


    def test_premium_selection_stays_close_to_az_ranking(self):
        # Bug réel signalé : le Ticket Premium sélectionnait des chevaux
        # loin de l'arrivée alors que la sélection Gratuite (indice AZ pur)
        # restait fiable. Cause : le bonus "outsider chaud" (+15, condition
        # trop large) se déclenchait sur ~40% des partants d'une course
        # type et effaçait des écarts d'Indice AZ légitimes. Vérifie que,
        # sur un jeu de données réaliste, le Top 5 Premium reste
        # majoritairement identique au Top 5 AZ (l'ordre interne peut
        # légèrement varier, mais pas la composition).
        from engine import calculer_indice_premium
        import random
        rng = random.Random(1)
        chevaux = []
        for i in range(1, 13):
            chevaux.append({
                "numero": str(i), "nom": f"C{i}",
                "indice_az": rng.uniform(80, 190),
                "forme": rng.uniform(3, 9), "regularite": rng.uniform(3, 9),
                "cote_brute": rng.uniform(1.5, 40), "cote": rng.uniform(1.5, 40) / 3,
                "experience": 5, "performances": [],
            })
        info_course = {"distance": 2000}
        top5_az = {c["numero"] for c in sorted(chevaux, key=lambda c: c["indice_az"], reverse=True)[:5]}
        top5_premium = {c["numero"] for c in sorted(chevaux, key=lambda c: calculer_indice_premium(c, info_course), reverse=True)[:5]}
        communs = len(top5_az & top5_premium)
        assert communs >= 4, f"Le Ticket Premium diverge trop du classement AZ ({communs}/5 communs)"


    def test_bonus_outsider_chaud_ne_se_declenche_plus_a_la_moindre_occasion(self):
        from engine import calculer_indice_premium
        info_course = {"distance": 2000}
        favori_net = {"numero": "1", "indice_az": 180, "forme": 9, "regularite": 8, "cote": 8, "cote_brute": 2.5, "experience": 6, "performances": [1, 1, 2]}
        outsider_moyen = {"numero": "9", "indice_az": 135, "forme": 7, "regularite": 6, "cote": 4, "cote_brute": 15.0, "experience": 4, "performances": [5, 4, 7]}
        assert calculer_indice_premium(favori_net, info_course) > calculer_indice_premium(outsider_moyen, info_course)


    def test_bonus_distance_predilection_jamais_invente(self):
        from engine import calculer_indice_premium
        info_course = {"distance": 2000}
        sans_donnee = {"numero": "1", "indice_az": 100, "forme": 5, "regularite": 5, "cote": 5, "cote_brute": 5}
        avec_donnee = dict(sans_donnee, distance_predilection=2000)
        assert round(calculer_indice_premium(avec_donnee, info_course) - calculer_indice_premium(sans_donnee, info_course), 2) == 10.0


    def test_calibration_sous_le_seuil_ne_change_rien(self):
        from modules.learning_turf import calculer_calibration
        lignes = [{"chevaux_json": [{"numero": "1", "forme": 8}], "arrivee_json": ["1", "2", "3", "4", "5"]}] * 5
        resultat = calculer_calibration(lignes)
        assert resultat["status"] == "donnees_insuffisantes"
        assert resultat["facteurs"] == {}


    def test_calibration_detecte_un_critere_discriminant_et_ignore_le_bruit(self):
        # Sur un historique simulé où la "forme" détermine clairement qui
        # se place et où la "régularité" est du bruit pur, la calibration
        # doit revaloriser la forme et laisser la régularité quasi neutre —
        # tout en restant dans les bornes de sécurité (±20%).
        from modules.learning_turf import calculer_calibration, SEUIL_MIN_COURSES
        import random
        rng = random.Random(42)
        lignes = []
        for _ in range(SEUIL_MIN_COURSES + 10):
            numeros = list(range(1, 13))
            rng.shuffle(numeros)
            arrivee = [str(n) for n in numeros[:5]]
            chevaux = []
            for n in numeros:
                est_place = str(n) in arrivee
                forme = rng.uniform(7, 10) if est_place else rng.uniform(2, 6)
                chevaux.append({
                    "numero": str(n), "forme": forme, "regularite": rng.uniform(3, 7),
                    "jockey_score": 5.0, "cote": rng.uniform(2, 20), "experience": 5.0,
                })
            lignes.append({"chevaux_json": chevaux, "arrivee_json": arrivee})

        resultat = calculer_calibration(lignes)
        assert resultat["status"] == "success"
        assert resultat["facteurs"]["forme"] > 1.10
        assert 0.95 < resultat["facteurs"]["regularite"] < 1.05
        for valeur in resultat["facteurs"].values():
            assert 0.80 <= valeur <= 1.20


    def test_scoring_retrocompatible_sans_calibration(self):
        # Aucune calibration fournie, ou calibration neutre (tous les
        # facteurs à 1.0) : le score doit être strictement identique à
        # avant l'introduction de ce paramètre.
        from scoring import calculer_score_az
        cheval = {"forme": 7, "regularite": 7, "gains": 6, "jockey_score": 8, "cote": 6, "distance": 5, "terrain": 5, "experience": 5}
        score_sans = calculer_score_az(cheval, "TROT_ATTELE")
        score_none = calculer_score_az(cheval, "TROT_ATTELE", calibration=None)
        score_neutre = calculer_score_az(cheval, "TROT_ATTELE", calibration={"forme": 1.0, "regularite": 1.0})
        assert score_sans == score_none == score_neutre


    def test_engine_charge_et_applique_la_calibration_stockee(self):
        import archive_store
        archive_store.lire_calibration = lambda: {"facteurs": {"forme": 1.15}, "echantillon_courses": 45, "echantillon_chevaux": 520, "calcule_le": "2026-01-01T00:00:00"}
        from engine import lancer_analyse
        chevaux = [{"numero": "3", "nom": "Bella Vista", "forme": 8, "regularite": 7, "cote": 3.2}]
        info_course = {"reunion": "R1", "course_numero": "1", "hippodrome": "Vincennes", "discipline": "TROT_ATTELE"}
        resultat = lancer_analyse(chevaux, info_course)
        assert resultat["calibration_appliquee"] == {"forme": 1.15}
        archive_store.lire_calibration = lambda: None


    def test_normaliser_date_est_idempotente_jours_19_et_20(self):
        # Bug réel constaté en production le 19/09/2026 : trouver_quinte_du_jour()
        # normalise la date, puis recuperer_programme() la re-normalise —
        # un DDMMYYYY dont le jour vaut 19 ou 20 ("1909..." / "2009...")
        # était alors pris à tort pour du YYYYMMDD et corrompu au 2e appel.
        from pmu_source import normaliser_date
        for jour in range(1, 29):  # tous les jours existent en septembre
            ddmmyyyy = f"{jour:02d}092026"
            une_fois = normaliser_date(ddmmyyyy)
            deux_fois = normaliser_date(une_fois)
            assert une_fois == ddmmyyyy, f"jour {jour}: 1er appel a changé la date ({une_fois})"
            assert deux_fois == ddmmyyyy, f"jour {jour}: 2e appel a corrompu la date ({deux_fois})"


    def test_normaliser_date_convertit_toujours_le_vrai_yyyymmdd(self):
        from pmu_source import normaliser_date
        assert normaliser_date("20260920") == "20092026"
        assert normaliser_date("20260119") == "19012026"


    def test_pmu_bascule_automatiquement_de_domaine(self):
        # Le PMU ne documente pas son API et a changé de sous-domaine
        # plusieurs fois par le passé sans préavis. recuperer_programme()
        # doit essayer les domaines candidats dans l'ordre et retenir celui
        # qui répond, plutôt que d'échouer dès que le premier ne répond plus.
        import pmu_source
        appels = []

        class FauxeReponse:
            def raise_for_status(self): pass
            def json(self): return {"programme": {"reunions": []}}

        def faux_get(url, params=None, timeout=None, headers=None):
            appels.append(url)
            if pmu_source.PMU_DOMAINES_CANDIDATS[0] in url:
                raise Exception("Connexion refusée (simulé)")
            return FauxeReponse()

        ancien_get = pmu_source.requests.get
        ancien_domaine_actif = pmu_source._domaine_pmu_actif
        try:
            pmu_source.requests.get = faux_get
            pmu_source._domaine_pmu_actif = None
            resultat = pmu_source.recuperer_programme("15092026")
            assert resultat == {"programme": {"reunions": []}}
            assert len(appels) == 2, "doit avoir essayé le domaine en échec puis le suivant"
            assert pmu_source._domaine_pmu_actif == pmu_source.PMU_DOMAINES_CANDIDATS[1]
        finally:
            pmu_source.requests.get = ancien_get
            pmu_source._domaine_pmu_actif = ancien_domaine_actif


    def test_premium_ne_compte_plus_forme_regularite_trois_fois(self):
        # Bug réel : forme et régularité étaient comptées jusqu'à 3 fois
        # dans le pipeline Premium (indice_az + formule Premium directe +
        # bonus_contexte_course), amplifiant le même signal au lieu
        # d'apporter une vraie analyse supplémentaire. À indice_az et
        # autres critères identiques, deux chevaux avec une forme et une
        # régularité très différentes ne doivent plus avoir d'écart
        # artificiel côté Premium — le signal ne doit venir que
        # d'indice_az, une seule fois.
        from engine import calculer_indice_premium
        info_course = {"distance": 2000}
        bonne_forme = {"numero": "1", "indice_az": 150, "forme": 9, "regularite": 9, "cote": 6, "cote_brute": 8.0, "experience": 5, "performances": []}
        forme_moyenne = {"numero": "2", "indice_az": 150, "forme": 4, "regularite": 4, "cote": 6, "cote_brute": 8.0, "experience": 5, "performances": []}
        ip1 = calculer_indice_premium(bonne_forme, info_course)
        ip2 = calculer_indice_premium(forme_moyenne, info_course)
        assert ip1 == ip2, f"écart artificiel encore présent : {ip1} vs {ip2}"


    def test_premium_ne_compte_plus_cote_experience_deux_fois(self):
        # Même famille de bug que forme/régularité : cote et expérience
        # étaient comptées une 2e fois dans la formule Premium en plus
        # d'indice_az. À indice_az identique, l'écart doit être nul.
        from engine import calculer_indice_premium
        info_course = {"distance": 2000}
        bonne_cote_exp = {"numero": "1", "indice_az": 150, "forme": 5, "regularite": 5, "cote": 9, "cote_brute": 4.0, "experience": 9, "performances": []}
        faible_cote_exp = {"numero": "2", "indice_az": 150, "forme": 5, "regularite": 5, "cote": 2, "cote_brute": 4.0, "experience": 2, "performances": []}
        ip1 = calculer_indice_premium(bonne_cote_exp, info_course)
        ip2 = calculer_indice_premium(faible_cote_exp, info_course)
        assert ip1 == ip2, f"écart artificiel encore présent : {ip1} vs {ip2}"

        # bonus_outsider_chaud (dépend de cote_brute, pas de cote_score)
        # doit rester pleinement fonctionnel malgré cette correction.
        avec_bonus = {"numero": "3", "indice_az": 100, "forme": 8, "regularite": 7, "cote": 3, "cote_brute": 15.0, "experience": 5, "performances": []}
        sans_bonus = dict(avec_bonus, cote_brute=5.0)
        assert calculer_indice_premium(avec_bonus, info_course) > calculer_indice_premium(sans_bonus, info_course)


    def test_deferrage_ne_compte_plus_trois_fois(self):
        # Le déferrage était compté 3 fois : indice_az (scoring.py),
        # bonus_expert (engine.py), bonus_contexte_course (race_analyzer.py).
        # L'écart entre un cheval déferré et non déferré doit être le même
        # au niveau AZ et au niveau Premium (plus d'amplification en plus).
        from engine import calculer_indice_premium
        from scoring import calculer_score_az
        info_course = {"distance": 2000}
        defer = {"numero": "1", "forme": 5, "regularite": 5, "gains": 5, "jockey_score": 5, "cote": 5, "distance": 5, "terrain": 5, "experience": 5, "cote_brute": 6.0, "deferre": "D4", "performances": []}
        sans_defer = dict(defer, deferre="")
        az1 = calculer_score_az(defer, "TROT_ATTELE")
        az2 = calculer_score_az(sans_defer, "TROT_ATTELE")
        assert az1 > az2, "l'indice AZ doit continuer à valoriser le déferrage"
        defer["indice_az"] = az1
        sans_defer["indice_az"] = az2
        ip1 = calculer_indice_premium(defer, info_course)
        ip2 = calculer_indice_premium(sans_defer, info_course)
        assert round(az1 - az2, 2) == round(ip1 - ip2, 2), "le déferrage est encore amplifié en plus d'indice_az"


    def test_bonus_smart_money_se_declenche_avec_une_vraie_variation(self):
        # Le bonus Smart Money existait mais ne recevait jamais de valeur
        # (personne n'enregistrait la cote du matin) ; il doit désormais
        # réagir à une vraie baisse de cote.
        from engine import calculer_indice_premium
        info_course = {"distance": 2000}
        base = {"numero": "1", "indice_az": 100, "forme": 5, "regularite": 5, "cote": 5, "cote_brute": 6.0, "experience": 5, "performances": []}
        smart_money = dict(base, variation_cote_pct=-60.0)
        stable = dict(base, variation_cote_pct=0.0)
        assert calculer_indice_premium(smart_money, info_course) > calculer_indice_premium(stable, info_course)


    def test_cotes_du_matin_restent_stables_entre_deux_analyses(self):
        # La 1re observation d'une cote devient "la cote du matin" ; une
        # analyse ultérieure avec une cote différente doit la conserver
        # et calculer la vraie variation par rapport à elle.
        import sqlite3, types, os
        import archive_store
        conn_reelle = sqlite3.connect(":memory:")

        class FauxCurseur:
            def __init__(self, c): self.c = c
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def execute(self, sql, params=None):
                sql2 = (sql.replace("DOUBLE PRECISION", "REAL").replace("TIMESTAMPTZ", "TEXT")
                           .replace("NOW()", "'now'").replace("%s", "?")
                           .replace("ON CONFLICT (course_key, numero) DO NOTHING", "")
                           .replace("INSERT INTO az_cote_matin", "INSERT OR IGNORE INTO az_cote_matin"))
                self.c.execute(sql2, params or ())
            def fetchone(self): return self.c.fetchone()

        class FausseConnexion:
            def cursor(self): return FauxCurseur(conn_reelle.cursor())
            def commit(self): conn_reelle.commit()
            def close(self): pass

        ancienne_connexion = archive_store._connexion
        try:
            archive_store._connexion = lambda: FausseConnexion()
            r1 = archive_store.obtenir_cotes_matin("course:test|R1|1", {"3": 15.0})
            r2 = archive_store.obtenir_cotes_matin("course:test|R1|1", {"3": 6.0})
            assert r1 == {"3": 15.0}
            assert r2 == {"3": 15.0}, "la cote du matin doit rester celle de la 1re observation"
        finally:
            archive_store._connexion = ancienne_connexion


    def test_calibration_etendue_aux_bonus_premium(self):
        # La calibration ne couvre plus seulement les 5 critères continus
        # (forme, régularité...) mais aussi les bonus binaires Premium :
        # ici, le déferrage rendu volontairement discriminant.
        from modules.learning_turf import calculer_calibration, SEUIL_MIN_COURSES
        import random
        rng = random.Random(3)
        lignes = []
        for _ in range(SEUIL_MIN_COURSES + 10):
            numeros = list(range(1, 13))
            rng.shuffle(numeros)
            arrivee = [str(n) for n in numeros[:5]]
            chevaux = []
            for n in numeros:
                est_place = str(n) in arrivee
                deferre = ("D4" if rng.random() < 0.7 else "") if est_place else ("D4" if rng.random() < 0.15 else "")
                chevaux.append({
                    "numero": str(n), "forme": rng.uniform(3, 7), "regularite": rng.uniform(3, 7),
                    "jockey_score": 5.0, "cote": rng.uniform(2, 20), "experience": 5.0,
                    "cote_brute": rng.uniform(2, 30), "deferre": deferre,
                })
            lignes.append({"chevaux_json": chevaux, "arrivee_json": arrivee})
        resultat = calculer_calibration(lignes)
        assert resultat["status"] == "success"
        assert resultat["facteurs"]["bonus_deferrage"] > 1.10
        for signal in ("bonus_outsider_chaud", "bonus_deferrage"):
            assert 0.80 <= resultat["facteurs"][signal] <= 1.20


    def test_facteurs_de_calibration_des_bonus_sont_appliques_et_retrocompatibles(self):
        from scoring import calculer_score_az
        from engine import calculer_indice_premium
        cheval = {"forme": 5, "regularite": 5, "gains": 5, "jockey_score": 5, "cote": 5, "distance": 5, "terrain": 5, "experience": 5, "deferre": "D4"}
        sans_defer = calculer_score_az(dict(cheval, deferre=""), "TROT_ATTELE")
        assert round(calculer_score_az(cheval, "TROT_ATTELE") - sans_defer, 2) == 18.0
        assert round(calculer_score_az(cheval, "TROT_ATTELE", calibration={"bonus_deferrage": 1.2}) - sans_defer, 2) == 21.6

        info_course = {"distance": 2000}
        outsider = {"numero": "9", "indice_az": 100, "forme": 8, "regularite": 7.5, "cote": 3, "cote_brute": 15.0, "experience": 5, "performances": []}
        sans_calib = calculer_indice_premium(outsider, info_course)
        avec_calib = calculer_indice_premium(outsider, info_course, calibration={"bonus_outsider_chaud": 0.8})
        assert round(sans_calib - avec_calib, 2) == 1.6
        assert calculer_indice_premium(outsider, info_course) == calculer_indice_premium(outsider, info_course, calibration={})
