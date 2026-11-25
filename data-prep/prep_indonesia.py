"""Turns the Indonesia downloads (made on GitHub's runner, fetch rounds 29-30) into the inputs build_latam.indonesia() reads
(data-prep/inputs/indonesia/).

- Poverty and population: Statistics Indonesia (BPS) figures for each regency (kabupaten) and city (kota), 2020, as
  published in the World Bank's Indonesia Database for Policy and Economic Research (INDO-DAPOER, World Bank API source
  45): the poverty rate (share of people below BPS's poverty line, all ages; SI.POV.NAPR.ZS) and the population
  (SP.POP.TOTL). BPS's own site doesn't answer GitHub's servers.
- Borders: geoBoundaries (gbOpen) IDN ADM2, simplified; each regency's province from the ADM1 borders it lies in.
  Names: "X, Kab." is the border "X", and "X, Kota" the border "Kota X".
- Enrollment: Ministry of Primary and Secondary Education (Kemendikdasmen), Portal Data: pupils at primary level (SD/MI
  and equivalent, grades 1-6), public (negeri) and private (swasta), 2025, by regency and city ("Jumlah peserta didik
  menurut agama", summed over religions; inputs/indonesia/idn_primary_pupils.csv, the columns used, 2021-2025).
- Children (for the enrollment estimate, data-prep/estimate_enrollment.py): WorldPop's 2025 age structures (R2025A,
  1 km), summed over each border by the runner (in_ages-style file idn_ages_2025.json).
Then, after build_latam.py, run data-prep/estimate_enrollment.py indonesia.csv and data-prep/simplify_borders.sh.
Usage: python3 data-prep/prep_indonesia.py RAWDIR
"""
import json, os, re, sys
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "indonesia")
key = lambda s: re.sub(r"[^a-z]", "", str(s).lower())
# World Bank (BPS) names that differ from geoBoundaries' after the Kab./Kota rule.
ALIAS = {"kotabaru": "kotabaru", "kotakotabaru": "kotabaru", "tojounauna": "tojounauna", "pangkajenekepulauan": "pangkajenedankepulauan",
         "kotabaubau": "kotabaubau", "kotabanjarbaru": "kotabanjarbaru", "kotapadangsidimpuan": "kotapadangsidempuan",
         "fakfak": "fakfak", "kotatanjungbalai": "kotatanjungbalai", "labuhanbatu": "labuhanbatu", "kotagunungsitoli": "kotagunungsitoli",
         "kepulauanseribu": "kepulauanseribu", "kotasawahlunto": "kotasawahlunto", "batanghari": "batanghari",
         "admkepulauanseribu": "kepulauanseribu", "kendaricity": "kotakendari", "kepsiautagulandangbiaro": "siautagulandangbiaro",
         "kotakepulauantidore": "kotatidorekepulauan", "kotapadangsidempuan": "kotapadangsidimpuan",
         "pasir": "paser", "pontianak": "mempawah"}   # Pasir is now Paser; Pontianak regency is now Mempawah


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def wbkey(name):
    m = re.match(r"(.*),\s*(Kab|Kota)\.?$", name.strip())
    if not m: return key(name)
    k = key(m.group(1))
    return key("kota" + m.group(1)) if m.group(2) == "Kota" else k


