// ==========================================================
// AZ TURF PRO - SCRIPT PREMIUM VIP (RÈGLES EXACTES)
// ==========================================================

const API_URL = "https://az-turf-pro-backend.onrender.com";

document.addEventListener("DOMContentLoaded", function () {
    initialiserPagePremium();
});

async function initialiserPagePremium() {
    const isPremium = localStorage.getItem("AZ_TURF_PREMIUM_ACTIF") === "true";
    const tel = localStorage.getItem("AZ_TURF_TELEPHONE");

    const blocage = document.getElementById("message-blocage");
    const contenu = document.getElementById("contenu-premium");

    // 1. GESTION DES ACCÈS
    if (isPremium || tel === "ADMINISTRATEUR" || tel === "COMPTE ADMINISTRATEUR") {
        if (blocage) blocage.classList.add("zone-masquee");
        if (contenu) contenu.classList.remove("zone-masquee");
    } else {
        if (blocage) blocage.classList.remove("zone-masquee");
        if (contenu) contenu.classList.add("zone-masquee");
        return;
    }

    // 2. TOGGLE TABLEAU LIVE
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

    // 3. CHARGEMENT SERVEUR OU DONNÉES DE SECOURS
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3500);

        const response = await fetch(`${API_URL}/api/premium-tickets`, { signal: controller.signal });
        clearTimeout(timeoutId);

        if (response.ok) {
            const data = await response.json();
            afficherDonneesVIP(data);
            return;
        }
    } catch (err) {
        console.warn("Serveur en veille. Affichage des données VIP configurées...");
    }

    // DONNÉES EXACTES APPLIQUÉES SELON TES DIRECTIVES
    afficherDonneesVIP({
        selection: "04 - 09 - 12 - 01 - 07 - 11 - 03",             // 7 Chevaux
        explication: "Sélection rigoureuse basée sur l'Indice AZ, la régularité et la forme récente.",
        quinte: "04 - 09 - 12 - 01 - 07 - 11",                    // 6 Chevaux
        quarte: "04 - 09 - 12 - 01 - 07",                         // 5 Chevaux
        trio: "04 - 09 - 12",                                     // 3 Chevaux
        couple: "04 - 09",                                        // 2 Chevaux
        champReduit: "04 - 09 - X - 01 - X / 12 - 07 - 11 - 03",  // Format exact avec double X et associés
        derniereMinute: "09 - Très bonne impression lors de son dernier passage.",
        analyse: "Bases solides avec le 04 et le 09. Le 01 constitue la base intermédiaire idéale.",
        message: "Excellente chance à tous nos abonnés VIP ! 🎯"
    });
}

// FORMATAGE AUTO DES NUMÉROS ET SIGNES EN PASTILLES RONDES
function formaterPastilles(texte) {
    if (!texte) return "";
    if (texte.includes("numero-cheval")) return texte;

    // Sépare en conservant la barre de séparation /
    const parties = texte.split('/');
    
    function convertirEnPastilles(chaine) {
        const elements = chaine.split(/[-,\s]+/).map(item => item.trim()).filter(Boolean);
        return elements.map(num => {
            if (!isNaN(num)) {
                const formattedNum = num.padStart(2, '0');
                return `<span class="numero-cheval">${formattedNum}</span>`;
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
