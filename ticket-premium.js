// =====================================
// AZ TURF PRO
// TICKET PREMIUM JS
// Correction affichage tickets
// =====================================


const API_ANALYSE =
"https://az-turf-pro.onrender.com/api/analyse";


const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/premium";



document.addEventListener(
"DOMContentLoaded",
verifierPremium
);




// =====================================
// VERIFICATION PREMIUM
// =====================================


async function verifierPremium(){


const telephone =
localStorage.getItem(
"AZ_TURF_TELEPHONE"
);



const message =
document.getElementById(
"message-bonne-chance"
);



if(!telephone){

if(message){

message.innerHTML =
"🔒 Accès réservé aux abonnés Premium.";

}

return;

}



try{


const response =
await fetch(
API_PREMIUM +
"/" +
encodeURIComponent(telephone)
);



const data =
await response.json();



if(
!response.ok ||
data.statut !== "ACTIF"
){

if(message){

message.innerHTML =
"🔒 Abonnement Premium inactif.";

}

return;

}



chargerPremium();



}

catch(error){

console.error(
"Erreur Premium :",
error
);


if(message){

message.innerHTML =
"❌ Impossible de vérifier l'abonnement.";

}


}


}






// =====================================
// CHARGEMENT TICKETS PREMIUM
// =====================================


async function chargerPremium(){


try{


const response =
await fetch(API_ANALYSE);



if(!response.ok){

throw new Error(
"Erreur API analyse"
);

}



const data =
await response.json();



console.log(
"Données reçues :",
data
);





// IMPORTANT : API actuelle
const tickets =

data.tickets?.premium ||

data.tickets?.vip ||

{};



const chevaux =

data.classement ||

data.chevaux ||

[];






// =====================================
// SELECTION 7 CHEVAUX
// =====================================


const selection =
document.getElementById(
"selection-premium"
);



if(selection){

selection.innerHTML = `

<div class="ticket-grand">

${
chevaux
.slice(0,7)
.map(c=>c.numero)
.join(" - ")
}

</div>

`;

}







// =====================================
// EXPLICATION
// =====================================


const explication =
document.getElementById(
"explication-premium"
);



if(explication){

explication.innerHTML =

chevaux
.slice(0,7)
.map(c=>`

<p>

🏇 N°${c.numero}

<br>

${c.raison || "Analyse professionnelle"}

</p>

`)
.join("");

}








// =====================================
// TICKETS
// =====================================


afficherTicket(
"quinte-premium",
tickets.quinte
);



afficherTicket(
"quarte-premium",
tickets.quarte
);



afficherTicket(
"trio-premium",
tickets.trio
);








// =====================================
// COUPLE GAGNANT / PLACE
// =====================================


const couple =
document.getElementById(
"couple-gagnant"
);



if(couple){


if(tickets.couple_gagnant_place){


couple.innerHTML = `

<div class="ticket-grand">

${
tickets.couple_gagnant_place
.map(c=>c.join(" - "))
.join("<br>")
}

</div>

`;

}else{

couple.innerHTML =
"Non disponible";

}


}








// =====================================
// CHAMP REDUIT
// =====================================


const champ =
document.getElementById(
"champ-premium"
);



if(champ){


if(tickets.champ_reduit){


champ.innerHTML = `

<div class="ticket-grand">

${tickets.champ_reduit.format}

</div>

`;

}else{

champ.innerHTML =
"Non disponible";

}


}








// =====================================
// ANALYSE PREMIUM
// =====================================


const analyse =
document.getElementById(
"analyse-premium"
);



if(analyse){


analyse.innerHTML = `

<h3>📈 Points forts</h3>

<p>
Forme, régularité, distance,
terrain et conditions de course.
</p>


<h3>📉 Points de vigilance</h3>

<p>
Étude des risques et de la concurrence.
</p>

`;

}








// =====================================
// DERNIERE MINUTE
// =====================================


const derniere =
document.getElementById(
"derniere-minute-premium"
);



if(derniere){


const dm =
tickets.ticket_derniere_minute;



if(dm){


derniere.innerHTML = `

<div class="ticket-grand">

${dm.format || "-"}

</div>


<br>

Sélection :

${
dm.selection
?
dm.selection.join(" - ")
:
"-"
}


<br>

Joker :

${dm.joker || "-"}

`;

}else{


derniere.innerHTML =
"Non disponible";

}


}








const messageFin =
document.getElementById(
"message-bonne-chance"
);



if(messageFin){


messageFin.innerHTML =

tickets.message_fin ||

"🍀 Bonne chance ! Jouez avec discipline.";

}



}

catch(error){

console.error(
"Erreur chargement Premium :",
error
);

}


}








// =====================================
// AFFICHAGE TICKET
// =====================================


function afficherTicket(id,liste){


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

${
liste.join(" - ")
}

</div>

`;

}
