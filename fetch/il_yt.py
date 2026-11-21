"""Israel: each local authority's council (and education committee) meetings on YouTube.
Search "ישיבת מועצה <name>"; keep a channel whose name has the authority's name and a word for municipality or
council; list its videos; count titles naming a council meeting, and those naming the education committee.
Usage: il_yt.py AUTHORITIES_CSV OUTDIR"""
import csv, json, os, re, subprocess, sys, time
src, out = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=600)
    if r.returncode: raise RuntimeError(r.stderr.strip()[-300:])
    return json.loads(r.stdout)
norm = lambda s: re.sub(r"[\"'׳״\-–_.,()]", " ", s or "").replace("  ", " ").strip()
CH = re.compile(r"עירי|מועצ|רשות|municipal|council|city of|עיר ")
MEET = re.compile(r"ישיבת|ישיבה|מליאת|מליאה|ועדת|ועדה|council meeting|מועצת העיר|מועצה")
EDU = re.compile(r"חינוך|education")
res, seen = [], {}
for r in rows:
    name = r["LocalAuthorityName"].strip()
    rec = {"code": r["LocalAuthorityCode"], "name": name, "type": r["LocalAuthorityType"], "channel": "", "url": "", "meet": 0, "edu": 0, "all": 0, "ex": [], "err": ""}
    try:
        cands = {}
        for q in (f"ישיבת מועצה {name}", f"{r['LocalAuthorityLongName']} ישיבת מועצה"):
            for e in yt(f"ytsearch15:{q}").get("entries") or []:
                if e.get("channel_url") and e.get("channel"): cands[e["channel_url"]] = e["channel"]
            time.sleep(1.5)
        nm = norm(name)
        ok = [(u, c) for u, c in cands.items() if nm and nm in norm(c) and CH.search(c)]
        if ok:
            u, c = ok[0]
            if u not in seen:
                vids = []
                for tab in ("/videos", "/streams"):
                    try: vids += [{"t": v.get("title") or "", "d": v.get("upload_date"), "u": v.get("url")} for v in yt(u + tab).get("entries") or []]
                    except RuntimeError: pass
                    time.sleep(1)
                seen[u] = vids
            vids = seen[u]
            m = [v for v in vids if MEET.search(v["t"])]
            rec.update(channel=c, url=u, all=len(vids), meet=len(m), edu=len([v for v in m if EDU.search(v["t"])]), ex=[v["t"] for v in m[:5]], vids=vids)
    except Exception as e:
        rec["err"] = str(e)[:200]
        if "Sign in" in str(e): res.append(rec); break
    res.append(rec); print(name, "->", rec["channel"], rec["meet"], flush=True)
    json.dump(res, open(f"{out}/il_yt.json", "w"), ensure_ascii=False)
