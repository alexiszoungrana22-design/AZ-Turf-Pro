const API_URL = "https://az-turf-pro.onrender.com";

const result = document.getElementById("result");
const button = document.getElementById("generate");

if (button) {
    button.addEventListener("click", async () => {
        result.innerHTML = "Analyse en cours...";

        try {
            const response = await fetch(API_URL + "/pronostic");

            const data = await response.json();

            result.innerHTML = `
                <h3>🏇 Pronostic AZ-Turf-Pro</h3>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;

        } catch (error) {
            result.innerHTML = 
            "❌ Impossible de contacter le serveur AZ-Turf-Pro";
            console.error(error);
        }
    });
}
