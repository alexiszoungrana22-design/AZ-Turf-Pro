/** AZ Turf Pro - Historique v8
 * L'archive PostgreSQL est prioritaire pour les courses passées.
 * L'ancien /api/historique reste un fallback : aucune route existante n'est supprimée.
 */
(() => {
  'use strict';
  const API_HISTORIQUE = '/api/historique';
  const API_ARCHIVE = '/api/archive/courses?limit=100';
  const API_PERFORMANCE = '/api/archive/performance';
  const STORAGE = 'AZ_TURF_HISTORIQUE_COURSES_V1';

  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const text = (v, fallback='-') => (v === null || v === undefined || v === '') ? fallback : String(v);
  const nums = v => Array.isArray(v) ? v.map(x => typeof x === 'object' ? x?.numero : x).filter(x => x !== null && x !== undefined && String(x).trim() !== '').map(String) : [];

  function dateFr(v) {
    if (!v) return '-';
    const s = String(v).trim();
    if (/^\d{8}$/.test(s)) return `${s.slice(0,2)}/${s.slice(2,4)}/${s.slice(4)}`;
    const d = new Date(s.replace(' ','T'));
    return Number.isNaN(d.getTime()) ? s : d.toLocaleDateString('fr-FR');
  }

  function nomFavori(v) {
    if (!v) return '-';
    if (typeof v === 'object') {
      const n = v.numero ?? '';
      const nom = v.nom ?? v.name ?? '';
      if (n && nom) return `N°${n} ${nom}`;
      if (n) return `N°${n}`;
      return nom || '-';
    }
    return String(v);
  }

  function liste(v) { return nums(v).join(' - ') || '-'; }

  function normaliserArchive(c) {
    const course = c.course_json && typeof c.course_json === 'object' ? c.course_json : {};
    const selection = c.selection_az_json ?? course.selection_az ?? [];
    const selectionPremium = c.selection_premium_json ?? course.selection_premium ?? [];
    const favori = c.favori_json ?? course.favori ?? {};
    const arrivee = c.arrivee_json ?? course.arrivee ?? [];
    return {
      date: c.date_course ?? course.date ?? '',
      reunion: c.reunion ?? course.reunion ?? '',
      numero: c.course_numero ?? course.course_numero ?? course.numero_course ?? '',
      nom: course.course ?? course.nom ?? course.libelle ?? 'Course',
      hippodrome: c.hippodrome ?? course.hippodrome ?? '',
      favori: nomFavori(favori),
      selectionPremium: nums(selectionPremium),
      arrivee: nums(arrivee)
    };
  }

  function normaliserAncienne(c) {
    const course = c?.course && typeof c.course === 'object' ? c.course : {};
    return {
      date: c?.date ?? course.date ?? c?.date_analyse ?? '',
      reunion: c?.reunion ?? course.reunion ?? '',
      numero: c?.course_numero ?? course.course_numero ?? c?.numero_course ?? '',
      nom: course.course ?? course.nom ?? c?.nom_course ?? 'Course',
      hippodrome: c?.hippodrome ?? course.hippodrome ?? '',
      favori: nomFavori(c?.favori ?? {}),
      selectionPremium: nums(c?.selection_premium ?? []),
      arrivee: nums(c?.arrivee ?? c?.arrivee_quinte ?? [])
    };
  }

  async function getJson(url) {
    const r = await fetch(`${url}${url.includes('?') ? '&' : '?'}t=${Date.now()}`, {cache:'no-store', headers:{Accept:'application/json'}});
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }

  async function chargerCourses() {
    try {
      const data = await getJson(API_ARCHIVE);
      if (data?.status === 'success' && Array.isArray(data.courses)) {
        return data.courses.map(normaliserArchive);
      }
    } catch (e) { console.warn('Archive PostgreSQL indisponible:', e); }

    try {
      const data = await getJson(API_HISTORIQUE);
      const arr = Array.isArray(data?.historique) ? data.historique : [];
      return arr.map(normaliserAncienne);
    } catch (e) { console.warn('Historique API indisponible:', e); }

    try {
      const arr = JSON.parse(localStorage.getItem(STORAGE) || '[]');
      return Array.isArray(arr) ? arr.map(normaliserAncienne) : [];
    } catch (_) { return []; }
  }

  function renderCourses(courses) {
    const body = document.getElementById('historique-body');
    if (!body) return;
    body.innerHTML = '';
    if (!courses.length) {
      body.innerHTML = '<tr><td colspan="5" class="az-empty">Aucune course archivée pour le moment.</td></tr>';
      return;
    }
    courses.forEach(c => {
      const identite = `${c.reunion ? esc(c.reunion) + ' ' : ''}${c.numero ? 'N°' + esc(c.numero) : ''}`.trim() || 'Course';
      const nom = esc(c.nom);
      const hippo = c.hippodrome ? `<br><small>${esc(c.hippodrome)}</small>` : '';
      const arrivee = c.arrivee.length ? esc(c.arrivee.join(' - ')) : '<span class="az-status pending">⏳ En attente</span>';
      body.insertAdjacentHTML('beforeend', `<tr>
        <td>${esc(dateFr(c.date))}</td>
        <td><strong>${identite}</strong><br>${nom}${hippo}</td>
        <td><strong style="color:#08783f">${esc(c.favori)}</strong></td>
        <td><strong style="color:#b8860b;letter-spacing:1px">${esc(c.selectionPremium.length ? c.selectionPremium.join(' - ') : '-')}</strong></td>
        <td>${arrivee}</td>
      </tr>`);
    });
  }

  function pct(v) {
    if (v === null || v === undefined || Number.isNaN(Number(v))) return '0 %';
    return `${Number(v).toFixed(1)} %`;
  }

  async function chargerPerformance() {
    const state = document.getElementById('az-performance-state');
    try {
      const data = await getJson(API_PERFORMANCE);
      if (data?.status !== 'success') throw new Error('Réponse invalide');
      const total = Number(data.courses_analysees ?? data.courses_terminees ?? 0);
      document.getElementById('perf-courses').textContent = total;
      document.getElementById('perf-selection').textContent = pct(data.selection_taux_gagnant);
      document.getElementById('perf-favori').textContent = pct(data.favori_taux);
      document.getElementById('perf-touche').textContent = pct(data.selection_taux_touchee);
      state.textContent = total ? `${total} course(s) terminée(s) évaluée(s).` : 'Aucune course terminée disponible pour le calcul.';
    } catch (e) {
      console.warn('Performances indisponibles:', e);
      state.textContent = 'Les performances seront calculées dès qu’une arrivée officielle sera disponible.';
    }
  }

  async function charger() {
    const courses = await chargerCourses();
    renderCourses(courses);
    await chargerPerformance();
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('az-performance-refresh')?.addEventListener('click', charger);
    charger();
  });
})();
