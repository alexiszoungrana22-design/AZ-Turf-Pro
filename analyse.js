const API = "https://az-turf-pro.onrender.com/api/analyse";


const tableBody = document.getElementById("table-body");

const kpiFavorite = document.getElementById("kpi-favorite");
const kpiConfidence = document.getElementById("kpi-confidence");
const kpiOutsider = document.getElementById("kpi-outsider");

const topCombination = document.getElementById("top-combination");
const ticketsBox = document.getElementById("tickets");



function raisonAZ(index){

    if(index === 0){
        return "⭐ Favori AZ";
    }

    if(index < 3){
        return "🔥 Base solide";
    }

    if(index < 5){
        return "🎯 Chance";
    }

    return "💎 Outsider";

}




async function chargerAnalyse(){


try{


const response = await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();





// récupération chevaux

const chevaux =
data.classement ||
data.chevaux ||
[];






// Tableau 7 retenus


if(tableBody){


tableBody.innerHTML = "";



chevaux.forEach((cheval,index)=>{


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

<strong>

${cheval.raison || cheval.type || raisonAZ(index)}

</strong>

</td>




<td>

<span class="badge-rank">

${cheval.rang || index + 1}

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
chevaux[chevaux.length - 1];



if(kpiOutsider){

kpiOutsider.textContent =
`${outsider.numero} - ${outsider.nom}`;

}



}








// Carte Tickets AZ


if(data.tickets && ticketsBox){


ticketsBox.innerHTML = `


<p>
🏆 Quinté AZ :
<br>

<strong>
${(data.tickets.quinte || []).join(" - ")}
</strong>

</p>



<p>
🥈 Quarté AZ :
<br>

<strong>
${(data.tickets.quarte || []).join(" - ")}
</strong>

</p>




<p>
🥉 Tiercé AZ :
<br>

<strong>
${(data.tickets.trio || []).join(" - ")}
</strong>

</p>




<p>
🎯 Couplé gagnant :
<br>

<strong>
${(data.tickets.couple_gagnant || []).join(" - ")}
</strong>

</p>



<p>
🔒 Champ réduit :
<br>

Bases :
<strong>
${(data.tickets.champ_reduit?.bases || []).join(" - ")}
</strong>

<br>

Compléments :
<strong>
${(data.tickets.champ_reduit?.complements || []).join(" - ")}
</strong>

</p>



`;

}




// Combinaison rapide


if(data.tickets && topCombination){


topCombination.innerHTML = `


<div class="combo-pill">

Q+ :
${(data.tickets.quinte || []).join(" - ")}

</div>



<div class="combo-pill">

Q :
${(data.tickets.quarte || []).join(" - ")}

</div>



<div class="combo-pill">

T :
${(data.tickets.trio || []).join(" - ")}

</div>


`;

}




}

catch(error){


console.log(
"Erreur Analyse :",
error
);


}



}




document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
