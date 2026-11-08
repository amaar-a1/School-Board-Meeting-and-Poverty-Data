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
from collections import Counter
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
         # Ecuador: the borders file's abbreviations and older names
         "EC": {"crnelmarcelinomariduena": "coronelmarcelinomariduena", "gnralantonioelizalde": "generalantonioelizaldebucay",
                "pablosexto": "pablovi", "salitre": "urbinajado"},
         # Colombia: the borders file's longer names for four municipalities
         "CO": {"distritoespecialindustrialyportuariodebarr": "barranquilla", "ricaurtecoloso": "coloso",
                "santanderararacuara": "puertosantander", "providenciasantaisabel": "providencia",
                "bogota": "bogotadc", "bogotadistritocapital": "bogotadc", "sanandres": "sanandres", "cartagena": "cartagenadeindias",
                "guadalajaradebuga": "buga", "santafedebogota": "bogotadc", "sanandresdetumaco": "tumaco", "sanjosedecucuta": "cucuta",
                "sanjosedetoluviejo": "toluviejo", "villadesandiegodeubate": "ubate", "tiquisio": "tiquiso", "papunahua": "papunauacordepartamental",
                "colosoricaurte": "coloso", "elsantuario": "santuario"},
         "MX": {"tlaquepaque": "sanpedrotlaquepaque"},
         # Spain: the borders file's older or other-language names
         "ES": {"maomahon": "mao", "castellplatjadaro": "castelldaroplatjadaroisagaro", "santcarlesdelarapita": "larapita",
                "alcocerdeplanes": "alcosser", "villanuevadecastellon": "castello",
                "aldehueladejerte": "aldehueladeljerte", "alfarp": "alfarb", "facheca": "fageca", "herbes": "herbers",
                "labisbaldefalset": "labisbaldemontsant", "santamariarivarredonda": "santamariaribarredonda", "goni": "valdegoni",
                "candin": "valledeancares"}}
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
DIRS = {"CL": "chile", "CO": "colombia", "MX": "mexico", "BR": "brazil", "PE": "peru", "ES": "spain", "FRA": "france", "EC": "ecuador", "IT": "italy", "PL": "poland", "JP": "japan", "PT": "portugal", "BE": "belgium"}
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

# France: the town council (conseil municipal) and its committee covering schools (commission des affaires
# scolaires / éducation / enfance). Children's and youth councils (conseil municipal des enfants / des jeunes),
# New Year greetings (vœux) and ceremonies aren't council meetings.
FR_NOT = re.compile(r"jeunes|enfants|\bcmj\b|\bcme\b|junior|interview|reportage|v[œo]eux|c[ée]r[ée]monie|inauguration|comm[ée]moration|bande.annonce|teaser|"
                    r"extrait|r[ée]sum[ée]|portrait|f[êe]te|concert|clip|spot|campagne|[ée]lection|candidat|replay des|d[ée]bat d.orientation citoyen", re.I)
RULES["FRA"] = (re.compile(r"^(?!.*(conseil municipal des|conseil d.[ée]cole)).*commission\b[^|]{0,60}(scolaire|[ée]ducation|enfance)", re.I),
                re.compile(r"conseil municipal|conseil communautaire|s[ée]ance", re.I),
                re.compile(r"^(?!.*(commission|communautaire|conseil des? (jeunes|enfants|sages|quartier))).*(conseil municipal|s[ée]ance (publique |ordinaire |extraordinaire )?du conseil)", re.I),
                FR_NOT)
# Ecuador: the cantonal council (concejo municipal / cantonal) of the GAD and its education committee; ceremonial
# and commemorative sessions (sesión solemne, conmemorativa) aren't counted.
RULES["EC"] = (re.compile(r"comisi[óo]n (permanente )?(de |del )?((cultura|deporte)s? y )?educaci[óo]n|educaci[óo]n.*comisi[óo]n", re.I),
               re.compile(r"sesi[óo]n", re.I),
               re.compile(r"^(?!.*(solemne|conmemorativa|comisi[óo]n)).*(sesi[óo]n (ordinaria|extraordinaria|de concejo|del concejo|del (i\. |ilustre )?concejo)|"
                          r"(ordinaria|extraordinaria) (de|del) concejo|concejo (municipal|cantonal)[^|]{0,30}sesi[óo]n)", re.I),
               re.compile(NOT_T.pattern + r"|solemne|conmemorativa|parroquial|provincial|junta|consejo cantonal de protecci", re.I))

# Italy: the town council (consiglio comunale) and its education committee (commissione istruzione / scuola);
# children's and youth councils (consiglio comunale dei ragazzi) and ceremonies aren't counted.
RULES["IT"] = (re.compile(r"commission[ei][^|]{0,50}(istruzione|scuol|scolastic|educazion|servizi educativi)", re.I),
               re.compile(r"consiglio comunale|seduta|sessione", re.I),
               re.compile(r"^(?!.*(commission|ragazzi|giovani|bambini|junior)).*(consiglio comunale|seduta (del |di )?consiglio|seduta consiliare|consiglio comunale)", re.I),
               re.compile(r"live session|intervista|\btg\b|notiziario|spot|promo|festa|concerto|premiazion|inaugurazion|cerimonia|ragazzi|bambini|elezion|"
                          r"campagna|candidat|messa|processione|auguri", re.I))
# Poland: council sessions (sesja rady gminy / rady miejskiej) and the education committee (komisja oświaty);
# youth and seniors' councils (młodzieżowa rada, rada seniorów) and ceremonies aren't counted.
RULES["PL"] = (re.compile(r"komisj[aiy][^|]{0,60}(o[sś]wiat|edukacj|szk[oó][lł])", re.I),
               re.compile(r"sesj|obrad", re.I),
               re.compile(r"^(?!.*(komisj|m[lł]odzie[zż]ow|senior|dzieci)).*(sesj[aię]\s+(rady|nadzwyczajn|zwyczajn|absolutoryjn|bud[zż]etow|nr)|"
                          r"\b[ivxlc]+\.?\s+(nadzwyczajna\s+)?sesj|\d+\.?\s+(nadzwyczajna\s+)?sesj|obrady\s+(sesji|rady)|sesja\s+\d)", re.I),
               re.compile(r"live session|uroczyst|wywiad|spot|reklam|festyn|koncert|do[zż]ynk|msza|[zż]yczenia|m[lł]odzie[zż]ow|senior|wybory|kampani|kandydat|"
                          r"relacja z|transmisja meczu", re.I))

