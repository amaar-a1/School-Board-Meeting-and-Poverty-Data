"""Turns the Israel downloads (made on GitHub's runner) into the small inputs build_latam.israel() reads
(data-prep/inputs/israel/).

- il_auth.geojson: each local authority's border, from OpenStreetMap (Geofabrik's Israel and Palestine extract,
  boundary=administrative, admin_level 8), matched by name; four authorities have no border there.
- il_data.json, per local authority (Interior Ministry list of local authorities, data.gov.il):
  pop22: people, Census 2022 (CBS, data.gov.il "Census 2022: population and households by locality"), added up over a
    regional council's localities;
  pop, age0_5, age6_18: residents in the Population Registry (Population and Immigration Authority, data.gov.il
    "Residents in Israel by locality and age groups"), current;
  welfare: people known to the municipal social services department in 2019 (Ministry of Welfare and Social Affairs,
    data.gov.il), and the authority's socio-economic cluster (1-10);
  pupils, public: pupils in schools (kindergartens left out) in 2015 (Ministry of Education, "Characteristics of
    education institutions"); public = official (רשמי) schools; recognized-unofficial (מוכר שאינו רשמי), exempt
    (פטור) and Talmud Torah schools are privately run;
  meetings: council meetings posted on the authority's own YouTube channel (fetch/il_yt.py).
Usage: python3 data-prep/prep_israel.py RAWDIR [RAWDIR ...]
"""
import csv, glob, json, os, re, sys
import openpyxl
from shapely.geometry import shape, mapping, Point

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "israel")
sys.path.insert(0, HERE)
from meeting_dates import parse as parse_date


def find(dirs, name):
    return sorted(f for d in dirs for f in glob.glob(os.path.join(d, "**", name), recursive=True))[-1]


def norm(s):
    s = re.sub(r"\(.*?\)", "", str(s or "")); s = re.sub(r"[\"'׳״\-–־_.,() ‏‎]", "", s)
    for pre in ("עיריית", "עירית", "מועצהמקומית", "מועצהאזורית", "מועצתאזורית", "מועצתמקומית", "רשות"):
        if s.startswith(pre): s = s[len(pre):]
    return s.replace("י", "").replace("ו", "").replace("קרת", "קרית")


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 4), round(c[1], 4)]


DISTRICT = {"הצפון": "Northern District", "המרכז": "Central District", "הדרום": "Southern District", "חיפה": "Haifa District",
            "אזור יהודה והשומרון": "West Bank (Judea and Samaria Area)", "תל אביב": "Tel Aviv District", "ירושלים": "Jerusalem District"}
SUBDISTRICT = {1: "Jerusalem District", 2: "Northern District", 3: "Haifa District", 4: "Central District", 5: "Tel Aviv District", 6: "Southern District",
               7: "West Bank (Judea and Samaria Area)"}
KIND = {"עירייה": "Municipality", "מועצה מקומית": "Local council", "מועצה אזורית": "Regional council"}
# Names OpenStreetMap spells another way (its English name), and two borders found by a point inside them.
OSM_EN = {"טירת כרמל": "Tirat HaCarmel", "סח'נין": "Sakhnin", "מגאר": "Maghar", "דאלית אל-כרמל": "Daliyat al-Karmel", "כסרא-סמיע": "Kisra - Sumei",
          "מג'דל שמס": "Majdal Shams", "סאג'ור": "Sajur", "שבלי - אום אל-גנם": "Shibli - Umm el Ghanam", "הגליל העליון": "Galil Elyon Regional Council",
          "הגליל התחתון": "Galil Tachton Regional Council", "כאוכב אבו אל-היג'א": "Kaukab Abu Al Hija", "תל אביב -יפו": "Tel-Aviv"}
