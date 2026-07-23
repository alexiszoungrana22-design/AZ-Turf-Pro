const API_URL = "/analyse";


const bouton = document.getElementById("analyse");


console.log("AZ Turf Pro chargé");



if (bouton) {


    bouton.addEventListener("click", async () => {


        const zone = document.getElementById("chevaux");


        if(zone){

            zone.innerHTML = "⏳ Analyse AZ en cours...";

        }



        try {


            const response = await fetch(API_URL);


            const data = await response.json();



            afficherResultats(data);



        } catch(error) {


            if(zone){

                zone.innerHTML =
                "❌ Erreur de connexion AZ Turf Pro";

            }


            console.log(error);


        }


    });


}





function afficherResultats(data){



    const chevaux = data.classement || [];



    if(chevaux.length === 0){


        document.getElementById("chevaux").innerHTML =
        "Aucun résultat";


        return;

    }




    let html = "";



    chevaux.forEach((cheval,index)=>{


        html += `


        <div class="cheval">


            <strong>

            ${index + 1} 🏇 N°${cheval.numero}

            </strong>


            <br>


            Indice AZ :

            <b>${cheval.indice_az}</b>


            <br>


            Confiance :

            <span>

            ${cheval.confiance} %

            </span>


            <br>


            ${cheval.type}


        </div>


        `;


    });



    const zone = document.getElementById("chevaux");


    if(zone){

        zone.innerHTML = html;

    }





    // Favori AZ


    const favori = data.favori;



    if(favori && document.getElementById("favori")){


        document.getElementById("favori").innerHTML = `


        ⭐ Cheval N°${favori.numero}


        <br>

        Indice AZ : ${favori.indice_az}


        <br>

        Confiance : ${favori.confiance}%


        `;


    }




    // Tickets AZ


    const tickets = data.tickets;



    if(tickets && document.getElementById("ticket")){


        document.getElementById("ticket").innerHTML = `


        🎫 Quinté :

        ${tickets.quinte.join(" - ")}


        <br><br>


        🎫 Quarté :

        ${tickets.quarte.join(" - ")}


        <br><br>


        🏇 Trio :

        ${tickets.trio.join(" - ")}


        <br><br>


        🔥 Champ réduit :

        ${tickets.champ_reduit.bases.join(" - ")}

        +

        ${tickets.champ_reduit.complements.join(" - ")}


        `;


    }


}
