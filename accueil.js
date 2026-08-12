const API = "https://az-turf-pro.onrender.com/api/analyse";

async function chargerAnalyse(){
    try {
        const response = await fetch(API);
        if(!response.ok){
            throw new Error("Erreur API");
        }

        const data = await response.json();

        afficherChronometre(data);

        const chevauxClassement = data.classement || data.chevaux || [];
        const chevaux = [...chevauxClassement].sort((a, b) => Number(a.numero || 0) - Number(b.numero || 0));
        const classement = [...chevauxClassement].sort((a, b) => Number(a.rang || 0) - Number(b.rang || 0));

        function afficher(id, valeur){
            const element = document.getElementById(id);
            if(element){
                element.textContent = valeur || "-";
            }
        }

        afficher("meta-hippodrome", data.hippodrome);
        afficher("meta-course", data.course);
        afficher("meta-discipline", data.discipline);
        afficher("meta-distance", data.distance ? data.distance + " m" : "-");
        afficher("meta-partants", data.partants);

        const popular = document.getElementById("popular-horses");
        if(popular){
            const plusJoues = data.plus_joues || [];
            if(plusJoues.length){
                popular.innerHTML = plusJoues.map(numero => `<div class="popular-number">${numero}</div>`).join("");
            } else {
                popular.innerHTML = "Plus joue indisponible";
            }
        }

        const tendance = document.getElementById("course-tendance");
        if(tendance && classement.length){
            tendance.innerHTML = `
                <p>Chevaux les plus joues : <strong>${(data.plus_joues || []).join(" - ")}</strong></p>
                <p>Favori AZ : <strong>NÂ°${classement[0].numero}</strong> avec un indice AZ de <strong>${classement[0].indice_az || "-"}</strong></p>
                <p>La tendance est basÃ©e sur la forme, la rÃ©gularitÃ© et le classement AZ.</p>
            `;
        }

        const favori = classement[0];
        if(favori){
            afficher("favori-numero", favori.numero);
            afficher("favori-nom", favori.nom);
            afficher("favori-indice", favori.indice_az);
            afficher("favori-confiance", (favori.confiance || "-") + " %");
            afficher("favori-raison", favori.raison || "Favori AZ");
        }

        const outsider = classement[6];
        if(outsider){
            afficher("outsider-numero", outsider.numero);
            afficher("outsider-nom", outsider.nom);
            afficher("outsider-indice", outsider.indice_az);
            afficher("outsider-confiance", (outsider.confiance || "-") + " %");
            afficher("outsider-raison", outsider.raison || "Outsider AZ");
        }

        const tableau = document.getElementById("all-horses") || document.getElementById("corps-tableau-partants");
        if(tableau){
            tableau.innerHTML = "";
            chevaux.forEach(cheval => {
                const numero = cheval.numero ?? "-";
                const jockey = cheval.jockey || cheval.driver || cheval.pilote || "-";
                const entraineur = cheval.entraineur || cheval.trainer || "-";
                const cote = cheval.cote_brute ?? cheval.rapport ?? cheval.cote ?? "-";

                tableau.innerHTML += `
                    <tr>
                        <td><strong>${numero}</strong></td>
                        <td>${cheval.nom || "-"}</td>
                        <td>${jockey}</td>
                        <td>${entraineur}</td>
                        <td><span class="badge-cote">${cote}</span></td>
                    </tr>
                `;
            });
        }

        const tickets = data.tickets?.gratuit || {};
        afficher("quinte-gratuit", (tickets.quinte || []).join(" - "));
        afficher("deux-sur-quatre", (tickets.deux_sur_quatre || []).join(" - "));

        const couple = document.getElementById("couple-place-gratuit");
        if(couple){
            couple.innerHTML = (tickets.couple_place || []).map(c => c.join(" - ")).join(" | ");
        }

        afficherConfianceCourse(data);
        afficherChevauxSurveiller(data);

    } catch(error) {
        console.log("Erreur analyse :", error);
    }
}

function normaliserHeureDepart(valeur){
    if(!valeur) return null;
    let texte = String(valeur).trim().toLowerCase();
    texte = texte.replace(/h/g, ":").replace(/m/g, ":").replace(/\s+/g, "");
    const morceaux = texte.split(":").filter(Boolean);
    if(morceaux.length < 2) return null;
    const heures = parseInt(morceaux[0], 10);
    const minutes = parseInt(morceaux[1], 10);
    if(isNaN(heures) || isNaN(minutes) || heures > 23 || minutes > 59) return null;
    return { heures, minutes, secondes: 0 };
}

