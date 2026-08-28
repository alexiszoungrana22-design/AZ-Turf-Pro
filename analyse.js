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




// ===============================
// OUTILS AFFICHAGE
// ===============================

function afficher(id,valeur){

const element = document.getElementById(id);

if(element){

element.textContent =
valeur || "-";

}

}




// ===============================
// SELECTION DU JOUR 8 CHEVAUX
// ===============================


const selection = chevaux.slice(0,8);



afficher(

"selection-jour",

selection
.map(c=>c.numero)
.join(" - ")

);




afficher(

"bases-solides",

selection
.slice(0,2)
.map(c=>c.numero)
.join(" - ")

);




afficher(

"chances-regulieres",

selection
.slice(2,5)
.map(c=>c.numero)
.join(" - ")

);




afficher(

"outsiders-selection",

selection
.slice(5,8)
.map(c=>c.numero)
.join(" - ")

);








// ===============================
// FAVORI AZ
// ===============================


const favori = chevaux[0];



if(favori){


afficher(

"favori-numero",

favori.numero

);



afficher(

"favori-nom",

favori.nom || "Cheval AZ"

);



afficher(

"favori-indice",

favori.indice_az

);



afficher(

"favori-confiance",

favori.confiance ?
favori.confiance + " %" :
"-"

);



afficher(

"favori-raison",

favori.raison ||
"⭐ Favori AZ : meilleur indice et profil prioritaire"

);


}






// ===============================
// OUTSIDER AZ
// ===============================


const outsider =

chevaux[7] ||
chevaux[6];



if(outsider){


afficher(

"outsider-numero",

outsider.numero

);



afficher(

"outsider-nom",

outsider.nom || "Cheval AZ"

);



afficher(

"outsider-indice",

outsider.indice_az

);



afficher(

"outsider-confiance",

outsider.confiance ?
outsider.confiance + " %" :
"-"

);



afficher(

"outsider-raison",

outsider.raison ||
"🔥 Outsider AZ : profil intéressant pouvant surprendre."

);


}
 // ===============================
// POURQUOI CETTE SELECTION
// ===============================


const raisons =

document.getElementById("raisons-selection");



if(raisons){


raisons.innerHTML =


chevaux
.slice(0,8)
.map(c => `

<div class="raison-cheval">

<h3>
🏇 N°${c.numero || "-"}
</h3>


<p>

${c.raison ||

"Cheval retenu selon la forme, la régularité et l'indice AZ."}

</p>


</div>

`)
.join("");

}






// ===============================
// TABLEAU ANALYSE DES 8 CHEVAUX
// ===============================


const tableau =

document.getElementById("analyse-body");



if(tableau){


tableau.innerHTML = "";



chevaux
.slice(0,8)
.forEach(cheval => {


tableau.innerHTML += `

<tr>

<td>
${cheval.numero || "-"}
</td>


<td>
${cheval.nom || "Cheval"}
</td>


<td>
${cheval.indice_az || "-"}
</td>


<td>
${cheval.confiance ? cheval.confiance + " %" : "-"}
</td>


<td>
${cheval.raison || "Analyse AZ"}
</td>


</tr>

`;

});


}







// ===============================
// TICKETS GRATUITS
// ===============================


const tickets =

data.tickets?.gratuit || {};





const quinte =

document.getElementById("quinte-gratuit");



if(quinte){


quinte.textContent =

(tickets.quinte || [])
.join(" - ");


}






const deuxSurQuatre =

document.getElementById("deux-sur-quatre");



if(deuxSurQuatre){


deuxSurQuatre.textContent =

(tickets.deux_sur_quatre || [])
.join(" - ");


}







const couplePlace =

document.getElementById("couple-place-gratuit");



if(couplePlace){


couplePlace.textContent =

(tickets.couple_place || [])
.join(" - ");


}






// ===============================
// AVIS COURSE
// ===============================


const avis =

document.getElementById("avis-course");



if(avis){


avis.textContent =

"Les chevaux retenus présentent des profils intéressants selon la forme, l'expérience et les conditions de course.";

}







// ===============================
// ACTUALITES
// ===============================


const actualites =

document.getElementById("actualites-course");



if(actualites){


actualites.textContent =

"Aucune actualité majeure disponible pour le moment.";

}






// ===============================
// SYNTHESE AZ
// ===============================


const synthese =

