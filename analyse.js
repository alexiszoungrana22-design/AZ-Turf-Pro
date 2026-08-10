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
function afficherInfoCourse(){
    afficher("course-nom", data.course || "Course");
    afficher("course-date", data.date || "-");
    afficher("course-reunion", `${data.reunion || "R?"}${data.course_numero || ""}`);
    afficher("course-hippodrome", data.hippodrome || "Non communiqué par l'API PMU");
    afficher("course-discipline", data.discipline || "-");
    afficher("course-distance", data.distance ? data.distance + " m" : "-");
    afficher("course-partants", data.partants || chevaux.length);
}





// ===============================
// OUTILS AFFICHAGE
// ===============================

function afficher(id,valeur){

const element = document.getElementById(id);

if(element){

element.textContent =
valeur || "-";

}

}




// ===============================
// SELECTION DU JOUR 8 CHEVAUX
// ===============================


const indicesSelection = [0, 2, 4, 6, 8, 10, 12];
const selection = indicesSelection
.map(i => chevaux[i])
.filter(Boolean);



afficher(

"selection-jour",

selection
.map(c=>c.numero)
.join(" - ")

);




afficher(

"bases-solides",

selection
.slice(0,2)
.map(c=>c.numero)
.join(" - ")

);




afficher(

"chances-regulieres",

selection
.slice(2,5)
.map(c=>c.numero)
.join(" - ")

);




afficher(

"outsiders-selection",

selection
.slice(5,8)
.map(c=>c.numero)
.join(" - ")

);








// ===============================
// FAVORI AZ
// ===============================


const favori = chevaux[0];



if(favori){


afficher(

"favori-numero",

favori.numero

);



afficher(

"favori-nom",

favori.nom || "Cheval AZ"

);



afficher(

"favori-indice",

favori.indice_az

);



afficher(

"favori-confiance",

favori.confiance ?
favori.confiance + " %" :
"-"

);



afficher(

"favori-raison",

favori.raison ||
"⭐ Favori AZ : meilleur indice et profil prioritaire"

);


}






// ===============================
// OUTSIDER AZ
// ===============================


const outsider =

chevaux[7] ||
chevaux[6];



if(outsider){


afficher(

"outsider-numero",

outsider.numero

);



afficher(

"outsider-nom",

outsider.nom || "Cheval AZ"

);



afficher(

"outsider-indice",

outsider.indice_az

);



afficher(

"outsider-confiance",

outsider.confiance ?
outsider.confiance + " %" :
"-"

);



afficher(

"outsider-raison",

outsider.raison ||
"🔥 Outsider AZ : profil intéressant pouvant surprendre."

);


}
 // ===============================
// POURQUOI CETTE SELECTION
// ===============================


const raisons =

document.getElementById("raisons-selection");



if(raisons){


raisons.innerHTML =


selection
.map(c => `

<div class="raison-cheval">

<h3>
🏇 N°${c.numero || "-"}
</h3>


<p>

${c.raison ||

"Cheval retenu selon la forme, la régularité et l'indice AZ."}

</p>


</div>

`)
.join("");

}






// ===============================
// TABLEAU ANALYSE DES 8 CHEVAUX
// ===============================


const tableau =

document.getElementById("analyse-body");



if(tableau){


tableau.innerHTML = "";



chevaux
.slice(0,8)
.forEach(cheval => {


tableau.innerHTML += `

<tr>

<td>
${cheval.numero || "-"}
</td>


<td>
${cheval.nom || "Cheval"}
</td>


<td>
${cheval.indice_az || "-"}
</td>


<td>
${cheval.confiance ? cheval.confiance + " %" : "-"}
</td>


<td>
${cheval.raison || "Analyse AZ"}
</td>


</tr>

`;

});


}







// ===============================
// TICKETS GRATUITS
// ===============================


const tickets =

data.tickets?.gratuit || {};





const quinte =

document.getElementById("quinte-gratuit");



if(quinte){


quinte.textContent =

(tickets.quinte || [])
.join(" - ");


}






const deuxSurQuatre =

document.getElementById("deux-sur-quatre");



if(deuxSurQuatre){


deuxSurQuatre.textContent =

(tickets.deux_sur_quatre || [])
.join(" - ");


}







const couplePlace =

document.getElementById("couple-place-gratuit");



if(couplePlace){


couplePlace.textContent =

(tickets.couple_place || [])
.join(" - ");


}






// ===============================
// AVIS COURSE
// ===============================


const avis =

document.getElementById("avis-course");



if(avis){


avis.textContent =

"Les chevaux retenus présentent des profils intéressants selon la forme, l'expérience et les conditions de course.";

}







// ===============================
// ACTUALITES
// ===============================


const actualites =

document.getElementById("actualites-course");



if(actualites){


actualites.textContent =

"Aucune actualité majeure disponible pour le moment.";

}






// ===============================
// SYNTHESE AZ
// ===============================


const synthese =

document.getElementById("synthese-az");



if(synthese){


synthese.textContent =

"La sélection AZ privilégie les chevaux réguliers avec les meilleurs indices de performance.";

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


// ===============================
// COMMENTAIRES VISITEURS
// (affichage local, même logique que
// commentaires.html — non persistant)
// ===============================

document.addEventListener("DOMContentLoaded", function(){

const bouton = document.getElementById("envoyer-message");

if(!bouton){

return;

}

bouton.addEventListener("click", function(){

const champ = document.getElementById("message-visiteur");

const liste = document.getElementById("messages-visiteurs");

const texte = champ ? champ.value.trim() : "";

if(!texte){

return;

}

if(liste){

liste.innerHTML +=
`<p>💬 ${texte}</p>`;

}

if(champ){

champ.value = "";

}

});

});
 
