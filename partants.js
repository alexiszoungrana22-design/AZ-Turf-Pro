/* AZ Turf Pro — Partants V17. Présentation uniquement, aucune modification du moteur. */
(() => {
  "use strict";
  const API = window.azApiUrl('/api/partants');
  const $ = (id) => document.getElementById(id);
  const state = { horses: [], sort: "numero", query: "", meta: {} };
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  const val = (...values) => values.find(v => v !== undefined && v !== null && String(v).trim() !== "");
  const display = (v) => v === undefined || v === null || String(v).trim() === "" ? "Non disponible" : String(v);
  const number = (v) => { const n = Number(String(v ?? "").replace(",", ".").replace(/[^0-9.]/g, "")); return Number.isFinite(n) ? n : null; };
  const setStatus = (message, kind="info") => { const el=$("partants-status"); if(el){el.textContent=message;el.dataset.kind=kind;} };
  function getHorses(data) {
    if (Array.isArray(data)) return data;
    return data?.classement || data?.chevaux || data?.partants_liste || data?.resultat?.chevaux || [];
  }
  function renderMeta(data, horses) {
    const course = val(data.nom_course, data.course, data.libelle_course, data.prix, "Course du jour");
    $("course-title").textContent = course;
    const source = String(val(data.source, "PMU") );
    $("course-source").textContent = source === "pmu_live" ? "SOURCE PMU" : source.toUpperCase();
    const facts = [
      `🏟️ Hippodrome : ${display(val(data.hippodrome, data.hippodrome_nom))}`,
      `🕒 Départ : ${display(val(data.heure_depart, data.depart, data.horaires?.depart))}`,
      `🐎 Partants : ${val(data.nombre_partants, data.partants, horses.length) ?? horses.length}`
    ];
    $("course-facts").innerHTML = facts.map(x=>`<span>${esc(x)}</span>`).join("");
    document.title = `Partants – ${course} | AZ Turf Pro`;
  }
  function normalizedHorse(h) {
    const numero = val(h.numero, h.numPmu, h.numéro, "—");
    const statusRaw = String(val(h.statut, h.etat, "Partant")).toLowerCase();
    const np = h.est_non_partant === true || h.non_partant === true || /non.?partant|^np$/.test(statusRaw);
    return {
      raw:h, numero, nom:val(h.nom, h.nom_cheval, h.cheval, "Cheval sans nom"),
      jockey:val(h.jockey, h.driver, h.driver_nom, ""), entraineur:val(h.entraineur, h.éntraineur, ""),
      cote:val(h.cote, h.cote_brute, h.cote_direct, h.rapport, ""),
      indice:val(h.indice_az, h.score_az, h.indice, ""),
      musique:val(h.musique_brute, h.musique, h.forme, ""),
      distance:val(h.distance, h.distance_course, ""), age:val(h.age, ""), gains:val(h.gains_carriere_brute, h.gains, ""),
      silk:val(h.casaque_url, h.url_casaque, h.casaque, ""), np
    };
  }
  function silkMarkup(h) {
    if (typeof h.silk === "string" && /^(https?:|data:image\/)/i.test(h.silk)) return `<img class="partant-silk" src="${esc(h.silk)}" alt="Casaque de ${esc(h.nom)}" loading="lazy">`;
    return `<span class="partant-silk" aria-label="Casaque non fournie">🏇</span>`;
  }
  function render() {
    const list=$("partants-list"); if(!list) return;
    let horses=state.horses.filter(h => {
      const q=state.query.toLocaleLowerCase("fr");
      return !q || [h.nom,h.numero,h.jockey,h.entraineur].some(v=>String(v??"").toLocaleLowerCase("fr").includes(q));
    });
    horses.sort((a,b)=>{
      if(state.sort==="cote"){const x=number(a.cote),y=number(b.cote);return (x??Infinity)-(y??Infinity);}
      if(state.sort==="indice"){const x=number(a.indice),y=number(b.indice);return (y??-Infinity)-(x??-Infinity);}
      return (number(a.numero)??9999)-(number(b.numero)??9999);
    });
    $("partants-count").textContent=`${state.horses.length} cheval${state.horses.length>1?"ux":""}`;
    if(!horses.length){list.innerHTML=`<div class="partants-empty">${state.horses.length?"Aucun cheval ne correspond à cette recherche.":"Aucun partant disponible pour le moment."}</div>`;return;}
    list.innerHTML=horses.map(h=>{
      const meta=[];
      if(h.jockey) meta.push(`Jockey : <strong>${esc(h.jockey)}</strong>`);
      if(h.entraineur) meta.push(`Entraîneur : <strong>${esc(h.entraineur)}</strong>`);
      const chips=[];
      if(h.distance) chips.push(`<span class="partant-chip">${esc(h.distance)} m</span>`);
      if(h.age) chips.push(`<span class="partant-chip">${esc(h.age)} ans</span>`);
      if(h.musique) chips.push(`<span class="partant-chip musique">Musique : ${esc(h.musique)}</span>`);
      if(h.indice!=="") chips.push(`<span class="partant-chip indice">Indice AZ : ${esc(h.indice)}</span>`);
      if(h.gains) chips.push(`<span class="partant-chip">Gains : ${esc(h.gains)}</span>`);
      return `<article class="partant-row${h.np?" is-non-runner":""}"><span class="partant-number">${esc(h.numero)}</span><div class="partant-identity"><div class="partant-name-line">${silkMarkup(h)}<span class="partant-name">${esc(h.nom)}</span></div><div class="partant-meta">${meta.join(" · ")||"Informations jockey et entraîneur non disponibles"}</div>${chips.length?`<div class="partant-extra">${chips.join("")}</div>`:""}</div><div class="partant-right"><span class="partant-odds">${h.cote!==""?esc(h.cote):"—"}</span><span class="partant-status${h.np?" np":""}">${h.np?"NON PARTANT":"PARTANT"}</span></div></article>`;
    }).join("");
  }
  async function load() {
    setStatus("Récupération des données de la course…");
    try {
      const response=await fetch(API,{cache:"no-store",headers:{"Accept":"application/json"}});
      if(!response.ok) throw new Error(`Service indisponible (${response.status})`);
      const data=await response.json();
      // /api/partants fournit la liste compacte ; /api/analyse apporte les métadonnées
      // de course déjà calculées par le backend. Si ce second appel échoue, la liste reste visible.
      let courseMeta = {};
      try {
        const metaResponse = await fetch(window.azApiUrl('/api/analyse'), {cache:"no-store",headers:{"Accept":"application/json"}});
        if (metaResponse.ok) courseMeta = await metaResponse.json();
      } catch (metaError) { console.warn("Métadonnées de course non disponibles :", metaError); }
      const raw=getHorses(data);
      state.horses=raw.filter(x=>x&&typeof x==="object").map(normalizedHorse);
      const mergedMeta = Array.isArray(data) ? {...courseMeta, source: val(data[0]?.source, courseMeta.source), donnees_demo: data[0]?.donnees_demo ?? courseMeta.donnees_demo} : {...courseMeta, ...data};
      renderMeta(mergedMeta,state.horses);
      if(!state.horses.length){setStatus("La source a répondu, mais aucun cheval n'est disponible pour cette course.","error");render();return;}
      setStatus(`${state.horses.length} chevaux chargés. Les champs absents ne sont pas inventés.`,"success");
      render();
    } catch(error) {
      console.error("Chargement des partants :",error);
      setStatus(`${error.message||"Impossible de charger les partants."} Réessayez dans quelques instants.`,"error");
      $("partants-list").innerHTML='<div class="partants-empty">Les partants ne sont pas accessibles pour le moment. Vérifiez votre connexion puis actualisez la page.</div>';
      $("course-title").textContent="Course momentanément indisponible";
    }
  }
  document.addEventListener("DOMContentLoaded",()=>{
    $("partants-search")?.addEventListener("input",e=>{state.query=e.target.value;render();});
    document.querySelectorAll(".sort-button").forEach(btn=>btn.addEventListener("click",()=>{
      state.sort=btn.dataset.sort;
      document.querySelectorAll(".sort-button").forEach(b=>b.classList.toggle("active",b===btn));
      render();
    }));
    load();
  });
})();
