const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerAccueil() {

    try {

        const response = await fetch(API);

        if (!response.ok) {
            throw new Error("Erreur API " + response.status);
        }


        const data = await response.json();



        // Informations course

        const elements = {

            "meta-course": data.course,
            "meta-hippodrome": data.hippodrome,
            "meta-discipline": data.discipline,
            "meta-distance": data.distance_course + " m",
            "meta-partants": data.partants

        };


        Object.keys(elements).forEach(id => {

            const el = document.getElementById(id);

            if (el) {
                el.textContent = elements[id] || "-";
            }

        });





        // Tableau des partants

        const table = document.getElementById("all-horses");


        if (table) {


            table.innerHTML = "";


            const chevaux = data.chevaux || data.classement || [];


            chevaux.forEach(cheval => {


                table.innerHTML += `

                <tr>

                <td>
                ${cheval.numero || "-"}
                </td>


                <td>
                ${cheval.nom || "Cheval"}
                </td>


                <td>
                ${cheval.indice_az || "-"}
                </td>


                </tr>

                `;


            });


        }





        // Favori AZ

        const classement =
        data.classement || data.chevaux || [];



        if (classement.length) {


            const favori = classement[0];

            const outsider =
            classement[classement.length - 1];



            const favBox =
            document.getElementById("kpi-favorite");


            if(favBox){

                favBox.textContent =
                `${favori.numero} - ${favori.nom}`;

            }



            const confBox =
            document.getElementById("kpi-confidence");


            if(confBox){

                confBox.textContent =
                (favori.confiance || 90) + "%";

            }



            const outBox =
            document.getElementById("kpi-outsider");


            if(outBox){

                outBox.textContent =
                `${outsider.numero} - ${outsider.nom}`;

            }



        }






        // Plus joués du jour

        const popular =
        document.getElementById("popular-horses");


        if(popular){


            popular.innerHTML = "";


            classement.slice(0,3)
            .forEach((cheval,index)=>{


                popular.innerHTML += `

                <p>

                ${index+1}️⃣
                N°${cheval.numero}
                ${cheval.nom}

                </p>

                `;


            });


        }





    }


    catch(error){

        console.log("Erreur chargement :", error);

    }


}





// Décompte simple

function lancerTimer(){


    const timer =
    document.getElementById("timer");


    if(!timer) return;



    let secondes = 3600;



    setInterval(()=>{


        let h =
        Math.floor(secondes / 3600);


        let m =
        Math.floor((secondes % 3600)/60);


        let s =
        secondes % 60;



        timer.textContent =
        `${String(h).padStart(2,"0")}:`+
        `${String(m).padStart(2,"0")}:`+
        `${String(s).padStart(2,"0")}`;



        if(secondes > 0){
            secondes--;
        }



    },1000);


}





document.addEventListener(
"DOMContentLoaded",
()=>{

    chargerAccueil();

    lancerTimer();

});
