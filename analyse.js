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
// TABLEAU CLASSEMENT
// ===============================


const tableau =
document.getElementById("analyse-body");



if(tableau){


tableau.innerHTML = "";



chevaux.forEach((cheval,index)=>{


tableau.innerHTML += `


<tr>


<td>${index+1}</td>


<td>${cheval.numero || "-"}</td>


<td>
<strong>
${cheval.nom || "Cheval"}
</strong>
</td>


<td>${cheval.indice_az || "-"}</td>


<td>${cheval.forme || "-"}</td>


<td>${cheval.regularite || "-"}</td>


<td>${cheval.jockey || "-"}</td>


<td>${cheval.entraineur || "-"}</td>


<td>
${cheval.confiance || "-"} %
</td>


</tr>


`;



});


}









// ===============================
// AVIS JOCKEYS / ENTRAINEURS
// ===============================


const avis =
document.getElementById("avis-course");



if(avis && chevaux.length){


avis.innerHTML = `


<p>

👤 <strong>Jockeys :</strong><br>

Les chevaux retenus présentent des profils intéressants selon la forme et les conditions de course.

</p>


<p>

🏇 <strong>Entraîneurs :</strong><br>

La préparation et la régularité des chevaux sont prises en compte dans la sélection AZ.

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


<p>
📰 Informations course :
</p>


<ul>

<li>Analyse des conditions de course</li>

<li>Étude des chevaux engagés</li>

<li>Surveillance des changements de dernière minute</li>

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

⭐ La sélection AZ privilégie les chevaux avec :

</p>


<ul>

<li>Bonne forme récente</li>

<li>Régularité</li>

<li>Profil adapté à la course</li>

<li>Capacité à lutter pour les premières places</li>

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
⭐ Base principale :
bonne forme, indice AZ élevé et profil favorable.
`;

}


if(index===1){


return `
⭐ Très bonne chance :
régularité et capacité à confirmer.
`;

}


if(index<4){


return `
✅ Belle possibilité :
profil intéressant pour les places.
`;

}



return `
🔥 Chance à surveiller :
peut profiter des conditions de course.
`;



}







document.addEventListener(

"DOMContentLoaded",

chargerAnalyse

);
