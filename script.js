// ===============================
// AZ TURF PRO - AFFICHAGE TICKETS
// Compatible ticket.html + API Premium
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


afficherListe(
"premium-quinte",
premium.quinte
);



afficherListe(
"premium-quarte",
premium.quarte
);



afficherListe(
"premium-trio",
premium.trio
);




// Couplé gagnant/placé Premium

const couple =
document.getElementById(
"couple-gagnant-place"
);



if(
couple
&&
premium.couple_gagnant_place
){


couple.innerHTML =

premium.couple_gagnant_place
.map(
c => c.join("-")
)
.join(" | ");


}




// Champ réduit

const champ =
document.getElementById(
"champ-reduit"
);



if(
champ
&&
premium.champ_reduit
){


champ.textContent =

premium.champ_reduit.format
+
" | Bases : "
+
premium.champ_reduit.bases.join("-")
+
" | Compléments : "
+
premium.champ_reduit.complements.join("-");


}




// Dernière minute

const derniere =
document.getElementById(
"derniere-minute"
);



if(
derniere
&&
premium.ticket_derniere_minute
){


derniere.textContent =

premium.ticket_derniere_minute.format;


}




// Message Premium

const message =
document.getElementById(
"message-fin"
);



if(message){


message.textContent =

premium.message_fin || "";


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



if(
!liste
||
liste.length === 0
){


element.textContent =
"Non disponible";


return;

}




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
