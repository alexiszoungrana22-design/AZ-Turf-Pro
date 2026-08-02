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
// PLUS JOUÉS
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
"Plus joué indisponible";

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
🔥 Chevaux les plus joués :
<strong>
${(data.plus_joues || []).join(" - ")}
</strong>
</p>


<p>
⭐ Favori AZ :
<strong>
N°${chevaux[0].numero}
</strong>
avec un indice AZ de
<strong>
${chevaux[0].indice_az || "-"}
</strong>
</p>


<p>
📊 La tendance est basée sur la forme, la régularité et le classement AZ.
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
"⭐ Favori AZ"
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
"🔥 Outsider AZ"
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
