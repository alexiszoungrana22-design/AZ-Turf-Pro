// =====================================
// AZ TURF PRO - TICKET PREMIUM
// Compatible ticket-premium.html
// Lecture API : tickets.vip
// =====================================


const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";



document.addEventListener(
"DOMContentLoaded",
chargerTicketPremium
);




async function chargerTicketPremium(){


try{


const response =
await fetch(API_URL);



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();



console.log(
"Données Premium :",
data
);



const vip =
data.tickets?.vip || {};




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

${
(vip.quinte || [])
.join(" - ")

}

</strong>

`;

}




// ===============================
// QUINTE PREMIUM
// ===============================


afficherListe(
"quinte-premium",
vip.quinte
);




// ===============================
// QUARTE PREMIUM
// ===============================


afficherListe(
"quarte-premium",
vip.quarte
);




// ===============================
// TRIO PREMIUM
// ===============================


afficherListe(
"trio-premium",
vip.trio
);




// ===============================
// COUPLES GAGNANT / PLACE
// ===============================


const couple =
document.getElementById(
"couple-gagnant"
);



if(couple && vip.couple_gagnant_place){


couple.innerHTML =

vip.couple_gagnant_place
.map(
c => c.join("-")
)
.join(" | ");


}




// ===============================
// COUPLE PLACE
// ===============================


const couplePlace =
document.getElementById(
"couple-place"
);



if(couplePlace){


couplePlace.innerHTML =

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
// ANALYSE PREMIUM
// ===============================


const analyse =
document.getElementById(
"analyse-premium"
);



if(analyse){


analyse.innerHTML = `

<p>
Course :
${data.course || ""}
</p>

<p>
Hippodrome :
${data.hippodrome || ""}
</p>

<p>
Distance :
${data.distance_course || ""} m
</p>

<p>
Discipline :
${data.discipline || ""}
</p>

`;

}




}

catch(error){


console.error(
"Erreur Premium AZ Turf :",
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
