"""Count recorded education-committee meetings that Nordic and Dutch municipalities post on YouTube.

For each municipality in docs/data/{country}.csv: search YouTube once for its council meetings, keep a
channel whose name has the municipality's name and a word like "kommune" or "gemeente", list its
videos and count titles naming a meeting (committee, council) about schools, education or children
in that country's language. Also records every meeting video found, for the notes.
Usage: python3 nordic_youtube.py OUTDIR [CC ...]   (writes OUTDIR/{cc}_youtube.csv, one thread per country)
"""
import csv, json, os, re, subprocess, sys, threading, time, unicodedata

TR = str.maketrans({"ø": "o", "Ø": "o", "æ": "ae", "Æ": "ae", "đ": "d", "ŋ": "n", "ŧ": "t", "þ": "th", "Þ": "th", "ð": "d", "Ð": "d"})
C = {
    "NO": dict(file="norway", q="{} kommune kommunestyre møte", chan=r"kommune|kommunestyre|kommunestyret|kommunal|politikk",
               edu=r"oppvekst|skole|utdanning|barn og unge|levek[aå]r|kultur og oppvekst|helse og oppvekst",
               meet=r"utvalg|komit[eé]|m[øo]te|hovedutvalg|styre"),
    "SE": dict(file="sweden", q="{} kommun sammanträde", chan=r"kommun|kommunfullm[aä]ktige|fullm[aä]ktige",
               edu=r"utbildning|skol|barn- och|barn och|bildning|f[oö]rskol|gymnasie",
               meet=r"n[aä]mnd|sammantr[aä]de|m[oö]te|utskott"),
    "FI": dict(file="finland", q="{} kunta valtuusto kokous", chan=r"kunta|kaupunki|kommun|stad|valtuusto",
               edu=r"sivistys|koulu|opetus|kasvatus|lasten ja nuorten|bildning|skol",
               meet=r"lautakunta|kokous|valiokunta|jaosto|n[aä]mnd|sammantr[aä]de|m[oö]te"),
    "DK": dict(file="denmark", q="{} kommune byrådsmøde", chan=r"kommune|byr[aå]d|kommunalbestyrelse",
               edu=r"b[øo]rn|skole|uddannelse|unge|dagtilbud",
               meet=r"udvalg|m[øo]de|byr[aå]d"),
    # Iceland: councils (bæjarstjórn, sveitarstjórn, borgarstjórn) and education committees (fræðsluráð, skólanefnd).
    "IS": dict(file="iceland", q="{} bæjarstjórnarfundur", chan=r"b[æa]r|borg|hreppur|sveitarf[ée]lag|bygg[dð]|kaupsta[dð]|stj[óo]rn",
               edu=r"fr[æa]ðslu|sk[óo]la|mennta|fr[íi]stund", meet=r"fund|stj[óo]rn|nefnd|r[áa]ð"),
    # Germany: district councils (Kreistag) and city councils, and their school committees (Schulausschuss).
    "DE": dict(file="germany", q="{} Kreistag Sitzung", chan=r"kreis|stadt|kreistag|landratsamt|rat\b|region|städteregion|bürgerschaft|abgeordnetenhaus",
               edu=r"schul|bildung", meet=r"ausschuss|sitzung|kreistag|stadtrat|ratssitzung|stadtverordnet|bürgerschaft"),
    "NL": dict(file="netherlands", q="gemeente {} raadsvergadering", chan=r"gemeente|gemeenteraad|raad|griffie",
               edu=r"onderwijs|jeugd|school|kind",
               meet=r"commissie|raad|vergadering|beeldvorm|oordeelvorm"),
}
GENERIC = set("kommune kommun kunta kaupunki stad gemeente municipality the og och ja en de het city district stadt kreis landkreis".split())
ANY_MEET = {cc: re.compile(c["meet"], re.I) for cc, c in C.items()}


def words(s):
    s = unicodedata.normalize("NFKD", str(s).translate(TR)).encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z]+", s)


def ytdlp(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-200:])
    return json.loads(r.stdout)


ALIAS = {"'s-Gravenhage": "Den Haag", "'s-Hertogenbosch": "Den Bosch"}


def names(name):
    """Every spelling: Norway's Sami/Norwegian pairs ("Aarborte/Hattfjelldal") and Dutch short names."""
    base = re.sub(r"\s*\(.*?\)", "", ALIAS.get(name, name))
    return [p.strip() for p in re.split(r"/| - ", base) if p.strip()]


