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
// SELECTION AZ 7 CHEVAUX
// ===============================


const selection =
document.getElementById("selection-az-chevaux");


if(selection){


selection.textContent = chevaux
.slice(0,7)
.map(c => c.numero)
.join(" - ");


}







// ===============================
// FAVORI AZ
// ===============================


const favori = chevaux[0];


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
numero.textContent = favori.numero || "-";


if(nom)
nom.textContent = favori.nom || "Cheval";


if(indice)
indice.textContent = favori.indice_az || "-";


if(confiance)
confiance.textContent =
(favori.confiance || "-") + " %";


if(raison)
raison.textContent =
"⭐ Base AZ : bonne forme, indice AZ élevé et conditions favorables.";


}








// ===============================
// OUTSIDER AZ
// ===============================


const outsider = chevaux[6];


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
numero.textContent = outsider.numero || "-";


if(nom)
nom.textContent = outsider.nom || "Cheval";


if(indice)
indice.textContent = outsider.indice_az || "-";


if(confiance)
confiance.textContent =
(outsider.confiance || "-") + " %";


if(raison)
raison.textContent =
"🔥 Outsider AZ : profil intéressant pouvant surprendre.";


}








// ===============================
// RAISONS SELECTION
// ===============================


const raisons =
document.getElementById("raisons-selection");



if(raisons){


raisons.innerHTML = "";



chevaux.slice(0,7).forEach((cheval,index)=>{


raisons.innerHTML += `


<div class="raison-cheval">


<h3>
N°${cheval.numero || "-"}
${cheval.nom || "Cheval"}
</h3>


<p>

${genererRaison(cheval,index)}

</p>


</div>


`;


});


}









// ===============================
// TABLEAU 7 CHEVAUX AZ
// ===============================


const tableau =
document.getElementById("analyse-body");



if(tableau){


tableau.innerHTML = "";



chevaux.slice(0,7).forEach((cheval,index)=>{


tableau.innerHTML += `


<tr>


<td>${index+1}</td>


<td>${cheval.numero || "-"}</td>


<td>
<strong>${cheval.nom || "Cheval"}</strong>
</td>


<td>${cheval.indice_az || "-"}</td>


<td>${cheval.confiance || "-"} %</td>


<td>
${genererRaison(cheval,index)}
</td>


</tr>


`;


});


}


// ===============================
// TICKETS GRATUITS
// ===============================


const ticketsGratuits =
data.tickets?.gratuit || {};



const quinteGratuit =
document.getElementById("quinte-gratuit");


if(quinteGratuit){

quinteGratuit.innerHTML = `

<strong>

${(ticketsGratuits.quinte || [])
.join(" - ")}

</strong>

`;

}



const deuxSurQuatre =
document.getElementById("deux-sur-quatre");


if(deuxSurQuatre){

deuxSurQuatre.innerHTML = `

<strong>

${(ticketsGratuits.deux_sur_quatre || [])
.join(" - ")}

</strong>

`;

}



const couplePlaceGratuit =
document.getElementById("couple-place-gratuit");


if(couplePlaceGratuit){

couplePlaceGratuit.innerHTML = `

<strong>

${
(ticketsGratuits.couple_place || [])
.map(c => c.join(" - "))
.join(" | ")
}

</strong>

`;

}





// ===============================
// AVIS JOCKEYS / ENTRAINEURS
// ===============================


const avis =
document.getElementById("avis-course");



if(avis && chevaux.length){


avis.innerHTML = `


<p>

👤 <strong>Avis jockeys :</strong><br>

Les chevaux retenus présentent des profils intéressants selon la forme et les conditions du jour.

</p>


<p>

🏇 <strong>Avis entraîneurs :</strong><br>

La préparation, la régularité et l'engagement sont pris en compte dans l'analyse AZ.

</p>


`;



}








// ===============================
// ACTUALITES COURSE
// ===============================


const actualites =
document.getElementById("actualites-course");



if(actualites){


actualites.innerHTML = `


<ul>

<li>📌 Analyse des conditions de course</li>

<li>🏇 Étude des chevaux engagés</li>

<li>⚠️ Surveillance des changements de dernière minute</li>

</ul>


`;



}








// ===============================
// SYNTHESE AZ
// ===============================


const synthese =
document.getElementById("synthese-az");



if(synthese && chevaux.length){


synthese.innerHTML = `


<p>
⭐ La sélection AZ privilégie :
</p>


<ul>

<li>La forme récente</li>

<li>La régularité</li>

<li>L'adaptation au parcours</li>

<li>Le potentiel pour les premières places</li>

</ul>


`;



}








// ===============================
// MESSAGES VISITEURS
// ===============================


const bouton =
document.getElementById("envoyer-message");


const zone =
document.getElementById("message-visiteur");


const affichage =
document.getElementById("messages-visiteurs");





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



zone.value="";


});


}




}

catch(error){


console.log(
"Erreur analyse :",
error
);


}



}







function genererRaison(cheval,index){


if(index===0){


return `
⭐ Base principale : excellente position AZ, forme et confiance élevées.
`;

}


if(index===1){


return `
⭐ Très belle chance : régularité et capacité à confirmer.
`;

}


if(index<4){


return `
✅ Chance solide : profil adapté pour jouer les premiers rôles.
`;

}



return `
🔥 Chance à surveiller : outsider avec possibilité de surprise.
`;



}







document.addEventListener(

"DOMContentLoaded",

chargerAnalyse

);
