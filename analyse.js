const API = "https://az-turf-pro.onrender.com/api/analyse";


const tableBody = document.getElementById("table-body");
const btnRefresh = document.getElementById("btn-refresh");

const kpiFavorite = document.getElementById("kpi-favorite");
const kpiConfidence = document.getElementById("kpi-confidence");
const kpiOutsider = document.getElementById("kpi-outsider");

const topCombination = document.getElementById("top-combination");
const ticketsBox = document.getElementById("tickets");



function raisonAZ(index){

    if(index === 0){

        return "⭐ Favori AZ : meilleur indice";

    }

    if(index < 3){

        return "🔥 Base solide : très bon profil";

    }

    if(index < 5){

        return "🎯 Chance : peut confirmer";

    }


    return "💎 Outsider : coup intéressant";

}




async function chargerAnalyse(){

try{


const response = await fetch(API);


if(!response.ok){

throw new Error("Erreur API");

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



Object.keys(elements).forEach(id=>{

const el=document.getElementById(id);

if(el){

el.textContent = elements[id] || "-";

}

});






// Classement 7 retenus


const chevaux =
data.classement || data.chevaux || [];




if(tableBody){


tableBody.innerHTML="";



chevaux.forEach((cheval,index)=>{


const tr=document.createElement("tr");



tr.innerHTML = `


<td>

<span class="num-badge">

${cheval.numero || "-"}

</span>

</td>



<td>

<strong>

${cheval.nom || "Cheval"}

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

<div class="score-bar-container">

<span>

${cheval.indice_az || 0}

</span>


<div class="score-bar">

<div class="score-fill"

style="width:${Math.min((cheval.indice_az || 0)/2.5,100)}%">

</div>

</div>


</div>

</td>





<td>

<strong>

${raisonAZ(index)}

</strong>

</td>






<td>

<span class="badge-rank ${
index===0
?"top1"
:index<3
?"top3"
:"outsider"

}">

${cheval.rang || index+1}

</span>


</td>


`;



tableBody.appendChild(tr);



});


}






// KPI


if(chevaux.length){



if(kpiFavorite){

kpiFavorite.textContent =
`${chevaux[0].numero} - ${chevaux[0].nom}`;

}




if(kpiConfidence){

kpiConfidence.textContent =
`${chevaux[0].confiance || 90}%`;

}




const outsider =
chevaux[chevaux.length-1];



if(kpiOutsider){

kpiOutsider.textContent =
`${outsider.numero} - ${outsider.nom}`;

}



}







// Tickets


if(data.tickets && topCombination){


topCombination.innerHTML = `


<div class="combo-pill">

<span>Q+</span>

${data.tickets.quinte.join(" - ")}

</div>



<div class="combo-pill">

<span>Q</span>

${data.tickets.quarte.join(" - ")}

</div>



<div class="combo-pill">

<span>T</span>

${data.tickets.trio.join(" - ")}

</div>


`;

}




if(data.tickets && ticketsBox){


ticketsBox.innerHTML = `


<p>
🥇 Couplé gagnant :
<strong>
${data.tickets.couple_gagnant.join(" - ")}
</strong>
</p>



<p>
🥈 Couplés placés :
<br>

${data.tickets.couple_place
.map(c=>c.join(" - "))
.join("<br>")}

</p>



<p>
🔒 Champ réduit :
<br>

Bases :
<strong>
${data.tickets.champ_reduit.bases.join(" - ")}
</strong>

<br>

Compléments :
<strong>
${data.tickets.champ_reduit.complements.join(" - ")}
</strong>

</p>


`;

}



}

catch(error){

console.log("Erreur Analyse :",error);

}


}




if(btnRefresh){

btnRefresh.onclick = chargerAnalyse;

}




document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
