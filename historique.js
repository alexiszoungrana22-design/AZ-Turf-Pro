const API = "https://az-turf-pro.onrender.com/api/analyse";
const HISTORIQUE_STORAGE = "az_turf_pro_historique_v1";

function chargerHistoriqueLocal(){
    try{
        const contenu = localStorage.getItem(
            HISTORIQUE_STORAGE
        );

        if(!contenu){
            return [];
        }

        const donnees = JSON.parse(contenu);

        return Array.isArray(donnees)
            ? donnees
            : [];
    }catch(error){
        console.log(
            "Erreur lecture historique local :",
            error
        );
        return [];
    }
}

function sauvegarderHistoriqueLocal(donnees){
    try{
        localStorage.setItem(
            HISTORIQUE_STORAGE,
            JSON.stringify(donnees)
        );
    }catch(error){
        console.log(
            "Erreur sauvegarde historique local :",
            error
        );
    }
}

function cleCourse(data){
    return [
        data?.date || "",
        data?.reunion || "",
        data?.course_numero || "",
        data?.course || ""
    ].join("|");
}

function ajouterCourseHistorique(data){if(!data||data.donnees_demo)return chargerHistoriqueLocal();const h=chargerHistoriqueLocal(),cle=cleCourse(data),i=h.findIndex(x=>x.cle===cle),old=i>=0?h[i]:{};const e={...old,cle,date:data.date||old.date||"",reunion:data.reunion||old.reunion||"",course_numero:data.course_numero||old.course_numero||"",course:data.course||old.course||"Course",hippodrome:data.hippodrome||old.hippodrome||"",discipline:data.discipline||old.discipline||"",distance:data.distance||old.distance||"",source:data.source||old.source||"",date_enregistrement:old.date_enregistrement||new Date().toISOString(),favori:data.favori||old.favori||{},selection:data.tickets?.gratuit?.quinte||old.selection||[],premium:data.tickets?.premium||old.premium||{},classement:data.classement||old.classement||[],arrivee:old.arrivee||[],rapports:old.rapports||[]};if(i>=0)h[i]=e;else h.unshift(e);const out=h.slice(0,100);sauvegarderHistoriqueLocal(out);return out;}
function fusionnerHistoriqueBackend(entrees){if(!Array.isArray(entrees))return chargerHistoriqueLocal();let h=chargerHistoriqueLocal();for(const item of entrees){const c=item.course||{},d={date:c.date||"",reunion:c.reunion||"",course_numero:c.course_numero||"",course:c.course||"Course",hippodrome:c.hippodrome||"",source:c.source||"",favori:(item.classement||[])[0]||{},classement:item.classement||[],tickets:item.tickets||{},donnees_demo:false};h=ajouterCourseHistorique(d);const i=h.findIndex(x=>x.cle===cleCourse(d));if(i>=0&&Array.isArray(item.arrivee)&&item.arrivee.length)h[i].arrivee=item.arrivee;}sauvegarderHistoriqueLocal(h);return h;}

function afficherHistorique(donnees){
    const body =
        document.getElementById(
            "historique-body"
        );

    if(!body) return;

    body.innerHTML = "";

    if(!donnees.length){
        body.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 15px; color: #9ca3af;">
                    Aucune course passée enregistrée.
                </td>
            </tr>
        `;
        return;
    }

    donnees.forEach(item => {
        const favori =
            item.favori?.numero
            ? "N°" + item.favori.numero +
              " " + (item.favori.nom || "")
            : "-";

        const selection =
            Array.isArray(item.selection)
            ? item.selection.join(" - ")
            : "-";

        let resultat = "En attente";

        if(
            Array.isArray(item.arrivee) &&
            item.arrivee.length
        ){
            resultat =
                item.arrivee.join(" - ");
        }

        body.innerHTML += `
            <tr style="border-bottom: 1px solid #374151;">
                <td style="padding: 12px; color: #fff;">${item.date || "-"}</td>
                <td style="padding: 12px; color: #fff;">
                    ${item.course || "-"}
                    ${
                        item.hippodrome
                        ? "<br><span style='font-size: 12px; color: #9ca3af;'>📍 " + item.hippodrome + "</span>"
                        : ""
                    }
                </td>
                <td style="padding: 12px; color: #10b981; font-weight: bold;">${favori}</td>
                <td style="padding: 12px; color: #fff;">${selection}</td>
                <td style="padding: 12px; color: #e5e7eb;">${resultat}</td>
            </tr>
        `;
    });
}

async function chargerHistorique(){try{const r=await fetch("https://az-turf-pro.onrender.com/api/historique");if(!r.ok)throw new Error("Erreur API historique");const d=await r.json(),h=fusionnerHistoriqueBackend(d.historique||[]);afficherHistorique(h);const total=document.getElementById("total-courses");if(total)total.textContent=h.length;const fav=document.getElementById("favoris-gagnants");if(fav)fav.textContent=h.filter(x=>Array.isArray(x.arrivee)&&x.arrivee.length&&x.favori?.numero&&Number(x.arrivee[0])===Number(x.favori.numero)).length;}catch(e){const h=chargerHistoriqueLocal();afficherHistorique(h);const total=document.getElementById("total-courses");if(total)total.textContent=h.length;console.log("Erreur historique :",e);}}

document.addEventListener("DOMContentLoaded",()=>{if(document.getElementById("historique-body"))chargerHistorique();});
            
