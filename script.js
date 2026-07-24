const API_URL = "https://az-turf-pro.onrender.com";


// Stockage de la dernière analyse
let analyseAZ = null;



// =========================
// LANCER ANALYSE AZ
// =========================

async function lancerAnalyse(){

    const resultat = document.getElementById("resultat");


    if(resultat){

        resultat.innerHTML = `
        <h3>⏳ Analyse en cours...</h3>
        <p>AZ Turf Pro calcule les meilleurs chevaux.</p>
        `;

    }


    try {


        const response = await fetch(
            API_URL + "/analyse"
        );


        const data = await response.json();



        analyseAZ = data;



        localStorage.setItem(
            "analyseAZ",
            JSON.stringify(data)
        );



        let liste = "";



        data.classement.forEach((cheval)=>{


            liste += `

            <li>

            🐎 Cheval n°${cheval.numero}

            <br>

            ⭐ Indice AZ :
            ${cheval.indice_az}

            <br>

            📊 Confiance :
            ${cheval.confiance}%

            <br>

            🏷️ ${cheval.type}

            </li>

            `;


        });



        if(resultat){


            resultat.innerHTML = `


            <h2>
            ✅ Résultat AZ
            </h2>



            <ol>

            ${liste}

            </ol>




            <h3>
            ⭐ Favori AZ
            </h3>



            <p>

            🐎 Cheval n°${data.favori.numero}

            <br>

            Indice :
            ${data.favori.indice_az}

            <br>

            Confiance :
            ${data.favori.confiance}%

            </p>



            `;

        }



        sauvegarderHistorique(data);


    }



    catch(error){


        console.log(error);


        if(resultat){

            resultat.innerHTML = `

            <h3>
            ❌ Erreur
            </h3>

            <p>
            Impossible de contacter AZ Turf Pro.
            </p>

            `;

        }

    }

}




// =========================
// GENERER TICKET PREMIUM
// =========================


function chargerTicket(){


    const data =
    JSON.parse(
        localStorage.getItem("analyseAZ")
    );



    if(!data){


        alert(
        "Lancez d'abord une analyse."
        );


        return;

    }



    const ticket = data.tickets;



    const zone =
    document.getElementById("ticket");



    if(zone){


        zone.innerHTML = `


        <h3>
        🎟️ Ticket AZ Premium
        </h3>



        <p>
        🏆 Quinté :
        <b>
        ${ticket.quinte.join(" - ")}
        </b>
        </p>



        <p>
        🥈 Quarté :
        <b>
        ${ticket.quarte.join(" - ")}
        </b>
        </p>



        <p>
        🥉 Trio :
        <b>
        ${ticket.trio.join(" - ")}
        </b>
        </p>



        <p>
        🔥 Bases :
        <b>
        ${ticket.champ_reduit.bases.join(" - ")}
        </b>
        </p>



        <p>
        ⭐ Compléments :
        <b>
        ${ticket.champ_reduit.complements.join(" - ")}
        </b>
        </p>


        `;

    }

}




// =========================
// HISTORIQUE
// =========================


function sauvegarderHistorique(data){


    let historique =
    JSON.parse(
        localStorage.getItem("historiqueAZ")
    ) || [];



    historique.push(data);



    localStorage.setItem(
        "historiqueAZ",
        JSON.stringify(historique)
    );


}





function afficherHistorique(){


    const zone =
    document.getElementById("historique");



    if(!zone) return;



    let historique =
    JSON.parse(
        localStorage.getItem("historiqueAZ")
    ) || [];



    if(historique.length === 0){

        zone.innerHTML =
        "<p>Aucune analyse enregistrée.</p>";

        return;

    }



    zone.innerHTML = "";



    historique.forEach((data)=>{


        zone.innerHTML += `

        <div class="card">

        📅 Analyse AZ

        <br>

        Favori :
        Cheval n°${data.favori.numero}


        <br>


        Quinté :
        ${data.tickets.quinte.join("-")}


        </div>

        `;


    });


}




window.onload = function(){

    afficherHistorique();

};
