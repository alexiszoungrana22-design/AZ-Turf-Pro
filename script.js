// ===============================
// AZ TURF PRO - SCRIPT TICKETS
// ===============================


const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";



document.addEventListener(
"DOMContentLoaded",
chargerTickets
);




async function chargerTickets(){


try{


const reponse =
await fetch(API_URL);



const data =
await reponse.json();



console.log(
"Analyse AZ :",
data
);



afficherTickets(
data.tickets || {}
);



}

catch(error){


console.error(
"Erreur AZ Turf Pro :",
error
);


}



}




function afficherTickets(tickets){


const gratuit =
tickets.gratuit || {};


const vip =
tickets.vip || {};




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
"vip-quinte",
vip.quinte
);



afficherListe(
"vip-quarte",
vip.quarte
);



afficherListe(
"vip-trio",
vip.trio
);



afficherCouples(
"couple-gagnant-place",
vip.couple_gagnant_place
);




// Champ réduit

const champ =
document.getElementById(
"champ-reduit"
);



if(champ && vip.champ_reduit){


champ.textContent =

vip.champ_reduit.format
+
" | Bases : "
+
vip.champ_reduit.bases.join("-")
+
" | Compléments : "
+
vip.champ_reduit.complements.join("-");


}




// Dernière minute

const derniere =
document.getElementById(
"derniere-minute"
);



if(derniere && vip.ticket_derniere_minute){


derniere.textContent =

vip.ticket_derniere_minute.format;


}




// Message final

const message =
document.getElementById(
"message-fin"
);



if(message){


message.textContent =

vip.message_fin || "";


}



}





function afficherListe(id, liste){


const element =
document.getElementById(id);



if(!element){

return;

}



if(!liste || liste.length===0){


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





function afficherCouples(id, couples){


const element =
document.getElementById(id);



if(!element){

return;

}



if(!couples || couples.length===0){


element.textContent =
"Non disponible";


return;

}



element.textContent =

couples
.map(
c => c.join("-")
)
.join(" | ");



}
