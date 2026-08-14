// ==========================================================
// AZ TURF PRO - SCRIPT PREMIUM DYNAMIQUE VIP (V4)
// ==========================================================

const API_URL = "https://az-turf-pro-backend.onrender.com"; // Remplace par ton URL exacte Render

document.addEventListener("DOMContentLoaded", function () {
    initialiserPagePremium();
});

async function initialiserPagePremium() {
    const isPremium = localStorage.getItem("AZ_TURF_PREMIUM_ACTIF") === "true";
    const tel = localStorage.getItem("AZ_TURF_TELEPHONE");

    const blocage = document.getElementById("message-blocage");
    const contenu = document.getElementById("contenu-premium");

    // GESTION DU DÉVERROUILLAGE SANS CONFLIT
    if (isPremium || tel === "ADMINISTRATEUR" || tel === "COMPTE ADMINISTRATEUR") {
        if (blocage) blocage.classList.add("zone-masquee");
        if (contenu) contenu.classList.remove("zone-masquee");
    } else {
        if (blocage) blocage.classList.remove("zone-masquee");
        if (contenu) contenu.classList.add("zone-masquee");
        return; // Stoppe l'exécution si non VIP
    }

    // BOUTON TABLEAU LIVE
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

    // CHARGEMENT DES DONNÉES DEPUIS RENDER OU SECOURS
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3500); // 3.5 sec max

        const response = await fetch(`${API_URL}/api/premium-tickets`, { signal: controller.signal });
        clearTimeout(timeoutId);

        if (response.ok) {
            const data = await response.json();
            afficherDonneesVIP(data);
            return;
        }
    } catch (err) {
        console.warn("Réseau lent ou Render en veille. Activation des données VIP locales...");
    }

    // DONNÉES PAR DÉFAUT SI LE SERVEUR EST LENT
    afficherDonneesVIP({
        selection: "04 - 09 - 12 - 01 - 07 - 11",
        explication: "Sélection basée sur l'indice de forme des chevaux et des jockeys du jour.",
        quinte: "04 - 09 - 12 - 01 - 07",
        quarte: "04 - 09 - 12 - 01",
        trio: "04 - 09 - 12",
        couple: "04 - 09",
        champReduit: "04 - 09 - X / 12, 01, 07, 11",
        derniereMinute: "09 - Très belles impressions le matin à l'entraînement.",
        analyse: "Épreuve ouverte. Avantage aux numéros du premier poteau.",
        message: "Bonne chance pour vos jeux du jour ! 🎯"
    });
}

// MISE EN FORME DES PASTILLES NUMÉROTÉES
function formaterPastilles(texte) {
    if (!texte) return "";
    if (texte.includes("numero-cheval")) return texte;

    const elements = texte.split(/[-,\/]+/).map(item => item.trim()).filter(Boolean);

    return elements.map(num => {
        if (!isNaN(num)) {
            const formattedNum = num.padStart(2, '0');
            return `<span class="numero-cheval">${formattedNum}</span>`;
        }
        return `<span class="numero-cheval" style="background-color: #d97706;">${num}</span>`;
    }).join(" ");
}

// INJECTION DANS LE DOM
function afficherDonneesVIP(data) {
    function injecter(id, contenu, estCombine = false) {
        const el = document.getElementById(id);
        if (el) {
            if (estCombine) {
                el.innerHTML = formaterPastilles(contenu);
            } else {
                el.innerText = contenu || "Donnée non disponible";
            }
        }
    }

    injecter("selection-premium", data.selection, true);
    injecter("explication-premium", data.explication, false);
    injecter("quinte-premium", data.quinte, true);
    injecter("quarte-premium", data.quarte, true);
    injecter("trio-premium", data.trio, true);
    injecter("couple-premium", data.couple, true);
    injecter("champ-reduit-premium", data.champReduit, true);
    injecter("derniere-minute-premium", data.derniereMinute, true);
    injecter("analyse-premium", data.analyse, false);
    injecter("message-premium", data.message, false);
}
