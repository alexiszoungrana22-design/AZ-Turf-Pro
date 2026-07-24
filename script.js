const API_URL = "https://az-turf-pro.onrender.com/api/analyse";


// Lancer analyse AZ

async function lancerAnalyse() {

    const resultat = document.getElementById("resultat");


    resultat.innerHTML = `
    <h3>⏳ Analyse AZ en cours...</h3>
    `;


    try {

        const response = await fetch(
            API_URL + "?v=" + Date.now()
        );


        const data = await response.json();


        localStorage.setItem(
            "analyseAZ",
            JSON.stringify(data)
        );


        afficherAnalyse(data);


    } catch(error) {

        console.log(error);

        resultat.innerHTML = `
        <h3>❌ Erreur connexion AZ</h3>
        `;

    }

}




// Affichage analyse

function afficherAnalyse(data) {


    const resultat =
    document.getElementById("resultat");


    let liste = "";


    data.chevaux.forEach((cheval)=>{


        liste += `

        <li>

        🐎 <strong>Cheval n°${cheval.numero}</strong>

        <br>

        🏇 Nom :
        ${cheval.nom || "Non renseigné"}

        <br>

        👤 Jockey :
        ${cheval.jockey || "Non renseigné"}

        <br>

        🏠 Entraîneur :
        ${cheval.entraineur || "Non renseigné"}

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



    const nombrePartants =
    data.partants || data.chevaux.length;



    resultat.innerHTML = `


    <h2>
    ✅ Analyse AZ terminée
    </h2>



    <div class="card">


    🐎 <strong>
    ${data.course || "Course AZ"}
    </strong>


    <br><br>


    📅 Date :
    ${data.date || "Non renseignée"}


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
    ${nombrePartants}


    </div>



    <h3>
    📊 Classement AZ
    </h3>


    <ol>

    ${liste}

    </ol>



    <h3>
    ⭐ Favori AZ
    </h3>


    🐎 Cheval n°${data.favori.numero || ""}

    ${data.favori.nom || ""}


    `;

}





// Charger ticket premium

function chargerTicket() {


    const zone =
    document.getElementById("ticket");


    if(!zone) return;



    const sauvegarde =
    localStorage.getItem("analyseAZ");



    if(!sauvegarde) {


        zone.innerHTML = `
        ⚠️ Lancez une analyse d'abord.
        `;


        return;

    }



    const data =
    JSON.parse(sauvegarde);



    const ticket =
    data.tickets;



    zone.innerHTML = `


    <h3>
    🎟️ Ticket AZ Premium
    </h3>


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

    ${ticket.couple_place
    .map(c => c.join("-"))
    .join(" / ")}


    <br><br>


    🔴 Bases :

    ${ticket.champ_reduit.bases.join(" - ")}


    <br>


    ⚪ Compléments :

    ${ticket.champ_reduit.complements.join(" - ")}


    `;

}





// Sauvegarde ticket

function sauverTicket(){

    const data =
    localStorage.getItem("analyseAZ");


    if(data){

        alert(
            "✅ Ticket AZ sauvegardé"
        );

    } else {

        alert(
            "⚠️ Aucun ticket disponible"
        );

    }

}




document.addEventListener(
"DOMContentLoaded",
()=>{

    chargerTicket();

});
