const API = "https://az-turf-pro.onrender.com/api/analyse";


// Informations course

const analyseCourse = document.getElementById("analyse-course");
const analyseHippodrome = document.getElementById("analyse-hippodrome");
const analyseDiscipline = document.getElementById("analyse-discipline");
const analyseDistance = document.getElementById("analyse-distance");


// Tableau

const tableBody = document.getElementById("az-selection");


// Commentaires

const commentairesPro = document.getElementById("commentaires-pro");


// Cartes horizontales

const selectionHorizontal =
document.getElementById("selection-az-horizontal");





function obtenirRaison(cheval,index){


if(cheval.raison){

return cheval.raison;

}


if(cheval.type){

return cheval.type;

}


if(index === 0){

return "⭐ Favori AZ";

}


if(index < 3){

return "🔥 Base solide";

}


if(index < 5){

return "🎯 Chance régulière";

}


return "💎 Outsider intéressant";


}








async function chargerAnalyse(){


try{


const response = await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();





// COURSE


if(analyseCourse)

analyseCourse.textContent =
data.course || "-";



if(analyseHippodrome)

analyseHippodrome.textContent =
data.hippodrome || "-";



if(analyseDiscipline)

analyseDiscipline.textContent =
data.discipline || "-";



if(analyseDistance)

analyseDistance.textContent =
(data.distance_course || "-") + " m";







const chevaux =
data.classement ||
data.chevaux ||
[];







// TABLEAU DES 7 RETENUS


if(tableBody){


tableBody.innerHTML = "";



chevaux.slice(0,7)
.forEach((cheval,index)=>{


const tr =
document.createElement("tr");



tr.innerHTML = `


<td>
${cheval.numero || "-"}
</td>


<td>
<strong>
${cheval.nom || "Cheval AZ"}
</strong>
</td>


<td>
${cheval.jockey || "-"}
</td>


<td>
${cheval.entraineur || "-"}
</td>


<td>
${cheval.forme || cheval.musique || "-"}
</td>


<td>
${cheval.indice_az || cheval.score || 0}
</td>


<td>
${obtenirRaison(cheval,index)}
</td>


<td>
${cheval.commentaire || "Analyse en cours"}
</td>


<td>
${cheval.rang || index+1}
</td>


`;



tableBody.appendChild(tr);


});


}








// COMMENTAIRES PROFESSIONNELS


if(commentairesPro){


commentairesPro.innerHTML = "";



chevaux.slice(0,7)
.forEach((cheval)=>{


const bloc =
document.createElement("p");



bloc.innerHTML = `


<strong>
N°${cheval.numero || "-"} 
${cheval.nom || "Cheval AZ"}
</strong>


<br>


🏇 Jockey :
${cheval.commentaire_jockey || "Pas de commentaire"}


<br>


👤 Entraîneur :
${cheval.commentaire_entraineur || "Pas de commentaire"}


`;



commentairesPro.appendChild(bloc);


});


}








// CARTES HORIZONTALES


if(selectionHorizontal){


selectionHorizontal.innerHTML = "";



chevaux.slice(0,7)
.forEach((cheval,index)=>{


const carte =
document.createElement("div");


carte.className =
"cheval-mini";



carte.innerHTML = `


<div class="mini-numero">

N°${cheval.numero || "-"}

</div>


<strong>
${cheval.nom || "Cheval AZ"}
</strong>


<br>


Indice AZ :
${cheval.indice_az || 0}


<br>


<small>

${obtenirRaison(cheval,index)}

</small>


`;



selectionHorizontal.appendChild(carte);


});


}




}


catch(error){


console.log(
"Erreur Analyse AZ :",
error
);


}



}






document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
