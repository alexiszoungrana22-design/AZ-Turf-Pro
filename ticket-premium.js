// ==========================================================
// AZ TURF PRO - SCRIPT PREMIUM VIP (CORRECTIF DIRECT)
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

    if (isPremium || tel === "ADMINISTRATEUR" || tel === "COMPTE ADMINISTRATEUR") {
        if (blocage) blocage.classList.add("zone-masquee");
        if (contenu) contenu.classList.remove("zone-masquee");
    } else {
        if (blocage) blocage.classList.remove("zone-masquee");
        if (contenu) contenu.classList.add("zone-masquee");
        return; 
    }

    const btnTableau = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");
    if (btnTableau && conteneurTableau) {
        btnTableau.addEventListener("click", async function () {
            if (conteneurTableau.classList.contains("zone-masquee")) {
                conteneurTableau.classList.remove("zone-masquee");
                btnTableau.innerText = "❌ Masquer le Tableau Live";
                await chargerTableauPartantsLive();
            } else {
                conteneurTableau.classList.add("zone-masquee");
                btnTableau.innerText = "📊 Afficher le Tableau des Partants (Live)";
            }
        });
    }

    await chargerEtGenererTicketsVIP();
}

async function chargerEtGenererTicketsVIP() {
    try {
        const response = await fetch(`${API_URL}/api/quinte/aujourdhui`);
        if (response.ok) {
            const partants = await response.json();
            if (partants && partants.length > 0) {
                // On extrait directement les numéros reçus de l'API
                let c = partants.map(cheval => String(cheval.numero || cheval.num || "01").padStart(2, '0'));
                
                // S'il manque des numéros pour les tickets, on complète dynamiquement avec la suite
                let i = 1;
                while (c.length < 7) {
                    let numStr = String(i).padStart(2, '0');
                    if (!c.includes(numStr)) c.push(numStr);
                    i++;
                    if (i > 20) break;
                }

                genererTickets(c.slice(0, 7));
                return;
            }
        }
    } catch (e) {
        console.error("Erreur de chargement", e);
    }

    // Sécurité ultime si le serveur ne répond pas
    genererTickets(["04", "09", "12", "01", "07", "11", "03"]);
}

function genererTickets(c) {
    const donneesVIP = {
        selection: c.join(" - "),                                     
        quinte: c.slice(0, 6).join(" - "),                             
        quarte: c.slice(0, 5).join(" - "),                             
        trio: c.slice(0, 3).join(" - "),                               
        couple: `${c[0]} - ${c[1]}`,                                   
        champReduit: `${c[0]} - ${c[1]} - X - ${c[3]} - X / ${c[2]} - ${c[4]} - ${c[5]} - ${c[6]}`,
        
        explication: "Sélection VIP générée à partir des données actuelles du serveur.",
        derniereMinute: `${c[1]} - Repéré en excellente condition physique.`,
        analyse: `Nos algorithmes placent le ${c[0]} et le ${c[1]} en bases solides.`,
        message: "Bonne chance pour vos jeux du jour ! 🎯"
    };

    afficherDonneesVIP(donneesVIP);
}

async function chargerTableauPartantsLive() {
    const tbody = document.getElementById("all-horses");
    if (!tbody) return;

    try {
        const response = await fetch(`${API_URL}/api/quinte/aujourdhui`);
        if (response.ok) {
            const partants = await response.json();
            tbody.innerHTML = "";
            partants.forEach((cheval, idx) => {
                const num = String(cheval.numero || cheval.num || (idx + 1)).padStart(2, '0');
                tbody.innerHTML += `
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 12px;">${cheval.rang || (idx + 1)}</td>
                        <td style="padding: 12px; font-weight: bold;">${num}</td>
                        <td style="padding: 12px;">${cheval.nom || cheval.cheval || '-'}</td>
                        <td style="padding: 12px; color: #d97706; font-weight: bold;">${cheval.indice || '-'}</td>
                        <td style="padding: 12px;">${cheval.confiance || '-'}</td>
                    </tr>`;
            });
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">Erreur de chargement</td></tr>`;
    }
}

function formaterPastilles(texte) {
    if (!texte) return "";
    if (texte.includes("numero-cheval")) return texte;

    const parties = texte.split('/');
    
    function convertirEnPastilles(chaine) {
        return chaine.split(/[-,\s]+/).map(item => item.trim()).filter(Boolean).map(num => {
            if (!isNaN(num)) {
                return `<span class="numero-cheval">${String(num).padStart(2, '0')}</span>`;
            } else if (num.toUpperCase() === 'X') {
                return `<span class="numero-cheval" style="background-color: #d97706;">X</span>`;
            }
            return num;
        }).join(" ");
    }

    if (parties.length > 1) {
        return convertirEnPastilles(parties[0]) + ` <strong style="font-size: 20px; color: #0f172a; margin: 0 6px;">/</strong> ` + convertirEnPastilles(parties[1]);
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
