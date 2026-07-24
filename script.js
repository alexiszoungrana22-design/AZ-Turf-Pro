async function lancerAnalyse(){

    const resultat = document.getElementById("resultat");

    resultat.innerHTML = `
    <h3>⏳ Analyse en cours...</h3>
    `;


    try {

        const response = await fetch(
            "https://az-turf-pro.onrender.com/analyse?v=" + Date.now()
        );


        const data = await response.json();


        localStorage.setItem(
            "analyseAZ",
            JSON.stringify(data)
        );


        let liste = "";


        data.chevaux.forEach((cheval)=>{

            liste += `

            <li>
            🐎 Cheval n°${cheval.numero}
            <br>
            ⭐ Indice AZ : ${cheval.indice_az}
            <br>
            📊 Confiance : ${cheval.confiance}%
            <br>
            🏷️ ${cheval.type}
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

    catch(error){

        resultat.innerHTML =
        "❌ Erreur connexion AZ";

        console.log(error);

    }

}
