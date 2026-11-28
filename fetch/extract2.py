# Round 68b (channels from oEmbed): US school boards' meetings before 2025. CivicSearch (the US meeting counts) indexes from January 2025;
# each of its places links its latest meeting video on YouTube, whose channel holds the board's older recordings.
# For each place: the channel of that video (yt-dlp), then the titles (and dates, where the listing gives them) of the
# channel's videos and live streams, keeping only those that could be meetings. Stops cleanly if YouTube asks to sign in.
import os, sys, json, re, subprocess, time, urllib.request, urllib.parse
OUT = "fetch/out/c68"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "-U", "yt-dlp"], check=False)
UA = {"User-Agent": "school-board-research-project/1.0 (github.com/amaar-a1)"}
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
        # the video's channel from YouTube's public oEmbed endpoint (no video page)
        try:
            o = json.loads(urllib.request.urlopen(urllib.request.Request("https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(link), headers=UA), timeout=60).read())
            ch = (o.get("author_url") or "").replace("http://", "https://") or None
        except Exception as e:
            ch = None; log.write(f"oembed {p['query_id']}: {e}\n")
        time.sleep(0.5)
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
