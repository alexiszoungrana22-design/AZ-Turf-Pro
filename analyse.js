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
// INFORMATIONS COURSE
// ===============================


const course =
data.course ||
data.courses ||
data;



const afficher = (id,valeur)=>{

const element =
document.getElementById(id);


if(element){

element.textContent =
valeur || "-";

}

};




afficher(
"meta-hippodrome",
course.hippodrome || data.hippodrome
);



afficher(
"meta-course",
course.course ||
course.nom_course ||
data.course
);



afficher(
"meta-discipline",
course.discipline ||
data.discipline
);



afficher(
"meta-distance",
course.distance ?
course.distance + " m" :
data.distance
);



afficher(
"meta-partants",
chevaux.length
);





// ===============================
// SELECTION DU JOUR 8 CHEVAUX
// ===============================


const selectionJour =
document.getElementById("selection-jour");


if(selectionJour){


selectionJour.textContent =

chevaux
.slice(0,8)
.map(c=>c.numero)
.join(" - ");


}





// ===============================
// REPARTITION SELECTION
// 2 BASES - 3 CHANCES - 3 OUTSIDERS
// ===============================


const bases =
document.getElementById("bases-solides");


if(bases){


bases.textContent =

chevaux
.slice(0,2)
.map(c=>c.numero)
.join(" - ");


}




const chances =
document.getElementById("chances-regulieres");


if(chances){


chances.textContent =

chevaux
.slice(2,5)
.map(c=>c.numero)
.join(" - ");


}




const outsiders =
document.getElementById("outsiders-selection");


if(outsiders){


outsiders.textContent =

chevaux
.slice(5,8)
.map(c=>c.numero)
.join(" - ");


}






// ===============================
// FAVORI AZ
// ===============================


const favori =
chevaux[0];



if(favori){


const numero =
document.getElementById("favori-numero");


const nom =
document.getElementById("favori-nom");


const indice =
document.getElementById("favori-indice");


const confiance =
document.getElementById("favori-confiance");


const raison =
document.getElementById("favori-raison");



if(numero)
numero.textContent =
favori.numero || "-";



if(nom)
nom.textContent =
favori.nom || "Cheval";



if(indice)
indice.textContent =
favori.indice_az || "-";



if(confiance)
confiance.textContent =
(favori.confiance || "-") + " %";



if(raison)
raison.textContent =

favori.raison ||
"⭐ Base AZ : cheval régulier avec un indice AZ élevé.";

}




// ===============================
// OUTSIDER AZ (8ème cheval)
// ===============================


const outsider =

chevaux[7] ||
chevaux[6];



if(outsider){


const numero =
document.getElementById("outsider-numero");


const nom =
document.getElementById("outsider-nom");


const indice =
document.getElementById("outsider-indice");


const confiance =
document.getElementById("outsider-confiance");


const raison =
document.getElementById("outsider-raison");



if(numero)
numero.textContent =
outsider.numero || "-";



if(nom)
nom.textContent =
outsider.nom || "Cheval";



if(indice)
indice.textContent =
outsider.indice_az || "-";



if(confiance)
confiance.textContent =
(outsider.confiance || "-") + " %";



if(raison)
raison.textContent =

outsider.raison ||

"🔥 Outsider AZ : cheval capable de créer une surprise.";


}

 // ===============================
// POURQUOI CETTE SELECTION
// ===============================


const raisons =
document.getElementById("raisons-selection");


if(raisons){


raisons.innerHTML =

chevaux
.slice(0,8)
.map(c=>`

<div class="raison-cheval">

<h3>
🏇 N°${c.numero || "-"}
</h3>

<p>
${c.raison ||
"Cheval retenu pour sa forme, sa régularité et ses conditions de course favorables."}
</p>

</div>

`)
.join("");

}






// ===============================
// TABLEAU ANALYSE DES 8 CHEVAUX
// ===============================


const analyseBody =
document.getElementById("analyse-body");



if(analyseBody){


analyseBody.innerHTML =

chevaux
.slice(0,8)
.map(c=>`

<tr>

<td>
${c.numero || "-"}
</td>


<td>
${c.nom || "Cheval"}
</td>


<td>
${c.indice_az || "-"}
</td>


<td>
${c.confiance || "-"}%
</td>


<td>
${c.raison ||
"Analyse spécialisée AZ."}
</td>


</tr>

`)
.join("");

}







// ===============================
// TICKETS GRATUITS
// ===============================


const tickets =

data.tickets?.gratuit || {};




const ticket24 =

document.getElementById("ticket-24-gratuit");



if(ticket24){


ticket24.textContent =

(tickets.deux_sur_quatre || [])
.join(" - ");


}





const couple =

document.getElementById("couple-place-gratuit");



if(couple){


couple.textContent =

(tickets.couple_place || [])
.join(" - ");


}







// ===============================
// CHEVAUX A SURVEILLER
// ===============================


const surveiller =

document.getElementById("chevaux-surveiller");



if(surveiller){


surveiller.innerHTML =

chevaux
.slice(5,8)
.map(c=>

`🏇 N°${c.numero} - ${c.nom || "Cheval"}`

)
.join("<br>");

}







// ===============================
// AVIS JOCKEYS
// ===============================


const avis =

document.getElementById("avis-course");



if(avis){


avis.textContent =

"Les chevaux retenus présentent des profils intéressants selon la forme, l'expérience des jockeys et les conditions de course.";


}






// ===============================
// ACTUALITES
// ===============================


const actualites =

document.getElementById("actualites-course");



if(actualites){


actualites.textContent =

"Aucune information majeure ne modifie actuellement l'analyse de la course.";

}







// ===============================
// TENDANCE COURSE
// ===============================


const tendance =

document.getElementById("tendance-course");



if(tendance){


tendance.textContent =

"La course présente un équilibre entre favoris, chevaux réguliers et outsiders capables de surprendre.";

}







// ===============================
// SYNTHESE AZ
// ===============================


const synthese =

document.getElementById("synthese-az");



if(synthese){


synthese.textContent =

"La sélection AZ privilégie les chevaux les plus réguliers, les mieux engagés et ceux ayant les meilleurs indices de performance.";

}







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
