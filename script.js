const API_URL = "https://az-turf-pro.onrender.com";

let derniereAnalyse = null;


// ==========================
// ANALYSE AZ
// ==========================

async function lancerAnalyse(){

    const resultat = document.getElementById("resultat");

    resultat.innerHTML = `
    <h3>⏳ Analyse en cours...</h3>
    <p>AZ Turf Pro calcule les meilleurs chevaux.</p>
    `;


    try {

        const response = await fetch(API_URL + "/analyse");

        const data = await response.json();

        derniereAnalyse = data;


        let chevaux = "";


        data.chevaux.forEach((cheval)=>{

            chevaux += `
            <li>
                🐎 <b>Cheval n°${cheval.numero}</b><br>
                ⭐ Indice AZ : ${cheval.indice_az}<br>
                📊 Confiance : ${cheval.confiance}%<br>
                🏷️ ${cheval.type}
            </li>
            <br>
            `;

        });


        resultat.innerHTML = `

        <h3>✅ Résultat AZ Turf</h3>

        <ol>
        ${chevaux}
        </ol>


        <h3>⭐ Favori AZ</h3>

        <p>
        🐎 Cheval n°${data.favori.numero}<br>
        Indice : ${data.favori.indice_az}<br>
        Confiance : ${data.favori.confiance}%
        </p>

        `;


        sauvegarderHistorique(data);


        localStorage.setItem(
            "derniere_analyse",
            JSON.stringify(data)
        );


    }


    catch(error){

        resultat.innerHTML = `
        <h3>❌ Erreur</h3>
        <p>Impossible de contacter AZ Turf Pro.</p>
        `;

        console.log(error);

    }

}



// ==========================
// AFFICHER TICKET PREMIUM
// ==========================

function chargerTicket(){

    let data =
    JSON.parse(
        localStorage.getItem("derniere_analyse")
    );


    if(!data){

        alert(
        "Lancez d'abord une analyse AZ."
        );

        return;

    }


    let ticket = data.tickets;


    document.getElementById("ticket").innerHTML = `

    <h3>🎟️ Ticket AZ Premium</h3>


    <p>
    🏆 Quinté :
    <b>${ticket.quinte.join(" - ")}</b>
    </p>


    <p>
    🥈 Quarté :
    <b>${ticket.quarte.join(" - ")}</b>
    </p>


    <p>
    🥉 Trio :
    <b>${ticket.trio.join(" - ")}</b>
    </p>


    <p>
    🔥 Bases :
    <b>${ticket.champ_reduit.bases.join(" - ")}</b>
    </p>


    <p>
    ⭐ Compléments :
    <b>${ticket.champ_reduit.complements.join(" - ")}</b>
    </p>

    `;

}



// ==========================
// HISTORIQUE
// ==========================

function sauvegarderHistorique(data){

    let historique =
    JSON.parse(
        localStorage.getItem("az_historique")
    ) || [];


    historique.push({

        date:
        new Date().toLocaleDateString(),

        chevaux:
        data.chevaux,

        tickets:
        data.tickets

    });


    localStorage.setItem(
        "az_historique",
        JSON.stringify(historique)
    );

}



// ==========================
// SAUVEGARDE TICKET
// ==========================

function sauverTicket(){

    let ticket =
    localStorage.getItem(
        "derniere_analyse"
    );


    if(!ticket){

        alert(
        "Aucun ticket disponible."
        );

        return;

    }


    alert(
    "✅ Ticket AZ Premium sauvegardé"
    );

}
