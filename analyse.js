// =====================================
// AZ Turf Pro - Analyse de la course
// =====================================


const API = "https://az-turf-pro.onrender.com/api/analyse";



// Informations course

const course =
document.getElementById("analyse-course");


const hippodrome =
document.getElementById("analyse-hippodrome");


const discipline =
document.getElementById("analyse-discipline");


const distance =
document.getElementById("analyse-distance");



// Tableau chevaux

const tableau =
document.getElementById("selection-horses");


// Commentaires

const commentaires =
document.getElementById("horse-comments");


// Sélection horizontale

const selection =
document.getElementById("selection-horizontal");






function raisonCheval(cheval,index){


if(cheval.type){

return cheval.type;

}


if(index===0){

return "Favori du jour";

}


if(index<3){

return "Cheval régulier";

}


return "Belle chance";

}





async function chargerAnalyse(){


try{


const reponse =
await fetch(API);


const data =
await reponse.json();





// COURSE


if(course)
course.textContent =
data.course || "-";


if(hippodrome)
hippodrome.textContent =
data.hippodrome || "-";


if(discipline)
discipline.textContent =
data.discipline || "-";


if(distance)
distance.textContent =
(data.distance_course || "-") + " m";







const chevaux =

data.classement ||
data.chevaux ||
[];




const retenus =

chevaux.slice(0,7);







// TABLEAU


if(tableau){


tableau.innerHTML="";



retenus.forEach((cheval,index)=>{


tableau.innerHTML += `


<tr>


<td>
${cheval.numero || "-"}
</td>


<td>
<strong>
${cheval.nom || "Cheval"}
</strong>
</td>


<td>
${cheval.jockey || "-"}
</td>


<td>
${cheval.entraineur || "-"}
</td>


<td>
${cheval.forme || "-"}
</td>


<td>
${cheval.indice_az || "-"}
</td>


<td>
${raisonCheval(cheval,index)}
</td>


<td>
${index+1}
</td>


</tr>


`;



});


}








// COMMENTAIRES


if(commentaires){


commentaires.innerHTML="";



retenus.forEach((cheval)=>{


commentaires.innerHTML += `


<div class="ticket-box">


<strong>
N°${cheval.numero} ${cheval.nom || ""}
</strong>


<br><br>


🧑 Jockey :
${cheval.commentaire_jockey || "Aucun commentaire disponible"}


<br>


🏇 Entraîneur :
${cheval.commentaire_entraineur || "Aucun commentaire disponible"}


</div>


`;



});


}







// SELECTION HORIZONTALE


if(selection){


selection.innerHTML="";



retenus.forEach((cheval)=>{


selection.innerHTML += `


<div class="cheval-mini">


<div class="mini-numero">

N°${cheval.numero}

</div>


<strong>

${cheval.nom || "Cheval"}

</strong>


<br><br>


Indice :
${cheval.indice_az || "-"}


</div>


`;



});


}





}


catch(erreur){


console.log(
"Erreur analyse :",
erreur
);


}



}




document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
