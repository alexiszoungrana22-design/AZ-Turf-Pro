const API_URL = "https://az-turf-pro.onrender.com/analyse";


document.addEventListener("DOMContentLoaded", function () {

    const boutonAnalyse = document.getElementById("analyse");

    if (boutonAnalyse) {
        boutonAnalyse.onclick = lancerAnalyse;
    }

});


async function lancerAnalyse() {

    const chevaux = document.getElementById("chevaux");
    const favori = document.getElementById("favori");
    const ticket = document.getElementById("ticket");


    if (chevaux) {
        chevaux.innerHTML = "⏳ Analyse AZ en cours...";
    }


    try {

        const response = await fetch(API_URL);

        const data = await response.json();


        console.log(data);



        // FAVORI AZ

        if (favori && data.favori) {

            favori.innerHTML = `
            🏆 Favori AZ<br><br>
            🐎 Cheval n°${data.favori.numero}<br>
            📊 Indice AZ : ${data.favori.indice_az}<br>
            🎯 Confiance : ${data.favori.confiance}%<br>
            ⭐ ${data.favori.type}
            `;

        }



        // CLASSEMENT

        if (chevaux && data.classement) {

            chevaux.innerHTML = "";

            data.classement.forEach(c => {

                chevaux.innerHTML += `

                <div class="cheval">

                <h3>
                Rang ${c.rang} - 🐎 N°${c.numero}
                </h3>

                <p>
                Indice AZ : <b>${c.indice_az}</b><br>
                Confiance : <b>${c.confiance}%</b><br>
                Type : ${c.type}
                </p>

                </div>

                `;

            });

        }



        // TICKETS

        if (ticket && data.tickets) {


            ticket.innerHTML = `

            🎫 <h3>Ticket Premium AZ</h3>


            Quinté :
            <b>${data.tickets.quinte.join(" - ")}</b>

            <br><br>

            Quarté :
            <b>${data.tickets.quarte.join(" - ")}</b>

            <br><br>

            Trio :
            <b>${data.tickets.trio.join(" - ")}</b>

            <br><br>

            Champ réduit :

            <br>
            Bases :
            <b>${data.tickets.champ_reduit.bases.join(" - ")}</b>

            <br>

            Compléments :
            <b>${data.tickets.champ_reduit.complements.join(" - ")}</b>

            `;

        }



    } catch(error) {


        console.error(error);


        if (chevaux) {

            chevaux.innerHTML =
            "❌ Erreur connexion API AZ Turf";

        }


    }

}
