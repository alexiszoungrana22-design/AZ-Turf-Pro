const API = "/api/analyse";


// MENU

const btnMenu = document.getElementById("btnMenu");
const menu = document.getElementById("menu");
const overlay = document.getElementById("overlay");


btnMenu.onclick = () => {

    menu.classList.add("active");
    overlay.classList.add("active");

};


overlay.onclick = () => {

    menu.classList.remove("active");
    overlay.classList.remove("active");

};




// COMPTEUR

let temps = 7200;


function compteur(){

    let h = Math.floor(temps / 3600);
    let m = Math.floor((temps % 3600) / 60);
    let s = temps % 60;


    document.getElementById("timer").innerHTML =
    `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;


    if(temps > 0){
        temps--;
    }

}


setInterval(compteur,1000);
compteur();





// CHARGEMENT ANALYSE

async function chargerAnalyse(){

try {


const reponse = await fetch(API);

const data = await reponse.json();



/* COURSE */

document.getElementById("courseInfo").innerHTML = `

<h3>${data.course}</h3>

<p>
📍 ${data.hippodrome}
</p>

<p>
🏇 ${data.discipline}
</p>

<p>
📏 ${data.distance_course} m
</p>

<p>
🐎 Partants : ${data.partants}
</p>

`;





/* CHEVAUX */

let chevaux = data.chevaux || data.classement || [];


let html="";


if(chevaux.length){


chevaux.forEach(c=>{


html += `

<div class="cheval">

<b>🐎 N°${c.numero} - ${c.nom}</b>

<br>

⭐ Indice AZ : ${c.indice_az || 0}

<br>

🏆 Rang : ${c.rang || "-"}

</div>

`;

});


}else{


html = "Liste des partants disponible après analyse.";

}


document.getElementById("chevaux").innerHTML = html;




/* TICKET */


if(data.tickets){


document.getElementById("ticket").innerHTML = `

🔥 Quinté :

<b>
${data.tickets.quinte.join(" - ")}
</b>

<br><br>

🎯 Trio :

<b>
${data.tickets.trio.join(" - ")}
</b>

`;

}



}

catch(error){

console.log(error);

}


}





chargerAnalyse();





// BOUTON ANALYSE

document.getElementById("analyseBtn").onclick = () => {


let zone = document.getElementById("resultat");


zone.innerHTML = `

⏳ Analyse AZ en cours...

`;



setTimeout(()=>{

chargerAnalyse();


zone.innerHTML = `

✅ Analyse terminée

`;

},1500);



};
