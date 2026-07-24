/* =====================================
   AZ TURF PRO V5
   SCRIPT FRONTEND COMPLET
===================================== */


/* ================================
   CONFIGURATION API
================================ */


const API_URL = "http://127.0.0.1:8000";




// ================================
// LANCER ANALYSE AZ
// ================================


async function lancerAnalyse(){


    const zone = document.getElementById("resultat");


    if(zone){

        zone.innerHTML = `

        <div class="cheval">

        ⏳ Analyse AZ en cours...

        </div>

        `;

    }



    try{


        const response = await fetch(
            `${API_URL}/analyse`
        );



        if(!response.ok){

            throw new Error(
                "Erreur serveur API"
            );

        }



        const data = await response.json();



        afficherResultat(data);



        enregistrerHistorique(data);



    }



    catch(error){



        console.error(error);



        if(zone){

            zone.innerHTML = `

            <div class="cheval">

            ❌ Serveur AZ inaccessible.

            <br><br>

            Vérifiez que l'API FastAPI fonctionne.

            </div>

            `;

        }



    }



}






// ================================
// AFFICHAGE ANALYSE
// ================================


function afficherResultat(data){



const zone = document.getElementById("resultat");



if(!zone){

    return;

}



let html = "";





if(data.chevaux && data.chevaux.length){



html += `

<div class="course-box">

<h2>

🏆 Résultat Analyse AZ

</h2>

</div>

`;





data.chevaux.forEach((cheval)=>{



html += `


<div class="cheval">


<span class="rang">

${cheval.rang || ""}

</span>



<div>


<h3>

🐎 Cheval N° ${cheval.numero}

</h3>


<p>

Indice AZ :

<strong>

${cheval.indice_az}

</strong>

</p>



<p class="confiance">

Confiance :

${cheval.confiance} %

</p>



<p>

${cheval.type || "Sélection AZ"}

</p>


</div>


</div>


`;



});



html += `


<div class="ticket-box">


<h2>

🎟️ Ticket conseillé

</h2>



<div class="ticket-number">

${genererTicket(data)}

</div>


</div>


`;



}

else{


html = `

<div class="cheval">

Aucun résultat disponible.

</div>

`;

}



zone.innerHTML = html;



}






// ================================
// GENERATION TICKET
// ================================


function genererTicket(data){



if(!data.chevaux){

return "N/A";

}



return data.chevaux

.slice(0,5)

.map(

cheval => cheval.numero

)

.join(" - ");



}






// ================================
// HISTORIQUE LOCAL
// ================================


function enregistrerHistorique(data){



let historique = JSON.parse(

localStorage.getItem(
"az_historique"
)

) || [];





historique.unshift({


date:new Date().toLocaleString(),

analyse:data


});





if(historique.length > 30){

historique.pop();

}





localStorage.setItem(

"az_historique",

JSON.stringify(historique)

);



}





// ================================
// AFFICHAGE HISTORIQUE
// ================================


function chargerHistorique(){



const zone = document.getElementById(

"historique"

);



if(!zone){

return;

}




let historique = JSON.parse(

localStorage.getItem(
"az_historique"
)

) || [];





if(historique.length===0){


zone.innerHTML = `

<div class="cheval">

Aucune analyse enregistrée.

</div>

`;

return;


}





let html="";




historique.forEach(item=>{



html += `


<div class="cheval">


<h3>

${item.date}

</h3>


<p>

Ticket AZ enregistré

</p>


</div>


`;



});





zone.innerHTML = html;



}






// ================================
// INITIALISATION
// ================================


document.addEventListener(

"DOMContentLoaded",

()=>{


chargerHistorique();



}

);
