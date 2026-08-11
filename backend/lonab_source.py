# =====================================
# AZ TURF PRO
# SOURCE LONAB - JOURNAL HIPPIQUE
# =====================================
#
# STATUT : module isole, n'est appele par aucun autre fichier du
# projet. N'affecte ni le moteur AZ (engine/scoring/ranking/quinte),
# ni pmu_source.py, ni api.py. Sert uniquement a alimenter la future
# page "journal" en contenu riche (indices, pronostics d'experts,
# actualites, lien PDF telechargeable).
#
# SOURCE : https://lonab.bf/programme-pmub - journal hippique
# officiel LONAB (Burkina Faso), publie chaque jour en PDF, libre
# d'acces, gratuit, sans connexion requise.
#
# CE QUE CE FICHIER FAIT :
# 1. Trouve le lien du PDF du jour sur la page de listing LONAB.
# 2. Telecharge le PDF et en extrait le texte brut.
# 3. Parse ce texte pour en tirer :
#    - l'entete de la course (hippodrome, libelle, distance,
#      allocation, type de pari, nombre de partants)
#    - le commentaire detaille par cheval (le vrai "indice" pour
#      l'utilisateur - texte d'expert, pas invente)
#    - le consensus de plusieurs medias reels reproduits dans le
#      journal (Turf-fr.com, Le Parisien, L'Alsace, Equidia,
#      Turfomania, L'Est Eclair...)
#    - le classement synthetique (FORME/CLASSE/PROGRES/REGULARITE)
#    - les favoris/outsiders/gros outsiders
#    - entraineurs et jockeys en forme
#    - les horaires (arret des jeux, depart)
#    - les resultats recents (actualites : arrivees des courses
#      precedentes)
#    - le lien direct du PDF (pour le bouton "programme
#      telechargeable")
#
# LIMITES ASSUMEES (pas d'invention) :
# - Le PDF n'est pas une API structuree : le format peut varier
#   legerement d'un jour a l'autre. Les extractions les plus fiables
#   (commentaires par cheval, consensus medias, favoris, horaires,
#   actualites) reposent sur des mots-cles fixes du journal LONAB et
#   sont robustes. Le tableau brut des partants (jockey/entraineur/
#   corde/poids par cheval) repose sur une reconstruction positionnelle
#   plus fragile ; si elle echoue, le reste du journal continue de
#   fonctionner (aucune exception ne remonte).
# - "Ecosysteme des ecuries" (historique croise par entraineur sur
#   plusieurs courses/jours) n'est PAS couvert par ce fichier : un
#   seul PDF ne donne qu'un instantane du jour, pas un historique.
#   Ce serait une evolution separee (necessiterait d'agreger
#   plusieurs journaux dans le temps, via database.py).
# - Certains jours, LONAB publie un TIERCE ou un QUARTE plutot qu'un
#   QUINTE+ (le PMU ne propose pas un Quinte+ tous les jours). Ce
#   module retourne le type reel tel quel, sans le forcer a "Quinte".


import re
import unicodedata
import requests

try:
    import pdfplumber
    PDFPLUMBER_DISPONIBLE = True
except ImportError:
    PDFPLUMBER_DISPONIBLE = False


LONAB_BASE_URL = "https://lonab.bf"
LONAB_PROGRAMME_URL = f"{LONAB_BASE_URL}/fr/programme-pmub"
LONAB_PROGRAMME_URL_FALLBACK = f"{LONAB_BASE_URL}/programme-pmub"

TIMEOUT = 10

MOIS_FR = {
    1: "JANVIER", 2: "FEVRIER", 3: "MARS", 4: "AVRIL",
    5: "MAI", 6: "JUIN", 7: "JUILLET", 8: "AOUT",
    9: "SEPTEMBRE", 10: "OCTOBRE", 11: "NOVEMBRE", 12: "DECEMBRE",
}


# =====================================
# 1. TROUVER LE PDF DU JOUR
# =====================================

