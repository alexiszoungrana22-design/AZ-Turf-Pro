const API = "https://az-turf-pro.onrender.com/api/analyse";


// ELEMENTS HTML

const tableBody = document.getElementById("az-selection");

const quinte = document.getElementById("quinte");
const quarte = document.getElementById("quarte");
const trio = document.getElementById("trio");

const coupleGagnant = document.getElementById("couple-gagnant");
const couplePlace = document.getElementById("couple-place");

const champReduit = document.getElementById("champ-reduit");




// RAISON AZ

function raisonAZ(cheval, index){

    if(cheval.raison){
        return cheval.raison;
    }

    if(cheval.type){
        return cheval.type;
    }


    if(index === 0){
        return "⭐ Favori AZ : meilleur indice";
    }


    if(index < 3){
        return "🔥 Base solide";
    }


    if(index < 5){
        return "🎯 Chance pour l'arrivée";
    }


    return "💎 Outsider intéressant";

}





async function chargerAnalyse(){


try{


const response = await fetch(API);



if(!response.ok){

throw new Error("Erreur API : " + response.status);

}



const data = await response.json();




// RECUPERATION CHEVAUX

const chevaux =
data.classement ||
data.chevaux ||
[];






// AFFICHAGE TABLEAU 7 RETENUS


if(tableBody){


tableBody.innerHTML = "";



chevaux.forEach((cheval,index)=>{


const ligne = document.createElement("tr");



ligne.innerHTML = `


<td>

<span class="num-badge">

${cheval.numero || "-"}

</span>

</td>



<td>

<strong>

${cheval.nom || "Cheval AZ"}

</strong>

</td>




<td>

${cheval.jockey || "-"}

</td>




<td>

${cheval.entraineur || "-"}

</td>




<td>

${cheval.forme || cheval.musique || "-"}

</td>




<td>

<strong>

${cheval.indice_az || cheval.score || 0}

</strong>

</td>




<td>

${raisonAZ(cheval,index)}

</td>




<td>

${cheval.rang || index+1}

</td>


`;



tableBody.appendChild(ligne);


});


}







// AFFICHAGE TICKETS AZ


if(data.tickets){



if(quinte){

quinte.textContent =
(data.tickets.quinte || [])
.join(" - ");

}



if(quarte){

quarte.textContent =
(data.tickets.quarte || [])
.join(" - ");

}



if(trio){

trio.textContent =
(data.tickets.trio || [])
.join(" - ");

}




if(coupleGagnant){

coupleGagnant.textContent =
(data.tickets.couple_gagnant || [])
.join(" - ");

}




if(couplePlace){

couplePlace.innerHTML =
(data.tickets.couple_place || [])
.map(c => c.join(" - "))
.join("<br>");

}




if(champReduit){


const bases =
data.tickets.champ_reduit?.bases || [];


const complements =
data.tickets.champ_reduit?.complements || [];



champReduit.innerHTML =

"Bases : " +
bases.join(" - ")
+
"<br>Compléments : "
+
complements.join(" - ");



}



}




}


catch(error){


console.log(
"Erreur analyse :",
error
);


}



}





document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
