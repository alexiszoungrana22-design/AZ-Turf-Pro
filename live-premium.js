/* AZ Turf Pro — Tableau des partants Live Premium
   Correctif V31 : l'accès administrateur est vérifié sur le serveur.
   Si la page est ouverte dans un autre onglet (sessionStorage non partagé),
   l'administrateur peut se reconnecter directement depuis cette page.
   Les routes backend et les autres pages restent inchangées.
*/

const API_URL = window.AZ_API_BASE || "https://az-turf-pro.onrender.com";

function afficherMessageLive(message, erreur = false) {
    let zone = document.getElementById("live-message");
    if (!zone) {
        zone = document.createElement("p");
        zone.id = "live-message";
        zone.setAttribute("role", "status");
        zone.style.margin = "10px 0";
        zone.style.padding = "9px 12px";
        zone.style.borderRadius = "8px";
        const bouton = document.getElementById("btn-toggle-tableau");
        if (bouton && bouton.parentNode) bouton.parentNode.insertBefore(zone, bouton.nextSibling);
    }
    zone.textContent = message;
    zone.style.color = erreur ? "#991b1b" : "#166534";
    zone.style.background = erreur ? "#fee2e2" : "#dcfce7";
    zone.style.display = message ? "block" : "none";
}

async function obtenirAccesLive() {
    if (!window.AZAuth) {
        afficherMessageLive("Le module de sécurité est indisponible. Rechargez la page.", true);
        return false;
    }

    // Un jeton Premium valide est déjà géré par le backend lors de l'appel API.
    if (window.AZAuth.getPremiumToken()) return true;

    // Vérifie une éventuelle clé administrateur déjà présente dans cet onglet.
    const cleExistante = window.AZAuth.getAdminKey();
    if (cleExistante) {
        try {
            const verification = await fetch(window.azApiUrl("/api/admin/verification"), {
                method: "GET",
                cache: "no-store",
                headers: { "X-Admin-Key": cleExistante, "Accept": "application/json" }
            });
            if (verification.ok) return true;
        } catch (error) {
            afficherMessageLive("Impossible de vérifier la session administrateur. Vérifiez votre connexion.", true);
            return false;
        }
    }

    // sessionStorage est propre à chaque onglet : proposer une reconnexion ici.
    const cle = window.prompt("Accès administrateur requis. Entrez votre clé administrateur AZ Turf Pro :");
    if (!cle || !cle.trim()) {
        afficherMessageLive("Connexion administrateur annulée. Le tableau Live reste protégé.", true);
        return false;
    }

    afficherMessageLive("Vérification de la clé administrateur…");
    const connecte = await window.AZAuth.loginAdmin(cle.trim());
    if (!connecte) {
        afficherMessageLive("Clé administrateur incorrecte ou serveur indisponible.", true);
        return false;
    }

    afficherMessageLive("Accès administrateur vérifié.");
    return true;
}

document.addEventListener("DOMContentLoaded", () => {
    const btnTableau = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");
    const contenuPremium = document.getElementById("contenu-premium");

    if (!btnTableau || !conteneurTableau) return;

    // Ne jamais désactiver le bouton uniquement parce que la session est
    // absente de cet onglet : l'administrateur pourra s'authentifier au clic.
    btnTableau.disabled = false;

    if (contenuPremium) {
        contenuPremium.classList.toggle("zone-masquee", !window.AZAuth || !window.AZAuth.hasAccess());
    }

    if (window.AZAuth && window.AZAuth.hasAccess()) {
        chargerTicketsPremiumLive();
    }

    btnTableau.addEventListener("click", async () => {
        if (!conteneurTableau.classList.contains("zone-masquee")) {
            conteneurTableau.classList.add("zone-masquee");
            btnTableau.innerText = "📊 Afficher le Tableau des Partants (Live)";
            return;
        }

        btnTableau.disabled = true;
        try {
            const autorise = await obtenirAccesLive();
            if (!autorise) return;

            if (contenuPremium) contenuPremium.classList.remove("zone-masquee");
            await chargerTableauPartantsLive();
            conteneurTableau.classList.remove("zone-masquee");
            btnTableau.innerText = "❌ Masquer le Tableau Live";
            chargerTicketsPremiumLive();
        } finally {
            btnTableau.disabled = false;
        }
    });
});