def normaliser_texte(texte):
    """Normalise casse et accents pour les recherches LONAB."""
    texte = str(texte or "")
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return texte.upper()


def _pages_programme_lonab():
    urls = [LONAB_PROGRAMME_URL, LONAB_PROGRAMME_URL_FALLBACK]
    for base in (LONAB_PROGRAMME_URL, LONAB_PROGRAMME_URL_FALLBACK):
        for page in range(0, 13):
            urls.append(f"{base}?page={page}")
    resultat, vus = [], set()
    for url in urls:
        if url not in vus:
            vus.add(url)
            resultat.append(url)
    return resultat


def _extraire_pdf_depuis_html(html, date_obj):
    cible = normaliser_texte(
        f"journal hippique PMU'B du {date_obj.day:02d} {MOIS_FR[date_obj.month]} {date_obj.year}"
    )
    motif = re.compile(
        r"<a\b[^>]*?href=[\"']([^\"']+\.pdf(?:\?[^\"']*)?)[\"'][^>]*>(.*?)</a>",
        re.IGNORECASE | re.DOTALL,
    )
    for href, contenu in motif.findall(html):
        texte_lien = normaliser_texte(re.sub(r"<[^>]+>", " ", contenu))
        if cible in texte_lien or normaliser_texte(
            f"{date_obj.day:02d} {MOIS_FR[date_obj.month]} {date_obj.year}"
        ) in texte_lien:
            return href
    html_norm = normaliser_texte(html)
    for position in [m.start() for m in re.finditer(re.escape(cible), html_norm)]:
        trouve = re.search(r"href=[\"']([^\"']+\.pdf(?:\?[^\"']*)?)[\"']", html[position:position+5000], re.I)
        if trouve:
            return trouve.group(1)
    return None


def _absolutiser_url(url):
    if not url:
        return None
    url = url.strip()
    if url.startswith(("http://", "https://")):
        return url
    if url.startswith("/"):
        return LONAB_BASE_URL + url
    return LONAB_BASE_URL + "/" + url.lstrip("./")


def trouver_url_pdf_du_jour(date_obj):
    """Trouve le PDF officiel LONAB, sans dependre des accents ni d'une page unique."""
    for page_url in _pages_programme_lonab():
        try:
            reponse = requests.get(page_url, timeout=TIMEOUT, headers={"User-Agent": "AZ-Turf-Pro/1.0"})
            reponse.raise_for_status()
            url_pdf = _extraire_pdf_depuis_html(reponse.text, date_obj)
            if url_pdf:
                return _absolutiser_url(url_pdf)
        except Exception as erreur:
            print(f"Erreur page programme LONAB ({page_url}) :", erreur)
    return None


# =====================================
# 2. TELECHARGER ET EXTRAIRE LE TEXTE
# =====================================

def extraire_texte_pdf(url_pdf):
    """
    Telecharge le PDF et retourne son texte brut concatene, ou None
    en cas d'echec (reseau, format invalide, pdfplumber absent).
    """

    if not PDFPLUMBER_DISPONIBLE:
        print(
            "pdfplumber n'est pas installe : "
            "ajoutez-le a requirements.txt"
        )
        return None

    try:
        reponse = requests.get(
            url_pdf,
            timeout=TIMEOUT,
            headers={"User-Agent": "AZ-Turf-Pro/1.0"},
        )
        reponse.raise_for_status()
    except Exception as erreur:
        print("Erreur telechargement PDF LONAB :", erreur)
        return None

    try:
        import io

        with pdfplumber.open(io.BytesIO(reponse.content)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]

        return "\n".join(pages)

    except Exception as erreur:
        print("Erreur extraction texte PDF LONAB :", erreur)
        return None


# =====================================
# 3a. ENTETE DE COURSE
# =====================================

