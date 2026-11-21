# Round 16: South Africa (newer masterlists), Korea (pupils), Georgia (PxWeb tables, Georgian names), Kenya (KNBS over http),
# and meetings on YouTube for Lithuania, South Africa, Kenya and Korea.
import os, re, json, subprocess, sys, urllib.request, urllib.parse, time
OUT = "fetch/out/five16"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
def get(n, u, data=None, hdr=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}, data=data), timeout=240).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); log.flush(); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n"); log.flush()
    finally: time.sleep(1.5)
def curl(n, u):
    r = subprocess.run(["curl", "-sSL", "-m", "300", "-A", UA["User-Agent"], "-o", f"{OUT}/{n}", "-w", "%{http_code}", u], capture_output=True, text=True)
    sz = os.path.getsize(f"{OUT}/{n}") if os.path.exists(f"{OUT}/{n}") else 0
    log.write(f"== {n} curl {r.stdout} {sz} {r.stderr.strip()[:120]} {u}\n"); log.flush(); time.sleep(1.5)
    return open(f"{OUT}/{n}", "rb").read() if sz else None
# meetings first (they take longest)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], capture_output=True, text=True)
env = {**os.environ, "NORDIC_DATA": "fetch/lists", "NORDIC_DEADLINE": str(time.time() + 4.7 * 3600)}
p1 = subprocess.Popen([sys.executable, "fetch/nyt.py", OUT, "LT", "ZA:0/3", "ZA:1/3", "ZA:2/3", "KE"], env=env, stdout=open(f"{OUT}/nyt_log.txt", "w"), stderr=subprocess.STDOUT)
p2 = subprocess.Popen([sys.executable, "fetch/kr_yt.py", OUT], stdout=open(f"{OUT}/kr_log.txt", "w"), stderr=subprocess.STDOUT)
# South Africa: the two masterlist links not yet downloaded
for n, u in [("za_master_new1.xlsx", "https://www.education.gov.za/LinkClick.aspx?fileticket=O2qbsfuGFC4%3d&tabid=466&portalid=0&mid=12482"),
             ("za_master_new2.xlsx", "https://www.education.gov.za/LinkClick.aspx?fileticket=XrhHvRrRkSk%3d&tabid=466&portalid=0&mid=7070")]:
    curl(n, u)
# Korea: pupils by province (data.go.kr file data pages and their files)
for did in ["15052732", "15152068"]:
    b = get(f"kr_dg_{did}.html", f"https://www.data.go.kr/data/{did}/fileData.do")
    if not b: continue
    t = b.decode("utf-8", "replace")
    for m in sorted(set(re.findall(r"(atchFileId=FILE_[0-9A-Za-z]+[^\"'&]*(?:&(?:amp;)?fileDetailSn=\d+)?)", t)))[:4]:
        u = "https://www.data.go.kr/cmm/cmm/fileDownload.do?" + m.replace("&amp;", "&")
        if "fileDetailSn" not in u: u += "&fileDetailSn=1"
        get(f"kr_dg_{did}_{len(os.listdir(OUT))}.bin", u)
    for m in re.findall(r"fn_fileDataDown\(([^)]*)\)|fileDownload\(([^)]*)\)", t)[:4]: log.write(f"   kr js {m}\n")
# Georgia: whole PxWeb tables
PX = "https://pc-axis.geostat.ge/PXWeb/api/v1/en/Database/"
for t in ["Demography/Population/01-population-by-self-governed-unit.px", "Demography/Population/04-mid-year-population-by-self-governed-units.px",
          "Social Statistics/Social Protection/Registered_Families_for_Subsistence_Allowance_by_Municipalities.px",
          "Social Statistics/Social Protection/Beneficiaries_of_Subsistence_Allowance.px",
          "Social Statistics/Education/School/05_Number_of_schools_and_Pupils_by_Regions.px",
          "Social Statistics/Education/School/01_Number_of_Gen._Edu._Schools.px",
          "Social Statistics/Education/School/06_Number_of_Pupils_by_Social_Status.px"]:
    n = "ge_" + re.sub(r"[^A-Za-z0-9]", "_", t.split("/")[-1])[:50]
    m = get(n + "_meta.json", PX + urllib.parse.quote(t))
    if m:
        q = [{"code": v["code"], "selection": {"filter": "all", "values": ["*"]}} for v in json.loads(m)["variables"]]
        get(n + ".json", PX + urllib.parse.quote(t), data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode(), hdr={"Content-Type": "application/json"})
get("w_ge_ka.html", "https://ka.wikipedia.org/w/index.php?title=%E1%83%A1%E1%83%90%E1%83%A5%E1%83%90%E1%83%A0%E1%83%97%E1%83%95%E1%83%94%E1%83%9A%E1%83%9D%E1%83%A1_%E1%83%9B%E1%83%A3%E1%83%9C%E1%83%98%E1%83%AA%E1%83%98%E1%83%9E%E1%83%90%E1%83%9A%E1%83%98%E1%83%A2%E1%83%94%E1%83%A2%E1%83%94%E1%83%91%E1%83%98&action=render")
get("w_ge_en2.html", "https://en.wikipedia.org/w/index.php?title=Administrative_divisions_of_Georgia_(country)&action=render")
# Kenya: KNBS over plain http (its https certificate chain is incomplete); World Bank subnational poverty
for n, u in [("ke_knbs_http.html", "http://www.knbs.or.ke/"), ("ke_knbs_census_http.html", "http://www.knbs.or.ke/2019-kenya-population-and-housing-census-reports/")]:
    b = curl(n, u)
    if b: log.write("   " + " ; ".join(sorted(set(re.findall(r'href="([^"]*(?:poverty|census|volume|education|abstract)[^"]*)"', b.decode("utf-8", "replace"), re.I)))[:30]) + "\n")
get("w_ke_edu.html", "https://en.wikipedia.org/w/index.php?title=Education_in_Kenya&action=render")
p1.wait(); p2.wait()
for fn in os.listdir(OUT):
    if os.path.getsize(f"{OUT}/{fn}") > 90e6: os.remove(f"{OUT}/{fn}")
