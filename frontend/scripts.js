console.log("AZ Turf-Pro connecté");

const API_URL = "https://az-turf-pro.onrender.com/pronostic";

async function chargerPronostic() {

    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        // Affichage des 7 chevaux
        const selection = document.getElementById("selection");

        selection.innerHTML = "";

        data.selection.forEach(cheval => {
            selection.innerHTML += `
                <div class="horse">
                    ${cheval.numero} - Cheval AZ
                    <span>${cheval.indice}</span>
                </div>
            `;
        });


        // Base AZ
        document.getElementById("base").innerHTML = data.base;


        // Outsider AZ
        document.getElementById("outsider").innerHTML = data.outsider;


        // Ticket
        document.querySelector(".ticket-result").innerHTML =
            data.ticket;


    } catch (error) {

        console.error("Erreur AZ Turf-Pro :", error);

    }
}


// Chargement automatique
chargerPronostic();
