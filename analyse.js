const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerAnalyse(){


    try{


        const response = await fetch(API);


        if(!response.ok){

            throw new Error("Erreur API");

        }



        const data = await response.json();





        // Informations course


        const infos = {

            "analyse-course": data.course,

            "analyse-hippodrome": data.hippodrome,

            "analyse-discipline": data.discipline,

            "analyse-distance":
            data.distance_course + " m"

        };



        Object.keys(infos).forEach(id=>{


            const element =
            document.getElementById(id);


            if(element){

                element.textContent =
                infos[id] || "-";

            }


        });







        // 7 retenus AZ


        const tableau =
        document.getElementById("az-selection");



        const chevaux =
        data.classement || data.chevaux || [];



        if(tableau){


            tableau.innerHTML="";



            chevaux.slice(0,7).forEach((cheval,index)=>{



                let profil="Chance";


                if(index===0){

                    profil="⭐ Favori AZ";

                }

                else if(index<3){

                    profil="🔥 Base solide";

                }

                else if(index<5){

                    profil="🎯 Chance";

                }

                else{

                    profil="💎 Outsider";

                }




                tableau.innerHTML += `


                <tr>


                <td>
                ${cheval.rang || index+1}
                </td>


                <td>
                ${cheval.numero}
                </td>


                <td>
                ${cheval.nom}
                </td>


                <td>
                ${cheval.indice_az}
                </td>


                <td>
                ${profil}
                </td>


                </tr>


                `;



            });


        }









        // Tickets


        if(data.tickets){



            const t = data.tickets;



            document.getElementById("quinte").textContent =

            t.quinte.join(" - ");




            document.getElementById("quarte").textContent =

            t.quarte.join(" - ");




            document.getElementById("trio").textContent =

            t.trio.join(" - ");





            document.getElementById("couple-gagnant").textContent =

            t.couple_gagnant.join(" - ");





            document.getElementById("couple-place").innerHTML =

            t.couple_place
            .map(c=>c.join(" - "))
            .join("<br>");







            document.getElementById("champ-reduit").innerHTML =


            "Bases : "
            +
            t.champ_reduit.bases.join(" - ")
            +
            "<br>Compléments : "
            +
            t.champ_reduit.complements.join(" - ");



        }



    }


    catch(error){


        console.log(
        "Erreur chargement analyse :",
        error
        );


    }



}





document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
