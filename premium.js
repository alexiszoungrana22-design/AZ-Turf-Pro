// =====================================
// AZ TURF PRO - PREMIUM.JS
// Nouvel espace Premium indépendant
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
"Données Premium :",
data
);



const classement =
data.classement || [];



const vip =
data.tickets?.vip || {};





// =====================================
// SELECTION 7 CHEVAUX
// =====================================


const selection =
document.getElementById(
"selection-premium"
);



if(selection){


const chevaux =
classement
.slice(0,7)
.map(c => c.numero);



selection.innerHTML = `

<strong>

${chevaux.join(" - ")}

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
🏇 N°${e.numero} :
${e.raison}
</p>

`)
.join("");

}


else{


explication.innerHTML = `

<p>
Analyse basée sur :
</p>

<ul>

<li>Forme récente</li>

<li>Régularité</li>

<li>Distance</li>

<li>Jockey et entourage</li>

<li>Expérience</li>

<li>Indice AZ</li>

</ul>

`;

}

}







// =====================================
// ANALYSE PERFORMANCE
// =====================================


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


analyse.innerHTML =

"Étude des bonnes et mauvaises performances en cours.";

}

}







// =====================================
// TICKETS PREMIUM
// =====================================



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







// =====================================
// COUPLE GAGNANT PLACE
// FORMAT : 3-5-2
// =====================================


const couple =
document.getElementById(
"couple-premium"
);



if(couple){


const base =
vip.couple_gagnant_place ||
[classement[0]?.numero,
 classement[1]?.numero,
 classement[2]?.numero];



couple.innerHTML = `

<strong>

${base.join(" - ")}

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
"Préparation du champ réduit.";

}


}







// =====================================
// DERNIERE MINUTE INDEPENDANTE
// =====================================


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

+ Joker ${minute.joker}

</strong>


<br><br>


${minute.raison || ""}

`;

}


else{


derniere.innerHTML =

"⚡ Dernière minute en préparation avant le départ.";

}


}







// =====================================
// MESSAGE FINAL
// =====================================


const message =
document.getElementById(
"message-premium"
);



if(message){


message.textContent =

vip.message_fin ||

"🍀 Bonne chance aux membres Premium. Jouez avec stratégie et responsabilité. Que vos chevaux soient à l'arrivée !";


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



if(!ticket || ticket.length === 0){


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
