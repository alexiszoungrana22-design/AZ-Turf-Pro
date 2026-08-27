const API = "https://az-turf-pro.onrender.com/api/analyse";

function badgeTendance(cheval){
    const signal = String(cheval && cheval.signal_marche || "NEUTRE");
    if(signal.includes("SMART_MONEY")) return '<span title="Gros mouvement d\'argent sur ce cheval">🔥</span>';
    if(signal.includes("SOUTENU")) return '<span title="Cote en baisse, cheval soutenu">📈</span>';
    if(signal.includes("DELAISSE")) return '<span title="Cote en hausse, cheval délaissé">📉</span>';
    return '<span style="color:#cbd5e1;">–</span>';
}

function enregistrerAnalyseDansHistorique(data){
    if(!data || data.donnees_demo) return;
    try{
        const key="AZ_TURF_HISTORIQUE_COURSES_V1"; 
        const h=JSON.parse(localStorage.getItem(key)||"[]");
        const cle=[data.date||"",data.reunion||"",data.course_numero||"",data.course||""].join("|");
        const i=h.findIndex(x=>x.cle===cle); 
        const old=i>=0?h[i]:{};
        const e={
            ...old,
            cle,
            date:data.date||"",
            reunion:data.reunion||"",
            course_numero:data.course_numero||"",
            course:data.course||"Course",
            hippodrome:data.hippodrome||"",
            discipline:data.discipline||"",
            distance:data.distance||"",
            source:data.source||"",
            date_enregistrement:old.date_enregistrement||new Date().toISOString(),
            favori:data.favori||old.favori||{},
            selection:data.tickets?.gratuit?.quinte||old.selection||[],
            premium:data.tickets?.premium||old.premium||{},
            classement:data.classement||old.classement||[],
            arrivee:old.arrivee||[],
            rapports:old.rapports||[]
        };
        if(i>=0) h[i]=e; else h.unshift(e); 
        localStorage.setItem(key,JSON.stringify(h.slice(0,100)));
    }catch(e){console.log("Historique local indisponible",e);}
}

async function chargerAnalyse(){
    try {
        const response = await fetch(API);
        if(!response.ok){
            throw new Error("Erreur API");
        }

        const data = await response.json();
        window.courseDuJourData = data;
        enregistrerAnalyseDansHistorique(data);
        afficherHeureDepartCourse(data);
        afficherChronometre(data);

        const chevauxClassement = data.classement || data.chevaux || [];
        const chevauxSource = data.partants_complets || data.chevaux || chevauxClassement;
        const nonPartants = new Set((data.non_partants || []).map(n => String(n)));
        const chevaux = [...chevauxSource].sort((a, b) => Number(a.numero || 0) - Number(b.numero || 0));
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
                popular.innerHTML = "Plus joué indisponible";
            }
        }

        const tendance = document.getElementById("course-tendance");
        if(tendance && classement.length){
            tendance.innerHTML = `
                <p>Chevaux les plus joués : <strong>${(data.plus_joues || []).join(" - ")}</strong></p>
                <p>Favori AZ : <strong>N°${classement[0].numero}</strong> avec un indice AZ de <strong>${classement[0].indice_az ? Math.round(classement[0].indice_az) : "-"}</strong></p>
                <p>La tendance est basée sur la forme, la régularité et le classement AZ.</p>
            `;
        }

        const favori = classement[0];
        if(favori){
            afficher("favori-numero", favori.numero);
            afficher("favori-nom", favori.nom);
            afficher("favori-indice", favori.indice_az ? Math.round(favori.indice_az) : "-");
            afficher("favori-confiance", (favori.confiance || "-") + " %");
            afficher("favori-raison", favori.raison || "Favori AZ");
        }

        const outsider = classement[6] || classement[3];
        if(outsider){
            afficher("outsider-numero", outsider.numero);
            afficher("outsider-nom", outsider.nom);
            afficher("outsider-indice", outsider.indice_az ? Math.round(outsider.indice_az) : "-");
            afficher("outsider-confiance", (outsider.confiance || "-") + " %");
            afficher("outsider-raison", outsider.raison || "Outsider AZ");
        }

        // TABLEAU DES PARTANTS
        const tableau = document.getElementById("all-horses") || document.getElementById("corps-tableau-partants");
        if(tableau){
            tableau.innerHTML="";
            chevaux.forEach(cheval=>{
                const numero=cheval.numero??"-", nom=cheval.nom||"-";
                const jockey=cheval.jockey||cheval.driver||"-";
                const entraineur=cheval.entraineur||cheval.trainer||"-";
                const cote=cheval.cote_brute??cheval.rapport??"-";
                const indice=cheval.indice_az!=null?Math.round(cheval.indice_az):"-";
                const confiance=cheval.confiance!=null?cheval.confiance+" %":"-";
                const estNonPartant = nonPartants.has(String(numero)) || cheval.non_partant === true || String(cheval.statut || "").toUpperCase().includes("NON_PARTANT") || String(cheval.statut || "").toUpperCase() === "NP";
                const styleNP = estNonPartant ? ' style="background:#ffe3e3;color:#b00020;font-weight:700"' : '';
                const nomAffiche = estNonPartant ? `${nom} <span style="color:#c00020;font-weight:800">— NON PARTANT</span>` : nom;
                const tendance = badgeTendance(cheval);
                tableau.innerHTML+=`<tr${styleNP}><td><strong>${numero}</strong></td><td>${nomAffiche}</td><td>${jockey}</td><td>${entraineur}</td><td>${cote}</td><td><span class="badge-indice">${indice}</span></td><td>${confiance}</td><td>${tendance}</td></tr>`;
            });
        }

        const tickets = data.tickets?.gratuit || {};
        afficher("quinte-gratuit", (tickets.quinte || []).join(" - "));
        afficher("deux-sur-quatre", (tickets.deux_sur_quatre || []).join(" - "));

        const couple = document.getElementById("couple-place-gratuit");
        if(couple){
            couple.innerHTML = (tickets.couple_place || []).join(" - ");
        }

        afficherConfianceCourse(data);
        afficherChevauxSurveiller(data);

    } catch(error) {
        console.log("Erreur analyse :", error);
    }
}

