# Round 15: data for Lithuania (SDMX), Georgia (PxWeb tree), South Africa (DBE masterlists), Korea (MOHW recipients, pupils), Kenya (KNBS via curl).
import os, re, json, subprocess, urllib.request, urllib.parse, time
OUT = "fetch/out/five15"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
def get(n, u, tries=2):
    for k in range(tries):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=240).read()
            open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); log.flush(); time.sleep(1.5); return b
        except Exception as e: err = e; time.sleep(3)
    log.write(f"== {n} ERR {err} {u}\n"); log.flush()
def curl(n, u):
    r = subprocess.run(["curl", "-sSL", "-m", "240", "-A", UA["User-Agent"], "-o", f"{OUT}/{n}", "-w", "%{http_code}", u], capture_output=True, text=True)
    sz = os.path.getsize(f"{OUT}/{n}") if os.path.exists(f"{OUT}/{n}") else 0
    log.write(f"== {n} curl {r.stdout} {sz} {r.stderr.strip()[:120]} {u}\n"); log.flush(); time.sleep(1.5)
    return open(f"{OUT}/{n}", "rb").read() if sz else None
def links(b, base, pat):
    out = []
    for l, t in re.findall(rb'href="([^"#]+)"[^>]*>(.{0,200}?)</a>', b or b"", re.S):
        l = l.decode("utf-8", "replace"); t = re.sub(r"<[^>]+>|\s+", " ", t.decode("utf-8", "replace")).strip()
        full = urllib.parse.urljoin(base, l.replace("&amp;", "&"))
        if re.search(pat, full + " " + t, re.I): out.append((t, full)); log.write(f"   link {t[:90]} | {full}\n")
    return out

# Lithuania
for f in ["S3R453_M3080308", "S3R0243_M3160702", "S3R469_M3160701_1", "S3R358_M3160909_1", "S3R057_M3110302_3", "S3R167_M3010213", "S3R0361_M3160701_3"]:
    get(f"lt_{f}.json", f"https://osp-rs.stat.gov.lt/rest_json/data/{f}")
# Georgia: list the PxWeb folders we need, two levels down
base = "https://pc-axis.geostat.ge/PXWeb/api/v1/en/Database/"
def walk(path, depth):
    b = get("ge_" + re.sub(r"[^A-Za-z0-9]", "_", path)[:60] + ".json", base + urllib.parse.quote(path))
    if not b: return
    for y in json.loads(b):
        log.write(f"     {'  '*depth}{path}/{y['id']} [{y.get('type')}] | {y.get('text','')}\n")
        if y.get("type") == "l" and depth < 2: walk(path + "/" + y["id"], depth + 1)
for p in ["Social Statistics/Education", "Social Statistics/Social Protection", "Social Statistics/Living Conditions, Subsistence Minimum", "Demography"]:
    walk(p, 0)
# South Africa: DBE masterlists (the page's "National" ordinary-school files)
pg = get("za_emis.html", "https://www.education.gov.za/Programmes/EMIS/EMISDownloads.aspx")
for i, (t, u) in enumerate([x for x in links(pg, "https://www.education.gov.za/", r"National.{0,4}ordinary") ][:8]):
    curl(f"za_master_{i:02d}.bin", u)
# Korea: MOHW 2025 basic livelihood recipients post and its attachments; pupils by province
pg = get("kr_mohw_post.html", "https://www.mohw.go.kr/board.es?mid=a10411010100&bid=0019&act=view&list_no=1491455&tag=&nPage=1")
for i, (t, u) in enumerate(links(pg, "https://www.mohw.go.kr/", r"download|file|\.xlsx?|\.pdf|\.hwp")[:6]):
    curl(f"kr_mohw_att{i}" + (os.path.splitext(t)[1][:6] or ".bin"), u)
for n, u in [("kr_datagokr.html", "https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword=%EC%8B%9C%EB%8F%84%EB%B3%84+%ED%95%99%EC%83%9D%EC%88%98"),
             ("kr_index_edu.html", "https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1520"),
             ("w_kr_edu.html", "https://ko.wikipedia.org/w/index.php?title=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EA%B5%90%EC%9C%A1%EC%B2%AD&action=render")]:
    b = get(n, u); links(b, u, r"xls|csv|download|fileData")
# Kenya: KNBS (curl, as Python lacks the site's intermediate certificate) and Wikipedia
for n, u in [("ke_knbs_census.html", "https://www.knbs.or.ke/2019-kenya-population-and-housing-census-reports/"),
             ("ke_knbs_pov.html", "https://www.knbs.or.ke/reports/kenya-poverty-report-2022/"),
             ("ke_knbs_search.html", "https://www.knbs.or.ke/?s=poverty"),
             ("ke_knbs_abstract.html", "https://www.knbs.or.ke/?s=county+statistical+abstract")]:
    b = curl(n, u); links(b, u, r"poverty|volume|\.pdf|county|education")
get("w_ke_pov.html", "https://en.wikipedia.org/w/index.php?title=List_of_counties_of_Kenya_by_poverty_rate&action=render")
get("w_ke_hdi.html", "https://en.wikipedia.org/w/index.php?title=List_of_Kenyan_counties_by_Human_Development_Index&action=render")
