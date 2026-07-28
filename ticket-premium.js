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


    }
    catch(error){

        console.error(
            "Erreur chargement Premium :",
            error
        );

    }

}





function afficherInfosCourse(data){

    const zone =
    document.getElementById("infos-course");


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
    document.getElementById("favori-az");


    if(!zone || !favori) return;


    zone.innerHTML = `

    Favori AZ : N°${favori.numero}

    `;

}





function afficherClassement(classement){

    const zone =
    document.getElementById("classement-premium");


    if(!zone) return;


    zone.innerHTML = classement.map(c => `

    ${c.rang} - N°${c.numero}
    Indice AZ : ${c.indice_az}<br>

    `).join("");

}






function afficherTicket(id,ticket){

    const zone =
    document.getElementById(id);


    if(!zone || !ticket) return;


    zone.innerHTML =
    ticket.join(" - ");

}







function afficherCouplePlace(ticket){

    const zone =
    document.getElementById(
        "ticket-couple-place"
    );


    if(!zone || !ticket) return;


    zone.innerHTML = ticket.map((couple,index)=>`

    ${index + 1} - ${couple[0]} / ${couple[1]}<br>

    `).join("");

}







function afficherChampReduit(champ){

    const zone =
    document.getElementById(
        "ticket-champ-reduit"
    );


    if(!zone || !champ) return;


    zone.innerHTML =
    champ.format;

}







document.addEventListener(
"DOMContentLoaded",
chargerTicketPremium
);