// =====================================
// FONCTION CORRIGÉE POUR L'HEURE DE DÉPART
// =====================================
function normaliserHeureDepart(valeur){
    if(valeur === null || valeur === undefined || valeur === "") return null;

    // 1. Si c'est un Timestamp (millisecondes ou secondes) ou nombre
    if (typeof valeur === "number" || (!isNaN(valeur) && String(valeur).trim().length >= 10 && !String(valeur).includes(":"))) {
        let ts = Number(valeur);
        if (ts < 10000000000) ts *= 1000; // Conversion secondes -> millisecondes
        const d = new Date(ts);
        if (!isNaN(d.getTime())) {
            return { heures: d.getHours(), minutes: d.getMinutes(), secondes: d.getSeconds(), dateComplete: d };
        }
    }

    let texte = String(valeur).trim();

    // 2. Si c'est un format Date ISO / Horodatage complet (ex: "2026-08-13T13:50:00")
    if (texte.includes("-") || texte.includes("T")) {
        const d = new Date(texte);
        if (!isNaN(d.getTime())) {
            return { heures: d.getHours(), minutes: d.getMinutes(), secondes: d.getSeconds(), dateComplete: d };
        }
    }

    // 3. Si format 4 chiffres (ex: 1350 ou "1350" pour 13h50)
    if (/^\d{4}$/.test(texte)) {
        const h = parseInt(texte.substring(0, 2), 10);
        const m = parseInt(texte.substring(2, 4), 10);
        if (h <= 23 && m <= 59) return { heures: h, minutes: m, secondes: 0 };
    }

    // 4. Formats textes classiques ("13h50", "13:50", "13h 50m")
    texte = texte.toLowerCase().replace(/h/g, ":").replace(/m/g, "").replace(/\s+/g, "");
    const morceaux = texte.split(":").filter(Boolean);
    if(morceaux.length >= 2){
        const h = parseInt(morceaux[0], 10);
        const m = parseInt(morceaux[1], 10);
        if(!isNaN(h) && !isNaN(m) && h <= 23 && m <= 59){
            return { heures: h, minutes: m, secondes: 0 };
        }
    }

    return null;
}

