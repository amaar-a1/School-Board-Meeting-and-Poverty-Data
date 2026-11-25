"""Monthly data refresh (run by .github/workflows/refresh-monthly.yml; can be run by hand too).

1. Malaysia: downloads DOSM's and the Ministry of Education's latest open data (OpenDOSM, data.gov.my), reruns
   prep_malaysia.py and the build. New years of poverty, population and enrollment are added as they're published.
2. Czechia: adds the newest December of MPSV's unemployment in municipalities, if there's one newer than the site's,
   to each municipality's figure and history.
3. US: adds the Census Bureau's newest SAIPE school district file (published each December) to the poverty history
   (prep_us_poverty_history.py's file); the main US figures stay with the daily build's file.
4. Meetings: lists again the videos of the council and board channels already found on YouTube, oldest-checked
   first, up to MAX_CHANNELS a run, adding new titles (old ones are kept, in case a channel hides videos), then
   rebuilds those countries.
Every rebuilt country is checked before it's kept: the same number of places, and no more than a fifth fewer meetings
found in all; otherwise its previous file is put back. Map border files are never changed here.
Usage: python3 data-prep/refresh_monthly.py [--no-youtube] [--max-channels N]
"""
import csv, datetime, glob, gzip, json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs", "data")
IN = os.path.join(HERE, "inputs")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
MAX_CHANNELS = int(sys.argv[sys.argv.index("--max-channels") + 1]) if "--max-channels" in sys.argv else 2400
DEADLINE = time.time() + float(os.environ.get("REFRESH_SECONDS", 4.5 * 3600))
log = lambda *a: print(*a, flush=True)


def fetch(url, path, timeout=300):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        open(path, "wb").write(b)
        return True
    except Exception as e:
        log("  couldn't download", url, e)
        return False


def snapshot(keys):
    """The current CSVs of these countries, to put back if a rebuild looks wrong."""
    return {k: open(os.path.join(DOCS, f"{k}.csv"), encoding="utf-8").read() for k in keys if os.path.exists(os.path.join(DOCS, f"{k}.csv"))}


def check(before):
    """Keep a rebuilt country only if it has as many places and at least four fifths of its meetings."""
    for k, old in before.items():
        p = os.path.join(DOCS, f"{k}.csv")
        o = list(csv.DictReader(old.splitlines()))
        n = list(csv.DictReader(open(p, encoding="utf-8")))
        meet = lambda rows: sum(int(float(r.get("Available Board Meetings") or 0)) for r in rows)
        if len(n) != len(o) or meet(n) < 0.8 * meet(o):
            log(f"  {k}: rebuilt file failed the check ({len(o)}->{len(n)} places, {meet(o)}->{meet(n)} meetings); keeping the old one")
            open(p, "w", encoding="utf-8").write(old)
        else:
            log(f"  {k}: {len(n)} places, meetings {meet(o)} -> {meet(n)}")


def build(keys):
    if keys:
        subprocess.run([sys.executable, os.path.join(HERE, "build_latam.py"), *keys], check=False)


