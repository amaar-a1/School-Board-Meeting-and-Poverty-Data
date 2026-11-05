"""Monthly refresh: list every video title on the YouTube channels already used for meeting counts.

The channels were found once (canada_youtube.py, uk_youtube.py, nordic_youtube.py, islands_youtube.py)
and checked by hand; this script doesn't search for new ones, so no new wrong matches can creep in.
It writes data-prep/inputs/youtube_titles.json ({"refreshed": date, "titles": {channel URL: [titles]}}),
which build_uk.py, finish_canada.py, build_germany.py, build_nordic.py, build_iceland.py, build_islands.py and
build_switzerland.py read in place of their older title lists, then recount with their own rules.
Run by .github/workflows/refresh-meetings.yml. Usage: python3 data-prep/refresh_youtube.py
"""
import csv, datetime, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")
OUT = os.path.join(IN, "youtube_titles.json")
sys.path.insert(0, HERE)


def channels():
    urls = set()
    def from_csv(path, col="Channel URL", keep=lambda r: True):
        if os.path.exists(path):
            for r in csv.DictReader(open(path, encoding="utf-8")):
                u = (r.get(col) or "").strip()
                if u.startswith("http") and keep(r): urls.add(u)
    from_csv(os.path.join(IN, "uk", "uk_youtube.csv"), keep=lambda r: (r.get("Meetings") or "0") != "0")
    from_csv(os.path.join(IN, "canada", "canada_youtube.csv"), keep=lambda r: (r.get("Board meetings on YouTube") or "0") != "0")
    from_csv(os.path.join(IN, "canada_channels.csv"))
    for cc in ("NO", "SE", "FI", "DK", "NL"):
        from_csv(os.path.join(IN, "nordic", "youtube", f"{cc}_youtube.csv"))
    import build_germany as de
    from_csv(os.path.join(IN, "germany", "youtube", "DE_youtube.csv"), keep=lambda r: r.get("Channel") and de.channel_ok(r["Channel"], "(city)" in r["District"] or r["District"] in ("Berlin", "Hamburg"), r["District"]))
    for f in ("IS_youtube.csv", "IS_youtube_rerun.csv"):
        from_csv(os.path.join(IN, "iceland", "youtube", f))
    from build_islands import ISLAND_CHANNELS
    urls |= {u for u, _ in ISLAND_CHANNELS.values()}
    import build_switzerland as ch
    named = {c["name"]: c["url"] for x in json.load(open(os.path.join(IN, "switzerland", "youtube", "channels.json"), encoding="utf-8")).values()
             for c in x.get("channels", [])}
    urls |= {u or named.get(n) for u, _, n in ch.CHANNELS.values()} - {None}
    return sorted(urls)


def titles_of(url):
    out = []
    for tab in ("/videos", "/streams"):
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", url + tab],
                           capture_output=True, text=True, timeout=900)
        if r.returncode == 0:
            out += [e.get("title") or "" for e in json.loads(r.stdout).get("entries") or []]
        elif "Sign in to confirm" in r.stderr:
            raise RuntimeError("YouTube asked to sign in")
        time.sleep(1)
    return out


def main():
    old = json.load(open(OUT, encoding="utf-8"))["titles"] if os.path.exists(OUT) else {}
    res, failed = {}, 0
    urls = channels()
    for i, u in enumerate(urls):
        try:
            t = titles_of(u)
        except RuntimeError:
            print("YouTube asked to sign in; keeping the older lists for the rest.")
            res.update({k: v for k, v in old.items() if k not in res})
            break
        except Exception:
            t = []
        if t or u not in old:
            res[u] = t
        else:
            res[u] = old[u]; failed += 1   # keep the last good list if a listing comes back empty
        print(f"{i + 1}/{len(urls)} {len(res[u])} {u}", flush=True)
    json.dump({"refreshed": datetime.date.today().isoformat(), "titles": res}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(len(res), "channels;", failed, "kept from the last refresh")


if __name__ == "__main__":
    main()
