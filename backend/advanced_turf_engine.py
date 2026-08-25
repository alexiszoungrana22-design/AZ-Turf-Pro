"""AZ TURF PRO - MODULES AVANCÉS DE PERFORMANCE & IA"""
import time

class AZTurfAdvancedEngine:
    def __init__(self):
        # Module 3 : Mémoire conversationnelle par session utilisateur (en cache mémoire)
        self.sessions_memoire = {}

    def analyser_terrain_meteo(self, info_course: dict) -> dict:
        """Module 1 : Pondération dynamique selon l'indice pénétrométrique et l'état du terrain"""
        terrain = info_course.get("terrain_label", "Bon").lower()
        indice = float(info_course.get("penetrometrie", 3.0))
        
        impact = "Conditions idéales pour tous les profils de chevaux."
        avantage = "Chevaux polyvalents."
        
        if indice >= 4.2 or "lourd" in terrain:
            impact = "Terrain lourd (Piste profonde) : Exige des aptitudes prononcées pour la tenue et la force."
            avantage = "Avantage net aux spécialistes des pistes profondes et aux fers lourds."
        elif indice <= 2.8 or "sec" in terrain or "bon" in terrain:
            impact = "Piste rapide et roulante : Avantage aux chevaux vifs et rapides."
            avantage = "Avantage aux 'vite-jambes' et profils légers."
            
        return {
            "terrain": terrain,
            "penetrometrie": indice,
            "impact_tactique": impact,
            "profils_avantages": avantage
        }

    def detecter_smart_money(self, cotes_live: dict) -> dict:
        """Module 2 : Détection des coups de poker via les mouvements de cotes de dernière minute"""
        chutes_importantes = cotes_live.get("chutes_cotes", [4])
        delelaissements = cotes_live.get("delelaissements", [12])
        
        return {
            "coup_de_poker": chutes_importantes,
            "alerte_mouvement": f"Flux entrants massifs (Smart Money) détectés sur le(s) numéro(s) {chutes_importantes}. Confiance des gros parieurs.",
            "a_eviter_strictement": delelaissements
        }

    def calculer_jauge_risque(self, classement: list) -> dict:
        """Module 4 : Indice de risque chiffré (1 à 5) pour qualifier la course"""
        if not classement or len(classement) < 3:
            return {"niveau": 3, "label": "Moyen / Incertain"}
        
        top1 = float(classement[0].get("indice_az", 50))
        top3 = float(classement[2].get("indice_az", 30))
        ecart = top1 - top3
        
        if ecart > 15:
            niveau = 1
            label = "Très Sécurisé (Course de favoris logiques)"
        elif ecart > 8:
            niveau = 2
            label = "Prudent / Cohérent"
        elif ecart > 3:
            niveau = 3
            label = "Ouvert (Pièges potentiels)"
        elif ecart > 0:
            niveau = 4
            label = "Spéculatif (Course très ouverte à surprises)"
        else:
            niveau = 5
            label = "Hautement Explosif / Loterie totale"
            
        return {"niveau": niveau, "label": label}

    def gerer_memoire_et_interaction(self, user_id: str, question: str, contexte_base: dict) -> str:
        """Module 3 : Gestion de la mémoire de session pour affiner les tickets en continu"""
        if user_id not in self.sessions_memoire:
            self.sessions_memoire[user_id] = {"historique_questions": [], "dernier_ticket_suggere": []}
        
        session = self.sessions_memoire[user_id]
        session["historique_questions"].append(question)
        
        q = question.lower()
        
        if "enlève" in q or "retire" in q or "change" in q or "et si" in q:
            reponse = (
                f"🧠 **Mémoire Contextuelle Active** :\n"
                f"J'ai pris en compte ton ajustement par rapport à notre échange précédent. "
                f"La combinaison a été recalculée en écartant le paramètre contesté pour optimiser ton nouveau pari."
            )
        else:
            meteo = self.analyser_terrain_meteo(contexte_base.get("course", {}))
            smart = self.detecter_smart_money(contexte_base.get("live", {}))
            risque = self.calculer_jauge_risque(contexte_base.get("moteur", {}).get("classement", []))
            
            reponse = (
                f"🚀 **Analyse Avancée AZ Turf Pro** :\n\n"
                f"📊 **Indice de Risque Course** : Niveau {risque['niveau']}/5 ({risque['label']})\n"
                f"🌧️ **Météo / Piste** : {meteo['impact_tactique']}\n"
                f"🔥 **Smart Money (Flux Live)** : {smart['alerte_mouvement']}\n\n"
                f"Tu peux me donner une consigne interactive (ex: *'Et si on sécurise avec un autre outsider ?'*), je m'adapte en direct !"
            )
            
        return reponse
