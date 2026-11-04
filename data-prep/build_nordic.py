"""Build docs/data/{norway,sweden,finland,denmark,netherlands}.csv and their map files.

Municipalities run schools in these countries, so each municipality is the board equivalent.
- Borders: Eurostat GISCO LAU 2023 (simplified).
- Child low income (each country's own measure, not comparable with each other or the US):
  Norway   SSB 12944: children 0-17 in households with persistent low income (EU 60%), 2022-2024
  Sweden   SCB TAB6685: people 0-19 with low economic standard (60% of median), 2024
  Finland  THL Sotkanet 228: at-risk-of-poverty rate for children (60% of median), latest year
  Denmark  Statistics Denmark LABY07: children 0-17 in relative poverty (50% of median), 2024
  Netherlands CBS 86132NED: children in poverty (CBS's "not much but sufficient" criterion), 2024
- Pupils: SSB 11980 (2025); Kolada N15835 (F-9, home municipality, 2025); Statistics Finland 133w
  (2025); Statistics Denmark LABY23 (Oct 2025); CBS 85701NED (primary, special and secondary by
  municipality of residence, 2025/26).
- Meetings: recordings of the municipality's education or children's committee on its own YouTube channel
  (data-prep/nordic_youtube.py finds the channel; inputs/nordic/youtube/titles.json lists its videos).
  A title counts only if it names such a committee and a meeting, in the country's language (STRICT
  below); children's councils, parent meetings and town-hall meetings don't count.
- Locale (estimated): people per km² from Eurostat's 2023 LAU figures (Finland: children / their share
  of the population, over the municipality's area, since Eurostat's Finnish figures are broken): urban 2,000+ people
  per km², suburban 500-2,000, mixed 100-500, rural under 100.
Usage: python3 data-prep/build_nordic.py
"""
import csv, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "nordic")
DOCS = os.path.join(HERE, "..", "docs", "data")
SHARE = {"NO": 0.21, "SE": 0.23, "FI": 0.19, "DK": 0.115, "NL": 0.19}   # child (or pupil) share of population
NAMES = {"NO": "norway", "SE": "sweden", "FI": "finland", "DK": "denmark", "NL": "netherlands"}
TR = str.maketrans({"ø": "o", "Ø": "o", "æ": "ae", "Æ": "ae", "đ": "d", "ŋ": "n", "ŧ": "t", "š": "s", "á": "a", "č": "c", "ž": "z"})


def norm(s):
    s = str(s).translate(TR)
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())


def variants(s):
    """'Namsos - Nåavmesjenjaelmie', 'Aarborte/Hattfjelldal', 'Herøy (Nordland)' -> every spelling."""
    s = str(s)
    base = re.sub(r"\s*\(.*?\)", "", s)
    out = {norm(s), norm(base)}
    for part in re.split(r"\s+-\s+|/", base):
        out.add(norm(part))
    return {v for v in out if v}


def jsonstat(path, region_dim):
    d = json.load(open(os.path.join(IN, path)))
    idx = d["dimension"][region_dim]["category"]["index"]; lab = d["dimension"][region_dim]["category"]["label"]
    sizes = d["size"]; ids = d["id"]; rpos = ids.index(region_dim)
    stride = 1
    for s in sizes[rpos + 1:]:
        stride *= s
    n_after = stride
    out = {}
    for code, i in idx.items():
        vals = [d["value"][i * n_after + k] for k in range(n_after)]
        out[code] = (lab[code], vals)
    return out


# A title must name a committee (or board) whose name is about schools, education or children.
STRICT = {
    "NO": (r"(hoved)?utvalg(et)?|utvalet|komit[eé]", r"oppvekst|skole|utdanning|levek[aå]r|barn og unge|kunnskap"),
    "SE": (r"n[aä]mnd(en)?s?\b|n[aä]mndens", r"utbildning|bildning|barn|skol|f[oö]rskol|gymnasie"),
    "FI": (r"lautakun|jaosto|n[aä]mnd", r"sivistys|opetus|kasvatus|koulu|bildning|utbildning"),
    "DK": (r"udvalg", r"b[øo]rn|skole|uddannelse|dagtilbud"),
    "NL": (r"commissie", r"onderwijs|jeugd|samenleving|sociaal|welzijn"),
}
# Sweden, Finland and the Netherlands also need a word for the meeting itself (videos about a committee don't count).
MEETW = {"SE": r"sammantr[aä]de|m[oö]te", "FI": r"kokous|sammantr[aä]de", "NL": r"vergadering|\b\d{1,2}[ .-]+(\w+|\d{1,2})[ .-]+20\d\d\b"}   # or a date
NOT = r"commissiekamer|kinderraad|kindergemeenteraad|jeugdraad|jeugdgemeenteraad|foreldrem[øo]te|folkem[øo]te|informasjonsm[øo]te|kontrollutvalg|f[oö]r[aä]ldram[oö]te|ungebyr[aå]d|kulturskolen|rapport fr[aå]n"