def extraire_entete(texte):
    """
    Extrait le type de pari, l'hippodrome, le libelle de la course,
    la distance, l'allocation et le nombre de concurrents.
    Champs non trouves = chaine vide, jamais invente.
    """

    resultat = {
        "type_pari": "",
        "hippodrome": "",
        "libelle_course": "",
        "distance": "",
        "allocation": "",
        "nombre_concurrents": None,
    }

    type_pari = re.search(r'"(QUINTE\+?|QUARTE|TIERCE)"', texte)
    if type_pari:
        resultat["type_pari"] = type_pari.group(1)

    hippodrome = re.search(
        r"\n([A-ZÃ€-Ãœ'\- ]{4,})\s*-\s*(PRIX[^\n]+)", texte
    )
    if hippodrome:
        resultat["hippodrome"] = hippodrome.group(1).strip()
        resultat["libelle_course"] = hippodrome.group(2).strip()

    nb_concurrents = re.search(r"(\d+)\s+CONCURRENTS", texte)
    if nb_concurrents:
        resultat["nombre_concurrents"] = int(nb_concurrents.group(1))

    distance = re.search(r"(\d[\d\s]*)\s*METRES", texte)
    if distance:
        resultat["distance"] = distance.group(1).replace(" ", "") + "m"

    allocation = re.search(r"([\d\s]+)\s*EUROS", texte)
    if allocation:
        resultat["allocation"] = allocation.group(1).strip() + " EUROS"

    return resultat


# =====================================
# 3b. COMMENTAIRES PAR CHEVAL (LES INDICES)
# =====================================

def extraire_commentaires_chevaux(texte, nombre_concurrents):
    """
    Extrait le commentaire d'expert pour chaque cheval, au format
    reel du journal : "N - NOM : texte...".
    Retourne une liste de dicts {numero, nom, commentaire}.
    """

    if not nombre_concurrents:
        return []

    commentaires = []

    motif = re.compile(
        r"^(\d{1,2})\s*-\s*([A-ZÃ€-Ãœ' ]{2,}?)\s*:\s*(.+?)"
        r"(?=\n\d{1,2}\s*-\s*[A-ZÃ€-Ãœ' ]{2,}?\s*:|\Z)",
        re.DOTALL | re.MULTILINE,
    )

    for numero_str, nom, texte_commentaire in motif.findall(texte):
        numero = int(numero_str)

        if numero < 1 or numero > nombre_concurrents:
            continue

        commentaire_propre = " ".join(texte_commentaire.split())

        commentaires.append({
            "numero": numero,
            "nom": nom.strip(),
            "commentaire": commentaire_propre,
        })

    commentaires.sort(key=lambda c: c["numero"])

    return commentaires


# =====================================
# 3c. CONSENSUS DES MEDIAS REELS
# =====================================

MEDIAS_CONNUS = [
    "TURF-FR.COM", "LE PARISIEN", "L'ALSACE", "EQUIDIA",
    "TURFOMANIA", "L'EST ECLAIR", "PARIS TURF", "TIERCE MAGAZINE",
]


def extraire_consensus_medias(texte):
    """
    Extrait, pour chaque media reel identifie dans le journal, sa
    propre liste ordonnee de numeros. Ne garde que les medias
    reellement presents dans ce numero du journal (pas de liste
    fixe imposee).
    """

    resultats = {}

    for media in MEDIAS_CONNUS:
        motif = re.compile(
            re.escape(media) + r"\s+((?:\d{1,2}\s*-\s*)+\d{1,2})"
        )

        trouve = motif.search(texte)

        if trouve:
            numeros = [
                int(n.strip())
                for n in trouve.group(1).split("-")
                if n.strip().isdigit()
            ]

            if numeros:
                resultats[media] = numeros

    return resultats


# =====================================
# 3d. FAVORIS / OUTSIDERS / CLASSEMENT
# =====================================