async function chargerTableauPartantsLive() {
    const tbody = document.getElementById("all-horses");
    if (!tbody) return;

    tbody.innerHTML = "";
    const ligneChargement = document.createElement("tr");
    const celluleChargement = document.createElement("td");
    celluleChargement.colSpan = 5;
    celluleChargement.textContent = "Chargement des partants…";
    ligneChargement.appendChild(celluleChargement);
    tbody.appendChild(ligneChargement);

    try {
        const res = await fetch(window.azApiUrl("/api/partants") || `${API_URL}/api/partants`, {
            method: "GET",
            cache: "no-store",
            headers: { "Accept": "application/json", ...window.AZAuth.authHeaders() }
        });
        if (!res.ok) {
            let detail = "";
            try {
                const erreur = await res.json();
                detail = erreur.detail || "";
            } catch (_) {}
            throw new Error(detail || `Erreur serveur (${res.status})`);
        }

        const data = await res.json();
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error("Aucun partant disponible pour le moment.");
        }

        tbody.innerHTML = "";
        data.forEach(cheval => {
            const ligne = document.createElement("tr");
            [cheval.rang, cheval.numero, cheval.nom, cheval.indice, cheval.confiance].forEach(valeur => {
                const cellule = document.createElement("td");
                cellule.textContent = valeur === null || valeur === undefined || valeur === "" ? "—" : String(valeur);
                ligne.appendChild(cellule);
            });
            tbody.appendChild(ligne);
        });
        afficherMessageLive(`${data.length} partant(s) chargé(s).`);
    } catch (e) {
        tbody.innerHTML = "";
        const ligne = document.createElement("tr");
        const cellule = document.createElement("td");
        cellule.colSpan = 5;
        cellule.textContent = e.message || "Données indisponibles.";
        ligne.appendChild(cellule);
        tbody.appendChild(ligne);
        afficherMessageLive(e.message || "Données indisponibles.", true);
    }
}

function formaterPastilles(texte) {
    const parties = String(texte || "").split("/");
    const conv = (chaine) => chaine.split(/[-,\s]+/).filter(Boolean).map(n => {
        if (/^\d+$/.test(n)) return `<span class="numero-cheval">${n.padStart(2, "0")}</span>`;
        if (n.toUpperCase() === "X") return '<span class="numero-cheval" style="background:#d97706">X</span>';
        return n;
    }).join(" ");
    return parties.length > 1 ? conv(parties[0]) + " / " + conv(parties[1]) : conv(texte);
}

async function chargerTicketsPremiumLive() {
    if (!window.AZAuth || !window.AZAuth.hasAccess()) return;

    try {
        const reponse = await fetch(window.azApiUrl("/api/analyse") || `${API_URL}/api/analyse`, {
            method: "GET",
            cache: "no-store",
            headers: { "Accept": "application/json", ...window.AZAuth.authHeaders() }
        });

        if (!reponse.ok) throw new Error(`Erreur API analyse : ${reponse.status}`);

        const data = await reponse.json();
        const tickets = data && data.tickets && data.tickets.premium ? data.tickets.premium : {};
        const quinte = Array.isArray(tickets.quinte)
            ? tickets.quinte.map(Number).filter(Number.isFinite).slice(0, 6).join(" - ")
            : "Non disponible";
        const champ = tickets.champ_reduit && tickets.champ_reduit.format
            ? tickets.champ_reduit.format
            : "Non disponible";

        const quinteElement = document.getElementById("quinte-premium");
        const champElement = document.getElementById("champ-reduit-premium");
        if (quinteElement) quinteElement.innerHTML = formaterPastilles(quinte);
        if (champElement) champElement.innerHTML = formaterPastilles(champ);
    } catch (error) {
        console.error("Erreur chargement ticket Premium live :", error);
        const quinteElement = document.getElementById("quinte-premium");
        const champElement = document.getElementById("champ-reduit-premium");
        if (quinteElement) quinteElement.textContent = "Données Premium indisponibles";
        if (champElement) champElement.textContent = "Données Premium indisponibles";
    }
}
