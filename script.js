/* =====================================
   AZ TURF PRO - SCRIPT PRINCIPAL
   Fonctions navigation et affichage
===================================== */


document.addEventListener("DOMContentLoaded", function(){


    // Animation légère des cartes

    const cards = document.querySelectorAll(".card, .box");


    cards.forEach(card => {

        card.addEventListener("mouseenter", function(){

            this.style.transform = "translateY(-5px)";

        });


        card.addEventListener("mouseleave", function(){

            this.style.transform = "translateY(0)";

        });


    });



    // Message utilisateur

    const message = document.querySelector(".message-icon");


    if(message){

        message.addEventListener("click", function(){

            alert(
            "Bienvenue sur AZ Turf Pro.\n\n" +
            "Retrouvez vos analyses spécialisées et vos tickets premium."
            );

        });

    }



    // Mise à jour automatique de l'année du footer

    const footerYear = document.querySelector(".footer-year");


    if(footerYear){

        footerYear.textContent = new Date().getFullYear();

    }



});





/* =====================================
   Préparation connexion API
   Analyse spécialisée
===================================== */


async function chargerAnalyse(){


try{


const reponse = await fetch("/api/analyse");


if(!reponse.ok){

throw new Error("Erreur serveur");

}


const donnees = await reponse.json();


console.log(
"Analyse AZ Turf Pro :",
donnees
);



}
catch(error){


console.log(
"Analyse disponible prochainement"
);


}



}
