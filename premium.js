// =====================================
// AZ TURF PRO - PREMIUM.JS
// Nouvel espace Premium
// Lecture directe API : tickets.vip
// =====================================


const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/analyse";



document.addEventListener(
"DOMContentLoaded",
chargerPremium
);




async function chargerPremium(){


try{


const response =
await fetch(API_PREMIUM);



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();



console.log(
"Premium AZ :",
data
);



const vip =
data.tickets?.vip || {};




// ===============================
// INFORMATIONS COURSE
// ===============================


const analyse =
document.getElementById(
"analyse-premium"
);



if(analyse){


analyse.innerHTML = `

<strong>${data.course || ""}</strong><br>

${data.hippodrome || ""}<br>

${data.reunion || ""} ${data.course_numero || ""}<br>

${data.discipline || ""}<br>

Distance : ${data.distance_course || ""} m

`;

}




// ===============================
// SELECTION PREMIUM
// ===============================


const selection =
document.getElementById(
"selection-premium"
);



if(selection){


selection.innerHTML = `

<strong>

${(vip.quinte || []).join(" - ")}

</strong>

`;

}





// ===============================
// TICKETS
// ===============================


afficher(
"quinte-premium",
vip.quinte
);



afficher(
"quarte-premium",
vip.quarte
);



afficher(
"trio-premium",
vip.trio
);




// ===============================
// COUPLES
// ===============================


const couples =
document.getElementById(
"couples-premium"
);



if(couples){


couples.innerHTML =

(vip.couple_gagnant_place || [])
.map(
c => c.join("-")
)
.join(" | ");


}





// ===============================
// CHAMP REDUIT
// ===============================


const champ =
document.getElementById(
"champ-premium"
);



if(champ && vip.champ_reduit){


champ.innerHTML = `

<strong>
${vip.champ_reduit.format}
</strong>

<br>

Bases :
${vip.champ_reduit.bases.join("-")}

<br>

Compléments :
${vip.champ_reduit.complements.join("-")}

`;

}




// ===============================
// DERNIERE MINUTE
// ===============================


const derniere =
document.getElementById(
"derniere-premium"
);



if(derniere){


if(vip.ticket_derniere_minute){


derniere.textContent =
vip.ticket_derniere_minute.format;


}

else{


derniere.textContent =
"Préparation avant départ";


}


}



}



catch(error){


console.error(
"Erreur Premium AZ :",
error
);


}



}




function afficher(id,liste){


const zone =
document.getElementById(id);



if(!zone){

return;

}



if(!liste || liste.length === 0){


zone.textContent =
"Non disponible";


return;

}



zone.innerHTML = `

<strong>

${liste.join(" - ")}

</strong>

`;

  }
