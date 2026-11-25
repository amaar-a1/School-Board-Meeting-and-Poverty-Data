"""Turns the Taiwan downloads (made on GitHub's runner) into the small inputs build_latam.taiwan() reads
(data-prep/inputs/taiwan/).

- tw_geo.geojson: the 22 special municipalities, counties and cities, from geoBoundaries gbOpen TWN ADM1 (simplified).
- tw_data.json, per county or city:
  low, low_ratio, midlow: Ministry of Health and Welfare, Department of Statistics, tables 1.1.1 (low-income households
    and persons, with persons as a share of the population, and the population it uses) and 1.1.5 (middle-low-income households and persons),
    latest quarter;
  pupils, public: Ministry of Education, Department of Statistics open data, school year 2025/26 (114): elementary schools
    (edu_B_3_2), junior high schools (edu_B_3_8) and senior high schools (edu_B_4_2) by county, all and public.
  meetings: the county or city council's YouTube channel (fetch/tw_yt.py).
Then, after build_latam.py, run data-prep/simplify_borders.sh (a lighter copy of the map file for zoomed-out views).
History (python3 data-prep/prep_taiwan.py --history RAWDIR): the same stand-in at the end of each year from 2018 (the
fourth quarter of each yearly sheet of tables 1.1.1 and 1.1.5; table 1.1.5's sheets before 2018 are laid out
differently), with the population the low-income table's rate implies (persons / rate), into tw_data.json's pov_years.
Usage: python3 data-prep/prep_taiwan.py RAWDIR [RAWDIR ...] GEODIR
"""
import csv, glob, io, json, os, re, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "taiwan")
# Chinese name -> (English name, geoBoundaries name, ID, kind)
TW = {"臺北市": ("Taipei City", "Taipei", "63000", "Special municipality"), "新北市": ("New Taipei City", "New Taipei", "65000", "Special municipality"),
      "桃園市": ("Taoyuan City", "Taoyuan", "68000", "Special municipality"), "臺中市": ("Taichung City", "Taichung", "66000", "Special municipality"),
      "臺南市": ("Tainan City", "Tainan", "67000", "Special municipality"), "高雄市": ("Kaohsiung City", "Kaohsiung", "64000", "Special municipality"),
      "基隆市": ("Keelung City", "Keelung", "10017", "City"), "新竹市": ("Hsinchu City", "Hsinchu", "10018", "City"), "嘉義市": ("Chiayi City", "Chiayi", "10020", "City"),
      "新竹縣": ("Hsinchu County", "Hsinchu County", "10004", "County"), "苗栗縣": ("Miaoli County", "Miaoli County", "10005", "County"),
      "彰化縣": ("Changhua County", "Changhua County", "10007", "County"), "南投縣": ("Nantou County", "Nantou County", "10008", "County"),
      "雲林縣": ("Yunlin County", "Yunlin County", "10009", "County"), "嘉義縣": ("Chiayi County", "Chiayi County", "10010", "County"),
      "屏東縣": ("Pingtung County", "Pingtung County", "10013", "County"), "宜蘭縣": ("Yilan County", "Yilan County", "10002", "County"),
      "花蓮縣": ("Hualien County", "Hualien County", "10015", "County"), "臺東縣": ("Taitung County", "Taitung County", "10014", "County"),
      "澎湖縣": ("Penghu County", "Penghu", "10016", "County"), "金門縣": ("Kinmen County", "Kinmen", "09020", "County"),
      "連江縣": ("Lienchiang County (Matsu)", "Matsu Islands", "09007", "County")}


