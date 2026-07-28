const API = "https://az-turf-pro.onrender.com/api/analyse";


// Informations course

const hippodrome = document.getElementById("meta-hippodrome");
const course = document.getElementById("meta-course");
const discipline = document.getElementById("meta-discipline");
const distance = document.getElementById("meta-distance");
const partants = document.getElementById("meta-partants");


// Tableau

const horsesTable = document.getElementById("all-horses");


// Analyse

const favoriNumero = document.getElementById("favori-numero");
const favoriNom = document.getElementById("favori-nom");
const favoriIndice = document.getElementById("favori-indice");
const favoriConfiance = document.getElementById("favori-confiance");
const favoriRaison = document.getElementById("favori-raison");


const outsiderNumero = document.getElementById("outsider-numero");
const outsiderNom = document.getElementById("outsider-nom");
const outsiderIndice = document.getElementById("outsider-indice");
const outsiderConfiance = document.getElementById("outsider-confiance");
const outsiderRaison = document.getElementById("outsider-raison");


// Chevaux joués

const popular = document.getElementById("popular-horses");


// Tendance

const tendance = document.getElementById("course-tendance");


// Chrono

const miniCountdown = document.getElementById("mini-countdown");





function raisonFavori(cheval){

return `
✅ Indice supérieur<br>
✅ Bonne régularité<br>
✅ Profil adapté à la course
`;

}



function raisonOutsider(cheval){

return `
🔥 Rapport intéressant<br>
🔥 Peut améliorer sa position<br>
🔥 Profil pour surprendre
`;

}







function lancerChrono(heure){


if(!heure || !miniCountdown){

return;

}


setInterval(()=>{


const maintenant = new Date();

const depart = new Date();


const temps = heure.split(":");


depart.setHours(temps[0]);

depart.setMinutes(temps[1]);

depart.setSeconds(0);



let diff = depart - maintenant;



if(diff <= 0){

miniCountdown.innerHTML="🏇 Course en cours";

return;

}



let minutes = Math.floor(diff / 60000);

let secondes = Math.floor((diff % 60000)/1000);



miniCountdown.innerHTML =
"⏱ "+minutes+"m "+secondes+"s";



if(minutes <= 5){

miniCountdown.classList.add("urgent");

}else{

miniCountdown.classList.remove("urgent");

}



},1000);


}







function afficherTendance(chevaux){


if(!tendance) return;



if(chevaux.length >= 8){

tendance.innerHTML =
"📈 Course ouverte : plusieurs chevaux peuvent jouer un rôle. Favori solide avec un outsider intéressant.";

}else{

tendance.innerHTML =
"⭐ Course plus lisible : les bases semblent se dégager.";

}


}








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





// COURSE


if(hippodrome)
hippodrome.textContent=data.hippodrome || "-";


if(course)
course.textContent=data.course || "-";


if(discipline)
discipline.textContent=data.discipline || "-";


if(distance)
distance.textContent=(data.distance_course || "-")+" m";


if(partants)
partants.textContent=chevaux.length;








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








// FAVORI


if(chevaux[0]){


const favori = chevaux[0];


favoriNumero.textContent =
"N°"+favori.numero;


favoriNom.textContent =
favori.nom || "Favori";


favoriIndice.textContent =
favori.indice_az || "-";


favoriConfiance.textContent =
(favori.confiance || "-")+" %";


favoriRaison.innerHTML =
raisonFavori(favori);


}







// OUTSIDER


if(chevaux[3]){


const outsider = chevaux[3];


outsiderNumero.textContent =
"N°"+outsider.numero;


outsiderNom.textContent =
outsider.nom || "Outsider";


outsiderIndice.textContent =
outsider.indice_az || "-";


outsiderConfiance.textContent =
(outsider.confiance || "-")+" %";


outsiderRaison.innerHTML =
raisonOutsider(outsider);


}








// CHEVAUX LES PLUS JOUÉS


if(popular){


const numeros = chevaux
.slice(0,5)
.map(cheval => cheval.numero);



popular.innerHTML = `

<div class="ticket-grand">

${numeros.join(" - ")}

</div>


<p>
Source : Turf.fr
</p>

`;

}








// TENDANCE


afficherTendance(chevaux);






// CHRONO


lancerChrono(data.heure_depart);



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
