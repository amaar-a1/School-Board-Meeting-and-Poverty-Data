# Round 18: Kenya (KNBS PDFs, with its certificate chain completed), Korea (KESS file), Georgia (Geostat xlsx files).
import os, re, json, subprocess, urllib.request, urllib.parse, time
OUT = "fetch/out/five18"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
def get(n, u, data=None, hdr=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}, data=data), timeout=300).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); log.flush(); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n"); log.flush()
    finally: time.sleep(1.5)
def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600); return r.stdout, r.stderr
# Kenya
o, _ = sh("openssl s_client -connect www.knbs.or.ke:443 -servername www.knbs.or.ke </dev/null 2>/dev/null | openssl x509 -noout -text | grep -A1 'CA Issuers'")
m = re.search(r"URI:(\S+)", o)
B = f"{OUT}/ke_bundle.pem"
if m:
    sh(f"curl -sSL -m 60 -o {OUT}/i.der '{m.group(1)}' && (openssl x509 -inform DER -in {OUT}/i.der -out {OUT}/i.pem || cp {OUT}/i.der {OUT}/i.pem) && cat /etc/ssl/certs/ca-certificates.crt {OUT}/i.pem > {B}")
def kc(n, u):
    o, e = sh(f"curl -sSL -m 600 --cacert {B} -A '{UA['User-Agent']}' -o {OUT}/{n} -w '%{{http_code}}' '{u}'")
    sz = os.path.getsize(f"{OUT}/{n}") if os.path.exists(f"{OUT}/{n}") else 0
    log.write(f"== {n} curl {o} {sz} {e.strip()[:100]} {u}\n"); log.flush(); time.sleep(2)
    return open(f"{OUT}/{n}", "rb").read() if sz else b""
kc("ke_poverty_2022.pdf", "https://www.knbs.or.ke/wp-content/uploads/2024/10/The-Kenya-Poverty-Report-2022.pdf")
kc("ke_child_poverty_2025.pdf", "https://www.knbs.or.ke/wp-content/uploads/2025/08/Brighter-Futures-Breaking-Cycles-of-Poverty-for-Kenyas-Children-2025-Report1.pdf")
kc("ke_abstract_2025.pdf", "https://www.knbs.or.ke/wp-content/uploads/2025/11/2025-Statistical-Abstract.pdf")
for n, u in [("ke_vol1", "https://www.knbs.or.ke/?wpdmpro=2019-kenya-population-and-housing-census-volume-i-population-by-county-and-sub-county"),
             ("ke_vol3", "https://www.knbs.or.ke/?wpdmpro=2019-kenya-population-and-housing-census-volume-iii-distribution-of-population-by-age-sex-and-administrative-units")]:
    t = kc(n + ".html", u).decode("utf-8", "replace")
    dl = sorted(set(re.findall(r'(https://www\.knbs\.or\.ke/[^"\']*wpdmdl=\d+[^"\']*)', t)))
    log.write(f"   dl {dl[:3]}\n")
    if dl: kc(n + ".pdf", dl[0].replace("&amp;", "&"))
for f in ["i.der", "i.pem", "ke_bundle.pem"]:
    if os.path.exists(f"{OUT}/{f}"): os.remove(f"{OUT}/{f}")
# Korea: KESS post with the province file
b = get("kr_kess_post.html", "https://kess.kedi.re.kr/post/6731854?itemCode=04&menuId=m_02_04_03_01")
if b:
    t = b.decode("utf-8", "replace")
    for l in sorted(set(re.findall(r'(?:href|data-url|onclick)="([^"]*(?:download|file|Down)[^"]*)"', t, re.I)))[:20]: log.write(f"   kr link {l}\n")
    for i, l in enumerate(sorted(set(re.findall(r'(/(?:download|file)[^"\'\s]*)', t)))[:4]):
        get(f"kr_kess_{i}.bin", urllib.parse.urljoin("https://kess.kedi.re.kr/", l.replace("&amp;", "&")), hdr={"Referer": "https://kess.kedi.re.kr/post/6731854"})
# Georgia: every xlsx on the education, population and social protection pages
for n, u in [("ge_edu.html", "https://www.geostat.ge/en/modules/categories/59/general-education"),
             ("ge_pop.html", "https://www.geostat.ge/en/modules/categories/41/population"),
             ("ge_soc.html", "https://www.geostat.ge/en/modules/categories/53/social-protection"),
             ("ge_soc2.html", "https://www.geostat.ge/en/modules/categories/54/social-protection"),
             ("ge_reg.html", "https://www.geostat.ge/en/modules/categories/27/regional-statistics")]:
    b = get(n, u)
    if not b: continue
    t = b.decode("utf-8", "replace")
    for x in sorted(set(re.findall(r'https?://(?:www\.)?geostat\.ge/media/\d+/[^"\'\s<>]+\.(?:xlsx|xls|XLSX|XLS)', t))):
        log.write(f"   ge xlsx {x}\n")
        if re.search(r"municipal|self-gov|subsistence|allowance|region|population|Pupils|schools", x, re.I):
            get("ge_" + re.sub(r"[^A-Za-z0-9.]", "_", x.split("/")[-1])[-70:], x)