function afficherChronometre(data){
    const zone = document.getElementById("mini-countdown");
    if(!zone) return;

    const heureBrute = (data.horaires && data.horaires.depart) ? data.horaires.depart : data.heure_depart;
    const heure = normaliserHeureDepart(heureBrute);

    if(!heure){
        zone.textContent = "Depart : heure indisponible";
        return;
    }

    if(window.chronoTimer) clearInterval(window.chronoTimer);

    function mettreAJour() {
        const maintenant = new Date();
        const depart = new Date();
        depart.setHours(heure.heures, heure.minutes, 0, 0);

        const quatreHeuresPlusTard = new Date(depart.getTime() + (4 * 60 * 60 * 1000));
        
        if (maintenant > quatreHeuresPlusTard) {
            zone.textContent = "Course terminee";
            return;
        }

        let diff = depart.getTime() - maintenant.getTime();
        if (diff <= 0) {
            zone.textContent = "Depart imminent";
            return;
        }

        const h = Math.floor(diff / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        const s = Math.floor((diff % 60000) / 1000);
        zone.textContent = `Depart dans ${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    mettreAJour();
    window.chronoTimer = setInterval(mettreAJour, 1000);
}

const publicites = [
    { image: "images/pub1.jpg", titre: "AZ Turf Pro Premium", texte: "Analyses specialisees et tickets exclusifs" },
    { image: "images/pub2.jpg", titre: "Analyse du Quinte", texte: "Des pronostics bases sur les performances" },
    { image: "images/pub3.jpg", titre: "Abonnement Premium", texte: "Accedez aux selections avancees" },
    { image: "images/pub4.jpg", titre: "Votre publicite ici", texte: "Un espace dedie aux partenaires" },
    { image: "images/pub5.jpg", titre: "AZ Turf Pro", texte: "Une analyse professionnelle au service des pronostics" }
];

let indexPub = 0;

function changerPublicite(){
    const image = document.getElementById("pub-image");
    const titre = document.getElementById("pub-title");
    const texte = document.getElementById("pub-text");
    const points = document.querySelectorAll(".dot");

    if(!image) return;

    indexPub++;
    if(indexPub >= publicites.length){
        indexPub = 0;
    }

    image.style.opacity = "0";

    setTimeout(() => {
        image.src = publicites[indexPub].image;
        if(titre) titre.innerHTML = publicites[indexPub].titre;
        if(texte) texte.innerHTML = publicites[indexPub].texte;

        points.forEach((point, i) => {
            point.classList.toggle("active", i === indexPub);
        });

        image.style.opacity = "1";
    }, 400);
}

function afficherConfianceCourse(data){
    const indice = document.getElementById("indice-confiance");
    const message = document.getElementById("message-confiance");

    if(!indice) return;

    let confiance = data.favori?.confiance || 0;
    indice.innerHTML = confiance + "%";

    if(message){
        if(confiance >= 80){
            message.innerHTML = "Course avec un niveau de confiance eleve";
        } else if(confiance >= 60){
            message.innerHTML = "Course avec quelques incertitudes";
        } else {
            message.innerHTML = "Course ouverte, prudence recommandee";
        }
    }
}

function afficherChevauxSurveiller(data){
    const zone = document.getElementById("chevaux-surveiller");
    if(!zone) return;

    const classement = data.classement || [];
    if(classement.length === 0){
        zone.innerHTML = "Analyse en cours...";
        return;
    }

    const meilleurIndice = classement[0].indice_az || 0;
    const SEUIL_MENACE = 0.70;

    let candidats = classement
        .filter(c => c.rang > 2)
        .filter(c => meilleurIndice > 0 && (c.indice_az || 0) >= meilleurIndice * SEUIL_MENACE)
        .sort((a, b) => (b.indice_az || 0) - (a.indice_az || 0))
        .slice(0, 3);

    if(candidats.length === 0){
        candidats = classement.filter(c => c.rang > 2).slice(0, 3);
    }

    if(candidats.length === 0){
        zone.innerHTML = "Analyse en cours...";
        return;
    }

    zone.innerHTML = candidats.map(c => {
        const ecart = meilleurIndice > 0 ? Math.round((c.indice_az || 0) / meilleurIndice * 100) : 0;
        return `
            <p>
                NÂ°${c.numero} ${c.nom || ""}
                <br>
                ${c.raison || "Cheval a surveiller"}
                <br>
                ${ecart}% de l'indice du leader - capable de creer la surprise
            </p>
        `;
    }).join("");
}

document.addEventListener("DOMContentLoaded", () => {
    chargerAnalyse();
    setInterval(changerPublicite, 4000);
});


<script src="tri-partants.js"></script>
