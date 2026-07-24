const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";



async function lancerAnalyse(){


    const resultat =
    document.getElementById("resultat");



    if(resultat){

        resultat.innerHTML = `

        <h3>⏳ Analyse AZ en cours...</h3>

        `;

    }



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



        if(resultat){

            resultat.innerHTML = `

            <h3>❌ Erreur connexion AZ</h3>

            `;

        }

    }

}




function afficherAnalyse(data){


    const resultat =
    document.getElementById("resultat");



    if(!resultat){

        return;

    }



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




    resultat.innerHTML = `


    <h2>
    ✅ Analyse AZ terminée
    </h2>



    <h3>
    🏇 ${data.course || "Course AZ"}
    </h3>



    <p>
    📅 Date :
    ${data.date || "Non définie"}
    </p>




    <ol>

    ${liste}

    </ol>




    <h3>
    ⭐ Favori AZ
    </h3>



    🐎 Cheval n°${data.favori.numero}



    `;


}




function chargerTicket(){


    const zone =
    document.getElementById("ticket");



    if(!zone){

        return;

    }



    const data =
    JSON.parse(
        localStorage.getItem("analyseAZ")
    );



    if(!data || !data.tickets){

        zone.innerHTML =
        "⚠️ Aucun ticket disponible";

        return;

    }



    const t =
    data.tickets;



    zone.innerHTML = `


    <h3>
    🎟️ Ticket AZ Premium
    </h3>



    <p>
    🏆 Quinté :
    ${t.quinte.join(" - ")}
    </p>



    <p>
    🏆 Quarté :
    ${t.quarte.join(" - ")}
    </p>



    <p>
    🏆 Trio :
    ${t.trio.join(" - ")}
    </p>



    <p>
    🥇 Couplé gagnant :
    ${t.couple_gagnant.join(" - ")}
    </p>



    <p>
    🥈 Couplé placé :
    ${JSON.stringify(t.couple_place)}
    </p>



    <p>
    🔵 Bases :
    ${t.champ_reduit.bases.join(" - ")}
    </p>



    <p>
    ⚪ Compléments :
    ${t.champ_reduit.complements.join(" - ")}
    </p>


    `;

}




function chargerHistorique(){


    const zone =
    document.getElementById("historique");



    if(!zone){

        return;

    }



    const data =
    JSON.parse(
        localStorage.getItem("analyseAZ")
    );



    if(!data){

        zone.innerHTML =
        "Aucune analyse enregistrée.";

        return;

    }



    zone.innerHTML = `


    <h3>
    ${data.course}
    </h3>


    <p>
    📅 ${data.date}
    </p>


    <p>
    ⭐ Favori :
    Cheval n°${data.favori.numero}
    </p>


    `;

}





document.addEventListener(
"DOMContentLoaded",
()=>{

    chargerHistorique();

    chargerTicket();

});
