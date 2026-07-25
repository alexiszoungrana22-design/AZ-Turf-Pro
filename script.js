/* =====================================
   AZ TURF PRO - SCRIPT API
   Connexion frontend / backend
===================================== */


document.addEventListener("DOMContentLoaded", function(){


    // Animation des cartes

    const cards = document.querySelectorAll(".card, .box");


    cards.forEach(card => {

        card.addEventListener("mouseenter", function(){

            this.style.transform = "translateY(-5px)";

        });


        card.addEventListener("mouseleave", function(){

            this.style.transform = "translateY(0)";

        });

    });



    // Bouton message

    const message = document.querySelector(".message-icon");


    if(message){

        message.addEventListener("click", function(){

            alert(
                "Bienvenue sur AZ Turf Pro.\n\n" +
                "Votre analyse hippique intelligente."
            );

        });

    }



    // Charger automatiquement l'analyse

    if(document.querySelector(".table-container")){

        chargerAnalyse();

    }


});





/* =====================================
   CONNEXION API AZ TURF PRO
===================================== */


async function chargerAnalyse(){


try{


const reponse = await fetch("/api/analyse");



if(!reponse.ok){

throw new Error("Erreur API");

}



const data = await reponse.json();



console.log(
"Résultat AZ Turf Pro :",
data
);



afficherCourse(data);

afficherPartants(data.chevaux);

afficherFavori(data.favori);

afficherTickets(data.tickets);



}

catch(error){


console.error(error);


console.log(
"Impossible de charger l'analyse AZ Turf"
);


}



}





/* =====================================
   AFFICHAGE COURSE
===================================== */


function afficherCourse(data){


const titre = document.querySelector(".course-card h2");


if(titre && data.course){

titre.textContent = "🏇 " + data.course;

}



const infos =
document.querySelectorAll(".course-info span");



if(infos.length >= 3){


infos[2].textContent =
(data.partants || 0) + " chevaux";


}


}





/* =====================================
   TABLEAU DES CHEVAUX
===================================== */


function afficherPartants(chevaux){


const tableau =
document.querySelector("tbody");



if(!tableau || !chevaux){

return;

}



tableau.innerHTML = "";



chevaux.forEach(cheval => {



const ligne =
document.createElement("tr");



ligne.innerHTML = `

<td>${cheval.numero ?? ""}</td>

<td>${cheval.nom ?? ""}</td>

<td>${cheval.jockey ?? ""}</td>

<td>${cheval.entraineur ?? ""}</td>

<td>${cheval.confiance ?? ""}%</td>

<td>${cheval.indice_az ?? ""}</td>

`;



tableau.appendChild(ligne);



});



}







/* =====================================
   FAVORI AZ
===================================== */


function afficherFavori(favori){


const bloc =
document.querySelector(".favorite p");



if(bloc && favori){


bloc.innerHTML = `

Cheval N° ${favori.numero ?? "-"} 

<br>

${favori.nom ?? ""}

<br>

Indice AZ :
${favori.indice_az ?? "-"}

`;

}



}







/* =====================================
   TICKETS
===================================== */


function afficherTickets(tickets){


const zone =
document.querySelector(
"section.welcome:last-child"
);



if(!zone || !tickets){

return;

}



zone.innerHTML = `

<h2>🎟 Sélection conseillée</h2>


<p>
Quinté :
<strong>
${JSON.stringify(tickets)}
</strong>
</p>


`;



}
