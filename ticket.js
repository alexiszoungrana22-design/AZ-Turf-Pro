const API = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerTicket(){


try{


const response = await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();



const chevaux =
data.classement ||
data.chevaux ||
[];



const tickets =
data.tickets || {};








// Fonction affichage ticket

function afficherSelection(element, liste){


const zone =
document.getElementById(element);



if(!zone){

return;

}



if(liste && liste.length){


zone.innerHTML = `


<div class="ticket-result">

<strong>

${liste.join(" - ")}

</strong>


</div>


`;

}


else{


zone.innerHTML =
"Indisponible";


}


}








// QUINTE 8 CHEVAUX GRATUIT


afficherSelection(

"quinte-ticket",

tickets.quinte ||
chevaux.slice(0,8)
.map(c=>c.numero)

);









// QUARTE 5 CHEVAUX GRATUIT


afficherSelection(

"quarte-ticket",

tickets.quarte ||
chevaux.slice(0,5)
.map(c=>c.numero)

);









// TIERCE 4 CHEVAUX GRATUIT


afficherSelection(

"trio-ticket",

tickets.trio ||
chevaux.slice(0,4)
.map(c=>c.numero)

);









// 2 SUR 4 4 CHEVAUX GRATUIT


afficherSelection(

"deux-quatre-ticket",

tickets.deux_sur_quatre ||
chevaux.slice(0,4)
.map(c=>c.numero)

);







}



catch(error){


console.log(
"Erreur ticket :",
error
);


}



}





document.addEventListener(

"DOMContentLoaded",

chargerTicket

);
