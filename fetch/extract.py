# Temporary: official figures for the remaining islands, saved as fetched.
import json, os, traceback, urllib.request
OUT = "fetch/out/isl3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
URLS = {
    "abs_cx.html": "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA51710",
    "abs_cc.html": "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA51860",
    "abs_nf.html": "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA51720",
    "cbs_85284.json": "https://opendata.cbs.nl/ODataApi/odata/85284NED/TypedDataSet?$format=json",
    "cbs_85284_meta.json": "https://opendata.cbs.nl/ODataApi/odata/85284NED/DataProperties?$format=json",
    "cbs_85284_regions.json": "https://opendata.cbs.nl/ODataApi/odata/85284NED/CaribischNederland?$format=json",
    "cbs_poverty_2024.html": "https://www.cbs.nl/en-gb/news/2026/29/poverty-on-bonaire-st-eustatius-and-saba-declined-in-2024",
    "gib_emp11.pdf": "https://www.gibraltar.gov.gi/uploads/statistics/2025/employment/EMP.11.pdf",
    "gib_emp12.pdf": "https://www.gibraltar.gov.gi/uploads/statistics/2025/employment/EMP.12.pdf",
    "gib_emp14.pdf": "https://www.gibraltar.gov.gi/uploads/statistics/2025/employment/EMP.14.pdf",
    "gib_emp16_2026.pdf": "https://www.gibraltar.gov.gi/uploads/statistics/2026/employment/EMP.16.pdf",
    "gib_w2024.pdf": "https://www.parliament.gi/uploads/contents/hansard/hansard_2024/questions_for_written_answer_september_2024.pdf",
    "gha_education.html": "https://www.gha.gi/jsna-education/",
    "tkl_hies.pdf": "https://spccfpstore1.blob.core.windows.net/digitallibrary-docs/files/73/73d325a34d612e880335fea49896211f.pdf",
    "ssb_svalbard_pop.json": "https://data.ssb.no/api/v0/no/table/07430/",
    "nz_chatham.html": "https://tools.summaries.stats.govt.nz/places/TA/chatham-islands-territory",
}
for name, u in URLS.items():
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180) as r: b = r.read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"ok {name} {len(b)}\n")
    except Exception as e: log.write(f"ERR {name} {str(e)[:150]}\n")
log.close()
