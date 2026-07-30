// ===============================
// AZ TURF PRO - AFFICHAGE TICKETS
// Compatible ticket.html + JSON API
// ===============================


const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";



document.addEventListener(
"DOMContentLoaded",
chargerTickets
);




async function chargerTickets(){


try{


const response = await fetch(API_URL);



if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();



console.log(
"JSON AZ Turf :",
data
);



const tickets =
data.tickets || {};



const gratuit =
tickets.gratuit || {};



const premium =
tickets.premium || {};




// ===============================
// GRATUIT
// ===============================


afficherListe(
"quinte",
gratuit.quinte
);



afficherListe(
"couple-place",
gratuit.couple_place
);




// ===============================
// PREMIUM
// ===============================

if(premiumActif){

afficherListe("vip-quinte", vip.quinte);

afficherListe("vip-quarte", vip.quarte);

afficherListe("vip-trio", vip.trio);

const couple =
document.getElementById("couple-gagnant-place");

if(couple && vip.couple_gagnant_place){

couple.textContent =
vip.couple_gagnant_place
.map(c => c.join("-"))
.join(" | ");

}

const champ =
document.getElementById("champ-reduit");

if(champ && vip.champ_reduit){

champ.textContent =
vip.champ_reduit.format +
" | Bases : " +
vip.champ_reduit.bases.join("-") +
" | Compléments : " +
vip.champ_reduit.complements.join("-");

}

const derniere =
document.getElementById("derniere-minute");

if(derniere && vip.ticket_derniere_minute){

derniere.textContent =
vip.ticket_derniere_minute.format;

}

const message =
document.getElementById("message-fin");

if(message){

message.textContent =
vip.message_fin || "";

}

}else{

premium.quinte
premium.quarte
premium.trio
premium.couple_gagnant_place
premium.champ_reduit
premium.ticket_derniere_minute
premium.message_fin

const el=document.getElementById(id);

if(el){

el.textContent =
"🔒 Réservé aux membres Premium";

}

});

const message =
document.getElementById("message-fin");

if(message){

message.textContent =
"Activez votre abonnement Premium pour accéder à ces sélections.";

}

}



catch(error){


console.error(
"Erreur affichage tickets :",
error
);


}



}





function afficherListe(id, liste){


const element =
document.getElementById(id);



if(!element){

return;

}



if(!liste || liste.length === 0){


element.textContent =
"Non disponible";


return;

}




// Gestion des couples sous forme tableau

if(Array.isArray(liste[0])){


element.textContent =

liste
.map(
c => c.join("-")
)
.join(" | ");


}

else{


element.textContent =

liste.join(" - ");


}



}
