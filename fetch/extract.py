# Temporary: second YouTube pass for Canadian boards with no meetings found, with other wordings.
import csv, os, re, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
sys.path.insert(0, "fetch"); import canada_youtube as c
OUT = "fetch/out/ca2"; os.makedirs(OUT, exist_ok=True)
T0 = time.time()
cols = ["District ID", "District", "Province", "Channel", "Channel URL", "Board meetings on YouTube", "Example titles", "Channel description", "Other candidates", "Error"]
w = csv.writer(open(f"{OUT}/canada_youtube_pass2.csv", "w", newline="", encoding="utf-8")); w.writerow(cols)
seen = {}
for b in csv.DictReader(open("fetch/canada_zero.csv", encoding="utf-8")):
    if time.time() - T0 > 4.5 * 3600: break
    name = b["District"]; row = {"District ID": b["District ID"], "District": name, "Province": b["Province"]}
    short = re.sub(r"^(The )?|( School Division| School District| District School Board| Catholic District School Board| Regional Centre for Education| School Board| Board of Education)$", "", name).strip()
    french = b["Province"] in ("QC", "Quebec") or "French" in b["Board type"] or "Franco" in b["Board type"]
    qs = [f"{name} board of trustees", f"{short} public board meeting", f"{short} trustees meeting"]
    if french: qs += [f"{name} conseil d'administration séance", f"{short} séance publique conseil d'administration"]
    try:
        chans = {}
        for q in qs:
            for e in c.ytdlp(f"ytsearch15:{q}").get("entries") or []:
                if e.get("channel_url") and e.get("channel"): chans[e["channel_url"]] = e["channel"]
            time.sleep(1)
        best = sorted(((c.score(name, ch), u, ch) for u, ch in chans.items()), reverse=True)
        row["Other candidates"] = " / ".join(f"{ch} ({sc:.2f})" for sc, u, ch in best[1:4] if sc > 0)
        if best and best[0][0] >= 0.6:
            sc, url, chan = best[0]
            if url not in seen: seen[url] = c.channel_meetings(url)
            n, ex, desc = seen[url]
            row.update({"Channel": chan, "Channel URL": url, "Board meetings on YouTube": n, "Example titles": " / ".join(ex), "Channel description": desc[:200].replace("\n", " ")})
    except Exception as e:
        row["Error"] = str(e)[:300]
        if "Sign in to confirm" in str(e): w.writerow([row.get(k, "") for k in cols]); break
    w.writerow([row.get(k, "") for k in cols]); print(name, "->", row.get("Channel", ""), row.get("Board meetings on YouTube", ""), flush=True)
