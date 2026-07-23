const API = "https://az-turf-pro.onrender.com/analyse";

const bouton = document.getElementById("btnAnalyse");
const resultat = document.getElementById("resultat");

bouton.addEventListener("click", async () => {

    resultat.innerHTML = "<h2>Analyse en cours...</h2>";

    try{

        const reponse = await fetch(API);
        const data = await reponse.json();

        resultat.innerHTML = `<h2>${data.message}</h2>`;

        data.chevaux.forEach((cheval)=>{

            let classe="outsider";

            if(cheval.type==="Favori AZ"){
                classe="favori";
            }else if(cheval.type==="Chance régulière"){
                classe="chance";
            }

            resultat.innerHTML += `
                <div class="cheval ${classe}">
                    <h3>🏇 Rang ${cheval.rang}</h3>
                    <p><strong>Cheval :</strong> N°${cheval.numero}</p>
                    <p><strong>Indice AZ :</strong> ${cheval.indice_az}</p>
                    <p><strong>Confiance :</strong> ${cheval.confiance}%</p>
                    <p><strong>Type :</strong> ${cheval.type}</p>
                </div>
            `;
        });

    }catch(e){

        resultat.innerHTML=`
            <h2>Erreur</h2>
            <p>Impossible de contacter le serveur AZ Turf Pro.</p>
        `;

    }

});
