console.log("AZ Turf-Pro V1 chargé");

const API_URL = "https://az-turf-pro.onrender.com";

const buttons = document.querySelectorAll("button");

buttons.forEach(button => {

    button.addEventListener("click", async () => {

        const result = document.querySelector(".ticket-result");

        result.innerHTML = "Analyse AZ en cours...";

        try {
            const response = await fetch(API_URL);

            const data = await response.json();

            result.innerHTML = `
                <h3>${data.message}</h3>
                <p>Version : ${data.version}</p>
                <p>Connexion Intelligence AZ : OK</p>
            `;

        } catch (error) {

            result.innerHTML =
            "Erreur de connexion au serveur AZ Turf-Pro";

            console.error(error);
        }

    });

});
