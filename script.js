/* =====================================
   AZ TURF PRO - SCRIPT PRINCIPAL
   Connexion API + affichage analyse
===================================== */


document.addEventListener("DOMContentLoaded", function(){


    // Animation cartes

    const cards = document.querySelectorAll(".card, .box");


    cards.forEach(card => {

        card.addEventListener("mouseenter", function(){

            this.style.transform = "translateY(-5px)";

        });


        card.addEventListener("mouseleave", function(){

            this.style.transform = "translateY(0)";

        });

    });



    // Message

    const message = document.querySelector(".message-icon");


    if(message){

        message.addEventListener("click", function(){

            alert(
                "Bienvenue sur AZ Turf Pro.\n\n" +
                "Analyse hippique intelligente et tickets premium."
            );

        });

    }



    // Chargement analyse uniquement sur la page analyse

    if(document.getElementById("table-partants")){

        chargerAnalyse();

    }


});





/* =====================================
   APPEL API AZ TURF PRO
===================================== */


async function chargerAnalyse(){


try{


const response = await fetch("/api/analyse");


if(!response.ok){

throw new Error("Erreur serveur");

}


const data = await response.json();



console.log(
"Analyse AZ :",
data
);



afficherCourse(data);

afficherChevaux(data.chevaux);

afficherFavori(data.favori);

afficherTickets(data.tickets);



}

catch(error){


console.error(error);


}

}






/* =====================================
   INFORMATIONS COURSE
===================================== */


function afficherCourse(data){


const elements = {

"course-nom" :
"🏇 " + (data.course || "Course AZ"),


"hippodrome" :
data.hippodrome || "--",


"discipline" :
data.discipline || "--",


"distance" :
(data.distance_course || "--") + " m",


"partants" :
(data.partants || 0) + " chevaux",


"date-course" :
data.date || "--"


};



for(const id in elements){


const element =
document.getElementById(id);


if(element){

element.textContent = elements[id];

}


}


}








/* =====================================
   TABLEAU CHEVAUX
===================================== */


function afficherChevaux(chevaux){


const tableau =
document.getElementById("table-partants");



if(!tableau){

return;

}



tableau.innerHTML = "";



chevaux.forEach(cheval => {


const ligne =
document.createElement("tr");



ligne.innerHTML = `

<td>${cheval.rang}</td>

<td>${cheval.numero}</td>

<td>${cheval.nom}</td>

<td>${cheval.jockey}</td>

<td>${cheval.entraineur}</td>

<td>${cheval.indice_az}</td>

<td>${cheval.confiance}%</td>

`;



tableau.appendChild(ligne);



});


}








/* =====================================
   FAVORI / BASE / OUTSIDERS
===================================== */


function afficherFavori(favori){


if(!favori){

return;

}



const bloc =
document.getElementById("favori-az");



if(bloc){


bloc.innerHTML = `

N° ${favori.numero}<br>

${favori.nom}<br>

Indice AZ : ${favori.indice_az}<br>

Confiance : ${favori.confiance}%

`;

}


const base =
document.getElementById("base-az");


if(base){


base.textContent =
"N° " + favori.numero +
" - " + favori.nom;

}



}









function afficherTickets(tickets){


if(!tickets){

return;

}



const quinte =
document.getElementById("quinte");


const quarte =
document.getElementById("quarte");


const trio =
document.getElementById("trio");


const couple =
document.getElementById("couple");



if(quinte){

quinte.textContent =
tickets.quinte.join(" - ");

}



if(quarte){

quarte.textContent =
tickets.quarte.join(" - ");

}



if(trio){

trio.textContent =
tickets.trio.join(" - ");

}



if(couple){

couple.textContent =
tickets.couple_gagnant.join(" - ");

}



}
