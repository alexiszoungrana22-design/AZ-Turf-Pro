/* AZ Turf Pro — configuration centralisée des appels API
   Le frontend est hébergé sur GitHub Pages ; toutes les API métier vivent sur Render.
   Modifier AZ_API_BASE ici si le backend change de domaine.
*/
(function (global) {
  "use strict";
  const API_BASE = "https://az-turf-pro.onrender.com";
  global.AZ_API_BASE = API_BASE;
  global.azApiUrl = function (path) {
    const value = String(path || "");
    if (/^https?:\/\//i.test(value)) return value;
    return API_BASE + (value.startsWith("/") ? value : "/" + value);
  };
})(window);
