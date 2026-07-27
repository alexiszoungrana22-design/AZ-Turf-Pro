const API = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerTicket(){


try{


const response =
await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();



const tickets =
data.tickets || {};







// QUINTE


const quinte =
document.getElementById("quinte-ticket");



if(quinte){


quinte.innerHTML = `


<div class="ticket-result">


🏆 Sélection Quinté


<br><br>


<strong>

${
tickets.quinte
?
tickets.quinte.join(" - ")
:
"-"

}

</strong>


</div>


`;

}









// TRIO


const trio =
document.getElementById("trio-ticket");



if(trio){


trio.innerHTML = `


<div class="ticket-result">


🥉 Sélection Tiercé


<br><br>


<strong>

${
tickets.trio
?
tickets.trio.join(" - ")
:
"-"

}

</strong>


</div>


`;

}









// CHAMP REDUIT


const champ =
document.getElementById("champ-ticket");



if(champ){


if(tickets.champ_reduit){


const bases =
tickets.champ_reduit.bases || [];



const complements =
tickets.champ_reduit.complements || [];




champ.innerHTML = `


<div class="ticket-result">


<p>

🔒 Bases :

<br>


<strong>

${bases.join(" - ") || "-"}

</strong>

</p>





<p>

➕

Compléments :

<br>


<strong>

${complements.join(" - ") || "-"}

</strong>

</p>



</div>


`;



}

else{


champ.innerHTML =
"Champ réduit non disponible";


}



}







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
