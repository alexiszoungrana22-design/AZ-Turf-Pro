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
// FONCTION AFFICHAGE
// ===============================

function afficher(id, valeur){

const element =
document.getElementById(id);

if(element){

element.textContent =
valeur || "-";

}

}



// ===============================
// INFORMATIONS COURSE
// ===============================

afficher(
"meta-hippodrome",
data.hippodrome
);


afficher(
"meta-course",
data.course
);


afficher(
"meta-discipline",
data.discipline
);


afficher(
"meta-distance",
data.distance ? data.distance + " m" : "-"
);


afficher(
"meta-partants",
data.partants
);




// ===============================
// PLUS JOUÃ‰S
// ===============================

const popular =
document.getElementById("popular-horses");


if(popular){

const plusJoues =
data.plus_joues || [];


if(plusJoues.length){

popular.innerHTML =
plusJoues.map(numero =>

`
<div class="popular-number">
${numero}
</div>
`

).join("");

}else{

popular.innerHTML =
"Plus jouÃ© indisponible";

}

}




// ===============================
// TENDANCE DE LA COURSE
// ===============================

const tendance =
document.getElementById("course-tendance");


if(tendance && chevaux.length){


tendance.innerHTML = `

<p>
ðŸ”¥ Chevaux les plus jouÃ©s :
<strong>
${(data.plus_joues || []).join(" - ")}
</strong>
</p>


<p>
â­ Favori AZ :
<strong>
NÂ°${chevaux[0].numero}
</strong>
avec un indice AZ de
<strong>
${chevaux[0].indice_az || "-"}
</strong>
</p>


<p>
ðŸ“Š La tendance est basÃ©e sur la forme, la rÃ©gularitÃ© et le classement AZ.
</p>

`;

}





// ===============================
// FAVORI AZ
// ===============================

const favori =
chevaux[0];


if(favori){


afficher(
"favori-numero",
favori.numero
);


afficher(
"favori-nom",
favori.nom
);


afficher(
"favori-indice",
favori.indice_az
);


afficher(
"favori-confiance",
(favori.confiance || "-") + " %"
);


afficher(
"favori-raison",
favori.raison ||
"â­ Favori AZ"
);

}





// ===============================
// OUTSIDER AZ
// ===============================

const outsider =
chevaux[6];


if(outsider){


afficher(
"outsider-numero",
outsider.numero
);


afficher(
"outsider-nom",
outsider.nom
);


afficher(
"outsider-indice",
outsider.indice_az
);


afficher(
"outsider-confiance",
(outsider.confiance || "-") + " %"
);


afficher(
"outsider-raison",
outsider.raison ||
"ðŸ”¥ Outsider AZ"
);

}






// ===============================
// TABLEAU DES PARTANTS
// ===============================

const tableau =
document.getElementById("all-horses");


