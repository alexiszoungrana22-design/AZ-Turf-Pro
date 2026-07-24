// =================================
// AZ TURF PRO v3
// Connexion API + affichage analyse
// =================================


const API_URL = "/api/analyse";



async function chargerAnalyse(){


    try{


        const response = await fetch(API_URL);


        const data = await response.json();



        afficherCourse(data);


        afficherChevaux(data.chevaux);


        afficherFavori(data.favori);


        afficherTickets(data.tickets);



    }

    catch(error){


        console.error(error);


        const course =
        document.getElementById("course");


        if(course){

            course.innerHTML =
            "❌ Impossible de charger l'analyse";

        }


    }


}




function afficherCourse(data){


    const bloc =
    document.getElementById("course");


    if(!bloc) return;



    const chevaux =
    data.chevaux || [];



    bloc.innerHTML = `


    <h2>
    🐎 ${data.course || "Course AZ"}
    </h2>


    <p>
    📅 Date : ${data.date || "Non renseignée"}
    </p>


    <p>
    🏇 Partants : ${chevaux.length}
    </p>


    <p>
    ⭐ Analyse AZ professionnelle
    </p>


    `;


}
// ================================
// AFFICHAGE DES CHEVAUX
// ================================


function afficherChevaux(chevaux){


    const liste =
    document.getElementById("chevaux");


    if(!liste) return;



    liste.innerHTML = "";



    chevaux.forEach((cheval,index)=>{


        const li =
        document.createElement("li");



        li.className =
        "cheval-card";



        li.innerHTML = `


        <h3>
        🐎 Cheval n°${cheval.numero}
        </h3>


        <p>
        👤 Jockey : ${cheval.jockey || "Non renseigné"}
        </p>


        <p>
        🏠 Entraîneur : ${cheval.entraineur || "Non renseigné"}
        </p>


        <p class="indice">

        ⭐ Indice AZ : ${cheval.indice_az}

        </p>


        <p class="confiance">

        📊 Confiance : ${cheval.confiance}%

        </p>


        <p>

        🏷️ ${cheval.type}

        </p>


        `;



        liste.appendChild(li);



    });


}




// ================================
// FAVORI AZ
// ================================


function afficherFavori(favori){


    const bloc =
    document.getElementById("favori");


    if(!bloc || !favori) return;



    bloc.innerHTML = `


    <h2>
    ⭐ Favori AZ
    </h2>


    <h3>
    🐎 Cheval n°${favori.numero}
    </h3>


    <p>
    Indice AZ : ${favori.indice_az}
    </p>


    <p>
    Confiance : ${favori.confiance}%
    </p>


    `;


}




// ================================
// TICKETS
// ================================


function afficherTickets(tickets){


    const bloc =
    document.getElementById("tickets");


    if(!bloc) return;



    bloc.innerHTML = `


    <p>
    🏆 Quinté :
    ${tickets.quinte || "-"}
    </p>


    <p>
    🥈 Quarté :
    ${tickets.quarte || "-"}
    </p>


    <p>
    🥉 Trio :
    ${tickets.trio || "-"}
    </p>


    `;


}




// Lancement automatique


document.addEventListener(

"DOMContentLoaded",

chargerAnalyse

);
