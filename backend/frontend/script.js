const API_URL = "https://az-turf-pro.onrender.com/analyse";


const bouton = document.getElementById("analyse");

console.log("AZ Turf Pro chargé", bouton);


if (bouton) {

    bouton.addEventListener("click", async () => {

        document.getElementById("chevaux").innerHTML =
            "⏳ Analyse AZ en cours...";


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



    // Ticket conseillé

    let ticket = chevaux
    .slice(0,5)
    .map(c => c.numero)
    .join(" - ");


    document.getElementById("ticket").innerHTML =

    "🎫 Quinté conseillé : " + ticket;

}
