"""India: each district's zila parishad (district council) YouTube channel. Writes OUT/in_meet_K.json for shard K/N:
{District ID: {"name", "state", "channel", "url", "videos": [titles]}}. A channel counts when its name (in Latin letters)
contains the district's name and says it is a zila parishad / zilla panchayat / district council."""
import csv, json, os, re, subprocess, sys, time, unicodedata
OUT, shard = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
k, n = map(int, shard.split("/"))
rows = list(csv.DictReader(open("fetch/lists/india.csv", encoding="utf-8")))[k::n]
deadline = time.time() + float(os.environ.get("IN_SECONDS", "15000"))
fold = lambda s: re.sub(r"[^a-z ]", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=900)
    if r.returncode: raise RuntimeError(r.stderr.strip()[-200:])
    return json.loads(r.stdout)
res = {}
for r in rows:
    if time.time() > deadline: break
    name = re.sub(r"\s*\(.*?\)", "", r["District"]).strip()
    words = [w for w in fold(name).split() if len(w) > 2 and w not in ("district", "north", "south", "east", "west")] or fold(name).split()
    rec = {"name": r["District"], "state": r["Region"], "channel": "", "url": "", "videos": [], "cands": {}}
    try:
        for q in (f"zila parishad {name} meeting", f"zilla panchayat {name} {r['Region']}"):
            for e in yt(f"ytsearch12:{q}").get("entries") or []:
                if e.get("channel_url") and e.get("channel"): rec["cands"][e["channel_url"]] = e["channel"]
            time.sleep(1.2)
        ok = [(u, ch) for u, ch in rec["cands"].items()
              if re.search(r"zil+a|jil+a|zp\b|district panchayat|district council|parishad|panchayat", fold(ch)) and all(w in fold(ch).split() or w in fold(ch) for w in words)
              and not re.search(r"news|live tv|samachar|police|school|college", fold(ch))]
        if ok:
            u, ch = ok[0]; vids = []
            for tab in ("/videos", "/streams"):
                try: vids += [v.get("title") or "" for v in yt(u + tab).get("entries") or []]
                except RuntimeError: pass
                time.sleep(1)
            rec.update(channel=ch, url=u, videos=vids)
    except Exception as e:
        rec["err"] = str(e)[:200]
        if "Sign in to confirm" in str(e): res[r["District ID"]] = rec; break
    res[r["District ID"]] = rec; print(r["District"], "->", rec["channel"], len(rec["videos"]), flush=True)
    json.dump(res, open(f"{OUT}/in_meet_{k}.json", "w"), ensure_ascii=False)
