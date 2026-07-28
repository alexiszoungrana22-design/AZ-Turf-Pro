// ticket-premium.js
// AZ Turf Pro - Affichage Ticket Premium
// L'API calcule, la page Premium affiche

async function chargerTicketPremium() {

    try {

        const reponse = await fetch("https://az-turf-pro.onrender.com/api/analyse");

        const data = await reponse.json();

        console.log("Données API Premium :", data);


        // Classement général fourni par l'API
        const classement = data.classement || [];


        // Tickets déjà générés par l'API
        const tickets = data.tickets || {};

        const quinte = tickets.quinte || [];
        const quarte = tickets.quarte || [];
        const trio = tickets.trio || [];
        const coupleGagnant = tickets.couple_gagnant || [];
        const couplePlace = tickets.couple_place || [];


        afficherClassement(classement);

        afficherTicket("ticket-quinte", quinte);
        afficherTicket("ticket-quarte", quarte);
        afficherTicket("ticket-trio", trio);
        afficherTicket("ticket-couple-gagnant", coupleGagnant);
        afficherTicket("ticket-couple-place", couplePlace);


    } catch (erreur) {

        console.error("Erreur chargement ticket premium :", erreur);

        const zone = document.getElementById("premium-resultat");

        if (zone) {
            zone.innerHTML = `
                <p class="erreur">
                Impossible de charger le ticket Premium.
                </p>
            `;
        }
    }
}


// Affichage classement AZ

function afficherClassement(classement) {

    const zone = document.getElementById("classement-premium");

    if (!zone) return;


    zone.innerHTML = "";


    classement.forEach(cheval => {

        zone.innerHTML += `
            <div class="cheval-premium">

                <span class="rang">
                ${cheval.rang}
                </span>

                <span>
                N° ${cheval.numero}
                </span>

                <span>
                Indice AZ : ${cheval.indice_az || cheval.score || "-"}
                </span>

                <span>
                ${cheval.type || "Cheval sélectionné"}
                </span>

            </div>
        `;

    });

}


// Affichage tickets

function afficherTicket(id, ticket) {

    const zone = document.getElementById(id);

    if (!zone) return;


    if (!ticket.length) {

        zone.innerHTML = `
            <p>Aucun ticket disponible</p>
        `;

        return;
    }


    zone.innerHTML = `

        <div class="ticket-box">

            ${ticket.map(numero => `

                <span class="numero-cheval">
                ${numero}
                </span>

            `).join("")}

        </div>

    `;

}


// Lancement automatique

document.addEventListener(
    "DOMContentLoaded",
    chargerTicketPremium
);
