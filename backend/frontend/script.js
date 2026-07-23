const API_URL = "https://az-turf-pro.onrender.com/analyse";


const bouton = document.getElementById("analyse");

console.log("AZ Turf Pro chargé", bouton);


if (bouton) {

    bouton.addEventListener("click", async () => {


        document.getElementById("chevaux").innerHTML =
        `
        <div class="animation">
            🏇 AZ Turf Pro analyse la course...<br>
            ⏳ Calcul des indices AZ en cours
        </div>
        `;


        document.getElementById("ticket").innerHTML =
        "⏳ Génération du ticket AZ Premium...";


        try {

            const response = await fetch(API_URL);

            const data = await response.json();


            afficherResultats(data);


        } catch(error) {


            document.getElementById("chevaux").innerHTML =
            "❌ Erreur de connexion avec AZ Turf Pro";


            console.log(error);

        }

    });

}



function afficherResultats(data) {


    let chevaux = data.chevaux;


    if (!chevaux || chevaux.length === 0) {


        document.getElementById("chevaux").innerHTML =
        "Aucun cheval trouvé.";


        return;

    }



    let html = "";



    chevaux.forEach((cheval,index)=>{


        html += `

        <div class="cheval">

            <strong>
            ${index+1} 🏇 N°${cheval.numero}
            </strong>

            <br>

            Indice AZ :
            <b>${cheval.indice_az}</b>

            <br>

            Confiance :
            <span class="confiance">
            ${cheval.confiance} %
            </span>

            <br>

            Catégorie :
            ${cheval.type}

        </div>

        `;


    });



    document.getElementById("chevaux").innerHTML = html;




    // Coup de coeur AZ

    let premier = chevaux[0];


    document.getElementById("favori").innerHTML = `

        🏇 Cheval N°${premier.numero}

        <br>

        Indice AZ : ${premier.indice_az}

        <br>

        Confiance : ${premier.confiance} %

    `;




    // Ticket AZ Premium

    if(data.ticket_premium){


        let premium = data.ticket_premium;


        document.getElementById("ticket").innerHTML = `


        🎫 <strong>Ticket AZ Premium</strong>

        <br><br>


        ⭐ Base :
        ${premium.base}


        <br><br>


        🔒 Associés :
        ${premium.associes.join(" - ")}


        <br><br>


        🎯 Outsider :
        ${premium.outsider}


        <br><br>


        🏇 Quinté conseillé :
        ${premium.quinte.join(" - ")}


        `;


    } else {


        let ticket = chevaux
        .slice(0,5)
        .map(c => c.numero)
        .join(" - ");


        document.getElementById("ticket").innerHTML =

        "🎫 Quinté conseillé : " + ticket;


    }


}
