// ==========================================================
// AZ TURF PRO - TICKETS PREMIUM (VERSION SÉCURISÉE & ORIGINALE)
// ==========================================================

document.addEventListener("DOMContentLoaded", function () {
    verifierAccesEtChargerTickets();

    // Gestion du bouton du tableau live
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

    // Cas administrateur ou abonnement local actif
    if (isLocalActive || tel === "ADMINISTRATEUR" || tel === "COMPTE ADMINISTRATEUR") {
        if (blocage) blocage.classList.add("zone-masquee");
        if (contenu) contenu.classList.remove("zone-masquee");
        chargerDonneesAPI();
        return;
    }

    // Vérification via l'API pour les abonnés
    if (tel) {
        try {
            const response = await fetch(`https://az-turf-pro.onrender.com/api/premium/${tel}`);
            const data = await response.json();

            if (data && data.isPremium) {
                if (blocage) blocage.classList.add("zone-masquee");
                if (contenu) contenu.classList.remove("zone-masquee");
                chargerDonneesAPI();
                return;
            }
        } catch (e) {
            console.error("Erreur lors de la vérification de l'abonnement :", e);
        }
    }

    // Si non abonné ou échec : on bloque l'accès
    if (blocage) blocage.classList.remove("zone-masquee");
    if (contenu) contenu.classList.add("zone-masquee");
}

async function chargerDonneesAPI() {
    try {
        const response = await fetch('https://az-turf-pro.onrender.com/api/analyse');
        const data = await response.json();

        // On vérifie si les tickets premium renvoyés par l'API existent
        if (data && data.tickets && data.tickets.premium) {
            afficherDonneesVIP(data.tickets.premium);
        } else if (data && data.selection) {
            // Structure de secours si l'API renvoie une sélection brute
            construireTicketsDepuisSelection(data.selection);
        }
    } catch (error) {
        console.error("Erreur de récupération des données de l'API :", error);
    }
}

function construireTicketsDepuisSelection(selection) {
    if (!Array.isArray(selection) || selection.length === 0) return;

    const donneesVIP = {
        selection: selection.join(" - "),
        quinte: selection.slice(0, 6).join(" - "),
        quarte: selection.slice(0, 5).join(" - "),
        trio: selection.slice(0, 3).join(" - "),
        couple: `${selection[0]} - ${selection[1]}`,
        champReduit: selection.length >= 7 ? `${selection[0]} - ${selection[1]} - X - ${selection[3]} - X / ${selection[2]} - ${selection[4]} - ${selection[5]} - ${selection[6]}` : selection.join(" - "),
        explication: "Sélection rigoureusement établie selon nos critères de sélection VIP.",
        derniereMinute: `${selection[1]} - Repéré pour sa forme du jour.`,
        analyse: `Nos analyses placent en priorité le ${selection[0]} et le ${selection[1]} pour disputer les premières places.`,
        message: "Bonne chance à tous les membres VIP pour cette course ! 🎯"
    };

    afficherDonneesVIP(donneesVIP);
}

// FORMATAGE DES PASTILLES
function formaterPastilles(texte) {
    if (!texte) return "";
    if (typeof texte !== 'string') texte = String(texte);
    if (texte.includes("numero-cheval")) return texte;

    const parties = texte.split('/');
    
    function convertirEnPastilles(chaine) {
        const elements = chaine.split(/[-,\s]+/).map(item => item.trim()).filter(Boolean);
        return elements.map(num => {
            if (!isNaN(num)) {
                return `<span class="numero-cheval">${String(num).padStart(2, '0')}</span>`;
            } else if (num.toUpperCase() === 'X') {
                return `<span class="numero-cheval" style="background-color: #d97706;">X</span>`;
            }
            return num;
        }).join(" ");
    }

    if (parties.length > 1) {
        return convertirEnPastilles(parties[0]) + 
               ` <strong style="font-size: 20px; color: #0f172a; margin: 0 6px;">/</strong> ` + 
               convertirEnPastilles(parties[1]);
    }

    return convertirEnPastilles(texte);
}

// INJECTION DANS LA PAGE HTML
function afficherDonneesVIP(data) {
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

    injecter("selection-premium", data.selection, true);
    injecter("explication-premium", data.explication, false);
    injecter("quinte-premium", data.quinte, true);
    injecter("quarte-premium", data.quarte, true);
    injecter("trio-premium", data.trio, true);
    injecter("couple-premium", data.couple, true);
    injecter("champ-reduit-premium", data.champReduit || data.champ_reduit, true);
    injecter("derniere-minute-premium", data.derniereMinute || data.derniere_minute, false);
    injecter("analyse-premium", data.analyse, false);
    injecter("message-premium", data.message, false);
        }
