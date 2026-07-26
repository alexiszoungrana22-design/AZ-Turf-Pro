const API = "https://az-turf-pro.onrender.com/api/analyse";


// ELEMENTS COURSE

const analyseCourse = document.getElementById("analyse-course");
const analyseHippodrome = document.getElementById("analyse-hippodrome");
const analyseDiscipline = document.getElementById("analyse-discipline");
const analyseDistance = document.getElementById("analyse-distance");


// TABLEAU 7 RETENUS

const tableBody = document.getElementById("az-selection");


// CARTES HORIZONTALES

const selectionHorizontal =
document.getElementById("selection-az-horizontal");





function raisonAZ(cheval,index){

    if(cheval.raison){
        return cheval.raison;
    }

    if(cheval.type){
        return cheval.type;
    }


    if(index === 0){
        return "⭐ Favori AZ";
    }


    if(index < 3){
        return "🔥 Base solide";
    }


    if(index < 5){
        return "🎯 Chance régulière";
    }


    return "💎 Outsider intéressant";

}







async function chargerAnalyse(){


try{


const response = await fetch(API);



if(!response.ok){

throw new Error(
"Erreur API : " + response.status
);

}



const data = await response.json();




// INFORMATIONS COURSE


if(analyseCourse)

analyseCourse.textContent =
data.course || "-";



if(analyseHippodrome)

analyseHippodrome.textContent =
data.hippodrome || "-";



if(analyseDiscipline)

analyseDiscipline.textContent =
data.discipline || "-";



if(analyseDistance)

analyseDistance.textContent =
(data.distance_course || "-") + " m";







// RECUPERATION CHEVAUX


const chevaux =

data.classement ||

data.chevaux ||

[];






// TABLEAU DES 7 RETENUS


if(tableBody){


tableBody.innerHTML = "";



chevaux.slice(0,7).forEach((cheval,index)=>{


const tr = document.createElement("tr");



tr.innerHTML = `

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

${cheval.commentaire || "-"}

</td>



<td>

${cheval.rang || index+1}

</td>


`;



tableBody.appendChild(tr);


});


}









// CARTES HORIZONTALES DES 7 CHEVAUX


if(selectionHorizontal){


selectionHorizontal.innerHTML = "";



chevaux.slice(0,7).forEach((cheval,index)=>{


const carte = document.createElement("div");


carte.className = "cheval-mini";



carte.innerHTML = `


<div class="mini-numero">

N°${cheval.numero || "-"}

</div>



<strong>

${cheval.nom || "Cheval AZ"}

</strong>


<br>


<span>

Indice AZ :
${cheval.indice_az || 0}

</span>


<br>


<small>

${raisonAZ(cheval,index)}

</small>


`;



selectionHorizontal.appendChild(carte);



});


}



}


catch(error){


console.log(
"Erreur Analyse AZ :",
error
);


}



}






document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
