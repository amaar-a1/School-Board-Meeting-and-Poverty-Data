"""Joins the Philippines' poverty estimates to its cities and municipalities (data-prep/inputs/philippines/ph_data.json),
for build_latam.philippines().

Inputs (in inputs/philippines/):
- ph_sae_2018_2021.csv: PSA, Municipal and City Level Small Area Poverty Estimates, 2018 and 2021 ("2018 - 2021
  SAE_with PSGC_noHUC.xlsx", pasted in by the project's owner): poverty incidence among population, coefficient of
  variation and 90% confidence interval, for 1,484 municipalities, 114 component cities and Manila's 14 districts. Old
  six-digit PSGC codes (region, province, municipality). Highly urbanized cities (HUCs) aren't in it.
- psa_t2a_poverty_2018_2023.json: PSA OpenSTAT table 2a (0041F3DF02A), poverty incidence among population by region,
  province and highly urbanized city, 2018, 2021 and 2023 (JSON-stat 1, whose values keep their decimal; the API's CSV
  and JSON-stat 2 round them): the HUCs, Manila as a whole, Pateros, Isabela
  City and Cotabato City.
- ph_municities.geojson: city and municipality borders with 2023 ten-digit PSGC codes (faeldon/philippines-json-maps,
  from PSA and NAMRIA), simplified with mapshaper.
- ph_popproj_admin3_2020_2025.xlsx: PSA mid-year population projections by city and municipality (HDX), July 2021.
Matching: the old code's province and municipality digits (PPMM) against the new code's; places whose codes changed
(Maguindanao, split in 2022 into del Norte and del Sur; Metro Manila; the HUCs) by name. PSA's file misnames two places
(San Miguel for San Manuel, Pangasinan; Candelabra for Candelaria, Zambales): the code wins. The eight municipalities of
the BARMM Special Geographic Area, created in 2024 from Cotabato province villages, have no estimate of their own.
Usage: python3 data-prep/prep_philippines.py
"""
import collections, csv, json, os, re, unicodedata
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "philippines")
def norm(t):
    t = re.sub(r"\s*\(.*?\)|\s*\d+/|\s*[a-c*]+/|\*+", "", str(t))
    t = re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower())
    for x, y in (("cityof", ""), ("city", ""), ("sto", "santo"), ("generaleral", "general")):
        t = t.replace(x, y)
    return re.sub(r"^gen(?!eral)", "general", t)


NIR = {"Negros Occidental", "Negros Oriental", "Siquijor"}


def t2a():
    d = json.load(open(os.path.join(IN, "psa_t2a_poverty_2018_2023.json"), encoding="utf-8"))["dataset"]   # JSON-stat 1 (keeps the decimals)
    lab = lambda k: [d["dimension"][k]["category"]["label"][i] for i in sorted(d["dimension"][k]["category"]["index"], key=lambda i: d["dimension"][k]["category"]["index"][i])]
    d["dimension"] = {k: {"category": {"label": dict(enumerate(lab(k)))}} for k in d["dimension"]["id"]}
    geo = list(d["dimension"]["Geolocation"]["category"]["label"].values())
    par = list(d["dimension"]["Threshold/Incidence/Parameters"]["category"]["label"].values())
    yrs = list(d["dimension"]["Year"]["category"]["label"].values())
    v = d["value"]; n3 = len(par) * len(yrs)
    get = lambda gi, p, y: v[gi * n3 + par.index(p) * len(yrs) + yrs.index(y)]
    out = {}; prov = ""
    for gi, label in enumerate(geo):
        depth = len(label) - len(label.lstrip("."))
        name = re.sub(r"\s*\(w/o.*$", "", label.strip(".")).strip()
        name = re.sub(r"(\s+(\d/|[a-c]/|r\d|\*+),?)+\s*$", "", re.sub(r",\s*$", "", name)).strip().rstrip(",")
        is_prov = depth == 4 and "City" not in name and name != "Pateros"
        if is_prov: prov = name
        out[("prov:" if is_prov else "") + norm(name)] = {"name": name, "province": prov, "pov2021": get(gi, "Poverty Incidence among Population (%)", "2021"),
                           "pov2018": get(gi, "Poverty Incidence among Population (%)", "2018"), "pov2023": get(gi, "Poverty Incidence among Population (%)", "2023"),
                           "cv2021": get(gi, "Coefficient of Variation", "2021")}
    return out