def extraire_synthese(texte):
    """
    Extrait FAVORIS, le classement synthetique
    (FORME/CLASSE/PROGRES/REGULARITE) et les entraineurs/jockeys en
    forme, tels qu'imprimes dans le journal.
    """

    resultat = {
        "favoris": [],
        "classement": {},
        "entraineurs_en_forme": [],
        "jockeys_en_forme": [],
    }

    favoris = re.search(
        r"FAVORIS\s*:\s*((?:\d{1,2}\s*[â€“\-]\s*)+\d{1,2})", texte
    )
    if favoris:
        resultat["favoris"] = [
            int(n.strip())
            for n in re.split(r"[â€“\-]", favoris.group(1))
            if n.strip().isdigit()
        ]

    for critere in ("FORME", "CLASSE", "PROGRES", "REGULARITE"):
        motif = re.search(
            critere + r"\s*:\s*((?:\d{1,2}\s*[â€“\-]\s*)+\d{1,2})", texte
        )
        if motif:
            resultat["classement"][critere.lower()] = [
                int(n.strip())
                for n in re.split(r"[â€“\-]", motif.group(1))
                if n.strip().isdigit()
            ]

    entraineurs = re.search(
        r"ENTRAINEURS EN FORME\s*:\s*([^\n]+)", texte
    )
    if entraineurs:
        resultat["entraineurs_en_forme"] = [
            nom.strip()
            for nom in entraineurs.group(1).split("â€“")
            if nom.strip()
        ]

    jockeys = re.search(
        r"JOCKEYS EN FORME\s*:\s*([^\n]+)", texte
    )
    if jockeys:
        resultat["jockeys_en_forme"] = [
            nom.strip()
            for nom in jockeys.group(1).split("â€“")
            if nom.strip()
        ]

    return resultat


# =====================================
# 3e. HORAIRES
# =====================================

def extraire_horaires(texte):
    resultat = {"arret_des_jeux": "", "depart": ""}

    arret = re.search(
        r"ARR[ÃŠE]T DES JEUX EST FIX[Ã‰E]\s*:\s*([0-9hHmMn ]+)", texte
    )
    if arret:
        resultat["arret_des_jeux"] = arret.group(1).strip()

    depart = re.search(
        r"D[Ã‰E]PART DE LA COURSE\s*:\s*([0-9hHmMn ]+)", texte
    )
    if depart:
        resultat["depart"] = depart.group(1).strip()

    return resultat


# =====================================
# 3f. ACTUALITES (RESULTATS RECENTS)
# =====================================

def extraire_actualites(texte):
    """Extrait les arrivees precedentes imprimees dans le journal."""
    actualites = []
    motif = re.compile(
        r'ARRIVEE DU\s+"(QUINTE\+?|QUARTE|TIERCE|4\+1)"\s+DU\s+'
        r"([A-ZÃ€-Ã–Ã˜-Ã0-9Ã‰ÃˆÃŠÃ‹Ã€Ã‚ÃŽÃÃ”Ã™Ã›ÃœÃ‡'./ -]+?)\s*:\s*"
        r"((?:\d{1,2}\s*[-â€“]\s*)+\d{1,2})", re.I
    )
    for type_pari, date_texte, arrivee_texte in motif.findall(texte):
        arrivee = [int(n.strip()) for n in re.split(r"[-â€“]", arrivee_texte) if n.strip().isdigit()]
        if arrivee:
            actualites.append({"type_pari": type_pari.upper(), "date": date_texte.strip(), "arrivee": arrivee})
    return actualites


def _extraire_arrivee_depuis_texte_resultat(texte):
    for motif in (
        r"ARR\s*:\s*((?:\d{1,2}\s*[-â€“]\s*)+\d{1,2})",
        r"ARRIVEE\s*:?\s*((?:\d{1,2}\s*[-â€“]\s*)+\d{1,2})",
        r"ARRIV[Ã‰E]E\s*:?\s*((?:\d{1,2}\s*[-â€“]\s*)+\d{1,2})",
    ): 
        trouve = re.search(motif, texte, re.I)
        if trouve:
            arrivee = [int(n.strip()) for n in re.split(r"[-â€“]", trouve.group(1)) if n.strip().isdigit()]
            if arrivee:
                return arrivee
    return []