def main(raw):
    gb = json.load(open(os.path.join(raw, "id_gb_ADM2.geojson"), encoding="utf-8"))["features"]
    prov = [(f["properties"]["shapeName"], shape(f["geometry"]).buffer(0)) for f in json.load(open(os.path.join(raw, "id_gb_ADM1.geojson"), encoding="utf-8"))["features"]]
    byk = {}
    for f in gb:
        byk.setdefault(key(f["properties"]["shapeName"]), []).append(f)
    series = lambda fn: {x["country"]["value"]: x["value"] for x in json.load(open(os.path.join(raw, fn), encoding="utf-8"))[1] if x["date"] == "2020" and x["value"] is not None}
    pov, pop = series("wb45_SI.POV.NAPR.ZS.json"), series("wb45_SP.POP.TOTL.json")
    data, feats, miss, used = {}, [], [], set()
    for name, rate in sorted(pov.items()):
        k = wbkey(name); k = ALIAS.get(k, k)
        fs = byk.get(k) or ([] if k.startswith("kota") else byk.get("kab" + k, []))
        fs = [f for f in fs if f["properties"]["shapeID"] not in used]
        if not fs: miss.append(name); continue
        f = fs[0]; used.add(f["properties"]["shapeID"])
        g = shape(f["geometry"]).buffer(0)
        pt = g.representative_point()
        pv = next((n for n, pg in prov if pg.contains(pt)), None)
        if not pv:   # islands outside the simplified province borders: the nearest province
            pv = min(prov, key=lambda p: p[1].distance(pt))[0]; print("nearest province:", name, "->", pv)
        if "Seribu" in name: pv = "Jakarta Special Capital Region"   # the Thousand Islands, in Jakarta Bay, are part of Jakarta
        did = "IDN-" + f["properties"]["shapeID"][-8:]
        label = re.sub(r"^Adm\.\s*", "", re.sub(r",\s*(Kab|Kota)\.?$", "", name)).strip().replace("Kep. ", "Kepulauan ")
        kota = name.strip().endswith("Kota")
        data[did] = {"name": f"Kota {label}" if kota else label, "kind": "City (kota)" if kota else "Regency (kabupaten)", "province": pv,
                     "pov": round(rate, 2), "pop": int(pop[name]) if pop.get(name) else None, "shape": f["properties"]["shapeID"]}
        feats.append({"type": "Feature", "properties": {"id": did, "NAME": data[did]["name"]},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    print("no border for:", miss)
    print("borders with no figure:", sorted(f["properties"]["shapeName"] for f in gb if f["properties"]["shapeID"] not in used))
    # Children from WorldPop, by border.
    ages = json.load(open(os.path.join(raw, "idn_ages_2025.json"), encoding="utf-8"))["districts"]
    for did, x in data.items():
        a = ages.get(x["shape"], {})
        if a: x["ages"] = {g: round(a.get("f" + g, 0) + a.get("m" + g, 0)) for g in ("05", "10", "15")}
        if not x.get("pop") and a: x["pop"], x["pop_wp"] = round(sum(a.values())), True   # three regencies newer than the 2020 series
    # Primary pupils (2025): the ministry's names are "KAB. X" and "KOTA X"; renamed regencies matched by hand.
    PUP_ALIAS = {"baru": "kotabaru", "kendaricity": "kotakendari", "kepulauanseribu": "kepseribu", "kepulauansiautagulandangbiaro": "kepsiautagulandangbiaro",
                 "kotakepulauantidore": "kotatidorekepulauan", "mahakamhulu": "mahakamulu", "malukutenggarabarat": "kepulauantanimbar",
                 "mamujuutara": "pasangkayu", "pangkajenekepulauan": "pangkajenedankepulauan", "pasir": "paser", "pontianak": "mempawah", "tobasamosir": "toba"}
    def pk(n):
        m = re.match(r"(KAB\.|KOTA)\s*(?:ADM\.\s*)?(.*)", n.strip())
        return (("kota" if m.group(1) == "KOTA" else "") + key(m.group(2))) if m else key(n)
    pup, pyears, pubyears = {}, {}, {}
    pf = os.path.join(OUT, "idn_primary_pupils.csv")
    if os.path.exists(pf):
        import csv
        for r in csv.DictReader(open(pf, encoding="utf-8")):
            if r["year"] == "2025": pup.setdefault(pk(r["regency_city"]), {})[r["status"]] = int(r["pupils"])
            if r["status"] == "Negeri dan Swasta": pyears.setdefault(pk(r["regency_city"]), {})[r["year"]] = int(r["pupils"])
            if r["status"] == "Negeri": pubyears.setdefault(pk(r["regency_city"]), {})[r["year"]] = int(r["pupils"])
    for did, x in data.items():
        k = ("kota" if x["kind"].startswith("City") else "") + key(re.sub(r"^Kota ", "", x["name"]))
        p = pup.get(PUP_ALIAS.get(k, k))
        if p: x["pupils"], x["public"] = p.get("Negeri dan Swasta"), p.get("Negeri")
        if pyears.get(PUP_ALIAS.get(k, k)): x["pupil_years"] = dict(sorted(pyears[PUP_ALIAS.get(k, k)].items()))
        kk = PUP_ALIAS.get(k, k)
        if pyears.get(kk) and pubyears.get(kk):   # public schools' share of pupils, each year
            x["public_years"] = {y: round(100 * pubyears[kk][y] / t, 1) for y, t in sorted(pyears[kk].items()) if t and y in pubyears[kk]}
    print("no pupil count:", [x["name"] for x in data.values() if not x.get("pupils")])
    # Current names for regencies renamed since the World Bank's series.
    RENAMED = {"Pasir": "Paser", "Pontianak": "Mempawah", "Mamuju Utara": "Pasangkayu", "Toba Samosir": "Toba", "Maluku Tenggara Barat": "Kepulauan Tanimbar"}
    for x in data.values():
        if x["name"] in RENAMED: x["name"] = RENAMED[x["name"]]
    for f in feats:
        f["properties"]["NAME"] = data[f["properties"]["id"]]["name"]
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "idn_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "idn_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"))
    print(len(data), "regencies and cities; population", sum(x["pop"] or 0 for x in data.values()))


def history(raw):
    """Poverty rate and population for every year from 2010 in the same World Bank INDO-DAPOER downloads (the site
    keeps 2020 as its figure), into idn_data.json's pov_years and pop_years. The names are matched to borders exactly as
    main() does. Regencies split off since 2010 have only the years since they were created, and their parent's
    earlier figures include them (a break the line graphs leave as it is).
    Usage: python3 data-prep/prep_indonesia.py --history RAWDIR"""
    gb = json.load(open(os.path.join(raw, "id_gb_ADM2.geojson"), encoding="utf-8"))["features"]
    byk = {}
    for f in gb: byk.setdefault(key(f["properties"]["shapeName"]), []).append(f)
    load = lambda fn: [x for x in json.load(open(os.path.join(raw, fn), encoding="utf-8"))[1] if x["value"] is not None and x["date"] >= "2010"]
    pov, pop = load("wb45_SI.POV.NAPR.ZS.json"), load("wb45_SP.POP.TOTL.json")
    names = sorted({x["country"]["value"] for x in pov if x["date"] == "2020"})
    did_of, used = {}, set()
    for name in names:   # the same matching as main()
        k = wbkey(name); k = ALIAS.get(k, k)
        fs = byk.get(k) or ([] if k.startswith("kota") else byk.get("kab" + k, []))
        fs = [f for f in fs if f["properties"]["shapeID"] not in used]
        if not fs: continue
        used.add(fs[0]["properties"]["shapeID"]); did_of[name] = "IDN-" + fs[0]["properties"]["shapeID"][-8:]
    p = os.path.join(OUT, "idn_data.json"); data = json.load(open(p, encoding="utf-8"))
    for rows, field, fmt in ((pov, "pov_years", lambda v: round(v, 2)), (pop, "pop_years", lambda v: int(v))):
        for x in rows:
            d = did_of.get(x["country"]["value"])
            if d in data: data[d].setdefault(field, {})[x["date"]] = fmt(x["value"])
    bad = [d for d, x in data.items() if x.get("pov_years", {}).get("2020") not in (None, x.get("pov"))]
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(sum(1 for x in data.values() if len(x.get("pov_years", {})) > 1), "with poverty years;", sum(1 for x in data.values() if len(x.get("pop_years", {})) > 1), "with population years; 2020 mismatches:", bad[:5])


if __name__ == "__main__" and sys.argv[1] == "--history":
    history(sys.argv[2])
elif __name__ == "__main__":
    main(*sys.argv[1:])
