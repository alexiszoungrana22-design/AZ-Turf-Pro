/**
 * AZ Turf Pro - Historique des analyses et arrivées
 */

const HISTORIQUE_STORAGE_KEY = "AZ_TURF_HISTORIQUE_COURSES_V1";
const API_HISTORIQUE = "https://az-turf-pro.onrender.com/api/historique";

document.addEventListener("DOMContentLoaded", () => {
    afficherPageHistorique();
});

function lireLocal(){
    try { return JSON.parse(localStorage.getItem(HISTORIQUE_STORAGE_KEY) || "[]"); }
    catch(e){ return []; }
}

function normaliserEntree(c){
    const tickets=c.tickets || {};
    const gratuit=tickets.gratuit || {};
    const selection=c.selection_az || gratuit.quinte || c.selection || [];
    const arrivee=Array.isArray(c.arrivee_quinte) ? c.arrivee_quinte : (Array.isArray(c.arrivee) ? c.arrivee.slice(0,5) : []);
    const courseInfo=(c.course && typeof c.course === "object") ? c.course : {};
    return {
        date:c.date || courseInfo.date || c.date_analyse || "-",
        reunion:c.reunion || courseInfo.reunion || "",
        numero:c.course_numero || courseInfo.course_numero || "",
        course:courseInfo.course || c.nom || c.course || "Course",
        hippodrome:courseInfo.hippodrome || c.hippodrome || "",
        selection:Array.isArray(selection) ? selection : [],
        arrivee,
        statut:arrivee.length >= 5 ? "ARRIVÉE OFFICIELLE" : "EN ATTENTE"
    };
}

async function chargerHistorique(){
    try{
        const r=await fetch(API_HISTORIQUE,{cache:"no-store"});
        if(!r.ok) throw new Error("API historique indisponible");
        const data=await r.json();
        const liste=Array.isArray(data.historique) ? data.historique : [];
        if(liste.length) return liste.map(normaliserEntree);
    }catch(e){
        console.warn("Historique API indisponible, utilisation locale",e);
    }
    return lireLocal().map(normaliserEntree);
}

function afficherPageHistorique(){
    const tbody=document.getElementById("historique-body") || document.getElementById("historique-table-body");
    const container=document.getElementById("historique-container");
    if(!tbody && !container) return;

    chargerHistorique().then(liste=>{
        if(tbody){
            tbody.innerHTML="";
            if(!liste.length){
                tbody.innerHTML='<tr><td colspan="5">Aucune course enregistrée pour le moment.</td></tr>';
                return;
            }
            liste.forEach(c=>{
                const selection=c.selection.length ? c.selection.join(" - ") : "-";
                const arrivee=c.arrivee.length ? c.arrivee.join(" - ") : "En attente";
                const tr=document.createElement("tr");
                tr.innerHTML=`
                    <td>${c.date}</td>
                    <td><strong>${c.reunion} ${c.numero}</strong><br>${c.course}${c.hippodrome ? `<br><small>${c.hippodrome}</small>` : ""}</td>
                    <td><strong>${selection}</strong></td>
                    <td><strong class="badge-arrivee">${arrivee}</strong></td>
                    <td>${c.statut}</td>`;
                tbody.appendChild(tr);
            });
        }else if(container){
            container.innerHTML=liste.map(c=>`
                <article class="historique-card">
                    <h3>${c.reunion} ${c.numero} - ${c.course}</h3>
                    <p>${c.hippodrome || "Hippodrome non disponible"}</p>
                    <p><strong>Sélection AZ Turf Pro :</strong> ${c.selection.join(" - ") || "-"}</p>
                    <p><strong>Arrivée Quinté :</strong> ${c.arrivee.join(" - ") || "En attente"}</p>
                </article>`).join("");
        }
    });
}

function reinitialiserHistorique(){
    if(confirm("Voulez-vous vraiment effacer tout l'historique local ?")){
        localStorage.removeItem(HISTORIQUE_STORAGE_KEY);
        afficherPageHistorique();
    }
}
