const API_URL = "https://az-turf-pro.onrender.com/analyse";


const boutonAnalyse = document.getElementById("analyse");


if (boutonAnalyse) {


    boutonAnalyse.addEventListener("click", analyser);


}



async function analyser(){


    const chevauxZone = document.getElementById("chevaux");


    if(chevauxZone){

        chevauxZone.innerHTML =
        "⏳ Analyse AZ en cours...";

    }



    try{


        const reponse = await fetch(API_URL);


        const data = await reponse.json();



        afficherAnalyse(data);



    }catch(error){


        console.error(error);



        if(chevauxZone){

            chevauxZone.innerHTML =
            "❌ Impossible de contacter le serveur AZ Turf.";

        }


    }


}




function afficherAnalyse(data){



    let chevaux = [];


    if(data.chevaux){

        chevaux = data.chevaux;

    }



    const zone = document.getElementById("chevaux");



    if(zone){


        zone.innerHTML = "";



        chevaux.forEach(cheval => {



            zone.innerHTML += `

            <div class="cheval">

                🏇 N°${cheval.numero}

                <br>

                Rang : ${cheval.rang}

                <br>

                Indice AZ :

                <b>${cheval.indice_az}</b>

                <br>

                Confiance :

                ${cheval.confiance}%

                <br>

                ${cheval.type}

            </div>


            `;



        });



    }




    const favori =
    document.getElementById("favori");



    if(favori && chevaux.length > 0){


        const meilleur = chevaux[0];


        favori.innerHTML = `


        ⭐ Cheval N°${meilleur.numero}


        <br>


        Indice AZ : ${meilleur.indice_az}


        <br>


        Confiance : ${meilleur.confiance}%


        `;


    }




    const ticket =
    document.getElementById("ticket");



    if(ticket && data.ticket_premium){



        ticket.innerHTML = `


        🎫 Quinté AZ :

        ${data.ticket_premium.quinte.join(" - ")}


        <br><br>


        Base :

        ${data.ticket_premium.base}


        <br>


        Associés :

        ${data.ticket_premium.associes.join(" - ")}


        <br>


        Outsider :

        ${data.ticket_premium.outsider}


        `;



    }



}
