async function chargerAnalyse() {

    try {

        const reponse = await fetch(
            "https://az-turf-pro.onrender.com/api/analyse"
        );

        const data = await reponse.json();


        const tickets = data.tickets || {};


        // =====================
        // TICKETS GRATUITS
        // =====================

        document.getElementById("quinte").innerHTML =
            afficherListe(tickets.quinte);

        document.getElementById("quarte").innerHTML =
            afficherListe(tickets.quarte);

        document.getElementById("trio").innerHTML =
            afficherListe(tickets.trio);

        document.getElementById("deux-sur-quatre").innerHTML =
            afficherListe(tickets.deux_sur_quatre);



        // =====================
        // VIP
        // =====================

        const vip = tickets.vip || {};


        document.getElementById("vip-ticket-7").innerHTML =
            afficherListe(vip.ticket_7);


        document.getElementById("vip-ticket-5").innerHTML =
            afficherListe(vip.ticket_5);



        if (vip.champ_reduit) {

            document.getElementById("vip-champ").innerHTML =
                vip.champ_reduit.format || "Non disponible";

        }



        document.getElementById("couple-gagnant").innerHTML =
            afficherListe(tickets.couple_gagnant);



        document.getElementById("couple-place").innerHTML =
            afficherCombinaisons(
                tickets.couple_place
            );



    }

    catch(error) {

        console.error(
            "Erreur chargement AZ Turf :",
            error
        );

    }

}




function afficherListe(liste) {

    if (!liste || liste.length === 0) {

        return "Aucun ticket";

    }


    return liste.join(" - ");

}



function afficherCombinaisons(data) {

    if (!data || data.length === 0) {

        return "Aucun ticket";

    }


    return data
        .map(
            combinaison =>
            combinaison.join("-")
        )
        .join("<br>");

}



chargerAnalyse();
