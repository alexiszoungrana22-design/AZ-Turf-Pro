/* =====================================
   AZ TURF PRO V3
   SCRIPT PRINCIPAL
===================================== */


// =============================
// CONFIGURATION API
// =============================

// Remplace cette adresse par ton URL Render quand le backend sera en ligne
const API_URL = "http://127.0.0.1:8000";



// =============================
// SPLASH SCREEN
// =============================

window.addEventListener("load", () => {

    const splash = document.getElementById("splash");

    if(splash){

        setTimeout(() => {

            splash.style.display = "none";

        },3000);

    }

});




// =============================
// ANALYSE AZ
// =============================


async function lancerAnalyse(){


    const resultat = document.getElementById("resultat");


    if(resultat){

        resultat.innerHTML = `
        <div class="card">
        ⏳ Analyse AZ en cours...
        </div>
        `;

    }



    try{


        const response = await fetch(
            `${API_URL}/analyse`
        );



        if(!response.ok){

            throw new Error("Erreur API");

        }



        const data = await response.json();



        afficherAnalyse(data);



        sauvegarderHistorique(data);



    }

    catch(error){


        if(resultat){

            resultat.innerHTML = `

            <div class="card">

            ❌ Impossible de contacter le serveur AZ.

            <br><br>

            Vérifie que l'API FastAPI est démarrée.

            </div>

            `;

        }


        console.error(error);


    }


}




// =============================
// AFFICHAGE RESULTATS
// =============================


function afficherAnalyse(data){


const resultat = document.getElementById("resultat");


if(!resultat){

    return;

}



let html = `


<div class="card">

<h2>🏇 Analyse AZ terminée</h2>


</div>


`;



if(data.chevaux){



data.chevaux.forEach(cheval => {



html += `


<div class="cheval-card">


<h3>

${cheval.rang || ""} -
Cheval N° ${cheval.numero}

</h3>


<p>

Indice AZ :
<span class="indice">

${cheval.indice_az}

</span>

</p>


<p>

Confiance :

<span class="confiance">

${cheval.confiance} %

</span>


</p>


<p>

${cheval.type || "Sélection AZ"}

</p>


</div>


`;



});



}



html += `


<div class="ticket">


<h2>🎟️ Ticket conseillé AZ</h2>


<p>

${genererTicket(data)}

</p>


</div>


`;



resultat.innerHTML = html;



}



// =============================
// GENERATION TICKET
// =============================


function genererTicket(data){


if(!data.chevaux){

    return "Aucun ticket disponible";

}



return data.chevaux

.slice(0,5)

.map(c => c.numero)

.join(" - ");



}




// =============================
// HISTORIQUE LOCAL
// =============================


function sauvegarderHistorique(data){



let historique = JSON.parse(

localStorage.getItem("az_historique")

) || [];



historique.unshift({

date:new Date().toLocaleString(),

data:data

});



if(historique.length > 20){

historique.pop();

}



localStorage.setItem(

"az_historique",

JSON.stringify(historique)

);



}



// =============================
// AFFICHAGE HISTORIQUE
// =============================


function afficherHistorique(){


const zone = document.getElementById("historique");


if(!zone){

return;

}



let historique = JSON.parse(

localStorage.getItem("az_historique")

) || [];



if(historique.length===0){


zone.innerHTML = `

<div class="card">

Aucune analyse enregistrée.

</div>

`;

return;


}




let html="";



historique.forEach(item=>{


html += `

<div class="card">


<h3>

${item.date}

</h3>


<p>

Analyse AZ enregistrée

</p>


</div>


`;



});



zone.innerHTML=html;



}



// =============================
// BOUTON ANALYSE
// =============================


document.addEventListener(

"DOMContentLoaded",

()=>{


const bouton = document.getElementById(

"btnAnalyse"

);



if(bouton){


bouton.addEventListener(

"click",

lancerAnalyse

);


}



afficherHistorique();



}

);
