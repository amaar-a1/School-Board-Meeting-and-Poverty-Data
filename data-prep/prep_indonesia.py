"""Turns the Indonesia downloads (made on GitHub's runner, fetch rounds 29-30) into the inputs build_latam.indonesia() reads
(data-prep/inputs/indonesia/).

- Poverty and population: Statistics Indonesia (BPS) figures for each regency (kabupaten) and city (kota), 2020, as
  published in the World Bank's Indonesia Database for Policy and Economic Research (INDO-DAPOER, World Bank API source
  45): the poverty rate (share of people below BPS's poverty line, all ages; SI.POV.NAPR.ZS) and the population
  (SP.POP.TOTL). BPS's own site doesn't answer GitHub's servers.
- Borders: geoBoundaries (gbOpen) IDN ADM2, simplified; each regency's province from the ADM1 borders it lies in.
  Names: "X, Kab." is the border "X", and "X, Kota" the border "Kota X".
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
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "idn_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "idn_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"))
    print(len(data), "regencies and cities; population", sum(x["pop"] or 0 for x in data.values()))


if __name__ == "__main__":
    main(*sys.argv[1:])
