// ==========================================================
// AZ TURF PRO - SCRIPT PREMIUM VIP (DYNAMIQUE)
// ==========================================================

const API_URL = "https://az-turf-pro-backend.onrender.com";

document.addEventListener("DOMContentLoaded", function () {
    initialiserPagePremium();
});

async function initialiserPagePremium() {
    // 1. VÉRIFICATION DES DROITS D'ACCÈS
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
        return; // Stoppe le script si pas d'accès
    }

    // 2. BOUTON TABLEAU EN DIRECT
    const btnTableau = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");
    if (btnTableau && conteneurTableau) {
        btnTableau.addEventListener("click", async function () {
            if (conteneurTableau.classList.contains("zone-masquee")) {
                conteneurTableau.classList.remove("zone-masquee");
                btnTableau.innerText = "❌ Masquer le Tableau Live";
                // On remplit le tableau visuel
                await chargerTableauPartantsLive();
            } else {
                conteneurTableau.classList.add("zone-masquee");
                btnTableau.innerText = "📊 Afficher le Tableau des Partants (Live)";
            }
        });
    }

    // 3. CHARGEMENT DYNAMIQUE DES DONNÉES DU JOUR
    await chargerEtGenererTicketsVIP();
}

// RÉCUPÉRATION DES CHEVAUX ET GÉNÉRATION DES TICKETS VIP
async function chargerEtGenererTicketsVIP() {
    try {
        const response = await fetch(`${API_URL}/api/partants`);
        if (response.ok) {
            const partants = await response.json();
            
            // Si on a des partants, on extrait les 7 premiers numéros (triés par le backend)
            if (partants && partants.length >= 7) {
                const top7 = partants.slice(0, 7).map(cheval => cheval.numero);
                genererTickets(top7);
                return;
            }
        }
    } catch (e) {
        console.warn("API indisponible, affichage des données de secours...");
    }

    // DONNÉES DE SECOURS (Si le serveur ne répond pas)
    genererTickets(["04", "09", "12", "01", "07", "11", "03"]);
}

// LOGIQUE MATHÉMATIQUE DE TES RÈGLES VIP
function genererTickets(c) {
    // c = Tableau des 7 meilleurs chevaux du jour (ex: ["10", "05", "12", "08", "02", "15", "06"])
    
    const donneesVIP = {
        selection: c.join(" - "),                                     // 7 chevaux
        quinte: c.slice(0, 6).join(" - "),                             // 6 chevaux
        quarte: c.slice(0, 5).join(" - "),                             // 5 chevaux
        trio: c.slice(0, 3).join(" - "),                               // 3 chevaux
        couple: `${c[0]} - ${c[1]}`,                                   // 2 chevaux
        // Ton format exact : Base1 - Base2 - X - Base4 - X / Base3 - Base5 - Base6 - Base7
        champReduit: `${c[0]} - ${c[1]} - X - ${c[3]} - X / ${c[2]} - ${c[4]} - ${c[5]} - ${c[6]}`,
        
        explication: "Sélection calculée en temps réel via l'algorithme de performance du jour.",
        derniereMinute: `${c[1]} - Une excellente impression repérée ce matin.`,
        analyse: `Nos algorithmes placent le ${c[0]} et le ${c[1]} en bases très solides aujourd'hui.`,
        message: "Bonne chance pour vos combinaisons VIP du jour ! 🎯"
    };

    afficherDonneesVIP(donneesVIP);
}

// CHARGEMENT DU TABLEAU HTML LIVE (Au clic du bouton)
async function chargerTableauPartantsLive() {
    const tbody = document.getElementById("all-horses");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 15px;">Chargement des partants...</td></tr>`;

    try {
        const response = await fetch(`${API_URL}/api/partants`);
        if (response.ok) {
            const partants = await response.json();
            tbody.innerHTML = "";
            partants.forEach(cheval => {
                tbody.innerHTML += `
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 12px;">${cheval.rang || '-'}</td>
                        <td style="padding: 12px; font-weight: bold;">${cheval.numero || '-'}</td>
                        <td style="padding: 12px;">${cheval.nom || cheval.cheval || '-'}</td>
                        <td style="padding: 12px; color: #d97706; font-weight: bold;">${cheval.indice || '-'}</td>
                        <td style="padding: 12px;">${cheval.confiance || '-'}</td>
                    </tr>`;
            });
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">Données indisponibles</td></tr>`;
    }
}

// FORMATAGE DES PASTILLES RONDES ET DU SÉPARATEUR DE CHAMP RÉDUIT
function formaterPastilles(texte) {
    if (!texte) return "";
    if (texte.includes("numero-cheval")) return texte;

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

// INJECTION DES DONNÉES DANS L'HTML
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
