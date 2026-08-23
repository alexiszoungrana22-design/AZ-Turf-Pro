const API_URL = window.location.origin;

function entetesAccesPremium() {
    const adminKey =
        sessionStorage.getItem("AZ_TURF_ADMIN_API_KEY") ||
        localStorage.getItem("AZ_TURF_ADMIN_API_KEY") ||
        sessionStorage.getItem("AZ_TURF_ADMIN_KEY") ||
        localStorage.getItem("AZ_TURF_ADMIN_KEY") ||
        sessionStorage.getItem("ADMIN_API_KEY") ||
        localStorage.getItem("ADMIN_API_KEY") ||
        "";
    const token = localStorage.getItem("AZ_TURF_PREMIUM_TOKEN") || "";
    if (adminKey) return { "X-Admin-Key": adminKey };
    if (token) return { "Authorization": "Bearer " + token };
    return {};
}

function accesLocalPremium() {
    return Boolean(
        sessionStorage.getItem("AZ_TURF_ADMIN_API_KEY") ||
        localStorage.getItem("AZ_TURF_ADMIN_API_KEY") ||
        sessionStorage.getItem("AZ_TURF_ADMIN_KEY") ||
        localStorage.getItem("AZ_TURF_ADMIN_KEY") ||
        sessionStorage.getItem("ADMIN_API_KEY") ||
        localStorage.getItem("ADMIN_API_KEY") ||
        localStorage.getItem("AZ_TURF_PREMIUM_TOKEN")
    );
}

document.addEventListener("DOMContentLoaded", () => {
    const btnTableau = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");
    
    // Toggle Tableau
    btnTableau.addEventListener("click", async () => {
        if (conteneurTableau.classList.contains("zone-masquee")) {
            conteneurTableau.classList.remove("zone-masquee");
            btnTableau.innerText = "❌ Masquer le Tableau Live";
            await chargerTableauPartantsLive();
        } else {
            conteneurTableau.classList.add("zone-masquee");
            btnTableau.innerText = "📊 Afficher le Tableau des Partants (Live)";
        }
    });

    const contenuPremium = document.getElementById("contenu-premium");
    chargerTicketsPremiumLive();
    if (contenuPremium) contenuPremium.classList.remove("zone-masquee");
    if (btnTableau) btnTableau.disabled = false;
});

async function chargerTableauPartantsLive() {
    const tbody = document.getElementById("all-horses");
    tbody.innerHTML = "<tr><td colspan='5'>Chargement...</td></tr>";
    try {
        const res = await fetch(`${API_URL}/api/partants`, {
            headers: { "Accept": "application/json", ...entetesAccesPremium() }
        });
        const data = await res.json();
        tbody.innerHTML = "";
        data.forEach(c => {
            tbody.innerHTML += `<tr>
                <td>${c.rang}</td><td>${c.numero}</td><td>${c.nom}</td>
                <td>${c.indice}</td><td>${c.confiance}</td>
            </tr>`;
        });
    } catch (e) {
        tbody.innerHTML = "<tr><td colspan='5'>Données indisponibles</td></tr>";
    }
}

function formaterPastilles(texte) {
    const parties = texte.split('/');
    const conv = (chaine) => chaine.split(/[-,\s]+/).map(n => 
        !isNaN(n) ? `<span class="numero-cheval">${n.padStart(2,'0')}</span>` : 
        (n.toUpperCase() === 'X' ? `<span class="numero-cheval" style="background:#d97706">X</span>` : n)
    ).join(" ");
    
    return parties.length > 1 ? conv(parties[0]) + " / " + conv(parties[1]) : conv(texte);
}

async function chargerTicketsPremiumLive() {
    try {
        const reponse = await fetch(`${API_URL}/api/premium/ticket`, {
            method: "GET",
            cache: "no-store",
            headers: { "Accept": "application/json", ...entetesAccesPremium() }
        });

        if (!reponse.ok) {
            throw new Error(`Erreur API analyse : ${reponse.status}`);
        }

        const data = await reponse.json();
        const tickets = data && data.tickets && data.tickets.premium
            ? data.tickets.premium
            : {};

        const quinte = Array.isArray(tickets.quinte)
            ? tickets.quinte.map(Number).filter(Number.isFinite).slice(0, 6).join(" - ")
            : "Non disponible";

        const champ = tickets.champ_reduit && tickets.champ_reduit.format
            ? tickets.champ_reduit.format
            : "Non disponible";

        const quinteElement = document.getElementById("quinte-premium");
        const champElement = document.getElementById("champ-reduit-premium");

        if (quinteElement) {
            quinteElement.innerHTML = formaterPastilles(quinte);
        }

        if (champElement) {
            champElement.innerHTML = formaterPastilles(champ);
        }

        console.log("AZ Turf Pro : Live Premium alimenté par le ticket Premium API.");
    } catch (error) {
        console.error("Erreur chargement ticket Premium live :", error);

        const quinteElement = document.getElementById("quinte-premium");
        const champElement = document.getElementById("champ-reduit-premium");

        if (quinteElement) {
            quinteElement.textContent = "Données Premium indisponibles";
        }

        if (champElement) {
            champElement.textContent = "Données Premium indisponibles";
        }
    }
}
