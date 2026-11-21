# Round 14: discovery for South Korea, South Africa, Kenya, Georgia and Lithuania (pages, APIs, links to data files).
import os, re, json, urllib.request, urllib.parse, time
OUT = "fetch/out/five14"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
def get(n, u, data=None, hdr=None):
    try:
        req = urllib.request.Request(u, headers={**UA, **(hdr or {})}, data=data)
        b = urllib.request.urlopen(req, timeout=180).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); log.flush(); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n"); log.flush()
    finally: time.sleep(1.5)
def links(n, u, pat, follow=None, maxf=12):
    b = get(n, u)
    if not b: return
    seen = 0
    for l, t in re.findall(rb'href="([^"#]+)"[^>]*>(.{0,200}?)</a>', b, re.S):
        l = l.decode("utf-8", "replace"); t = re.sub(r"<[^>]+>|\s+", " ", t.decode("utf-8", "replace")).strip()
        full = urllib.parse.urljoin(u, l.replace("&amp;", "&"))
        if re.search(pat, full + " " + t, re.I):
            log.write(f"   link {t[:90]} | {full}\n")
            if follow and re.search(follow, full, re.I) and seen < maxf:
                seen += 1; get(f"{n}_dl{seen:02d}" + os.path.splitext(urllib.parse.urlparse(full).path)[1][:6], full)
    log.flush()

# Lithuania: Official Statistics Portal SDMX dataflows
b = get("lt_dataflows.xml", "https://osp-rs.stat.gov.lt/rest_xml/dataflow/")
if b:
    t = b.decode("utf-8", "replace")
    for m in re.finditer(r'<str:Dataflow[^>]*id="([^"]+)"[^>]*>.*?<com:Name xml:lang="en">([^<]*)</com:Name>', t, re.S):
        if re.search(r"pupil|student|social|benefit|assistance|population|poverty|at-risk|income", m.group(2), re.I): log.write(f"   LT {m.group(1)} | {m.group(2)}\n")
# Georgia: Geostat PxWeb tree
for n, u in [("ge_px_root.json", "https://pc-axis.geostat.ge/PXWeb/api/v1/en/Database"), ("ge_px_root2.json", "http://pc-axis.geostat.ge/PXWeb/api/v1/en/Database/")]:
    b = get(n, u)
    if b: break
if b:
    try:
        root = json.loads(b); log.write("   GE root: " + ", ".join(x["id"] for x in root) + "\n")
        for x in root:
            if re.search(r"Population|Education|Social|Living|Regional", x["id"] + x.get("text", ""), re.I):
                bb = get(f"ge_px_{re.sub('[^A-Za-z0-9]', '_', x['id'])[:40]}.json", u.rstrip("/") + "/" + urllib.parse.quote(x["id"]))
                if bb:
                    for y in json.loads(bb): log.write(f"     {x['id']}/{y['id']} | {y.get('text','')}\n")
    except Exception as e: log.write(f"   GE parse {e}\n")
links("ge_ssa.html", "https://ssa.gov.ge/", r"statist|სტატისტ|xls|pdf", None)
links("ge_geostat_reg.html", "https://www.geostat.ge/en/modules/categories/27/regional-statistics", r"xls|municipal", r"\.xlsx?$")
links("ge_geostat_edu.html", "https://www.geostat.ge/en/modules/categories/59/general-education", r"xls|school|pupil", r"\.xlsx?$")
links("ge_geostat_soc.html", "https://www.geostat.ge/en/modules/categories/192/living-conditions-subsistence-minimum-and-social-assistance", r"xls|assist|poverty", r"\.xlsx?$")
# South Africa: DBE EMIS masterlists; Stats SA
links("za_emis.html", "https://www.education.gov.za/Programmes/EMIS/EMISDownloads.aspx", r"master|school|\.xls|\.zip", r"master.*\.(xlsx?|zip)|\.(xlsx|zip)$", 15)
links("za_statssa_c22.html", "https://www.statssa.gov.za/?page_id=16716", r"census|municipal|xls|pdf", None)
# Kenya: KNBS
links("ke_knbs_census.html", "https://www.knbs.or.ke/2019-kenya-population-and-housing-census-reports/", r"volume|county|pdf", None)
links("ke_knbs_poverty.html", "https://www.knbs.or.ke/?s=poverty+report", r"poverty", None)
links("ke_knbs_pubs.html", "https://www.knbs.or.ke/publications/", r"poverty|statistical abstract|county|education", None)
links("ke_moe.html", "https://www.education.go.ke/publications", r"statistic|booklet|pdf", None)
# South Korea: education statistics and KOSIS
links("kr_kess.html", "https://kess.kedi.re.kr/index", r"xls|통계|연보|download", None)
links("kr_kess_pub.html", "https://kess.kedi.re.kr/publ/list?itemCode=02&menuId=m_02_02_01", r"연보|xls|pdf|download", None)
links("kr_kosis.html", "https://kosis.kr/statHtml/statHtml.do?orgId=117&tblId=DT_117N_A00001", r"xls|csv", None)
links("kr_mohw.html", "https://www.mohw.go.kr/board.es?mid=a10411010100&bid=0019", r"기초생활|수급|통계|xls", None)
# Wikipedia (population and area tables as fallbacks)
for n, t in [("w_lt.html", "Municipalities_of_Lithuania"), ("w_ge.html", "Municipalities_of_Georgia"), ("w_ke.html", "Counties_of_Kenya"),
             ("w_za.html", "List_of_municipalities_in_South_Africa"), ("w_kr.html", "Provinces_of_South_Korea")]:
    get(n, f"https://en.wikipedia.org/w/index.php?title={t}&action=render")
