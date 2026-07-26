const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerVIP(){


try{


const response =
await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();




const chevaux =
data.classement ||
data.chevaux ||
[];







// BASE DU JOUR


const baseBox =
document.getElementById("base-vip");



if(baseBox && chevaux.length){


baseBox.innerHTML = `

<div class="vip-choice">

⭐ Base 1 :

<strong>

N°${chevaux[0].numero}
-
${chevaux[0].nom || ""}

</strong>

</div>


<div class="vip-choice">

⭐ Base 2 :

<strong>

N°${chevaux[1]?.numero || "-"}
-
${chevaux[1]?.nom || ""}

</strong>

</div>

`;

}








// CHAMP REDUIT


if(data.tickets &&
data.tickets.champ_reduit){



const champ =
data.tickets.champ_reduit;



const bases =
champ.bases || [];



const complements =
champ.complements || [];





const vipBase =
document.getElementById("vip-base");



if(vipBase){

vipBase.textContent =
bases.join(" - ") || "-";

}






const systeme =
document.getElementById("vip-systeme");



if(systeme){

systeme.textContent =
"Bases principales + compléments";

}







const comp =
document.getElementById("vip-complements");



if(comp){

comp.textContent =
complements.join(" - ") || "-";

}



}










// CHEVAL À SURVEILLER


const surveille =
document.getElementById("cheval-surveille");



if(surveille && chevaux[2]){


surveille.innerHTML = `


🎯 Cheval à surveiller :


<br>


<strong>

N°${chevaux[2].numero}
-
${chevaux[2].nom || ""}

</strong>


<br>


Indice :
${chevaux[2].indice_az || "-"}


`;

}










// TICKET SÉCURITÉ


const ticket =
document.getElementById("ticket-vip");



if(ticket && data.tickets){


ticket.innerHTML = `


<p>

🏆 Quinté :

<br>

<strong>

${
data.tickets.quinte
?
data.tickets.quinte.join(" - ")
:
"-"
}

</strong>

</p>





<p>

🥉 Tiercé :

<br>

<strong>

${
data.tickets.trio
?
data.tickets.trio.join(" - ")
:
"-"
}

</strong>

</p>





`;

}



}



catch(error){


console.log(
"Erreur VIP :",
error
);


}



}




document.addEventListener(
"DOMContentLoaded",
chargerVIP
);
