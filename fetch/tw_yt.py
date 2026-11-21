"""Taiwan: each county or city council's YouTube channel; its plenary sittings and education-committee meetings.
Writes OUT/tw_meet.json: {county: {"channel", "url", "videos": [titles]}}"""
import json, os, re, subprocess, sys, time
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
C = ["臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市", "新竹市", "嘉義市", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
     "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=600)
    if r.returncode: raise RuntimeError(r.stderr.strip()[-200:])
    return json.loads(r.stdout)
res = {}
for c in C:
    alts = {c, c.replace("臺", "台")}
    rec = {"channel": "", "url": "", "videos": [], "cands": {}}
    try:
        for q in (f"{c}議會 定期大會", f"{c}議會 教育委員會", f"{c}議會 直播"):
            for e in yt(f"ytsearch20:{q}").get("entries") or []:
                ch = e.get("channel") or ""
                if e.get("channel_url") and "議會" in ch: rec["cands"][e["channel_url"]] = ch
            time.sleep(1.5)
        ok = [(u, ch) for u, ch in rec["cands"].items() if any(a in ch for a in alts) and not re.search(r"議員|黨團|服務處", ch)]
        if ok:
            u, ch = ok[0]; vids = []
            for tab in ("/videos", "/streams"):
                try: vids += [v.get("title") or "" for v in yt(u + tab).get("entries") or []]
                except RuntimeError: pass
                time.sleep(1)
            rec.update(channel=ch, url=u, videos=vids)
    except Exception as e:
        rec["err"] = str(e)[:200]
    res[c] = rec; print(c, rec["channel"], len(rec["videos"]), flush=True)
    json.dump(res, open(f"{OUT}/tw_meet.json", "w"), ensure_ascii=False)
