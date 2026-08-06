// =====================================
// AZ TURF PRO
// TICKET PREMIUM
// AFFICHAGE FINAL + PROTECTION PREMIUM
// =====================================


const API_ANALYSE =
"https://az-turf-pro.onrender.com/api/analyse";


const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/premium";



document.addEventListener(
"DOMContentLoaded",
async () => {

const acces =
await verifierAccesPremium();


if(acces){

chargerPremium();

}

});




// =====================================
// VERIFICATION ACCES PREMIUM
// =====================================

async function verifierAccesPremium(){


const telephone =
localStorage.getItem("telephone");



if(!telephone){


window.location.href =
"abonnement.html";


return false;

}



try{


const response =
await fetch(
`${API_PREMIUM}/${telephone}`
);



if(!response.ok){

throw new Error(
"Erreur vérification Premium"
);

}



const data =
await response.json();



if(
data.statut !== "ACTIF"
){


window.location.href =
"abonnement.html";


return false;

}



return true;



}
catch(error){


console.error(
"Erreur Premium :",
error
);


window.location.href =
"abonnement.html";


return false;


}


}







async function chargerPremium(){


try{


const response =
await fetch(API_ANALYSE);



if(!response.ok){

throw new Error(
"Erreur API"
);

}



const data =
await response.json();



console.log(
"Données Premium :",
data
);




const premium =
data.tickets?.premium || {};



const classement =
data.classement || [];






// =====================================
// SELECTION PREMIUM
// =====================================


afficherListe(

"selection-premium",

classement
.slice(0,7)
.map(c=>c.numero)

);








// =====================================
// EXPLICATION
// =====================================


afficherTexte(

"explication-premium",

classement
.slice(0,7)
.map(c=>`

<p>
🏇 N°${c.numero}

<br>

${c.raison || "Analyse spécialisée en cours"}

</p>

`)
.join("")

);







// =====================================
// TICKETS
// =====================================


afficherTicket(
"quinte-premium",
premium.quinte
);



afficherTicket(
"quarte-premium",
premium.quarte
);



afficherTicket(
"trio-premium",
premium.trio
);






// =====================================
// COUPLE
// =====================================


if(premium.couple_gagnant_place){


let couple =
premium.couple_gagnant_place;



if(Array.isArray(couple)){


couple =
couple
.flat()
.slice(0,3);


}



afficherTicket(

"couple-premium",

couple

);


}








// =====================================
// CHAMP REDUIT
// =====================================


if(premium.champ_reduit){


let champ =
premium.champ_reduit.format ||
"Non disponible";



afficherTexte(

"champ-reduit-premium",

champ

);


}








// =====================================
// DERNIERE MINUTE
// =====================================


if(premium.ticket_derniere_minute){


let derniere =
premium.ticket_derniere_minute.selection || [];



derniere =
derniere.slice(0,6);



afficherTicket(

"derniere-minute-premium",

derniere

);


}








// =====================================
// ANALYSE
// =====================================


afficherTexte(

"analyse-premium",

`

<h3>📈 Points forts</h3>

<p>
Analyse de la forme, régularité,
distance, terrain et expérience.
</p>


<h3>📉 Points de vigilance</h3>

<p>
Évaluation des risques liés à la course.
</p>

`

);








// =====================================
// MESSAGE
// =====================================


afficherTexte(

"message-premium",

premium.message_fin ||

"🍀 Bonne chance ! Jouez avec discipline."

);



}



catch(error){


console.error(

"Erreur Premium :",

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



if(!liste || liste.length===0){


zone.innerHTML =
"Non disponible";


return;

}



zone.innerHTML =
liste.join(" - ");


}









// =====================================
// AFFICHAGE LISTE
// =====================================


function afficherListe(id,liste){


const zone =
document.getElementById(id);



if(zone){


zone.innerHTML =
liste.join(" - ");


}


}









// =====================================
// AFFICHAGE TEXTE
// =====================================


function afficherTexte(id,contenu){


const zone =
document.getElementById(id);



if(zone){


zone.innerHTML =
contenu;


}


}
