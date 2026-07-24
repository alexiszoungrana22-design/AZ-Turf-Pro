const API_URL = "https://az-turf-pro.onrender.com/api/analyse";


// ===============================
// LANCER ANALYSE AZ
// ===============================

async function lancerAnalyse(){

    const resultat = document.getElementById("resultat");


    if(resultat){

        resultat.innerHTML = `
            <h3>⏳ Analyse AZ en cours...</h3>
            <p>Connexion au moteur AZ Turf Pro...</p>
        `;

    }


    try {


        const response = await fetch(
            API_URL + "?v=" + Date.now()
        );



        if(!response.ok){

            throw new Error(
                "Erreur serveur : " + response.status
            );

        }



        const data = await response.json();



        localStorage.setItem(
            "analyseAZ",
            JSON.stringify(data)
        );



        afficherAnalyse(data);



    }


    catch(error){


        console.error(error);



        if(resultat){

            resultat.innerHTML = `

            <h3>❌ Erreur AZ Turf Pro</h3>

            <p>
            Impossible de contacter le serveur Render.
            </p>

            `;

        }

    }

}




// ===============================
// AFFICHAGE RESULTAT ANALYSE
// ===============================


function afficherAnalyse(data){


    const resultat = document.getElementById("resultat");



    if(!resultat){

        return;

    }



    if(!data.chevaux || data.chevaux.length === 0){


        resultat.innerHTML = `

        <h3>⚠️ Aucun résultat</h3>

        `;


        return;

    }




    let liste = "";



    data.chevaux.forEach((cheval)=>{


        liste += `

        <li>

        🐎 <strong>Cheval n°${cheval.numero}</strong>

        <br>

        ⭐ Indice AZ : ${cheval.indice_az}

        <br>

        📊 Confiance : ${cheval.confiance}%

        <br>

        🏷️ Type : ${cheval.type}

        </li>

        `;


    });





    resultat.innerHTML = `


    <h2>✅ Analyse AZ terminée</h2>


    <ol>

    ${liste}

    </ol>



    <h3>⭐ Favori AZ</h3>


    🐎 Cheval n°${data.favori.numero}



    `;


}





// ===============================
// CHARGER TICKET PREMIUM
// ===============================


function chargerTicket(){



    const zone = document.getElementById("ticket");



    if(!zone){

        return;

    }




    const data = JSON.parse(

        localStorage.getItem("analyseAZ")

    );





    if(!data || !data.tickets){



        zone.innerHTML = `


        <h3>⚠️ Aucun ticket disponible</h3>


        <p>

        Lancez une analyse avant de générer un ticket.

        </p>


        `;



        return;


    }





    const tickets = data.tickets;





    zone.innerHTML = `



    <h3>🎟️ Ticket AZ Premium</h3>


    <p>
    🏆 <strong>Quinté :</strong>
    ${tickets.quinte.join(" - ")}
    </p>


    <p>
    🏆 <strong>Quarté :</strong>
    ${tickets.quarte.join(" - ")}
    </p>


    <p>
    🏆 <strong>Trio :</strong>
    ${tickets.trio.join(" - ")}
    </p>


    <p>
    🔵 <strong>Bases :</strong>
    ${tickets.champ_reduit.bases.join(" - ")}
    </p>


    <p>
    ⚪ <strong>Compléments :</strong>
    ${tickets.champ_reduit.complements.join(" - ")}
    </p>


    `;



}




// ===============================
// SAUVEGARDER TICKET
// ===============================


function sauverTicket(){



    const data = localStorage.getItem(
        "analyseAZ"
    );



    if(data){


        localStorage.setItem(
            "ticketAZ",
            data
        );



        alert(
            "✅ Ticket AZ sauvegardé"
        );



    }

    else{


        alert(
            "⚠️ Aucun ticket à sauvegarder"
        );


    }


}





// ===============================
// HISTORIQUE
// ===============================


function chargerHistorique(){



    const zone = document.getElementById(
        "historique"
    );



    if(!zone){

        return;

    }





    const data = JSON.parse(

        localStorage.getItem("analyseAZ")

    );





    if(!data || !data.chevaux){


        zone.innerHTML = `

        <p>
        Aucune analyse enregistrée.
        </p>

        `;


        return;


    }





    let liste = "";



    data.chevaux.forEach((cheval)=>{


        liste += `

        <li>

        🐎 Cheval n°${cheval.numero}

        |

        ⭐ ${cheval.indice_az}

        |

        📊 ${cheval.confiance}%

        </li>

        `;


    });





    zone.innerHTML = `



    <h3>📜 Dernière analyse AZ</h3>


    <ol>

    ${liste}

    </ol>


    <h3>⭐ Favori</h3>


    🐎 Cheval n°${data.favori.numero}



    `;



}





// ===============================
// INITIALISATION AUTOMATIQUE
// ===============================


document.addEventListener(
    "DOMContentLoaded",
    ()=>{


        chargerHistorique();


        const ticket = document.getElementById(
            "ticket"
        );


        if(ticket){

            chargerTicket();

        }


    }
);
