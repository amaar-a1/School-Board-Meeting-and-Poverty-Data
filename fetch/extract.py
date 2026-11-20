# Round 2: Argentina and Israel data files; Israel's local-authority borders from OpenStreetMap (Geofabrik).
import os, urllib.request, urllib.parse, json, re, time, subprocess, sys
OUT = "fetch/out/arisr2"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, keep=True, timeout=300):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if keep and name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"== {name} OK {len(b)} {url}\n{b[:300]!r}\n"); log.flush(); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush(); return None
    finally: time.sleep(2)
# --- Argentina
sp = {"ar_matricula_2024.csv": "https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/ESkFQBp0i6xAsQxQCXUjNIkBRhMRmywRXGmK_wSLbQcaGQ?e=hMEGTx",
      "ar_caract_2024.csv": "https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/ETYnM6yznjhAsDGJKzosO3kBcbatxfGEaEmZ9Of1NsbyEg?e=4MRMuq",
      "ar_diccionario.xlsx": "https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/ETNQUApUc51BiLJLGAWuKtkB3PDw1t4QJZCX9d61_6D8-Q?e=hEkxgc"}
for n, u in sp.items():
    b = get(n, u + "&download=1")
    if b and b[:200].lstrip().startswith(b"<"): get(n, u.split("?")[0] + "?download=1")
get("ar_eph_pobreza_series.csv", "https://infra.datos.gob.ar/catalog/sspm/dataset/60/distribution/60.1/download/hogares-por-debajo-linea-pobreza-e-indigencia-eph-puntual.csv")
for tag in ["09_26", "03_26", "09_25", "03_25"]:
    for stem in ["cuadros_informe_pobreza_", "cuadros_pobreza_"]:
        if get(f"ar_{stem}{tag}.xls", f"https://www.indec.gob.ar/ftp/cuadros/sociedad/{stem}{tag}.xls"): break
    get(f"ar_eph_pobreza_{tag}.pdf", f"https://www.indec.gob.ar/uploads/informesdeprensa/eph_pobreza_{tag}.pdf")
get("ar_ign_prov.json", "https://wms.ign.gob.ar/geoserver/ign/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ign:provincia&outputFormat=application/json")
# --- Israel
il = {"il_mosdot_edu.csv": "https://data.gov.il/dataset/55ef9f65-c6af-47c8-8f0f-7ce6990420ad/resource/2055063b-93e8-4d6a-b2c5-c253d18c0cf6/download/mosdot_edu.csv",
      "il_mosdot.xlsx": "https://data.gov.il/dataset/5a9278c8-fa76-46e1-bf2d-0368078c9cc7/resource/5548fd63-5868-4053-ad81-98caddc5e232/download/mosdot.xlsx",
      "il_authorities.csv": "https://data.gov.il/dataset/009348a4-40d5-4bbe-92ab-ac19e4460fce/resource/c4916937-f5d3-4295-a22e-88a1af5cde6a/download/localauthorities.csv",
      "il_welfare_by_authority.csv": "https://data.gov.il/dataset/35f9e1d4-a407-4d8f-af87-9e3ccb02c05d/resource/b6dcbb4c-4102-43d2-a5a1-8e049457fe7a/download/-1.3.21.csv",
      "il_welfare_by_authority_fields.pdf": "https://data.gov.il/dataset/35f9e1d4-a407-4d8f-af87-9e3ccb02c05d/resource/1ac83090-dcae-41b5-80a5-0a22fe89427d/download/-.pdf",
      "il_ses_2019.csv": "https://data.gov.il/dataset/df3b0e8d-b76a-4186-a6e1-df8eada5ef27/resource/7c860e04-9f8d-41c2-9f24-6249958d2081/download/-2019.csv"}
for n, u in il.items(): get(n, u)
for y in ["2025/local_authorities2023/p_libud_23", "2024/local_authorities2022/p_libud_22", "2025/local_authorities2024/p_libud_24", "2023/local_authorities2021/p_libud_21"]:
    get("il_cbs_" + y.split("/")[-1] + ".xlsx", f"https://www.cbs.gov.il/he/publications/doclib/{y}.xlsx")
# Borders: OSM administrative boundaries in Israel's extract
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "osmium", "shapely"], check=True)
    pbf = "/tmp/il.osm.pbf"
    urllib.request.urlretrieve("https://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf", pbf)
    import osmium, shapely.wkb, shapely
    from shapely.geometry import mapping
    wkb = osmium.geom.WKBFactory()
    feats = []
    class H(osmium.SimpleHandler):
        def area(self, a):
            t = a.tags
            if t.get("boundary") != "administrative" or t.get("admin_level") not in ("4", "5", "6", "7", "8", "9"): return
            try: g = shapely.wkb.loads(wkb.create_multipolygon(a), hex=True)
            except Exception: return
            g = g.simplify(0.0008, preserve_topology=True)
            feats.append({"type": "Feature", "properties": {k: t.get(k, "") for k in ("name", "name:he", "name:en", "name:ar", "admin_level", "ref", "official_name", "wikidata", "border_type", "place")} | {"osm_id": a.orig_id(), "from_way": a.from_way()},
                          "geometry": mapping(g)})
    H().apply_file(pbf, locations=True)
    def rnd(c): return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 5), round(c[1], 5)]
    for f in feats: f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    json.dump({"type": "FeatureCollection", "features": feats}, open(f"{OUT}/il_osm_admin.geojson", "w"), ensure_ascii=False)
    log.write(f"== osm admin {len(feats)} features\n")
except Exception as e:
    log.write(f"== osm ERR {e}\n")
