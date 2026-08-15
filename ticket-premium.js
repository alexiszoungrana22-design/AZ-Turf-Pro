// ==========================================================
// AZ TURF PRO - TICKETS PREMIUM (AFFICHAGE NORMAL D'ORIGINE)
// ==========================================================

document.addEventListener("DOMContentLoaded", function () {
    initialiserPagePremium();
});

function initialiserPagePremium() {
    // 1. VÉRIFICATION DE LA SÉCURITÉ ABONNÉ / ADMIN
    const isPremium = localStorage.getItem("AZ_TURF_PREMIUM_ACTIF") === "true";
    const tel = localStorage.getItem("AZ_TURF_TELEPHONE");
    const blocage = document.getElementById("message-blocage");
    const contenu = document.getElementById("contenu-premium");

    if (isPremium || tel === "ADMINISTRATEUR" || tel === "COMPTE ADMINISTRATEUR") {
        if (blocage) blocage.classList.add("zone-masquee");
        if (contenu) contenu.classList.remove("zone-masquee");
    } else {
        if (blocage) blocage.classList.remove("zone-masquee");
        if (contenu) contenu.classList.add("zone-masquee");
        return; 
    }

    // 2. GESTION DU BOUTON DU TABLEAU LIVE (OPTIONNEL)
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

    // 3. CHARGEMENT DES TICKETS D'ORIGINE
    chargerTicketsOriginaux();
}

function chargerTicketsOriginaux() {
    // Données stables d'origine pour les tickets premium
    const selection = ["04", "09", "12", "01", "07", "11", "03"];

    const donneesVIP = {
        selection: selection.join(" - "),
        quinte: selection.slice(0, 6).join(" - "),
        quarte: selection.slice(0, 5).join(" - "),
        trio: selection.slice(0, 3).join(" - "),
        couple: `${selection[0]} - ${selection[1]}`,
        // Ton format de champ réduit d'origine : Base1 - Base2 - X - Base4 - X / Base3 - Base5 - Base6 - Base7
        champReduit: `${selection[0]} - ${selection[1]} - X - ${selection[3]} - X / ${selection[2]} - ${selection[4]} - ${selection[5]} - ${selection[6]}`,
        
        explication: "Sélection rigoureusement établie selon nos critères de sélection VIP.",
        derniereMinute: `${selection[1]} - Très remarqué lors des heats d'échauffement.`,
        analyse: `Nos analyses placent en priorité le ${selection[0]} et le ${selection[1]} pour disputer les premières places.`,
        message: "Bonne chance à tous les membres VIP pour cette course ! 🎯"
    };

    afficherDonneesVIP(donneesVIP);
}

// FORMATAGE DES PASTILLES (BULLES DE NUMÉROS)
function formaterPastilles(texte) {
    if (!texte) return "";
    if (texte.includes("numero-cheval")) return texte;

    const parties = texte.split('/');
    
    function convertirEnPastilles(chaine) {
        const elements = chaine.split(/[-,\s]+/).map(item => item.trim()).filter(Boolean);
        return elements.map(num => {
            if (!isNaN(num)) {
                const formattedNum = String(num).padStart(2, '0');
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
    injecter("champ-reduit-premium", data.champReduit, true);
    injecter("derniere-minute-premium", data.derniereMinute, true);
    injecter("analyse-premium", data.analyse, false);
    injecter("message-premium", data.message, false);
}
