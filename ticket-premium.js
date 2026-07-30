// =====================================
// ESPACE PREMIUM
// Connexion ticket.html
// =====================================

const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";


document.addEventListener(
"DOMContentLoaded",
chargerPremium
);



async function chargerPremium(){

try{


const response = await fetch(API_URL);


if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();


console.log(
"Données Premium :",
data
);



const premium =
data.tickets?.premium || {};


const classement =
data.classement || [];




// ===============================
// SELECTION PREMIUM 7 CHEVAUX
// ===============================

const selection =
document.getElementById(
"selection-premium"
);



if(selection){

selection.innerHTML = `

<div class="ticket-grand">

${
classement
.slice(0,7)
.map(c => c.numero)
.join(" - ")
}

</div>

`;

}





// ===============================
// EXPLICATION DES CHOIX
// ===============================

const explication =
document.getElementById(
"explication-choix"
);



if(explication){

explication.innerHTML =

classement
.slice(0,7)
.map(c => `

<p>

🏇 N°${c.numero}

<br>

${c.raison || "Analyse professionnelle en cours"}

</p>

`)
.join("");

}





// ===============================
// TICKETS PREMIUM
// ===============================


afficherTicket(
"vip-quinte",
premium.quinte
);



afficherTicket(
"vip-quarte",
premium.quarte
);



afficherTicket(
"vip-trio",
premium.trio
);





// ===============================
// COUPLÉ GAGNANT / PLACÉ
// ===============================


const couple =
document.getElementById(
"couple-gagnant-place"
);



if(
couple &&
premium.couple_gagnant_place
){

const numerosCouple =
premium.couple_gagnant_place
.flat();


couple.innerHTML = `

<div class="ticket-grand">

${numerosCouple.join(" - ")}

</div>

`;

}





// ===============================
// CHAMP RÉDUIT
// ===============================


const champ =
document.getElementById(
"champ-reduit"
);



if(
champ &&
premium.champ_reduit
){

champ.innerHTML = `

<div class="ticket-grand">

${premium.champ_reduit.format}

</div>

`;

}





// ===============================
// ANALYSE PERFORMANCE
// ===============================


const analyse =
document.getElementById(
"analyse-performance"
);



if(analyse){

analyse.innerHTML = `

<h3>📈 Points forts</h3>

<p>
Étude de la forme récente, de la régularité,
du profil du cheval, de la distance et des conditions de course.
</p>


<h3>📉 Points de vigilance</h3>

<p>
Analyse des risques liés au parcours,
à la distance et au niveau d'opposition.
</p>

`;

}





// ===============================
// DERNIÈRE MINUTE
// ===============================


const derniere =
document.getElementById(
"derniere-minute"
);



if(
derniere &&
premium.ticket_derniere_minute
){

derniere.innerHTML = `

<div class="ticket-grand">

${premium.ticket_derniere_minute.format}

</div>

<br>

Sélection :
${premium.ticket_derniere_minute.selection.join(" - ")}

<br>

Joker :
N°${premium.ticket_derniere_minute.joker}

`;

}





// ===============================
// MESSAGE FINAL
// ===============================


const message =
document.getElementById(
"message-fin"
);



if(message){

message.innerHTML =

premium.message_fin ||

"🍀 Bonne chance ! Jouez avec discipline et responsabilité.";

}





}

catch(error){

console.error(
"Erreur Premium :",
error
);

}

}







function afficherTicket(id, liste){


const zone =
document.getElementById(id);



if(!zone){

return;

}



if(
!liste ||
liste.length === 0
){

zone.innerHTML =
"Non disponible";

return;

}



zone.innerHTML = `

<div class="ticket-grand">

${liste.join(" - ")}

</div>

`;

}
