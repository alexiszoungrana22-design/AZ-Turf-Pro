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

    // Gestion de la sauvegarde des contacts Admin
    const btnSauvegarder = document.getElementById("btn-sauvegarder-contacts");
    if (btnSauvegarder) {
        btnSauvegarder.addEventListener("click", function () {
            const contact = document.getElementById("admin-input-contact").value;
            localStorage.setItem("AZ_TURF_CONTACT_PAIEMENT", contact);
            alert("✅ Contacts de paiement mis à jour avec succès !");
        });
    }
    const contactSauvegarde = localStorage.getItem("AZ_TURF_CONTACT_PAIEMENT");
    if (contactSauvegarde) {
        const inputContact = document.getElementById("admin-input-contact");
        if (inputContact) inputContact.value = contactSauvegarde;
    }
});

async function verifierAccesEtChargerTickets() {
    const tel = localStorage.getItem("AZ_TURF_TELEPHONE");
    const isLocalActive = localStorage.getItem("AZ_TURF_PREMIUM_ACTIF") === "true";
    const blocage = document.getElementById("message-blocage");
    const contenu = document.getElementById("contenu-premium");
    const blocAdmin = document.getElementById("bloc-admin-paiements");

    let accesAutorise = false;
    let estAdmin = false;

    if (tel === "ADMINISTRATEUR" || tel === "COMPTE ADMINISTRATEUR") {
        accesAutorise = true;
        estAdmin = true;
    } else if (isLocalActive) {
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
        if (blocAdmin && estAdmin) blocAdmin.classList.remove("zone-masquee");
        chargerDonneesAPI();
    } else {
        if (blocage) blocage.classList.remove("zone-masquee");
        if (contenu) contenu.classList.add("zone-masquee");
        if (blocAdmin) blocAdmin.classList.add("zone-masquee");
    }
}

// Convertisseur universel tout-terrain pour extraire du texte propre peu importe la structure backend
function extraireContenuInfaillible(valeur) {
    if (valeur === undefined || valeur === null) return "";
    
    // Si c'est déjà une chaîne de caractères
    if (typeof valeur === 'string') return valeur;
    
    // Si c'est un tableau (ex: ["08", "06", "01"])
    if (Array.isArray(valeur)) {
        return valeur.map(e => extraireContenuInfaillible(e)).filter(Boolean).join(" - ");
    }
    
    // Si c'est un objet (ex: champ réduit ou structure complexe)
    if (typeof valeur === 'object') {
        if (valeur.bases || valeur.complements) {
            const b = extraireContenuInfaillible(valeur.bases);
            const c = extraireContenuInfaillible(valeur.complements);
            if (b && c) return `${b} / ${c}`;
            return b || c;
        }
        if (valeur.selection) return extraireContenuInfaillible(valeur.selection);
        if (valeur.valeur) return extraireContenuInfaillible(valeur.valeur);
        if (valeur.texte) return extraireContenuInfaillible(valeur.texte);
        if (valeur.format) return extraireContenuInfaillible(valeur.format);
        if (valeur.combinaison) return extraireContenuInfaillible(valeur.combinaison);
    }
    
    return String(valeur);
}

async function chargerDonneesAPI() {
    try {
        const response = await fetch('https://az-turf-pro.onrender.com/api/analyse');
        const data = await response.json();

        // Récupération globale du sous-objet premium s'il existe
        let prem = {};
        if (data && data.tickets && data.tickets.premium) {
            prem = data.tickets.premium;
        } else if (data && data.tickets) {
            prem = data.tickets;
        }

        // On vérifie d'abord dans 'prem', puis directement à la racine de 'data' ou 'data.tickets'
        const ticketsRemplis = {
            selection: extraireContenuInfaillible(prem.selection || data.selection),
            explication: extraireContenuInfaillible(prem.explication || data.explication),
            quinte: extraireContenuInfaillible(prem.quinte || (data.tickets && data.tickets.quinte)),
            quarte: extraireContenuInfaillible(prem.quarte || (data.tickets && data.tickets.quarte)),
            trio: extraireContenuInfaillible(prem.trio || (data.tickets && data.tickets.trio)),
            couple: extraireContenuInfaillible(prem.couple || prem.coupleGagnant || (data.tickets && data.tickets.couple)),
            champReduit: extraireContenuInfaillible(prem.champReduit || prem.champ_reduit || (data.tickets && data.tickets.champReduit)),
            derniereMinute: extraireContenuInfaillible(prem.derniereMinute || prem.derniere_minute || (data.tickets && data.tickets.derniereMinute)),
            analyse: extraireContenuInfaillible(prem.analyse || data.analyse),
            message: extraireContenuInfaillible(prem.message || data.message)
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
        if (estCombine && contenu) {
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
    injecter("derniere-minute-premium", data.derniereMinute, true);
    injecter("analyse-premium", data.analyse, false);
    injecter("message-premium", data.message, false);
}