// =====================================
// FONCTION CORRIGÉE DU CHRONOMÈTRE
// =====================================
function afficherHeureDepartCourse(data){
    const zone = document.getElementById("heure-depart-course");
    if(!zone) return;

    const heureBrute = (data.horaires && data.horaires.depart) || data.heure_depart || data.heure || "";
    const heure = normaliserHeureDepart(heureBrute);
    if(!heure){
        zone.textContent = "Départ : --:--";
        return;
    }

    zone.textContent = `Départ : ${String(heure.heures).padStart(2,"0")}:${String(heure.minutes).padStart(2,"0")}`;
}

function afficherChronometre(data){
    const zone = document.getElementById("mini-countdown");
    if(!zone) return;

    const heureBrute = (data.horaires && data.horaires.depart) || data.heure_depart || data.heure || "";
    const heure = normaliserHeureDepart(heureBrute);
    if(!heure){
        zone.textContent = "Départ : heure indisponible";
        return;
    }

    if(window.chronoTimer) clearInterval(window.chronoTimer);

    function dateCourseDepuisAPI(){
        const brut = String(data.date || "").trim();
        if(/^\d{8}$/.test(brut)){
            const jj=Number(brut.slice(0,2)), mm=Number(brut.slice(2,4))-1, aa=Number(brut.slice(4,8));
            return new Date(aa,mm,jj,heure.heures,heure.minutes,heure.secondes||0,0);
        }
        const d = new Date(brut);
        if(!isNaN(d.getTime())){
            d.setHours(heure.heures,heure.minutes,heure.secondes||0,0);
            return d;
        }
        const d2 = new Date();
        d2.setHours(heure.heures,heure.minutes,heure.secondes||0,0);
        return d2;
    }

    const depart = heure.dateComplete || dateCourseDepuisAPI();

    function mettreAJour(){
        const maintenant = new Date();
        const diff = depart.getTime() - maintenant.getTime();
        if(diff > 0){
            const h=Math.floor(diff/3600000);
            const m=Math.floor((diff%3600000)/60000);
            const s=Math.floor((diff%60000)/1000);
            zone.textContent=`Départ dans ${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
            return;
        }

        // Après le départ, ne jamais rester bloqué sur « Départ imminent ».
        const ecoule = maintenant.getTime() - depart.getTime();
        if(ecoule <= 2*60*60*1000){
            zone.textContent = "🏇 Course en cours";
        }else{
            zone.textContent = "🏁 Course terminée";
            clearInterval(window.chronoTimer);
        }
    }

    mettreAJour();
    window.chronoTimer=setInterval(mettreAJour,1000);
}

const publicites = [
    { image: "images/pub1.jpg", titre: "AZ Turf Pro Premium", texte: "Analyses spécialisées et tickets exclusifs" },
    { image: "images/pub2.jpg", titre: "Analyse du Quinté", texte: "Des pronostics basés sur les performances" },
    { image: "images/pub3.jpg", titre: "Abonnement Premium", texte: "Accédez aux sélections avancées" },
    { image: "images/pub4.jpg", titre: "Votre publicité ici", texte: "Un espace dédié aux partenaires" },
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
            message.innerHTML = "Course avec un niveau de confiance élevé";
        } else if(confiance >= 60){
            message.innerHTML = "Course avec quelques incertitudes";
        } else {
            message.innerHTML = "Course ouverte, prudence recommandée";
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
                N°${c.numero} ${c.nom || ""}
                <br>
                ${c.raison || "Cheval à surveiller"}
                <br>
                ${ecart}% de l'indice du leader - capable de créer la surprise
            </p>
        `;
    }).join("");
}


// =====================================
// QUINTÉ HIER / JOUR / DEMAIN
// =====================================
let quintesPeriodes = {};
let periodeActive = "jour";

function textePeriode(periode){
    return periode === "hier" ? "d'hier" : periode === "demain" ? "de demain" : "du jour";
}