# Spain: a committee covering education counts only when at least this many of its sessions are posted; otherwise the
# council's plenaries do (one stray committee clip shouldn't replace 160 plenaries).
MIN_EDU = {"ES": 3, "FRA": 3, "EC": 3, "IT": 3, "PL": 3}


def session_key(cc, t):
    """A key for an undated title. Brazilian chambers often post one clip per speaker ("Fulano - Pequeno Expediente da
    85ª Sessão Ordinária"), so there the session's number and kind (and year, when given) identify the meeting."""
    if cc == "BR":
        m = re.search(r"(\d+)\s*[ªºa°o]?\.?\s*sess[ãa]o\s+(ordin|extra|solen|espec)", t, re.I)
        if m:
            y = re.search(r"\b(20\d\d)\b", t)
            return f"{m.group(1)} {m.group(2).lower()} {y.group(1) if y else ''}"
    return re.sub(r"\b(parte|part|cz[eę][sś][cć])\s*\d+\b|\(\d\)|\d/\d", "", t, flags=re.I).strip().lower()


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
    # Italy: one of Rome's districts (municipi), not Rome's city council
    "IT": {"https://www.youtube.com/channel/UCTzjPrb12wVS2Io2QN_Mo0g"},   # Municipio Roma VI
    # France: Quebec towns with a French commune's name (checked by their videos' titles)
    "FRA": {
        "https://www.youtube.com/channel/UCNsIi4vI4it0sAn8Afu4l7w",   # Montréal (Quebec), Outremont borough
        "https://www.youtube.com/channel/UCy70F0jEYrWzl91rLqNgnHg",   # Saint-Colomban (Quebec): "séance ordinaire du conseil municipal"
        "https://www.youtube.com/channel/UCtmxC4mDsr1ZOjz82jOIcfw",   # Saint-Urbain (Charlevoix, Quebec)
        "https://www.youtube.com/channel/UCe2bGobWvN5-V3lm1bxSA3Q",   # Carignan (Quebec): "séance du conseil de la ville"
    },
    # Ecuador: channels of a town with the same name elsewhere (checked by their videos' titles)
    "EC": {
        "https://www.youtube.com/channel/UCZaI4dep0kp5vZa3gCsEwLQ",   # Santo Domingo (Chile): "I.M." and Chilean council terms
        "https://www.youtube.com/channel/UCQSNpiNkO1HiGbGdqBjzNoQ",   # San Miguel (Chile): its PLADECO
        "https://www.youtube.com/channel/UCT1O2zd6JGvB8RHXfCSmUxg",   # San Fernando (Chile): "agenda comunal"
        "https://www.youtube.com/channel/UCvjGChO7WnaVGeYmY4p97Ig",   # Santa Ana: no sign it is Ecuadorian
        "https://www.youtube.com/channel/UCQhuEql9HplzsCZ4Oxv5yew",   # El Carmen: no sign it is Ecuadorian
        "https://www.youtube.com/channel/UCU8hYDWnuwJ28rsbTtND1LA",   # San Vicente: English titles, another country
        "https://www.youtube.com/channel/UCZXpwy8DfsnN1x61GBQB0ZA",   # Santa Cruz: no sign it is Ecuadorian (Bolivia?)
        "https://www.youtube.com/channel/UCAMrQUisobtjKiSE4vWvu9g",   # Lo Espejo (Chile)
        "https://www.youtube.com/channel/UCTW3WKCTHx5N1jkO_T-6R2A",   # Santa Rosa de Osos (Colombia)
    },
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


