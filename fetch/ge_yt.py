"""Georgia: each municipality's council (sakrebulo) YouTube channel. Writes OUT/ge_meet.json:
{District ID: {"name", "channel", "url", "videos": [titles]}}. Channel names are in Georgian: a channel counts when it names
the municipality (its Georgian stem) and is a council's or municipality's."""
import csv, json, os, re, subprocess, sys, time
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open("fetch/lists/georgia.csv", encoding="utf-8")))
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=900)
    if r.returncode: raise RuntimeError(r.stderr.strip()[-200:])
    return json.loads(r.stdout)
res = {}
for r in rows:
    ka = r["ka"]; gen = ka.replace(" მუნიციპალიტეტი", "")            # genitive ("გორის") or the city's name
    stem = re.sub(r"(ის|ს)$", "", gen)[:max(3, len(re.sub(r"(ის|ს)$", "", gen)) - 1)]
    rec = {"name": r["District"], "channel": "", "url": "", "videos": [], "cands": {}}
    try:
        for q in (f"{gen} საკრებულოს სხდომა", f"{gen} მუნიციპალიტეტის საკრებულო", f"{r['District']} sakrebulo"):
            for e in yt(f"ytsearch15:{q}").get("entries") or []:
                if e.get("channel_url") and e.get("channel"): rec["cands"][e["channel_url"]] = e["channel"]
            time.sleep(1.5)
        ok = [(u, ch) for u, ch in rec["cands"].items()
              if re.search(r"საკრებულო|მუნიციპალიტეტ|მერია|sakrebulo|municipality|city hall|city council", ch, re.I)
              and (stem in ch or r["District"].lower()[:5] in ch.lower()) and not re.search(r"ტელევიზ|TV\b|news|ახალი ამბ", ch, re.I)]
        ok.sort(key=lambda x: "საკრებულო" not in x[1] and "sakrebulo" not in x[1].lower())
        if ok:
            u, ch = ok[0]; vids = []
            for tab in ("/videos", "/streams"):
                try: vids += [v.get("title") or "" for v in yt(u + tab).get("entries") or []]
                except RuntimeError: pass
                time.sleep(1)
            rec.update(channel=ch, url=u, videos=vids)
    except Exception as e:
        rec["err"] = str(e)[:200]
    res[r["District ID"]] = rec; print(r["District"], rec["channel"], len(rec["videos"]), flush=True)
    json.dump(res, open(f"{OUT}/ge_meet.json", "w"), ensure_ascii=False)
