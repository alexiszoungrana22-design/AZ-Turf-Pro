const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerAnalyse(){

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
// INFORMATIONS COURSE
// ===============================


function afficher(id, valeur){

const element =
document.getElementById(id);


if(element){

element.textContent =
valeur || "-";

}

}



afficher(
"meta-hippodrome",
data.hippodrome
);


afficher(
"meta-course",
data.course
);


afficher(
"meta-discipline",
data.discipline
);


afficher(
"meta-distance",
data.distance ? data.distance + " m" : "-"
);


afficher(
"meta-partants",
data.partants
);






// ===============================
// PLUS JOUÉS
// ===============================


const popular =
document.getElementById("popular-horses");



if(popular){


const plusJoues =
data.plus_joues || [];



if(plusJoues.length){


popular.innerHTML =
plusJoues.map(numero =>

`
<div class="popular-number">
${numero}
</div>
`

).join("");


}
else{

popular.innerHTML =
"Plus joué indisponible";

}


}








// ===============================
// FAVORI AZ
// ===============================


const favori =
chevaux[0];



if(favori){


const numero =
document.getElementById("favori-numero");


const nom =
document.getElementById("favori-nom");


const indice =
document.getElementById("favori-indice");


const confiance =
document.getElementById("favori-confiance");


const raison =
document.getElementById("favori-raison");



if(numero)
numero.textContent =
favori.numero || "-";


if(nom)
nom.textContent =
favori.nom || "Cheval";


if(indice)
indice.textContent =
favori.indice_az || "-";


if(confiance)
confiance.textContent =
(favori.confiance || "-") + " %";


if(raison)
raison.textContent =
favori.raison ||
"⭐ Base AZ";

}



 



// ===============================
// OUTSIDER AZ
// ===============================


const outsider =
chevaux[6];



if(outsider){


const numero =
document.getElementById("outsider-numero");


const nom =
document.getElementById("outsider-nom");


const indice =
document.getElementById("outsider-indice");


const confiance =
document.getElementById("outsider-confiance");


const raison =
document.getElementById("outsider-raison");



if(numero)
numero.textContent =
outsider.numero || "-";


if(nom)
nom.textContent =
outsider.nom || "Cheval";


if(indice)
indice.textContent =
outsider.indice_az || "-";


if(confiance)
confiance.textContent =
(outsider.confiance || "-") + " %";


if(raison)
raison.textContent =
outsider.raison ||
"🔥 Outsider AZ";

}



 



// ===============================
// TABLEAU DES PARTANTS
// ===============================


const tableau =
document.getElementById("all-horses");



if(tableau){


tableau.innerHTML = "";



chevaux.forEach(cheval => {


tableau.innerHTML += `

<tr>

<td>${cheval.numero || "-"}</td>

<td>${cheval.nom || "-"}</td>

<td>${cheval.jockey || "-"}</td>

<td>${cheval.entraineur || "-"}</td>

<td>${cheval.cote || "-"}</td>

</tr>

`;

});


}






// ===============================
// TICKETS GRATUITS
// ===============================


const tickets =
data.tickets?.gratuit || {};



const quinte =
document.getElementById("quinte-gratuit");



if(quinte){

quinte.innerHTML =
(tickets.quinte || [])
.join(" - ");

}




const deux =
document.getElementById("deux-sur-quatre");



if(deux){

deux.innerHTML =
(tickets.deux_sur_quatre || [])
.join(" - ");

}




const couple =
document.getElementById("couple-place-gratuit");



if(couple){

couple.innerHTML =
(tickets.couple_place || [])
.map(c => c.join(" - "))
.join(" | ");

}





}

catch(error){


console.log(
"Erreur analyse :",
error
);


}


}




document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
