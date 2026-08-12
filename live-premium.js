const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/premium/";


document.addEventListener("DOMContentLoaded", verifierAccesPremium);


// =====================================
// VERIFICATION ACCES PREMIUM
// (meme principe que ticket-premium.js)
// =====================================

async function verifierAccesPremium(){

    const telephone =
    localStorage.getItem("AZ_TURF_TELEPHONE");

    const contenu =
    document.getElementById("contenu-premium");

    const blocage =
    document.getElementById("message-blocage");

    if(!telephone){

        if(blocage) blocage.style.display = "block";

        return;

    }

    try{

        const reponse = await fetch(
            API_PREMIUM + encodeURIComponent(telephone)
        );

        const data = await reponse.json();

        if(reponse.ok && data.statut === "ACTIF"){

            if(contenu) contenu.style.display = "block";

            initialiserBoutonToggle();

        }else{

            if(blocage) blocage.style.display = "block";

        }

    }catch(error){

        console.error("Erreur vÃ©rification Premium :", error);

        if(blocage) blocage.style.display = "block";

    }

}


function initialiserBoutonToggle(){
    const btnToggle = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");

    if (btnToggle && conteneurTableau) {
        btnToggle.addEventListener("click", () => {
            if (conteneurTableau.style.display === "none") {
                conteneurTableau.style.display = "block";
                btnToggle.innerHTML = "ðŸ“Š Masquer le Tableau des Partants";
                btnToggle.style.background = "#ef4444"; 

                chargerDonneesLive();
            } else {
                conteneurTableau.style.display = "none";
                btnToggle.innerHTML = "ðŸ“Š Afficher le Tableau des Partants (Live)";
                btnToggle.style.background = "#10b981"; 
            }
        });
    }
}

async function chargerDonneesLive() {
    const tableau = document.getElementById("all-horses");
    if (!tableau) return;

    tableau.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #9ca3af; padding: 15px;">Chargement en cours...</td></tr>`;

    try {
        const reponse = await fetch("https://az-turf-pro.onrender.com/api/analyse"); 
        
        if (!reponse.ok) {
            throw new Error(`Erreur HTTP : ${reponse.status}`);
        }

        const data = await reponse.json();
        const listeCheval = data.classement;

        if (Array.isArray(listeCheval) && listeCheval.length > 0) {
            tableau.innerHTML = "";
            
            listeCheval.forEach(cheval => {
                const rang = cheval.rang ?? "-";
                const numero = cheval.numero ?? "-"; 
                const nom = cheval.nom || "-";
                const indice = (cheval.indice_az !== null && cheval.indice_az !== undefined) ? Math.round(cheval.indice_az) : "-";
                const confiance = (cheval.confiance !== null && cheval.confiance !== undefined) ? cheval.confiance + " %" : "-";

                tableau.innerHTML += `
                    <tr style="border-bottom: 1px solid #374151;">
                        <td style="padding: 12px; color: #fff;"><strong>${rang}</strong></td>
                        <td style="padding: 12px; color: #fff;"><strong>${numero}</strong></td>
                        <td style="padding: 12px; color: #fff;">${nom}</td>
                        <td style="padding: 12px;"><span style="background: #1f2937; padding: 4px 8px; border-radius: 4px; color: #10b981; font-weight: bold;">${indice}</span></td>
                        <td style="padding: 12px; color: #fff;">${confiance}</td>
                    </tr>
                `;
            });
        } else {
            tableau.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #ef4444; padding: 15px;">Le tableau 'classement' est vide.</td></tr>`;
        }
    } catch (erreur) {
        console.error("Erreur attrapÃ©e :", erreur);
        // Affiche l'erreur directement sur ton Ã©cran de tÃ©lÃ©phone pour qu'on sache quoi corriger
        tableau.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #ef4444; padding: 15px;">Erreur : ${erreur.message}</td></tr>`;
    }
}
