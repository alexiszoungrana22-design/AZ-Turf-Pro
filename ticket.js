// =================================
// AZ Turf Pro - Sélection du jour
// =================================


const API = "https://az-turf-pro.onrender.com/api/analyse";



const course =
document.getElementById("ticket-course");


const hippodrome =
document.getElementById("ticket-hippodrome");



const quinte =
document.getElementById("quinte");


const quarte =
document.getElementById("quarte");


const trio =
document.getElementById("trio");


const couples =
document.getElementById("couples");


const champ =
document.getElementById("champ-reduit");





async function chargerSelection(){


try{


const reponse = await fetch(API);


const data = await reponse.json();





// Informations course

if(course){

course.textContent =
data.course || "-";

}


if(hippodrome){

hippodrome.textContent =
data.hippodrome || "-";

}






// Chevaux retenus

const chevaux =
data.classement ||
data.chevaux ||
[];




const selection =
chevaux
.slice(0,7)
.map(cheval => cheval.numero);







// QUINTE+

if(quinte){

quinte.innerHTML =

selection.join(" - ");

}






// QUARTE

if(quarte){

quarte.innerHTML =

selection
.slice(0,5)
.join(" - ");

}






// TIERCE

if(trio){

trio.innerHTML =

selection
.slice(0,4)
.join(" - ");

}







// COUPLES

if(couples){

couples.innerHTML = `

${selection[0]} - ${selection[1]}
<br><br>
${selection[0]} - ${selection[2]}
<br><br>
${selection[1]} - ${selection[3]}

`;

}







// CHAMP REDUIT

if(champ){

champ.innerHTML = `

<strong>Base :</strong>

N° ${selection[0]}


<br><br>


<strong>Associés :</strong>

${selection.slice(1).join(" - ")}

`;

}




}

catch(erreur){


console.log(
"Erreur chargement sélection :",
erreur
);


}


}





document.addEventListener(
"DOMContentLoaded",
chargerSelection
);
