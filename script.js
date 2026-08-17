// ===============================
// AZ TURF PRO - AFFICHAGE TICKETS
// Compatible ticket.html + API Premium
// ===============================

const API_URL = "https://az-turf-pro.onrender.com/api/analyse";

document.addEventListener("DOMContentLoaded", chargerTickets);

async function chargerTickets() {
    // 1. Indicateur visuel pendant le chargement
    indiquerChargement();

    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`Erreur API (${response.status})`);
        }

        const data = await response.json();
        console.log("JSON AZ Turf :", data);

        const tickets = data.tickets || {};
        const gratuit = tickets.gratuit || {};
        const premium = tickets.premium || {};

        // ===============================
        // TICKETS GRATUITS
        // ===============================
        afficherListe("quinte", gratuit.quinte);
        afficherListe("couple-place", gratuit.couple_place);

        // ===============================
        // TICKETS PREMIUM
        // ===============================
        afficherListe("premium-quinte", premium.quinte);
        afficherListe("premium-quarte", premium.quarte);
        afficherListe("premium-trio", premium.trio);

        // Couplé gagnant / placé Premium
        const couple = document.getElementById("couple-gagnant-place");
        if (couple) {
            if (Array.isArray(premium.couple_gagnant_place) && premium.couple_gagnant_place.length > 0) {
                couple.textContent = premium.couple_gagnant_place
                    .map(c => (Array.isArray(c) ? c.join("-") : c))
                    .join(" | ");
            } else {
                couple.textContent = "Non disponible";
            }
        }

        // Champ réduit
        const champ = document.getElementById("champ-reduit");
        if (champ) {
            if (premium.champ_reduit) {
                const cr = premium.champ_reduit;
                const format = cr.format || "Champ Réduit";
                const bases = Array.isArray(cr.bases) ? cr.bases.join("-") : "-";
                const complements = Array.isArray(cr.complements) ? cr.complements.join("-") : "-";
                champ.textContent = `${format} | Bases : ${bases} | Compléments : ${complements}`;
            } else {
                champ.textContent = "Non disponible";
            }
        }

        // Dernière minute
        const derniere = document.getElementById("derniere-minute");
        if (derniere) {
            if (premium.ticket_derniere_minute) {
                const dm = premium.ticket_derniere_minute;
                derniere.textContent = typeof dm === "object" ? (dm.format || dm.selection?.join(" - ") || "-") : String(dm);
            } else {
                derniere.textContent = "Non disponible";
            }
        }

        // Message Premium / Fin
        const message = document.getElementById("message-fin");
        if (message) {
            message.textContent = premium.message_fin || "";
        }

    } catch (error) {
        console.error("Erreur affichage tickets :", error);
        afficherErreur();
    }
}

// Helper pour afficher une liste d'éléments (chiffres ou sous-tableaux)
function afficherListe(id, liste) {
    const element = document.getElementById(id);
    if (!element) return;

    if (!liste || !Array.isArray(liste) || liste.length === 0) {
        element.textContent = "Non disponible";
        return;
    }

    if (Array.isArray(liste[0])) {
        element.textContent = liste.map(c => (Array.isArray(c) ? c.join("-") : c)).join(" | ");
    } else {
        element.textContent = liste.join(" - ");
    }
}

// Affiche un état "Chargement..." sur tous les champs concernés
function indiquerChargement() {
    const ids = ["quinte", "couple-place", "premium-quinte", "premium-quarte", "premium-trio", "couple-gagnant-place", "champ-reduit", "derniere-minute"];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = "Chargement...";
    });
}

// Affiche un message explicite en cas d'échec de la connexion
function afficherErreur() {
    const ids = ["quinte", "couple-place", "premium-quinte", "premium-quarte", "premium-trio", "couple-gagnant-place", "champ-reduit", "derniere-minute"];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = "Indisponible (Erreur serveur)";
    });
}
// Déclaration du graphique Chart.js
let radarChartInstance = null;

function ouvrirFicheCheval(cheval) {
    document.getElementById("modal-nom-cheval").innerText = `${cheval.numero} - ${cheval.nom}`;
    
    // 1. Affichage des Badges Intelligents
    const badgesContainer = document.getElementById("container-badges");
    badgesContainer.innerHTML = "";
    
    if (cheval.badges && cheval.badges.length > 0) {
        cheval.badges.forEach(b => {
            const span = document.createElement("span");
            span.className = "badge-item";
            span.style.backgroundColor = b.couleur;
            span.innerText = b.libelle;
            badgesContainer.appendChild(span);
        });
    }

    // 2. Traçage du Radar de Performance (Chart.js)
    const ctx = document.getElementById('radarChart').getContext('2d');
    
    if (radarChartInstance) {
        radarChartInstance.destroy();
    }

    radarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Forme', 'Distance', 'Jockey', 'Classe/Gains', 'Fraîcheur'],
            datasets: [{
                label: 'Indice AZ Expert',
                data: [
                    cheval.radar.forme, 
                    cheval.radar.distance, 
                    cheval.radar.jockey, 
                    cheval.radar.classe, 
                    cheval.radar.fraicheur
                ],
                backgroundColor: 'rgba(0, 123, 255, 0.2)',
                borderColor: '#007bff',
                pointBackgroundColor: '#007bff'
            }]
        },
        options: {
            scales: {
                r: { min: 0, max: 100, ticks: { display: false } }
            }
        }
    });
}
