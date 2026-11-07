// Interface language: English, French or Spanish. Translates the site's labels, tabs, buttons and
// headings (any text node or placeholder that matches an entry below, including ones app.js adds
// later); the longer notes and the data itself stay in English. The choice is kept in the link
// (?lang=fr) and in this browser.
(function () {
  const T = {
    fr: {
      "School Board Meetings & Poverty Data": "Réunions des conseils scolaires et pauvreté",
      "Overview": "Vue d'ensemble", "By district size": "Par taille de district", "By locale": "Par milieu", "State rules": "Règles des États",
      "Province rules": "Règles des provinces", "Rules": "Règles", "State & province rules": "Règles des États et provinces",
      "Map": "Carte", "Trends": "Tendances", "Sources": "Sources", "Chart": "Graphique", "Data table": "Tableau de données",
      "Urban & suburban": "Urbain et périurbain", "Urban only": "Urbain seulement", "Data:": "Données :", "All": "Tout",
      "Islands & microstates": "Îles et micro-États", "Copy link": "Copier le lien", "Link copied": "Lien copié",
      "Choose a state or province…": "Choisir un État ou une province…", "Choose a state…": "Choisir un État…", "All states…": "Tous les États…", "Choose a state, province or region…": "Choisir un État, une province ou une région…", "Choose a province or territory…": "Choisir une province ou un territoire…", "Choose a nation…": "Choisir une nation…", "Choose a region…": "Choisir une région…", "Choose a department…": "Choisir un département…", "Choose a province…": "Choisir une province…", "Choose a county…": "Choisir un comté…", "Choose an island…": "Choisir une île…", "Choose a region or island…": "Choisir une région ou une île…", "Whole region": "Toute la région",
      "Find a district": "Trouver un district", "Type a district, board, county, state or province…": "Tapez un district, un conseil, un comté, un État ou une province…",
      "Search rows…": "Rechercher…", "Download CSV": "Télécharger le CSV", "Filters": "Filtres", "Clear filters": "Effacer les filtres",
      "Locale": "Milieu", "Meetings": "Réunions", "Child poverty": "Pauvreté des enfants", "District size": "Taille du district", "Any": "Tous",
      "min": "min", "max": "max", "to": "à", "Urban": "Urbain", "Suburban": "Périurbain", "Town": "Petite ville", "Rural": "Rural", "Mixed": "Mixte",
      "X axis": "Axe X", "Y axis": "Axe Y", "Type": "Type", "Show": "Afficher", "Bar": "Barres", "Line": "Courbe", "Scatter": "Nuage de points",
      "Top 25": "25 premiers", "Top 50": "50 premiers", "Top 100": "100 premiers",
      "Map of school districts": "Carte des districts scolaires", "Color by": "Colorer selon", "Go to": "Aller à",
      "Child poverty rate": "Taux de pauvreté des enfants", "Available board meetings": "Réunions disponibles",
      "Poverty rank within its country": "Rang de pauvreté dans son pays", "Secondary districts": "Districts secondaires",
      "Overlapping Canadian boards": "Conseils canadiens qui se chevauchent", "Loading data…": "Chargement des données…",
      "Loading district borders…": "Chargement des limites…", "Poverty and meetings, country by country": "Pauvreté et réunions, pays par pays",
      "Recorded meetings by year": "Réunions enregistrées par année", "Child poverty over time": "Pauvreté des enfants dans le temps",
      "Overall": "Ensemble", "With available meetings": "Avec réunions disponibles", "Without available meetings": "Sans réunions disponibles",
      "Share of districts with available meetings": "Part des districts avec réunions", "Average number of available meetings": "Nombre moyen de réunions",
      "Child poverty: with vs. without available meetings": "Pauvreté des enfants : avec ou sans réunions", "US and Canada together": "États-Unis et Canada ensemble",
      "Who's covered": "Qui est concerné", "Size threshold": "Seuil de taille", "What's required": "Ce qui est exigé", "State": "État",
      "Proposed, but not law (US)": "Proposé, mais pas encore loi (É.-U.)", "Country": "Pays", "Places": "Lieux", "With meetings": "Avec réunions",
      "Avg meetings": "Réunions (moy.)", "Correlation (r)": "Corrélation (r)", "Relationship": "Relation",
      "Ask about the data": "Poser une question", "Language": "Langue", "Show on map": "Voir sur la carte", "Show in data table": "Voir dans le tableau",
      "United States": "États-Unis", "United Kingdom": "Royaume-Uni", "Germany": "Allemagne", "Denmark": "Danemark", "Finland": "Finlande",
      "Iceland": "Islande", "Ireland": "Irlande", "Netherlands": "Pays-Bas", "New Zealand": "Nouvelle-Zélande", "Norway": "Norvège",
      "Sweden": "Suède", "Switzerland": "Suisse", "Canada": "Canada", "Saint-Pierre-et-Miquelon": "Saint-Pierre-et-Miquelon", "Chile": "Chili", "Colombia": "Colombie", "Mexico": "Mexique", "Brazil": "Brésil", "Peru": "Pérou", "Spain": "Espagne", "France": "France", "Ecuador": "Équateur",
      "Notes and sources are in English.": "Les notes et les sources sont en anglais."
    },
    es: {
      "School Board Meetings & Poverty Data": "Reuniones de consejos escolares y pobreza",
      "Overview": "Resumen", "By district size": "Por tamaño de distrito", "By locale": "Por entorno", "State rules": "Normas estatales",
      "Province rules": "Normas provinciales", "Rules": "Normas", "State & province rules": "Normas estatales y provinciales",
      "Map": "Mapa", "Trends": "Tendencias", "Sources": "Fuentes", "Chart": "Gráfico", "Data table": "Tabla de datos",
      "Urban & suburban": "Urbano y suburbano", "Urban only": "Solo urbano", "Data:": "Datos:", "All": "Todo",
      "Islands & microstates": "Islas y microestados", "Copy link": "Copiar enlace", "Link copied": "Enlace copiado",
      "Choose a state or province…": "Elija un estado o provincia…", "Choose a state…": "Elija un estado…", "All states…": "Todos los estados…", "Choose a state, province or region…": "Elija un estado, provincia o región…", "Choose a province or territory…": "Elija una provincia o territorio…", "Choose a nation…": "Elija una nación…", "Choose a region…": "Elija una región…", "Choose a department…": "Elija un departamento…", "Choose a province…": "Elija una provincia…", "Choose a county…": "Elija un condado…", "Choose an island…": "Elija una isla…", "Choose a region or island…": "Elija una región o isla…", "Whole region": "Toda la región",
      "Find a district": "Buscar un distrito", "Type a district, board, county, state or province…": "Escriba un distrito, consejo, condado, estado o provincia…",
      "Search rows…": "Buscar…", "Download CSV": "Descargar CSV", "Filters": "Filtros", "Clear filters": "Borrar filtros",
      "Locale": "Entorno", "Meetings": "Reuniones", "Child poverty": "Pobreza infantil", "District size": "Tamaño del distrito", "Any": "Todos",
      "min": "mín", "max": "máx", "to": "a", "Urban": "Urbano", "Suburban": "Suburbano", "Town": "Pueblo", "Rural": "Rural", "Mixed": "Mixto",
      "X axis": "Eje X", "Y axis": "Eje Y", "Type": "Tipo", "Show": "Mostrar", "Bar": "Barras", "Line": "Líneas", "Scatter": "Dispersión",
      "Top 25": "Primeros 25", "Top 50": "Primeros 50", "Top 100": "Primeros 100",
      "Map of school districts": "Mapa de distritos escolares", "Color by": "Colorear por", "Go to": "Ir a",
      "Child poverty rate": "Tasa de pobreza infantil", "Available board meetings": "Reuniones disponibles",
      "Poverty rank within its country": "Rango de pobreza dentro de su país", "Secondary districts": "Distritos secundarios",
      "Overlapping Canadian boards": "Consejos canadienses superpuestos", "Loading data…": "Cargando datos…",
      "Loading district borders…": "Cargando límites…", "Poverty and meetings, country by country": "Pobreza y reuniones, país por país",
      "Recorded meetings by year": "Reuniones grabadas por año", "Child poverty over time": "Pobreza infantil a lo largo del tiempo",
      "Overall": "En total", "With available meetings": "Con reuniones disponibles", "Without available meetings": "Sin reuniones disponibles",
      "Share of districts with available meetings": "Proporción de distritos con reuniones", "Average number of available meetings": "Número medio de reuniones",
      "Child poverty: with vs. without available meetings": "Pobreza infantil: con o sin reuniones", "US and Canada together": "EE. UU. y Canadá juntos",
      "Who's covered": "A quién se aplica", "Size threshold": "Umbral de tamaño", "What's required": "Qué se exige", "State": "Estado",
      "Proposed, but not law (US)": "Propuesto, pero no es ley (EE. UU.)", "Country": "País", "Places": "Lugares", "With meetings": "Con reuniones",
      "Avg meetings": "Reuniones (media)", "Correlation (r)": "Correlación (r)", "Relationship": "Relación",
      "Ask about the data": "Preguntar sobre los datos", "Language": "Idioma", "Show on map": "Ver en el mapa", "Show in data table": "Ver en la tabla",
      "United States": "Estados Unidos", "United Kingdom": "Reino Unido", "Germany": "Alemania", "Denmark": "Dinamarca", "Finland": "Finlandia",
      "Iceland": "Islandia", "Ireland": "Irlanda", "Netherlands": "Países Bajos", "New Zealand": "Nueva Zelanda", "Norway": "Noruega",
      "Sweden": "Suecia", "Switzerland": "Suiza", "Canada": "Canadá", "Saint-Pierre-et-Miquelon": "San Pedro y Miquelón", "Chile": "Chile", "Colombia": "Colombia", "Mexico": "México", "Brazil": "Brasil", "Peru": "Perú", "Spain": "España", "France": "Francia", "Ecuador": "Ecuador",
      "Notes and sources are in English.": "Las notas y las fuentes están en inglés."
    }
  };
  const params = new URLSearchParams(location.search);
  let lang = params.get("lang");
  try { lang = lang || localStorage.getItem("sbmpd-lang"); } catch (e) { /* private mode */ }
  if (!T[lang]) lang = "en";
  const orig = new WeakMap();   // node -> its English text, so switching back works

  function translateNode(n) {
    if (n.nodeType === 3) {
      const en = orig.has(n) ? orig.get(n) : n.nodeValue;
      const key = en.trim();
      const want = lang === "en" ? key : (T[lang][key] || null);
      if (want === null) return;
      if (!orig.has(n)) orig.set(n, en);
      const out = en.replace(key, want);
      if (n.nodeValue !== out) n.nodeValue = out;
    } else if (n.nodeType === 1 && n.placeholder) {
      const en = n.dataset.enPlaceholder || n.placeholder;
      n.dataset.enPlaceholder = en;
      n.placeholder = lang === "en" ? en : (T[lang][en] || en);
    }
  }
  function walk(root) {
    if (root.nodeType === 3) return translateNode(root);
    if (root.closest && root.closest("script, style, #lang-note-skip")) return;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    for (let n = root; n; n = w.nextNode()) {
      if (n.nodeType === 1 && /^(SCRIPT|STYLE|CANVAS)$/.test(n.tagName)) continue;
      translateNode(n);
    }
  }
  let busy = false;
  const obs = new MutationObserver((muts) => {
    if (busy || lang === "en") return;
    busy = true;
    muts.forEach((m) => { if (m.type === "characterData") translateNode(m.target); else m.addedNodes.forEach(walk); });
    if (muts.some((m) => m.target.id === "tabs" || m.target.id === "country-select")) resort();
    busy = false;
  });

  // Keep the country menu in alphabetical order in the chosen language ("All" stays last).
  function resort() {
    const sel = document.getElementById("country-select");
    if (!sel) return;
    const os = [...sel.options], keep = sel.value;
    const all = os.filter((o) => (o.value || "").startsWith("All"));
    const rest = os.filter((o) => !all.includes(o)).sort((a, b) => a.textContent.localeCompare(b.textContent, lang));
    const want = [...rest, ...all];
    if (want.every((o, i) => o === os[i])) return;   // already in order (moving them would loop the observer)
    want.forEach((o) => sel.appendChild(o));
    sel.value = keep;
  }

  function setLang(l) {
    lang = T[l] ? l : "en";
    try { localStorage.setItem("sbmpd-lang", lang); } catch (e) { /* ignore */ }
    document.documentElement.lang = lang;
    busy = true; walk(document.body); resort(); busy = false;
    const note = document.getElementById("lang-note");
    if (note) note.hidden = lang === "en";
    if (window.SiteLinks) window.SiteLinks.set({ lang: lang === "en" ? "" : lang });
  }

  function init() {
    const head = document.querySelector(".hero .wrap");
    const box = document.createElement("label");
    box.className = "lang-select";
    const span = document.createElement("span");
    span.textContent = "Language";
    const sel = document.createElement("select");
    sel.id = "lang-select";
    [["en", "English"], ["fr", "Français"], ["es", "Español"]].forEach(([v, t]) => sel.add(new Option(t, v)));
    sel.value = lang;
    sel.addEventListener("change", () => setLang(sel.value));
    box.append(span, " ", sel);
    const note = document.createElement("span");
    note.id = "lang-note";
    note.className = "muted";
    note.textContent = " Notes and sources are in English.";
    box.appendChild(note);
    head.insertBefore(box, head.firstChild);
    obs.observe(document.body, { childList: true, subtree: true, characterData: true });
    setLang(lang);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
