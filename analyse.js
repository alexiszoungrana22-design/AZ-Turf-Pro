const API = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerAnalyse(){


try{


const response = await fetch(API);


if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();



const chevaux =
data.classement ||
data.chevaux ||
[];




// Informations générales

const course =
document.getElementById("analyse-course");


const hippodrome =
document.getElementById("analyse-hippodrome");


if(course){

course.textContent =
data.course || "Course du jour";

}


if(hippodrome){

hippodrome.textContent =
data.hippodrome || "-";

}







// Favori du jour


const favori =
document.getElementById("favori");


if(favori && chevaux[0]){


favori.innerHTML = `

<h3>⭐ Favori du jour</h3>

<p>
N°${chevaux[0].numero}
-
${chevaux[0].nom || "Cheval"}
</p>

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







// Outsider du jour


const outsider =
document.getElementById("outsider");


if(outsider && chevaux[3]){


outsider.innerHTML = `

<h3>🔥 Outsider du jour</h3>

<p>
N°${chevaux[3].numero}
-
${chevaux[3].nom || "Cheval"}
</p>

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







// Tableau analyse


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
${cheval.nom || "-"}
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
? "Favori du jour"
:
index<3
? "Belle chance"
:
"Chance"
}

</td>


</tr>

`;

});


}







// Ticket


const ticket =
document.getElementById("analyse-ticket");



if(ticket && data.tickets){


ticket.innerHTML = `


<h3>🎟️ Sélection</h3>


<p>
Quinté :
<strong>
${data.tickets.quinte?.join(" - ") || "-"}
</strong>
</p>


<p>
Tiercé :
<strong>
${data.tickets.trio?.join(" - ") || "-"}
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
