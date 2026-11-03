"""Count board meetings Canadian school boards post on YouTube.

For each board in canada.csv: search YouTube for the board's name, keep channels whose name
matches the board's distinctive words (place names, district numbers), list each matching
channel's videos, and count the titles that look like board meetings. A meeting split into
parts counts once. Writes canada_youtube.csv (District ID, channel, count, examples).

Usage: python3 canada_youtube.py canada.csv out.csv [data-prep/inputs/canada_channels.csv]
"""
import csv, json, os, re, subprocess, sys, time, unicodedata

GENERIC = set("""the of and de du des la le les l d school schools district division divisions board boards public catholic
separate roman regional centre center services service scolaire scolaires commission conseil education educational
authority francophone english french anglophone authority no number sd rce centre-de-services area county""".split())
MEETING = re.compile(r"\bmeeting\b|s[ée]ance|r[ée]union (du|ordinaire|extraordinaire|publique)|assembl[ée]e (publique|du conseil|ordinaire)", re.I)
NOT = re.compile(r"graduation|concert|tournament|highlights|commencement|webinar|town hall|information session|parent|"
                 r"council meeting|city council|library|school options|open house|trustee (tour|corner)|message", re.I)
SCHOOLISH = re.compile(r"school|schools|board|division|district|\bsd\s?\d|\bsd\b|dsb|cdsb|education|scolaire|commission|conseil|"
                       r"trustees|ecsd|centre de services|\bcss\b|ecoles|écoles|rce\b|csf|catholic", re.I)
# Not a school board's own channel: news, cities, churches, and US districts with the same place names.
NOT_BOARD = re.compile(r"\b(city|town|municipality|county of|village|journal|gazette|news|tv|radio|church|parish|voters|library|"
                       r"isd|csd|usd|area school district|local schools|school district of|idaho|kansas|ohio|texas|washington|"
                       r"pennsylvania|minnesota|wisconsin|michigan|oregon|california|new york|illinois|indiana)\b", re.I)



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


US_DESC = re.compile(r"\b(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Idaho|Illinois|"
                     r"Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|"
                     r"Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|"
                     r"Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|"
                     r"Virginia|Washington|West Virginia|Wisconsin|Wyoming|ISD|U\.S\.)\b")
CA_DESC = re.compile(r"Canada|Alberta|British Columbia|Manitoba|Saskatchewan|Ontario|Qu[ée]bec|Nova Scotia|New Brunswick|"
                     r"Newfoundland|Prince Edward|Yukon|Northwest Territories|Nunavut|\b(AB|BC|MB|SK|ON|QC|NS|NB|PE|NL)\b")


def initials(name):
    return "".join(w[0] for w in norm(name) if w not in {"the", "of", "and", "de", "du", "des", "la", "le", "les", "d", "l"} and not w.isdigit())


def score(name, channel):
    if not SCHOOLISH.search(channel) or NOT_BOARD.search(channel):
        return 0
    want, have = key_words(name), set(norm(channel))
    if len(initials(name)) >= 3 and initials(name) in have:
        return 1.0
    hit = [w for w in want if w in have or any(h.startswith(w[:6]) and len(w) >= 6 for h in have)]
    nums = [w for w in want if w.isdigit()] if name.startswith("School District") else []
    want = [w for w in want if not w.isdigit()] + nums
    if nums and not all(n in have for n in nums):
        return 0
    cath = lambda ws: bool({"catholic", "catholique", "separate"} & set(ws))
    if cath(norm(name)) != cath(have):   # keep public and Catholic boards apart
        return 0
    fr = lambda ws: bool({"francophone", "conseil", "csf", "dsfm", "csap", "cepeo", "csviamonde", "fransaskois"} & set(ws))
    if fr(norm(name)) and not fr(have) and not {"scolaire", "ecole", "ecoles"} & have:
        return 0
    return len(hit) / len(want)


def channel_meetings(url):
    """(meeting count, example titles, channel description) for one channel."""
    vids, desc = [], ""
    for tab in ("/videos", "/streams"):
        try:
            j = ytdlp(url + tab)
            desc = desc or (j.get("description") or "")
            vids += [v.get("title") or "" for v in j.get("entries") or []]
        except RuntimeError:
            pass
        time.sleep(1)
    titles = [t for t in vids if MEETING.search(t) and not NOT.search(t)]
    meetings = {re.sub(r"\b(part|partie|pt)\s*\d+\b|\(\d\)|[-–|:]\s*$", "", t, flags=re.I).strip().lower() for t in titles}
    return len(meetings), titles[:3], desc


def main(src, dst, overrides=""):
    boards = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    # data-prep/inputs/canada_channels.csv: a board's channel checked by hand ("none" = no channel)
    fixed = {r["District ID"]: r["Channel URL"].strip() for r in csv.DictReader(open(overrides, newline="", encoding="utf-8"))} if overrides and os.path.exists(overrides) else {}
    seen = {}
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["District ID", "District", "Province", "Channel", "Channel URL", "Board meetings on YouTube", "Example titles",
                    "Channel description", "Other candidates", "Error"])
        for b in boards:
            name = b["District"]
            row = {"District ID": b["District ID"], "District": name, "Province": b["Province"]}
            try:
                if b["District ID"] in fixed:
                    url, chan, others = fixed[b["District ID"]], "(checked by hand)", ""
                else:
                    french = b["Province"] == "QC" or b["Board type"] in ("French", "Francophone", "French public", "French Catholic")
                    queries = [f"{name} board meeting"] + ([f"{name} séance du conseil"] if french else [])
                    chans = {}
                    for q in queries:
                        for e in ytdlp(f"ytsearch12:{q}").get("entries") or []:
                            if e.get("channel_url") and e.get("channel"):
                                chans[e["channel_url"]] = e["channel"]
                        time.sleep(1)
                    best = sorted(((score(name, c), u, c) for u, c in chans.items()), reverse=True)
                    others = " / ".join(f"{c} ({sc:.2f})" for sc, u, c in best[1:4] if sc > 0)
                    url, chan = (best[0][1], best[0][2]) if best and best[0][0] >= 0.6 else ("", "")
                row["Other candidates"] = others
                if url and url != "none":
                    if url not in seen:
                        seen[url] = channel_meetings(url)
                    n, ex, desc = seen[url]
                    if chan != "(checked by hand)" and US_DESC.search(desc) and not CA_DESC.search(desc):
                        row["Error"] = f"skipped {chan}: its description points to the US"
                        raise StopIteration
                    row.update({"Channel": chan, "Channel URL": url, "Board meetings on YouTube": n, "Example titles": " / ".join(ex),
                                "Channel description": desc[:200].replace("\n", " ")})
            except StopIteration:
                pass
            except Exception as e:
                row["Error"] = str(e)[:300]
                if "Sign in to confirm" in str(e):
                    w.writerow([row.get(c, "") for c in ["District ID", "District", "Province", "Channel", "Channel URL", "Board meetings on YouTube", "Example titles", "Channel description", "Other candidates", "Error"]])
                    print("YouTube asked to sign in; stopping."); return
            w.writerow([row.get(c, "") for c in ["District ID", "District", "Province", "Channel", "Channel URL", "Board meetings on YouTube",
                                                 "Example titles", "Channel description", "Other candidates", "Error"]]); f.flush()
            print(name, "->", row.get("Channel", ""), row.get("Board meetings on YouTube", ""), row.get("Error", "")[:80], flush=True)
            time.sleep(1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
