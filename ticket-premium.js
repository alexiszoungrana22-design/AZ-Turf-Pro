// ticket-premium.js
// AZ Turf Pro - Affichage Premium
// L'API calcule, Premium affiche


const API_URL = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerTicketPremium() {

    try {

        const response = await fetch(API_URL);

        const data = await response.json();

        console.log("Données Premium :", data);



        const classement = data.classement || [];

        const tickets = data.tickets || {};



        afficherClassement(classement);



        afficherTicket(
            "ticket-quinte",
            tickets.quinte
        );


        afficherTicket(
            "ticket-quarte",
            tickets.quarte
        );


        afficherTicket(
            "ticket-trio",
            tickets.trio
        );


        afficherTicket(
            "ticket-couple-gagnant",
            tickets.couple_gagnant
        );


        afficherCouplesPlace(
            tickets.couple_place
        );


        afficherChampReduit(
            tickets.vip?.champ_reduit
        );



    } catch(error) {


        console.error(
            "Erreur Premium :",
            error
        );


    }

}




function afficherClassement(classement){


    const zone =
    document.getElementById(
        "classement-premium"
    );


    if(!zone) return;



    zone.innerHTML = classement.map(cheval => `

        <div class="cheval-premium">

            ${cheval.rang} - N°${cheval.numero}

            <span>
            Indice AZ : ${cheval.indice_az}
            </span>

        </div>

    `).join("");

}





function afficherTicket(id,ticket){


    const zone =
    document.getElementById(id);


    if(!zone || !ticket) return;



    zone.innerHTML = `

    <div class="ticket-box">

        ${ticket.join(" - ")}

    </div>

    `;

}






function afficherCouplesPlace(ticket){


    const zone =
    document.getElementById(
        "ticket-couple-place"
    );


    if(!zone || !ticket) return;



    zone.innerHTML = `

    <div class="ticket-box">

    ${
        ticket
        .map(couple =>
            couple.join(" - ")
        )
        .join(" / ")
    }

    </div>

    `;

}






function afficherChampReduit(champ){


    const zone =
    document.getElementById(
        "ticket-champ-reduit"
    );


    if(!zone || !champ) return;



    zone.innerHTML = `

    <div class="ticket-box">

        ${champ.format}

    </div>

    `;

}






document.addEventListener(
    "DOMContentLoaded",
    chargerTicketPremium
);