def strict_count(cc, titles):
    unit, topic = (re.compile(x, re.I) for x in STRICT[cc])
    mw = re.compile(MEETW.get(cc, "."), re.I)
    keep = [t for t in titles if unit.search(t) and topic.search(t) and mw.search(t) and not re.search(NOT, t, re.I)]
    return len({re.sub(r"\b(del|osa|deel|part|video)\s*\d+(\s*(av|af|van|/)\s*\d+)?\b|\(\d\)|\d/\d\s*$", "", t, flags=re.I).strip().lower() for t in keep}), keep[:3]


def meetings(cc):
    """{District ID: (count, channel URL, examples)} from the YouTube search and title lists."""
    f = os.path.join(IN, "youtube", f"{cc}_youtube.csv")
    tf = os.path.join(IN, "youtube", "titles.json")
    if not os.path.exists(f):
        return {}
    titles = json.load(open(tf, encoding="utf-8")) if os.path.exists(tf) else {}
    out = {}
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if not r["Channel URL"]:
            continue
        n, ex = strict_count(cc, titles[r["Channel URL"]]) if r["Channel URL"] in titles else (0, [])
        out[r["District ID"]] = (n, r["Channel URL"], ex)
    return out


def locale(kids, share, area):
    dens = kids / share / area if area else 0
    return ("Urban" if dens >= 2000 else "Suburban" if dens >= 500 else "Mixed" if dens >= 100 else "Rural"), round(dens)


