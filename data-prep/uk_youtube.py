"""Count recorded education/children's committee meetings that UK councils post on YouTube.

For each council in docs/data/uk.csv: search YouTube for the council's meetings, keep a channel
whose name matches the council (e.g. "Kent County Council", "Glasgow City Council"), list its
videos and count titles naming an education, schools, children's services or children and young
people committee (or the Education Authority's board). Writes uk_youtube.csv.
Usage: python3 uk_youtube.py docs/data/uk.csv uk_youtube.csv
"""
import csv, json, re, subprocess, sys, time, unicodedata

GENERIC = set("council county borough city district metropolitan royal of the and on upon".split())
EDU = re.compile(r"educat|school|children|young people|learning|cyp\b|childrens|families|lifelong", re.I)
MEET = re.compile(r"committee|scrutiny|board|panel|cabinet|forum|meeting|sub-committee", re.I)
NOT = re.compile(r"\b(news|tv|radio|bbc|itv|live music|football|church)\b", re.I)


def words(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    return re.findall(r"[a-z]+", s)


def ytdlp(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-200:])
    return json.loads(r.stdout)


def is_channel_for(name, channel):
    want = [w for w in words(name) if w not in GENERIC] or words(name)
    have = set(words(channel))
    if NOT.search(channel) or not ({"council", "councils", "cyngor", "authority", "webcast", "webcasts", "democracy", "democratic", "meetings"} & have):
        return False
    return all(w in have for w in want)


def main(src, dst):
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    seen = {}
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["District ID", "District", "Channel", "Channel URL", "Meetings", "Example titles", "Error"])
        for r in rows:
            name = r["District"].replace("Education Authority (Northern Ireland)", "Education Authority Northern Ireland")
            out = [r["District ID"], r["District"], "", "", "", "", ""]
            try:
                chans = {}
                for q in (f"{name} council committee meeting", f"{name} council children's services committee"):
                    for e in ytdlp(f"ytsearch12:{q}").get("entries") or []:
                        if e.get("channel_url") and e.get("channel"):
                            chans[e["channel_url"]] = e["channel"]
                    time.sleep(1)
                pick = [(u, c) for u, c in chans.items() if is_channel_for(name, c)]
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
                        t = [v for v in vids if EDU.search(v) and MEET.search(v)]
                        if "Education Authority" in name:
                            t = [v for v in vids if re.search(r"board", v, re.I) and MEET.search(v)]
                        uniq = {re.sub(r"\b(part|pt)\s*\d+\b|\(\d\)", "", v, flags=re.I).strip().lower() for v in t}
                        seen[url] = (len(uniq), t[:3])
                    n, ex = seen[url]
                    out[2:6] = [chan, url, n, " / ".join(ex)]
            except Exception as e:
                out[6] = str(e)[:200]
                if "Sign in to confirm" in str(e):
                    w.writerow(out); print("YouTube asked to sign in; stopping."); return
            w.writerow(out); f.flush()
            print(r["District"], "->", out[2], out[4], flush=True)
            time.sleep(1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
