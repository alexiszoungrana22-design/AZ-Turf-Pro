// =====================================
// AZ TURF PRO - TICKET PREMIUM
// Version corrigée
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





const classement =
data.classement || [];



const tickets =
data.tickets || {};



const vip =
tickets.vip || {};








// =====================================
// SELECTION 7 CHEVAUX
// =====================================


const selection =
document.getElementById(
"selection-premium"
);



if(selection){


selection.innerHTML = `

<strong>

${
classement
.slice(0,7)
.map(c => c.numero)
.join(" - ")
}

</strong>

`;

}







// =====================================
// EXPLICATION DES CHOIX
// =====================================


const explication =
document.getElementById(
"explication-premium"
);



if(explication){


if(data.explication_premium){


explication.innerHTML =

data.explication_premium
.map(e => `

<p>

🏇 N°${e.numero}

<br>

${e.raison}

</p>

`)
.join("");


}

else{


explication.innerHTML = `

<p>
Les chevaux retenus sont étudiés selon :
</p>

<ul>

<li>Forme récente</li>

<li>Régularité</li>

<li>Distance</li>

<li>Jockey et entourage</li>

<li>Indice AZ</li>

<li>Conditions de course</li>

</ul>

`;

}

}









// =====================================
// TICKETS PREMIUM
// =====================================


afficherListe(
"quinte-premium",
vip.quinte
);



afficherListe(
"quarte-premium",
vip.quarte
);



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


let valeur =
vip.couple_gagnant_place;



if(Array.isArray(valeur)){


if(
typeof valeur[0] === "object"
){


couple.innerHTML =

valeur
.map(c => c.join("-"))
.join(" | ");


}

else{


couple.innerHTML =

valeur.join(" - ");

}


}

else{


couple.innerHTML =

classement
.slice(0,3)
.map(c => c.numero)
.join(" - ");

}


}









// =====================================
// CHAMP REDUIT
// =====================================


const champ =
document.getElementById(
"champ-premium"
);



if(champ){


if(vip.champ_reduit){


champ.innerHTML = `

<strong>

${vip.champ_reduit.format}

</strong>

`;

}

else{


champ.innerHTML =
"Champ réduit en préparation";


}


}









// =====================================
// ANALYSE PERFORMANCE
// =====================================


const analyse =
document.getElementById(
"analyse-premium"
);



if(analyse){


analyse.innerHTML = `

<p>
📈 Bonnes performances :
Analyse de la forme, de la régularité,
de la distance et des conditions favorables.
</p>


<p>
📉 Mauvaises performances :
Recherche des causes possibles :
mauvais parcours, distance,
niveau d'opposition ou circonstances de course.
</p>


<p>
🏇 Course :
${data.course || ""}
</p>


<p>
🏟 Hippodrome :
${data.hippodrome || ""}
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



if(derniere){


const minute =
data.derniere_minute;



if(minute){


derniere.innerHTML = `

<strong>

${minute.selection.join(" - ")}

</strong>


<br><br>

🎯 Joker :
${minute.joker || "-"}


<br><br>

${minute.raison || ""}

`;

}

else{


derniere.innerHTML =

"⚡ La dernière minute sera ajustée avant le départ.";


}


}









// =====================================
// MESSAGE BONNE CHANCE
// =====================================


const message =
document.getElementById(
"message-bonne-chance"
);



if(message){


message.innerHTML = `

🍀 Bonne chance à tous les membres Premium.

<br><br>

Notre analyse repose sur l'étude des performances,
de la forme des chevaux et des conditions de course.

<br><br>

Jouez avec stratégie et responsabilité.

<br><br>

🏇 Que vos chevaux soient à l'arrivée !

`;

}



}





catch(error){


console.error(
"Erreur Ticket Premium AZ :",
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



if(
!liste ||
liste.length === 0
){


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
