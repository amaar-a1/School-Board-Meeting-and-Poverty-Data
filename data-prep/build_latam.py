"""Build docs/data/chile.csv, docs/data/colombia.csv and their map files.

Chile: 345 comunas. Public schools are run by each municipality (its education department, DAEM, or
corporation) or, where the 2017 reform has reached, by a Local Public Education Service (SLEP).
- Poverty: Ministerio de Desarrollo Social y Familia, small-area estimates (SAE) 2024: share of people
  (all ages) in income poverty; the multidimensional rate is a second column. No child rate is
  published by comuna.
- Enrollment: Mineduc, Resumen de Matrícula por Establecimiento 2026, added up by comuna.
Colombia: 1,122 municipalities. Schools are run by the 96 "certified" territorial entities (ETC:
departments, districts and larger municipalities); the others' schools are run by their department.
- Poverty: DANE, multidimensional poverty index (IPM) by municipality from the 2018 census, all ages.
- Enrollment (estimated): Ministry of Education statistics by municipality, 2024: children 5-16 times
  the net enrollment rate for ages 5-16 (datos.gov.co nudc-7mev).
Both:
- Borders: geoBoundaries (gbOpen) ADM3 (Chile) and ADM2 (Colombia), simplified. Colombian municipalities
  are matched by name within their department, found from where each lies.
- Meetings (stand-in): municipal council (concejo municipal) sessions on the municipality's or council's
  own YouTube channel (nordic_youtube.py, countries CL and CO), its education committee where recorded,
  counted once per day.
- Locale (estimated): people per km² (Chile: projected population; Colombia: children 5-16 / 0.19).
Usage: python3 data-prep/build_latam.py
"""
import csv, json, os, re, sys, unicodedata
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2
from meeting_dates import parse as parse_date, summary as date_summary
from shared_titles import shared_titles

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")
DOCS = os.path.join(HERE, "..", "docs", "data")
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
ALIAS = {"CL": {"paiguano": "paihuano", "marchigue": "marchihue", "aisen": "aysen", "coihaique": "coyhaique", "llayllay": "llaillay", "padrelascasas": "padrelascasas",
                "ohiggins": "ohiggins", "trehuaco": "treguaco", "lascabras": "lascabras", "cabodehornos": "cabodehornos"},
         "CO": {"bogota": "bogotadc", "bogotadistritocapital": "bogotadc", "sanandres": "sanandres", "cartagena": "cartagenadeindias",
                "guadalajaradebuga": "buga", "santafedebogota": "bogotadc", "sanandresdetumaco": "tumaco", "sanjosedecucuta": "cucuta",
                "sanjosedetoluviejo": "toluviejo", "villadesandiegodeubate": "ubate", "tiquisio": "tiquiso", "papunahua": "papunauacordepartamental",
                "colosoricaurte": "coloso", "elsantuario": "santuario"},
         "MX": {"tlaquepaque": "sanpedrotlaquepaque"},
         # Spain: the borders file's older or other-language names
         "ES": {"maomahon": "mao", "castellplatjadaro": "castelldaroplatjadaroisagaro", "santcarlesdelarapita": "larapita",
                "alcocerdeplanes": "alcosser", "villanuevadecastellon": "castello"}}
EDU = re.compile(r"comisi[óo]n (de )?educaci[óo]n|educaci[óo]n.*comisi[óo]n|comisi[óo]n de cultura y educaci[óo]n", re.I)
COUNCIL = re.compile(r"sesi[óo]n|plenaria|concejo", re.I)
COUNCIL_MUST = re.compile(r"concejo|sesi[óo]n (ordinaria|extraordinaria|plenaria|n[°º.]|del concejo)|plenaria", re.I)
NOT_T = re.compile(r"live session|cuenta p[úu]blica|entrevista|noticias|resumen|capsula|cápsula|juvenil|infantil|niñ|elecci|campaña|candidat|aniversario|fiesta|"
                   r"himno|desfile|tedeum|te deum|saludo|felicit|programa|podcast|rendici[óo]n", re.I)


def pip(pt, geom):
    """Point in polygon (ray casting) for a Polygon or MultiPolygon."""
    x, y = pt
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        ring = poly[0]; inside = False; j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]; xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: inside = not inside
            j = i
        if inside: return True
    return False


