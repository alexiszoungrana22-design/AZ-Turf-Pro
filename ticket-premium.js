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

        const normaliserFormat = (val) => {
            if (!val) return "";
            if (Array.isArray(val)) return val.join(" - ");
            return String(val);
        };

        // Extraire proprement le champ réduit
        let cr = prem.champReduit || prem.champ_reduit;
        let basesCR = [];
        let complementsCR = [];
        if (typeof cr === 'object' && cr !== null) {
            basesCR = Array.isArray(cr.bases) ? cr.bases : [];
            complementsCR = Array.isArray(cr.complements) ? cr.complements : [];
            const b = basesCR.join(" - ");
            const c = complementsCR.join(" - ");
            cr = (b && c) ? `${b} / ${c}` : (b || c || cr.format || "");
        }

        // Récupération des tickets de base
        const quinteTxt = normaliserFormat(prem.quinte);
        const quarteTxt = normaliserFormat(prem.quarte);
        const trioTxt = normaliserFormat(prem.trio);

        // 1. SÉLECTION DU JOUR : Garantie exacte à 7 chevaux
        let selectionTxt = normaliserFormat(prem.selection || data.selection);
        let listeNums = selectionTxt ? selectionTxt.split(/[-,\s]+/).filter(num => !isNaN(num) && num.trim() !== '') : [];

        if (listeNums.length !== 7) {
            // Reconstitution automatique à 7 chevaux à partir du Quinté et Compléments
            let numsQuinte = quinteTxt.split(/[-,\s]+/).filter(num => !isNaN(num) && num.trim() !== '');
            let tousLesNums = Array.from(new Set([...numsQuinte, ...basesCR, ...complementsCR]));
            if (tousLesNums.length >= 7) {
                selectionTxt = tousLesNums.slice(0, 7).join(" - ");
            } else if (numsQuinte.length > 0) {
                selectionTxt = numsQuinte.slice(0, 7).join(" - ");
            }
        }

        // 2. COUPLÉ GAGNANT PLACÉ
        let coupleTxt = normaliserFormat(prem.couple || prem.coupleGagnant);
        if (!coupleTxt && quinteTxt) {
            let numsQuinte = quinteTxt.split(/[-,\s]+/).filter(num => !isNaN(num) && num.trim() !== '');
            coupleTxt = numsQuinte.slice(0, 3).join(" - ");
        }

        // 3. DERNIÈRE MINUTE : Ne reste plus jamais vide
        let dmTxt = normaliserFormat(prem.derniereMinute || prem.derniere_minute || data.derniereMinute);
        if (!dmTxt && quinteTxt) {
            let premierCheval = quinteTxt.split(/[-,\s]+/).filter(num => !isNaN(num) && num.trim() !== '')[0] || "08";
            dmTxt = premierCheval;
        }

        const ticketsRemplis = {
            selection: selectionTxt,
            explication: prem.explication || "Sélection VIP rigoureusement établie sur la base des meilleures performances du jour.",
            quinte: quinteTxt,
            quarte: quarteTxt,
            trio: trioTxt,
            couple: coupleTxt,
            champReduit: cr,
            derniereMinute: dmTxt,
            analyse: prem.analyse || data.analyse || "L'analyse indique une course ouverte où les bases VIP présentent les plus fortes garanties.",
            message: prem.message || "Toute l'équipe AZ Turf Pro VIP vous souhaite une excellente journée et de très grands gains !"
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
