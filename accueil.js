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



// Tableau chevaux

const horsesTable =
document.getElementById("all-horses");



// KPI

const favorite =
document.getElementById("kpi-favorite");

const confidence =
document.getElementById("kpi-confidence");

const outsider =
document.getElementById("kpi-outsider");



// Favori / Outsider grand format

const favoriteHome =
document.getElementById("favorite-home");


const outsiderHome =
document.getElementById("outsider-home");



// Chevaux joués

const popular =
document.getElementById("popular-horses");



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









function lancerCompteRebours(heure){


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
Math.floor((diff % 3600000)/60000);


let secondes =
Math.floor((diff % 60000)/1000);



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



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();





// COURSE


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
${cheval.cote || "-"}
</td>


<td>
${raisonCheval(cheval,index)}
</td>


</tr>


`;

});


}









// FAVORI GRAND FORMAT


if(chevaux[0]){


if(favoriteHome){


favoriteHome.innerHTML = `


<div class="favorite-number">

N°${chevaux[0].numero}

</div>


<h3>

${chevaux[0].nom || "Cheval"}

</h3>


<p>

Indice :
${chevaux[0].indice_az || "-"}

</p>


<p>

Confiance :
${chevaux[0].confiance || "-"} %

</p>


`;

}





if(favorite){

favorite.textContent =

"N°"+chevaux[0].numero+
" "+(chevaux[0].nom || "");

}


if(confidence){

confidence.textContent =

(chevaux[0].confiance ||
chevaux[0].indice_az ||
"-")
+" %";

}



}









// OUTSIDER GRAND FORMAT


if(chevaux[3]){


if(outsiderHome){


outsiderHome.innerHTML = `


<div class="outsider-number">

N°${chevaux[3].numero}

</div>


<h3>

${chevaux[3].nom || "Cheval"}

</h3>


<p>

Indice :
${chevaux[3].indice_az || "-"}

</p>


<p>

Confiance :
${chevaux[3].confiance || "-"} %

</p>


`;

}





if(outsider){

outsider.textContent =

"N°"+chevaux[3].numero+
" "+(chevaux[3].nom || "");

}


}









// CHEVAUX LES PLUS JOUÉS


if(popular){


popular.innerHTML="";



chevaux.slice(0,5)
.forEach((cheval)=>{


popular.innerHTML += `


<p>

🐎 N°${cheval.numero}
${cheval.nom || ""}

</p>


`;

});


}








// COMPTE À REBOURS


lancerCompteRebours(
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
