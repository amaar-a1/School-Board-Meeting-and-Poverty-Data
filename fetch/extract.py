# Temporary: check candidate pages for school enrollment on the Falklands, Niue, Tokelau and Pitcairn.
import os, re, html, urllib.request
OUT = "fetch/out/isl_links1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
U = ["https://www.falklands.gov.fk/policy/statistics", "https://www.falklands.gov.fk/policy/statistics/census", "https://www.falklands.gov.fk/education",
     "https://www.secondary.ac.fk", "https://www.ijs.ac.fk",
     "https://niuestatistics.nu", "https://niuestatistics.nu/education/", "https://niuestatistics.nu/social/education/", "https://www.gov.nu/education",
     "https://www.tokelau.org.nz/Stats.html", "https://www.tokelau.org.nz/Tokelau+Government/Government+Departments/Office+of+the+Council+for+the+Ongoing+Government+OCOG/Tokelau+National+Statistics+Office.html",
     "https://www.government.pn", "https://www.government.pn/policies/education", "https://www.immigration.gov.pn/community/education"]
for u in U:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40); t = r.read().decode("utf-8", "replace")
        txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
        title = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
        hits = [m.group(0) for m in re.finditer(r".{0,80}\b(pupils|students|enrol\w*|roll)\b.{0,80}", txt, re.I)][:3]
        links = [l for l in re.findall(r'href="([^"]+)"', t) if re.search(r"educat|school|census|statist|\.pdf|\.xlsx", l, re.I)][:12]
        log.write(f"OK {r.status} {u} | {title.group(1).strip()[:80] if title else ''}\n  hits {hits}\n  links {links}\n")
    except Exception as e: log.write(f"ERR {u} {str(e)[:80]}\n")
log.close()
