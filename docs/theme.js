// Light or dark: follows the system unless the reader picks one with the switch in the header (kept in this
// browser, or ?theme=dark in a link). Loaded in the page's head, so the page is drawn in the right colours from
// the start; the stylesheet's dark colours apply under @media (prefers-color-scheme: dark) unless
// <html data-theme="light">, and under data-theme="dark" always. Scripts that draw their own colours (the map,
// the charts) ask SiteTheme.dark() and redraw on SiteTheme.onChange.
(function () {
  const mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : { matches: false, addEventListener() {} };
  let pref = null;
  try { pref = localStorage.getItem("theme"); } catch (e) { /* storage blocked */ }
  const q = new URLSearchParams(location.search).get("theme");
  if (q === "dark" || q === "light") pref = q;
  if (pref !== "dark" && pref !== "light") pref = null;
  const subs = [];
  const dark = () => (pref ? pref === "dark" : mq.matches);
  const apply = () => { if (pref) document.documentElement.dataset.theme = pref; else delete document.documentElement.dataset.theme; };
  const fire = () => {
    const box = document.getElementById("theme-switch");
    if (box) box.checked = dark();
    subs.forEach((f) => { try { f(dark()); } catch (e) { console.error(e); } });
  };
  apply();
  mq.addEventListener("change", () => { if (!pref) fire(); });
  function set(isDark) {
    pref = isDark ? "dark" : "light";
    try { localStorage.setItem("theme", pref); } catch (e) { /* storage blocked */ }
    apply(); fire();
  }
  window.SiteTheme = { dark, set, onChange: (f) => subs.push(f) };

  function init() {
    const head = document.querySelector(".hero .wrap");
    if (!head) return;
    const box = document.createElement("label");
    box.className = "theme-toggle";
    const input = document.createElement("input");
    input.type = "checkbox"; input.id = "theme-switch"; input.setAttribute("role", "switch");
    input.checked = dark();
    input.addEventListener("change", () => set(input.checked));
    const track = document.createElement("span");
    track.className = "switch-track"; track.setAttribute("aria-hidden", "true");
    const text = document.createElement("span");
    text.textContent = "Dark mode";
    box.append(input, track, text);
    head.insertBefore(box, head.firstChild);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