def main():
    feats = {str(f["properties"]["adm3_psgc"]).zfill(10): f["properties"] for f in json.load(open(os.path.join(IN, "ph_municities.geojson"), encoding="utf-8"))["features"]}
    bypm = collections.defaultdict(list)
    for c in feats: bypm[c[3:7]].append(c)
    byname = collections.defaultdict(list)
    for c, p in feats.items(): byname[norm(p["adm3_en"])].append(c)
    sae = list(csv.DictReader(open(os.path.join(IN, "ph_sae_2018_2021.csv"), encoding="utf-8")))
    # The pasted table names a province on its first row only, and once (Surigao del Sur) a few rows late: by code prefix.
    pname = {}
    for r in sae:
        if r["province"] and r["psgc6"][:4] not in pname: pname[r["psgc6"][:4]] = r["province"]
    for r in sae:
        named = [x["province"] for x in sae if x["psgc6"][:4] == r["psgc6"][:4]]
        r["province"] = collections.Counter(named).most_common(1)[0][0]
    # Population, July 2021, by the old code's province and municipality digits, and by name.
    ws = openpyxl.load_workbook(os.path.join(IN, "ph_popproj_admin3_2020_2025.xlsx"), read_only=True)["PopnProj_adm3"]
    it = ws.iter_rows(values_only=True); h = next(it); ix = {k: h.index(k) for k in h}
    poppm, popname = {}, collections.defaultdict(list)
    for row in it:
        if not row[ix["Mun_Pcode"]]: continue
        pc = row[ix["Mun_Pcode"]][2:8]; p = row[ix["July2021"]]
        poppm[pc[2:6]] = p; popname[norm(row[ix["Municipality_City"]])].append((str(row[ix["Municipality_City"]]), str(row[ix["Province"]]), p))
    out = {}
    for r in sae:
        o = r["psgc6"]
        if o.startswith("1339"): continue   # Manila's districts: the city is one border, with table 2a's rate
        c = o[:2] + "0" + o[2:] + "000"
        if c not in feats:
            cs = bypm.get(o[2:6], []); c = cs[0] if len(cs) == 1 else None
        if not c:   # Maguindanao: new codes, by name
            cs = [x for x in byname.get(norm(r["name"]), []) if x.startswith("19087") or x.startswith("19088")]
            c = cs[0] if len(cs) == 1 else None
        assert c and c not in out, (o, r["name"], c)
        f = lambda k: float(r[k]) if r[k] not in ("", None, "None") else None
        out[c] = {"sae_name": r["name"], "province": r["province"], "region": "Negros Island Region (NIR)" if r["province"] in NIR else r["region"],
                  "pov2021": f("pov2021"), "pov2018": f("pov2018"), "cv2021": f("cv2021"), "lo2021": f("lo2021"), "hi2021": f("hi2021"), "source": "sae",
                  "pop2021": poppm.get(o[2:6])}
    hucs = t2a()
    regions = {}
    for c, p in feats.items():
        o = out.setdefault(c, {})
        o.update({"name": p["adm3_en"], "area": (p["area_crs"] / 1e6) if p.get("area_crs") else p.get("area_km2"), "level": p.get("geo_level")})   # area_km2 is rounded to whole km²
        if "pov2021" in o: continue
        t = hucs.get(norm(p["adm3_en"]))
        if t and t["pov2021"] is None and t["pov2018"] is not None:   # San Juan: PSA withheld the 2021 figure as unreliable
            o.update({"source": "est2018", "province": t["province"], "est_pov2018": t["pov2018"], "pov2023": t["pov2023"]})
        elif t and t["pov2021"] is not None:
            o.update({"pov2021": t["pov2021"], "pov2018": t["pov2018"], "pov2023": t["pov2023"], "cv2021": t["cv2021"], "source": "t2a", "province": t["province"]})
        elif c.startswith("19999"):   # BARMM Special Geographic Area (2024)
            ct = hucs["prov:" + norm("Cotabato")]
            o.update({"source": "est", "province": "Special Geographic Area (BARMM)", "region": "Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)",
                      "est_pov2021": ct["pov2021"]})
        pops = popname.get(norm(p["adm3_en"]), [])
        if not o.get("pop2021") and pops:
            if p.get("geo_level") == "City": pops = [x for x in pops if "city" in x[0].lower() or "not a province" in x[1].lower()] or pops
            if len(pops) > 1 and o.get("province"): pops = [x for x in pops if norm(o["province"]) in norm(x[1])] or pops
            if len(pops) == 1 or p.get("geo_level") == "City": o["pop2021"] = max(x[2] for x in pops)
    # Regions for the places taken from table 2a, from their border code's region.
    for c, o in out.items():
        if o.get("region"): regions.setdefault(c[:2], collections.Counter())[o["region"]] += 1
    regions["13"] = collections.Counter({"National Capital Region (NCR)": 1})
    for c, o in out.items():
        if not o.get("region") and c[:2] in regions: o["region"] = regions[c[:2]].most_common(1)[0][0]
    json.dump(out, open(os.path.join(IN, "ph_data.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(out), "places;", collections.Counter(o.get("source") for o in out.values()), "; no rate:", [o["name"] for o in out.values() if o.get("pov2021") is None and o.get("source") != "est"],
          "; no population:", [o["name"] for o in out.values() if not o.get("pop2021")], "; no region:", [o["name"] for o in out.values() if not o.get("region")])


if __name__ == "__main__":
    main()
