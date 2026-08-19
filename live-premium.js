const API_URL = window.location.origin;

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

    // Affichage des tickets (Données forcées selon tes besoins)
    afficherDonneesVIP({
        quinte: "04 - 09 - 12 - 01 - 07 - 11",
        champReduit: "04 - 09 - X - 01 - X / 12 - 07 - 11 - 03"
    });
    
    document.getElementById("contenu-premium").classList.remove("zone-masquee");
});

async function chargerTableauPartantsLive() {
    const tbody = document.getElementById("all-horses");
    tbody.innerHTML = "<tr><td colspan='5'>Chargement...</td></tr>";
    try {
        const res = await fetch(`${API_URL}/api/partants`);
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

function afficherDonneesVIP(data) {
    document.getElementById("quinte-premium").innerHTML = formaterPastilles(data.quinte);
    document.getElementById("champ-reduit-premium").innerHTML = formaterPastilles(data.champReduit);
}
