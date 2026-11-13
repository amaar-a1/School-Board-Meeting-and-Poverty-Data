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
# Enrollment where the World Bank has none. Norfolk Island: residents attending primary (155) and secondary (110)
# school, ABS 2021 Census QuickStats (SAL90004, CC BY 4.0), the measure used for Australia's council areas.
ENR_MANUAL = {"NFK": (265, "2021 Census (residents attending primary and secondary school; ABS)")}
MANUAL = {"NFK": (2.8, "Unemployment rate, a stand-in for poverty (Australian Bureau of Statistics, 2021 Census: 33 of 1,187 in the labour force)"),
          "MAF": (27.0, "Unemployment rate, a stand-in for poverty (census definition, 2023; IEDOM annual report on Saint-Martin, 2025 edition)"),
          "BLM": (1.9, "Unemployment rate, a stand-in for poverty (ILO definition, 2021; IEDOM annual report on Saint-Barthélemy, 2025 edition)")}
# Places added in November 2026, which Natural Earth doesn't list on their own (borders: prep_islands_extra.py).
# Figures found by hand from each place's statistics office (sources in docs/sources.js).
EXTRA = {
    "BON": dict(name="Bonaire", region="Caribbean", status="Special municipality of the Netherlands", rate=29.0,
                measure="Children under 18 living in poverty (Statistics Netherlands, CBS, 2024; below the Caribbean Netherlands social minimum)",
                pop=27611, kids=4202, enr=3764, ey="2025/26 (primary and secondary, CBS)", land=288),
    "STA": dict(name="Sint Eustatius", region="Caribbean", status="Special municipality of the Netherlands", rate=35.0,
                measure="Children under 18 living in poverty (Statistics Netherlands, CBS, 2024; below the Caribbean Netherlands social minimum)",
                pop=3348, kids=587, enr=536, ey="2025/26 (primary and secondary, CBS)", land=21),
    "SAB": dict(name="Saba", region="Caribbean", status="Special municipality of the Netherlands", rate=32.0,
                measure="Children under 18 living in poverty (Statistics Netherlands, CBS, 2024; below the Caribbean Netherlands social minimum)",
                pop=2270, kids=296, enr=252, ey="2025/26 (primary and secondary, CBS)", land=13),
    "CXR": dict(name="Christmas Island", region="Asia and the Indian Ocean", status="Territory of Australia", rate=1.5,
                measure="Unemployment rate, a stand-in for poverty (Australian Bureau of Statistics, 2021 Census: 12 people)",
                pop=1692, kids=283, enr=212, ey="2021 (Census: pupils at government primary and secondary schools)", land=135),
    "CCK": dict(name="Cocos (Keeling) Islands", region="Asia and the Indian Ocean", status="Territory of Australia", rate=2.0,
                measure="Unemployment rate, a stand-in for poverty (Australian Bureau of Statistics, 2021 Census: 5 people)",
                pop=593, kids=125, enr=82, ey="2021 (Census: pupils at government primary and secondary schools)", land=14),
    "GIB": dict(name="Gibraltar", region="Europe and the North Atlantic", status="Territory of the United Kingdom", rate=1.0,
                measure="Unemployment rate, a stand-in for poverty (CIA World Factbook, 2016 estimate)",
                pop=29733, kids=5940, enr=6262, ey="September 2023 (government schools, Gibraltar Health Authority)", land=6.5),
    # Svalbard: NAV's monthly tables count 14 (January 2025) and 11 (July 2025) people fully unemployed in "Svalbard and
    # other areas" but suppress the rate; Statistics Norway counts about 2,500 people employed there (2022, Rapporter
    # 2023/36: 383 more than in 2008, an 18% rise). 12.5 / (2,511 + 12.5) = 0.5%.
    "SJM": dict(name="Svalbard", region="Europe and the North Atlantic", status="Part of Norway", rate=0.5,
                measure="Unemployment rate, an estimate standing in for poverty: about 12 people fully unemployed (NAV, January and July 2025) "
                        "out of about 2,500 in work (Statistics Norway, 2022); Norway's poverty statistics leave Svalbard out",
                # Pupils: Longyearbyen school (grades 1-10, its only Norwegian school), Statistics Norway table 11980, 2025;
                # Barentsburg's small Russian school isn't counted.
                pop=2933, kids=None, enr=194, ey="2025 (Longyearbyen school, grades 1–10: Statistics Norway)", land=61022),
    "CHT": dict(name="Chatham Islands", region="Pacific", status="Part of New Zealand", rate=2.9,
                measure="Unemployed people as a share of everyone aged 15 and over, a stand-in for poverty (Stats NZ, 2023 Census: 15 people)",
                pop=615, kids=99, enr=None, ey="", land=966),
    # Pitcairn: the Pitcairn Island Economic Review (Solomon Leonard for the UK government, January 2014), paragraphs 11 and 234.
    "PCN": dict(name="Pitcairn Islands", region="Pacific", status="Territory of the United Kingdom", rate=0.0,
                measure="Unemployment rate, a stand-in for poverty: all 31 working-age adults held part-time government jobs (Pitcairn Island Economic Review, 2014); "
                        "average household income was about NZ$27,000 a year, a third of New Zealand's",
                pop=50, kids=None, enr=None, ey="", land=47),
    "TKL": dict(name="Tokelau", region="Pacific", status="Territory of New Zealand", rate=3.9,
                measure="People below the basic-needs poverty line, all ages (Tokelau Household Income and Expenditure Survey, 2015/16)",
                pop=2453, kids=None, enr=None, ey="", land=12),
}
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
    "BON": ("https://www.youtube.com/channel/UCxqEdMrLfjuM_PiOW0nfFTg", "all"),   # Konseho Insular Bonaire (the Island Council)
    "STA": ("https://www.youtube.com/channel/UCMHMQ2Ugkm8qLSudfNV-nzg", "all"),   # Island Council Sint Eustatius
    "SAB": ("https://www.youtube.com/channel/UCAag5hACX3kH2zFmB3YvA7w", "filter"),   # Public Entity Saba
    "CXR": ("https://www.youtube.com/channel/UCBskr7IINEHAYUmtMxOoTyg", "all"),   # Shire of Christmas Island
}
# A second channel whose sittings count too (still one per day): the government's channel, which posts some of the same meetings.
MORE_CHANNELS = {"STA": ("https://www.youtube.com/channel/UCHPtYhBXgaCWac8QqxQVZlg", "filter", "Statia Government"),
                 "SAB": ("https://www.youtube.com/channel/UCo-EbrFXLtZOo_XB50hUEbg", "all", "Island Council Saba")}
