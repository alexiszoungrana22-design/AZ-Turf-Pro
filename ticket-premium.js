// ticket-premium.js
// AZ Turf Pro Premium
// L'API calcule - Premium affiche


const API_URL = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerTicketPremium(){

    try{

        const response = await fetch(API_URL);

        const data = await response.json();


        console.log("Données Premium :", data);



        const tickets = data.tickets || {};



        afficherInfosCourse(data);


        afficherFavori(data.favori);



        afficherClassement(
            data.classement || []
        );



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



        afficherCouplePlace(
            tickets.couple_place
        );



        afficherChampReduit(
            tickets.vip?.champ_reduit
        );



        afficherTicketDeuxHeures(
            tickets.ticket_2h_avant
        );



    }
    catch(error){

        console.error(
            "Erreur Premium :",
            error
        );

    }

}





function afficherInfosCourse(data){

    const zone =
    document.getElementById(
        "infos-course"
    );


    if(!zone) return;


    zone.innerHTML = `

    ${data.course || ""}<br>

    ${data.date || ""}<br>

    ${data.hippodrome || ""}<br>

    ${data.reunion || ""} ${data.course_numero || ""}<br>

    Distance : ${data.distance_course || ""} m

    `;

}





function afficherFavori(favori){

    const zone =
    document.getElementById(
        "favori-az"
    );


    if(!zone || !favori) return;


    zone.innerHTML =

    `Favori AZ : N°${favori.numero}`;

}





function afficherClassement(classement){

    const zone =
    document.getElementById(
        "classement-premium"
    );


    if(!zone) return;


    zone.innerHTML = classement.map(c => `

    ${c.rang} - N°${c.numero}
    Indice AZ : ${c.indice_az}<br>

    `).join("");

}







// Quinté - Quarté - Trio - Couplé gagnant

function afficherTicket(id,ticket){

    const zone =
    document.getElementById(id);


    if(!zone || !ticket) return;



    zone.innerHTML = `

    <div class="ticket-grand">

    ${ticket.join(" - ")}

    </div>

    `;

}







// Couplé placé vertical sans numéro 1 2 3

function afficherCouplePlace(ticket){

    const zone =
    document.getElementById(
        "ticket-couple-place"
    );


    if(!zone || !ticket) return;



    zone.innerHTML = ticket.map(couple => `

    <div class="ticket-grand">

    ${couple[0]} / ${couple[1]}

    </div>


    `).join("");

}







function afficherChampReduit(champ){

    const zone =
    document.getElementById(
        "ticket-champ-reduit"
    );


    if(!zone || !champ) return;


    zone.innerHTML = `

    <div class="ticket-grand">

    ${champ.format}

    </div>

    `;

}







function afficherTicketDeuxHeures(ticket){

    const zone =
    document.getElementById(
        "ticket-2h-avant"
    );


    if(!zone) return;



    if(!ticket){

        zone.innerHTML =
        "Ticket 2h avant en préparation";

        return;

    }



    zone.innerHTML = `

    <div class="ticket-grand">

    ${ticket.join(" - ")}

    </div>

    `;

}







document.addEventListener(
"DOMContentLoaded",
chargerTicketPremium
);