IS_SUFFIX = r"(urborg|borg|arkaupsta[dð]ur|kaupsta[dð]ur|arb[æa]r|sb[æa]r|b[æa]r|hreppur|sveitarf[ée]lag|bygg[dð])$"


def is_channel_for(cc, name, channel):
    if not re.search(C[cc]["chan"], channel, re.I):
        return False
    have = words(channel)
    if cc == "IS":   # "Hafnarfjarðarkaupstaður" posts as "Hafnarfjarðarbær": compare the stem before the suffix
        main = [w for w in name.split() if not re.match(r"sveitarf[ée]lag", w, re.I)] or name.split()
        stem = words(re.sub(IS_SUFFIX, "", main[0], flags=re.I))
        stem = stem[0] if stem else ""
        if len(stem) < 4:   # "Árborg": the suffix is most of the name, so match the whole word
            whole = words(main[0])
            return bool(whole) and whole[0] in have
        return any(h.startswith(stem[:max(4, len(stem) - 1)]) for h in have)
    for n in names(name):
        want = [w for w in words(n) if w not in GENERIC] or words(n)
        # "Københavns Kommune" matches "København"; Finnish channels use the genitive ("Helsingin kaupunki").
        ok = lambda w: any(h == w or h == w + "s" or (cc == "FI" and len(h) <= len(w) + 4 and h[:max(3, len(w) - 3)] == w[:max(3, len(w) - 3)]) for h in have)
        if all(ok(w) for w in want):
            return True
    return False


def run(cc, outdir):
    c = C[cc]
    rows = list(csv.DictReader(open(f"{os.environ.get('NORDIC_DATA', 'docs/data')}/{c['file']}.csv", encoding="utf-8")))
    edu, meet = re.compile(c["edu"], re.I), ANY_MEET[cc]
    seen = {}
    with open(f"{outdir}/{cc}_youtube.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["District ID", "District", "Channel", "Channel URL", "Meetings", "All meeting videos", "Example titles", "Error"])
        for r in rows:
            name = r["District"]
            out = [r["District ID"], name, "", "", "", "", "", ""]
            try:
                chans = {}
                for q in [c["q"]] + [x for x in os.environ.get(f"EXTRA_Q_{cc}", "").split("|") if x]:
                    for e in ytdlp(f"ytsearch15:{q.format(' '.join(names(name)))}").get("entries") or []:
                        if e.get("channel_url") and e.get("channel"):
                            chans[e["channel_url"]] = e["channel"]
                exact = lambda ch: any(all(w in words(ch) for w in words(n)) for n in names(name))
                pick = sorted([(u, ch) for u, ch in chans.items() if is_channel_for(cc, name, ch)], key=lambda x: not exact(x[1]))
                if pick:
                    url, chan = pick[0]
                    if url not in seen:
                        vids = []
                        for tab in ("/videos", "/streams"):
                            try:
                                vids += [v.get("title") or "" for v in ytdlp(url + tab).get("entries") or []]
                            except RuntimeError:
                                pass
                            time.sleep(1)
                        m = [v for v in vids if meet.search(v)]
                        t = [v for v in m if edu.search(v)]
                        uniq = {re.sub(r"\b(del|osa|deel|part)\s*\d+\b|\(\d\)", "", v, flags=re.I).strip().lower() for v in t}
                        seen[url] = (len(uniq), len(m), t[:3])
                        TITLES[url] = vids
                    n, nm, ex = seen[url]
                    out[2:7] = [chan, url, n, nm, " / ".join(ex)]
            except Exception as e:
                out[7] = str(e)[:200]
                if "Sign in to confirm" in str(e):
                    w.writerow(out); print(cc, "YouTube asked to sign in; stopping.", flush=True); return
            w.writerow(out); f.flush()
            print(cc, name, "->", out[2], out[4], flush=True)
            time.sleep(1.5)


TITLES = {}   # channel URL -> every video title, for a strict recount (written to OUTDIR/titles.json)

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    ts = [threading.Thread(target=run, args=(cc, outdir)) for cc in (sys.argv[2:] or list(C))]
    [t.start() for t in ts]; [t.join() for t in ts]
    json.dump(TITLES, open(os.path.join(outdir, "titles.json"), "w", encoding="utf-8"), ensure_ascii=False)
