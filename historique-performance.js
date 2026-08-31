/* AZ Turf Pro - panneau Performance dans Historique
 * Additif : ne remplace aucune logique historique existante.
 */
(() => {
  'use strict';
  const API_BASE = (window.AZ_API_BASE || '').replace(/\/$/, '');
  const API = `${API_BASE}/api/archive/performance`;

  function esc(v) {
    return String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  }

  function ensurePanel() {
    let panel = document.getElementById('az-archive-performance');
    if (panel) return panel;
    panel = document.createElement('section');
    panel.id = 'az-archive-performance';
    panel.className = 'az-performance-card';
    panel.innerHTML = `
      <div class="az-performance-head">
        <div>
          <h2>📊 Performances AZ</h2>
          <p>Résultats calculés uniquement sur les courses ayant une arrivée officielle.</p>
        </div>
        <button type="button" id="az-performance-refresh">Actualiser</button>
      </div>
      <div id="az-performance-state" class="az-performance-state">Chargement…</div>
      <div id="az-performance-grid" class="az-performance-grid" hidden></div>
    `;
    const host = document.querySelector('main') || document.body;
    host.appendChild(panel);
    panel.querySelector('#az-performance-refresh').addEventListener('click', load);
    return panel;
  }

  function render(data) {
    const panel = ensurePanel();
    const state = panel.querySelector('#az-performance-state');
    const grid = panel.querySelector('#az-performance-grid');
    if (!data || data.status !== 'success') {
      state.textContent = 'Performances indisponibles pour le moment.';
      grid.hidden = true;
      return;
    }
    const courses = Number(data.courses_evaluees ?? data.courses_terminees ?? data.total ?? 0);
    const selection = data.taux_selection_az ?? data.selection_az_taux ?? null;
    const favori = data.taux_favori_gagnant ?? data.favori_gagnant_taux ?? null;
    const touche = data.taux_selection_az_touche ?? data.selection_az_touche_taux ?? null;
    const fmt = v => v == null ? '—' : `${Number(v).toFixed(1)} %`;
    const cards = [
      ['Courses évaluées', courses],
      ['Sélection AZ réussie', fmt(selection)],
      ['Favori AZ gagnant', fmt(favori)],
      ['Sélection AZ dans l’arrivée', fmt(touche)]
    ];
    state.textContent = courses ? `${courses} course(s) évaluée(s)` : 'Aucune course terminée disponible pour le calcul.';
    grid.innerHTML = cards.map(([label, value]) => `<div class="az-performance-metric"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join('');
    grid.hidden = false;
  }

  async function load() {
    ensurePanel();
    const state = document.getElementById('az-performance-state');
    state.textContent = 'Chargement…';
    try {
      const r = await fetch(`${API}?t=${Date.now()}`, { cache: 'no-store', headers: { Accept: 'application/json' } });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      render(await r.json());
    } catch (e) {
      console.error('AZ Performance:', e);
      state.textContent = 'Impossible de charger les performances.';
    }
  }

  window.azArchivePerformanceReload = load;
  document.addEventListener('DOMContentLoaded', load);
})();
