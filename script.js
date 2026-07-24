const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";


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




function afficherAnalyse(data){

    const resultat =
    document.getElementById("resultat");


    let liste = "";


    data.chevaux.forEach((cheval)=>{


        liste += `

        <li>

        🐎 <strong>N°${cheval.numero} - ${cheval.nom || ""}</strong>

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



    resultat.innerHTML = `


    <h2>
    ✅ Analyse AZ terminée
    </h2>


    <div class="card">

    🐎 <strong>${data.course}</strong>

    <br><br>

    📅 Date :
    ${data.date}

    <br>

    📍 Hippodrome :
    ${data.hippodrome}

    <br>

    🏇 Réunion :
    ${data.reunion}
    - ${data.course_numero}

    <br>

    🐴 Discipline :
    ${data.discipline}

    <br>

    📏 Distance :
    ${data.distance_course} m

    <br>

    💰 Allocation :
    ${data.allocation}

    <br>

    👥 Partants :
    ${data.partants}

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


    🐎 N°${data.favori.numero}
    - ${data.favori.nom || ""}


    `;

}




function chargerTicket(){

    const zone =
    document.getElementById("ticket");


    if(!zone) return;


    const data =
    JSON.parse(
        localStorage.getItem("analyseAZ")
    );


    if(!data){

        zone.innerHTML =
        "⚠️ Lancez une analyse d'abord.";

        return;

    }


    const t = data.tickets;


    zone.innerHTML = `

    <h3>🎟️ Ticket AZ Premium</h3>

    🏆 Quinté :
    ${t.quinte.join(" - ")}

    <br><br>

    🏆 Quarté :
    ${t.quarte.join(" - ")}

    <br><br>

    🏆 Trio :
    ${t.trio.join(" - ")}

    <br><br>

    🔵 Bases :
    ${t.champ_reduit.bases.join(" - ")}

    <br>

    ⚪ Compléments :
    ${t.champ_reduit.complements.join(" - ")}

    `;

}



document.addEventListener(
"DOMContentLoaded",
()=>{

    chargerTicket();

});
