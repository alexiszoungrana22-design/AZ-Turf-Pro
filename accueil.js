const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerAccueil() {

    try {

        const response = await fetch(API);


        if (!response.ok) {

            throw new Error("Erreur API");

        }


        const data = await response.json();



        // Informations course

        const infos = {

            "meta-hippodrome": data.hippodrome,

            "meta-course": data.course,

            "meta-discipline": data.discipline,

            "meta-distance": data.distance_course + " m",

            "meta-partants": data.partants

        };



        Object.keys(infos).forEach(id => {


            const element = document.getElementById(id);


            if (element) {

                element.textContent = infos[id] || "-";

            }


        });







        // Tableau des partants accueil

        const tableau = document.getElementById("all-horses");


        if (tableau) {


            tableau.innerHTML = "";


            const chevaux = data.chevaux || data.classement || [];


            chevaux.forEach(cheval => {


                tableau.innerHTML += `

                <tr>

                    <td>
                    ${cheval.numero || "-"}
                    </td>


                    <td>
                    ${cheval.nom || "Cheval"}
                    </td>


                </tr>

                `;


            });


        }







        // Cartes rapides


        const classement =
        data.classement || data.chevaux || [];



        if (classement.length > 0) {



            const favori = classement[0];

            const outsider =
            classement[classement.length - 1];



            const fav =
            document.getElementById("kpi-favorite");


            if(fav){

                fav.textContent =
                `${favori.numero} - ${favori.nom}`;

            }




            const confiance =
            document.getElementById("kpi-confidence");


            if(confiance){

                confiance.textContent =
                `${favori.confiance || 90}%`;

            }




            const out =
            document.getElementById("kpi-outsider");


            if(out){

                out.textContent =
                `${outsider.numero} - ${outsider.nom}`;

            }



        }








        // Les plus joués du jour


        const populaires =
        document.getElementById("popular-horses");



        if(populaires){


            populaires.innerHTML = "";



            classement.slice(0,3).forEach((cheval,index)=>{


                populaires.innerHTML += `

                <p>
                ${index+1}️⃣ 
                N°${cheval.numero} - ${cheval.nom}
                </p>

                `;


            });


        }





    }


    catch(error){


        console.log(
            "Erreur accueil : ",
            error
        );


    }


}







// Décompte

function lancerCompteARebours(){


    const timer =
    document.getElementById("timer");


    if(!timer) return;



    let temps = 3600;



    setInterval(()=>{


        let heures =
        Math.floor(temps / 3600);



        let minutes =
        Math.floor((temps % 3600) / 60);



        let secondes =
        temps % 60;



        timer.textContent =
        String(heures).padStart(2,"0")
        + ":"
        +
        String(minutes).padStart(2,"0")
        + ":"
        +
        String(secondes).padStart(2,"0");



        if(temps > 0){

            temps--;

        }


    },1000);



}







document.addEventListener(
"DOMContentLoaded",
()=>{

    chargerAccueil();

    lancerCompteARebours();

});