# Council meetings: a meeting of the council or its plenary (מליאה), not a planning committee, a yeshiva (ישיבה also means
# yeshiva), a Knesset committee or an emergency-situation briefing.
OFFICIAL = re.compile(r"עירי|מועצה מקומית|מועצה אזורית|המועצה המקומית|המועצה האזורית|^מועצת|^רשות|שידורי|municipality|local council|regional council|بلدية|مجلس")
NOT_OFFICIAL = re.compile(r"נוער|דתית|לראשות|חבר מועצ|חדשות|נט |כל העיר|בעד|למען|תנועת|סיעת|מטה")
MEET = re.compile(r"(ישיבת|ישיבה|ישיבות|ישבת)\s*:?\s*(ה)?(מועצ|מליא|מלאה|תקציב|מן המני|מן המנין|שלא מן|לא מן|מיוחדת|חגיגית|עירייה|מס)|מליאת\s+(ה)?(מועצ|המועצה)|"
                  r"^(הקלטת |שידור |הסרטה )?(ה)?(ישיבת )?מליאה|מליאה (מוקלטת|מועצה|מן|שלא|לא מן|\d)|מועצת העיר [^|]*(\d{1,2}[./]\d{1,2}|מן המני|חודש)|^(דיון|ישיבת) מועצ|"
                  r"פרוטוקול ישיבה|ישיבת ה?מועצ|המליאה השקופה")
NOT_MEET = re.compile(r"ועדה המקומית|הועדה המקומית|ועדה מקומית|תכנון|ובני|מל\"?ח|כנסת|ממשלה|בני עקיבא|ראש ישיבת|ישיבה גבוהה|ישיבת הסדר|הספד|טקס|בחירות|לראשות|"
                      r"פודקאסט|נוער|ישיבת ועד|ועד מקומי|דתית|סיכום|מברכ|קורונה|ועדת הכספים|ועדת הפנים|ועדת הכלכלה|מערכון")
EDU = re.compile(r"ועדת\s+(ה)?חינוך")


# Other sources' names for an authority (welfare 2019 and pupils 2015), by the authority's name in the Interior Ministry list.
ALIAS = {"באקה אל-גרביה": ["באקה אל-גרביה - גת"], "בוסתן אל-מרג'": ["בוסתאן אל-מרג'", "בוסתאן אל מרג"], "בוקעאתא": ["בוקעתא", "בוקעאתה"],
         "בית אריה-עופרים": ["בית אריה"], "בסמת טבעון": ["בשמת טבעון"], "ג'סר א-זרקא": ["ג'סר אל זרקא"], "ג'ש (גוש חלב)": ["גוש-חלב", "גוש חלב"],
         "דרום השרון": ["דרום השרון - רמות השבים"], "חוף הכרמל": ["חוף הכרמל - עתלית"], "חצור הגלילית": ["חצור"], "טירת כרמל": ["טירת הכרמל"],
         "יהוד-מונוסון": ["יהוד - נווה  אפרים", "יהוד נווה אפרים"], "יקנעם עילית": ["יוקנעם"], "יאנוח-ג'ת": ["ינוח - ג'ת", '"ינוח-ג\'ת"'],
         "כאוכב אבו אל-היג'א": ["כאוכב אל היג'", '"כאוכב אבו אל-ה'], "כסיפה": ["כסייפא"], "כעביה-טבאש-חג'אג'רה": ["כעביה-טבאש", "כעביה-טבאש*"],
         "כאבול": ["מ.מ  כאבול"], "מג'דל שמס": ["מג'ד אל שאמס"], "מגילות ים המלח": ["מגילות"], "ג'דיידה-מכר": ["מכאר-ג'דידה"], "מעיליא": ["מעיליה"],
         "מעלה עירון": ["מעלה עירון / זלפה"], "סאג'ור": ["סג'ור", "שגור"], "עספיא": ["עוספיה"], "עין קנייא": ["עין קיניה", "עין קניה"],
         "ערערה-בנגב": ["ערערה- הנגב"], "פסוטה": ["פאסוטה"], "רמת נגב": ["רמת הנגב"], "שדות נגב": ["שדות הנגב", "שדות נגב עזתה"], "תל אביב -יפו": ["תל אביב"],
         "בועיינה-נוג'ידאת": ['"בעיינה-נג\'יידא'], "אפרת": ["אפרתה"], "בנימינה-גבעת עדה": ["בנימינה גבעת עד"], "ערבות הירדן": ["בקעת הירדן"],
         "כפר כמא": ["כפר קמא"], "מודיעין-מכבים-רעות": ["מודיעין מכבים ר"], "נוף הגליל": ["נצרת עילית"], "שדות דן": ["עמק לוד"],
         "פקיעין (בוקייעה)": ["פקיעין - בוקייע"], "קדימה-צורן": ["צורן קדימה"]}