def find(dirs, name):
    return sorted(f for d in dirs for f in glob.glob(os.path.join(d, "**", name), recursive=True))[-1]


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def latest_block(path, sheet="2026"):
    """The last quarter with figures in a MOHW quarterly sheet: {county: row values}."""
    rows = list(openpyxl.load_workbook(path, read_only=True, data_only=True)[sheet].iter_rows(values_only=True))
    starts = [i for i, r in enumerate(rows) if r and any(isinstance(x, str) and "季底" in x for x in r)]
    for s in reversed(starts):
        block = {}
        for r in rows[s + 1:s + 32]:
            k = str(r[0] or "").strip()
            if k in TW and isinstance(r[2], (int, float)): block[k] = r
        if len(block) == 22:
            return [x for x in rows[s] if x][0].strip(), block
    raise ValueError("no complete quarter")


def edu(dirs, fn, total, public, private=None):
    rr = list(csv.reader(io.StringIO(open(find(dirs, fn), encoding="utf-8-sig").read())))
    h = rr[0]; last = max(r[0] for r in rr[1:])
    out = {}
    for r in rr[1:]:
        if r[0] != last: continue
        k = r[1].replace("台", "臺")
        if k not in TW: continue
        pub = int(r[h.index(public)]); tot = int(r[h.index(total)]) if total else pub + int(r[h.index(private)])
        out[k] = (tot, pub)
    return last, out


# Council sittings and committee meetings, not news clips, tours, ceremonies or third-party channels.
SIT = re.compile(r"(第\s*\d+\s*(屆)?)?第?\s*\d+\s*次\s*(定期|臨時)(大)?會|定期大會|臨時會|總質詢|業務(報告|質詢)|大會議事|大會議程|審查(會議|委員會)|第\s*\d+\s*次會議")
EDU = re.compile(r"教育[^，,]{0,6}(委員會|部門|審查)|(民政|文化)教育委員會|教育文化委員會")
NOT = re.compile(r"新聞|專訪|記者會|典禮|活動|簡介|拜年|盃|參訪|視察|勘查|外勘|導覽|宣誓|演哪齣")
NOT_CHANNELS = {"UC0ulQyhkXJ1UgKN06mGPqdw", "UC9Vixsg2lS0RRiKvUXLJeRg"}   # "議會演哪齣？": a civic group's recordings, not the councils'


def roc_date(t):
    """An ISO date from a title: ROC years (115 = 2026) as 115年9月11日, 1150911, 115.09.11 or 115-09-16; or 2026.06.03 / 20261006."""
    m = re.search(r"(1[01]\d)\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", t) or re.search(r"(?<!\d)(1[01]\d)\s*[.\-/ ]\s*(\d{1,2})\s*[.\-/ ]\s*(\d{1,2})(?!\d)", t) \
        or re.search(r"(?<!\d)(1[01]\d)(\d{2})(\d{2})(?!\d)", t)
    if m:
        y, mo, d = int(m.group(1)) + 1911, int(m.group(2)), int(m.group(3))
    else:
        m = re.search(r"(20\d\d)\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", t) or re.search(r"(?<!\d)(20\d\d)[.\-/]?(\d{2})[.\-/]?(\d{2})(?!\d)", t)
        if not m: return None
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 and 2000 <= y <= 2030 else None


def meetings(dirs):
    f = find(dirs, "tw_meet.json")
    if not f: return {}
    out = {}
    for c, x in json.load(open(f, encoding="utf-8")).items():
        if not x.get("url") or x["url"].rsplit("/", 1)[-1] in NOT_CHANNELS: continue
        vids = [t for t in x["videos"] if not NOT.search(t)]
        # An undated title counts only when it names a numbered meeting or an agenda (Nantou's undated titles are news about sittings).
        vids = [t for t in vids if roc_date(t) or re.search(r"第\s*\d+\s*次會議|議程", t)]
        keyed = lambda ts: {(roc_date(t) or re.sub(r"[\s（(]*(上午|下午|PM|AM|\d)[)）]?$", "", t)): (f"{roc_date(t)} " if roc_date(t) else "") + t for t in ts}
        edu = keyed([t for t in vids if EDU.search(t)])
        sit = keyed([t for t in vids if SIT.search(t)])
        if len(edu) >= 3: out[c] = {"n": len(edu), "type": "Council education committee", "source": x["url"], "channel": x["channel"], "titles": list(edu.values())}
        elif sit: out[c] = {"n": len(sit), "type": "Council sittings (stand-in)", "source": x["url"], "channel": x["channel"], "titles": list(sit.values())}
    return out


