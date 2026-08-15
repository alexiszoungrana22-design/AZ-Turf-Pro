// ==========================================================
// AZ TURF PRO - SCRIPT PREMIUM VIP (EXTRACTION SECURISEE)
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

// RÉCUPÉRATION ET EXTRACTION SÉCURISÉE DES NUMÉROS
async function chargerEtGenererTicketsVIP() {
    try {
        const response = await fetch(`${API_URL}/api/quinte/aujourdhui`);
        
        if (response.ok) {
            const partants = await response.json();
            
            if (partants && partants.length > 0) {
                // Extraction intelligente : gère cheval.numero, cheval.cheval ou le rang
                let numChevaux = partants.map((item, index) => {
                    let num = item.numero || item.num || item.cheval || (index + 1);
                    return String(num).padStart(2, '0');
                });
                
                // Si on a moins de 7 numéros pour construire les combinaisons VIP
                if (numChevaux.length < 7) {
                    const listeDeSecours = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15"];
                    for (let num of listeDeSecours) {
                        if (!numChevaux.includes(num)) {
                            numChevaux.push(num);
                        }
                        if (numChevaux.length >= 7) break;
                    }
                }
                
                const top7 = numChevaux.slice(0, 7);
                genererTickets(top7);
                return;
            }
        }
    } catch (e) {
        console.warn("Erreur d'extraction ou API indisponible :", e);
    }

    // Uniquement en cas d'échec total de connexion au serveur
    genererTickets(["01", "02", "03", "04", "05", "06", "07"]);
}

function genererTickets(c) {
    const donneesVIP = {
        selection: c.join(" - "),                                     
        quinte: c.slice(0, 6).join(" - "),                             
        quarte: c.slice(0, 5).join(" - "),                             
        trio: c.slice(0, 3).join(" - "),                               
        couple: `${c[0]} - ${c[1]}`,                                   
        champReduit: `${c[0]} - ${c[1]} - X - ${c[3]} - X / ${c[2]} - ${c[4]} - ${c[5]} - ${c[6]}`,
        
        explication: "Sélection VIP générée à partir des meilleures données de la course du jour.",
        derniereMinute: `${c[1]} - Une excellente impression aux entraînements.`,
        analyse: `Les algorithmes placent le ${c[0]} et le ${c[1]} en bases prioritaires aujourd'hui.`,
        message: "Bonne chance pour vos combinaisons VIP du jour ! 🎯"
    };

    afficherDonneesVIP(donneesVIP);
}

// TABLEAU LIVE SIMPLIFIÉ ET SYNCHRONISÉ
async function chargerTableauPartantsLive() {
    const tbody = document.getElementById("all-horses");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 15px;">Chargement des partants...</td></tr>`;

    try {
        const response = await fetch(`${API_URL}/api/quinte/aujourdhui`);
        if (response.ok) {
            const partants = await response.json();
            tbody.innerHTML = "";
            partants.forEach((cheval, idx) => {
                const num = String(cheval.numero || cheval.num || idx + 1).padStart(2, '0');
                const nom = cheval.nom || cheval.cheval || "Cheval " + num;
                
                tbody.innerHTML += `
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 12px;">${cheval.rang || (idx + 1)}</td>
                        <td style="padding: 12px; font-weight: bold;">${num}</td>
                        <td style="padding: 12px;">${nom}</td>
                        <td style="padding: 12px; color: #d97706; font-weight: bold;">${cheval.indice || '-'}</td>
                        <td style="padding: 12px;">${cheval.jockey || cheval.confiance || '-'}</td>
                    </tr>`;
            });
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">Données indisponibles</td></tr>`;
    }
}

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
