const API = "https://az-turf-pro.onrender.com/api/analyse";


// Informations course

const ticketCourse =
document.getElementById("ticket-course");

const ticketHippodrome =
document.getElementById("ticket-hippodrome");


// Sélections

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


const response =
await fetch(API);


const data =
await response.json();




if(ticketCourse){

ticketCourse.textContent =
data.course || "-";

}



if(ticketHippodrome){

ticketHippodrome.textContent =
data.hippodrome || "-";

}






const chevaux =
data.classement ||
data.chevaux ||
[];




// Récupération des 7 retenus

const selection =
chevaux.slice(0,7).map(
cheval => cheval.numero
);





// QUINTE+

if(quinte){

quinte.innerHTML =

selection.join(" - ");

}





// QUARTE

if(quarte){

quarte.innerHTML =

selection.slice(0,5).join(" - ");

}





// TIERCE

if(trio){

trio.innerHTML =

selection.slice(0,4).join(" - ");

}





// COUPLES

if(couples){

couples.innerHTML = `

🤝 ${selection[0]} - ${selection[1]}

<br><br>

🤝 ${selection[0]} - ${selection[2]}

<br><br>

🤝 ${selection[1]} - ${selection[3]}

`;

}






// CHAMP REDUIT

if(champ){

champ.innerHTML = `

<strong>Base :</strong>

${selection[0]}


<br><br>


<strong>Associés :</strong>

${selection.slice(1).join(" - ")}

`;

}




}


catch(error){


console.log(
"Erreur sélection :",
error
);


}


}




document.addEventListener(
"DOMContentLoaded",
chargerSelection
);