# English names the locality list cuts off at 20 characters, or spells unusually.
EN_FIX = {"Modi'in-Makkabbim-Re": "Modi'in-Makkabbim-Re'ut", "Kochav Yair Tsur Yi": "Kokhav Yair-Tzur Yigal", "Ka'abiyye-Tabbash-Ha": "Ka'abiyye-Tabbash-Hajajre",
          "Bi Ne": "Bi'ine", "Jish(Gush Halav)": "Jish (Gush Halav)", "Elat": "Eilat", "al-Qasoum": "Al-Kasom", "Brener": "Brenner"}


def key(t):
    return re.sub(r"\b(חלק|part)\s*['א-ת\d]+|\(\d\)", "", t).strip()


def main(dirs):
    os.makedirs(OUT, exist_ok=True)
    auth = list(csv.DictReader(open(find(dirs, "il_authorities.csv"), encoding="utf-8-sig")))
    # Census 2022 and the Population Registry, by locality; localities' regional council
    rec = lambda f: json.load(open(find(dirs, f), encoding="utf-8"))["result"]["records"]
    num = lambda v: int(str(v).replace(",", "").strip() or 0) if v not in (None, "") else 0
    sub = {int(l["סמל_ישוב"]): int(l["סמל_נפה"] or 0) for l in rec("il_localities.json")}
    loc_rc = {int(l["סמל_ישוב"]): norm(l["שם_מועצה"]) for l in rec("il_localities.json") if int(l["סמל_מועצה_איזורית"] or 0)}
    c22 = {int(r["LocalityCode"]): num(r["Total_Population"]) for r in rec("il_census22_pop_households.json") if r["LocalityCode"]}
    loc_en = {int(l["city_code"]): l["city_name_en"].strip() for l in rec("il_localities_en.json") if l.get("city_name_en")}
    reg = {int(r["סמל_ישוב"]): r for r in rec("il_residents_age_current.json") if int(r["סמל_ישוב"] or 0)}
    reg_rc = {}
    for c, r in reg.items():
        if int(r["קוד_מועצה_אזורית"] or 0): reg_rc.setdefault(norm(r["מועצה_אזורית"]), []).append(c)
    # Welfare 2019 (cp1255), by name
    w = {}
    for r in list(csv.reader(open(find(dirs, "il_welfare_by_authority.csv"), encoding="cp1255")))[1:]:
        if r[0] == "2019": w[norm(r[2])] = {"welfare": num(r[4]), "cluster": num(r[3])}
    # Pupils 2015 by authority name
    ws = openpyxl.load_workbook(find(dirs, "il_mosdot.xlsx"), read_only=True).worksheets[0]
    it = ws.iter_rows(values_only=True); h = next(it); I = {k: i for i, k in enumerate(h)}
    pup = {}
    for r in it:
        if r[0] != 2015 or r[I["סוג מסגרת אירגונית"]] == "גן ילדים": continue
        n = r[I["סהכ תלמידים במוסד"]] or 0
        p = pup.setdefault(norm(r[I["שם רשות"]]), [0, 0]); p[0] += n
        if r[I["מעמד משפטי"]] == "רשמי": p[1] += n
    # Borders
    osm = json.load(open(find(dirs, "il_osm_admin.geojson"), encoding="utf-8"))["features"]
    osm8 = [f for f in osm if f["properties"]["admin_level"] == "8"]
    idx = {}
    for f in osm8:
        for k in ("name", "name:he", "official_name"):
            n = norm(f["properties"].get(k))
            if n: idx.setdefault(n, f); idx.setdefault(n.lstrip("ה"), f)
    en = {f["properties"].get("name:en"): f for f in osm8 if f["properties"].get("name:en")}
    yt = {x["code"]: x for x in json.load(open(find(dirs, "il_yt.json"), encoding="utf-8"))}
    data, feats, miss = {}, [], {}
    for a in auth:
        name, code, kind = a["LocalAuthorityName"].strip(), a["LocalAuthorityCode"], a["LocalAuthorityType"]
        n = norm(name); rc = kind == "מועצה אזורית"
        x = {"name": name, "kind": KIND[kind], "district": DISTRICT.get(a["LocalAuthorityDistrict"], ""), "long": a["LocalAuthorityLongName"]}
        alts = [n, n.lstrip("ה")] + [norm(v) for v in ALIAS.get(name, [])]
        locs = [c for c, r in loc_rc.items() if r in alts] if rc else [int(code)]
        rlocs = next((reg_rc[k] for k in alts if k in reg_rc), []) if rc else [int(code)]
        # District from the localities' subdistrict (CBS codes: 1x Jerusalem, 2x Northern, 3x Haifa, 4x Central, 5x Tel Aviv,
        # 6x Southern, 7x West Bank); the authority list's own district column has errors (it puts Akko in the West Bank).
        subs = [sub[c] // 10 for c in locs if sub.get(c)]
        if subs: x["district"] = SUBDISTRICT[max(set(subs), key=subs.count)]
        elif name == "מגדל תפן": x["district"] = "Northern District"   # an industrial council with no residents (in Akko subdistrict)
        if any(c in c22 for c in locs): x["pop22"] = sum(c22.get(c, 0) for c in locs)
        rr = [reg[c] for c in rlocs if c in reg]
        if rr:
            x["pop"] = sum(num(r["סהכ"]) for r in rr); x["age0_5"] = sum(num(r["גיל_0_5"]) for r in rr); x["age6_18"] = sum(num(r["גיל_6_18"]) for r in rr)
        wv = next((w[k] for k in alts if k in w), None)
        if wv: x.update(wv)
        pv = next((pup[k] for k in alts if k in pup), None)
        if pv: x["pupils"], x["public"] = pv
        f = idx.get(n) or idx.get(n.lstrip("ה")) or en.get(OSM_EN.get(name))
        if f:
            g = shape(f["geometry"]).buffer(0).simplify(0.0008, preserve_topology=True)
            feats.append({"type": "Feature", "properties": {"id": f"ISR-{code}", "NAME": name}, "geometry": {"type": g.geom_type, "coordinates": rnd(mapping(g)["coordinates"])}})
            x["area_km2"] = None
        e = loc_en.get(int(code)) if not rc else None
        e = re.sub(r"[^\s\-()]+", lambda m: m.group(0).capitalize(), re.sub(r"\s+", " ", e)) if e else None
        if not e and f: e = re.sub(r"\s*(Regional|Local) Council$", "", f["properties"].get("name:en") or "").strip() or None
        x["en"] = EN_FIX.get(e, e) or ""
        y = yt.get(code) or {}
        ch = y.get("channel") or ""
        if ch and OFFICIAL.search(ch) and not NOT_OFFICIAL.search(ch):
            m = [v["t"] for v in y.get("vids") or [] if MEET.search(v["t"]) and not NOT_MEET.search(v["t"])]
            e = [v["t"] for v in y.get("vids") or [] if EDU.search(v["t"]) and "כנסת" not in v["t"]]
            keys = {parse_date(t) or key(t) for t in m}
            if keys: x["meetings"] = {"n": len(keys), "edu": len(e), "source": y["url"], "channel": ch, "titles": m}
        for k in ("pop22", "pop", "welfare", "pupils"):
            if k not in x: miss.setdefault(k, []).append(name)
        if not f: miss.setdefault("border", []).append(name)
        data[code] = x
    json.dump(data, open(os.path.join(OUT, "il_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "il_auth.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(len(data), "authorities;", len(feats), "borders;", sum(1 for x in data.values() if x.get("meetings")), "with meetings")
    for k, v in miss.items(): print("missing", k, len(v), v)


if __name__ == "__main__":
    main(sys.argv[1:])
