const API_URL = "https://az-turf-1.onrender.com";


// Lancer une analyse AZ

async function lancerAnalyse(){

    const resultat = document.getElementById("resultat");

    resultat.innerHTML = `
    <h3>Analyse en cours...</h3>
    <p>⏳ AZ Turf Pro calcule les meilleurs chevaux.</p>
    `;


    try{

        const response = await fetch(API_URL + "/analyse");

        const data = await response.json();


        let chevaux = "";


        if(data.chevaux){

            data.chevaux.forEach((cheval)=>{

                chevaux += `
                <li>
                🐎 ${cheval.nom || cheval}
                </li>
                `;

            });

        }


        resultat.innerHTML = `

        <h3>✅ Résultat AZ</h3>

        <p>
        Analyse terminée.
        </p>

        <ul>
        ${chevaux}
        </ul>

        `;


        sauvegarderHistorique(data);


    }


    catch(error){


        resultat.innerHTML = `

        <h3>❌ Erreur</h3>

        <p>
        Impossible de contacter le serveur AZ Turf.
        </p>

        `;


        console.log(error);

    }


}



// Sauvegarde historique

function sauvegarderHistorique(data){


    let historique =
    JSON.parse(localStorage.getItem("az_historique")) || [];


    historique.push({

        date:new Date().toLocaleDateString(),

        chevaux:
        JSON.stringify(data.chevaux || []),

        indice:
        data.indice || "AZ"

    });


    localStorage.setItem(
        "az_historique",
        JSON.stringify(historique)

    );


}



// Sauvegarde ticket premium

function sauverTicket(){


    let historique =
    JSON.parse(localStorage.getItem("az_historique")) || [];


    historique.push({

        date:new Date().toLocaleDateString(),

        chevaux:
        "1-5-7-10-14-15-16",

        indice:
        "Ticket Premium AZ"

    });


    localStorage.setItem(
        "az_historique",
        JSON.stringify(historique)

    );


    alert(
    "✅ Ticket AZ Premium sauvegardé"
    );


}
