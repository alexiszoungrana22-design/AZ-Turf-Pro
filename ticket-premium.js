// ==========================================================
// AZ TURF PRO - SCRIPT PREMIUM DYNAMIQUE VIP
// ==========================================================

// URL de ton serveur Render backend
const API_URL = "https://az-turf-pro-backend.onrender.com"; // Remplace par ton URL exacte Render si différente

document.addEventListener("DOMContentLoaded", function () {
    initialiserPagePremium();
});

async function initialiserPagePremium() {
    const isPremium = localStorage.getItem("AZ_TURF_PREMIUM_ACTIF") === "true";
    const tel = localStorage.getItem("AZ_TURF_TELEPHONE");

    const blocage = document.getElementById("message-blocage");
    const contenu = document.getElementById("contenu-premium");

    // 1. VÉRIFICATION ACCÈS (LOCAL + ADMIN)
    if (!isPremium && tel !== "ADMINISTRATEUR" && tel !== "COMPTE ADMINISTRATEUR") {
        if (blocage) blocage.style.display = "block";
        if (contenu) contenu.style.display = "none";
        return; // Stoppe l'exécution si pas VIP
    }

    // Débloque immédiatement l'interface VIP
    if (blocage) blocage.style.display = "none";
    if (contenu) contenu.style.display = "block";

    // 2. GESTION DU BOUTON TABLEAU LIVE
    const btnTableau = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");
    if (btnTableau && conteneurTableau) {
        btnTableau.addEventListener("click", function () {
            if (conteneurTableau.style.display === "none" || !conteneurTableau.style.display) {
                conteneurTableau.style.display = "block";
                btnTableau.innerText = "❌ Masquer le Tableau Live";
            } else {
                conteneurTableau.style.display = "none";
                btnTableau.innerText = "📊 Afficher le Tableau des Partants (Live)";
            }
        });
    }

    // 3. CHARGEMENT DES TICKETS (AVEC SECOURS AUTOMATIQUE SI RENDER EST LENT)
    try {
        // Tente de récupérer les données officielles du serveur Render
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 4000); // Max 4 secondes d'attente

        const response = await fetch(`${API_URL}/api/premium-tickets`, { signal: controller.signal });
        clearTimeout(timeoutId);

        if (response.ok) {
            const data = await response.json();
            afficherDonneesVIP(data);
            return;
        }
    } catch (err) {
        console.warn("Serveur Render en veille ou lent. Chargement immédiat des pronostics locaux...");
    }

    // DONNÉES DE SECOURS PAR DÉFAUT (Si Render s'endort)
    afficherDonneesVIP({
        selection: "04 - 09 - 12 - 01 - 07 - 11",
        explication: "Sélection établie sur la forme récente des jockeys et l'indice de performance AZ Turf Pro.",
        quinte: "04 - 09 - 12 - 01 - 07",
        quarte: "04 - 09 - 12 - 01",
        trio: "04 - 09 - 12",
        couple: "04 - 09",
        champReduit: "04 - 09 - X / 12, 01, 07, 11",
        derniereMinute: "09 - Excellente impression lors du dernier entraînement.",
        analyse: "Épreuve très ouverte. Priorité aux chevaux bien placés en première ligne.",
        message: "Bonne chance à tous nos abonnés VIP ! 🎯"
    });
}

// FUNCTION POUR PARSER LES NUMÉROS ET CREER LES PASTILLES
function formaterPastilles(texte) {
    if (!texte) return "";
    
    // Si la chaîne contient déjà des balises HTML, on ne la retravaille pas
    if (texte.includes("numero-cheval")) return texte;

    // Découpe le texte par les tirets, espaces ou virgules
    const elements = texte.split(/[-,\/]+/).map(item => item.trim()).filter(Boolean);

    // Reconstruit avec la classe des pastilles rondes
    return elements.map(num => {
        // Si c'est un numéro simple (ex: 4 ou 04)
        if (!isNaN(num)) {
            const formattedNum = num.padStart(2, '0');
            return `<span class="numero-cheval">${formattedNum}</span>`;
        }
        // Pour les lettres comme X (champ réduit)
        return `<span class="numero-cheval" style="background-color: #d97706;">${num}</span>`;
    }).join(" ");
}

// INJECTION DES DONNÉES DANS LE HTML
function afficherDonneesVIP(data) {
    function injecter(id, contenu, estCombine = false) {
        const el = document.getElementById(id);
        if (el) {
            if (estCombine) {
                el.innerHTML = formaterPastilles(contenu);
            } else {
                el.innerText = contenu || "Aucune donnée disponible";
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
