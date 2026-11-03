"""Count board meetings Canadian school boards post on YouTube.

For each board in canada.csv: search YouTube for the board's name, keep channels whose name
matches the board's distinctive words (place names, district numbers), list each matching
channel's videos, and count the titles that look like board meetings. A meeting split into
parts counts once. Writes canada_youtube.csv (District ID, channel, count, examples).

Usage: python3 canada_youtube.py canada.csv out.csv
"""
import csv, json, re, subprocess, sys, time, unicodedata

GENERIC = set("""the of and de du des la le les l d school schools district division divisions board boards public catholic
separate roman regional centre center services service scolaire scolaires commission conseil education educational
authority francophone english french anglophone authority no number sd rce centre-de-services area county""".split())
MEETING = re.compile(r"board meeting|public meeting|regular meeting|special meeting|board of trustees|trustee|"
                     r"s[ée]ance|conseil d.administration|r[ée]union (du|publique)|assembl[ée]e (publique|du conseil)|"
                     r"committee of the whole|public board", re.I)
NOT = re.compile(r"graduation|concert|tournament|highlights|commencement|webinar|town hall", re.I)


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z]+|\d+", s)


def key_words(name):
    w = [t for t in norm(name) if t not in GENERIC and (len(t) > 2 or t.isdigit())]
    return w or norm(name)


def ytdlp(*args):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--no-warnings", *args], capture_output=True, text=True, timeout=300)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-300:])
    return json.loads(r.stdout)


def score(name, channel):
    want, have = key_words(name), set(norm(channel))
    hit = [w for w in want if w in have or any(h.startswith(w[:6]) and len(w) >= 6 for h in have)]
    nums = [w for w in want if w.isdigit()]
    if nums and not all(n in have for n in nums):
        return 0
    cath = lambda ws: bool({"catholic", "catholique", "separate"} & set(ws))
    if cath(norm(name)) != cath(have):   # keep public and Catholic boards apart
        return 0
    fr = lambda ws: bool({"francophone", "conseil", "csf", "dsfm", "csap", "cepeo", "csviamonde", "fransaskois"} & set(ws))
    if fr(norm(name)) and not fr(have) and not {"scolaire", "ecole", "ecoles"} & have:
        return 0
    return len(hit) / len(want)


def main(src, dst):
    boards = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    seen = {}
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["District ID", "District", "Channel", "Channel URL", "Board meetings on YouTube", "Example titles", "Error"])
        for b in boards:
            name = b["District"]
            row = [b["District ID"], name, "", "", "", "", ""]
            try:
                res = ytdlp(f"ytsearch15:{name} board meeting")
                chans = {}
                for e in res.get("entries") or []:
                    if e.get("channel_url") and e.get("channel"):
                        chans[e["channel_url"]] = e["channel"]
                best = sorted(((score(name, c), u, c) for u, c in chans.items()), reverse=True)
                if best and best[0][0] >= 0.6:
                    _, url, chan = best[0]
                    if url not in seen:
                        time.sleep(2)
                        vids = []
                        for tab in ("/videos", "/streams"):
                            try:
                                vids += [v.get("title") or "" for v in ytdlp(url + tab).get("entries") or []]
                            except RuntimeError:
                                pass
                        titles = [t for t in vids if MEETING.search(t) and not NOT.search(t)]
                        meetings = {re.sub(r"\b(part|partie|pt)\s*\d+\b|\(\d\)|[-–|:]\s*$", "", t, flags=re.I).strip().lower() for t in titles}
                        seen[url] = (len(meetings), titles[:3])
                    n, ex = seen[url]
                    row[2:6] = [chan, url, n, " / ".join(ex)]
            except Exception as e:
                row[6] = str(e)[:300]
                if "Sign in to confirm" in str(e):
                    w.writerow(row); print("YouTube asked to sign in; stopping."); return
            w.writerow(row); f.flush()
            print(name, "->", row[2], row[4], row[6][:80], flush=True)
            time.sleep(2)


if __name__ == "__main__":
    main(*sys.argv[1:3])
