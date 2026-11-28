# Round 68: US school boards' meetings before 2025. CivicSearch (the US meeting counts) indexes from January 2025;
# each of its places links its latest meeting video on YouTube, whose channel holds the board's older recordings.
# For each place: the channel of that video (yt-dlp), then the titles (and dates, where the listing gives them) of the
# channel's videos and live streams, keeping only those that could be meetings. Stops cleanly if YouTube asks to sign in.
import os, sys, json, re, subprocess, time, urllib.request
OUT = "fetch/out/c68"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "-U", "yt-dlp"], check=False)
UA = {"User-Agent": "school-board-research-project/1.0 (github.com/amaar-a1)"}
# Round 68, part 1: residents enrolled in public and private school, kindergarten to grade 12, by school district:
# ACS 2019-2023 table B14002 from the Census Bureau's table-based summary file (no API key needed), keeping the
# unified (970), elementary (950) and secondary (960) school district rows.
import io, gzip
def acs_part():
    os.makedirs("fetch/out/c67", exist_ok=True)
    lg = open("fetch/out/c67/log.txt", "w")
    u = "https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/acsdt5y2023-b14002.dat"
    nums = ["008", "009", "011", "012", "014", "015", "017", "018", "032", "033", "035", "036", "038", "039", "041", "042"]
    pub_n = {"008", "011", "014", "017", "032", "035", "038", "041"}
    out = {}
    try:
        resp = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=600)
        head = None
        for raw in io.TextIOWrapper(resp, encoding="utf-8", errors="replace"):
            f = raw.rstrip("\n").split("|")
            if head is None:
                head = {k: i for i, k in enumerate(f)}; lg.write("columns " + " ".join(f[:6]) + f" ... {len(f)}\n"); continue
            g = f[head["GEO_ID"]]
            if not g[:3] in ("970", "950", "960"): continue
            code = g.split("US")[-1]
            pub = priv = 0
            for n in nums:
                v = f[head.get(f"B14002_E{n}", -1)] if f"B14002_E{n}" in head else ""
                try: v = int(float(v))
                except ValueError: v = 0
                if n in pub_n: pub += max(v, 0)
                else: priv += max(v, 0)
            out[code] = {"kind": {"970": "unified", "950": "elementary", "960": "secondary"}[g[:3]], "public": pub, "private": priv}
        lg.write(f"OK {len(out)} districts\n")
    except Exception as e:
        lg.write(f"ERR {e}\n")
    json.dump({"source": "ACS 2019-2023 5-year, table B14002 (K-12 enrollment of residents by type of school)", "districts": out}, open("fetch/out/c67/acs_b14002_sd.json", "w"))
    lg.close()
acs_part()

places = json.loads(urllib.request.urlopen(urllib.request.Request("https://schools.civicsearch.org/api/get_place_list", headers=UA), timeout=180).read())
log.write(f"places {len(places)}\n"); log.flush()
MAYBE = re.compile(r"board|meeting|boe\b|b\.o\.e|trustee|school committee|session|hearing|workshop|\b(19|20)\d\d\b|\d{1,2}[./-]\d{1,2}[./-]\d{2,4}", re.I)
def ytdlp(args, timeout=600):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings"] + args, capture_output=True, text=True, timeout=timeout)
    if "Sign in to confirm" in r.stderr: raise RuntimeError("sign-in")
    return r
res = {"places": {}, "channels": {}}
t0 = time.time()
try:
    for i, p in enumerate(places):
        link = p.get("last_meeting_link") or ""
        if "youtube.com" not in link and "youtu.be" not in link:
            res["places"][p["query_id"]] = None; continue
        r = ytdlp(["--skip-download", "--print", "%(channel_url)s", link], 180)
        ch = r.stdout.strip().splitlines()[-1] if r.returncode == 0 and r.stdout.strip() else None
        res["places"][p["query_id"]] = ch
        if ch and ch not in res["channels"]:
            items = []
            for tab in ("/videos", "/streams"):
                r = ytdlp(["--flat-playlist", "-J", ch + tab], 900)
                if r.returncode == 0:
                    for e in json.loads(r.stdout).get("entries") or []:
                        t = e.get("title") or ""
                        if MAYBE.search(t):
                            items.append([t, e.get("upload_date") or "", e.get("timestamp") or e.get("release_timestamp") or ""])
                time.sleep(1)
            res["channels"][ch] = items
        if i % 25 == 0:
            log.write(f"{i + 1}/{len(places)} {len(res['channels'])} channels, {int(time.time() - t0)}s\n"); log.flush()
            json.dump(res, open(f"{OUT}/us_youtube_titles.json", "w"))
        if time.time() - t0 > 5.2 * 3600: log.write("time limit\n"); break
except RuntimeError:
    log.write(f"YouTube asked to sign in at place {i}; stopped\n")
json.dump(res, open(f"{OUT}/us_youtube_titles.json", "w"))
log.write(f"done: {len(res['places'])} places, {len(res['channels'])} channels\n")
log.close()
