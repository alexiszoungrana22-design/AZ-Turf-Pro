// =====================================
// AZ TURF PRO
// TICKET PREMIUM
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
// SELECTION 7 CHEVAUX
// =====================================

afficherTexte(
"selection-premium",
`

<div class="ticket-grand">

${classement
.slice(0,7)
.map(c=>c.numero)
.join(" - ")}

</div>

`
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

${c.raison || 
"Analyse spécialisée en cours"}

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


if(
premium.couple_gagnant_place
){

afficherTexte(

"couple-premium",

`

<div class="ticket-grand">

${
premium.couple_gagnant_place
.map(c=>c.join(" - "))
.join("<br>")
}

</div>

`

);

}





// =====================================
// CHAMP REDUIT
// =====================================


if(
premium.champ_reduit
){

afficherTexte(

"champ-reduit-premium",

`

<div class="ticket-grand">

${premium.champ_reduit.format}

</div>

`

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


if(
premium.ticket_derniere_minute
){

afficherTexte(

"derniere-minute-premium",

`

<div class="ticket-grand">

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



zone.innerHTML = `

<div class="ticket-grand">

${liste.join(" - ")}

</div>

`;

}





function afficherTexte(id,contenu){


const zone =
document.getElementById(id);


if(zone){

zone.innerHTML =
contenu;

}

  }
