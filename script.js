const API_URL = "https://az-turf-pro.onrender.com";

let derniereAnalyse = null;


// Lancer une analyse AZ

async function lancerAnalyse(){

    const resultat = document.getElementById("resultat");

    resultat.innerHTML = `
    <h3>⏳ Analyse en cours...</h3>
    <p>AZ Turf Pro calcule les meilleurs chevaux.</p>
    `;


    try{

        const response = await fetch(API_URL + "/analyse");

        const data = await response.json();

        derniereAnalyse = data;


        let chevaux = "";


        data.chevaux.forEach((cheval)=>{

            chevaux += `
            <li>
                🐎 <b>Cheval n°${cheval.numero}</b>
                <br>
                ⭐ Indice AZ : ${cheval.indice_az}
                <br>
                📊 Confiance : ${cheval.confiance}%
                <br>
                🏷️ ${cheval.type}
            </li>
            <br>
            `;

        });



        resultat.innerHTML = `

        <h3>✅ Résultat AZ Turf</h3>

        <p>
        Classement des 7 chevaux :
        </p>

        <ol>
        ${chevaux}
        </ol>


        <hr>

        <h3>⭐ Favori AZ</h3>

        <p>
        🐎 Cheval n°${data.favori.numero}
        <br>
        Indice : ${data.favori.indice_az}
        <br>
        Confiance : ${data.favori.confiance}%
        </p>


        `;


        sauvegarderHistorique(data);


    }


    catch(error){


        resultat.innerHTML = `

        <h3>❌ Erreur</h3>

        <p>
        Impossible de contacter AZ Turf Pro.
        </p>

        `;


        console.log(error);

    }

}



// Historique

function sauvegarderHistorique(data){


    let historique =
    JSON.parse(localStorage.getItem("az_historique")) || [];


    historique.push({

        date:new Date().toLocaleDateString(),

        classement:data.chevaux,

        tickets:data.tickets

    });


    localStorage.setItem(
        "az_historique",
        JSON.stringify(historique)
    );


}



// Ticket Premium AZ

function afficherTicket(){


    if(!derniereAnalyse){

        alert(
        "Lancez d'abord une analyse AZ."
        );

        return;

    }


    const ticket =
    derniereAnalyse.tickets;


    alert(
`
🎟️ TICKET PREMIUM AZ

Quinté :
${ticket.quinte.join("-")}

Quarté :
${ticket.quarte.join("-")}

Trio :
${ticket.trio.join("-")}

Base :
${ticket.champ_reduit.bases.join("-")}

Compléments :
${ticket.champ_reduit.complements.join("-")}
`
    );

}
