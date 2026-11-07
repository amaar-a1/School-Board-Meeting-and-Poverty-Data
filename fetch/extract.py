# Temporary: France (INSEE Filosofi 2023, populations, primary-school pupils) and Ecuador (poverty and population by canton).
import csv, io, json, os, time, traceback, urllib.parse, urllib.request, zipfile
OUT = "fetch/out/fr_ec2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=600):
    err = None
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except Exception as e:
            err = e; time.sleep(10)
    raise err
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-700:]}\n\n")
    log.flush()
def unzip(name, u):
    b = get(u); z = zipfile.ZipFile(io.BytesIO(b)); out = []
    for n in z.namelist():
        data = z.read(n); open(f"{OUT}/{name}__{os.path.basename(n)}", "wb").write(data)
        out.append(f"{n}: {len(data)} bytes; head {data[:400]!r}")
    return f"{len(b)} bytes zip\n" + "\n".join(out)
step("Filosofi communes 2023", lambda: unzip("filosofi_cc", "https://api.insee.fr/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR"))
step("Filosofi by age, départements 2023", lambda: unzip("filosofi_sage", "https://api.insee.fr/melodi/file/DS_FILOSOFI_SAGE_LOG_TP_NIVVIE/DS_FILOSOFI_SAGE_LOG_TP_NIVVIE_2023_CSV_FR"))
step("Populations de référence 2023", lambda: unzip("pop_ref", "https://api.insee.fr/melodi/file/DS_POPULATIONS_REFERENCE/DS_POPULATIONS_REFERENCE_2023_CSV_FR"))
def pupils():
    q = urllib.parse.urlencode({"select": "code_commune_insee, secteur, sum(nombre_total_eleves) as eleves, count(*) as ecoles",
                                "group_by": "code_commune_insee, secteur", "where": 'rentree_scolaire="2025"', "limit": -1})
    b = get("https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ecoles-effectifs-nb_classes/exports/csv?" + q, 900)
    open(f"{OUT}/fr_ecoles_eleves_2025_by_commune.csv", "wb").write(b)
    return f"{len(b)} bytes; head {b[:400]!r}"
step("Primary-school pupils by commune, rentrée 2025", pupils)
# Ecuador
def save(name, u):
    b = get(u); open(f"{OUT}/{name}", "wb").write(b); return f"{len(b)} bytes; head {b[:200]!r}"
step("INEC NBI tabulados (census)", lambda: save("ec_tabulados_pobreza_nbi.xlsx", "https://www.ecuadorencifras.gob.ec//documentos/web-inec/POBREZA/NBI/NBI-FUENTE-CPV/Tabulados_pobreza_por_NBI.xlsx"))
step("INEC NBI dic 2025", lambda: save("ec_tabulados_nbi_dic25.xlsx", "https://www.ecuadorencifras.gob.ec/documentos/web-inec/POBREZA/2025/Diciembre/Tabulados_NBI-dic25.xlsx"))
step("BRC cantones y parroquias", lambda: save("ec_brc_cantones_parroquias.xlsx", "https://data.humdata.org/dataset/947e78a1-0e3d-4f6f-a956-4d6f80915d84/resource/13695d08-cc7f-46b0-9ba1-cd6177eea7cb/download/datos_cantones-y-parroquias.xlsx"))
step("OCHA population by canton", lambda: save("ec_eclb012.xls", "https://data.humdata.org/dataset/edcef26f-fdc3-40c4-ba88-219982e7517f/resource/9cac15c3-a1f4-4004-b082-98e0e4d3df04/download/eclb012.xls"))
def censo_pages():
    import re
    out = []
    for u in ("https://www.ecuadorencifras.gob.ec/pobreza-por-necesidades-basicas-insatisfechas-nbi/", "https://www.ecuadorencifras.gob.ec/censo-de-poblacion-y-vivienda-2022/",
              "https://www.ecuadorencifras.gob.ec/tabulados-censo-2022/", "https://www.censoecuador.gob.ec/data-censo/"):
        try:
            t = get(u, 60).decode("utf-8", "replace")
            out.append(f"{u}: {len(t)} chars; files: {sorted(set(re.findall(r'href=[\"\\']([^\"\\']+\\.(?:xlsx?|zip|csv))', t, re.I)))[:80]}")
        except Exception as e: out.append(f"{u}: {e}")
    return "\n".join(out)
step("INEC census 2022 pages", censo_pages)
log.close()
