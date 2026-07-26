const API = "https://az-turf-pro.onrender.com/api/analyse";


// Informations course

const hippodrome = document.getElementById("meta-hippodrome");
const course = document.getElementById("meta-course");
const discipline = document.getElementById("meta-discipline");
const distance = document.getElementById("meta-distance");
const partants = document.getElementById("meta-partants");


// Tableau partants

const horsesTable = document.getElementById("all-horses");


// KPI

const favorite = document.getElementById("kpi-favorite");
const confidence = document.getElementById("kpi-confidence");
const outsider = document.getElementById("kpi-outsider");


// Chevaux populaires

const popular = document.getElementById("popular-horses");


// Sélection horizontale

const selection =
document.getElementById("home-selection");


// Horloge

const timer =
document.getElementById("timer");





function raisonCheval(cheval,index){

    if(cheval.type){
        return cheval.type;
    }

    if(index===0){
        return "⭐ Favori AZ";
    }

    if(index<3){
        return "🔥 Base";
    }

    return "🎯 Chance";

}







function lancerCompteARebours(heure){

    if(!heure || !timer){
        return;
    }


    setInterval(()=>{


        const maintenant = new Date();

        const depart = new Date();

        const [h,m] = heure.split(":");


        depart.setHours(h);
        depart.setMinutes(m);
        depart.setSeconds(0);



        let diff = depart - maintenant;



        if(diff <=0){

            timer.textContent =
            "🏇 Course en cours";

            return;

        }



        let heures =
        Math.floor(diff / 3600000);


        let minutes =
        Math.floor((diff % 3600000)/60000);


        let secondes =
        Math.floor((diff % 60000)/1000);



        timer.textContent =

        `${String(heures).padStart(2,"0")}:
        ${String(minutes).padStart(2,"0")}:
        ${String(secondes).padStart(2,"0")}`;



    },1000);


}









async function chargerAccueil(){


try{


const response =
await fetch(API);



const data =
await response.json();




// COURSE


if(hippodrome)
hippodrome.textContent =
data.hippodrome || "-";


if(course)
course.textContent =
data.course || "-";


if(discipline)
discipline.textContent =
data.discipline || "-";


if(distance)
distance.textContent =
(data.distance_course || "-")+" m";




// CHEVAUX

const chevaux =
data.classement ||
data.chevaux ||
[];




if(partants)
partants.textContent =
chevaux.length + " chevaux";







// TABLEAU DES PARTANTS


if(horsesTable){


horsesTable.innerHTML="";


chevaux.forEach((cheval,index)=>{


const ligne =
document.createElement("tr");


ligne.innerHTML = `

<td>${cheval.numero || "-"}</td>

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
${cheval.cote || "-"}
</td>

<td>
${raisonCheval(cheval,index)}
</td>

`;


horsesTable.appendChild(ligne);


});


}







// FAVORI


if(favorite && chevaux[0]){

favorite.textContent =

"N°"+chevaux[0].numero+
" "+(chevaux[0].nom || "");

}




// CONFIANCE


if(confidence && chevaux[0]){

confidence.textContent =

(chevaux[0].confiance || 
chevaux[0].indice_az || "-")
+" %";

}





// OUTSIDER


if(outsider && chevaux[3]){

outsider.textContent =

"N°"+chevaux[3].numero+
" "+(chevaux[3].nom || "");

}






// PLUS JOUES


if(popular){


popular.innerHTML="";


chevaux.slice(0,5)
.forEach((cheval)=>{


popular.innerHTML += `

<p>
🐎 N°${cheval.numero}
${cheval.nom || ""}
</p>

`;

});


}






// SELECTION HORIZONTALE


if(selection){


selection.innerHTML="";


chevaux.slice(0,7)
.forEach((cheval)=>{


selection.innerHTML += `

<div class="cheval-mini">

<div class="mini-numero">

N°${cheval.numero}

</div>


<strong>
${cheval.nom || "Cheval"}
</strong>


<br>

Indice AZ :
${cheval.indice_az || "-"}


</div>

`;


});


}






// HORLOGE SI DISPONIBLE


lancerCompteARebours(
data.heure_depart
);



}


catch(error){


console.log(
"Erreur accueil : ",
error
);


}


}





document.addEventListener(
"DOMContentLoaded",
chargerAccueil
);
