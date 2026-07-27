const API = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerAccueil(){


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


const elements = {

hippodrome:"meta-hippodrome",

course:"meta-course",

discipline:"meta-discipline",

distance:"meta-distance",

partants:"meta-partants"

};



if(document.getElementById(elements.hippodrome))
document.getElementById(elements.hippodrome).textContent =
data.hippodrome || "-";


if(document.getElementById(elements.course))
document.getElementById(elements.course).textContent =
data.course || "-";


if(document.getElementById(elements.discipline))
document.getElementById(elements.discipline).textContent =
data.discipline || "-";


if(document.getElementById(elements.distance))
document.getElementById(elements.distance).textContent =
(data.distance_course || "-")+" m";


if(document.getElementById(elements.partants))
document.getElementById(elements.partants).textContent =
chevaux.length+" chevaux";






// ===============================
// PUBLICITE IMAGE / VIDEO
// ===============================


const video =
document.getElementById("pub-video");

const image =
document.getElementById("pub-image");



if(video && image){


video.addEventListener("loadeddata",()=>{

image.style.display="none";

video.style.display="block";

});


}







// ===============================
// TABLEAU PARTANTS
// ===============================


const tableau =
document.getElementById("all-horses");



if(tableau){


tableau.innerHTML="";



chevaux.forEach((cheval,index)=>{


tableau.innerHTML += `

<tr>

<td>${cheval.numero || "-"}</td>

<td><strong>${cheval.nom || "Cheval"}</strong></td>

<td>${cheval.jockey || "-"}</td>

<td>${cheval.entraineur || "-"}</td>

<td>${cheval.cote || "-"}</td>

<td>
${
cheval.type ||
(index===0
?"Favori"
:index<3
?"Chance"
:"Outsider")
}
</td>

</tr>

`;


});


}







// ===============================
// ANALYSE AZ
// ===============================


const favori =
chevaux[0];


const outsider =
chevaux[3];




if(favori){


document.getElementById("favori-numero").textContent =
"N°"+favori.numero;


document.getElementById("favori-nom").textContent =
favori.nom || "Cheval";


document.getElementById("favori-raison").innerHTML =

`
Pourquoi nous le préférons :

<br>
✅ Indice AZ : ${favori.indice_az || "-"}
<br>
✅ Confiance : ${favori.confiance || "-"} %
<br>
✅ Forme : ${favori.forme || "-"}
`;



}






if(outsider){


document.getElementById("outsider-numero").textContent =
"N°"+outsider.numero;


document.getElementById("outsider-nom").textContent =
outsider.nom || "Cheval";


document.getElementById("outsider-raison").innerHTML =

`
Pourquoi il peut surprendre :

<br>
🔥 Indice AZ : ${outsider.indice_az || "-"}
<br>
🔥 Cote : ${outsider.cote || "-"}
<br>
🔥 Régularité : ${outsider.regularite || "-"}
`;



}








// ===============================
// CHEVAUX LES PLUS JOUES
// ===============================


const popular =
document.getElementById("popular-horses");



if(popular){


popular.innerHTML="";



chevaux.slice(0,6).forEach((cheval)=>{


popular.innerHTML += `

<div class="popular-card">

<strong>

N°${cheval.numero}

</strong>


<p>

${cheval.nom || "Cheval"}

</p>


</div>

`;



});


}







// ===============================
// MINI COMPTE A REBOURS
// ===============================


lancerMiniCompte(
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








function lancerMiniCompte(heure){


const timer =
document.getElementById("mini-countdown");



if(!timer || !heure){

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



const diff =
depart - maintenant;



if(diff<=0){

timer.textContent =
"🏇 Course en cours";

timer.classList.add("urgent");

return;

}




const minutes =
Math.floor(diff/60000);



if(minutes<=5){

timer.classList.add("urgent");

}

else{

timer.classList.remove("urgent");

}




const heures =
Math.floor(diff/3600000);



const mins =
Math.floor((diff%3600000)/60000);



const secondes =
Math.floor((diff%60000)/1000);




timer.textContent =

`⏱ Départ : ${String(heures).padStart(2,"0")}:${String(mins).padStart(2,"0")}:${String(secondes).padStart(2,"0")}`;



},1000);



}







document.addEventListener(
"DOMContentLoaded",
chargerAccueil
);