def main(*args):
    *dirs, geo = args
    os.makedirs(OUT, exist_ok=True)
    when, low = latest_block(find(dirs, "tw_lowincome_111.xlsx"))
    _, mid = latest_block(find(dirs, "tw_midlow_115.xlsx"))
    y1, el = edu(dirs, "tw_edu_B_3_2.csv", "學生數", "公立學生數")
    y2, jh = edu(dirs, "tw_edu_B_3_8.csv", "學生總數", "公立學生數")
    y3, sh = edu(dirs, "tw_edu_B_4_2.csv", None, "公立學生數[人]", "私立學生數[人]")
    assert y1 == y2 == y3 and len(el) == len(jh) == len(sh) == 22, (y1, y2, y3, len(el), len(jh), len(sh))
    meet = meetings(dirs)
    data = {}
    for k, (en, gb, code, kind) in TW.items():
        r = low[k]
        persons, ratio, pop = r[5], r[27], r[30]   # persons; persons as % of the population; the population it uses
        data[k] = {"en": en, "kind": kind, "code": code, "low": persons, "low_ratio": ratio, "pop": pop,
                   "midlow": mid[k][5], "pupils": el[k][0] + jh[k][0] + sh[k][0], "public": el[k][1] + jh[k][1] + sh[k][1],
                   "quarter": when, "school_year": y1, **({"meetings": meet[k]} if k in meet else {})}
    g = json.load(open(os.path.join(geo, "geoBoundaries-TWN-ADM1_simplified.geojson"), encoding="utf-8"))["features"]
    by = {f["properties"]["shapeName"]: f for f in g}
    feats = [{"type": "Feature", "properties": {"id": "TWN-" + v[2], "NAME": v[0]}, "geometry": {"type": by[v[1]]["geometry"]["type"], "coordinates": rnd(by[v[1]]["geometry"]["coordinates"])}} for v in TW.values()]
    json.dump(data, open(os.path.join(OUT, "tw_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "tw_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for k, x in data.items(): print((x.get("meetings") or {}).get("type"), (x.get("meetings") or {}).get("n"), x["en"], x["pop"], x["low_ratio"], round(100 * (x["low"] + x["midlow"]) / x["pop"], 2), x["pupils"], round(100 * x["public"] / x["pupils"], 1))
    print(when, y1, sum(x["pop"] for x in data.values()))


def history(raw):
    import openpyxl as ox
    lowf, midf = find([raw], "tw_lowincome_111.xlsx"), find([raw], "tw_midlow_115.xlsx")
    p = os.path.join(OUT, "tw_data.json"); data = json.load(open(p, encoding="utf-8"))
    for y in [str(y) for y in range(2018, 2026)]:
        w1, low = latest_block(lowf, y); w2, mid = latest_block(midf, y)
        assert "第4季" in w1 and "第4季" in w2, (y, w1, w2)
        for k, x in data.items():
            pop = low[k][5] * 100 / low[k][27]
            x.setdefault("pov_years", {})[y] = round(100 * (low[k][5] + mid[k][5]) / pop, 2)
    for k, x in data.items():   # the site's own figure, the latest quarter
        x["pov_years"][x["quarter"].split(",")[-1].split()[0]] = round(100 * (x["low"] + x["midlow"]) / x["pop"], 2)
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({x["en"]: x["pov_years"] for x in list(data.values())[:2]})


if __name__ == "__main__" and sys.argv[1] == "--history":
    history(sys.argv[2])
elif __name__ == "__main__":
    main(*sys.argv[1:])
