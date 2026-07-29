// =====================================
// AZ TURF PRO - TICKET PREMIUM
// Compatible avec ticket-premium.html
// Lecture API : tickets.vip
// =====================================

const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";
console.log("TICKET PREMIUM JS CHARGE");

document.addEventListener(
"DOMContentLoaded",
chargerTicketPremium
);



async function chargerTicketPremium(){

try{

const response = await fetch(API_URL);

if(!response.ok){
throw new Error("Erreur API");
}


const data = await response.json();

console.log("Données Premium :", data);



const vip = data.tickets?.vip || {};

const classement = data.classement || [];




// =====================================
// SELECTION PREMIUM 7 CHEVAUX
// =====================================

const selection =
document.getElementById("selection-premium");


if(selection){

selection.innerHTML = `

<strong>
${classement
.slice(0,7)
.map(c => c.numero)
.join(" - ")}
</strong>

<br><br>

${classement
.slice(0,7)
.map(c => 
`
<p>
🏇 N°${c.numero} :
${c.raison}
</p>
`
)
.join("")}

`;

}




// =====================================
// QUINTE PREMIUM
// =====================================

afficherListe(
"quinte-premium",
vip.quinte
);



// =====================================
// QUARTE PREMIUM
// =====================================

afficherListe(
"quarte-premium",
vip.quarte
);



// =====================================
// TRIO PREMIUM
// =====================================

afficherListe(
"trio-premium",
vip.trio
);




// =====================================
// COUPLE GAGNANT / PLACE
// FORMAT 3-5-2
// =====================================

const couple =
document.getElementById(
"couple-gagnant"
);


if(couple){

couple.innerHTML = `

<strong>

${classement
.slice(0,3)
.map(c=>c.numero)
.join(" - ")}

</strong>

`;

}



// =====================================
// CHAMP REDUIT
// =====================================

const champ =
document.getElementById(
"champ-premium"
);



if(champ && vip.champ_reduit){


champ.innerHTML = `

<strong>
${vip.champ_reduit.format}
</strong>

<br><br>

Bases :
${vip.champ_reduit.bases.join("-")}

<br>

Compléments :
${vip.champ_reduit.complements.join("-")}

`;

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

<p>
🏇 Course :
${data.course || ""}
</p>


<p>
🏟 Hippodrome :
${data.hippodrome || ""}
</p>


<p>
📏 Distance :
${data.distance_course || ""} m
</p>


<h3>🧠 Explication des choix</h3>

${classement
.slice(0,7)
.map(c=>`

<p>
N°${c.numero} :
${c.raison}
</p>

`)
.join("")}


<h3>📈 Analyse performances</h3>

<p>
Les bonnes performances sont étudiées selon la forme,
la régularité, la distance, le profil du cheval et les conditions de course.
</p>


<p>
Les mauvaises performances sont analysées pour rechercher
les causes possibles : mauvais parcours, distance,
niveau d'opposition ou circonstances défavorables.
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


if(derniere && vip.ticket_derniere_minute){


derniere.innerHTML = `

<strong>

${vip.ticket_derniere_minute.format}

</strong>


<br><br>

Sélection :
${vip.ticket_derniere_minute.selection.join(" - ")}


<br>

Joker :
N°${vip.ticket_derniere_minute.joker}

`;

}



// =====================================
// MESSAGE FIN
// =====================================

const message =
document.getElementById(
"message-bonne-chance"
);


if(message){


message.innerHTML =

vip.message_fin ||

"🍀 Bonne chance à tous les membres Premium !";


}



}

catch(error){

console.error(
"Erreur Ticket Premium :",
error
);

}

}





function afficherListe(id,liste){


const zone =
document.getElementById(id);


if(!zone){
return;
}


if(!liste || liste.length === 0){

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
