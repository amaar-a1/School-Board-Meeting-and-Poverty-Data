# Round 17: Korea pupils by province (data.go.kr file data), Georgia PxWeb tables (variants), Kenya KNBS (completing its
# certificate chain with the intermediate its certificate names) and HDX school datasets.
import os, re, json, subprocess, urllib.request, urllib.parse, time
OUT = "fetch/out/five17"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
def get(n, u, data=None, hdr=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}, data=data), timeout=240).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); log.flush(); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n"); log.flush()
    finally: time.sleep(1.5)
def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300); return r.stdout, r.stderr
# Korea
for pk in ["15152068"]:
    for n, u, data in [("kr_sel_get.json", f"https://www.data.go.kr/tcs/dss/selectFileDataDownload.do?publicDataPk={pk}&fileDetailSn=1&dataNm=", None),
                       ("kr_sel_post.json", "https://www.data.go.kr/tcs/dss/selectFileDataDownload.do", f"publicDataPk={pk}&fileDetailSn=1".encode())]:
        b = get(n, u, data, {"Content-Type": "application/x-www-form-urlencoded", "Referer": f"https://www.data.go.kr/data/{pk}/fileData.do"})
        if not b: continue
        t = b.decode("utf-8", "replace"); log.write("   " + t[:400].replace("\n", " ") + "\n")
        for a, d in re.findall(r'"atchFileId"\s*:\s*"([^"]+)".*?"fileDetailSn"\s*:\s*"?(\d+)', t, re.S)[:2]:
            get(f"kr_{pk}_{a[-6:]}_{d}.bin", f"https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId={a}&fileDetailSn={d}&insertDataPrcus=N",
                hdr={"Referer": f"https://www.data.go.kr/data/{pk}/fileData.do"})
# Georgia: PxWeb, several URL forms
for base in ["https://pc-axis.geostat.ge/PXWeb/api/v1/en/Database/", "http://pc-axis.geostat.ge/PXWeb/api/v1/en/Database/", "https://pc-axis.geostat.ge/PXWeb/api/v1/ka/Database/"]:
    t = "Demography/Population/01-population-by-self-governed-unit.px"
    b = get("ge_try_" + str(abs(hash(base)) % 1000) + ".json", base + urllib.parse.quote(t))
    if not b:
        b = get("ge_trypost_" + str(abs(hash(base)) % 1000) + ".json", base + urllib.parse.quote(t), data=json.dumps({"query": [], "response": {"format": "json-stat2"}}).encode(), hdr={"Content-Type": "application/json"})
    if b:
        for t in ["Demography/Population/01-population-by-self-governed-unit.px", "Social Statistics/Social Protection/Registered_Families_for_Subsistence_Allowance_by_Municipalities.px",
                  "Social Statistics/Social Protection/Beneficiaries_of_Subsistence_Allowance.px", "Social Statistics/Education/School/05_Number_of_schools_and_Pupils_by_Regions.px",
                  "Social Statistics/Education/School/01_Number_of_Gen._Edu._Schools.px", "Demography/Population/02-population-by-age-groups-and-sex.px"]:
            get("ge_" + re.sub(r"[^A-Za-z0-9]", "_", t.split("/")[-1])[:50] + ".json", base + urllib.parse.quote(t), data=json.dumps({"query": [], "response": {"format": "json-stat2"}}).encode(), hdr={"Content-Type": "application/json"})
        break
# Kenya: complete KNBS's certificate chain with the intermediate it names (AIA "CA Issuers"), then fetch with verification on
o, e = sh("openssl s_client -connect www.knbs.or.ke:443 -servername www.knbs.or.ke </dev/null 2>/dev/null | openssl x509 -noout -text | grep -A1 'CA Issuers' ")
log.write("   AIA: " + o.strip()[:300] + "\n")
m = re.search(r"URI:(\S+)", o)
if m:
    sh(f"curl -sSL -m 60 -o {OUT}/ke_inter.der '{m.group(1)}'")
    sh(f"(openssl x509 -inform DER -in {OUT}/ke_inter.der -out {OUT}/ke_inter.pem || cp {OUT}/ke_inter.der {OUT}/ke_inter.pem) && cat /etc/ssl/certs/ca-certificates.crt {OUT}/ke_inter.pem > {OUT}/ke_bundle.pem")
    for n, u in [("ke_census.html", "https://www.knbs.or.ke/2019-kenya-population-and-housing-census-reports/"), ("ke_pov.html", "https://www.knbs.or.ke/?s=poverty+report"),
                 ("ke_abstract.html", "https://www.knbs.or.ke/?s=statistical+abstract"), ("ke_edu.html", "https://www.knbs.or.ke/?s=education")]:
        o, e = sh(f"curl -sSL -m 120 --cacert {OUT}/ke_bundle.pem -A '{UA['User-Agent']}' -o {OUT}/{n} -w '%{{http_code}}' '{u}'")
        sz = os.path.getsize(f"{OUT}/{n}") if os.path.exists(f"{OUT}/{n}") else 0
        log.write(f"== {n} curl {o} {sz} {e.strip()[:120]} {u}\n")
        if sz:
            t = open(f"{OUT}/{n}", encoding="utf-8", errors="replace").read()
            for l in sorted(set(re.findall(r'href="([^"]+)"', t))):
                if re.search(r"poverty|volume|county|abstract|education|wpdmpro|\.pdf|\.xlsx", l, re.I): log.write(f"   link {l}\n")
    for f in ["ke_inter.der", "ke_bundle.pem"]:
        if os.path.exists(f"{OUT}/{f}"): os.remove(f"{OUT}/{f}")
# HDX: Kenya schools / enrolment datasets
b = get("hdx_ke.json", "https://data.humdata.org/api/3/action/package_search?q=" + urllib.parse.quote("kenya schools enrolment") + "&rows=15")
if b:
    for p in json.loads(b)["result"]["results"]:
        log.write(f"   HDX {p['name']} | {p['title']} | {p.get('dataset_date')}\n")
        for r in p.get("resources", [])[:4]: log.write(f"       {r.get('format')} {r.get('url')}\n")
