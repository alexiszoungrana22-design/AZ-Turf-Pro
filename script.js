const API_URL = "https://az-turf-pro.onrender.com/api/analyse";


// Lancer analyse

async function lancerAnalyse(){

    const resultat =
    document.getElementById("resultat");


    resultat.innerHTML = `
    <h3>⏳ Analyse AZ en cours...</h3>
    `;


    try{

        const response = await fetch(
            API_URL + "?v=" + Date.now()
        );


        const data =
        await response.json();


        localStorage.setItem(
            "analyseAZ",
            JSON.stringify(data)
        );


        afficherAnalyse(data);


    }catch(error){

        console.log(error);

        resultat.innerHTML = `
        <h3>❌ Erreur connexion AZ</h3>
        `;

    }

}



// Affichage analyse

function afficherAnalyse(data){


    const resultat =
    document.getElementById("resultat");


    let liste = "";


    data.chevaux.forEach((cheval)=>{


        liste += `

        <li>

        🐎 <strong>N°${cheval.numero} - ${cheval.nom}</strong>

        <br><br>

        👤 Jockey :
        ${cheval.jockey || "Non renseigné"}

        <br>

        🏠 Entraîneur :
        ${cheval.entraineur || "Non renseigné"}

        <br>

        📈 Performances :
        ${
            cheval.performances
            ?
            cheval.performances.join(" - ")
            :
            "Non renseignées"
        }

        <br><br>

        ⭐ Indice AZ :
        ${cheval.indice_az}

        <br>

        📊 Confiance :
        ${cheval.confiance} %

        <br>

        🏷️ ${cheval.type}

        </li>

        `;

    });



    resultat.innerHTML = `


    <h2>
    ✅ Analyse AZ terminée
    </h2>



    <div class="card course-card">

    🐎 <strong>
    ${data.course}
    </strong>

    <br>

    📅 Date :
    ${data.date}

    <br>

    📍 Hippodrome :
    ${data.hippodrome || "Non renseigné"}

    <br>

    🏇 Réunion :
    ${data.reunion || ""}
    ${data.course_numero || ""}

    <br>

    🐴 Discipline :
    ${data.discipline || "Non renseignée"}

    <br>

    📏 Distance :
    ${data.distance_course || 0} m

    <br>

    💰 Allocation :
    ${data.allocation || 0}

    <br>

    👥 Partants :
    ${data.partants || data.chevaux.length}


    </div>



    <h3>
    📊 Classement AZ
    </h3>


    <ol>

    ${liste}

    </ol>



    <div class="favori">


    ⭐ <strong>Favori AZ</strong>


    <br><br>


    🐎 N°${data.favori.numero}

    - ${data.favori.nom}


    <br>

    ⭐ Indice :
    ${data.favori.indice_az}


    </div>


    `;


}




// Ticket premium

function chargerTicket(){


    const zone =
    document.getElementById("ticket");


    if(!zone) return;



    const sauvegarde =
    localStorage.getItem("analyseAZ");



    if(!sauvegarde){

        return;

    }



    const data =
    JSON.parse(sauvegarde);



    const ticket =
    data.tickets;



    zone.innerHTML = `


    <div class="ticket">


    🎟️ <strong>Ticket AZ Premium</strong>


    <br><br>


    🏆 Quinté :
    ${ticket.quinte.join(" - ")}


    <br><br>


    🏆 Quarté :
    ${ticket.quarte.join(" - ")}


    <br><br>


    🏆 Trio :
    ${ticket.trio.join(" - ")}


    <br><br>


    🟢 Couplé gagnant :
    ${ticket.couple_gagnant.join(" - ")}


    <br><br>


    🔵 Couplé placé :

    ${
        ticket.couple_place
        .map(c=>c.join("-"))
        .join(" / ")
    }


    <br><br>


    🔴 Bases :

    ${ticket.champ_reduit.bases.join(" - ")}


    <br>

    ⚪ Compléments :

    ${ticket.champ_reduit.complements.join(" - ")}


    </div>


    `;


}




function sauverTicket(){

    alert(
        "✅ Ticket AZ sauvegardé"
    );

}



document.addEventListener(
"DOMContentLoaded",
()=>{

    chargerTicket();

});
