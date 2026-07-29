// =====================================
// AZ TURF PRO - PREMIUM.JS
// Espace Premium indépendant
// =====================================


const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";



document.addEventListener(
"DOMContentLoaded",
chargerPremium
);





async function chargerPremium(){


try{


const response =
await fetch(API_URL);



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();



console.log(
"Données Premium AZ :",
data
);





const classement =
data.classement || [];



const tickets =
data.tickets || {};



const vip =
tickets.vip || {};







// ===============================
// SELECTION 7 CHEVAUX
// ===============================


const selection =
document.getElementById(
"selection-premium"
);



if(selection){


const chevaux =
classement
.slice(0,7)
.map(c => `N°${c.numero}`);



selection.innerHTML = `

<strong>

${chevaux.join(" - ")}

</strong>

`;

}









// ===============================
// EXPLICATION DES CHOIX
// ===============================


const explication =
document.getElementById(
"explication-premium"
);



if(explication){


if(data.explication_premium){


explication.innerHTML =

data.explication_premium
.map(item => `

<div class="analyse-cheval">

<h3>
🏇 N°${item.numero}
</h3>

<p>
${item.raison}
</p>

</div>

`)
.join("");


}

else{


explication.innerHTML = `

<p>
Analyse des chevaux retenus selon :
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









// ===============================
// BONNES / MAUVAISES PERFORMANCES
// ===============================


const analyse =
document.getElementById(
"analyse-performance"
);



if(analyse){


if(data.analyse_performance){


analyse.innerHTML =
data.analyse_performance;


}

else{


analyse.innerHTML = `

<p>
📈 Étude des bonnes performances :
Les réussites sont analysées selon les conditions favorables,
la distance, la forme et l'adaptation au parcours.
</p>


<p>
📉 Étude des mauvaises performances :
Les échecs sont analysés selon les causes possibles :
mauvais parcours, distance, niveau d'opposition ou circonstances de course.
</p>

`;

}


}









// ===============================
// TICKETS PREMIUM
// ===============================


afficherTicket(
"quinte-premium",
vip.quinte
);



afficherTicket(
"quarte-premium",
vip.quarte
);



afficherTicket(
"trio-premium",
vip.trio
);









// ===============================
// COUPLE GAGNANT PLACE
// FORMAT 3-5-2
// ===============================


const couple =
document.getElementById(
"couple-premium"
);



if(couple){


let base =
vip.couple_gagnant_place;



if(
Array.isArray(base)
&& base.length > 0
){


couple.innerHTML = `

<strong>

${base.join(" - ")}

</strong>

`;

}

else{


const trois =
classement
.slice(0,3)
.map(c => c.numero);



couple.innerHTML = `

<strong>

${trois.join(" - ")}

</strong>

`;

}


}









// ===============================
// CHAMP REDUIT
// ===============================


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









// ===============================
// DERNIERE MINUTE
// ===============================


const derniere =
document.getElementById(
"derniere-premium"
);



if(derniere){



const minute =
data.derniere_minute;



if(minute){


derniere.innerHTML = `

<strong>

${minute.selection.join(" - ")}

</strong>


<br>

🎯 Joker :
${minute.joker || "-"}


<br><br>


${minute.raison || ""}

`;

}


else{


derniere.innerHTML =

"⚡ Sélection dernière minute préparée avant le départ.";


}


}









// ===============================
// MESSAGE FINAL
// ===============================


const message =
document.getElementById(
"message-premium"
);



if(message){


message.textContent =

vip.message_fin ||

"🍀 Bonne chance aux membres Premium. Analysez vos jeux avec discipline et responsabilité.";

}



}



catch(error){


console.error(
"Erreur Premium AZ :",
error
);


}



}









function afficherTicket(id,ticket){


const zone =
document.getElementById(id);



if(!zone){

return;

}



if(
!ticket ||
ticket.length === 0
){


zone.textContent =
"Non disponible";


return;

}



zone.innerHTML = `

<strong>

${ticket.join(" - ")}

</strong>

`;

}