# Why an island shows 0 meetings, where the reason is more specific than "nothing found".
ZERO_NOTES = {
    "IMN": "No school board meets in public. Tynwald's YouTube channel posts Tynwald Day and committee videos but not its sittings, which it streams on its own website",
    "GGY": "No school board meets in public. The States of Guernsey's YouTube channel posts government news, not States meetings, which are streamed elsewhere",
    "FLK": "No school board meets in public. Falkland Islands Television's channel reports on the Legislative Assembly but doesn't post its sittings",
    "LUX": "Luxembourg's communes run primary schools, but no school board meets in public. The Chamber of Deputies streams its sittings on its own website (Chamber TV), not on YouTube",
    "LIE": "No school board meets in public. No recorded sittings of the Landtag were found on YouTube",
    "SMR": "No school board meets in public. Only party channels post clips of the Consiglio Grande e Generale on YouTube, not full sittings",
    "GRL": "No school board meets in public. KNR, the public broadcaster, posts only a few clips of Inatsisartut sittings",
    "CCK": "No school board meets in public (Western Australia's education department runs the school). No recordings of the Shire of Cocos (Keeling) Islands council were found on YouTube",
    "GIB": "No school board meets in public. GBC News posts reports on the Gibraltar Parliament, not its sittings, and no other channel posts them",
    "SJM": "No school board meets in public (the Longyearbyen Community Council runs the school). Its YouTube channel has only a few information videos, not its meetings",
    "CHT": "No school board meets in public. No recordings of the Chatham Islands Council were found on YouTube",
    "PCN": "No school board meets in public. No recordings of the Island Council were found on YouTube (a channel named Pitcairn Borough is a town in Pennsylvania)",
    "TKL": "No school board meets in public. No recordings of the General Fono, Tokelau's national assembly, were found on YouTube",
}
LEGIS_WORDS = re.compile(r"house of assembly|house of representatives|parliament|parlement|legislative (assembly|council)|national assembly|"
                         r"\bsenate\b|lower house|tynwald|states (assembly|of deliberation|meeting)|\bthe states\b|majlis|nitijela|maneaba|"
                         r"\bcongr[eè]s|\bcongress\b|assembl[ée]e|assembleia|conseil territorial|inatsisartut|fono|ολομέλεια|βουλ|مجلس|"
                         r"olbiil|regional council|island council|konseho insular|central committee|sitting|séance|sessão|sess[ãa]o plen|plen[áa]ri|kantonsrat|grosse[nr]? rat|landrat|grand conseil|"
                         r"gran consiglio|parlement jurassien|consell general|conseil national|landtag", re.I)