if(tableau){


tableau.innerHTML = "";


chevaux.forEach(cheval => {


tableau.innerHTML += `

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







// ===============================
// TICKETS GRATUITS
// ===============================

const tickets =
data.tickets?.gratuit || {};



afficher(
"quinte-gratuit",
(tickets.quinte || []).join(" - ")
);



afficher(
"deux-sur-quatre",
(tickets.deux_sur_quatre || []).join(" - ")
);



const couple =
document.getElementById("couple-place-gratuit");


if(couple){

couple.innerHTML =
(tickets.couple_place || [])
.map(c => c.join(" - "))
.join(" | ");

}





afficherConfianceCourse(data);

afficherChevauxSurveiller(data);




}

catch(error){

console.log(
"Erreur analyse :",
error
);

}

}



document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
/* =====================================
   AZ TURF PRO
   SLIDER PUBLICITAIRE ACCUEIL V2
===================================== */


const publicites = [

{
image:"images/pub1.jpg",
titre:"â­ AZ Turf Pro Premium",
texte:"Analyses spÃ©cialisÃ©es et tickets exclusifs"
},

{
image:"images/pub2.jpg",
titre:"ðŸ‡ Analyse du QuintÃ©",
texte:"Des pronostics basÃ©s sur les performances"
},

{
image:"images/pub3.jpg",
titre:"ðŸ’Ž Abonnement Premium",
texte:"AccÃ©dez aux sÃ©lections avancÃ©es"
},

{
image:"images/pub4.jpg",
titre:"ðŸ“¢ Votre publicitÃ© ici",
texte:"Un espace dÃ©diÃ© aux partenaires"
},

{
image:"images/pub5.jpg",
titre:"ðŸ† AZ Turf Pro",
texte:"Une analyse professionnelle au service des pronostics"
}

];



let indexPub = 0;



function changerPublicite(){


const image =
document.getElementById("pub-image");


const titre =
document.getElementById("pub-title");


const texte =
document.getElementById("pub-text");


const points =
document.querySelectorAll(".dot");



if(!image){

return;

}



indexPub++;



if(indexPub >= publicites.length){

indexPub = 0;

}



image.style.opacity = "0";



setTimeout(()=>{


image.src =
publicites[indexPub].image;


if(titre){

titre.innerHTML =
publicites[indexPub].titre;

}


if(texte){

texte.innerHTML =
publicites[indexPub].texte;

}



points.forEach(
(point,i)=>{

point.classList.toggle(
"active",
i===indexPub
);

}

);



image.style.opacity="1";


},400);



}




setInterval(
changerPublicite,
4000
);
/* =====================================
   AZ TURF PRO
   NOUVEAUX BLOCS ACCUEIL
   INDICE CONFIANCE + SURVEILLANCE
===================================== */


function afficherConfianceCourse(data){


const indice =
document.getElementById("indice-confiance");


const message =
document.getElementById("message-confiance");



if(!indice){

return;

}



/*
   Utilise l'indice de confiance
   dÃ©jÃ  fourni par l'analyse
*/

let confiance = 
data.favori?.confiance || 0;



indice.innerHTML =
confiance + "%";




if(message){


if(confiance >= 80){

message.innerHTML =
"âœ… Course avec un niveau de confiance Ã©levÃ©";


}

else if(confiance >= 60){


message.innerHTML =
"âš ï¸ Course avec quelques incertitudes";


}

else{


message.innerHTML =
"ðŸ”Ž Course ouverte, prudence recommandÃ©e";


}


}


}








function afficherChevauxSurveiller(data){


const zone =
document.getElementById("chevaux-surveiller");



if(!zone){

return;

}



const classement =
data.classement || [];



if(classement.length === 0){


zone.innerHTML =
"Analyse en cours...";


return;

}



// =====================================
// LOGIQUE "CHEVAUX A SURVEILLER"
//
// Ce ne sont PAS simplement les 3 premiers
// du classement (dÃ©jÃ  mis en avant comme
// Favori/Outsider ailleurs sur la page).
//
// Ce sont des chevaux hors du top 2 dont
// l'indice AZ reste suffisamment proche du
// leader pour reprÃ©senter une vraie menace :
// capables de battre les favoris ou de
// crÃ©er la surprise, d'aprÃ¨s les donnÃ©es
// de l'analyse (indice_az / confiance).
// =====================================

const meilleurIndice =
classement[0].indice_az || 0;

const SEUIL_MENACE = 0.70;
// un cheval hors du top 2 est considÃ©rÃ©
// "Ã  surveiller" si son indice AZ atteint
// au moins 70% du meilleur indice de la course

let candidats =
classement
.filter(c => c.rang > 2)
.filter(c =>
meilleurIndice > 0 &&
(c.indice_az || 0) >= meilleurIndice * SEUIL_MENACE
)
.sort((a,b) => (b.indice_az||0) - (a.indice_az||0))
.slice(0,3);


// Repli : si aucun cheval n'atteint le seuil
// (course trÃ¨s hiÃ©rarchisÃ©e), on prend quand
// mÃªme les mieux placÃ©s juste derriÃ¨re le podium,
// plutÃ´t que de laisser le bloc vide.
if(candidats.length === 0){

candidats =
classement
.filter(c => c.rang > 2)
.slice(0,3);

}


if(candidats.length === 0){

zone.innerHTML =
"Analyse en cours...";

return;

}


zone.innerHTML =


candidats.map(c => {

const ecart =
meilleurIndice > 0
? Math.round((c.indice_az||0) / meilleurIndice * 100)
: 0;

return `

<p>

ðŸ‡ NÂ°${c.numero} ${c.nom || ""}

<br>

${c.raison || "Cheval Ã  surveiller"}

<br>

âš¡ ${ecart}% de l'indice du leader â€” capable de crÃ©er la surprise

</p>

`;

}).join("");



   }
    