def malaysia():
    log("Malaysia: OpenDOSM and data.gov.my")
    raw = tempfile.mkdtemp()
    ok = all([fetch("https://storage.dosm.gov.my/hies/hh_poverty_district.csv", f"{raw}/my_hh_poverty_district.csv"),
              fetch("https://storage.dosm.gov.my/hies/hies_district.csv", f"{raw}/my_hies_district.csv"),
              fetch("https://storage.dosm.gov.my/hies/hies_state.csv", f"{raw}/my_hies_state.csv"),
              fetch("https://storage.dosm.gov.my/population/population_district.csv", f"{raw}/my_pop_district.csv"),
              fetch("https://api.data.gov.my/data-catalogue?id=enrolment_school_district&limit=100000", f"{raw}/my_enrol.json"),
              fetch("https://raw.githubusercontent.com/dosm-malaysia/data-open/main/datasets/geodata/administrative_2_district.geojson", f"{raw}/my_district.geojson")])
    if not ok:
        return []
    before = json.load(open(os.path.join(IN, "malaysia", "my_data.json"), encoding="utf-8"))
    r = subprocess.run([sys.executable, os.path.join(HERE, "prep_malaysia.py"), raw], capture_output=True, text=True)
    log(r.stdout[-400:], r.stderr[-400:])
    after = json.load(open(os.path.join(IN, "malaysia", "my_data.json"), encoding="utf-8"))
    if r.returncode or len(after) != len(before):
        json.dump(before, open(os.path.join(IN, "malaysia", "my_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        log("  Malaysia: the new files didn't match; kept the old data")
        return []
    shutil.rmtree(raw, ignore_errors=True)
    return ["malaysia"]


def czechia():
    p = os.path.join(IN, "czechia", "cze_data.json")
    data = json.load(open(p, encoding="utf-8"))
    have = max((int(y) for x in data.values() for y in (x.get("unemp_years") or {})), default=2024)
    year = datetime.date.today().year - 1   # December of last year is the newest full year
    if year <= have:
        log(f"Czechia: newest December is {have}; nothing newer yet")
        return []
    raw = tempfile.mkdtemp()
    f = f"{raw}/u.json.gz"
    if not fetch(f"https://data.mpsv.cz/od/soubory/nezamestnanost-v-obcich/nezamestnanost-v-obcich-12-{year}.json.gz", f):
        return []
    rows = {x["obec"].split("/")[1]: x for x in json.loads(gzip.decompress(open(f, "rb").read()))["polozky"]}
    n = 0
    for did, x in data.items():
        u = rows.get(did.split("-")[1])
        if not u: continue
        x.update({"unemp": u["podilNezamestnanychOsob"], "jobseekers": u["dosazitelniUchazeci"], "pop15_64": u["obyvatelstvo15_64"], "unemp_year": year})
        x.setdefault("unemp_years", {})[str(year)] = round(u["podilNezamestnanychOsob"], 1)
        n += 1
    if n < 0.95 * len(data):
        log(f"Czechia: December {year} covers only {n} municipalities; skipped")
        return []
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    log(f"Czechia: added December {year} for {n} municipalities")
    return ["czechia"]


def us_history():
    p = os.path.join(IN, "us_poverty_history.json")
    hist = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    have = max((int(y) for v in hist.values() for y in v), default=2024)
    year = have + 1
    raw = tempfile.mkdtemp()
    yy = str(year)[2:]
    base = f"https://www2.census.gov/programs-surveys/saipe/datasets/{year}/{year}-school-districts/ussd{yy}"
    if fetch(base + ".csv", f"{raw}/u.csv", timeout=120):
        rows = list(csv.DictReader(open(f"{raw}/u.csv", encoding="latin-1")))
        kids, poor = f"rpop5_17v_{yy}", f"saepov5_17rv_{yy}"
        n = 0
        for r in rows:
            k = int(r.get(kids) or 0)
            if k > 0:
                hist.setdefault(r["state"].zfill(2) + r["distid"].zfill(5), {})[str(year)] = round(100 * int(r[poor]) / k, 1); n += 1
        if n > 10000:
            json.dump(hist, open(p, "w"), separators=(",", ":"))
            log(f"US: added SAIPE {year} for {n} districts (the daily build adds it to the site)")
            return
    log(f"US: no SAIPE {year} school district file yet")


def ytdlp(url):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", url], capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-160:])
    return [e.get("title") or "" for e in json.loads(r.stdout).get("entries") or []]


def youtube():
    """Relist the channels already found, oldest-checked first; returns the countries whose titles changed."""
    state_p = os.path.join(IN, "youtube_refreshed.json")
    state = json.load(open(state_p, encoding="utf-8")) if os.path.exists(state_p) else {}
    sys.path.insert(0, HERE)
    import build_latam
    chans = {}   # url -> (country folder, titles file)
    for d in sorted(set(build_latam.DIRS.values())):
        yd = os.path.join(IN, d, "youtube")
        if not os.path.isdir(yd): continue
        tfiles = sorted(glob.glob(os.path.join(yd, "titles*.json")))
        where = {}
        for tf in tfiles:
            for u in json.load(open(tf, encoding="utf-8")): where.setdefault(u, tf)
        for f in glob.glob(os.path.join(yd, "*_youtube.csv")):
            for r in csv.DictReader(open(f, encoding="utf-8")):
                u = r.get("Channel URL")
                if u and u in where: chans.setdefault(u, (d, where[u]))
    todo = sorted(chans, key=lambda u: state.get(u, ""))[:MAX_CHANNELS]
    log(f"YouTube: {len(chans)} channels known; relisting {len(todo)}")
    found = {}
    def one(u):
        if time.time() > DEADLINE: return u, None
        try:
            v = []
            for tab in ("/videos", "/streams"):
                try: v += ytdlp(u + tab)
                except RuntimeError: pass
            time.sleep(1)
            return u, v
        except Exception:
            return u, None
    with ThreadPoolExecutor(3) as ex:
        for u, v in ex.map(one, todo):
            if v is not None:
                found[u] = v; state[u] = datetime.date.today().isoformat()
    changed = set()
    byfile = {}
    for u, v in found.items():
        byfile.setdefault(chans[u][1], []).append((u, v))
    for tf, items in byfile.items():
        t = json.load(open(tf, encoding="utf-8"))
        for u, v in items:
            old = t.get(u, [])
            new = v + [x for x in old if x not in set(v)]
            if new != old: t[u] = new; changed.add(chans[u][0])
        json.dump(t, open(tf, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(state, open(state_p, "w", encoding="utf-8"), indent=0)
    log(f"YouTube: relisted {len(found)}; new titles in {sorted(changed)}")
    return sorted(changed)


def main():
    keys = malaysia() + czechia()
    us_history()
    if "--no-youtube" not in sys.argv:
        keys += [k for k in youtube() if k not in keys]
    before = snapshot(keys)
    build(keys)
    subprocess.run([sys.executable, os.path.join(HERE, "estimate_enrollment.py"), *[f"{k}.csv" for k in keys]], check=False)
    if keys: subprocess.run([sys.executable, os.path.join(HERE, "population_history.py"), "apply"], check=False)
    check(before)
    log("Refreshed:", keys or "nothing")


if __name__ == "__main__":
    main()
