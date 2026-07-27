// ===============================
// AZ TURF PRO - SCRIPT PRINCIPAL
// ===============================


const API_URL =
    "https://az-turf-pro.onrender.com/api/analyse";



async function chargerAnalyse() {

    try {

        const reponse = await fetch(API_URL);

        const data = await reponse.json();



        console.log("Analyse AZ :", data);



        const tickets = data.tickets || {};



        // ===============================
        // TICKETS GRATUITS
        // ===============================


        afficher(
            "quinte",
            tickets.quinte
        );


        afficher(
            "quarte",
            tickets.quarte
        );


        afficher(
            "trio",
            tickets.trio
        );


        afficher(
            "deux-sur-quatre",
            tickets.deux_sur_quatre
        );





        // ===============================
        // ESPACE VIP
        // ===============================


        const vip = tickets.vip || {};



        afficher(
            "vip-ticket-7",
            vip.ticket_7
        );



        afficher(
            "vip-ticket-5",
            vip.ticket_5
        );



        if (
            document.getElementById("vip-champ")
            &&
            vip.champ_reduit
        ) {

            document.getElementById(
                "vip-champ"
            ).innerHTML =
                vip.champ_reduit.format;

        }




        if (
            document.getElementById("couple-gagnant")
        ) {

            afficher(
                "couple-gagnant",
                tickets.couple_gagnant
            );

        }




        if (
            document.getElementById("couple-place")
        ) {

            const place =
                tickets.couple_place || [];

            document.getElementById(
                "couple-place"
            ).innerHTML =

                place
                .map(
                    c => c.join("-")
                )
                .join("<br>");

        }


    }

    catch(error) {


        console.error(
            "Erreur AZ Turf Pro :",
            error
        );


    }

}





function afficher(id, liste) {


    const element =
        document.getElementById(id);



    if (!element) {

        return;

    }



    if (
        !liste
        ||
        liste.length === 0
    ) {

        element.innerHTML =
            "Non disponible";

        return;

    }



    element.innerHTML =
        liste.join(" - ");

}





chargerAnalyse();
