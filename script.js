const API_URL = "https://az-turf-pro.onrender.com/analyse";


document.addEventListener("DOMContentLoaded", () => {

    const bouton = document.getElementById("analyse");

    if (bouton) {
        bouton.addEventListener("click", lancerAnalyse);
    }

});


async function lancerAnalyse() {

    const chevauxDiv = document.getElementById("chevaux");
    const favoriDiv = document.getElementById("favori");
    const ticketDiv = document.getElementById("ticket");

    if (chevauxDiv) {
        chevauxDiv.innerHTML = "⏳ Analyse AZ en cours...";
    }

    try {

        const reponse = await fetch(API_URL);

        const data = await reponse.json();


        // Affichage favori AZ
        if (favoriDiv && data.favori) {

            favoriDiv.innerHTML = `
                🏆 Cheval favori AZ : <b>${data.favori.numero}</b><br>
                Indice AZ : ${data.favori.indice_az}<br>
                Confiance : ${data.favori.confiance}%
            `;

        }



        // Affichage classement
        if (chevauxDiv && data.classement) {

            chevauxDiv.innerHTML = "";

            data.classement.forEach(cheval => {

                chevauxDiv.innerHTML += `
                    <div class="cheval">
                        <b>Rang ${cheval.rang}</b><br>
                        🐎 Numéro : ${cheval.numero}<br>
                        📊 Indice AZ : ${cheval.indice_az}<br>
                        🎯 Confiance : ${cheval.confiance}%<br>
                        ⭐ ${cheval.type}
                    </div>
                    <hr>
                `;

            });

        }



        // Affichage tickets
        if (ticketDiv && data.tickets) {

            ticketDiv.innerHTML = `

                🎫 <b>Ticket Quinté :</b><br>
                ${data.tickets.quinte.join(" - ")}
                <br><br>

                🎟️ <b>Quarté :</b><br>
                ${data.tickets.quarte.join(" - ")}
                <br><br>

                🔥 <b>Trio :</b><br>
                ${data.tickets.trio.join(" - ")}
                <br><br>

                🏇 <b>Champ réduit :</b><br>
                Bases :
                ${data.tickets.champ_reduit.bases.join(" - ")}
                <br>
                Compléments :
                ${data.tickets.champ_reduit.complements.join(" - ")}

            `;

        }


    } catch (erreur) {

        console.error(erreur);

        if (chevauxDiv) {
            chevauxDiv.innerHTML =
            "❌ Erreur de connexion avec AZ Turf Pro";
        }

    }

}