document.getElementById("synthese-az");



if(synthese){


synthese.textContent =

"La sélection AZ privilégie les chevaux réguliers avec les meilleurs indices de performance.";

}



}


catch(error){


console.log(
"Erreur analyse :",
error
);


}



}




document.addEventListener("DOMContentLoaded", () => chargerAnalyse());


// ===============================
// COMMENTAIRES VISITEURS
// (affichage local, même logique que
// commentaires.html — non persistant)
// ===============================

document.addEventListener("DOMContentLoaded", function(){

const bouton = document.getElementById("envoyer-message");

if(!bouton){

return;

}

bouton.addEventListener("click", function(){

const champ = document.getElementById("message-visiteur");

const liste = document.getElementById("messages-visiteurs");

const texte = champ ? champ.value.trim() : "";

if(!texte){

return;

}

if(liste){

liste.innerHTML +=
`<p>💬 ${texte}</p>`;

}

if(champ){

champ.value = "";

}

});

});
 


async function chargerActualitesAnalyse(){
  const z=document.getElementById('analyse-news'); if(!z)return;
  try{const r=await fetch('/api/actualites?limit=6',{cache:'no-store'});const d=await r.json();const items=d.actualites||[];z.innerHTML=items.length?items.map(a=>`<a class="news-item" href="${a.url}" target="_blank" rel="noopener noreferrer"><span class="news-source">${a.source||'Source hippique'}</span><div class="news-title">${a.titre}</div><span class="news-more">Lire la source →</span></a>`).join(''):'<div class="news-skeleton">Actualités indisponibles momentanément.</div>';}catch(e){z.innerHTML='<div class="news-skeleton">Actualités indisponibles momentanément.</div>';}}

function formaterDepart(value){
  if(value===null||value===undefined||value==='') return 'Non communiqué';
  const n=Number(value);
  if(Number.isFinite(n) && n>100000000000){
    const d=new Date(n);
    if(!Number.isNaN(d.getTime())) return d.toLocaleString('fr-FR',{dateStyle:'short',timeStyle:'short'});
  }
  return String(value);
}
function enrichirContexteAnalyse(data){
  const set=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=(v===0||v)?v:'—'};
  set('ctx-hippodrome',data.hippodrome||'Non communiqué'); set('ctx-discipline',data.discipline||'Non communiquée'); set('ctx-distance',data.distance?data.distance+' m':'—'); set('ctx-partants',data.partants??'—'); set('ctx-depart',formaterDepart((data.horaires&&data.horaires.depart)||data.heure_depart)); set('ctx-terrain',data.terrain||data.etat_piste||'Donnée non disponible');
  const b=document.getElementById('analyse-source-badge'); if(b) b.textContent='Source : '+(data.source==='pmu_live'?'PMU live':(data.source||'—'));
}
async function chargerContexteAvance(){
  try{
    const r=await fetch(API,{cache:'no-store'}); if(!r.ok) return; const data=await r.json(); enrichirContexteAnalyse(data);
    const r2=await fetch('/api/analyse/complete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chevaux:data.chevaux||data.classement||[],info_course:data})});
    if(!r2.ok) return; const d=await r2.json();
    const c=d.tendances_cotes||[]; const sig=c.find(x=>x.signal&&x.signal!=='NEUTRE');
    const set=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v||'—'};
    set('signal-cotes',sig?`${sig.signal} · N°${sig.numero}`:'Aucun signal fort'); set('signal-cotes-detail',sig?`${sig.nom||''} · variation ${sig.variation_pct??'—'} %`:'Aucun mouvement exploitable disponible.');
    const presse=d.consensus_presse||[]; set('signal-presse',presse.length?`${presse.length} avis disponibles`:'Non disponible'); set('signal-presse-detail',presse.length?'Consensus reçu depuis le module presse.':'Aucun consensus réel disponible.');
    set('signal-piste',d.impact_meteo||'INCONNU'); set('signal-piste-detail',d.impact_meteo&&d.impact_meteo!=='NEUTRE'?'Impact transmis au contexte de course.':'Pas de signal terrain exploitable.');
  }catch(e){ console.log('Contexte avancé indisponible',e); }
}
const _chargerAnalyseOrig=chargerAnalyse;
chargerAnalyse=async function(){ await _chargerAnalyseOrig(); await chargerContexteAvance(); await chargerActualitesAnalyse(); };
