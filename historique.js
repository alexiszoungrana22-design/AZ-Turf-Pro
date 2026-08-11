
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

function ajouterCourseHistorique(data){
    if(!data || data.donnees_demo){
        return chargerHistoriqueLocal();
    }

    const historique =
        chargerHistoriqueLocal();

    const cle =
        cleCourse(data);

    const maintenant =
        new Date().toISOString();

    const index =
        historique.findIndex(
            item => item.cle === cle
        );

    const entree = {
        cle,
        date: data.date || "",
        reunion: data.reunion || "",
        course_numero: data.course_numero || "",
        course: data.course || "Course",
        hippodrome: data.hippodrome || "",
        discipline: data.discipline || "",
        distance: data.distance || "",
        source: data.source || "",
        date_enregistrement: maintenant,
        favori: data.favori || {},
        selection: data.tickets?.gratuit?.quinte || [],
        classement: data.classement || [],
        arrivee: index >= 0
            ? (historique[index].arrivee || [])
            : [],
        rapports: index >= 0
            ? (historique[index].rapports || [])
            : []
    };

    if(index >= 0){
        historique[index] = {
            ...historique[index],
            ...entree,
            date_enregistrement:
                historique[index].date_enregistrement ||
                maintenant
        };
    }else{
        historique.unshift(entree);
    }

    // On conserve les 100 dernières courses.
    const limite = historique.slice(0, 100);

    sauvegarderHistoriqueLocal(limite);

    return limite;
}

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
                <td colspan="5">
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
            <tr>
                <td>${item.date || "-"}</td>
                <td>
                    ${item.course || "-"}
                    ${
                        item.hippodrome
                        ? "<br>📍 " + item.hippodrome
                        : ""
                    }
                </td>
                <td>${favori}</td>
                <td>${selection}</td>
                <td>${resultat}</td>
            </tr>
        `;
    });
}

async function chargerHistorique(){
    try{
        const response =
            await fetch(API);

        if(!response.ok){
            throw new Error(
                "Erreur API"
            );
        }

        const data =
            await response.json();

        const historique =
            ajouterCourseHistorique(data);

        afficherHistorique(historique);

        const total =
            document.getElementById(
                "total-courses"
            );

        if(total){
            total.textContent =
                historique.length;
        }

        const favoris =
            document.getElementById(
                "favoris-gagnants"
            );

        if(favoris){
            const nombre =
                historique.filter(
                    item =>
                        Array.isArray(item.arrivee) &&
                        item.arrivee.length &&
                        item.favori?.numero &&
                        Number(item.arrivee[0]) ===
                        Number(item.favori.numero)
                ).length;

            favoris.textContent = nombre;
        }

        const tickets =
            document.getElementById(
                "tickets-reussis"
            );

        if(tickets){
            tickets.textContent = "—";
        }

    }catch(error){
        console.log(
            "Erreur historique :",
            error
        );

        const historique =
            chargerHistoriqueLocal();

        afficherHistorique(historique);

        const total =
            document.getElementById(
                "total-courses"
            );

        if(total){
            total.textContent =
                historique.length;
        }
    }
}

document.addEventListener(
    "DOMContentLoaded",
    chargerHistorique
);