function afficherResumeQuinte(periode){
    periodeActive = periode;
    const data = periode === "jour" ? window.courseDuJourData : quintesPeriodes[periode];

    document.querySelectorAll(".clone-tab").forEach(tab => {
        tab.classList.toggle("active", tab.dataset.periode === periode);
    });

    const label = document.getElementById("periode-course-label");
    if(label) label.textContent = textePeriode(periode);

    if(!data || data.disponible === false){
        ["meta-course","meta-nom-prix","meta-date","meta-discipline","meta-distance","meta-partants","meta-hippodrome","heure-depart-course"].forEach(id => {
            const el = document.getElementById(id);
            if(el) el.textContent = id === "heure-depart-course" ? "Départ : indisponible" : "Donnée indisponible";
        });
        return;
    }

    const afficher = (id, valeur) => {
        const el = document.getElementById(id);
        if(el) el.textContent = valeur ?? "-";
    };

    afficher("meta-course", data.course || "Quinté+");
    afficher("meta-nom-prix", data.nom_prix || data.course || "");
    afficher("meta-date", data.date || "");
    afficher("meta-discipline", data.discipline || "-");
    afficher("meta-distance", data.distance ? `${data.distance} m` : "-");
    afficher("meta-partants", data.partants || "-");
    afficher("meta-hippodrome", data.hippodrome || "-");
    afficherHeureDepartCourse(data);
}

async function chargerQuintesPeriodes(){
    const tabs = document.querySelectorAll(".clone-tab[data-periode]");
    if(!tabs.length) return;

    try{
        const response = await fetch("https://az-turf-pro.onrender.com/api/quintes-periodes");
        if(!response.ok) throw new Error("Erreur API Quinté périodes");
        quintesPeriodes = await response.json();
    }catch(error){
        console.log("Quinté hier/demain indisponible", error);
        quintesPeriodes = {};
    }

    tabs.forEach(tab => {
        tab.addEventListener("click", () => afficherResumeQuinte(tab.dataset.periode));
    });

    // Le jour reste l'onglet actif par défaut et continue d'être alimenté
    // par /api/analyse comme avant.
    afficherResumeQuinte("jour");
}

document.addEventListener("DOMContentLoaded", () => {
    chargerAnalyse();
    chargerQuintesPeriodes();
    setInterval(changerPublicite, 4000);
});
                                                                                                               


async function chargerActualitesHippiques(){
    const zone=document.getElementById('home-news'), status=document.getElementById('news-status'), sources=document.getElementById('news-sources');
    if(!zone) return;
    try{
        const r=await fetch('/api/actualites?limit=10',{cache:'no-store'}); const d=await r.json();
        const items=d.actualites||[];
        if(status) status.textContent=items.length?'● En direct':'● Sources indisponibles';
        zone.innerHTML=items.length?items.map(a=>`<a class="news-item" href="${a.url}" target="_blank" rel="noopener noreferrer"><span class="news-source">${a.source||'Source hippique'}</span><div class="news-title">${a.titre}</div><span class="news-more">Lire la source →</span></a>`).join(''):'<div class="news-skeleton">Les sources d’actualité ne sont pas disponibles pour le moment. Aucun contenu n’est inventé.</div>';
        if(sources && d.sources) sources.innerHTML=d.sources.map(x=>`<a href="${x.url}" target="_blank" rel="noopener noreferrer">Source : ${x.nom}</a>`).join(' · ');
    }catch(e){ zone.innerHTML='<div class="news-skeleton">Actualités indisponibles momentanément. Consultez les sources officielles.</div>'; if(status) status.textContent='● Indisponible'; }
}

function enrichirTableauDeBordAccueil(data){
    const c=(data.classement||data.chevaux||[]); const fav=c[0], out=c[6]||c[3];
    const set=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v||'—'};
    set('day-course',data.course||'Course du jour'); set('day-course-meta',[data.hippodrome,data.discipline,data.distance?data.distance+' m':''].filter(Boolean).join(' · '));
    set('day-favori',fav?`N°${fav.numero} ${fav.nom||''}`:'—'); set('day-favori-meta',fav?`Indice ${Math.round(fav.indice_az||0)} · ${fav.confiance||'—'} %`:'—');
    set('day-outsider',out?`N°${out.numero} ${out.nom||''}`:'—'); set('day-outsider-meta',out?`Indice ${Math.round(out.indice_az||0)} · ${out.confiance||'—'} %`:'—');
}
const _chargerAnalyseAccueil=chargerAnalyse;
chargerAnalyse=async function(){ await _chargerAnalyseAccueil(); enrichirTableauDeBordAccueil(window.courseDuJourData||{}); chargerActualitesHippiques(); };
