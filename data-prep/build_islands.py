"""Build docs/data/islands.csv and docs/data/map/islands.json: small island countries and territories.

Each island country or territory runs its schools through one government education ministry or
department, so each is a single "district". (Iceland's municipalities run its compulsory schools;
it's shown as one unit here.) The US territories and Saint-Pierre-et-Miquelon have their own views.
- Borders: Natural Earth 1:10m admin-0 (public domain), inputs/world/ne_10m_islands.geojson.
- Poverty, best available for each place, in this order:
  1. children under 18 below 60% of the median income (Eurostat EU-SILC ilc_li02): Malta, Cyprus;
  2. people below the national poverty line (World Bank SI.POV.NAHC, else the CIA World Factbook);
  3. unemployment rate as a stand-in (World Bank SL.UEM.TOTL.ZS, ILO estimate, else the Factbook).
  The national poverty lines differ from country to country, so these aren't comparable.
- Enrollment: primary plus secondary pupils (World Bank SE.PRM.ENRL + SE.SEC.ENRL, UNESCO), latest year
  with both.
- Children: population x share aged 0-14 (World Bank, else the Factbook).
- Locale (estimated): people per km² of land (Factbook area): urban 2,000+, suburban 500-2,000, mixed
  100-500, rural under 100.
Usage: python3 data-prep/build_islands.py
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")
DOCS = os.path.join(HERE, "..", "docs", "data")
REGION = {"Caribbean": "Caribbean", "Polynesia": "Pacific", "Melanesia": "Pacific", "Micronesia": "Pacific",
          "Australia and New Zealand": "Pacific", "Northern Europe": "Europe and the North Atlantic",
          "Southern Europe": "Europe and the North Atlantic", "Western Asia": "Asia and the Indian Ocean",
          "South-Eastern Asia": "Asia and the Indian Ocean", "Southern Asia": "Asia and the Indian Ocean",
          "Eastern Africa": "Africa and the South Atlantic", "Western Africa": "Africa and the South Atlantic",
          "Middle Africa": "Africa and the South Atlantic", "South America": "Africa and the South Atlantic",
          "Northern America": "Europe and the North Atlantic", "Seven seas (open ocean)": "Africa and the South Atlantic"}
NAMES = {"Antigua and Barb.": "Antigua and Barbuda", "St. Kitts and Nevis": "Saint Kitts and Nevis", "St. Vin. and Gren.": "Saint Vincent and the Grenadines",
         "Cayman Is.": "Cayman Islands", "British Virgin Is.": "British Virgin Islands", "Turks and Caicos Is.": "Turks and Caicos Islands",
         "Solomon Is.": "Solomon Islands", "Cook Is.": "Cook Islands", "Marshall Is.": "Marshall Islands", "Fr. Polynesia": "French Polynesia",
         "Wallis and Futuna Is.": "Wallis and Futuna", "Falkland Is.": "Falkland Islands", "Faeroe Is.": "Faroe Islands",
         "St-Barthélemy": "Saint-Barthélemy", "St-Martin": "Saint-Martin (French part)", "Sint Maarten": "Sint Maarten (Dutch part)",
         "Micronesia": "Federated States of Micronesia", "São Tomé and Principe": "São Tomé and Príncipe",
         "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha"}
# Figures found by hand where neither the World Bank nor the Factbook has one.
MANUAL = {"NFK": (2.8, "Unemployment rate, a stand-in for poverty (Australian Bureau of Statistics, 2021 Census: 33 of 1,187 in the labour force)"),
          "MAF": (27.0, "Unemployment rate, a stand-in for poverty (census definition, 2023; IEDOM annual report on Saint-Martin, 2025 edition)"),
          "BLM": (1.9, "Unemployment rate, a stand-in for poverty (ILO definition, 2021; IEDOM annual report on Saint-Barthélemy, 2025 edition)")}
# Meetings: no island has a school board (a ministry runs the schools), so, as for Saint-Pierre-et-Miquelon,
# the stand-in is the elected legislature's sittings on its YouTube channel (islands_youtube.py finds
# them; checked by hand). "all": the legislature's own channel, where every dated sitting counts;
# "filter": a government channel or public broadcaster, where only titles naming the legislature count.
ISLAND_CHANNELS = {
    "AIA": ("https://www.youtube.com/channel/UCjiAiUlclJclXnl21fFCwuA", "all"),   # Anguilla House of Assembly
    "ATG": ("https://www.youtube.com/channel/UCK3jWfTQ9Z-3I8nsZoh-YDQ", "filter"),   # GovernmentOf AntiguaBarbuda
    "BHS": ("https://www.youtube.com/channel/UCzPJSjQcWfBBwsUutIGFh2w", "all"),   # Bahamas Parliament
    "BHR": ("https://www.youtube.com/channel/UCfxhU2lYxn1IwNUSSxsyiaQ", "all"),   # مجلس النواب Council of Representatives
    "BRB": ("https://www.youtube.com/channel/UCnAo0XVbxFF2UCpkIkAS-6A", "all"),   # Barbados Parliament Channel
    "VGB": ("https://www.youtube.com/channel/UCVDl37r5uaMsdQkgzFkXAJg", "all"),   # House of Assembly VI
    "CPV": ("https://www.youtube.com/channel/UC5ACfRTTXZPcxtPyWQ6idGA", "all"),   # Assembleia Nacional de Cabo Verde
    "CYM": ("https://www.youtube.com/channel/UCGVlgTtKrEQHpXgoGNH_e7w", "filter"),   # Cayman Islands Government
    "COK": ("https://www.youtube.com/channel/UC6NJVTHu-5eMP88UrGi7KqA", "all"),   # Cook Islands Parliament
    "CYP": ("https://www.youtube.com/channel/UC16VW_MkPM-9zu_E3wYweOw", "all"),   # HoR Cyprus
    "DMA": ("https://www.youtube.com/channel/UCPhmdFljqjcsh6eeQz7_W6Q", "filter"),   # Government of Dominica
    "FLK": ("https://www.youtube.com/channel/UCh0L8fHZWyH6X6fvw8u-58Q", "filter"),   # Falkland Islands Television
    "FSM": ("https://www.youtube.com/channel/UCo_dc4xUi_eA5poaFqHeGpA", "all"),   # FSM CONGRESS LIVE STREAMING
    "FJI": ("https://www.youtube.com/channel/UCxLeKmHqzi8lXSt7iahHCSg", "all"),   # PARLIAMENT OF THE REPUBLIC OF FIJI
    "PYF": ("https://www.youtube.com/channel/UCloO4Y-IYevM0CI40h-gUoQ", "all"),   # AssembleePolynesie
    "GRL": ("https://www.youtube.com/channel/UCIjOAtv53RHerlfl98fZmcQ", "filter"),   # Kalaallit Nunaata Radioa | KNR TV
    "GRD": ("https://www.youtube.com/channel/UCHuhtDvg1bcJC9aP7ZjBHfw", "all"),   # Grenada Houses of Parliament HOPGrenada
    "GGY": ("https://www.youtube.com/channel/UCC7bV5KJPlbGILCAVj3Th_A", "filter"),   # States of Guernsey
    "IMN": ("https://www.youtube.com/channel/UC7GKuEIT2_CMuGM-i6q-hXQ", "all"),   # Tynwald - the Parliament of the Isle of Man
    "JAM": ("https://www.youtube.com/channel/UC8X0kkF7HNdWUxTMjAagJxw", "filter"),   # pbcjamaica
    "JEY": ("https://www.youtube.com/channel/UC_YQyGJnnapagsgpDBwpsDg", "all"),   # States Assembly – Jersey’s elected parliament
    "KIR": ("https://www.youtube.com/channel/UC6hL4ApJbKNXZZHYuVxRM4A", "all"),   # Maneaba ni Maungatabu
    "MDV": ("https://www.youtube.com/channel/UCCNGwK1wJExFHdRxUzcbZtg", "all"),   # People's Majlis
    "MHL": ("https://www.youtube.com/channel/UCaC1H0k4_JELFWyRmbhsD4g", "all"),   # Nitijela - Parliament of Marshall Islands
    "MUS": ("https://www.youtube.com/channel/UCpRbEVvMAHS45Y1mbHLwbbQ", "all"),   # Mauritius National Assembly
    "NCL": ("https://www.youtube.com/channel/UC8EZmJGsQHhhXQxB4gtxtiQ", "all"),   # Congrès de la Nouvelle-Calédonie
    "NFK": ("https://www.youtube.com/channel/UCcB_GOAFVvtOogfua9xFooA", "all"),   # Norfolk Island Regional Council
    "PLW": ("https://www.youtube.com/channel/UCc7VufcUmUXMkZutIR7H9Jg", "all"),   # The Senate, Palau National Congress
    "SHN": ("https://www.youtube.com/channel/UCBFgWiNkm0VVvAyBWH0CkkQ", "filter"),   # St Helena Government
    "KNA": ("https://www.youtube.com/channel/UCMM3pFsfN2CYHpUa-xMbKQg", "filter"),   # ZIZOnline
    "LCA": ("https://www.youtube.com/channel/UC4al3A_gysYEIzAM1L2qZbg", "filter"),   # Saint Lucia Government
    "MAF": ("https://www.youtube.com/channel/UCjbcair9XWLnDqRjEpYa4ig", "filter"),   # Collectivité de Saint-Martin Our News
    "WSM": ("https://www.youtube.com/channel/UCr3GMtN93gkstVvc0FAu83Q", "all"),   # Samoa Parliament
    "SYC": ("https://www.youtube.com/channel/UCTqupZT9yhkwOG3nmtRluig", "all"),   # The National Assembly of Seychelles
    "SGP": ("https://www.youtube.com/channel/UC1NBkF4mXpQXvokXgRomh9w", "filter"),   # MDDI Singapore
    "SXM": ("https://www.youtube.com/channel/UCUJgZueTkFd-iJzYvKgJ-qg", "all"),   # Sint Maarten Parliament
    "SLB": ("https://www.youtube.com/channel/UCqGCc68Oy5I19akSiXsm5Ow", "all"),   # National Parliament of Solomon Islands
    "STP": ("https://www.youtube.com/channel/UCOX7tuDH1IF2wsJ8mdjpT9A", "all"),   # Assembleia Nacional de São Tomé e Príncipe
    "TTO": ("https://www.youtube.com/channel/UCDvTAcd3t8yEAIiM-Ck49lg", "all"),   # ParlView (the Parliament of Trinidad and Tobago's broadcast channel)
    "TCA": ("https://www.youtube.com/channel/UChNtWbhuWfZMjZtAnrE7SEQ", "all"),   # Parliament of the Turks and Caicos Islands
    "VUT": ("https://www.youtube.com/channel/UCxEEMV6ADp7-h5yFPxqTidw", "all"),   # Vanuatu Parliament
    "MSR": ("https://www.youtube.com/channel/UCSrOT5JzaIXcr1btNC9LaTQ", "all"),   # Montserrat Legislative Assembly
    "VCT": ("https://www.youtube.com/channel/UCnSUlj13EVE449biHplmLlw", "filter"),   # API SVG (government information service)
    "MCO": ("https://www.youtube.com/channel/UCrUztlaGkaqr6AeONbmfcCw", "all"),   # Conseil National TV (Monaco)
    "AND": ("https://www.youtube.com/channel/UC8DPQPM6kHQ7ygyPgDicHyA", "all"),   # Consell General (Andorra)
}
# Why an island shows 0 meetings, where the reason is more specific than "nothing found".
ZERO_NOTES = {
    "IMN": "No school board meets in public. Tynwald's YouTube channel posts Tynwald Day and committee videos but not its sittings, which it streams on its own website",
    "GGY": "No school board meets in public. The States of Guernsey's YouTube channel posts government news, not States meetings, which are streamed elsewhere",
    "FLK": "No school board meets in public. Falkland Islands Television's channel reports on the Legislative Assembly but doesn't post its sittings",
    "LUX": "Luxembourg's communes run primary schools, but no school board meets in public. The Chamber of Deputies streams its sittings on its own website (Chamber TV), not on YouTube",
    "LIE": "No school board meets in public. No recorded sittings of the Landtag were found on YouTube",
    "SMR": "No school board meets in public. Only party channels post clips of the Consiglio Grande e Generale on YouTube, not full sittings",
    "GRL": "No school board meets in public. KNR, the public broadcaster, posts only a few clips of Inatsisartut sittings",
}
LEGIS_WORDS = re.compile(r"house of assembly|house of representatives|parliament|parlement|legislative (assembly|council)|national assembly|"
                         r"\bsenate\b|lower house|tynwald|states (assembly|of deliberation|meeting)|\bthe states\b|majlis|nitijela|maneaba|"
                         r"\bcongr[eè]s|\bcongress\b|assembl[ée]e|assembleia|conseil territorial|inatsisartut|fono|ολομέλεια|βουλ|مجلس|"
                         r"olbiil|regional council|sitting|séance|sessão|sess[ãa]o plen|plen[áa]ri|kantonsrat|grosse[nr]? rat|landrat|grand conseil|"
                         r"gran consiglio|parlement jurassien|consell general|conseil national|landtag", re.I)
SITTING = re.compile(r"sitting|session|séance|seance|sess[ãa]o|meeting|plen[aá]r|plénière|συνεδρ|ολομέλεια|جلسة|vergadering|"
                     r"the honourable the (house|senate)|house of (assembly|representatives)|\bsenate\b|maneaba|ataatsimiinne|states meeting|"
                     r"question (time|hour)|budget (debate|address)|\bcrs\b|nitijela|regular session|"
                     r"sitzung|kantonsrat|grosse[nr]? rat|landrat|grand conseil|gran consiglio|seduta|sessione|sessi[óo]|consell general|conseil national", re.I)
NUMBERED = re.compile(r"\b\d+(st|nd|rd|th|ª|º|e|ème)?\s+(sitting|meeting|day|session|séance|sessão|reunião)|\bday\s+\d+|\bmeeting\s*(no\.?|#)\s*\d+|"
                      r"\bpublic meeting\s*#?\s*\d+|الانعقاد|دور", re.I)
NOT_SITTING = re.compile(r"how to|interview|trailer|promo|highlight|tour of|visit|youth|children|mock|explain|documentar|podcast|shorts|"
                         r"announcement|press (conference|briefing)|remarks|message|speech|discours|ομιλία|ceremon|cérémon|signing|sign |"
                         r"delegat|recebe|calls on|courtesy|in 90 seconds|cosac|personalit|clerk's corner|update|outreach|getting to know|"
                         r"know the house|luncheon|showcase|workshop|training|validation|forum|conference|launch|tynwald day|wins at|hustings|know your house|released|news", re.I)
MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|janv|févr|fevr|mars|avr|mai|juin|juil|août|aout|sept|déc|janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"


def sitting_key(t):
    """One key per sitting day: its date in any common format, else the title without part markers."""
    s = t.lower()
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?[\s./-]+(" + MONTHS + r")\w*\.?,?[\s./-]+(\d{4})", s) \
        or re.search(r"\b(" + MONTHS + r")\w*\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", s)
    if m: return "d" + "-".join(sorted(m.groups()))
    m = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})\b", s) or re.search(r"\b(\d{4})[./-](\d{1,2})[./-](\d{1,2})\b", s)
    if m: return "n" + "-".join(str(int(x)) for x in m.groups())
    return re.sub(r"\b(part|pt|parte|partie|session)\s*\w+\b|\(\d\)|\d/\d|[-–|]", " ", s).split("  ")[0].strip()


def sittings(titles, mode):
    dated = lambda t: re.search(r"\b(19|20)\d{2}\b|\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b", t)
    keep = [t for t in titles if SITTING.search(t) and not NOT_SITTING.search(t) and (dated(t) or NUMBERED.search(t))
            and (mode == "all" or LEGIS_WORDS.search(t))]
    return len({sitting_key(t) for t in keep}), keep


pct = lambda s: float(re.match(r"\s*([\d.]+)%", s).group(1)) if s and re.match(r"\s*([\d.]+)%", s) else None
year = lambda s: (re.search(r"\((\d{4})", s or "") or [None, ""])[1]
num = lambda s: float(re.match(r"\s*([\d,.]+)", s).group(1).replace(",", "")) if s and re.match(r"\s*[\d,.]*\d", s) else None


def txt(v):
    return v.get("text") if isinstance(v, dict) and "text" in v else v


def fb_latest(v):
    """Factbook values: plain text, or {"Unemployment rate 2024": {"text": ...}, ...}."""
    if v is None: return None, ""
    if isinstance(v, dict) and "text" not in v:
        ks = sorted((k for k in v if re.search(r"\d{4}$", k)), reverse=True)
        v = v[ks[0]] if ks else None
    t = txt(v)
    return (pct(t), year(t)) if t else (None, "")


def main():
    ne = {o["ISO_A3"]: o for o in json.load(open(os.path.join(IN, "world", "islands_ne.json"), encoding="utf-8"))}
    fb = json.load(open(os.path.join(IN, "islands", "factbook_extract.json"), encoding="utf-8"))
    # The 2026 Factbook dropped poverty and unemployment for many territories; the November 2023
    # edition (factbook.json commit 546573f) still has them, often from older surveys.
    old = json.load(open(os.path.join(IN, "islands", "factbook_2023_economy.json"), encoding="utf-8"))["data"]
    wb = json.load(open(os.path.join(IN, "islands", "worldbank.json")))
    W = {}
    for ind, rows in wb.items():
        for r in rows:
            W.setdefault(ind, {}).setdefault(r["countryiso3code"], {})[int(r["date"])] = r["value"]
    latest = lambda ind, iso: max(W.get(ind, {}).get(iso, {}).items(), default=(None, None))
    es = json.load(open(os.path.join(IN, "islands", "eurostat_ilc_li02.json")))
    ids, size = es["id"], es["size"]; cat = {k: list(es["dimension"][k]["category"]["index"]) for k in ids}
    def esv(geo, t):
        if geo == "LU":   # in a second Eurostat download
            ids2, size2 = lu["id"], lu["size"]; cat2 = {k: list(lu["dimension"][k]["category"]["index"]) for k in ids2}
            if t not in cat2["time"]: return None
            sel = dict(freq="A", statinfo="MED_EI", unit="PC", rskpovth="B_60", sex="T", age="Y_LT18", geo=geo, time=t); i = 0
            for k, n in zip(ids2, size2): i = i * n + cat2[k].index(sel[k])
            return lu["value"].get(str(i))
        sel = dict(freq="A", statinfo="MED_EI", unit="PC", rskpovth="B_60", sex="T", age="Y_LT18", geo=geo, time=t); i = 0
        for k, s in zip(ids, size): i = i * s + cat[k].index(sel[k])
        return es["value"].get(str(i))
    ISO2 = {"MLT": "MT", "CYP": "CY", "ISL": "IS", "LUX": "LU"}
    lu = json.load(open(os.path.join(IN, "islands", "eurostat_ilc_li02_lu_ch.json")))
    titles = {}
    for f in ("islands/youtube/islands_titles.json", "islands/youtube/islands_titles_extra.json", "islands/youtube/islands_titles_parlview.json",
              "switzerland/youtube/titles.json"):   # the last has the microstates' parliaments
        p = os.path.join(IN, f)
        if os.path.exists(p): titles.update(json.load(open(p, encoding="utf-8")))
    from shared_titles import shared_titles
    titles.update(shared_titles())
    names = {}
    for line in open(__file__, encoding="utf-8"):
        m = re.match(r'\s+"([A-Z]{3})": \("([^"]+)", "(all|filter)"\),\s+# (.+)', line)
        if m: names[m.group(1)] = m.group(4).strip()
    out = []
    for iso, n in sorted(ne.items(), key=lambda x: NAMES.get(x[1]["NAME"], x[1]["NAME"])):
        if iso == "ISL":   # Iceland has its own data set (municipalities), docs/data/iceland.csv
            continue
        f = fb.get(n["ADM0_A3"]) or fb.get(iso) or {}
        econ = {**old.get(iso, {}), **f.get("Economy", {})}
        name = NAMES.get(n["NAME"], n["NAME"])
        rate = measure = ""
        if iso in ISO2:
            t = max((t for t in set(cat["time"]) | {"2023", "2024", "2025"} if esv(ISO2[iso], t) is not None), default=None)
            if t: rate, measure = esv(ISO2[iso], t), f"Children under 18 below 60% of the median income (Eurostat EU-SILC, {t})"
        if rate == "":
            y, v = latest("SI.POV.NAHC", iso)
            fv, fy = fb_latest(econ.get("Population below poverty line"))
            if v is not None and (not fy or int(fy) <= y):
                rate, measure = v, f"People below the national poverty line, all ages (World Bank, {y})"
            elif fv is not None:
                rate, measure = fv, f"People below the national poverty line, all ages (CIA World Factbook, {fy} estimate)"
        if rate == "" and iso in MANUAL:
            rate, measure = MANUAL[iso]
        if rate == "":
            y, v = latest("SL.UEM.TOTL.ZS", iso)
            fv, fy = fb_latest(econ.get("Unemployment rate"))
            if fv is not None and (y is None or (fy and int(fy) >= y)):
                rate, measure = fv, f"Unemployment rate, a stand-in for poverty (CIA World Factbook, {fy} estimate)"
            elif v is not None:
                rate, measure = v, f"Unemployment rate, a stand-in for poverty (World Bank / ILO estimate, {y})"
        py, pop = latest("SP.POP.TOTL", iso)
        if pop is None:
            pop = num(txt((f.get("People and Society", {}).get("Population") or {}).get("total")) if isinstance(f.get("People and Society", {}).get("Population"), dict) else txt(f.get("People and Society", {}).get("Population")))
        _, share = latest("SP.POP.0014.TO.ZS", iso)
        if share is None:
            share = pct(txt((f.get("People and Society", {}).get("Age structure") or {}).get("0-14 years")))
        # Enrollment: latest year with both primary and secondary.
        pr, se = W.get("SE.PRM.ENRL", {}).get(iso, {}), W.get("SE.SEC.ENRL", {}).get(iso, {})
        both = sorted(set(pr) & set(se))
        enr, ey = (round(pr[both[-1]] + se[both[-1]]), str(both[-1])) if both else ("", "")
        area = f.get("Geography", {}).get("Area") or {}
        land = num(txt(area.get("land"))) or num(txt(area.get("total") or area.get("total ")))
        dens = pop / land if pop and land else None
        loc = "" if dens is None else "Urban" if dens >= 2000 else "Suburban" if dens >= 500 else "Mixed" if dens >= 100 else "Rural"
        sov = n["SOVEREIGNT"]
        status = "Independent country" if sov in (n["NAME"], n["NAME_LONG"]) or iso in ("FSM", "KNA", "VCT", "ATG", "STP", "BHS", "MHL", "SLB") else f"Territory of {'the United Kingdom' if sov == 'United Kingdom' else 'the Netherlands' if sov == 'Netherlands' else sov}"
        if iso in ("COK", "NIU"): status = "Self-governing, in free association with New Zealand"
        out.append({"District": name, "Region": "European microstates" if n.get("MICRO") else REGION.get(n["SUBREGION"], n["SUBREGION"]), "Status": status,
                    "Available Board Meetings": 0, "Meetings source": "", "Latest meeting": "", "Meetings by year": "", "Meetings note": "",
                    "Poverty rate or stand-in": f"{rate:.2f}%" if rate != "" else "", "Poverty measure": measure,
                    "Population": round(pop) if pop else "", "Children Ages 0-14 (estimated)": round(pop * share / 100) if pop and share else "",
                    "Enrollment": enr, "Enrollment year": ey, "Locale": loc, "People per km² (estimated)": round(dens) if dens else "",
                    "District ID": f"ISLE-{iso}"})
    for r in out:
        iso = r["District ID"].split("-", 1)[1]
        url, mode = ISLAND_CHANNELS.get(iso, ("", ""))
        n, kept = sittings(titles[url], mode) if url and url in titles else (0, [])
        if n:
            from meeting_dates import summary as date_summary
            r["Latest meeting"], r["Meetings by year"] = date_summary(kept)
            r["Available Board Meetings"] = n
            r["Meetings source"] = url
            r["Meetings note"] = (f"Stand-in: recorded sittings (and committee meetings) of the legislature on {names.get(iso, 'its YouTube channel')}, one per day; "
                                  "no school board meets in public")
        else:
            r["Meetings note"] = ZERO_NOTES.get(iso, "No school board meets in public, and no recorded sittings of the legislature were found on YouTube "
                                                     "(the search found only news, party or other countries' channels); it may stream on its own website")
    cols = list(out[0])
    with open(os.path.join(DOCS, "islands.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=cols); w.writeheader(); w.writerows(out)
    shapes = json.load(open(os.path.join(IN, "world", "ne_10m_islands.geojson"), encoding="utf-8"))
    iso_of = {o["ADM0_A3"]: o["ISO_A3"] for o in ne.values()}
    rnd = lambda c: [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]
    feats = [f for f in shapes["features"] if f["properties"]["ADM0_A3"] != "ISL"]
    shapes["features"] = feats
    feats = [{"type": "Feature", "properties": {"id": f"ISLE-{iso_of[f['properties']['ADM0_A3']]}", "NAME": f["properties"]["NAME"]},
              "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}} for f in shapes["features"]]
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", "islands.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for r in out:
        print(f"{r['District'][:28]:28} {r['Region'][:12]:12} {r['Poverty rate or stand-in']:>7} {r['Poverty measure'][:55]:55} enr {r['Enrollment']!s:>7} {r['Enrollment year']} {r['Locale']}")


if __name__ == "__main__":
    main()
