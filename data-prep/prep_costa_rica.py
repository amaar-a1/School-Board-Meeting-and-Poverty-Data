"""Turns the Costa Rica downloads (made on GitHub's runner) into the small inputs build_latam.costa_rica() reads
(data-prep/inputs/costa_rica/).

- cr_geo.geojson: the cantons, from geoBoundaries gbOpen CRI ADM2 (simplified; 83 cantons: Monteverde, made a canton
  in 2021 out of Puntarenas, has no border of its own there and stays inside Puntarenas).
- cr_data.json, per canton (IDs CRI-01..84 in cr_cantons.csv, alphabetical):
  province, pop, area: Spanish Wikipedia, "Anexo:Cantones de Costa Rica" (INEC's 2022 estimate from the census's partial
    results, and the canton's area);
  ipm: UNDP, Atlas de Desarrollo Humano Cantonal 2024, Cuadro 5, Índice de Pobreza Multidimensional 2023 (cr_ipm_2023.csv);
  pupils, public: MEP (Departamento de Análisis Estadístico), initial enrollment by school, 2022: day primary schools
    (grades 1-6, "matriculainicialescuelasdiurnas-2014-2022-aniocursadosexo.xlsx") and day secondary schools (grades 7-12,
    academic, technical and arts; "MATRICULA_INICIAL_COLEGIOS_2014-2022_POR_ANIO_CURSADO_Y_SEXO.xlsx"). Sector 1 is
    public; private (2) and state-subsidized private schools (3, subvencionado) are privately run and count as private.
    Schools in Puerto Jiménez and Monteverde districts count toward the new cantons.
  meetings: the municipal council's YouTube channel (fetch/nyt.py, CR).
Usage: python3 data-prep/prep_costa_rica.py RAWDIR [RAWDIR ...] GEODIR
"""
import csv, glob, html, json, os, re, sys, unicodedata
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "costa_rica")
key = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
ALIAS = {"palmeras": "palmares", "leoncortescastro": "leoncortes"}
MEPNAME = {"valverdevega": "sarchi", "vasquezdecoronado": "vazquezdecoronado"}   # Sarchí was Valverde Vega until 2018
PROV = {}


def find(dirs, name):
    return sorted(f for d in dirs for f in glob.glob(os.path.join(d, "**", name), recursive=True))[-1]


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def wiki(path):
    """{canton key: (province, area km2, population)} from the Wikipedia table (rowspans for the province)."""
    s = open(path, encoding="utf-8").read()
    t = re.findall(r"<table.*?</table>", s, re.S)[0]
    cl = lambda c: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()
    num = lambda v: float(v.replace(" ", "").replace(" ", "").replace(",", "."))
    out, prov = {}, ""
    for r in re.findall(r"<tr.*?</tr>", t, re.S):
        cells = [cl(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
        i = next((k for k, c in enumerate(cells) if c.startswith("Cantón de ")), None)
        if i is None: continue
        if i >= 1 and cells[0]: prov = cells[0].split(" ")[0] if cells[0].split(" ")[0] == cells[0].split(" ")[-1] else cells[0][:len(cells[0]) // 2].strip()
        name = re.sub(r"^Cantón de ", "", cells[i]); name = name[:len(name) // 2].strip() if name[:len(name) // 2].strip() == name[len(name) // 2:].strip() else name
        area, pop = num(cells[i + 3]), int(cells[i + 5].replace(" ", "").replace(" ", ""))
        out[re.sub(r"costarica.*", "", key(name)).replace("leoncortescastro", "leoncortes")] = (prov, area, pop)
    return out


def mep(path, cols, rama=None):
    """{(province no., canton no., district name key): [public, private]} for 2022."""
    ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
    out = {}
    for r in ws.iter_rows(min_row=4, values_only=True):
        if r[0] != 2022: continue
        if rama and str(r[14]) not in rama: continue
        h = dict(zip(["PR", "CAN", "DIS", "PROVINCIA", "CANTON", "DISTRITO", "SECTOR"], [r[5], r[6], r[7], r[8], r[9], r[10], r[12]]))
        n = sum(int(r[c] or 0) for c in cols)
        k = (MEPNAME.get(key(h["CANTON"]), key(h["CANTON"])), key(h["DISTRITO"]))
        PROV[k[0]] = h["PROVINCIA"].title().replace("Jose", "José").replace("Limon", "Limón")
        out.setdefault(k, [0, 0])[0 if str(h["SECTOR"]) == "1" else 1] += n
    return out


def main(*args):
    *dirs, geo = args
    cantons = list(csv.DictReader(open(os.path.join(OUT, "cr_cantons.csv"), encoding="utf-8")))
    ipm = {key(r["canton"]): float(r["ipm"]) for r in csv.DictReader(open(os.path.join(OUT, "cr_ipm_2023.csv"), encoding="utf-8"))}
    w = wiki(find(dirs, "wiki_es.html"))
    # Grades 1-6 are T1..T6 (columns 17, 20, ...); grades 7-12 are T7..T12 (columns 18, 21, ...). Night schools (adults) left out.
    pri = mep(find(dirs, "*iculainicialescuelasdiurnas-2014-2022*.xlsx"), [17, 20, 23, 26, 29, 32])
    sec = mep(find(dirs, "*CULA_INICIAL_COLEGIOS_2014-2022*.xlsx"), [18, 21, 24, 27, 30, 33], rama={"11", "21", "31"})
    pupils = {}
    for part in (pri, sec):
        for (c, dis), (pub, prv) in part.items():
            if c == "golfito" and dis == "puertojimenez": c = "puertojimenez"
            if c == "puntarenas" and dis == "monteverde": c = "monteverde"
            p = pupils.setdefault(c, [0, 0]); p[0] += pub; p[1] += prv
    g = {ALIAS.get(key(f["properties"]["shapeName"]), key(f["properties"]["shapeName"])): f
         for f in json.load(open(os.path.join(geo, "geoBoundaries-CRI-ADM2_simplified.geojson"), encoding="utf-8"))["features"]}
    data, feats, miss = {}, [], []
    for c in cantons:
        k = key(c["District"]); did = c["District ID"]
        _, area, pop = w.get(k, ("", None, None))
        prov = PROV.get(k) or PROV.get({"puertojimenez": "golfito", "monteverde": "puntarenas"}.get(k, ""), "")
        pub, prv = pupils.get(k, [0, 0])
        data[did] = {"name": c["District"], "province": prov, "pop": pop, "area": area, "ipm": ipm.get(k),
                     "pupils": pub + prv or None, "public": pub if pub + prv else None}
        if k in g:
            feats.append({"type": "Feature", "properties": {"id": did, "NAME": c["District"]},
                          "geometry": {"type": g[k]["geometry"]["type"], "coordinates": rnd(g[k]["geometry"]["coordinates"])}})
        for f, v in (("wiki", pop), ("ipm", ipm.get(k)), ("pupils", pub + prv), ("border", k in g)):
            if not v: miss.append((c["District"], f))
    print("missing:", miss)
    print("extra pupil cantons:", sorted(set(pupils) - {key(c["District"]) for c in cantons}))
    json.dump(data, open(os.path.join(OUT, "cr_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "cr_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    tp = sum(x["pupils"] or 0 for x in data.values()); pb = sum(x["public"] or 0 for x in data.values())
    print(len(data), "cantons;", len(feats), "borders; pop", sum(x["pop"] or 0 for x in data.values()), "; pupils", tp, "public", round(100 * pb / tp, 1))


if __name__ == "__main__":
    main(*sys.argv[1:])
