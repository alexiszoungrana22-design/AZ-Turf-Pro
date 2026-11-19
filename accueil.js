const API = window.azApiUrl('/api/analyse');

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
        const response = await fetch(API, { cache: "no-store" });
        if(!response.ok){
            throw new Error("Erreur API");
        }

        const data = await response.json();
        window.courseDuJourData = data;
        enregistrerAnalyseDansHistorique(data);
        afficherHeureDepartCourse(data);
        afficherChronometre(data);

        // La réponse PMU réelle utilise notamment "course", "partants" et "chevaux".
        // Sécuriser les tableaux pour éviter qu'un champ absent bloque tout l'affichage.
        const chevauxAPI = Array.isArray(data.chevaux) ? data.chevaux : [];
        const classementAPI = Array.isArray(data.classement) ? data.classement : chevauxAPI;
        const partantsCompletsAPI = Array.isArray(data.partants_complets) ? data.partants_complets : [];
        const chevauxClassement = classementAPI;
        const chevauxSource = partantsCompletsAPI.length ? partantsCompletsAPI : (chevauxAPI.length ? chevauxAPI : classementAPI);
        const nonPartants = new Set((Array.isArray(data.non_partants) ? data.non_partants : []).map(n => String(n)));
        const chevaux = [...chevauxSource].sort((a, b) => Number(a.numero || 0) - Number(b.numero || 0));
        const classement = [...chevauxClassement].sort((a, b) => Number(a.rang || 0) - Number(b.rang || 0));

        function afficher(id, valeur){
            const element = document.getElementById(id);
            if(element){
                element.textContent = valeur || "-";
            }
        }

        // Le titre réel de la course est dans "course". "nom_prix" peut
        // contenir un code de réunion/course (ex. R1/C6) et ne doit pas le remplacer.
        afficher("meta-hippodrome", data.hippodrome);
        afficher("meta-course", data.course || data.nom_course || data.nom_prix);
        afficher("meta-nom-prix", (data.nom_prix && !/^R\d+\/C\d+$/i.test(String(data.nom_prix).trim())) ? data.nom_prix : "");
        // Libellé public : éviter d'afficher les codes techniques de la source PMU.
        const disciplinesLisibles = {
            "ATTELE_TROT_ATTELE": "Trot attelé",
            "MONTE_TROT_MONTE": "Trot monté",
            "PLAT_GALOP_PLAT": "Galop - plat",
            "OBSTACLE_HAIES": "Obstacle - haies",
            "OBSTACLE_STEEPLE": "Obstacle - steeple-chase"
        };
        const disciplineBrute = String(data.discipline || "").trim();
        const disciplineAffichee = disciplinesLisibles[disciplineBrute.toUpperCase()] || disciplineBrute.replace(/_/g, " ").toLowerCase().replace(/(^|\s)\S/g, c => c.toUpperCase());
        afficher("meta-discipline", disciplineAffichee);
        afficher("meta-distance", data.distance ? data.distance + " m" : "-");
        // Le compteur de partants utilise le champ API s'il est numérique,
        // sinon le nombre réel de chevaux reçus dans la liste.
        const partantsAPI = Number.parseInt(data.partants, 10);
        const nombrePartants = Number.isFinite(partantsAPI) && partantsAPI > 0
            ? partantsAPI
            : chevaux.length;
        afficher("meta-partants", nombrePartants > 0 ? nombrePartants : "Partants indisponibles");

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

        // Liste des partants : tri fonctionnel sur les données réelles, sans manipuler le DOM comme un tableau HTML.
        window.azHomePartantsData = Array.isArray(chevaux) ? chevaux.slice() : [];
        window.azHomeNonPartants = Array.from(nonPartants);
        afficherListePartantsAccueil(window.azHomePartantsData);

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
        console.error("Erreur analyse AZ Turf Pro :", error);
        const titre = document.getElementById("meta-course");
        const infos = document.querySelector(".clone-info-text");
        if(titre && !titre.textContent.trim()) titre.textContent = "Données de course momentanément indisponibles";
        if(infos && !infos.textContent.trim()) infos.textContent = "Vérifiez la connexion aux données PMU puis actualisez la page.";
        const heure = document.getElementById("heure-depart-course");
        if(heure) heure.textContent = "Départ : données indisponibles";
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

    // La confiance du favori mesure seulement sa proximité au meilleur indice.
    // Elle ne doit jamais être présentée comme la qualité de toute la course.
    const qualite = data && data.qualite_donnees_pourcentage;
    const effectif = Number(data && data.qualite_donnees_effectif || 0);
    const valeur = (qualite !== null && qualite !== undefined && Number.isFinite(Number(qualite)))
        ? Math.max(0, Math.min(100, Math.round(Number(qualite))))
        : null;

    indice.textContent = valeur === null ? "Non évaluée" : valeur + "%";
    if(message){
        if(valeur === null || effectif === 0){
            message.textContent = "Qualité non calculable : les indicateurs de provenance des données ne sont pas disponibles.";
        } else if(valeur >= 80){
            message.textContent = `Données bien documentées (${effectif} partants évalués). Cet indicateur mesure la disponibilité des données, pas une chance de victoire.`;
        } else if(valeur >= 60){
            message.textContent = `Données partiellement documentées (${effectif} partants évalués). Certaines informations sont manquantes.`;
        } else {
            message.textContent = `Données peu documentées (${effectif} partants évalués). Prudence : plusieurs informations manquent.`;
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
// QUINTÉ DU JOUR UNIQUEMENT
// La course du jour est chargée par /api/analyse dans chargerAnalyse().
// Les fenêtres hier et demain ont été retirées de l'accueil.
// =====================================

// Tri et affichage des partants de l'accueil (V19).
window.azHomePartantsSort = window.azHomePartantsSort || "numero";
function valeurCoteAccueil(cheval){
    const brut = cheval && (cheval.cote_direct ?? cheval.cote_brute ?? cheval.cote ?? cheval.rapport);
    if (brut === null || brut === undefined || brut === "") return Number.POSITIVE_INFINITY;
    const n = Number(String(brut).replace(/\s/g, "").replace(",", ".").replace(/[^0-9.]/g, ""));
    return Number.isFinite(n) && n > 0 ? n : Number.POSITIVE_INFINITY;
}
function afficherListePartantsAccueil(source){
    const zone = document.getElementById("all-horses");
    if(!zone) return;
    const echapper = valeur => String(valeur ?? "-").replace(/[&<>"']/g, c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
    const chevaux = (Array.isArray(source) ? source : []).slice();
    if(window.azHomePartantsSort === "cote"){
        chevaux.sort((a,b) => valeurCoteAccueil(a)-valeurCoteAccueil(b) || (Number(a.numero)||9999)-(Number(b.numero)||9999));
    } else {
        chevaux.sort((a,b) => (Number(a.numero)||9999)-(Number(b.numero)||9999));
    }
    const compteur = document.getElementById("home-partants-count");
    if(compteur) compteur.textContent = `${chevaux.length} partant${chevaux.length > 1 ? "s" : ""}`;
    if(!chevaux.length){ zone.innerHTML='<div class="home-partants-loading">Aucun partant disponible pour cette course.</div>'; return; }
    zone.innerHTML = chevaux.map(cheval => {
        const numero = cheval.numero ?? "-";
        const nom = cheval.nom || cheval.nom_cheval || "Cheval sans nom";
        const jockey = cheval.jockey || cheval.driver || cheval.driver_nom || "";
        const entraineur = cheval.entraineur || cheval.trainer || "";
        const cote = cheval.cote_direct ?? cheval.cote_brute ?? cheval.cote ?? cheval.rapport ?? null;
        const indice = cheval.indice_az != null ? Math.round(cheval.indice_az) : null;
        const confiance = cheval.confiance != null ? cheval.confiance : null;
        const musique = cheval.musique_brute || cheval.musique || cheval.forme || "";
        const gains = cheval.gains_carriere_brute || cheval.gains || "";
        const age = cheval.age ?? "";
        const sexe = cheval.sexe ?? "";
        const poids = cheval.poids ?? cheval.poids_monte ?? "";
        const corde = cheval.corde ?? cheval.numero_corde ?? "";
        const estNonPartant = (window.azHomeNonPartants || []).includes(String(numero)) || cheval.non_partant === true || String(cheval.statut || "").toUpperCase().includes("NON_PARTANT") || String(cheval.statut || "").toUpperCase() === "NP";
        const casaque = cheval.casaque_url || cheval.url_casaque || cheval.casaque || "";
        const casaqueHtml = /^https?:\/\//i.test(String(casaque)) ? `<img class="home-horse-silk" src="${echapper(casaque)}" alt="Casaque" loading="lazy">` : `<span class="home-horse-silk home-horse-silk-fallback" aria-hidden="true">🏇</span>`;
        const tendance = badgeTendance(cheval);
        const meta = [sexe, age ? `${age} ans` : "", poids ? `${poids}kg` : "", corde ? `Corde ${corde}` : ""].filter(Boolean).join(" · ");
        const details = [jockey ? `<span>Jockey <strong>${echapper(jockey)}</strong></span>` : "", entraineur ? `<span>Entraîneur <strong>${echapper(entraineur)}</strong></span>` : ""].filter(Boolean).join('<i aria-hidden="true">·</i>');
        const indicateurs = [
            musique ? `<span class="home-horse-chip music" title="Musique">${echapper(musique)}</span>` : "",
            indice !== null ? `<span class="home-horse-chip index">AZ ${echapper(indice)}</span>` : "",
            confiance !== null ? `<span class="home-horse-chip confidence">${echapper(confiance)}% confiance</span>` : "",
            gains ? `<span class="home-horse-chip gains">Gains ${echapper(gains)}</span>` : ""
        ].filter(Boolean).join("");
        return `<article class="home-horse-row${estNonPartant ? " is-non-runner" : ""}">
          <span class="home-horse-number">${echapper(numero)}</span>
          <div class="home-horse-silk-wrap">${casaqueHtml}</div>
          <div class="home-horse-content">
            <div class="home-horse-title"><strong>${echapper(nom)}</strong>${estNonPartant ? '<span class="home-horse-np">NON PARTANT</span>' : ""}</div>
            ${meta ? `<div class="home-horse-meta">${echapper(meta)}</div>` : ""}
            <div class="home-horse-people">${details || '<span>Jockey et entraîneur non renseignés</span>'}</div>
            ${indicateurs ? `<div class="home-horse-indicators">${indicateurs}</div>` : ""}
          </div>
          <div class="home-horse-right"><span class="home-horse-odds">${cote !== null && cote !== "" ? echapper(cote) : "—"}</span><span class="home-horse-odds-label">COTE</span><span class="home-horse-trend">${tendance}</span></div>
        </article>`;
    }).join("");
    document.querySelectorAll(".home-sort-btn").forEach(btn => {
        const active = (btn.id === "home-sort-odds" && window.azHomePartantsSort === "cote") || (btn.id === "home-sort-number" && window.azHomePartantsSort === "numero");
        btn.classList.toggle("is-active", active);
        btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
}
document.addEventListener("DOMContentLoaded", () => {
    const numero = document.getElementById("home-sort-number");
    const cote = document.getElementById("home-sort-odds");
    if(numero) numero.addEventListener("click", () => { window.azHomePartantsSort="numero"; afficherListePartantsAccueil(window.azHomePartantsData || []); });
    if(cote) cote.addEventListener("click", () => { window.azHomePartantsSort="cote"; afficherListePartantsAccueil(window.azHomePartantsData || []); });
});

document.addEventListener("DOMContentLoaded", () => {
    chargerAnalyse();
    setInterval(changerPublicite, 4000);
});
                                                                                                               


async function chargerActualitesHippiques(){
    const zone=document.getElementById('home-news'), status=document.getElementById('news-status'), sources=document.getElementById('news-sources');
    if(!zone) return;
    try{
        const r=await fetch(window.azApiUrl('/api/actualites?limit=10'),{cache:'no-store'}); const d=await r.json();
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
