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


        function afficherTickets(tickets){

    if(!tickets){
        return;
    }


    const vip = tickets.vip || {};


    const quinte = document.getElementById("quinte");
    const quarte = document.getElementById("quarte");
    const trio = document.getElementById("trio");
    const couple = document.getElementById("couple");
    const champ = document.getElementById("champ-reduit");
    const derniere = document.getElementById("derniere-minute");
    const message = document.getElementById("message-premium");



    if(quinte){
        quinte.textContent =
        (vip.quinte || []).join(" - ");
    }


    if(quarte){
        quarte.textContent =
        (vip.quarte || []).join(" - ");
    }


    if(trio){
        trio.textContent =
        (vip.trio || []).join(" - ");
    }


    if(couple){

        couple.textContent =
        (vip.couple_gagnant_place || [])
        .map(c => c.join("-"))
        .join(" | ");

    }



    if(champ && vip.champ_reduit){

        champ.textContent =
        vip.champ_reduit.format;

    }



    if(derniere && vip.ticket_derniere_minute){

        derniere.textContent =
        vip.ticket_derniere_minute.format;

    }



    if(message){

        message.textContent =
        vip.message_fin || "";

    }

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