def main():
    for cc, key in NAMES.items():
        geo = json.load(open(os.path.join(IN, f"lau_{cc}.geojson")))
        rows = {}
        for f in geo["features"]:
            p = f["properties"]
            rows[p["LAU_ID"]] = {"District": p["LAU_NAME"], "Available Board Meetings": 0, "Meetings source": "",
                                 "Children": "", "Children in Low Income": "", "Percentage of Children in Low Income": "",
                                 "Enrollment": "", "Enrollment year": "", "District ID": f"{cc}-{p['LAU_ID']}", "_area": area_km2(f["geometry"]),
                                 "_dens": p.get("POP_DENS_2023") if cc != "FI" else None}
        if cc == "NL":   # Brielle, Hellevoetsluis and Westvoorne merged into Voorne aan Zee (GM1992) in 2023
            parts = [f for f in geo["features"] if f["properties"]["LAU_ID"] in ("GM0501", "GM0530", "GM0614")]
            if parts:
                polys = []
                for f in parts:
                    g = f["geometry"]; polys += g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
                    rows.pop(f["properties"]["LAU_ID"], None)
                geo["features"] = [f for f in geo["features"] if f not in parts] + [{"type": "Feature", "properties": {"LAU_ID": "GM1992", "LAU_NAME": "Voorne aan Zee"}, "geometry": {"type": "MultiPolygon", "coordinates": polys}}]
                g = geo["features"][-1]
                rows["GM1992"] = {**{k: "" for k in ("Meetings source", "Children", "Children in Low Income", "Percentage of Children in Low Income", "Enrollment", "Enrollment year")},
                                  "District": "Voorne aan Zee", "Available Board Meetings": 0, "District ID": "NL-GM1992", "_area": area_km2(g["geometry"])}
        if cc == "NO":
            for r in rows.values():
                r["District"] = {"Gjemmes": "Gjemnes"}.get(r["District"], r["District"])
        byname = {norm(r["District"]): k for k, r in rows.items()}
        for k, r in rows.items():
            for v in variants(r["District"]):
                byname.setdefault(v, k)
        def put(code=None, name=None, **kv):
            if name and re.search(r"\((\d{4})?-\d{4}\)", str(name)):
                return "old"   # a former municipality (SSB keeps them with a year range)
            k = code if code in rows else (byname.get(norm(name)) or next((byname[v] for v in variants(name) if v in byname), None)) if name else None
            if k:
                rows[k].update(kv)
            return k
        miss = []
        if cc == "NO":
            li = jsonstat("no_lowincome.json", "Region")
            for code, (lab, (n, pct)) in li.items():
                if len(code) == 4 and n is not None and pct:
                    if not put(name=lab, **{"Children in Low Income": n, "Percentage of Children in Low Income": f"{pct:.2f}%", "Children": round(n / pct * 100)}):
                        miss.append(lab)
            for code, (lab, (n,)) in jsonstat("no_pupils.json", "KOKkommuneregion0000").items():
                if n: put(name=lab, **{"Enrollment": n, "Enrollment year": "2025"})
        elif cc == "SE":
            for r in csv.DictReader(open(os.path.join(IN, "se_lowincome.csv"), encoding="utf-8-sig")):
                pct, n = r["000008AC 2024"], r["000008AE 2024"]
                if pct not in ("", ".", ".."):
                    put(code=r["Region"], **{"Percentage of Children in Low Income": f"{float(pct):.2f}%", "Children": int(float(n)),
                                             "Children in Low Income": round(float(n) * float(pct) / 100)})
            for v in json.load(open(os.path.join(IN, "se_pupils_N15835_2025.json")))["values"]:
                t = [x for x in v["values"] if x["gender"] == "T" and x["value"] is not None]
                if t: put(code=v["municipality"], **{"Enrollment": round(t[0]["value"]), "Enrollment year": "2025"})
        elif cc == "FI":
            reg = {r["id"]: r for r in json.load(open(os.path.join(IN, "fi_regions.json")))}
            vals = {}
            for v in json.load(open(os.path.join(IN, "fi_228.json"))):
                if v["region"] in reg and v.get("value") is not None and (v["region"] not in vals or v["year"] > vals[v["region"]]["year"]):
                    vals[v["region"]] = v
            for rid, v in vals.items():
                code = str(int(reg[rid]["code"]))
                kids = round(v["absValue"] / v["value"] * 100) if v.get("absValue") and v["value"] else ""
                put(code=code, name=reg[rid]["name"], **{"Percentage of Children in Low Income": f"{v['value']:.2f}%", "Children in Low Income": v.get("absValue") or "", "Children": kids})
            for code, (lab, (n,)) in jsonstat("fi_pupils.json", "alue_23_20250101").items():
                if code.startswith("KU") and n: put(code=str(int(code[2:])), name=lab, **{"Enrollment": n, "Enrollment year": "2025"})
        elif cc == "DK":
            alias = {"copenhagen": "kobenhavn", "aarhus": "aarhus", "hojetaastrup": "hojetaastrup"}
            for r in csv.DictReader(open(os.path.join(IN, "dk_LABY07.csv"), encoding="utf-8-sig"), delimiter=";"):
                nm = alias.get(norm(r["KOMGRP"]), norm(r["KOMGRP"]))
                if nm in byname: rows[byname[nm]]["Percentage of Children in Low Income"] = f"{float(r['INDHOLD']):.2f}%"
            for r in csv.DictReader(open(os.path.join(IN, "dk_LABY23.csv"), encoding="utf-8-sig"), delimiter=";"):
                nm = alias.get(norm(r["KOMGRP"]), norm(r["KOMGRP"]))
                if nm in byname: rows[byname[nm]].update({"Enrollment": int(r["INDHOLD"]), "Enrollment year": "October 2025"})
        elif cc == "NL":
            best = {}
            for v in json.load(open(os.path.join(IN, "nl_childpoverty.json")))["value"]:
                g = v["RegioS"].strip()
                if g.startswith("GM") and v["KinderenArmRelatief_4"] is not None and (g not in best or v["Perioden"] > best[g]["Perioden"]):
                    best[g] = v
            for g, v in best.items():
                put(code=g, **{"Percentage of Children in Low Income": f"{v['KinderenArmRelatief_4']:.2f}%", "Children": round(v["KinderenTotaal_1"] * 1000),
                               "Children in Low Income": round(v["KinderenTotaal_1"] * 10 * v["KinderenArmRelatief_4"])})   # CBS counts are in thousands
            tot = {}
            for v in json.load(open(os.path.join(IN, "nl_pupils.json")))["value"]:
                if v["LeerlingenStudenten_1"]:
                    tot[v["Regiokenmerken"].strip()] = tot.get(v["Regiokenmerken"].strip(), 0) + v["LeerlingenStudenten_1"]
            for g, n in tot.items():
                put(code=g, **{"Enrollment": n, "Enrollment year": "2025/26"})
        meet = meetings(cc)
        for k, r in rows.items():
            if r["District ID"] in meet:
                n, url, ex = meet[r["District ID"]]
                r["Available Board Meetings"] = n
                r["Meetings source"] = url
        out = []
        for k, r in rows.items():
            basis = float(r["Enrollment"] or 0) if cc == "DK" else float(r["Children"] or 0)
            area, dens = r.pop("_area"), r.pop("_dens", None)
            if dens:   # Eurostat's 2023 density (its Finnish figures are broken, so Finland is estimated)
                r["People per km² (estimated)"] = round(dens)
                r["Locale"] = locale(dens, 1, 1)[0]
            else:
                r["Locale"], r["People per km² (estimated)"] = locale(basis, SHARE[cc], area)
            out.append(r)
        out.sort(key=lambda r: r["District"])
        cols = ["District", "Locale", "Available Board Meetings", "Meetings source", "Children", "Children in Low Income",
                "Percentage of Children in Low Income", "Enrollment", "Enrollment year", "People per km² (estimated)", "District ID"]
        with open(os.path.join(DOCS, f"{key}.csv"), "w", newline="", encoding="utf-8") as fo:
            w = csv.DictWriter(fo, fieldnames=cols); w.writeheader(); w.writerows(out)
        for f in geo["features"]:
            f["properties"] = {"id": f"{cc}-{f['properties']['LAU_ID']}", "NAME": f["properties"]["LAU_NAME"]}
        json.dump(geo, open(os.path.join(DOCS, "map", f"{key}.json"), "w"), separators=(",", ":"))
        np_ = sum(1 for r in out if r["Percentage of Children in Low Income"]); ne = sum(1 for r in out if r["Enrollment"])
        print(cc, len(out), "municipalities; low income for", np_, "; pupils for", ne, "; not matched:", miss[:8])
        print("   no low income:", [r["District"] for r in out if not r["Percentage of Children in Low Income"]][:12])
        print("   no pupils:", [r["District"] for r in out if not r["Enrollment"]][:12])


if __name__ == "__main__":
    main()