SITTING = re.compile(r"reuni[oó]n|sitting|session|séance|seance|sess[ãa]o|meeting|plen[aá]r|plénière|συνεδρ|ολομέλεια|جلسة|vergadering|"
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
              "islands/youtube/islands_titles_more.json", "switzerland/youtube/titles.json"):   # the last has the microstates' parliaments
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
        if not both and iso in ENR_MANUAL: enr, ey = ENR_MANUAL[iso]
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
    for iso, e in EXTRA.items():
        dens = e["pop"] / e["land"]
        out.append({"District": e["name"], "Region": e["region"], "Status": e["status"],
                    "Available Board Meetings": 0, "Meetings source": "", "Latest meeting": "", "Meetings by year": "", "Meetings note": "",
                    "Poverty rate or stand-in": f"{e['rate']:.2f}%" if e["rate"] is not None else "", "Poverty measure": e["measure"],
                    "Population": e["pop"], "Children Ages 0-14 (estimated)": e["kids"] or "", "Enrollment": e["enr"] or "", "Enrollment year": e["ey"],
                    "Locale": "Urban" if dens >= 2000 else "Suburban" if dens >= 500 else "Mixed" if dens >= 100 else "Rural",
                    "People per km² (estimated)": round(dens), "District ID": f"ISLE-{iso}"})
    out.sort(key=lambda r: r["District"])
    for r in out:
        iso = r["District ID"].split("-", 1)[1]
        url, mode = ISLAND_CHANNELS.get(iso, ("", ""))
        n, kept = sittings(titles[url], mode) if url and url in titles else (0, [])
        if iso in MORE_CHANNELS and MORE_CHANNELS[iso][0] in titles:
            n2, kept2 = sittings(titles[MORE_CHANNELS[iso][0]], MORE_CHANNELS[iso][1])
            kept = kept + kept2; n = len({sitting_key(t) for t in kept})
        if n:
            from meeting_dates import summary as date_summary
            r["Latest meeting"], r["Meetings by year"] = date_summary(kept)
            r["Available Board Meetings"] = n
            r["Meetings source"] = url
            on = names.get(iso, "its YouTube channel") + (f" and {MORE_CHANNELS[iso][2]}" if iso in MORE_CHANNELS else "")
            body = "the island council" if iso in ("BON", "STA", "SAB") else "the shire council" if iso == "CXR" else "the legislature"
            r["Meetings note"] = (f"Stand-in: recorded sittings (and committee meetings) of {body} on {on}, one per day; "
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
    for f in json.load(open(os.path.join(IN, "islands", "extra_borders.geojson"), encoding="utf-8"))["features"]:
        feats.append({"type": "Feature", "properties": {"id": f"ISLE-{f['properties']['ISO']}", "NAME": f["properties"]["NAME"]},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", "islands.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for r in out:
        print(f"{r['District'][:28]:28} {r['Region'][:12]:12} {r['Poverty rate or stand-in']:>7} {r['Poverty measure'][:55]:55} enr {r['Enrollment']!s:>7} {r['Enrollment year']} {r['Locale']}")


if __name__ == "__main__":
    main()
