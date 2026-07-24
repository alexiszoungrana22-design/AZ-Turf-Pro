/* =====================================
   AZ TURF PRO V6
   SCRIPT INTERACTIF
===================================== */



// ===============================
// CONFIGURATION API
// ===============================

const API_URL = "http://127.0.0.1:8000";





// ===============================
// COMPTE A REBOURS
// ===============================


function lancerCompteARebours(){


    const compteur = document.getElementById("countdown");


    if(!compteur){
        return;
    }


    let temps = 30 * 60;



    setInterval(()=>{


        let heures = Math.floor(temps / 3600);

        let minutes = Math.floor((temps % 3600) / 60);

        let secondes = temps % 60;



        compteur.textContent =

        `${String(heures).padStart(2,"0")}:`+
        `${String(minutes).padStart(2,"0")}:`+
        `${String(secondes).padStart(2,"0")}`;



        if(temps > 0){

            temps--;

        }



    },1000);


}







// ===============================
// LANCER ANALYSE
// ===============================


async function lancerAnalyse(){


    const resultat =
    document.getElementById("resultat");



    if(resultat){

        resultat.innerHTML =

        `
        <div class="cheval">
        ⏳ Analyse spécialisée en cours...
        </div>
        `;

    }




    try{


        const reponse = await fetch(

            `${API_URL}/analyse`

        );



        const donnees = await reponse.json();



        afficherResultats(donnees);

        sauvegarderHistorique(donnees);



    }


    catch(erreur){


        console.log(erreur);



        if(resultat){

            resultat.innerHTML =

            `
            <div class="cheval">
            ❌ Service d'analyse indisponible
            </div>
            `;

        }


    }



}








// ===============================
// AFFICHAGE RESULTATS
// ===============================


function afficherResultats(donnees){



const zone =

document.getElementById("resultat");



if(!zone){

return;

}



let contenu="";





if(donnees.chevaux){



donnees.chevaux
.slice(0,7)
.forEach((cheval,index)=>{



contenu +=


`

<div class="cheval">


<strong>

${index+1} - Cheval N° ${cheval.numero}

</strong>


<p>

Indice de performance :

${cheval.indice_az || cheval.indice}

</p>


<p class="confiance">

Confiance :

${cheval.confiance} %

</p>


<p>

${cheval.type || "Sélection recommandée"}

</p>



</div>


`;



});



}

else{


contenu =

`

<div class="cheval">

Aucun résultat disponible

</div>

`;



}




zone.innerHTML = contenu;



}







// ===============================
// HISTORIQUE
// ===============================


function sauvegarderHistorique(donnees){



let historique =

JSON.parse(

localStorage.getItem("historique_courses")

)

|| [];




historique.unshift({

date:new Date().toLocaleString(),

analyse:donnees

});




if(historique.length > 20){

historique.pop();

}



localStorage.setItem(

"historique_courses",

JSON.stringify(historique)

);



}








function chargerHistorique(){



const zone =

document.getElementById("historique");



if(!zone){

return;

}




let historique =

JSON.parse(

localStorage.getItem("historique_courses")

)

|| [];




if(historique.length===0){


zone.innerHTML =

`

<div class="cheval">

Aucune analyse enregistrée.

</div>

`;

return;

}





zone.innerHTML="";




historique.forEach(item=>{


zone.innerHTML +=


`

<div class="cheval">


<strong>

${item.date}

</strong>


<p>

Analyse spécialisée enregistrée

</p>


</div>


`;



});



}







// ===============================
// DEMARRAGE
// ===============================


document.addEventListener(

"DOMContentLoaded",

()=>{


lancerCompteARebours();


chargerHistorique();


}

);
