const API = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerAnalyse(){


try{


const response =
await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();





const chevaux =
data.classement ||
data.chevaux ||
[];








// FAVORI DU JOUR


const favori =
document.getElementById("favori");



if(favori && chevaux[0]){


favori.innerHTML = `


<div class="favorite-number">

N°${chevaux[0].numero}

</div>


<h3>

${chevaux[0].nom || "Cheval"}

</h3>


<p>

Indice :
${chevaux[0].indice_az || "-"}

</p>


<p>

Confiance :
${chevaux[0].confiance || "-"} %

</p>


`;

}









// OUTSIDER DU JOUR


const outsider =
document.getElementById("outsider");



if(outsider && chevaux[3]){


outsider.innerHTML = `


<div class="outsider-number">

N°${chevaux[3].numero}

</div>


<h3>

${chevaux[3].nom || "Cheval"}

</h3>


<p>

Indice :
${chevaux[3].indice_az || "-"}

</p>


<p>

Confiance :
${chevaux[3].confiance || "-"} %

</p>


`;

}









// TABLEAU CLASSEMENT


const tableau =
document.getElementById("analyse-body");



if(tableau){


tableau.innerHTML="";



chevaux.forEach((cheval,index)=>{


tableau.innerHTML += `


<tr>


<td>

${cheval.numero || "-"}

</td>



<td>

<strong>

${cheval.nom || "Cheval"}

</strong>

</td>



<td>

${cheval.indice_az || "-"}

</td>



<td>

${cheval.confiance || "-"} %

</td>



<td>

${
index===0
?
"Favori du jour"
:
index<3
?
"Belle chance"
:
"Chance"
}

</td>


</tr>


`;

});


}









// TICKET


const ticket =
document.getElementById("analyse-ticket");



if(ticket && data.tickets){


ticket.innerHTML = `


<p>

🏆 Quinté :

<br>

<strong>

${
data.tickets.quinte
?
data.tickets.quinte.join(" - ")
:
"-"
}

</strong>

</p>




<p>

🥉 Tiercé :

<br>

<strong>

${
data.tickets.trio
?
data.tickets.trio.join(" - ")
:
"-"
}

</strong>

</p>



`;

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
