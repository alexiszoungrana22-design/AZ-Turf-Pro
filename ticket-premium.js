// =====================================
// AZ TURF PRO
// TICKET PREMIUM
// VERSION OPTIMISEE
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






// =====================================
// SELECTION PREMIUM
// =====================================


afficherNumeros(

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
// COUPLE UNIQUE 3 NUMEROS
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



afficherNumeros(

"couple-premium",

couple

);



}








// =====================================
// CHAMP REDUIT
// =====================================


if(premium.champ_reduit){


afficherTexte(

"champ-reduit-premium",

premium.champ_reduit.format

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
// DERNIERE MINUTE
// =====================================


if(premium.ticket_derniere_minute){


afficherTexte(

"derniere-minute-premium",

`

<div>

${premium.ticket_derniere_minute.format}

</div>


<p>
Sélection :
${premium.ticket_derniere_minute.selection.join(" - ")}
</p>


<p>
Joker :
N°${premium.ticket_derniere_minute.joker}
</p>

`

);


}







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
// AFFICHAGE NUMEROS
// =====================================


function afficherNumeros(id,numeros){


const zone =
document.getElementById(id);



if(!zone){

return;

}



if(!numeros || numeros.length===0){

zone.innerHTML =
"Non disponible";

return;

}



zone.innerHTML =

numeros
.map(n=>`

<span>
${n}
</span>

`)
.join("");

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

liste
.map(n=>`

<span>
${n}
</span>

`)
.join("");

}








// =====================================
// TEXTE
// =====================================


function afficherTexte(id,contenu){


const zone =
document.getElementById(id);



if(zone){

zone.innerHTML =
contenu;

}


}
