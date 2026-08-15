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

    if (isLocalActive || tel === "ADMINISTRATEUR" || tel === "COMPTE ADMINISTRATEUR") {
        if (blocage) blocage.classList.add("zone-masquee");
        if (contenu) contenu.classList.remove("zone-masquee");
        chargerDonneesAPI();
        return;
    }

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
            console.error("Erreur d'authentification :", e);
        }
    }

    if (blocage) blocage.classList.remove("zone-masquee");
    if (contenu) contenu.classList.add("zone-masquee");
}

async function chargerDonneesAPI() {
    try {
        const response = await fetch('https://az-turf-pro.onrender.com/api/analyse');
        const data = await response.json();

        // Récupération sécurisée des tickets renvoyés par l'API
        let ticketsData = null;
        if (data && data.tickets && data.tickets.premium) {
            ticketsData = data.tickets.premium;
        } else if (data && data.selection) {
            const sel = data.selection;
            ticketsData = {
                selection: sel.join(" - "),
                quinte: sel.slice(0, 6).join(" - "),
                quarte: sel.slice(0, 5).join(" - "),
                trio: sel.slice(0, 3).join(" - "),
                couple: `${sel[0]} - ${sel[1]}`,
                champReduit: sel.length >= 7 ? `${sel[0]} - ${sel[1]} - X - ${sel[3]} - X / ${sel[2]} - ${sel[4]} - ${sel[5]} - ${sel[6]}` : sel.join(" - "),
                explication: "Sélection VIP établie selon nos critères.",
                derniereMinute: `${sel[1]} - Repéré pour sa forme.",
                analyse: data.analyse || "Analyse indisponible pour le moment.",
                message: "Bonne chance à tous les membres VIP !"
            };
        }

        if (ticketsData) {
            afficherDonneesVIP(ticketsData);
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

    injecter("selection-premium", data.selection || data.selection_VIP, true);
    injecter("explication-premium", data.explication, false);
    injecter("quinte-premium", data.quinte, true);
    injecter("quarte-premium", data.quarte, true);
    injecter("trio-premium", data.trio, true);
    injecter("couple-premium", data.couple || data.couple_gagnant_place, true);
    injecter("champ-reduit-premium", data.champReduit || data.champ_reduit, true);
    injecter("derniere-minute-premium", data.derniereMinute || data.derniere_minute, false);
    injecter("analyse-premium", data.analyse, false);
    injecter("message-premium", data.message, false);
}
