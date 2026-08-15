// ==========================================================
// AZ TURF PRO - TICKETS PREMIUM (CORRIGÉ & DYNAMIQUE)
// ==========================================================

document.addEventListener("DOMContentLoaded", function () {
    // 1. FORCAGE DE L'AFFICHAGE (Supprime les masquages pour éviter tout blocage)
    const blocage = document.getElementById("message-blocage");
    const contenu = document.getElementById("contenu-premium");
    
    if (blocage) blocage.classList.add("zone-masquee");
    if (contenu) contenu.classList.remove("zone-masquee");

    // 2. GESTION DU BOUTON DU TABLEAU LIVE
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

    // 3. CHARGEMENT AUTOMATIQUE DU QUINTÉ DU JOUR DEPUIS L'API
    chargerQuintePremiumDynamique();
});

async function chargerQuintePremiumDynamique() {
    try {
        // Interroge l'API backend pour récupérer les données du jour
        const response = await fetch('https://az-turf-pro-backend.onrender.com/api/quinte/aujourdhui');
        const data = await response.json();

        let selection = [];
        if (Array.isArray(data)) {
            selection = data.map(item => String(item.numero || item.num || item).padStart(2, '0'));
        } else if (data.selection) {
            selection = data.selection;
        }

        // Si l'API renvoie bien les chevaux, on génère les tickets premium du jour
        if (selection.length > 0) {
            const donneesVIP = {
                selection: selection.join(" - "),
                quinte: selection.slice(0, 6).join(" - "),
                quarte: selection.slice(0, 5).join(" - "),
                trio: selection.slice(0, 3).join(" - "),
                couple: `${selection[0]} - ${selection[1]}`,
                champReduit: `${selection[0]} - ${selection[1]} - X - ${selection[3]} - X / ${selection[2]} - ${selection[4]} - ${selection[5]} - ${selection[6]}`,
                explication: "Sélection VIP mise à jour automatiquement selon le quinté du jour.",
                derniereMinute: `${selection[1]} - Repéré pour sa forme du jour.`,
                analyse: `Nos analyses prioritaires basées sur le quinté du jour placent le ${selection[0]} et le ${selection[1]}.`,
                message: "Bonne chance à tous les abonnés pour cette course ! 🎯"
            };
            afficherDonneesVIP(donneesVIP);
        }
    } catch (error) {
        console.error("Erreur de chargement des tickets premium dynamiques :", error);
    }
}

// FORMATAGE DES PASTILLES
function formaterPastilles(texte) {
    if (!texte) return "";
    if (texte.includes("numero-cheval")) return texte;

    const parties = texte.split('/');
    
    function convertirEnPastilles(chaine) {
        const elements = String(chaine).split(/[-,\s]+/).map(item => item.trim()).filter(Boolean);
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
    injecter("champ-reduit-premium", data.champReduit, true);
    injecter("derniere-minute-premium", data.derniereMinute, true);
    injecter("analyse-premium", data.analyse, false);
    injecter("message-premium", data.message, false);
             }
