# Temporary: (1) First Nations reserves and settlements inside Canada's "Rest of Ontario/Alberta" map areas, from
# the 2021 census subdivision borders (this repo's statcan-csd-2021 release), with mapshaper; (2) IBGE's 2024/2025
# municipal borders for Mato Grosso (Boa Esperança do Norte).
import json, os, subprocess, time, traceback, urllib.request, zipfile
OUT = "fetch/out/ca_reserves2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=900):
    err = None
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except Exception as e:
            err = e; time.sleep(10)
    raise err
def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True); return f"$ {cmd[:160]}\n{r.stdout[-1500:]}{r.stderr[-1500:]}"
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1200:]}\n\n")
    log.flush()
log.write(run("npm install -g mapshaper@0.6 >/dev/null 2>&1; mapshaper -v") + "\n")

def reserves():
    open("/tmp/csd.zip", "wb").write(get("https://github.com/amaar-a1/School-Board-Meeting-and-Poverty-Data/releases/download/statcan-csd-2021/lcsd000b21a_e.zip"))
    zipfile.ZipFile("/tmp/csd.zip").extractall("/tmp/csd")
    shp = [os.path.join(dp, f) for dp, _, fs in os.walk("/tmp/csd") for f in fs if f.endswith(".shp")][0]
    out = [run(f"mapshaper -i {shp} -info 2>&1 | head -30")]
    out.append(run(f"mapshaper -i {shp} encoding=utf8 -filter \"PRUID == '35' || PRUID == '48'\" -proj wgs84 "
                   f"-join fetch/ca_rest.geojson point-method fields=id "
                   f"-filter \"id == 'CA-ON-REST' || id == 'CA-AB-REST'\" "
                   f"-each \"area_km2 = Math.round(this.area / 1e5) / 10\" "
                   f"-o /tmp/rest_all.json format=geojson"))
    g = json.load(open("/tmp/rest_all.json"))
    types = {}
    for f in g["features"]: types[f["properties"]["CSDTYPE"]] = types.get(f["properties"]["CSDTYPE"], 0) + 1
    out.append(f"subdivisions inside the Rest-of areas: {len(g['features'])}; types {types}")
    fn = {"type": "FeatureCollection", "features": [f for f in g["features"] if f["properties"]["CSDTYPE"] in ("IRI", "S-É", "TI", "IGD", "NL")]}
    json.dump(fn, open("/tmp/fn.json", "w"))
    out.append(run(f"mapshaper -i /tmp/fn.json -simplify 4% keep-shapes -o {OUT}/ca_rest_first_nations.geojson format=geojson precision=0.0001"))
    out.append("kept: " + "; ".join(f"{f['properties']['CSDNAME']} ({f['properties']['CSDTYPE']}, {f['properties']['id']}, {f['properties']['area_km2']} km²)" for f in fn["features"][:200]))
    return "\n".join(out)
step("Canada: First Nations lands in the Rest-of areas", reserves)

def ibge():
    out = []
    for y in ("2025", "2024"):
        u = f"https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_{y}/UFs/MT/MT_Municipios_{y}.zip"
        try:
            b = get(u, 300); open(f"/tmp/mt{y}.zip", "wb").write(b); zipfile.ZipFile(f"/tmp/mt{y}.zip").extractall(f"/tmp/mt{y}")
            shp = [os.path.join(dp, f) for dp, _, fs in os.walk(f"/tmp/mt{y}") for f in fs if f.endswith(".shp")][0]
            out.append(f"{y}: {len(b)} bytes")
            out.append(run(f"mapshaper -i {shp} encoding=utf8 -filter \"CD_MUN == '5101837'\" -proj wgs84 -simplify 5% keep-shapes -o {OUT}/br_5101837_{y}.geojson format=geojson precision=0.0001"))
        except Exception as e:
            out.append(f"{y}: {e}")
    return "\n".join(out)
step("Brazil: Boa Esperança do Norte (IBGE)", ibge)
log.close()
