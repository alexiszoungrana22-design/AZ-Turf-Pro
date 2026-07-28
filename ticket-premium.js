// ticket-premium.js
// AZ Turf Pro Premium

const API_URL = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerTicketPremium() {

    try {

        const response = await fetch(API_URL);
        const data = await response.json();

        console.log("API Premium :", data);


        const classement = data.classement || [];
        const tickets = data.tickets || {};


        afficherClassement(classement);


        afficherTicket(
            "ticket-quinte",
            tickets.quinte,
            classement
        );


        afficherTicket(
            "ticket-quarte",
            tickets.quarte,
            classement
        );


        afficherTicket(
            "ticket-trio",
            tickets.trio,
            classement
        );


        afficherTicket(
            "ticket-couple-gagnant",
            tickets.couple_gagnant,
            classement
        );


        afficherCouplesPlace(
            tickets.couple_place,
            classement
        );


    } catch(error) {

        console.error(error);

        document.body.innerHTML +=
        "<p>Erreur chargement Premium</p>";

    }

}



function nomCheval(numero, classement){

    const cheval = classement.find(
        c => c.numero === numero
    );

    return cheval 
        ? `N°${numero} - ${cheval.nom}`
        : `N°${numero}`;

}



function afficherClassement(classement){

    const zone = document.getElementById(
        "classement-premium"
    );

    if(!zone) return;


    zone.innerHTML = classement.map(c => `

        <div class="cheval-premium">

            <b>${c.rang}e</b>
            ${c.nom}

            <span>
            Indice AZ : ${c.indice_az}
            </span>

        </div>

    `).join("");

}




function afficherTicket(id,ticket,classement){

    const zone = document.getElementById(id);

    if(!zone || !ticket) return;


    zone.innerHTML = `

    <div class="ticket-box">

    ${
        ticket.map(numero => 
        `
        <div class="numero-cheval">
        ${nomCheval(numero,classement)}
        </div>
        `
        ).join("")
    }

    </div>

    `;

}



function afficherCouplesPlace(ticket,classement){

    const zone =
    document.getElementById(
        "ticket-couple-place"
    );


    if(!zone || !ticket) return;


    zone.innerHTML = ticket.map(couple => `

        <div class="ticket-box">

        ${couple.map(numero =>
            nomCheval(numero,classement)
        ).join(" - ")}

        </div>

    `).join("");

}




document.addEventListener(
"DOMContentLoaded",
chargerTicketPremium
);
