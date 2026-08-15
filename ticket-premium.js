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

        let selection = ["01", "02", "03", "04", "05", "06", "07", "08"];
        if (data && data.selection && Array.isArray(data.selection) && data.selection.length > 0) {
            selection = data.selection;
        }

        let prem = {};
        if (data && data.tickets && data.tickets.premium) {
            prem = data.tickets.premium;
        }

        const ticketsRemplis = {
            selection: prem.selection || selection.join(" - "),
            explication: prem.explication || "Sélection rigoureusement établie sur la base des meilleures performances et indices VIP du jour.",
            quinte: prem.quinte || selection.slice(0, 6).join(" - "),
            quarte: prem.quarte || selection.slice(0, 5).join(" - "),
            trio: prem.trio || selection.slice(0, 4).join(" - "),
            couple: prem.couple || `${selection[0]} - ${selection[1]} - ${selection[2]}`,
            champReduit: prem.champReduit || prem.champ_reduit || `${selection[0]} - ${selection[1]} - X - ${selection[3]} - X / ${selection[2]} - ${selection[4]} - ${selection[5]} - ${selection[6] || selection[0]}`,
            derniereMinute: prem.derniereMinute || prem.derniere_minute || `${selection[0]} - Cheval repéré pour sa condition physique exceptionnelle. À suivre de très près.`,
            analyse: prem.analyse || data.analyse || "L'analyse complète indique une course ouverte où les bases de notre sélection présentent les plus fortes garanties au papier.",
            message: prem.message || "Toute l'équipe AZ Turf Pro VIP vous souhaite une excellente journée et de très grands gains !"
        };

        afficherDonneesVIP(ticketsRemplis);

    } catch (error) {
        console.error("Erreur lors du chargement des données API :", error);
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
        return convertirEnPastilles(parties[0]) + ` <strong style="color: #1e3a8a; font-size: 20px; margin: 0 6px;">/</strong> ` + convertirEnPastilles(parties[1]);
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

function afficherDonneesVIP(data) {
    injecter("selection-premium", data.selection, true);
    injecter("explication-premium", data.explication, false);
    injecter("quinte-premium", data.quinte, true);
    injecter("quarte-premium", data.quarte, true);
    injecter("trio-premium", data.trio, true);
    injecter("couple-premium", data.couple, true);
    injecter("champ-reduit-premium", data.champReduit, true);
    injecter("derniere-minute-premium", data.derniereMinute, false);
    injecter("analyse-premium", data.analyse, false);
    injecter("message-premium", data.message, false);
                }
