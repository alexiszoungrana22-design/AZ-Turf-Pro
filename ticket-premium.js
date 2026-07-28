// ticket-premium.js
// AZ Turf Pro Premium
// API calcule - Premium affiche


const API_URL = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerTicketPremium(){

    try{

        const response = await fetch(API_URL);

        const data = await response.json();

        console.log("Données Premium :", data);


        afficherInfosCourse(data);

        afficherFavori(data.favori);


        const tickets = data.tickets || {};


        afficherTicket("ticket-quinte", tickets.quinte);

        afficherTicket("ticket-quarte", tickets.quarte);

        afficherTicket("ticket-trio", tickets.trio);

        afficherTicket("ticket-couple-gagnant", tickets.couple_gagnant);

        afficherCouplePlace(tickets.couple_place);

        afficherChampReduit(
            tickets.vip?.champ_reduit
        );


        afficherClassement(
            data.classement || []
        );


    }catch(error){

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

    <h2>🏇 ${data.course || ""}</h2>

    <p>
    📅 ${data.date || ""}
    </p>

    <p>
    🏟️ ${data.hippodrome || ""}
    </p>

    <p>
    ${data.reunion || ""} - ${data.course_numero || ""}
    </p>

    <p>
    📏 Distance : ${data.distance_course || ""} m
    </p>

    `;

}





function afficherFavori(favori){

    const zone =
    document.getElementById(
        "favori-az"
    );


    if(!zone || !favori) return;


    zone.innerHTML = `

    ⭐ Favori AZ :

    <strong>
    N°${favori.numero}
    </strong>

    - Indice AZ :
    ${favori.indice_az}

    `;

}





function afficherTicket(id,ticket){

    const zone =
    document.getElementById(id);


    if(!zone || !ticket) return;


    zone.innerHTML = ticket.map(numero => `

        <span class="boule-numero">
        ${numero}
        </span>

    `).join("");

}





function afficherCouplePlace(ticket){

    const zone =
    document.getElementById(
        "ticket-couple-place"
    );


    if(!zone || !ticket) return;


    zone.innerHTML = ticket.map(couple => `

        <div>

        ${
            couple.map(numero => `

            <span class="boule-numero">
            ${numero}
            </span>

            `).join("")
        }

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

    <div class="champ-reduit">

    ${champ.format}

    </div>

    `;

}





function afficherClassement(classement){

    const zone =
    document.getElementById(
        "classement-premium"
    );


    if(!zone) return;


    zone.innerHTML = classement.map(c => `

    <div>

    ${c.rang} - N°${c.numero}

    Indice AZ : ${c.indice_az}

    </div>

    `).join("");

}





document.addEventListener(
"DOMContentLoaded",
chargerTicketPremium
);
