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







// TABLEAU ANALYSE


const tableau =
document.getElementById("analyse-body");



if(tableau){


tableau.innerHTML = "";



chevaux.forEach((cheval,index)=>{


const ligne =
document.createElement("tr");



ligne.innerHTML = `


<td>

${index + 1}

</td>



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

${cheval.forme || "-"}

</td>



<td>

${cheval.regularite || "-"}

</td>



<td>

${cheval.jockey || "-"}

</td>



<td>

${cheval.entraineur || "-"}

</td>



<td>

${cheval.confiance || "-"} %

</td>



<td>

${
cheval.type
||
(index===0
?
"Favori"
:
index<3
?
"Base"
:
"Chance")
}

</td>


`;



tableau.appendChild(ligne);



});



}









// DETAILS ANALYSE


const details =
document.getElementById("details-analyse");



if(details && chevaux.length){


details.innerHTML = `


<h3>

⭐ Point fort du classement

</h3>


<p>

N°${chevaux[0].numero || "-"}
-
${chevaux[0].nom || "Cheval"}

</p>


<p>

Indice AZ :
${chevaux[0].indice_az || "-"}

</p>


<p>

Confiance :
${chevaux[0].confiance || "-"} %

</p>


`;

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








// MESSAGES VISITEURS (LOCAL)


const bouton =
document.getElementById("envoyer-message");


const zoneMessage =
document.getElementById("message-visiteur");


const zoneAffichage =
document.getElementById("messages-visiteurs");





if(bouton){


bouton.addEventListener("click",()=>{


const message =
zoneMessage.value.trim();



if(message===""){

return;

}



zoneAffichage.innerHTML += `


<p>

💬 ${message}

</p>


`;



zoneMessage.value="";



});


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
