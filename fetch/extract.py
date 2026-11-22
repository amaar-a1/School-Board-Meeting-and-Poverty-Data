# Round 20: India discovery: NITI Aayog MPI reports (district tables), UDISE+ / data.gov.in enrolment, Wikipedia district list.
import os, re, json, urllib.request, urllib.parse, time
OUT = "fetch/out/in20"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "text/html,application/json,application/pdf,*/*"}
def get(n, u, data=None, hdr=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}, data=data), timeout=300).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); log.flush(); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n"); log.flush()
    finally: time.sleep(1.5)
def links(b, base, pat):
    for l, t in re.findall(rb'href="([^"#]+)"[^>]*>(.{0,200}?)</a>', b or b"", re.S):
        l = l.decode("utf-8", "replace"); t = re.sub(r"<[^>]+>|\s+", " ", t.decode("utf-8", "replace")).strip()
        full = urllib.parse.urljoin(base, l.replace("&amp;", "&"))
        if re.search(pat, full + " " + t, re.I): log.write(f"   link {t[:90]} | {full}\n")
for n, u in [("niti_mpi_2023.pdf", "https://www.niti.gov.in/sites/default/files/2023-08/India-National-Multidimentional-Poverty-Index-2023.pdf"),
             ("niti_mpi_2021.pdf", "https://www.niti.gov.in/sites/default/files/2021-11/National_MPI_India-11242021.pdf")]:
    get(n, u)
b = get("niti_reports.html", "https://www.niti.gov.in/whats-new/national-multidimentional-poverty-index-2023")
links(b, "https://www.niti.gov.in/", r"\.pdf|\.xlsx|mpi|poverty")
b = get("niti_mpi_page.html", "https://www.niti.gov.in/national-multidimensional-poverty-index")
links(b, "https://www.niti.gov.in/", r"\.pdf|\.xlsx|district")
# UDISE+
for n, u in [("udise_home.html", "https://udiseplus.gov.in/"), ("udise_reports.html", "https://udiseplus.gov.in/#/en/page/publications"),
             ("udise_dashboard.html", "https://dashboard.udiseplus.gov.in/")]:
    b = get(n, u); links(b, u, r"\.pdf|\.xlsx|report|district|api")
    if b: log.write("   scripts " + " ".join(sorted(set(re.findall(r'src="([^"]+\.js[^"]*)"', b.decode("utf-8", "replace"))))[:10]) + "\n")
# data.gov.in catalogue search for district enrolment
for q in ["district wise enrolment UDISE", "district wise enrolment of students"]:
    b = get("dgi_" + re.sub(r"\W", "_", q)[:30] + ".html", "https://www.data.gov.in/search?title=" + urllib.parse.quote(q))
    links(b, "https://www.data.gov.in/", r"resource|catalog|enrol")
# Wikipedia: districts with 2011 population and area
get("w_in_districts.html", "https://en.wikipedia.org/w/index.php?title=List_of_districts_in_India&action=render")
