document.addEventListener("DOMContentLoaded", function () {
    verifierAccesEtChargerTickets();

    const btnTableau = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");
    if (btnTableau && conteneurTableau) {
        btnTableau.addEventListener("click", function () {
            if (conteneurTableau.classList.contains("zone-masquee")) {
                conteneurTableau.classList.remove("zone-masquee");
                btnTableau.innerText = "❌ Masquer le Tableau Live";
            } else {
                conteneurTableau.classList.add("zone-masquee");
                btnTableau.innerText = "📊 Afficher le Tableau des Partants (Live)";
            }
        });
    }
});

async function verifierAccesEtChargerTickets() {
    const tel = localStorage.getItem("AZ_TURF_TELEPHONE");
    const isLocalActive = localStorage.getItem("AZ_TURF_PREMIUM_ACTIF") === "true";
    const blocage = document.getElementById("message-blocage");
    const contenu = document.getElementById("contenu-premium");

    let accesAutorise = false;

    if (isLocalActive || tel === "ADMINISTRATEUR" || tel === "COMPTE ADMINISTRATEUR") {
        accesAutorise = true;
    } else if (tel) {
        try {
            const response = await fetch(`https://az-turf-pro.onrender.com/api/premium/${tel}`);
            const data = await response.json();
            if (data && data.isPremium) {
                accesAutorise = true;
            }
        } catch (e) {
            console.error("Erreur d'authentification :", e);
            if (tel) accesAutorise = true; 
        }
    }

    if (accesAutorise) {
        if (blocage) blocage.classList.add("zone-masquee");
        if (contenu) contenu.classList.remove("zone-masquee");
        chargerDonneesAPI();
    } else {
        if (blocage) blocage.classList.remove("zone-masquee");
        if (contenu) contenu.classList.add("zone-masquee");
    }
}

async function chargerDonneesAPI() {
    try {
        const response = await fetch('https://az-turf-pro.onrender.com/api/analyse');
        const data = await response.json();

        // Récupération directe depuis l'objet 'tickets.premium' renvoyé par ton api.py
        if (data && data.tickets && data.tickets.premium) {
            const t = data.tickets.premium;
            
            // Remplissage direct de chaque champ avec les clés exactes du backend
            injecter("selection-premium", t.selection || t.selection_VIP, true);
            injecter("explication-premium", t.explication, false);
            injecter("quinte-premium", t.quinte, true);
            injecter("quarte-premium", t.quarte, true);
            injecter("trio-premium", t.trio, true);
            injecter("couple-premium", t.couple || t.couple_gagnant_place, true);
            injecter("champ-reduit-premium", t.champReduit || t.champ_reduit, true);
            injecter("derniere-minute-premium", t.derniereMinute || t.derniere_minute, false);
            injecter("analyse-premium", t.analyse, false);
            injecter("message-premium", t.message, false);
        } else {
            console.warn("Structure de tickets premium introuvable dans la réponse de l'API.");
        }
    } catch (error) {
        console.error("Erreur de récupération de l'API :", error);
    }
}

function formaterPastilles(texte) {
    if (!texte) return "";
    if (typeof texte !== 'string') texte = String(texte);
    if (texte.includes("numero-cheval")) return texte;

    const parties = texte.split('/');
    
    function convertirEnPastilles(chaine) {
        return chaine.split(/[-,\s]+/).map(item => item.trim()).filter(Boolean).map(num => {
            if (!isNaN(num)) {
                return `<span class="numero-cheval">${String(num).padStart(2, '0')}</span>`;
            } else if (num.toUpperCase() === 'X') {
                return `<span class="numero-cheval" style="background: linear-gradient(135deg, #d97706, #b45309);">X</span>`;
            }
            return num;
        }).join(" ");
    }

    if (parties.length > 1) {
        return convertirEnPastilles(parties[0]) + ` <strong style="color: #60a5fa; margin: 0 6px;">/</strong> ` + convertirEnPastilles(parties[1]);
    }

    return convertirEnPastilles(texte);
}

function injecter(id, contenu, estCombine = false) {
    const el = document.getElementById(id);
    if (el) {
        if (estCombine) {
            el.innerHTML = formaterPastilles(contenu);
        } else {
            el.innerText = contenu || "";
        }
    }
}
