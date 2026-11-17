(() => {
  "use strict";
  const API_PROGRAMME = "https://az-turf-pro.onrender.com/api/programme";
  const dateInput = document.getElementById("programme-date");
  const status = document.getElementById("programme-status");
  const summary = document.getElementById("programme-summary");
  const meetings = document.getElementById("programme-meetings");
  const results = document.getElementById("programme-results");
  let programme = null;
  let selectedMeeting = null;

  const pad = n => String(n).padStart(2, "0");
  const dateLocal = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const today = () => dateLocal(new Date());

  function addDays(dateText, amount) {
    const [y,m,d] = dateText.split("-").map(Number);
    const date = new Date(y, m-1, d);
    date.setDate(date.getDate()+amount);
    return dateLocal(date);
  }

  function setStatus(message, kind="info") {
    status.textContent = message;
    status.dataset.kind = kind;
    status.hidden = !message;
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function formatDate(value) {
    const [y,m,d] = value.split("-").map(Number);
    return new Intl.DateTimeFormat("fr-FR", {weekday:"long", day:"numeric", month:"long", year:"numeric"})
      .format(new Date(y,m-1,d));
  }

  async function loadProgramme() {
    const date = dateInput.value || today();
    dateInput.value = date;
    setStatus("Récupération du programme officiel PMU…");
    summary.hidden = true;
    meetings.replaceChildren();
    results.replaceChildren();
    try {
      const response = await fetch(`${API_PROGRAMME}?date=${encodeURIComponent(date)}`, {cache:"no-store"});
      let data = {};
      try { data = await response.json(); } catch (_) {}
      if (!response.ok) {
        const detail = data.detail || `Erreur du serveur (${response.status})`;
        throw new Error(detail);
      }
      if (!data || !Array.isArray(data.reunions)) throw new Error("Format de programme non reconnu.");
      programme = data;
      selectedMeeting = data.reunions.length ? 0 : null;
      renderProgramme(date);
      if (!data.reunions.length) setStatus("Aucune réunion PMU n’est publiée pour cette date.", "empty");
      else setStatus(`Programme officiel chargé pour le ${formatDate(date)}.`, "success");
    } catch (error) {
      programme = null;
      setStatus(`${error.message} Les données de démonstration ne sont pas utilisées ici.`, "error");
    }
  }

  function renderProgramme(date) {
    const reunions = programme.reunions;
    summary.replaceChildren(
      element("strong", "", `${programme.nombre_reunions ?? reunions.length} réunion(s)`),
      element("span", "", `${programme.nombre_courses ?? reunions.reduce((n,r)=>n+(r.courses||[]).length,0)} course(s)`),
      element("span", "", formatDate(date))
    );
    summary.hidden = false;

    meetings.replaceChildren();
    reunions.forEach((meeting, index) => {
      const button = element("button", `meeting-tab${index===selectedMeeting?" active":""}`,
        `${meeting.code || `R${meeting.numero ?? index+1}`} · ${meeting.hippodrome || "Hippodrome non renseigné"}`);
      button.type = "button";
      button.setAttribute("aria-pressed", String(index===selectedMeeting));
      button.addEventListener("click", () => {
        selectedMeeting = index;
        renderProgramme(date);
      });
      meetings.appendChild(button);
    });

    results.replaceChildren();
    if (selectedMeeting === null || !reunions[selectedMeeting]) return;
    const meeting = reunions[selectedMeeting];
    const heading = element("h2", "meeting-heading",
      `${meeting.code || `Réunion ${meeting.numero ?? ""}`} — ${meeting.hippodrome || "Hippodrome non renseigné"}`);
    results.appendChild(heading);
    const courseList = element("div", "course-list");
    (meeting.courses || []).forEach(course => {
      const card = element("article", "programme-course");
      const top = element("div", "course-top");
      top.appendChild(element("span", "course-number",
        course.code || `Course ${course.numero ?? "?"}`));
      if (course.quinte) top.appendChild(element("span", "quinte-tag", "QUINTÉ+"));
      card.appendChild(top);
      card.appendChild(element("h3", "course-name", course.nom || "Nom de course non renseigné"));
      const details = element("div", "course-details");
      const facts = [
        ["Départ", course.heure_depart || "Horaire non publié"],
        ["Distance", course.distance ? `${course.distance} m` : "Non renseignée"],
        ["Partants", course.nombre_partants ?? "Non renseigné"],
        ["Discipline", course.discipline || "Non renseignée"],
        ["Allocation", course.allocation || "Non renseignée"],
        ["Statut", course.statut || "Non renseigné"]
      ];
      facts.forEach(([label,value]) => {
        const item = element("div", "course-fact");
        item.appendChild(element("span", "fact-label", label));
        item.appendChild(element("strong", "fact-value", value));
        details.appendChild(item);
      });
      card.appendChild(details);

      const horseButton = element("button", "course-horses-button", "Voir les partants");
      horseButton.type = "button";
      horseButton.addEventListener("click", () => loadCourseHorses(date, meeting.numero, course.numero, card, horseButton));
      card.appendChild(horseButton);
      courseList.appendChild(card);
    });
    if (!(meeting.courses || []).length) courseList.appendChild(element("p","empty-courses","Aucune course publiée pour cette réunion."));
    results.appendChild(courseList);
  }

  async function loadCourseHorses(date, reunion, course, card, button) {
    let panel = card.querySelector(".course-horses-panel");
    if (panel) {
      panel.remove();
      button.textContent = "Voir les partants";
      return;
    }
    if (reunion == null || course == null) {
      setStatus("Les identifiants de cette course ne sont pas fournis par le programme PMU.", "error");
      return;
    }

    button.disabled = true;
    button.textContent = "Chargement des partants…";
    panel = element("section", "course-horses-panel");
    panel.setAttribute("aria-live", "polite");
    panel.appendChild(element("p", "horses-loading", "Récupération des partants officiels PMU…"));
    card.appendChild(panel);

    try {
      const query = new URLSearchParams({date, reunion: String(reunion), course: String(course)});
      const response = await fetch(`${API_PROGRAMME}/partants?${query.toString()}`, {cache:"no-store"});
      let data = {};
      try { data = await response.json(); } catch (_) {}
      if (!response.ok) throw new Error(data.detail || `Erreur du serveur (${response.status})`);
      if (data.source !== "pmu_live" || !Array.isArray(data.chevaux)) throw new Error("Les données reçues ne sont pas des partants PMU confirmés.");

      panel.replaceChildren();
      const header = element("div", "horses-header");
      header.appendChild(element("strong", "", `${data.chevaux.length} cheval(aux)`));
      if (data.non_partants && data.non_partants.length) {
        header.appendChild(element("span", "horses-non-runners", `Non-partants : ${data.non_partants.join(", ")}`));
      }
      panel.appendChild(header);

      const list = element("div", "horses-list");
      data.chevaux.forEach(horse => {
        const row = element("article", `horse-row${horse.statut === "Non-partant" ? " is-non-runner" : ""}`);
        row.appendChild(element("span", "horse-number", horse.numero ?? "–"));
        const identity = element("div", "horse-identity");
        identity.appendChild(element("strong", "horse-name", horse.nom || "Nom non renseigné"));
        const details = [horse.age ? `${horse.age} ans` : "", horse.sexe, horse.jockey ? `Jockey : ${horse.jockey}` : "", horse.entraineur ? `Entraîneur : ${horse.entraineur}` : "", horse.musique ? `Musique : ${horse.musique}` : ""]
          .filter(Boolean).join(" · ");
        if (details) identity.appendChild(element("span", "horse-meta", details));
        row.appendChild(identity);
        const odds = horse.cote !== null && horse.cote !== undefined && horse.cote !== "" ? horse.cote : "—";
        row.appendChild(element("strong", "horse-odds", `Cote ${odds}`));
        if (horse.statut === "Non-partant") row.appendChild(element("span", "horse-status", "NP"));
        list.appendChild(row);
      });
      panel.appendChild(list);
      panel.appendChild(element("p", "horses-source", "Source : programme officiel PMU. Les cotes peuvent ne pas être publiées."));
      button.textContent = "Masquer les partants";
    } catch (error) {
      panel.replaceChildren(element("p", "horses-error", `${error.message} Aucun partant de démonstration n’est affiché.`));
      button.textContent = "Réessayer";
    } finally {
      button.disabled = false;
    }
  }

  document.getElementById("date-previous").addEventListener("click", () => {
    dateInput.value = addDays(dateInput.value || today(), -1); loadProgramme();
  });
  document.getElementById("date-next").addEventListener("click", () => {
    dateInput.value = addDays(dateInput.value || today(), 1); loadProgramme();
  });
  document.getElementById("date-today").addEventListener("click", () => {
    dateInput.value = today(); loadProgramme();
  });
  dateInput.addEventListener("change", loadProgramme);
  dateInput.value = today();
  loadProgramme();
})();