const API = "https://az-turf-pro.onrender.com/api/analyse";


// Informations course

const hippodrome =
document.getElementById("meta-hippodrome");

const course =
document.getElementById("meta-course");

const discipline =
document.getElementById("meta-discipline");

const distance =
document.getElementById("meta-distance");

const partants =
document.getElementById("meta-partants");



// Tableau

const horsesTable =
document.getElementById("all-horses");



// Favori

const favoriteNumber =
document.getElementById("favorite-number");

const favoriteName =
document.getElementById("favorite-name");

const favoriteIndex =
document.getElementById("favorite-index");

const favoriteConfidence =
document.getElementById("favorite-confidence");



// Outsider

const outsiderNumber =
document.getElementById("outsider-number");

const outsiderName =
document.getElementById("outsider-name");

const outsiderIndex =
document.getElementById("outsider-index");

const outsiderConfidence =
document.getElementById("outsider-confidence");



// KPI

const confidence =
document.getElementById("kpi-confidence");

const kpiPartants =
document.getElementById("kpi-partants");

const kpiFollow =
document.getElementById("kpi-follow");



// Populaires

const popular =
document.getElementById("popular-horses");



// Sélection

const selection =
document.getElementById("home-selection");



// Horloge

const timer =
document.getElementById("timer");






function raisonCheval(cheval,index){


if(cheval.type){

return cheval.type;

}


if(index===0){

return "Favori du jour";

}


if(index<3){

return "Belle chance";

}


return "Chance";

}







function lancerCompteARebours(heure){


if(!heure || !timer){

return;

}



setInterval(()=>{


const maintenant =
new Date();


const depart =
new Date();



const [h,m] =
heure.split(":");



depart.setHours(h);
depart.setMinutes(m);
depart.setSeconds(0);



let diff =
depart - maintenant;



if(diff<=0){


timer.textContent =
"🏇 Course en cours";

return;


}



let heures =
Math.floor(diff / 3600000);


let minutes =
Math.floor(
(diff % 3600000)/60000
);


let secondes =
Math.floor(
(diff % 60000)/1000
);



timer.textContent =

`${String(heures).padStart(2,"0")}:
${String(minutes).padStart(2,"0")}:
${String(secondes).padStart(2,"0")}`;



},1000);


}








async function chargerAccueil(){


try{


const response =
await fetch(API);



const data =
await response.json();





if(hippodrome)
hippodrome.textContent =
data.hippodrome || "-";



if(course)
course.textContent =
data.course || "-";



if(discipline)
discipline.textContent =
data.discipline || "-";



if(distance)
distance.textContent =
(data.distance_course || "-")+" m";







const chevaux =
data.classement ||
data.chevaux ||
[];





if(partants)
partants.textContent =
chevaux.length+" chevaux";






// TABLEAU PARTANTS


if(horsesTable){


horsesTable.innerHTML="";



chevaux.forEach((cheval,index)=>{


horsesTable.innerHTML += `

<tr>

<td>${cheval.numero || "-"}</td>

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
${cheval.cote || "-"}
</td>

<td>
${raisonCheval(cheval,index)}
</td>

</tr>

`;

});


}









// FAVORI DU JOUR


if(chevaux[0]){


const fav =
chevaux[0];



if(favoriteNumber)
favoriteNumber.textContent =
"N°"+fav.numero;



if(favoriteName)
favoriteName.textContent =
fav.nom || "-";



if(favoriteIndex)
favoriteIndex.textContent =
fav.indice_az || "-";



if(favoriteConfidence)
favoriteConfidence.textContent =
(fav.confiance || "-")+" %";


}








// OUTSIDER DU JOUR


if(chevaux[3]){


const out =
chevaux[3];



if(outsiderNumber)
outsiderNumber.textContent =
"N°"+out.numero;



if(outsiderName)
outsiderName.textContent =
out.nom || "-";



if(outsiderIndex)
outsiderIndex.textContent =
out.indice_az || "-";



if(outsiderConfidence)
outsiderConfidence.textContent =
(out.confiance || "-")+" %";


}








// KPI


if(confidence && chevaux[0]){

confidence.textContent =
(chevaux[0].confiance || "-")+" %";

}


if(kpiPartants){

kpiPartants.textContent =
chevaux.length;

}


if(kpiFollow){

kpiFollow.textContent =
chevaux.slice(0,5).length;

}








// CHEVAUX LES PLUS JOUÉS


if(popular){


popular.innerHTML="";



chevaux.slice(0,5)
.forEach(cheval=>{


popular.innerHTML += `

<p>
🐎 N°${cheval.numero}
${cheval.nom || ""}
</p>

`;

});


}








// SELECTION DU JOUR


if(selection){


selection.innerHTML="";



chevaux.slice(0,7)
.forEach(cheval=>{


selection.innerHTML += `

<div class="cheval-mini">


<div class="mini-numero">

N°${cheval.numero}

</div>


<strong>

${cheval.nom || "Cheval"}

</strong>


<br>

Indice :
${cheval.indice_az || "-"}


</div>

`;

});


}






lancerCompteARebours(
data.heure_depart
);



}


catch(error){


console.log(
"Erreur accueil :",
error
);


}


}






document.addEventListener(
"DOMContentLoaded",
chargerAccueil
);