FR_FOREIGN = re.compile(r"municipalit[ée]|qu[ée]bec|\bqc\b|belgique|suisse|\bcanton\b|\bcom\.?\s*com", re.I)
FR_JOIN = {"de", "du", "des", "d", "sur", "sous", "les", "lez", "en", "la", "le", "aux", "au", "et"}
FR_BEFORE = {"de", "d", "du", "ville", "mairie", "commune", "cite", "officiel", "conseil", "municipal", "ma", "agglo", "metropole", "hotel"}
# Poland: county councils (powiat, starostwo), youth councils and councillors' own channels aren't the gmina council.
PL_NOT_OWN = re.compile(r"powiat|starostw|m[lł]odzie[zż]|radn[ya]\b|radnego|radnej|senior", re.I)
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
            if cc == "PL":   # "(rural gmina)" isn't in channel names
                alts = [re.sub(r" (urban|rural|urban rural) gmina$", "", a) for a in alts]
            nm = next((a for a in alts if " " + a + " " in ch), "")
            if not nm and cc == "PL":
                # Polish channels use other cases of the name: "Rada m.st. Warszawy", "Rada Miejska w Łodzi", "Rada Miasta Krakowa"
                stem = lambda w: w[:max(4, len(w) - 2)]
                nm = next((a for a in alts if all(any(c.startswith(stem(w)) and len(c) <= len(w) + 3 for c in ch.split()) for w in a.split())), "")
            if cc == "PL" and PL_NOT_OWN.search(raw): return -1
            if not nm: return -1
            if cc == "FRA":
                # French names are often the start of a longer one (Saint-Joseph-du-Lac, Saint-Paul-lès-Dax) or the end of
                # one (La Côte-Saint-André), and Quebec's municipalities share many: the name must stand on its own.
                if FR_FOREIGN.search(raw): return -1
                i = ch.index(" " + nm + " "); before = ch[:i].split()[-1:] or [""]; after = ch[i + len(nm) + 2:].split()[:1] or [""]
                if after[0] in FR_JOIN or (before[0] and before[0] not in FR_BEFORE): return -1
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
        if r.get("_own_meetings"): continue   # counted another way (Japan: board of education minutes)
        n, url, keep, kind = meetings(cc, r["District ID"])
        if url and cc not in CHECKED and own.get(url) != r["District ID"]: n, url, keep, kind = 0, "", [], ""
        latest, years = date_summary(keep) if n else ("", "")
        r.update({"Available Board Meetings": n, "Meetings type": kind, "Meetings source": url, "Latest meeting": latest, "Meetings by year": years})
    cols = ["District", "Region", "Locale", "Available Board Meetings", "Meetings type", "Meetings source", "Latest meeting", "Meetings by year",
            "Population", "Percentage of Children in Low Income", "Poverty rate (all ages)", "Multidimensional poverty (all ages)", "Poverty note", "Enrollment", "Enrollment year",
            "Public school enrollment", "School system", "People per km² (estimated)", "District ID"]
    extra = [c for c in ("Province", "Autonomous community", "Children under 18 (estimated)", "Poverty year", "Poverty range", "Poverty rate (region, all ages)", ES_EST,
                         "Child poverty rate (département)", "Median standard of living (€ per year)", "Poverty standard error", "Unmet basic needs (NBI, 2010)", "Extreme poverty (all ages)", "Poverty by year", "Children 6–17", "Bolsa Família families per 100 households", "Bolsa Família families", "Households", "Mean income (€ per filer)", "Children on family benefit", "Social assistance (% of people)", "Welfare rate basis", "Unemployment rate (2020 census)", "Children under 15", "Children on family benefit (% of under-20s)", "Median income (€ per taxpayer)", "Children under 18", "Mean income (€ per tax return)") if any(r.get(c) not in (None, "") for r in rows)]
    pov = "Percentage of Children in Low Income" if any(r.get("Percentage of Children in Low Income") for r in rows) else "Poverty rate (all ages)"
    cols = [c for c in cols if c not in ("Percentage of Children in Low Income", "Poverty rate (all ages)", "Multidimensional poverty (all ages)") or any(r.get(c) not in (None, "") for r in rows)]
    cols = cols[:cols.index("Poverty note") + 1] + [c for c in extra if c != "Children 6–17"] + cols[cols.index("Poverty note") + 1:-1] + [c for c in extra if c == "Children 6–17"] + cols[-1:]
    for c in ("Autonomous community", "Province"):
        if c in cols: cols.remove(c); cols.insert(cols.index("Region") + 1, c)
    # Spain's regional stand-in rate goes near the end, out of the summary figures (the first number columns).
    for c in ("Poverty rate (region, all ages)", ES_EST):
        if c in cols: cols.remove(c); cols.insert(len(cols) - 1, c)
    # Newer borders for places the main borders file lacks (districts and municipalities created since), checked to lie
    # inside the place they were made from: inputs/<country>/extra_borders.geojson.
    xf = os.path.join(IN, DIRS.get(cc, key), "extra_borders.geojson")
    if os.path.exists(xf):
        have = {f["properties"]["id"] for f in feats}
        for f in json.load(open(xf, encoding="utf-8"))["features"]:
            r = next((r for r in rows if r["District ID"] == f["properties"]["id"]), None)
            if r and f["properties"]["id"] not in have and f.get("geometry"):
                feats.append({"type": "Feature", "properties": {"id": f["properties"]["id"], "NAME": r["District"]},
                              "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
                r["_geo"] = True
                # Its locale, from its own border (the main file had none to measure).
                area, pop = area_km2(f["geometry"]), toint(r.get("Population"))
                if not r.get("Locale") and area and pop:
                    r["Locale"] = loc(pop / area)
                    if "People per km² (estimated)" in r: r["People per km² (estimated)"] = round(pop / area)
    # Places still without a locale (no population or no border to measure): the most common locale in their
    # region, as an estimate, said so in a column of its own.
    known = {}
    for r in rows:
        if r.get("Locale"): known.setdefault(r.get("Region"), Counter())[r["Locale"]] += 1
    for r in rows:
        if not r.get("Locale") and known.get(r.get("Region")):
            r["Locale"] = known[r.get("Region")].most_common(1)[0][0]
            r["Locale note"] = f"Locale estimated: no population or border to measure, so it's the most common locale in {r.get('Region')}"
    if any(r.get("Locale note") for r in rows) and "Locale note" not in cols: cols.insert(len(cols) - 1, "Locale note")
    rows.sort(key=lambda r: r["District"])
    with open(os.path.join(DOCS, f"{key}.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=cols, restval="", extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", f"{key}.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(cc, len(rows), "rows; poverty", sum(1 for r in rows if r.get(pov)), "; enrollment", sum(1 for r in rows if r.get("Enrollment")),
          "; meetings", sum(1 for r in rows if r["Available Board Meetings"]), "; no border", [r["District"] for r in rows if not r.get("_geo")][:10])


ES_EST = "Child low-income rate (estimated from its province)"


def toint(v):
    try: return int(float(str(v).replace(",", "")))
    except (TypeError, ValueError): return 0


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
        n = norm(f["properties"]["shapeName"])
        # The borders file names Pozo Almonte (Tarapacá) "Tocopilla" too; the real Tocopilla is further south.
        if n == "tocopilla" and centroid(f["geometry"])[1] > -21.5: n = "pozoalmonte"
        by_name[ALIAS["CL"].get(n, n)] = f
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
    # Created after CONEVAL's 2020 figures, so they have none of their own: the rate of the municipality each was
    # made from stands in, in a column of its own (as Brazil's Boa Esperança do Norte does).
    for new, old in (("MX-07125", "MX-07080"), ("MX-04012", "MX-04004")):
        n, o = (next((r for r in rows if r["District ID"] == k), None) for k in (new, old))
        if n and o and not n["Poverty rate (all ages)"]:
            n["Poverty rate (region, all ages)"] = o["Poverty rate (all ages)"]
            n["Poverty note"] = (f"Made from {o['District']} and not in CONEVAL's 2020 figures: {o['District']}'s rate "
                                 "(multidimensional poverty, all ages, 2020) as a stand-in")
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
    # Boa Esperança do Norte (2025) was a district of Sorriso at the 2022 census, so it has no figures of its own:
    # Sorriso's rate stands in, in a column of its own.
    new, old = next((r for r in rows if r["District ID"] == "BR-5101837"), None), next((r for r in rows if r["District ID"] == "BR-5107925"), None)
    if new and old and not new.get("Poverty rate (all ages)") and old.get("Poverty rate (all ages)"):
        new["Poverty rate (region, all ages)"] = old["Poverty rate (all ages)"]
        new["Poverty note"] = "Created in 2025 from Sorriso, after the 2022 census: Sorriso's rate (all ages, household income up to half the minimum wage per person, 2022) as a stand-in"
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
ES_NUTS2 = {"Galicia": "ES11", "Asturias": "ES12", "Cantabria": "ES13", "País Vasco": "ES21", "Navarra": "ES22", "La Rioja": "ES23",
            "Aragón": "ES24", "Madrid": "ES30", "Castilla y León": "ES41", "Castilla-La Mancha": "ES42", "Extremadura": "ES43",
            "Cataluña": "ES51", "Comunitat Valenciana": "ES52", "Illes Balears": "ES53", "Andalucía": "ES61", "Murcia": "ES62",
            "Ceuta": "ES63", "Melilla": "ES64", "Canarias": "ES70"}


def es_region_poverty():
    """{NUTS 2 code: (rate, year)}: Eurostat's at-risk-of-poverty rate (all ages, below 60% of the national median
    income) for each autonomous community (ilc_li41), latest year."""
    d = json.load(open(os.path.join(IN, "spain", "eurostat_ilc_li41_es.json")))
    ids, size = d["id"], d["size"]; cat = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
    out = {}
    for g in cat["geo"]:
        for t in sorted(cat["time"], reverse=True):
            sel = {k: cat[k][0] for k in ids}; sel.update(geo=g, time=t); i = 0
            for k, n in zip(ids, size): i = i * n + cat[k].index(sel[k])
            if str(i) in d["value"]:
                out[g] = (d["value"][str(i)], t); break
    return out


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
    # Putumayo province (2014) took two of Maynas's districts, which got new codes; the borders file has the old ones.
    # Putumayo's old border also covers Rosa Panduro and Yaguas, made from it.
    for old, new in (("160109", "160801"), ("160114", "160803")):
        if old in geo and new not in geo: geo[new] = geo.pop(old)
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
    reg = es_region_poverty()
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
    # INE leaves out small municipalities' child figure. Estimate for each: the child low-income rate of the
    # province's other small municipalities (under 10,000 people) that have a figure, weighted by their children;
    # all of the province's municipalities with a figure if fewer than 3 small ones have one.
    latest = {c: v[max(v)] for c, v in pov.items() if v}
    weight = lambda c: (float(dem[c].get("pop") or 0) * (dem[c].get("pct18") or 18) / 100) or 1
    prov_est = {}
    for pr in {c[:2] for c in dem}:
        have = [c for c in latest if c[:2] == pr and c in dem]
        small = [c for c in have if float(dem[c].get("pop") or 0) < 10000]
        use = small if len(small) >= 3 else have
        if use: prov_est[pr] = (sum(latest[c] * weight(c) for c in use) / sum(weight(c) for c in use), len(use), use is small)
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
                     ES_EST: "" if p or code[:2] not in prov_est else f"{prov_est[code[:2]][0]:.1f}%",
                     "Poverty rate (region, all ages)": "" if p or code[:2] in prov_est else f"{reg[ES_NUTS2[ES_CCAA[code[:2]]]][0]:.1f}%",
                     "Poverty note": "People under 18 in households below 60% of the national median income per consumption unit (INE, household income atlas)" if p else
                         (f"No child figure: INE leaves out small municipalities. Estimated from {ES_PROV[code[:2]]}'s {prov_est[code[:2]][1]} "
                          f"{'smaller municipalities (under 10,000 people)' if prov_est[code[:2]][2] else 'municipalities'} that have one (same measure, weighted by their children)")
                         if code[:2] in prov_est else
                         f"No child figure: INE leaves out small municipalities. In its place, {ES_CCAA[code[:2]]}'s overall poverty rate (all ages, below 60% of the national median income; Eurostat, {reg[ES_NUTS2[ES_CCAA[code[:2]]]][1]})",
                     "Children under 18 (estimated)": kids, "School system": f"{ES_CCAA[code[:2]]} education department",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    # Land that belongs to no single municipality (Bardenas Reales, facerías, comunidades and ledanías shared by
    # several towns): drawn on the map only, like the US areas outside every school district.
    used = {id(f) for f in geo.values()}
    for i, f in enumerate(x for x in adm3 if id(x) not in used):
        feats.append({"type": "Feature", "properties": {"id": f"ES-SHARED-{i}", "NAME": f"Shared land (no municipality): {f['properties']['shapeName']}"},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("ES", "spain", rows, feats)



def france():
    """The communes INSEE publishes a poverty rate for (Filosofi 2023: those with enough tax households, about
    2,000+ people), in mainland France, Corsica and Réunion. Communes own and run the buildings of nursery and
    primary schools; the national education ministry employs the teachers. The town council (conseil municipal)
    stands in for meetings. Every other commune (too few households for INSEE to publish a rate) is listed too,
    with its département's rate in a column of its own."""
    d = os.path.join(IN, "france")
    ins = json.load(open(os.path.join(d, "fr_insee_2023.json"), encoding="utf-8"))
    pupils = json.load(open(os.path.join(d, "fr_ecoles_eleves_2025.json"), encoding="utf-8"))["by_commune"]
    geo = {f["properties"]["grp"]: f for f in json.load(open(os.path.join(d, "fr_communes_map_2023.geojson"), encoding="utf-8"))["features"] if f.get("geometry")}
    deps = {f["properties"]["code"]: f["properties"]["nom"] for f in json.load(open(os.path.join(d, "fr_departements.geojson"), encoding="utf-8"))["features"]}
    deps["974"] = "La Réunion"
    # Overseas départements with no commune rates: each commune gets its département's rate (INSEE's regional table)
    # in a column of its own, as Spain's small municipalities do.
    om = json.load(open(os.path.join(d, "fr_outremer_poverty.json"), encoding="utf-8"))["departements"]
    om_names = json.load(open(os.path.join(d, "fr_outremer_commune_names.json"), encoding="utf-8"))
    for k, v in om.items(): deps[k] = v["name"]
    for c, n in om_names.items():
        ins["communes"].setdefault(c, {"name": n, "pop": None})
    dep_of = lambda c: c[:3] if c.startswith("97") else c[:2]
    rows, feats, small_feats = [], [], []
    for code, x in sorted(ins["communes"].items()):
        if dep_of(code) not in deps: continue
        dp = dep_of(code); dx = ins["departements"].get(dp, {})
        # Communes INSEE publishes no rate for (too few tax households): the département's rate, 2023.
        small = "PR_MD60" not in x and dp not in om and dx.get("PR_MD60") is not None
        f = geo.get(code); area = area_km2(f["geometry"]) if f else 0
        dens = x["pop"] / area if area and x.get("pop") else 0
        pu = pupils.get(code, {})
        did = f"FRA-{code}"
        o = om.get(dp) if "PR_MD60" not in x else None
        rows.append({"District": x["name"], "Region": deps[dp], "Population": x.get("pop") or "",
                     "Poverty rate (all ages)": f"{x['PR_MD60']:.1f}%" if "PR_MD60" in x else "",
                     "Poverty rate (region, all ages)": f"{o['rate']:.1f}%" if o else f"{dx['PR_MD60']:.1f}%" if small else "",
                     "Child poverty rate (département)": f"{dx['child']:.1f}%" if dx.get("child") is not None else "",
                     "Median standard of living (€ per year)": round(x["MED_SL"]) if x.get("MED_SL") else "",
                     "Poverty note": (f"No commune figure: {deps[dp]}'s overall rate, {o['year']} (INSEE, {o['basis']}; people below 60% of mainland France's median standard of living)"
                                      + ("" if dp == "972" else "; from a survey, so not comparable with the other départements' figures")) if o else
                         "No commune figure (too few households): the département's rate, 2023" if small else
                         "People below 60% of the national median standard of living, all ages, 2023 (INSEE, Filosofi); INSEE publishes no child rate by commune, so the département's rate for under-18s is given too",
                     "Enrollment": pu.get("total", ""), "Enrollment year": "2025-26 (nursery and primary schools)" if pu else "",
                     "Public school enrollment": pu.get("public", ""), "School system": "Commune (school buildings); Ministry of Education (teachers)",
                     # Mayotte has no commune populations here: its overall density (256,518 people in 2017 on 374 km², about 690 per km²)
                     "Locale": loc(dens) if dens else "Suburban" if dp == "976" else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: (small_feats if small else feats).append({"type": "Feature", "properties": {"id": did, "NAME": x["name"]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    # The map draws the small communes only when asked ("Smaller French communes", data/map/france-small.json);
    # otherwise each département's small communes are one map-only area, with the département's rate.
    merged = json.load(open(os.path.join(d, "fr_communes_map_merged.geojson"), encoding="utf-8"))["features"]
    for f in merged:
        k = f["properties"]["grp"]
        if not k.startswith("REST-") or k[5:] not in deps or not f.get("geometry"): continue
        dp = k[5:]; dx = ins["departements"].get(dp, {})
        sm = [c for c, x in ins["communes"].items() if dep_of(c) == dp and "PR_MD60" not in x]
        feats.append({"type": "Feature", "properties": {"id": f"FRA-REST-{dp}", "NAME": f"Smaller communes of {deps[dp]}", "pseudo": True, "dep": deps[dp],
                      "pct": dx.get("PR_MD60"), "child": dx.get("child"), "communes": len(sm), "pop": sum(ins["communes"][c].get("pop") or 0 for c in sm)},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("FRA", "france", rows, feats)
    json.dump({"type": "FeatureCollection", "features": small_feats}, open(os.path.join(DOCS, "map", "france-small.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print("  small communes on their own map layer:", len(small_feats))


def italy():
    """7,896 comuni. State schools are run by the Ministry of Education (Ministero dell'Istruzione e del Merito);
    comuni own and look after the buildings of nursery, primary and lower secondary schools, and run school meals
    and transport. The town council (consiglio comunale) stands in for meetings. Poverty stand-in: the share of
    income-tax filers with a total income of 10,000 euros a year or less (Ministry of Economy and Finance, 2023):
    Italy publishes no poverty rate by comune."""
    d = os.path.join(IN, "italy")
    com = json.load(open(os.path.join(d, "it_comuni.json"), encoding="utf-8"))
    inc = json.load(open(os.path.join(d, "it_income_2023.json"), encoding="utf-8"))
    pup = json.load(open(os.path.join(d, "it_pupils_2024_25.json"), encoding="utf-8"))
    geo = {f["properties"]["GISCO_ID"][3:]: f for f in json.load(open(os.path.join(d, "lau_IT.geojson"), encoding="utf-8"))["features"]}
    # The province's share, for the few comuni whose figure the ministry leaves out.
    prov = {}
    for code, x in com.items():
        i = inc.get(code) or {}
        if i.get("share") is not None:
            a = prov.setdefault(x["province"], [0, 0]); a[0] += i["under10k"]; a[1] += i["taxpayers"]
    rows, feats = [], []
    for code, x in sorted(com.items()):
        f = geo.get(code); p = f["properties"] if f else {}
        pop = int(p["POP_2024"]) if p.get("POP_2024") else ""
        dens = p.get("POP_DENS_2024") or (pop / area_km2(f["geometry"]) if f and pop else 0)
        i = inc.get(code, {}); pu = pup.get(code)
        did = f"IT-{code}"
        name = x["name"] + (f" / {x['other']}" if x["other"] and x["other"] != x["name"] else "")
        rows.append({"District": name, "Region": x["region"], "Province": x["province"], "Population": pop,
                     "Poverty rate (all ages)": f"{i['share']:.1f}%" if i.get("share") is not None else "",
                     "Poverty rate (region, all ages)": "" if i.get("share") is not None or x["province"] not in prov else f"{100 * prov[x['province']][0] / prov[x['province']][1]:.1f}%",
                     "Poverty note": "Stand-in: the share of income-tax filers whose total income was 10,000 euros a year or less, 2023 "
                                     "(Ministry of Economy and Finance); Italy publishes no poverty rate by comune" if i.get("share") is not None else
                                     f"Stand-in: the ministry leaves out this comune's count of low incomes (too few filers), so the share for the province of {x['province']} is shown, 2023",
                     "Mean income (€ per filer)": i.get("mean_income") or "",
                     "Enrollment": (pu["state"] + pu["private"]) if pu else "", "Public school enrollment": pu["state"] if pu else "",
                     "Enrollment year": "2024-25 (primary and lower secondary schools)" if pu else "",
                     "School system": "Ministry of Education (schools); comune (buildings, meals, transport)",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("IT", "italy", rows, feats)


PL_VOIV = {"02": "Dolnośląskie", "04": "Kujawsko-pomorskie", "06": "Lubelskie", "08": "Lubuskie", "10": "Łódzkie", "12": "Małopolskie",
           "14": "Mazowieckie", "16": "Opolskie", "18": "Podkarpackie", "20": "Podlaskie", "22": "Pomorskie", "24": "Śląskie",
           "26": "Świętokrzyskie", "28": "Warmińsko-mazurskie", "30": "Wielkopolskie", "32": "Zachodniopomorskie"}
PL_KIND = {"1": "urban gmina", "2": "rural gmina", "3": "urban-rural gmina"}


def poland():
    """2,477 municipalities (gminy), which run their nursery and primary schools. The town council (rada gminy or
    rada miejska) is the elected body; since 2018 every council must record its sessions and publish the
    recordings. Poverty: the share of children aged 0-17 whose parents receive the means-tested family benefit
    (zasiłek rodzinny), 2024 (Statistics Poland, Local Data Bank)."""
    d = os.path.join(IN, "poland")
    bdl = json.load(open(os.path.join(d, "pl_bdl_2024.json"), encoding="utf-8"))
    pup_f = os.path.join(d, "pl_pupils.json")
    pup = json.load(open(pup_f, encoding="utf-8")) if os.path.exists(pup_f) else {}
    geo = {f["properties"]["GISCO_ID"][5:]: f for f in json.load(open(os.path.join(d, "lau_PL.geojson"), encoding="utf-8"))["features"]}
    names, vals = bdl["names"], bdl["values"]
    units = [u for u in names if u[-1] in PL_KIND]
    dup = Counter((u[2:4], names[u]) for u in units)
    rows, feats = [], []
    for u in sorted(units, key=lambda u: names[u]):
        f = geo.get(u[:-1]); p = f["properties"] if f else {}
        # Statistics Poland's names carry notes ("M.st.Warszawa od 2002", "Wałbrzych od 2013").
        base = re.sub(r"\s+od \d{4}$", "", names[u]).replace("M.st.Warszawa", "Warszawa")
        name = base + (f" ({PL_KIND[u[-1]]})" if dup[(u[2:4], names[u])] > 1 else "")
        share = vals.get("259889", {}).get(u, {}); kids = vals.get("259888", {}).get(u, {}); sa = vals.get("1548717", {}).get(u, {})
        y = max(share) if share else ""
        pop = int(p["POP_2024"]) if p.get("POP_2024") else ""
        dens = p.get("POP_DENS_2024") or 0
        did = f"PL-{u}"
        enr = pup.get(u, "")
        rows.append({"District": name, "Region": PL_VOIV.get(u[2:4], ""), "Population": pop,
                     "Percentage of Children in Low Income": f"{share[y]:.1f}%" if share else "", "Poverty year": y,
                     "Poverty note": "Share of children aged 0-17 whose parents receive the means-tested family benefit (zasiłek rodzinny), "
                                     f"{y} (Statistics Poland, Local Data Bank)" if share else "",
                     "Children on family benefit": round(kids[max(kids)]) if kids else "",
                     "Social assistance (% of people)": f"{sa[max(sa)] / 100:.1f}%" if sa else "",
                     "Enrollment": enr, "Enrollment year": "2024-25 (primary schools)" if enr != "" else "",
                     "School system": f"Gmina ({PL_KIND[u[-1]]})",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("PL", "poland", rows, feats)


def japan():
    """1,741 municipalities (cities, towns, villages and Tokyo's special wards), each with its own board of education
    (教育委員会), which runs its elementary and lower secondary schools and meets in public, usually monthly.
    Poverty stand-in: the welfare rate (生活保護), people receiving public assistance as a share of the population,
    FY2024 (Ministry of Health, Labour and Welfare). It's published for designated and core cities; every other
    municipality gets its prefecture's rate outside those cities (the survey splits a prefecture by who runs the welfare
    office, not by cities and towns: in Shimane and Hiroshima the towns run their own, so its town figure is empty)."""
    d = os.path.join(IN, "japan")
    mun = json.load(open(os.path.join(d, "jp_municipal.json"), encoding="utf-8"))
    wel = json.load(open(os.path.join(d, "jp_welfare_2024.json"), encoding="utf-8"))
    mf = os.path.join(d, "jp_minutes.json")
    mins = {m["code"]: m for m in json.load(open(mf, encoding="utf-8"))} if os.path.exists(mf) else {}
    geo = {f["properties"]["id"]: f for f in json.load(open(os.path.join(d, "jp_borders.geojson"), encoding="utf-8"))["features"]}
    pref = {c[:2]: v for c, v in mun.items() if c.endswith("000")}
    places = {c: v for c, v in mun.items() if not c.endswith("000") and c != "13100" and not (v["name"].endswith("区") and not c.startswith("131"))}
    pref_en = lambda c: re.sub(r"-(ken|fu|to)$", "", pref[c[:2]]["en"])
    own = {c for c, v in places.items() if v["name"] in wel["cities"] and wel["cities"][v["name"]]["total"]}
    # Each prefecture outside its designated and core cities: recipients (monthly average) over people.
    grp = {}
    for c, v in places.items():
        if c in own: continue
        g = grp.setdefault(c[:2], [0, 0]); g[1] += v.get("pop") or 0
    for pc, g in grp.items():
        w = wel["prefectures"].get(pref[pc]["name"], {}).get("total")
        g[0] = w / 12 if w else None
    rows, feats = [], []
    for c, v in sorted(places.items()):
        pop = v.get("pop") or 0
        if c in own:
            rate, basis = wel["cities"][v["name"]]["total"] / 12 / pop * 100 if pop else None, f"Its own ({wel['cities'][v['name']]['kind']})"
        else:
            g = grp[c[:2]]
            rate = g[0] / g[1] * 100 if g[0] and g[1] else None
            basis = f"{pref_en(c)} outside its designated and core cities"
        en = re.sub(r"-(shi|machi|cho|mura|son|ku)$", "", v["en"])
        name = f"{en} ({v['name']})"
        f = geo.get(f"JP-{c}")
        dens = pop / v["area"] if pop and v.get("area") else 0
        enr = (v.get("elementary") or 0) + (v.get("lower_secondary") or 0)
        m = mins.get(c, {})
        n = m.get("meetings") or 0
        years = "; ".join(f"{y}:{k}" for y, k in sorted(m.get("years", {}).items()) if y != "?")
        rows.append({"District": name, "Region": pref_en(c), "Population": round(pop) if pop else "",
                     "Poverty rate (all ages)": f"{rate:.2f}%" if rate is not None else "",
                     "Welfare rate basis": basis if rate is not None else "",
                     "Poverty note": ("Welfare rate: people receiving public assistance (生活保護), monthly average for FY2024, as a share of the 2020 census population "
                                      "(Ministry of Health, Labour and Welfare, survey of welfare recipients). "
                                      + ("" if c in own else f"Published only for designated and core cities; this is the rate for {basis}")),
                     "Unemployment rate (2020 census)": f"{100 * v['unemployed'] / v['labour_force']:.1f}%" if v.get("unemployed") and v.get("labour_force") else "",
                     "Children under 15": round(v["under15"]) if v.get("under15") else "",
                     "Enrollment": round(enr) if enr else "", "Enrollment year": "2024 (elementary and lower secondary schools)" if enr else "",
                     "School system": "Board of education (教育委員会)",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": f"JP-{c}", "_geo": bool(f),
                     "_own_meetings": True, "Available Board Meetings": n, "Meetings type": "Board of education (minutes)" if n else "",
                     "Meetings source": (m.get("pages") or [m.get("board", "")])[0] if n else "", "Latest meeting": max((y for y in m.get("years", {}) if y != "?"), default="") if n else "",
                     "Meetings by year": years if n else ""})
        if f: feats.append({"type": "Feature", "properties": {"id": f"JP-{c}", "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("JP", "japan", rows, feats)


PT_DIST = {"01": "Aveiro", "02": "Beja", "03": "Braga", "04": "Bragança", "05": "Castelo Branco", "06": "Coimbra", "07": "Évora", "08": "Faro",
           "09": "Guarda", "10": "Leiria", "11": "Lisboa", "12": "Portalegre", "13": "Porto", "14": "Santarém", "15": "Setúbal",
           "16": "Viana do Castelo", "17": "Vila Real", "18": "Viseu", "31": "Madeira", "32": "Madeira"}


def portugal():
    """308 municipalities (municípios). Since 2019 they run more of public schooling (buildings, non-teaching staff,
    meals, transport for pre-school and basic education); the Ministry of Education employs teachers. The municipal
    assembly (assembleia municipal) and council (câmara municipal) meet in public; their sessions stand in for
    meetings. Poverty stand-in: social insertion income (RSI) beneficiaries per 100 people of working age, 2025."""
    d = os.path.join(IN, "portugal")
    ine = json.load(open(os.path.join(d, "pt_ine.json"), encoding="utf-8"))
    geo = {f["properties"]["muni"]: f for f in json.load(open(os.path.join(d, "pt_municipalities.geojson"), encoding="utf-8"))["features"]}
    rows, feats = [], []
    for code, x in sorted(ine.items()):
        f = geo.get(code); p = f["properties"] if f else {}
        pop = x.get("pop") or p.get("POP") or 0
        dens = pop / p["AREA"] if pop and p.get("AREA") else 0
        region = PT_DIST.get(code[:2]) or ("Açores" if code[:2] >= "41" else "")
        did = f"PT-{code}"
        rsi = x.get("rsi_per1000")
        rows.append({"District": x["name"], "Region": region, "Population": round(pop) if pop else "",
                     "Poverty rate (all ages)": f"{rsi / 10:.2f}%" if rsi is not None else "",
                     "Poverty note": f"Stand-in: people receiving the social insertion income (rendimento social de inserção), Portugal's minimum-income benefit, "
                                     f"per 100 people of working age, {x.get('rsi_per1000_year', '')} (INE, from Social Security records); Portugal publishes no poverty rate by municipality",
                     "Children on family benefit (% of under-20s)": f"{100 * x['abono_children'] / x['u20']:.0f}%" if x.get("abono_children") and x.get("u20") else "",
                     "Median income (€ per taxpayer)": round(x["median_income"]) if x.get("median_income") else "",
                     "Children under 18 (estimated)": round(x["u18"]) if x.get("u18") else "",
                     "School system": "Ministry of Education (teachers); municipality (buildings, staff, meals, transport)",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": x["name"]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("PT", "portugal", rows, feats)


def belgium():
    """565 municipalities (after the 2025 mergers). Municipalities run their own primary schools (municipal
    education, gemeentelijk onderwijs / enseignement communal) alongside the communities' and the free (mostly Catholic)
    networks; the town council (gemeenteraad / conseil communal) is their school board. Poverty stand-in: people
    receiving the integration income (leefloon / revenu d'intégration), per 100 inhabitants, 2025 (PPS Social Integration)."""
    d = os.path.join(IN, "belgium")
    be = json.load(open(os.path.join(d, "be_data.json"), encoding="utf-8"))
    ris = json.load(open(os.path.join(d, "be_ris_2025.json"), encoding="utf-8"))
    geo = {f["properties"]["refnis"]: f for f in json.load(open(os.path.join(d, "be_municipalities_2025.geojson"), encoding="utf-8"))["features"]}
    rows, feats = [], []
    for code, x in sorted(be.items()):
        f = geo.get(code); p = f["properties"] if f else {}
        reg = x["region_nl"]
        name = (x["nl"] if reg == "Vlaams Gewest" else x["fr"] if reg == "Waals Gewest" else (x["fr"] if x["fr"] == x["nl"] else f"{x['fr']} / {x['nl']}"))
        name = re.sub(r"\s*\((?:à partir de|vanaf) 2025\)|\s*\([^)]*\)$", "", name).strip()
        prov = "Brussels" if x["province_nl"] == "Brussels" else re.sub(r"^(Provincie|Province)\s+(de |du |d’|d')?", "", x["province_nl"] if reg == "Vlaams Gewest" else x["province_fr"])
        pop = x.get("pop") or p.get("POP") or 0
        dens = pop / p["AREA"] if pop and p.get("AREA") else 0
        r = ris.get(code)
        did = f"BE-{code}"
        rows.append({"District": name, "Region": prov, "Population": round(pop) if pop else "",
                     "Poverty rate (all ages)": f"{r['per1000'] / 10:.2f}%" if r else "",
                     "Poverty note": "Stand-in: people receiving the integration income (leefloon / revenu d'intégration), Belgium's minimum-income benefit paid by the "
                                     "municipality's social welfare centre (OCMW / CPAS), during 2025, per 100 inhabitants (PPS Social Integration); Belgium publishes no poverty rate by municipality" if r else "",
                     "Children under 18": x.get("u18") or "",
                     "Mean income (€ per tax return)": x.get("income_per_return") or "",
                     "School system": "Municipality (its own primary schools), alongside the community's and the free schools",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("BE", "belgium", rows, feats)


EC_PROV_CAPS = {}


def ecuador():
    """221 cantons. Schools are run by the national Ministry of Education through its zones and districts; the
    cantonal council (concejo municipal of the GAD) stands in for meetings. Poverty: INEC and the World Bank's
    small-area estimate of consumption poverty (2010 census with the 2013-14 living conditions survey), all ages;
    also INEC's unmet basic needs (NBI) rate from the 2010 census."""
    d = os.path.join(IN, "ecuador")
    pv = json.load(open(os.path.join(d, "ec_poverty_cantons.json"), encoding="utf-8"))
    prov = {c: re.sub(r"\s+", " ", n).strip() for c, n in pv["provinces"].items()}
    pupils_f = os.path.join(d, "ec_pupils_by_canton.json")
    pup = json.load(open(pupils_f, encoding="utf-8")) if os.path.exists(pupils_f) else {"by_canton": {}, "year": ""}
    adm1 = json.load(open(os.path.join(d, "gb_ECU_ADM1.geojson"), encoding="utf-8"))["features"]
    pn = {norm(n): c for c, n in prov.items()}
    st = {id(f): pn.get(norm(f["properties"]["shapeName"])) for f in adm1}
    adm2 = [f for f in json.load(open(os.path.join(d, "gb_ECU_ADM2.geojson"), encoding="utf-8"))["features"] if f.get("geometry")]
    geo = adm_match("EC", [{"name": x["name"], "state": c[:2], "id": c} for c, x in pv["cantons"].items()], adm2, adm1, st)
    rows, feats = [], []
    for code, x in sorted(pv["cantons"].items()):
        f = geo.get(code); area = area_km2(f["geometry"]) if f else 0
        people = x.get("pop2010") or 0
        dens = people / area if area and people else 0
        p = pup["by_canton"].get(code, {})
        did = f"EC-{code}"
        est = "pov" in x and not (x["pov"] == 0 and x.get("pov_se") == 0)   # Galápagos: outside the survey, shown as 0
        rows.append({"District": x["name"], "Region": prov.get(code[:2], ""), "Population": people or "",
                     "Poverty rate (all ages)": f"{x['pov']:.2f}%" if est else "",
                     "Poverty standard error": f"{x['pov_se']:.2f}" if est else "",
                     # Galápagos: the province's 2010 poverty rate as reported by BBC News (2013; the measure isn't stated there)
                     "Poverty rate (region, all ages)": "" if est else "31.0%",
                     "Unmet basic needs (NBI, 2010)": f"{x['nbi2010']:.1f}%" if "nbi2010" in x else "",
                     "Poverty note": "Share of people below the consumption poverty line, all ages (INEC and World Bank poverty map: 2010 census with the 2013-14 living conditions survey); population from the 2010 census" if est else
                         "No consumption poverty estimate: the Galápagos were outside the 2013-14 living conditions survey. Shown instead: the Galápagos province's poverty rate of about 31% in 2010, as reported by BBC News (2013), which doesn't say how it was measured, so it isn't comparable with the other cantons; INEC's unmet basic needs (NBI) rate is given too",
                     "Enrollment": round(p["total"]) if p.get("total") else "", "Enrollment year": pup.get("year", "") if p else "",
                     "Public school enrollment": round(p["fiscal"]) if p.get("fiscal") else "",
                     "School system": "Ministry of Education (zone and district)",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": x["name"]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    # Map only: the zones whose canton is disputed (zonas no delimitadas), part of no canton.
    used = {id(f) for f in geo.values() if f}
    for i, f in enumerate(f for f in adm2 if id(f) not in used):
        feats.append({"type": "Feature", "properties": {"id": f"EC-SHARED-{i}", "NAME": f"Zone with no canton: {f['properties']['shapeName']}"},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("EC", "ecuador", rows, feats)


if __name__ == "__main__":
    which = sys.argv[1:] or ["chile", "colombia", "mexico", "brazil"]
    for w in which: globals()[w]()