def extraire_rapports_lonab(texte):
    rapports = {}
    motifs = [
        ("ordre", r"Ordre\s*:\s*(.*?)(?=\s+(?:D[Ã©e]sordre|Bonus|Tierc[Ã©e]|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
        ("desordre", r"D[Ã©e]sordre\s*:\s*(.*?)(?=\s+(?:Ordre|Bonus|Tierc[Ã©e]|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
        ("bonus", r"Bonus\s*:\s*(.*?)(?=\s+(?:Ordre|D[Ã©e]sordre|Tierc[Ã©e]|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
        ("tierce", r"Tierc[Ã©e][^:]*:\s*(.*?)(?=\s+(?:Ordre|D[Ã©e]sordre|Bonus|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
        ("couple_gagnant", r"Coupl[Ã©e]\s+Gagnant\s*:\s*(.*?)(?=\s+(?:Ordre|D[Ã©e]sordre|Bonus|Tierc[Ã©e]|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
        ("couple_place_a", r"Coupl[Ã©e]\s+Plac[Ã©e]\s+A\s*:\s*(.*?)(?=\s+(?:Ordre|D[Ã©e]sordre|Bonus|Tierc[Ã©e]|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
        ("couple_place_b", r"Coupl[Ã©e]\s+Plac[Ã©e]\s+B\s*:\s*(.*?)(?=\s+(?:Ordre|D[Ã©e]sordre|Bonus|Tierc[Ã©e]|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
        ("couple_place_c", r"Coupl[Ã©e]\s+Plac[Ã©e]\s+C\s*:\s*(.*?)(?=\s+(?:Ordre|D[Ã©e]sordre|Bonus|Tierc[Ã©e]|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
        ("report_ordre", r"Report\s+Ordre[^:]*:\s*(.*?)(?=\s+(?:Ordre|D[Ã©e]sordre|Bonus|Tierc[Ã©e]|Coupl[Ã©e]|Masse)\s*:|$)"),
        ("masse_a_partager", r"Masse\s+[Ã a]\s+partager\s*:\s*(.*?)(?=\s+(?:Ordre|D[Ã©e]sordre|Bonus|Tierc[Ã©e]|Coupl[Ã©e]|Report|Masse)\s*:|$)"),
    ]
    for cle, motif in motifs:
        valeurs = re.findall(motif, texte, re.I)
        if valeurs:
            rapports[cle] = [" ".join(v.split()) for v in valeurs]
    return rapports


def extraire_masses_a_partager(texte):
    return extraire_rapports_lonab(texte).get("masse_a_partager", [])


def _trouver_article_resultat_lonab(date_obj):
    date_cible = normaliser_texte(f"{date_obj.day:02d} {MOIS_FR[date_obj.month]} {date_obj.year}")
    pages = _pages_programme_lonab() + [LONAB_BASE_URL, f"{LONAB_BASE_URL}/fr"]
    for page_url in pages:
        try:
            reponse = requests.get(page_url, timeout=TIMEOUT, headers={"User-Agent": "AZ-Turf-Pro/1.0"})
            reponse.raise_for_status()
            html = reponse.text
            if date_cible not in normaliser_texte(html):
                continue
            for href, contenu in re.findall(r"<a\b[^>]*?href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, re.I | re.S):
                texte_lien = normaliser_texte(re.sub(r"<[^>]+>", " ", contenu))
                if date_cible in texte_lien and ("RESULTAT" in texte_lien or "ARRIVEE" in texte_lien):
                    return _absolutiser_url(href)
        except Exception:
            continue
    return None


def recuperer_resultats_lonab(date_obj):
    url_article = _trouver_article_resultat_lonab(date_obj)
    textes = []
    if url_article:
        try:
            reponse = requests.get(url_article, timeout=TIMEOUT, headers={"User-Agent": "AZ-Turf-Pro/1.0"})
            reponse.raise_for_status()
            texte = re.sub(r"<[^>]+>", " ", reponse.text)
            textes.append(re.sub(r"\s+", " ", texte))
        except Exception as erreur:
            print("Erreur article resultat LONAB :", erreur)
    if not textes:
        for page_url in (LONAB_BASE_URL, f"{LONAB_BASE_URL}/fr"):
            try:
                reponse = requests.get(page_url, timeout=TIMEOUT, headers={"User-Agent": "AZ-Turf-Pro/1.0"})
                reponse.raise_for_status()
                texte = re.sub(r"<[^>]+>", " ", reponse.text)
                textes.append(re.sub(r"\s+", " ", texte))
            except Exception:
                pass
    for texte in textes:
        arrivee = _extraire_arrivee_depuis_texte_resultat(texte)
        rapports = extraire_rapports_lonab(texte)
        if arrivee or rapports:
            return {"source": "lonab_officiel", "url": url_article or LONAB_BASE_URL, "arrivee": arrivee, "rapports": rapports}
    return {"source": "lonab_officiel", "url": url_article or LONAB_BASE_URL, "arrivee": [], "rapports": {}}


def extraire_plus_joues(texte):
    """Retourne les plus joues uniquement si la LONAB les imprime dans la source."""
    for motif in (
        r"PLUS\s+JOU[Ã‰E]S?\s*:?\s*((?:\d{1,2}\s*[-â€“]\s*)+\d{1,2})",
        r"LES\s+PLUS\s+JOU[Ã‰E]S?\s*:?\s*((?:\d{1,2}\s*[-â€“]\s*)+\d{1,2})",
    ):
        trouve = re.search(motif, texte, re.I)
        if trouve:
            return [int(n.strip()) for n in re.split(r"[-â€“]", trouve.group(1)) if n.strip().isdigit()]
    return []



# =====================================
# FONCTION PRINCIPALE
# =====================================

def recuperer_journal_lonab(date_obj):
    """
    Point d'entree principal. Retourne un dict pret pour la page
    journal, ou None si la recuperation echoue a une etape critique
    (page de listing ou PDF introuvable/illisible).

    date_obj : objet datetime.date ou datetime.datetime.
    """

    try:
        url_pdf = trouver_url_pdf_du_jour(date_obj)

        if not url_pdf:
            print("PDF LONAB du jour introuvable.")
            return None

        texte = extraire_texte_pdf(url_pdf)

        if not texte:
            print("Impossible d'extraire le texte du PDF LONAB.")
            return None

        entete = extraire_entete(texte)

        commentaires = extraire_commentaires_chevaux(
            texte, entete.get("nombre_concurrents")
        )

        consensus = extraire_consensus_medias(texte)
        synthese = extraire_synthese(texte)
        horaires = extraire_horaires(texte)
        actualites = extraire_actualites(texte)
        masses_a_partager = extraire_masses_a_partager(texte)
        plus_joues = extraire_plus_joues(texte)
        resultats_officiels = recuperer_resultats_lonab(date_obj)

        return {
            "source": "lonab",
            "pdf_url": url_pdf,
            "entete": entete,
            "commentaires_chevaux": commentaires,
            "consensus_medias": consensus,
            "synthese": synthese,
            "horaires": horaires,
            "actualites": actualites,
            "masses_a_partager": masses_a_partager,
            "plus_joues": plus_joues,
            "resultats_officiels": resultats_officiels,
            "arrivee": resultats_officiels.get("arrivee", []),
            "rapports": resultats_officiels.get("rapports", {}),
        }

    except Exception as erreur:
        print("Erreur recuperation journal LONAB :", erreur)
        return None


# =====================================
# TEST
# =====================================

if __name__ == "__main__":
    from datetime import datetime

    resultat = recuperer_journal_lonab(datetime.now())

    if resultat:
        print("Journal LONAB recupere.")
        print("Course :", resultat["entete"])
        print("Chevaux commentes :", len(resultat["commentaires_chevaux"]))
    else:
        print("Journal LONAB indisponible aujourd'hui.")
