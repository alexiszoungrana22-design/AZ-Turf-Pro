/* =====================================
   AZ TURF PRO V6
   SCRIPT INTERACTIF PREMIUM
===================================== */



// ===============================
// CONFIGURATION API
// ===============================


// À remplacer par ton URL Render plus tard
const API_URL = "http://127.0.0.1:8000";





// ===============================
// COMPTE A REBOURS
// ===============================


function lancerCompteARebours(){


    const compteur = document.getElementById("countdown");


    if(!compteur){

        return;

    }



    // Exemple : prochain départ dans 30 minutes

    let temps = 30 * 60;



    setInterval(()=>{


        let heures = Math.floor(
            temps / 3600
        );


        let minutes = Math.floor(
            (temps % 3600) / 60
        );


        let secondes = temps % 60;



        compteur.innerHTML =

        `${String(heures).padStart(2,"0")}:`+
        `${String(minutes).padStart(2,"0")}:`+
        `${String(secondes).padStart(2,"0")}`;



        if(temps > 0){

            temps--;

        }



    },1000);



}







// ===============================
// ANALYSE AZ API
// ===============================


async function lancerAnalyse(){


const zone = document.getElementById("resultat");



if(zone){

zone.innerHTML =

`

<div class="cheval">

⏳ Analyse AZ en cours...

</div>

`;

}



try{


const reponse = await fetch(

`${API_URL}/analyse`

);



const data = await reponse.json();



afficherAnalyse(data);



enregistrerHistorique(data);



}



catch(error){


console.log(error);



if(zone){


zone.innerHTML =

`

<div class="cheval">

❌ API AZ indisponible

</div>

`;


}


}



}







// ===============================
// AFFICHAGE RESULTATS
// ===============================


function afficherAnalyse(data){



const zone =
document.getElementById("resultat");



if(!zone){

return;

}



let contenu="";




if(data.chevaux){



data.chevaux
.slice(0,7)
.forEach((cheval,index)=>{



contenu +=


`

<div class="cheval">


<strong>

${index+1} - N° ${cheval.numero}

</strong>


<p>

Indice AZ :
${cheval.indice_az}

</p>


<p class="confiance">

Confiance :
${cheval.confiance} %

</p>


<p>

${cheval.type || "Sélection AZ"}

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


function enregistrerHistorique(data){



let historique =

JSON.parse(

localStorage.getItem(
"az_historique"
)

) || [];




historique.unshift({

date:
new Date().toLocaleString(),

resultat:data

});




if(historique.length > 20){

historique.pop();

}




localStorage.setItem(

"az_historique",

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

localStorage.getItem(
"az_historique"
)

) || [];




if(historique.length===0){


zone.innerHTML =

`

<div class="cheval">

Aucune analyse enregistrée

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

Analyse AZ enregistrée

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
