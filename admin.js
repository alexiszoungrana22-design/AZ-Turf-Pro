/* AZ Turf Pro — Administration v39
 * Clé serveur vérifiée une seule fois puis remplacée par un jeton de session court.
 */
(function(){
  "use strict";
  const SESSION_KEY="AZ_TURF_ADMIN_SESSION";
  const API_BASE="";
  const getSession=()=>sessionStorage.getItem(SESSION_KEY)||"";
  const clearSession=()=>sessionStorage.removeItem(SESSION_KEY);
  const headers=()=>{const t=getSession(); return t?{"X-Admin-Session":t}:{};};

  async function jsonResponse(r){
    let d=null; try{d=await r.json();}catch(_){}
    if(!r.ok) throw new Error(d?.detail||`Erreur serveur (${r.status})`);
    return d||{};
  }

  async function verifyRawKey(key){
    const r=await fetch(API_BASE+"/api/admin/verification",{
      headers:{"X-Admin-Key":key},cache:"no-store"
    });
    return jsonResponse(r);
  }

  window.enregistrerCleAdmin=async function(){
    const input=document.getElementById("admin-api-key");
    const state=document.getElementById("etat-cle-admin");
    const key=(input?.value||"").trim();
    if(!key){if(state)state.textContent="⚠️ Saisissez la clé administrateur.";return false;}
    if(state)state.textContent="⏳ Vérification sécurisée auprès du serveur…";
    try{
      const d=await verifyRawKey(key);
      if(!d.authorized||!d.session_token) throw new Error("Le serveur n'a pas délivré de session administrateur.");
      sessionStorage.setItem(SESSION_KEY,d.session_token);
      if(input) input.value="";
      if(state)state.textContent="✅ Accès administrateur validé (session sécurisée).";
      await Promise.all([window.chargerStatistiquesAdmin(),window.chargerAbonnements()]);
      return true;
    }catch(e){clearSession();if(state)state.textContent=`❌ ${e.message}`;return false;}
  };

  async function check(){
    const token=getSession();
    const state=document.getElementById("etat-cle-admin");
    if(!token){if(state)state.textContent="🔒 Clé administrateur requise.";return false;}
    try{await jsonResponse(await fetch(API_BASE+"/api/admin/verification",{headers:headers(),cache:"no-store"}));return true;}
    catch(e){clearSession();if(state)state.textContent=`❌ ${e.message}`;return false;}
  }

  window.chargerStatistiquesAdmin=async function(){
    const state=document.getElementById("etat-api");
    if(!getSession()){if(state)state.textContent="🔒 Clé administrateur requise";return;}
    try{
      const d=await jsonResponse(await fetch(API_BASE+"/api/admin/statistiques",{headers:headers(),cache:"no-store"}));
      const put=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=String(v??0);};
      put("total-abonnements",d.total??d.total_abonnements??d.abonnements??0);
      put("nombre-premium",d.actifs??d.premium_actifs??d.nombre_premium??0);
      put("paiements-attente",d.attente??d.paiements_attente??d.en_attente??0);
      put("abonnements-expire",d.expires??d.expire??d.abonnements_expires??0);
      if(state)state.textContent="✅ Administrateur authentifié";
    }catch(e){if(state)state.textContent=`❌ ${e.message}`;}
  };

  window.chargerAbonnements=async function(){
    const c=document.getElementById("liste-abonnements");if(!c||!getSession())return;
    try{
      const d=await jsonResponse(await fetch(API_BASE+"/api/admin/abonnements",{headers:headers(),cache:"no-store"}));
      const items=Array.isArray(d)?d:(d.abonnements||[]);
      c.innerHTML=items.length?items.map((a,i)=>`<div style="padding:10px;border-bottom:1px solid #ddd"><b>${i+1}. ${String(a.telephone||a.phone||"—")}</b><br>Statut : ${String(a.statut||a.status||"—")}<br>Référence : ${String(a.reference||a.reference_paiement||"—")}</div>`).join(""):"Aucun abonnement.";
    }catch(e){c.textContent=`❌ ${e.message}`;}
  };

  window.verifierUtilisateurPremium=async function(){
    const out=document.getElementById("resultat-premium"),tel=(document.getElementById("telephone-premium")?.value||"").trim();
    if(!getSession()){if(out)out.textContent="🔒 Clé administrateur requise.";return;}
    if(!tel){if(out)out.textContent="⚠️ Numéro téléphone obligatoire.";return;}
    try{const d=await jsonResponse(await fetch(`/api/premium/${encodeURIComponent(tel)}`,{cache:"no-store"}));if(out)out.textContent=`✅ ${d.statut||d.status||"Abonnement trouvé"}`;}catch(e){if(out)out.textContent=`❌ ${e.message}`;}
  };

  window.activerPremium=async function(){
    const out=document.getElementById("resultat-activation"),telephone=(document.getElementById("activation-telephone")?.value||"").trim(),reference=(document.getElementById("activation-reference")?.value||"").trim();
    if(!getSession()){if(out)out.textContent="🔒 Clé administrateur requise.";return;}
    if(!telephone||!reference){if(out)out.textContent="⚠️ Téléphone et référence obligatoires.";return;}
    try{const d=await jsonResponse(await fetch("/api/activation",{method:"POST",headers:{"Content-Type":"application/json",...headers()},body:JSON.stringify({telephone,reference})}));if(out)out.textContent=`✅ ${d.message||"Premium activé"}`;await Promise.all([window.chargerStatistiquesAdmin(),window.chargerAbonnements()]);}catch(e){if(out)out.textContent=`❌ ${e.message}`;}
  };

  window.actualiserAdmin=async function(){
    const state=document.getElementById("etat-cle-admin");
    if(!(await check()))return;
    if(state)state.textContent="✅ Accès administrateur validé (session sécurisée).";
    await Promise.all([window.chargerStatistiquesAdmin(),window.chargerAbonnements()]);
  };

  window.getAdminSessionToken=()=>getSession();

  document.addEventListener("DOMContentLoaded",()=>{if(getSession())window.actualiserAdmin();});
})();
