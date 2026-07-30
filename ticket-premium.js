// =====================================
// ESPACE PREMIUM
// Vérification abonnement + Tickets Premium
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
// VERIFICATION COMPTE PREMIUM
// =====================================


async function verifierPremium(){


const telephone =

localStorage.getItem(
"AZ_TURF_TELEPHONE"
);



const message =

document.getElementById(
"message-fin"
);



if(!telephone){


if(message){

message.innerHTML =

"🔒 Accès réservé aux abonnés Premium.<br>Veuillez vous abonner.";

}


return;

}





try{


const response = await fetch(

API_PREMIUM + "/" + encodeURIComponent(telephone)

);





const data = await response.json();





if(

!response.ok ||

data.statut !== "ACTIF"

){



if(message){

message.innerHTML =

"🔒 Votre abonnement Premium n'est pas actif.";

}


return;

}





// Vérification expiration


if(data.date_fin){


const expiration =

new Date(data.date_fin);



const aujourd_hui =

new Date();



if(expiration < aujourd_hui){


if(message){

message.innerHTML =

"⏳ Votre abonnement Premium a expiré.";

}


return;


}


}





// Accès autorisé

chargerPremium();



}



catch(error){


console.error(

"Erreur vérification Premium",

error

);



if(message){

message.innerHTML =

"❌ Impossible de vérifier votre abonnement.";

}



}



}








// =====================================
// CHARGEMENT DES TICKETS PREMIUM
// =====================================


async function chargerPremium(){


try{


const response = await fetch(
API_ANALYSE
);



if(!response.ok){

throw new Error(
"Erreur API"
);

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







// SELECTION 7 CHEVAUX


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
.map(c=>c.numero)
.join(" - ")
}

</div>

`;

}








// EXPLICATION


const explication =

document.getElementById(
"explication-choix"
);



if(explication){


explication.innerHTML =

classement
.slice(0,7)
.map(c=>`

<p>

🏇 N°${c.numero}

<br>

${c.raison || "Analyse professionnelle en cours"}

</p>

`)
.join("");

}








// TICKETS


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









// COUPLE


const couple =

document.getElementById(
"couple-gagnant-place"
);



if(

couple &&

premium.couple_gagnant_place

){


const affichage =

premium.couple_gagnant_place

.slice(0,3)

.map(c=>c[0]);



couple.innerHTML = `

<div class="ticket-grand">

${affichage.join(" - ")}

</div>

`;

}









// CHAMP REDUIT


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









// ANALYSE PERFORMANCE


const analyse =

document.getElementById(
"analyse-performance"
);



if(analyse){


analyse.innerHTML = `

<h3>📈 Points forts</h3>

<p>
Étude de la forme récente, régularité,
distance et conditions de course.
</p>


<h3>📉 Points de vigilance</h3>

<p>
Analyse des risques liés au parcours
et au niveau d'opposition.
</p>

`;

}









// DERNIERE MINUTE


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








const message =

document.getElementById(
"message-fin"
);



if(message){


message.innerHTML =

premium.message_fin ||

"🍀 Bonne chance ! Jouez avec discipline.";

}



}



catch(error){


console.error(

"Erreur Premium :",

error

);


}

}








function afficherTicket(id,liste){



const zone =

document.getElementById(id);



if(!zone){

return;

}



if(

!liste ||

liste.length===0

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
