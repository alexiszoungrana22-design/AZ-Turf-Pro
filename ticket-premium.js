// =====================================
// AZ TURF PRO
// TICKET PREMIUM
// AFFICHAGE FINAL
// =====================================

const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";

const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/premium/";


document.addEventListener(
"DOMContentLoaded",
verifierAccesPremium
);


// =====================================
// VERIFICATION ACCES PREMIUM
// (protège le contenu ci-dessous)
// =====================================

async function verifierAccesPremium(){


const telephone =
localStorage.getItem("AZ_TURF_TELEPHONE");

const contenu =
document.getElementById("contenu-premium");

const blocage =
document.getElementById("message-blocage");


if(!telephone){

if(blocage) blocage.style.display = "block";

return;

}


try{

const reponse = await fetch(
API_PREMIUM + encodeURIComponent(telephone)
);

const data = await reponse.json();

if(reponse.ok && data.statut === "ACTIF"){

if(contenu) contenu.style.display = "block";

chargerPremium();

}else{

if(blocage) blocage.style.display = "block";

}

}catch(error){

console.error(
"Erreur vérification Premium :",
error
);

if(blocage) blocage.style.display = "block";

}

}



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
// COUPLE 3 NUMEROS
// =====================================

if(premium.couple_gagnant_place){


let couple =
premium.couple_gagnant_place;



if(Array.isArray(couple)){

// Conserve chaque couple séparément.
// Exemple API : [[3,5],[3,2],[5,2]]
// Affichage : 3-5 | 3-2 | 5-2

couple =
couple
.map(c => {

if(Array.isArray(c)){

return c.join(" - ");

}

return c;

})
.join(" | ");

}

afficherTexte(

"couple-premium",

couple

);


}








// =====================================
// CHAMP REDUIT
// FORMAT : 3-5-X 2-X / 8-1-4-12
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
// DERNIERE MINUTE 6 NUMEROS
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
  
