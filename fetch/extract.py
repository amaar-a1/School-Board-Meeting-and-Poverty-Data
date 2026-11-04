# Temporary: Territorial Council session dates of Saint-Pierre-et-Miquelon from its published deliberations (jo-spm.fr).
import json, os, re, subprocess, time, urllib.request
OUT = "fetch/out/spm3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
subprocess.run("sudo apt-get install -y -q poppler-utils >/dev/null 2>&1", shell=True)
found, log, fails = {}, [], 0
def date_of(url):
    global fails
    time.sleep(1.5)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            data = r.read()
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); fails += 1
        return None
    open("/tmp/d.pdf", "wb").write(data)
    t = subprocess.run(["pdftotext", "-l", "2", "/tmp/d.pdf", "-"], capture_output=True, text=True).stdout
    m = re.search(r"S[ée]ance\s+(officielle|extraordinaire|publique)?\s*du\s+(\w+\s+)?(\d{1,2}\s*(?:er)?\s+\w+\s+20\d\d)", t, re.I)
    return (m.group(1) or "", m.group(3)) if m else ("?", t[:120].replace("\n", " "))
for year, pattern, top in [(2025, "https://jo-spm.fr/doc_jo/DELIB2025-{:04d}.pdf", 320), (2026, "https://jo-spm.fr/doc_jo/DELIB_{:03d}_2026.pdf", 260)]:
    for n in range(1, top, 4):
        if fails > 12 and not found:
            log.append("stopping: the site isn't answering"); break
        d = date_of(pattern.format(n))
        if d:
            found[f"{year}-{n}"] = d
json.dump(found, open(f"{OUT}/sessions.json", "w"), indent=1, ensure_ascii=False)
open(f"{OUT}/log.txt", "w").write("\n".join(log[-200:]))
