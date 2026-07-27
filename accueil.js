const API = "https://az-turf-pro.onrender.com/api/analyse";


// ELEMENTS COURSE

const hippodrome = document.getElementById("meta-hippodrome");
const course = document.getElementById("meta-course");
const discipline = document.getElementById("meta-discipline");
const distance = document.getElementById("meta-distance");
const partants = document.getElementById("meta-partants");


// TABLEAU

const horsesTable = document.getElementById("all-horses");


// ANALYSE AZ

const favoriNumero = document.getElementById("favori-numero");
const favoriNom = document.getElementById("favori-nom");
const favoriRaison = document.getElementById("favori-raison");

const outsiderNumero = document.getElementById("outsider-numero");
const outsiderNom = document.getElementById("outsider-nom");
const outsiderRaison = document.getElementById("outsider-raison");


// POPULAR

const popular = document.getElementById("popular-horses");


// TENDANCE

const tendance = document.getElementById("course-tendance");


// CHRONO

const miniCountdown = document.getElementById("mini-countdown");





function raisonFavori(cheval){

return `
✅ Indice AZ élevé<br>
✅ Bonne forme récente<br>
✅ Confiance forte dans l'analyse
`;

}



function raisonOutsider(cheval){

return `
🔥 Belle cote possible<br>
🔥 Régularité intéressante<br>
🔥 Peut créer la surprise
`;

}







function lancerChrono(heure){


if(!heure || !miniCountdown){

return;

}



setInterval(()=>{


const maintenant = new Date();


const depart = new Date();


let [h,m] = heure.split(":");


depart.setHours(h);

depart.setMinutes(m);

depart.setSeconds(0);



let difference = depart - maintenant;



if(difference <= 0){

miniCountdown.innerHTML =
"🏇 Course en cours";

return;

}



let minutes =
Math.floor(difference / 60000);


let secondes =
Math.floor((difference % 60000)/1000);



miniCountdown.innerHTML =
"⏱ "+minutes+"m "+secondes+"s";



if(minutes <= 5){

miniCountdown.classList.add("urgent");

}

else{

miniCountdown.classList.remove("urgent");

}



},1000);



}









function afficherTendance(chevaux){


if(!tendance){

return;

}



if(chevaux.length >= 8){


tendance.innerHTML =

"📊 Course avec plusieurs possibilités.<br>Favori solide mais outsiders à surveiller.";

}


else{


tendance.innerHTML =

"⭐ Course plus lisible avec des bases fortes.";

}



}








async function chargerAccueil(){


try{


const response = await fetch(API);


const data = await response.json();



const chevaux =
data.classement ||
data.chevaux ||
[];





// INFOS COURSE


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


if(partants)
partants.textContent =
chevaux.length;






// TABLEAU PARTANTS


if(horsesTable){


horsesTable.innerHTML="";


chevaux.forEach((cheval)=>{


horsesTable.innerHTML += `

<tr>

<td>${cheval.numero || "-"}</td>

<td><strong>${cheval.nom || "Cheval"}</strong></td>

<td>${cheval.jockey || "-"}</td>

<td>${cheval.entraineur || "-"}</td>

<td>${cheval.cote || "-"}</td>

<td>${cheval.type || "Chance"}</td>

</tr>

`;


});


}








// ANALYSE AZ


if(chevaux[0]){


favoriNumero.textContent =
"N°"+chevaux[0].numero;


favoriNom.textContent =
chevaux[0].nom || "Favori";


favoriRaison.innerHTML =
raisonFavori(chevaux[0]);


}





if(chevaux[3]){


outsiderNumero.textContent =
"N°"+chevaux[3].numero;


outsiderNom.textContent =
chevaux[3].nom || "Outsider";


outsiderRaison.innerHTML =
raisonOutsider(chevaux[3]);


}








// CHEVAUX LES PLUS JOUES


if(popular){


popular.innerHTML="";


chevaux.slice(0,8).forEach((cheval)=>{


popular.innerHTML += `

<div class="popular-card">

${cheval.numero}

</div>

`;


});


}







// TENDANCE


afficherTendance(chevaux);






// CHRONO


lancerChrono(data.heure_depart);



}



catch(error){


console.log(
"Erreur accueil : ",
error
);


}



}





document.addEventListener(
"DOMContentLoaded",
chargerAccueil
);
