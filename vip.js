const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerVIP(){


    try{


        const response = await fetch(API);



        if(!response.ok){

            throw new Error("Erreur API");

        }



        const data = await response.json();




        const chevaux =
        data.classement || data.chevaux || [];




        // Base VIP

        const baseVIP =
        chevaux.slice(0,2);



        const baseBox =
        document.getElementById("base-vip");


        if(baseBox){


            baseBox.innerHTML =

            baseVIP
            .map(c =>
            `⭐ N°${c.numero} - ${c.nom}`
            )
            .join("<br>");

        }





        // Champ réduit VIP


        if(data.tickets && data.tickets.champ_reduit){



            const champ =
            data.tickets.champ_reduit;



            const base =
            champ.bases || [];



            const complements =
            champ.complements || [];




            const baseElement =
            document.getElementById("vip-base");



            if(baseElement){

                baseElement.textContent =
                base.join(" - ");

            }






            const systeme =
            document.getElementById("vip-systeme");



            if(systeme){


                systeme.textContent =

                base[0]
                +
                "-X-"
                +
                base[1]
                +
                "-X-X";


            }







            const comp =
            document.getElementById("vip-complements");



            if(comp){


                comp.textContent =
                complements.join(" - ");


            }



        }







        // Cheval à surveiller


        const surveille =
        document.getElementById("cheval-surveille");



        if(surveille && chevaux.length > 2){


            const cheval =
            chevaux[2];



            surveille.innerHTML =

            `
            🎯 N°${cheval.numero} - ${cheval.nom}
            <br>
            Indice AZ : ${cheval.indice_az}
            `;


        }








        // Ticket sécurité VIP


        const ticket =
        document.getElementById("ticket-vip");



        if(ticket && data.tickets){



            ticket.innerHTML =

            `
            🏆 Quinté sécurité :
            <strong>
            ${data.tickets.quinte.join(" - ")}
            </strong>
            <br><br>

            🥉 Tiercé :
            <strong>
            ${data.tickets.trio.join(" - ")}
            </strong>
            `;


        }




    }


    catch(error){


        console.log(
        "Erreur VIP :",
        error
        );


    }



}





document.addEventListener(
"DOMContentLoaded",
chargerVIP
);
