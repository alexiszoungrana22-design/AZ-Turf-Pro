const API = "https://az-turf-pro.onrender.com/api/analyse";

const hippodrome = document.getElementById("meta-hippodrome");
const course = document.getElementById("meta-course");
const discipline = document.getElementById("meta-discipline");
const distance = document.getElementById("meta-distance");
const partants = document.getElementById("meta-partants");

const horsesTable = document.getElementById("all-horses");

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

const popular = document.getElementById("popular-horses");

const tendance = document.getElementById("course-tendance");

const miniCountdown = document.getElementById("mini-countdown");


function raisonFavori(){
return `
✅ Meilleur indice<br>
✅ Bonne régularité<br>
✅ Profil adapté
`;
}


function raisonOutsider(){
return `
🔥 Rapport intéressant<br>
🔥 Peut surprendre
`;
}



function afficherTendance(chevaux){

if(!tendance) return;

if(chevaux.length >= 8){

tendance.innerHTML =
"📈 Course ouverte";

}else{

tendance.innerHTML =
"⭐ Course plus lisible";

}

}



function lancerChrono(){

if(miniCountdown){

miniCountdown.innerHTML="⏱ Départ : --:--:--";

}

}





async function chargerAccueil(){

try{


const response = await fetch(API);


if(!response.ok){

throw new Error("API inaccessible");

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
partants.textContent=data.partants || chevaux.length;





// PARTANTS

if(horsesTable){

horsesTable.innerHTML="";


chevaux.forEach((cheval)=>{

horsesTable.innerHTML += `

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





// FAVORI

if(chevaux[0]){

let favori=chevaux[0];


if(favoriNumero)
favoriNumero.textContent="N°"+favori.numero;


if(favoriNom)
favoriNom.textContent=favori.nom;


if(favoriIndice)
favoriIndice.textContent=favori.indice_az;


if(favoriConfiance)
favoriConfiance.textContent=(favori.confiance || "-")+" %";


if(favoriRaison)
favoriRaison.innerHTML=raisonFavori();

}





// OUTSIDER

if(chevaux[3]){

let outsider=chevaux[3];


if(outsiderNumero)
outsiderNumero.textContent="N°"+outsider.numero;


if(outsiderNom)
outsiderNom.textContent=outsider.nom;


if(outsiderIndice)
outsiderIndice.textContent=outsider.indice_az;


if(outsiderConfiance)
outsiderConfiance.textContent=(outsider.confiance || "-")+" %";


if(outsiderRaison)
outsiderRaison.innerHTML=raisonOutsider();

}





// CHEVAUX LES PLUS JOUÉS

if(popular){

const numeros = data.plus_joues || [];

const source = data.source_plus_joues || "";


popular.innerHTML = `

<div style="font-size:32px;font-weight:bold;text-align:center;">

${numeros.join(" - ")}

</div>


<div style="text-align:center;margin-top:10px;">

Source : ${source}

</div>

`;

}





afficherTendance(chevaux);


lancerChrono();



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
