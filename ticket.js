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






// ===============================
// SELECTION AZ 7 CHEVAUX
// ===============================


const selection =
document.getElementById("selection-ticket");


if(selection){


selection.innerHTML = `


<strong>

${
chevaux
.slice(0,7)
.map(c => c.numero)
.join(" - ")
}

</strong>


`;



}









// ===============================
// 2 SUR 4
// ===============================


const deuxQuatre =
document.getElementById("deux-quatre-ticket");



if(deuxQuatre){


deuxQuatre.innerHTML = `


<strong>

${
chevaux
.slice(0,4)
.map(c => c.numero)
.join(" - ")
}

</strong>


`;



}









// ===============================
// OUTSIDER AZ
// ===============================


const outsider =
document.getElementById("outsider-ticket");



if(outsider){


const cheval =
chevaux[6];



outsider.innerHTML = `


<strong>

N°${cheval ? cheval.numero : "-"}

</strong>


`;



}









// ===============================
// CHEVAL CACHE
// ===============================


const cache =
document.getElementById("cache-ticket");



if(cache){


const cheval =
chevaux[7];



cache.innerHTML = `


<strong>

N°${cheval ? cheval.numero : "-"}

</strong>


`;



}









// ===============================
// ACTUALITES
// ===============================


const actualites =
document.getElementById("actualites-ticket");



if(actualites){


actualites.innerHTML = `


<p>
📰 Informations course du jour
</p>


<ul>

<li>Analyse des engagés</li>

<li>Suivi de la forme des chevaux</li>

<li>Informations importantes avant le départ</li>

</ul>


`;



}









// ===============================
// MESSAGES VISITEURS
// ===============================


const bouton =
document.getElementById("envoyer-ticket");


const zone =
document.getElementById("message-ticket");


const affichage =
document.getElementById("messages-ticket");





if(bouton){


bouton.addEventListener("click",()=>{


const message =
zone.value.trim();



if(message === ""){

return;

}



affichage.innerHTML += `


<p>

💬 ${message}

</p>


`;



zone.value = "";


});


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
