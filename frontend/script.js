const API = "https://az-turf-pro.onrender.com/analyse";

const bouton = document.getElementById("btnAnalyse");
const resultat = document.getElementById("resultat");

bouton.addEventListener("click", async () => {

    resultat.innerHTML = "⏳ Analyse en cours...";

    try {

        const reponse = await fetch(API);
        const data = await reponse.json();

        resultat.innerHTML = `
            <h2>${data.message}</h2>
        `;

        data.chevaux.forEach(cheval => {

            let classe = "";

            if(cheval.type === "Favori AZ"){
                classe = "favori";
            }
            else if(cheval.type === "Chance régulière"){
                classe = "chance";
            }
            else{
                classe = "outsider";
            }

            resultat.innerHTML += `
                <div class="cheval ${classe}">
                    <h3>🏇 Rang ${cheval.rang} - Cheval N°${cheval.numero}</h3>
                    <p>Indice AZ : <b>${cheval.indice_az}</b></p>
                    <p>Confiance : <b>${cheval.confiance}%</b></p>
                    <p>${cheval.type}</p>
                </div>
            `;

        });

    } catch(error){

        resultat.innerHTML =
        "❌ Erreur de connexion avec AZ Turf Pro";

    }

});
