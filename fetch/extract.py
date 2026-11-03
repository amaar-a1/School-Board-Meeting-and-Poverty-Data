# Temporary: check which Canadian data sources can be downloaded (status, type and size only).
import json, urllib.request
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
def head(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r:
            first = r.read(2000)
            return {"status": r.status, "type": r.headers.get("Content-Type"), "length": r.headers.get("Content-Length"), "start": first[:300].decode("latin-1")}
    except Exception as e:
        return {"error": str(e)[:200]}
urls = {
 "statcan_tbl_98100103": "https://www150.statcan.gc.ca/n1/tbl/csv/98100103-eng.zip",
 "statcan_csd_bnd": "https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/files-fichiers/lcsd000b21a_e.zip",
 "statcan_da_bnd": "https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/files-fichiers/lda_000b21a_e.zip",
 "statcan_profile_da": "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=006",
 "bc_wfs": "https://openmaps.gov.bc.ca/geo/pub/WHSE_TANTALIS.TA_SCHOOL_DISTRICTS_SVW/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=WHSE_TANTALIS.TA_SCHOOL_DISTRICTS_SVW&outputFormat=application/json&count=2",
 "qc_shp": "https://www.donneesquebec.ca/recherche/dataset/37d944eb-335b-40fe-8d80-835ff77bc5cb/resource/2ded8ebe-5e71-4dff-91de-896b4150e19c/download",
 "ab_rest": "https://geospatial.alberta.ca/titan/rest/services/nadc/edu_school_and_school_authority_boundaries/MapServer?f=json",
 "mb_rest": "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_School_Divisions/FeatureServer?f=json",
 "on_service_area": "https://data.ontario.ca/api/3/action/package_search?q=%22Board%20service%20area%22&rows=2",
 "on_regions": "https://data.ontario.ca/api/3/action/package_search?q=%22district%20school%20board%20regions%22&rows=2",
 "ns_search": "https://data.novascotia.ca/api/catalog/v1?q=regional%20centre%20for%20education%20boundaries&limit=10",
 "sk_search": "https://open.canada.ca/data/api/3/action/package_search?q=Saskatchewan%20school%20division%20boundaries&rows=5",
 "nb_search": "https://gnb.socrata.com/api/catalog/v1?q=school%20district%20boundaries&limit=10",
}
out = {k: head(v) for k, v in urls.items()}
for k in ("on_service_area", "on_regions"):
    try:
        with urllib.request.urlopen(urllib.request.Request(urls[k], headers=UA), timeout=60) as r:
            res = json.load(r)["result"]["results"]
        out[k + "_resources"] = [[(x.get("format"), x.get("name"), x.get("url")) for x in p.get("resources", [])] for p in res]
    except Exception as e:
        out[k + "_resources"] = str(e)
json.dump(out, open("fetch/out/canada_check.json", "w"), indent=1)
