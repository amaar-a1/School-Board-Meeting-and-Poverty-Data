// Terms of use on a first visit: the footer's terms in a dialog that has to be agreed to before the site can be used,
// with the site's languages (English, French, Spanish) to read them in. The agreement is remembered in this browser
// (if it allows storage; otherwise the dialog comes back on the next visit), for this wording of the terms: when the
// terms change it shows again to everyone.
(function () {
  "use strict";
  // The version is a fingerprint of the terms' own (English) wording in index.html, so editing any word of the terms
  // shows the dialog again to everyone, with nothing else to update. It is read as this script runs, before the
  // page is translated (i18n.js translates on DOMContentLoaded, after the page has been read).
  const termsText = [...document.querySelectorAll("#terms > p")].map((p) => p.textContent.replace(/\s+/g, " ").trim()).join("\n");
  let h = 5381;
  for (let i = 0; i < termsText.length; i++) h = ((h * 33) ^ termsText.charCodeAt(i)) >>> 0;
  const TERMS_VERSION = "t" + h.toString(36) + "-" + termsText.length;
  const KEY = "terms-agreed";
  const read = () => { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
  const save = () => { try { localStorage.setItem(KEY, TERMS_VERSION); } catch (e) { /* private window: ask again next time */ } };

  function init() {
    const dlg = document.getElementById("terms-gate");
    if (!dlg || read() === TERMS_VERSION || typeof dlg.showModal !== "function") return;
    // The same paragraphs as the footer's terms (so the two never differ), translated like the rest of the page.
    const body = dlg.querySelector(".terms-gate-body");
    document.querySelectorAll("#terms > p").forEach((p) => body.appendChild(p.cloneNode(true)));
    const langs = dlg.querySelectorAll("[data-lang]");
    const mark = () => langs.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === (window.SiteLang ? window.SiteLang.get() : "en"))));
    langs.forEach((b) => b.addEventListener("click", () => { if (window.SiteLang) window.SiteLang.set(b.dataset.lang); mark(); }));
    document.getElementById("lang-select")?.addEventListener("change", mark);
    mark();
    dlg.addEventListener("cancel", (e) => e.preventDefault());   // Escape doesn't skip it
    document.getElementById("terms-gate-agree").addEventListener("click", () => { save(); dlg.close(); });
    dlg.showModal();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
