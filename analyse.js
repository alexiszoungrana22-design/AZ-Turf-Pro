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

const course = data.course || data.courses || data;


const afficher = (id, valeur) => {

const element = document.getElementById(id);

if(element){
element.textContent = valeur || "-";
}

};


afficher(
"meta-hippodrome",
course.hippodrome || data.hippodrome
);


afficher(
"meta-course",
course.course || course.nom_course || data.course
);


afficher(
"meta-discipline",
course.discipline || data.discipline
);


afficher(
"meta-distance",
course.distance ? course.distance + " m" : data.distance
);


afficher(
"meta-partants",
chevaux.length
);




// ===============================
// PLUS JOUÉS
// ===============================

const popular =
document.getElementById("popular-horses");


if(popular){


const plusJoues =
data.plus_joues ||
course.plus_joues ||
[];


if(plusJoues.length){


popular.innerHTML =
plusJoues
.map(numero =>

`
<div class="popular-number">
${numero}
</div>
`

)
.join("");


}
else{


popular.innerHTML =
"Plus joué indisponible";


}

}





// ===============================
// SELECTION AZ 7 CHEVAUX
// ===============================

const selection =
document.getElementById("selection-az-chevaux");


if(selection){

selection.textContent =
chevaux
.slice(0,7)
.map(c => c.numero)
.join(" - ");

}






// ===============================
// FAVORI AZ
// ===============================

const favori = chevaux[0];


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
numero.textContent = favori.numero || "-";


if(nom)
nom.textContent = favori.nom || "Cheval";


if(indice)
indice.textContent = favori.indice_az || "-";


if(confiance)
confiance.textContent =
(favori.confiance || "-") + " %";


if(raison)
raison.textContent =
"⭐ Base AZ : bonne forme, indice AZ élevé et conditions favorables.";

}






// ===============================
// OUTSIDER AZ
// ===============================

const outsider = chevaux[6];


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
numero.textContent = outsider.numero || "-";


if(nom)
nom.textContent = outsider.nom || "Cheval";


if(indice)
indice.textContent = outsider.indice_az || "-";


if(confiance)
confiance.textContent =
(outsider.confiance || "-") + " %";


if(raison)
raison.textContent =
"🔥 Outsider AZ : profil intéressant pouvant surprendre.";

}






// ===============================
// TABLEAU PARTANTS
// ===============================

const tableau =
document.getElementById("all-horses");


if(tableau){


tableau.innerHTML="";


chevaux.forEach(cheval=>{


tableau.innerHTML += `

<tr>

<td>${cheval.numero || "-"}</td>

<td>${cheval.nom || "Cheval"}</td>

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


const q =
document.getElementById("quinte-gratuit");


if(q){

q.innerHTML =
(tickets.quinte || []).join(" - ");

}


const deux =
document.getElementById("deux-sur-quatre");


if(deux){

deux.innerHTML =
(tickets.deux_sur_quatre || []).join(" - ");

}

// ===============================
// COUPLÉ PLACÉ GRATUIT
// ===============================

const couple = document.getElementById("couple-place-gratuit");

if (couple) {
    couple.innerHTML = (tickets.couple_place || []).join(" - ");
}


// ===============================
// POURQUOI CETTE SÉLECTION
// ===============================

const raisons = document.getElementById("raisons-selection");

if (raisons) {

    raisons.innerHTML = chevaux
        .slice(0,7)
        .map(c => `
            <div class="raison-cheval">
                <h3>🏇 N°${c.numero}</h3>
                <p>${c.raison || "Analyse spécialisée AZ."}</p>
            </div>
        `)
        .join("");

}


// ===============================
// TABLEAU ANALYSE
// ===============================

const analyseBody = document.getElementById("analyse-body");

if (analyseBody) {

    analyseBody.innerHTML = chevaux
        .slice(0,7)
        .map(c => `
            <tr>
                <td>${c.numero}</td>
                <td>${c.nom || "-"}</td>
                <td>${c.indice_az || "-"}</td>
                <td>${c.confiance || "-"}%</td>
                <td>${c.raison || "Analyse AZ"}</td>
            </tr>
        `)
        .join("");

}


// ===============================
// AVIS JOCKEYS / ENTRAÎNEURS
// ===============================

const avis = document.getElementById("avis-course");

if (avis) {

    avis.innerHTML =
        "Les jockeys les plus expérimentés bénéficient de bonnes montes et les entraîneurs présentent plusieurs chevaux en forme.";

}


// ===============================
// ACTUALITÉS
// ===============================

const actualites = document.getElementById("actualites-course");

if (actualites) {

    actualites.innerHTML =
        "Aucune information majeure susceptible de modifier les pronostics pour le moment.";

}


// ===============================
// SYNTHÈSE AZ
// ===============================

const synthese = document.getElementById("synthese-az");

if (synthese) {

    synthese.innerHTML =
        "La sélection AZ privilégie les chevaux les plus réguliers, les mieux engagés et les plus performants selon notre indice.";

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
