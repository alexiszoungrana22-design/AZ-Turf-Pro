const API = "/api/analyse";


// MENU

const menuBtn = document.getElementById("menuBtn");
const sideMenu = document.getElementById("sideMenu");
const overlay = document.getElementById("overlay");


menuBtn.onclick = () => {

    sideMenu.classList.add("active");
    overlay.classList.add("active");

};


overlay.onclick = () => {

    sideMenu.classList.remove("active");
    overlay.classList.remove("active");

};




// COMPTEUR

let secondes = 5400;


function updateCountdown(){

    let h = Math.floor(secondes / 3600);
    let m = Math.floor((secondes % 3600) / 60);
    let s = secondes % 60;


    document.getElementById("countdown").innerHTML =
    `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;


    if(secondes > 0){
        secondes--;
    }

}


setInterval(updateCountdown,1000);

updateCountdown();






// CHARGEMENT API

async function chargerAnalyse(){

try{


const response = await fetch(API);

const data = await response.json();




// COURSE

document.getElementById("course").innerHTML = `

<h3>${data.course}</h3>

<p>
📍 Hippodrome : ${data.hippodrome}
</p>

<p>
🏇 Discipline : ${data.discipline}
</p>

<p>
📏 Distance : ${data.distance_course} m
</p>

<p>
💰 Allocation : ${data.allocation}
</p>

<p>
🐎 Partants : ${data.partants}
</p>

`;






// CHEVAUX

let chevaux = data.chevaux || data.classement || [];

let html = "";



if(chevaux.length){


chevaux.forEach((cheval)=>{


html += `

<div class="horse">

<b>
🐎 N°${cheval.numero} ${cheval.nom}
</b>

<br>

⭐ Indice AZ :
${cheval.indice_az || 0}

<br>

🏆 Rang :
${cheval.rang || "-"}

</div>

`;

});


}else{


html = `
<div class="horse">
Liste des partants disponible après analyse.
</div>
`;

}



document.getElementById("horses").innerHTML = html;






// TICKET

if(data.tickets){


document.getElementById("ticket").innerHTML = `

<p>
🔥 Quinté :
<b>
${data.tickets.quinte.join(" - ")}
</b>
</p>


<p>
🎯 Quarté :
<b>
${data.tickets.quarte.join(" - ")}
</b>
</p>


<p>
🏆 Trio :
<b>
${data.tickets.trio.join(" - ")}
</b>
</p>


`;

}





}

catch(error){

console.log(
"Erreur AZ Turf :",
error
);

}


}




chargerAnalyse();






// ANALYSE BUTTON


document.getElementById("analyseBtn").onclick = ()=>{


const zone = document.getElementById("analyseResult");


zone.innerHTML = `

<p>
⏳ Analyse AZ en cours...
</p>

`;



setTimeout(()=>{


chargerAnalyse();


zone.innerHTML = `

<p>
✅ Analyse terminée
</p>

`;


},1500);



};