def centroid(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    ring = max((p[0] for p in polys), key=len)
    a = cx = cy = 0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        c = x0 * y1 - x1 * y0; a += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    return (cx / (3 * a), cy / (3 * a)) if a else tuple(ring[0])


_CACHE = {}
DIRS = {"CL": "chile", "CO": "colombia", "MX": "mexico", "BR": "brazil", "PE": "peru", "ES": "spain"}
# Brazil: municipal chambers (câmara municipal) and their education committees, in Portuguese.
RULES = {"BR": (re.compile(r"comiss[ãa]o (permanente )?de educa[çc][ãa]o|educa[çc][ãa]o.*comiss[ãa]o", re.I),
                re.compile(r"sess[ãa]o|c[âa]mara", re.I),
                re.compile(r"sess[ãa]o (ordin[áa]ria|extraordin[áa]ria|solene|especial|de |da |n[°º.]|\d)|\d+[ªa]? sess[ãa]o|sess[ãa]o plen", re.I),
                re.compile(r"live session|entrevista|not[íi]cias|resumo|podcast|programa|campanha|candidat|anivers[áa]rio|festa|hino|desfile|"
                           r"homenagem|solene|culto|missa|show|jogo|futebol|sess[ãa]o de fotos|mirim|mirins|parlamento jovem|c[âa]mara jovem|estudantil", re.I))}

# Mexico: the town council (cabildo, ayuntamiento) and its education committee (comisión edilicia de educación).
# Some titles come back machine-translated into English. Other committees' sessions don't count as council
# meetings, and municipal election councils (consejo municipal electoral) aren't the town council.
RULES["MX"] = (re.compile(r"comisi[óo]n (edilicia )?(de |del )?[\"“]?((salud|cultura|deporte|ciencia)s? y )?educaci[óo]n|educaci[óo]n.*comisi[óo]n|"
                          r"education(al)? (committee|commission)|(committee|commission) (on|of|for) education", re.I),
               re.compile(r"sesi[óo]n|session", re.I),
               re.compile(r"^(?!.*(comisi[óo]n|comit[ée]|consejo|committee|commission|board|electoral)).*(sesi[óo]n (ordinaria|extraordinaria|solemne|p[úu]blica|abierta|"
                          r"de cabildo|del? (h\.? )?(cabildo|ayuntamiento|concejo)|n[°º.]|\d)|\d+\S* sesi[óo]n|"
                          r"(ordinary|extraordinary|solemn|open|public) (town |city )?(council )?(session|meeting)|council (session|meeting)|cabildo abierto)", re.I),
               re.compile(NOT_T.pattern + r"|consejo municipal electoral|consejo municipal \d|junta municipal \d|electoral", re.I))

# Peru: the district or provincial council (concejo municipal) and its education committee. A provincial council
# is also the council of the province's capital district. Ceremonial sessions (sesión solemne, for anniversaries),
# cooking demonstrations (sesiones demostrativas) and the citizen-security committees (CODISEC, COPROSEC) aren't
# council meetings.
RULES["PE"] = (re.compile(r"comisi[óo]n (ordinaria )?(de |del )?((cultura|deporte)s? y )?educaci[óo]n|educaci[óo]n.*comisi[óo]n", re.I),
               re.compile(r"sesi[óo]n", re.I),
               re.compile(r"sesi[óo]n (ordinaria |extraordinaria |descentralizada )?(de |del )(h\.? |honorable )?(concejo|consejo municipal)|"
                          r"sesi[óo]n (ordinaria|extraordinaria|descentralizada)|(ordinaria|extraordinaria) de concejo", re.I),
               re.compile(NOT_T.pattern + r"|solemne|demostrativa|codisec|coprosec|cosoc|comit[ée]|regional|delegados|ministros|gimnasia|miss |audiencia|congreso", re.I))

# Spain: the town council's plenary session (pleno; ple or plenari in Catalan and Valencian, osoko bilkura in Basque)
# and any council committee that covers education ("Comisión de Euskera, Cultura, Educación..."). Children's and
# youth plenaries, committee meetings and "en pleno ..." phrases aren't council meetings.
RULES["ES"] = (re.compile(r"^(?!.*(sant jordi|homenat|reglament|agenda urbana|districte de|distrito de|consultiva)).*(comisi[óo]n|comissi[óo])\b[^|]{0,70}\beducaci[óo]n?\b", re.I),
               re.compile(r"\bple(no|nari|nario)?s?\b|plenaria|pl[eè]n[àa]ria|osoko bilkura", re.I),
               re.compile(r"^(?!.*(comisi[óo]n|comissi[óo]|junta de gobierno)).*(^|[\s\-|.:\[(\"'»«])(ple|pleno|plenari|plenario)(\s+(ordinari[oa]?|extraordinari[oa]?|urgent[e]?|municipal|del?\b|do\b|de l|d'|d’|corporatiu|\d)|[\s\-_.:(\[|]*\d|\s*$)|"
                          r"sesi[óo]n plenaria|sessi[óo] pl[eè]n[àa]ria|osoko bilkura", re.I),
               re.compile(NOT_T.pattern + r"|escolar|jove|joven|xiquet|mayores|majors|consell|consejo|resum|avance|previa|"
                          r"teaser|prueba|declaraci|\ben pleno\b|\ba pleno\b|pleno empleo|jornada|concierto|concert|pregón|preg[oó]", re.I))

# Spain: a committee covering education counts only when at least this many of its sessions are posted; otherwise the
# council's plenaries do (one stray committee clip shouldn't replace 160 plenaries).
MIN_EDU = {"ES": 3}


def session_key(cc, t):
    """A key for an undated title. Brazilian chambers often post one clip per speaker ("Fulano - Pequeno Expediente da
    85ª Sessão Ordinária"), so there the session's number and kind (and year, when given) identify the meeting."""
    if cc == "BR":
        m = re.search(r"(\d+)\s*[ªºa°o]?\.?\s*sess[ãa]o\s+(ordin|extra|solen|espec)", t, re.I)
        if m:
            y = re.search(r"\b(20\d\d)\b", t)
            return f"{m.group(1)} {m.group(2).lower()} {y.group(1) if y else ''}"
    return re.sub(r"\b(parte|part)\s*\d+\b|\(\d\)|\d/\d", "", t, flags=re.I).strip().lower()


def meetings(cc, did):
    d = os.path.join(IN, DIRS[cc], "youtube")
    files = sorted(f for f in os.listdir(d) if re.fullmatch(rf"{cc}(_\d+)?_youtube\.csv", f)) if os.path.isdir(d) else []   # one file, or one per shard
    if not files: return 0, "", [], ""
    if cc not in _CACHE:
        titles = {}
        for f in sorted(os.listdir(d)):
            if re.fullmatch(r"titles(_\d+)?\.json", f): titles.update(json.load(open(os.path.join(d, f), encoding="utf-8")))
        titles.update(shared_titles())
        _CACHE[cc] = ({r["District ID"]: r for f in files for r in csv.DictReader(open(os.path.join(d, f), encoding="utf-8"))}, titles)
    rows, titles = _CACHE[cc]
    r = rows.get(did) or {}
    url = CHECKED[cc].get(did, "") if cc in CHECKED else r.get("Channel URL", "")
    if not url or url not in titles or url in NOT_CHANNELS.get(cc, set()): return 0, "", [], ""
    edu, council, must, not_t = RULES.get(cc, (EDU, COUNCIL, COUNCIL_MUST, NOT_T))
    vids = [t for t in titles[url] if not not_t.search(t)]
    for keep, kind in (([t for t in vids if edu.search(t)], "Education committee"),
                       ([t for t in vids if council.search(t) and must.search(t) and not edu.search(t)], "Council (stand-in)")):
        keys = {parse_date(t) or session_key(cc, t) for t in keep}
        if len(keys) >= (MIN_EDU.get(cc, 1) if kind == "Education committee" else 1): return len(keys), url, keep, kind
    return 0, "", [], ""


# Channels checked by hand and found to be another place's (by channel URL). The search matched on the name, and
# many of these names exist in other Spanish-speaking countries too, or in both Chile and Colombia.
NOT_CHANNELS = {
    "MX": {"https://www.youtube.com/channel/UCJ_QgHV7jNH5PWK-hD3ZigA",    # Santa Ana, Costa Rica ("Gobierno Local"), not Oaxaca's
           "https://www.youtube.com/channel/UC_NzgVf7xT5SWA3dsBUOh6g",    # Coyotepec, Estado de México (2019-2021 term), not Puebla's
           "https://www.youtube.com/channel/UC-RQwxdFz9c8an1SthCk27A",    # Tamazula de Gordiano, Jalisco, not Tamazula, Durango
           "https://www.youtube.com/channel/UCfm4ANhQp5dTff6rmh7RJzQ",    # Santa Cruz de La Palma (Spain), not Santa Cruz, Sonora
           "https://www.youtube.com/channel/UCKoEOfBTuO570QHJ_2NpdCw",    # Esperanza, Santa Fe (Argentina), not Puebla's
           "https://www.youtube.com/channel/UCK-_PQD2Ey6dvQmphdsqlzg",    # Atizapán de Zaragoza's council, not Atizapán's
           "https://www.youtube.com/channel/UC2DrRwc-AyOPhOUjizUFJMA",    # election boards, not town councils: Actopan (Veracruz),
           "https://www.youtube.com/channel/UC9rp_w5KZKax5MOoDDxKDAw",    # Chiconcuac
           "https://www.youtube.com/channel/UCn1zNwM4qlnZL01gFzbwgDw"},   # and Villa Victoria
    "BR": {"https://www.youtube.com/channel/UCwL8TsjsmqixFQKK4fIdU1g"},   # Aveiro, Portugal (Assembleia Municipal), not Pará's
    "CL": {"https://www.youtube.com/channel/UC70nQc3caJyhIQQHlwBb_RA",    # La Molina, Lima (Peru), not Molina
           "https://www.youtube.com/channel/UCgvUIPWaySeDAGe-oUTSDUA",    # La Unión, Costa Rica ("Concejo de Distrito")
           "https://www.youtube.com/channel/UCQgCHXXxl4IyPg0GEULz2RA",    # San Carlos, Costa Rica
           "https://www.youtube.com/channel/UC3rWA_wd9eyOA1T0WuMTZQg",    # San Ramón, Costa Rica (regidores, cantonal)
           "https://www.youtube.com/channel/UCZXpwy8DfsnN1x61GBQB0ZA",    # Santa Cruz, Bolivia
           "https://www.youtube.com/channel/UCdjGfVXeZ7nu1QYlS49q91g",    # El Retiro, Antioquia (Colombia's Retiro)
           "https://www.youtube.com/channel/UCe1pVTpAU89txiLiGPFe3YA"},   # La Calera, Cundinamarca (Colombia's)
    "CO": {"https://www.youtube.com/channel/UCj983fAuispRHiUb9KfZH0Q",    # Santa Lucía, Corrientes (Argentina)
           "https://www.youtube.com/channel/UCzxvBsAVswjwc6dRN4uglWA",    # a Colón with "Sesión de Cabildo" (Mexico/Panama)
           "https://www.youtube.com/channel/UClJErJ8eEEUQ6cIJOfn1TFw",    # La Chorrera, Panama
           "https://www.youtube.com/channel/UCkV-Fcci5WXRTNKk3EI43cg",    # San Marcos, El Salvador
           "https://www.youtube.com/channel/UChP0E7AeiBDBKFRrYBhrEgw",    # San Cristóbal, Táchira (Venezuela)
           "https://www.youtube.com/channel/UCZaI4dep0kp5vZa3gCsEwLQ",    # Santo Domingo, Chile ("I.M.")
           "https://www.youtube.com/channel/UCK7OgXBRvGeUy0op536HsNg",    # Villarrica, Chile ("Cuenta Pública")
           "https://www.youtube.com/channel/UC3rOsD5LY68opkbDQnSjA7A",    # Santiago, Chile's capital
           "https://www.youtube.com/channel/UC3t9uauFej-XiU3VoNWKB-A"},   # Santiago, Dominican Republic (Ayuntamiento)
}

# Peru: most of what the search found are councils in Chile, Costa Rica, Argentina and Colombia with the same
# names, so there only channels checked by hand as Peruvian count, for the district given (by district ID).
_PE = "https://www.youtube.com/channel/"
CHECKED = {"PE": {k: _PE + v for k, v in {
    "PE-150101": "UCJ3f5r4cWt0aB_wRZPSejWQ", "PE-080101": "UCF9ojHlJloZwKDOzA5GrxFw", "PE-140101": "UCN4jLG_fhtebv1JQ9DWgzxQ",
    "PE-040701": "UCIQQUl10eKVVSgwJI8jluIg", "PE-150111": "UCW2rXxUyC1IeRK4GRBRPY7A", "PE-150113": "UCjABI3bxBiscyimOSuzLzhA",
    "PE-150115": "UCLifOhcJ6XAaF0GU2T6VARg", "PE-150121": "UCMdFUMIO9LIHpLbDmVxXEIA", "PE-150129": "UCKVQ8NsWNtZIdP9ZF4IVZ6w",
    "PE-150131": "UCn2gaVv77AER_KNaJGZ28RQ", "PE-150135": "UCKkBxaHbSsY8IEsGsd8HXtw", "PE-150143": "UC8TDnlG1GaYFMmxeXNnFi_Q",
    "PE-150701": "UCrenDH8TgyAz2jiuy_PdJ0A", "PE-150801": "UCqgZKEyw08kgfRDxNOaYQpA", "PE-150122": "UC8FiOrR4JKMX1gbFTcCqlqA",
    "PE-170101": "UCn8fgzTt7vyGxx7XJjxthiw", "PE-200101": "UCVdp_iUn0qDLlSppUMNCmUA", "PE-200401": "UC9OicPMGlOBEXqGAoH7S0SA",
    "PE-021201": "UCWVJkvnKmur8dg786wJJ70w",   # Huaylas province, whose capital is Caraz
    "PE-021809": "UCil_Yf91yaQaMDVVAhcCz0g", "PE-050401": "UC23J1HNLtE_1_9faXqs4JCQ", "PE-070105": "UCfPiN3_pIi8YNAKk0EWdEUg",
    "PE-080914": "UCWaGrJ3wuoM-BIdWIgHdAlQ", "PE-130107": "UCvetP1TUv-tFpImEjYPKG1g", "PE-130208": "UCf8-pfi_bQoFtQj98CGTArw",
    "PE-150104": "UC9YnoLRTJW74orZDh-UOhFQ", "PE-150106": "UCpg-im9SD9DTIn84XTe6fgg", "PE-150110": "UCK-IYgrmoXvBZKCqhK98bBw",
    "PE-150114": "UC70nQc3caJyhIQQHlwBb_RA", "PE-150116": "UCQQL72xP2L6lkFtEO9wkhkw", "PE-150128": "UCPHXgqgMGHiHF-jjgvExELg",
    "PE-150130": "UC4zMDhTiNWkVZ8q8zcoITuw", "PE-150140": "UC-AkDvXd88-mhcirAdr4JRg", "PE-150142": "UCRs70NeKnDQvTZqTjzAg0JQ",
    "PE-170102": "UCHlJ6WzNpVWg_KaF7aguEng", "PE-220201": "UCTjCeb9ggDIlwLxWzR1rS-g", "PE-250105": "UCGiUuor7J9yFe8J9p4aNY3Q",
    "PE-250107": "UC-oSE57lL79rK3aepmY5bpw", "PE-250202": "UCH7p0VMERLz61DF3qglwmGg", "PE-050115": "UC9Xe1vm8VStutAoJUBJqpmQ",
    "PE-110107": "UCI2tQgwzoXnRCILyieLJuFg", "PE-080108": "UCZltJAIVktGErXGt5HsVpsw", "PE-070106": "UC5388UeYO6oj4JXq4HHFeuw",
    "PE-040101": "UC44tK57rCBV2scQtcTs87Jg", "PE-150117": "UC_yuEQsrS22GNLqT7R0xlGg", "PE-150120": "UCEGsSBdm3eOa8cjrVrEBwxw",
    "PE-150124": "UCObrdr2CkkwbTnAdnr-Ruaw", "PE-150141": "UCN8I6t7LjFnrSD5dIgvCEDw", "PE-070104": "UCe53Z9uqvbc51ssQ3R27Y_Q",
    "PE-080104": "UChAF18cDdXeN3vbIrKc1VeQ", "PE-080106": "UCKYFe4ppuLoPv39yGWgoI_A", "PE-120601": "UC2WBf-K3u8jsLfprLePFh1g",
    "PE-060601": "UCcmZgayO2jPPu6_lrzXWozw", "PE-060801": "UCSqamMwpS4xdDMsZdj8b6QQ", "PE-010201": "UCGcKt1ovycMtsjdjS-C4rxQ",
    "PE-021101": "UCGwdDewNh0gGIPHc5Sa1XKg", "PE-080401": "UC5M9-m2D_7aDca4tDUrhhOA", "PE-080909": "UCqNq2lecGmASUVTDmASeH6w",
    "PE-081304": "UCDWro981gzoQK5jCQ_2vZ0Q", "PE-080408": "UC_0O2U4ZAciJH8RTVxOC3kA", "PE-230101": "UCZUeshy-Ud8IoVczaZ9--6w",
    "PE-230302": "UC0adRZGi3WxiiC90oI0LtKw", "PE-230102": "UCJbL9DCPxUWwtWG2t2SZI0Q", "PE-070103": "UCEgNm3Xfil0I_KKFZshSvrg",
    "PE-100102": "UC8uANJ7Nvq5BoPzzlwl--cg", "PE-110106": "UCGoE7OI_OeSJFjEi8W-IyIw", "PE-110113": "UCoJvYlcpRqgTSjp0Ezz5KnA",
    "PE-140201": "UCPwi3vEslpVHjLBUqoXMSnw", "PE-150201": "UCF1bNMCs61IWDnlmbiK3AbQ", "PE-190202": "UCH89lak3ghSiNpbk2gqKb4A",
    "PE-050404": "UCSZGko_PnCjJ5eJdMrGS0Ig", "PE-051101": "UCRi0Aa6053U1MDx1o8YuvJg", "PE-022001": "UCL-VQ_WuOhUUbc0UjK-i6Tw"}.items()}}


FOREIGN = re.compile(r"deliberante|distrital de carmen alto|municipalidad distrital|provincial", re.I)   # Argentina's and Peru's councils


def owners(cc, rows):
    """Which district each channel belongs to. Many places share a name (Colombia has three Granadas and four
    Villanuevas), so the search found the same channel for several. A channel counts for one district only:
    the one whose longer full name, or whose department, the channel name gives; if none does, for none.
    A channel naming a different department is dropped."""
    if cc not in _CACHE: return {}
    yt = _CACHE[cc][0]
    words = lambda s: " " + re.sub(r"[^a-z]+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()) + " "
    regions = {words(r["Region"]).strip() for r in rows if r.get("Region")}
    names = {words(x).strip() for r in rows for x in r.get("_names") or [r["District"]]}
    by = {}
    for r in rows:
        y = yt.get(r["District ID"]) or {}
        if y.get("Channel URL"): by.setdefault(y["Channel URL"], []).append(r)
    own = {}
    for url, rs in by.items():
        raw = (yt.get(rs[0]["District ID"]) or {}).get("Channel", "")
        ch = words(raw)
        if FOREIGN.search(ch): continue
        # Brazilian channel names often end with the state's abbreviation ("Rio Negro - PR", "Belém PB", "(SC)").
        abbr = {a for a in re.findall(r"(?:[-/(–]\s*|\s)([A-Z]{2})\b\)?\s*$", raw.strip())} if cc == "BR" else set()
        def score(r):
            alts = [words(x).strip() for x in r.get("_names") or [r["District"]]]   # Spain: "Alacant / Alicante"
            nm = next((a for a in alts if " " + a + " " in ch), "")
            if not nm: return -1
            if any(len(o) > len(nm) and " " + nm + " " in " " + o + " " and " " + o + " " in ch for o in names): return -1   # "Alfredo Chaves", not Chaves
            other = any(" " + g + " " in ch for g in regions - {words(r["Region"]).strip()} if " " + g + " " not in " " + nm + " ")
            named = " " + words(r["Region"]).strip() + " " in ch or (cc == "CO" and words(r["Region"]).split()[0] in ch.split())
            if abbr:
                own_abbr = next((a for a, c in BR_ABBR.items() if BR_UF[c] == r["Region"]), "")
                named, other = named or own_abbr in abbr, other or bool(abbr - {own_abbr})
            return -1 if other and not named else len(nm) + (100 if named else 0)
        sc = sorted(((score(r), r["District ID"]) for r in rs), reverse=True)
        if sc[0][0] < 0: continue
        if len(sc) > 1 and sc[0][0] == sc[1][0]: continue
        own[url] = sc[0][1]
    return own


def write(cc, key, rows, feats):
    meetings(cc, "")
    own = owners(cc, rows)
    for r in rows:
        n, url, keep, kind = meetings(cc, r["District ID"])
        if url and cc not in CHECKED and own.get(url) != r["District ID"]: n, url, keep, kind = 0, "", [], ""
        latest, years = date_summary(keep) if n else ("", "")
        r.update({"Available Board Meetings": n, "Meetings type": kind, "Meetings source": url, "Latest meeting": latest, "Meetings by year": years})
    cols = ["District", "Region", "Locale", "Available Board Meetings", "Meetings type", "Meetings source", "Latest meeting", "Meetings by year",
            "Population", "Percentage of Children in Low Income", "Poverty rate (all ages)", "Multidimensional poverty (all ages)", "Poverty note", "Enrollment", "Enrollment year",
            "Public school enrollment", "School system", "People per km² (estimated)", "District ID"]
    extra = [c for c in ("Province", "Autonomous community", "Children under 18 (estimated)", "Poverty year", "Poverty range", "Extreme poverty (all ages)", "Poverty by year", "Children 6–17", "Bolsa Família families per 100 households", "Bolsa Família families", "Households") if any(r.get(c) not in (None, "") for r in rows)]
    pov = "Percentage of Children in Low Income" if any(r.get("Percentage of Children in Low Income") for r in rows) else "Poverty rate (all ages)"
    cols = [c for c in cols if c not in ("Percentage of Children in Low Income", "Poverty rate (all ages)", "Multidimensional poverty (all ages)") or any(r.get(c) not in (None, "") for r in rows)]
    cols = cols[:cols.index("Poverty note") + 1] + [c for c in extra if c != "Children 6–17"] + cols[cols.index("Poverty note") + 1:-1] + [c for c in extra if c == "Children 6–17"] + cols[-1:]
    for c in ("Autonomous community", "Province"):
        if c in cols: cols.remove(c); cols.insert(cols.index("Region") + 1, c)
    rows.sort(key=lambda r: r["District"])
    with open(os.path.join(DOCS, f"{key}.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=cols, restval="", extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", f"{key}.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(cc, len(rows), "rows; poverty", sum(1 for r in rows if r.get(pov)), "; enrollment", sum(1 for r in rows if r.get("Enrollment")),
          "; meetings", sum(1 for r in rows if r["Available Board Meetings"]), "; no border", [r["District"] for r in rows if not r.get("_geo")][:10])


def loc(d):
    return "Urban" if d >= 2000 else "Suburban" if d >= 500 else "Mixed" if d >= 100 else "Rural"


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def chile():
    sheet = lambda f: [r for r in openpyxl.load_workbook(os.path.join(IN, "chile", f), read_only=True).worksheets[0].iter_rows(values_only=True)
                       if r and isinstance(r[0], (int, float))]
    inc = {str(int(r[0])).zfill(5): r for r in sheet("sae_ingresos_2024.xlsx")}
    mul = {str(int(r[0])).zfill(5): r for r in sheet("sae_multidimensional_2024.xlsx")}
    enr = json.load(open(os.path.join(IN, "chile", "enrolment_by_comuna_2026.json")))
    geo = json.load(open(os.path.join(IN, "chile", "gb_CHL_ADM3.geojson"), encoding="utf-8"))
    by_name = {}
    for f in geo["features"]:
        n = norm(f["properties"]["shapeName"]); by_name[ALIAS["CL"].get(n, n)] = f
    rows, feats = [], []
    for code, r in inc.items():
        e = enr.get(str(int(code))) or enr.get(code) or {}
        dep = e.get("by_dependency", {})
        public = sum(v for k, v in dep.items() if k in ("1", "2", "5", "6"))   # COD_DEPE: 1-2 municipal, 5 delegated, 6 SLEP
        slep = dep.get("6", 0); muni = dep.get("1", 0) + dep.get("2", 0)
        f = by_name.get(ALIAS["CL"].get(norm(r[2]), norm(r[2])))
        area = area_km2(f["geometry"]) if f else 0
        did = f"CL-{code}"
        row = {"District": r[2], "Region": r[1], "Population": int(r[3]), "Poverty rate (all ages)": f"{100 * r[5]:.2f}%",
               "Multidimensional poverty (all ages)": f"{100 * mul[code][5]:.2f}%" if code in mul else "",
               "Poverty note": f"All ages, 2024 small-area estimate ({r[9]}); no child rate is published by comuna",
               "Enrollment": e.get("total", ""), "Enrollment year": "2026" if e else "", "Public school enrollment": public or "",
               "School system": "Local Public Education Service (SLEP)" if slep > muni else "Municipality (DAEM or corporation)" if muni else "",
               "Locale": loc(int(r[3]) / area) if area else "", "People per km² (estimated)": round(int(r[3]) / area) if area else "",
               "District ID": did, "_geo": bool(f)}
        rows.append(row)
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": r[2]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("CL", "chile", rows, feats)


def colombia():
    ws = openpyxl.load_workbook(os.path.join(IN, "colombia", "ipm_municipal_2018.xlsx"), read_only=True)["2_IPM Mpio y Dpt"]
    ipm = {str(r[0]): r for r in ws.iter_rows(values_only=True) if r and r[0] and len(str(r[0])) == 5 and str(r[0]).isdigit()}
    men = {r["c_digo_municipio"].zfill(5): r for r in json.load(open(os.path.join(IN, "colombia", "men_estadisticas_municipio_2024.json"), encoding="utf-8"))}
    dept_name = {r["c_digo_departamento"].zfill(2): r["departamento"] for r in men.values()}
    adm1 = json.load(open(os.path.join(IN, "colombia", "gb_COL_ADM1.geojson"), encoding="utf-8"))["features"]
    dcode = {}
    for f in adm1:
        n = norm(f["properties"]["shapeName"])
        code = next((c for c, nm in dept_name.items() if norm(nm) == n or norm(nm)[:8] == n[:8] or (c == "11" and "bogota" in n)), None)
        dcode[id(f)] = code
    geo = json.load(open(os.path.join(IN, "colombia", "gb_COL_ADM2.geojson"), encoding="utf-8"))
    keyed = {}
    for f in geo["features"]:
        c = centroid(f["geometry"])
        d = next((dcode[id(a)] for a in adm1 if pip(c, a["geometry"])), None)
        n = norm(f["properties"]["shapeName"]); n = ALIAS["CO"].get(n, n)
        keyed.setdefault((d, n), f)
    rows, feats = [], []
    # Exact matches (department and name) first, so a fuzzy match never takes another municipality's border.
    exact = {code: keyed.get((code[:2], ALIAS["CO"].get(norm(r[1]), norm(r[1])))) for code, r in ipm.items()}
    used = {id(f) for f in exact.values() if f}
    for code, r in ipm.items():
        m = men.get(code, {})
        nm = str(r[1]).title().replace(" De ", " de ").replace(" Del ", " del ").replace(" La ", " la ").replace(" El ", " el ")
        n = norm(r[1]); n = ALIAS["CO"].get(n, n)
        f = exact[code] or next((g for (d, k), g in keyed.items() if id(g) not in used and d == code[:2] and (k.startswith(n) or n.startswith(k)) and min(len(k), len(n)) >= 5), None)
        if not f:   # a border near a coast or department edge can fall outside its simplified department: use the name if it's unique
            same = [g for (d, k), g in keyed.items() if k == n and id(g) not in used]
            f = same[0] if len(same) == 1 else None
        if f and not exact[code]: used.add(id(f))
        pop = float(m.get("poblaci_n_5_16") or 0); rate = float(m.get("tasa_matriculaci_n_5_16") or 0)
        area = area_km2(f["geometry"]) if f else 0
        dens = pop / 0.19 / area if area and pop else 0
        did = f"CO-{code}"
        rows.append({"District": nm, "Region": dept_name.get(code[:2], ""), "Poverty rate (all ages)": f"{float(r[2]):.2f}%" if isinstance(r[2], (int, float)) else "",
                     "Poverty note": "Multidimensional poverty, all ages, 2018 census (DANE); no child or income rate is published by municipality",
                     "Enrollment": round(pop * rate / 100) if pop and rate else "", "Enrollment year": "2024 (estimated: children 5–16 × net enrollment rate)" if pop and rate else "",
                     "School system": m.get("etc", ""), "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "",
                     "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": nm}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("CO", "colombia", rows, feats)


def adm_match(cc, rows, adm2, adm1, state_of_adm1):
    """Borders for rows ({"name", "state", "id"}): exact (state, name) first, then a prefix match within the
    state, then a name unique in the country; a border is never used twice. Returns {id: feature}."""
    full = lambda s: re.sub(r"\bDr\.\s*", "Doctor ", re.sub(r"\bGral\.\s*", "General ", str(s)))   # Nuevo León's abbreviations
    keyed, dup = {}, []
    for f in adm2:
        c = centroid(f["geometry"])
        st = next((state_of_adm1[id(a)] for a in adm1 if pip(c, a["geometry"])), None)
        n = norm(full(f["properties"]["shapeName"])); n = ALIAS.get(cc, {}).get(n, n)
        if (st, n) in keyed: dup.append((n, f))   # e.g. a border whose centre falls just over a state line
        else: keyed[(st, n)] = f
    key = lambda r: ALIAS.get(cc, {}).get(norm(full(r["name"])), norm(full(r["name"])))
    bare = lambda k: re.sub(r"^(el|la|los|las|o|a|os|as)(?=[a-z]{4})", "", k)   # "El Carmen" / "Carmen"
    out = {r["id"]: keyed.get((r["state"], key(r))) for r in rows}
    used = {id(f) for f in out.values() if f}
    for r in rows:
        if out[r["id"]]: continue
        n = key(r)
        f = next((g for (d, k), g in keyed.items() if id(g) not in used and d == r["state"] and (k.startswith(n) or n.startswith(k)) and min(len(k), len(n)) >= 5), None)
        f = f or next((g for (d, k), g in keyed.items() if id(g) not in used and d == r["state"] and (bare(k) == bare(n) or (len(n) >= 12 and n in k))), None)
        if not f:
            same = [g for (d, k), g in keyed.items() if k == n and id(g) not in used] + [g for k, g in dup if k == n and id(g) not in used]
            f = same[0] if len(same) == 1 else None
        if f: used.add(id(f)); out[r["id"]] = f
    return out


MX_ISO = {"AGU": "01", "BCN": "02", "BCS": "03", "CAM": "04", "COA": "05", "COL": "06", "CHP": "07", "CHH": "08", "CMX": "09", "DIF": "09", "DUR": "10",
          "GUA": "11", "GRO": "12", "HID": "13", "JAL": "14", "MEX": "15", "MIC": "16", "MOR": "17", "NAY": "18", "NLE": "19", "OAX": "20", "PUE": "21",
          "QUE": "22", "ROO": "23", "SLP": "24", "SIN": "25", "SON": "26", "TAB": "27", "TAM": "28", "TLA": "29", "VER": "30", "YUC": "31", "ZAC": "32"}
MX_STATE = {"México": "Estado de México", "Coahuila de Zaragoza": "Coahuila", "Michoacán de Ocampo": "Michoacán", "Veracruz de Ignacio de la Llave": "Veracruz"}


def mexico():
    """2,469 municipalities. Schools are run by each state's education authority (the federal SEP pays for most
    basic education), not by municipalities; town councils (cabildos) stand in for meetings."""
    ws = openpyxl.load_workbook(os.path.join(IN, "mexico", "coneval_pobreza_municipal_2020.xlsx"), read_only=True)["Concentrado municipal"]
    con = {str(r[3]): r for r in ws.iter_rows(values_only=True) if r and r[3] and re.fullmatch(r"\d{5}", str(r[3]))}
    num = lambda v: int(v) if str(v).strip().isdigit() else None
    it = {}
    for r in csv.DictReader(open(os.path.join(IN, "mexico", "inegi_iter_2020_municipal.csv"), encoding="utf-8")):
        it[r["ENTIDAD"] + r["MUN"]] = r
    adm1 = json.load(open(os.path.join(IN, "mexico", "gb_MEX_ADM1.geojson"), encoding="utf-8"))["features"]
    st = {id(f): MX_ISO.get(f["properties"]["shapeISO"].split("-")[-1]) for f in adm1}
    adm2 = json.load(open(os.path.join(IN, "mexico", "gb_MEX_ADM2.geojson"), encoding="utf-8"))["features"]
    geo = adm_match("MX", [{"name": r[4], "state": c[:2], "id": c} for c, r in con.items()], adm2, adm1, st)
    rows, feats = [], []
    for code, r in con.items():
        i = it.get(code, {})
        a, b, c6, d, e = (num(i.get(k)) for k in ("P_6A11", "P6A11_NOA", "P_12A14", "P12A14NOA", "P15A17A"))
        enr = (a - b) + (c6 - d) + e if None not in (a, b, c6, d, e) else ""
        kids = sum(x for x in (num(i.get("P_6A11")), num(i.get("P_12A14")), num(i.get("P_15A17"))) if x) or ""
        pop = num(i.get("POBTOT")) or (int(r[7]) if r[7] else 0)
        f = geo.get(code); area = area_km2(f["geometry"]) if f else 0
        dens = pop / area if area and pop else 0
        pct = lambda v: f"{float(v):.2f}%" if isinstance(v, (int, float)) else ""
        did = f"MX-{code}"
        rows.append({"District": str(r[4]), "Region": MX_STATE.get(str(r[2]), str(r[2])), "Population": pop,
                     "Poverty rate (all ages)": pct(r[10]), "Extreme poverty (all ages)": pct(r[19]),
                     "Poverty by year": "; ".join(f"{y}:{float(v):.1f}" for y, v in zip((2010, 2015, 2020), r[8:11]) if isinstance(v, (int, float))),
                     "Poverty note": "Multidimensional poverty (income below the poverty line and at least one social deprivation), all ages, 2020 (CONEVAL); no child rate is published by municipality",
                     "Enrollment": enr, "Enrollment year": "2020 (estimated: census count of children 6–17 attending school)" if enr != "" else "",
                     "Children 6–17": kids, "School system": "State education authority",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": str(r[4])}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("MX", "mexico", rows, feats)


BR_UF = {"11": "Rondônia", "12": "Acre", "13": "Amazonas", "14": "Roraima", "15": "Pará", "16": "Amapá", "17": "Tocantins",
         "21": "Maranhão", "22": "Piauí", "23": "Ceará", "24": "Rio Grande do Norte", "25": "Paraíba", "26": "Pernambuco",
         "27": "Alagoas", "28": "Sergipe", "29": "Bahia", "31": "Minas Gerais", "32": "Espírito Santo", "33": "Rio de Janeiro",
         "35": "São Paulo", "41": "Paraná", "42": "Santa Catarina", "43": "Rio Grande do Sul", "50": "Mato Grosso do Sul",
         "51": "Mato Grosso", "52": "Goiás", "53": "Distrito Federal"}
BR_ABBR = {"RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17", "MA": "21", "PI": "22", "CE": "23",
           "RN": "24", "PB": "25", "PE": "26", "AL": "27", "SE": "28", "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35",
           "PR": "41", "SC": "42", "RS": "43", "MS": "50", "MT": "51", "GO": "52", "DF": "53"}


def brazil():
    """5,570 municipalities. Municipalities run most early-years schools (the rede municipal, under a municipal
    education secretariat and council); the municipal chamber (câmara municipal) stands in for meetings."""
    import xlrd
    d = os.path.join(IN, "brazil")
    sh = xlrd.open_workbook(os.path.join(d, "ibge_estimativa_populacao_2025.xls")).sheet_by_name("Municípios")
    pop = {}
    for i in range(2, sh.nrows):
        v = sh.row_values(i)
        uf, mun = str(v[1]).replace(".0", "").strip(), str(v[2]).replace(".0", "").strip()
        if uf.isdigit() and mun.isdigit():
            n = v[4] if isinstance(v[4], float) else re.sub(r"\(.*?\)|\D", "", str(v[4]).split("(")[0])
            pop[f"{int(uf):02d}{int(mun):05d}"] = (str(v[3]).strip(), int(n) if n not in ("", None) else None)
    siafi = {r[0].strip(): r[4].strip() for r in csv.reader(open(os.path.join(d, "tesouro_tabmun_siafi_ibge.csv"), encoding="latin-1"), delimiter=";") if len(r) > 4}
    fam = {}
    for r in csv.DictReader(open(os.path.join(d, "bolsa_familia_familias_202509.csv"), encoding="utf-8")):
        c = siafi.get(r["siafi"].strip())
        if c: fam[c] = fam.get(c, 0) + int(float(r["familias"]))
    extra = {}   # census tables saved from SIDRA: {ibge7: {column: value}}
    for f in sorted(os.listdir(d)):
        if f.startswith("br_") and f.endswith(".csv"):
            for r in csv.DictReader(open(os.path.join(d, f), encoding="utf-8")):
                extra.setdefault(r["ibge7"], {}).update({k: v for k, v in r.items() if k != "ibge7"})
    adm1 = json.load(open(os.path.join(d, "gb_BRA_ADM1.geojson"), encoding="utf-8"))["features"]
    st = {id(f): BR_ABBR.get(f["properties"]["shapeISO"].split("-")[-1]) for f in adm1}
    adm2 = json.load(open(os.path.join(d, "gb_BRA_ADM2.geojson"), encoding="utf-8"))["features"]
    geo = adm_match("BR", [{"name": n, "state": c[:2], "id": c} for c, (n, _) in pop.items()], adm2, adm1, st)
    rows, feats = [], []
    for code, (name, people) in sorted(pop.items()):
        x = extra.get(code, {}); hh = int(x["Households"]) if x.get("Households", "").isdigit() else None
        n = lambda k: int(x[k]) if x.get(k, "").isdigit() else None
        res, q, h, z = n("Residents"), n("Up to 1/4 minimum wage per person"), n("Over 1/4 to 1/2 minimum wage per person"), n("No income")
        poor = f"{100 * (q + h + z) / res:.2f}%" if res and None not in (q, h, z) else ""
        extreme = f"{100 * (q + z) / res:.2f}%" if res and None not in (q, z) else ""
        f = geo.get(code); area = area_km2(f["geometry"]) if f else 0
        dens = people / area if area and people else 0
        did = f"BR-{code}"
        rows.append({"District": name, "Region": BR_UF[code[:2]], "Population": people or "",
                     "Poverty rate (all ages)": poor, "Extreme poverty (all ages)": extreme,
                     "Poverty note": "Residents of households with income up to half the minimum wage per person (R$606 a month in 2022), all ages, 2022 census; extreme: up to a quarter; both include households with no income",
                     "Bolsa Família families per 100 households": f"{100 * fam[code] / hh:.2f}" if hh and code in fam else "",
                     "Bolsa Família families": fam.get(code, ""), "Households": hh or "",
                     "Enrollment": x.get("Enrollment", ""), "Enrollment year": x.get("Enrollment year", ""),
                     "Children 6–17": x.get("Children 6–17", ""), "School system": "Municipal and state school networks",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("BR", "brazil", rows, feats)


PE_DEPT = {"01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho", "06": "Cajamarca", "07": "Callao",
           "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque",
           "15": "Lima", "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura", "21": "Puno",
           "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali"}


# Spain's provinces by INE code (the first two digits of a municipality's code).
ES_PROV = {"01": "Álava", "02": "Albacete", "03": "Alicante", "04": "Almería", "05": "Ávila", "06": "Badajoz", "07": "Illes Balears",
           "08": "Barcelona", "09": "Burgos", "10": "Cáceres", "11": "Cádiz", "12": "Castellón", "13": "Ciudad Real", "14": "Córdoba",
           "15": "A Coruña", "16": "Cuenca", "17": "Girona", "18": "Granada", "19": "Guadalajara", "20": "Gipuzkoa", "21": "Huelva",
           "22": "Huesca", "23": "Jaén", "24": "León", "25": "Lleida", "26": "La Rioja", "27": "Lugo", "28": "Madrid", "29": "Málaga",
           "30": "Murcia", "31": "Navarra", "32": "Ourense", "33": "Asturias", "34": "Palencia", "35": "Las Palmas", "36": "Pontevedra",
           "37": "Salamanca", "38": "Santa Cruz de Tenerife", "39": "Cantabria", "40": "Segovia", "41": "Sevilla", "42": "Soria",
           "43": "Tarragona", "44": "Teruel", "45": "Toledo", "46": "Valencia", "47": "Valladolid", "48": "Bizkaia", "49": "Zamora",
           "50": "Zaragoza", "51": "Ceuta", "52": "Melilla"}
ES_CCAA = {"Andalucía": "04 11 14 18 21 23 29 41", "Aragón": "22 44 50", "Asturias": "33", "Illes Balears": "07", "Canarias": "35 38",
           "Cantabria": "39", "Castilla y León": "05 09 24 34 37 40 42 47 49", "Castilla-La Mancha": "02 13 16 19 45",
           "Cataluña": "08 17 25 43", "Comunitat Valenciana": "03 12 46", "Extremadura": "06 10", "Galicia": "15 27 32 36",
           "Madrid": "28", "Murcia": "30", "Navarra": "31", "País Vasco": "01 20 48", "La Rioja": "26", "Ceuta": "51", "Melilla": "52"}
ES_CCAA = {c: k for k, v in ES_CCAA.items() for c in v.split()}


def es_parts(n):
    """INE names put articles last and give co-official forms with a slash: 'Rozas de Madrid, Las' -> ['Las Rozas de Madrid'],
    'Poble Nou de Benitatxell, el/Benitachell' -> ['el Poble Nou de Benitatxell', 'Benitachell']."""
    out = []
    for x in n.split("/"):
        m = re.fullmatch(r"(.+?), (la|las|el|els|los|les|l'|o|os|a|as|lo|la|sa|ses|es|s')", x.strip(), re.I)
        out.append((m.group(2)[0].upper() + m.group(2)[1:] + ("" if m.group(2).endswith("'") else " ") + m.group(1)) if m else x.strip())
    return out


def es_title(s):
    """'SAN JUAN DE LOPECANCHA' -> 'San Juan de Lopecancha'."""
    small = {"de", "del", "la", "las", "los", "el", "y", "e", "en"}
    w = s.strip().lower().split()
    return " ".join(x if (i and x in small) else x[:1].upper() + x[1:] for i, x in enumerate(w))


def peru_poverty():
    """INEI, Mapa de pobreza monetaria provincial y distrital 2018, Anexo 1 (text of the PDF): per district its ubigeo,
    2018 population and the 95% confidence interval of the share of people in monetary poverty; and province names."""
    t = open(os.path.join(IN, "peru", "inei_mapa_pobreza_2018_anexo.txt"), encoding="utf-8").read()
    num = lambda x: float(x.replace(" ", "").replace(",", "."))
    dist = {}
    for m in re.finditer(r"^\s*(\d{6})\s+(\d{3})\s+(.+?)\s{2,}(\d{1,3}(?: \d{3})*)\s+(\d{1,3},\d)\s+(\d{1,3},\d)\s+(\d{1,3}(?: \d{3})?)\s*$", t, re.M):
        dist[m.group(1)] = {"name": es_title(m.group(3)), "pop": int(num(m.group(4))), "lo": num(m.group(5)), "hi": num(m.group(6)), "rank": int(num(m.group(7)))}
    prov = {}
    for m in re.finditer(r"^\s*(\d{4})00\s{2,}([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ .'-]+?)\s{2,}\d", t, re.M):
        prov.setdefault(m.group(1), es_title(m.group(2)))
    return dist, prov


def peru():
    """1,874 districts. Schools are run by the regional education directorates and their local units (UGEL), not by
    the districts; the district council (concejo municipal) stands in for meetings. INEI publishes district poverty
    only as a 95% confidence interval; the midpoint is shown."""
    dist, prov = peru_poverty()
    geo = {f["properties"]["IDDIST"]: f for f in json.load(open(os.path.join(IN, "peru", "peru_distrital_simple.geojson"), encoding="utf-8"))["features"] if f.get("geometry")}
    rows, feats = [], []
    for code, d in sorted(dist.items()):
        f = geo.get(code); area = area_km2(f["geometry"]) if f else 0
        dens = d["pop"] / area if area and d["pop"] else 0
        did = f"PE-{code}"
        rows.append({"District": d["name"], "Region": PE_DEPT[code[:2]], "Province": prov.get(code[:4], ""), "Population": d["pop"],
                     "Poverty rate (all ages)": f"{(d['lo'] + d['hi']) / 2:.2f}%", "Poverty range": f"{d['lo']:.1f}–{d['hi']:.1f}%",
                     "Poverty note": "Share of people below the monetary poverty line, all ages, 2018 (INEI poverty map): midpoint of the 95% confidence interval; no child rate is published by district",
                     "School system": "Regional education directorate (UGEL)",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": d["name"]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("PE", "peru", rows, feats)


def spain():
    """8,132 municipalities. Schools are run by each autonomous community's education department; municipalities
    look after primary school buildings. The town council's plenary session (pleno) stands in for meetings.
    Child poverty: INE's household income atlas (ADRH), people under 18 below 60% of the national median income
    per consumption unit; INE suppresses it for small municipalities."""
    d = os.path.join(IN, "spain")
    dem = json.load(open(os.path.join(d, "ine_adrh_demographics.json"), encoding="utf-8"))
    pov = json.load(open(os.path.join(d, "ine_adrh_under18_below60.json"), encoding="utf-8"))
    adm1 = json.load(open(os.path.join(d, "gb_ESP_ADM2.geojson"), encoding="utf-8"))["features"]
    pn = {norm(v): k for k, v in ES_PROV.items()}
    pn.update({"balearsilles": "07", "coruna": "15", "palmaslas": "35", "riojala": "26", "alava": "01"})
    st = {id(f): pn[norm(f["properties"]["shapeName"])] for f in adm1}
    adm3 = json.load(open(os.path.join(d, "gb_ESP_ADM3_simplified.geojson"), encoding="utf-8"))["features"]
    geo = {}
    # Names as INE writes them, then each form of a two-language name on either side ("Alacant/Alicante" in INE,
    # "Alicante/Alacant" in the borders file).
    for alt in range(4):
        todo = [c for c in dem if c not in geo]
        used = {id(f) for f in geo.values()}
        cand = []
        for f in adm3:
            if id(f) in used: continue
            ns = f["properties"]["shapeName"].split("/")
            for n in (ns if alt % 2 else [f["properties"]["shapeName"]]):
                cand.append({"properties": {"shapeName": n}, "geometry": f["geometry"], "_f": f})
        rows_ = [{"name": (es_parts(dem[c]["name"]) * 2)[alt // 2] if alt >= 2 else dem[c]["name"] if alt == 0 else es_parts(dem[c]["name"])[0], "state": c[:2], "id": c} for c in todo]
        got = adm_match("ES", rows_, cand, adm1, st)
        for k, v in got.items():
            if v and id(v["_f"]) not in {id(g) for g in geo.values()}: geo[k] = v["_f"]
    rows, feats = [], []
    for code, x in sorted(dem.items()):
        parts = es_parts(x["name"]); name = " / ".join(parts)
        people = int(x["pop"]) if x.get("pop") else 0
        kids = round(people * x["pct18"] / 100) if people and x.get("pct18") is not None else ""
        p = pov.get(code, {}); y = max(p) if p else ""
        f = geo.get(code); area = area_km2(f["geometry"]) if f else 0
        dens = people / area if area and people else 0
        did = f"ES-{code}"
        rows.append({"District": name, "_names": parts, "Region": ES_PROV[code[:2]], "Autonomous community": ES_CCAA[code[:2]], "Population": people or "",
                     "Percentage of Children in Low Income": f"{p[y]:.1f}%" if p else "", "Poverty year": y,
                     "Poverty by year": "; ".join(f"{k}:{v:.1f}" for k, v in sorted(p.items())),
                     "Poverty note": "People under 18 in households below 60% of the national median income per consumption unit (INE, household income atlas)" if p else "Not published for this municipality (INE leaves out small municipalities)",
                     "Children under 18 (estimated)": kids, "School system": f"{ES_CCAA[code[:2]]} education department",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("ES", "spain", rows, feats)


if __name__ == "__main__":
    which = sys.argv[1:] or ["chile", "colombia", "mexico", "brazil"]
    for w in which: globals()[w]()
