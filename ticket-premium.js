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

// Nettoyage et conversion sécurisée des données issues de l'API (tableaux, objets ou chaînes)
function extraireDonnee(champ, defaut = "") {
    if (!champ) return defaut;
    if (typeof champ === 'string') return champ;
    if (Array.isArray(champ)) return champ.join(" - ");
    if (typeof champ === 'object') {
        if (champ.bases || champ.complements) {
            const bases = Array.isArray(champ.bases) ? champ.bases.join(" - ") : (champ.bases || "");
            const complements = Array.isArray(champ.complements) ? champ.complements.join(" - ") : (champ.complements || "");
            return bases && complements ? `${bases} / ${complements}` : (bases || complements);
        }
        return champ.texte || champ.valeur || champ.combinaison || defaut;
    }
    return String(champ);
}

async function chargerDonneesAPI() {
    try {
        const response = await fetch('https://az-turf-pro.onrender.com/api/analyse');
        const data = await response.json();

        let prem = {};
        if (data && data.tickets && data.tickets.premium) {
            prem = data.tickets.premium;
        } else if (data && data.tickets) {
            prem = data.tickets;
        }

        const ticketsRemplis = {
            selection: extraireDonnee(prem.selection),
            explication: extraireDonnee(prem.explication),
            quinte: extraireDonnee(prem.quinte),
            quarte: extraireDonnee(prem.quarte),
            trio: extraireDonnee(prem.trio),
            couple: extraireDonnee(prem.couple),
            champReduit: extraireDonnee(prem.champReduit || prem.champ_reduit),
            derniereMinute: extraireDonnee(prem.derniereMinute || prem.derniere_minute),
            analyse: extraireDonnee(prem.analyse || data.analyse),
            message: extraireDonnee(prem.message)
        };

        afficherDonneesVIP(ticketsRemplis);

    } catch (error) {
        console.error("Erreur lors du chargement des données API :", error);
    }
}

// Transforme une chaîne de numéros ("08 - 06 - X / 01 - 02") en pastilles graphiques exactes de la page d'accueil/analyse
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
    injecter("derniere-minute-premium", data.derniereMinute, true);
    injecter("analyse-premium", data.analyse, false);
    injecter("message-premium", data.message, false);
}
