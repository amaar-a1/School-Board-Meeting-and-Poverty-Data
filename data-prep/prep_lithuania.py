"""Turns the Lithuania downloads (made on GitHub's runner from the Official Statistics Portal's SDMX API,
osp-rs.stat.gov.lt/rest_json/data/<dataflow>) into the small inputs build_latam.lithuania() reads (data-prep/inputs/lithuania/).

- ltu_geo.geojson: the 60 municipalities (savivaldybės), from geoBoundaries gbOpen LTU ADM2 (simplified), matched by name.
- ltu_data.json, per municipality (the portal's code):
  poverty: S3R453_M3080308, at-risk-of-poverty rate by municipality (latest year);
  social: S3R0243_M3160702, social assistance benefit recipients per 1,000 residents (latest year);
  meals: S3R358_M3160909_1, pupils receiving free school meals (latest year);
  pupils: S3R057_M3110302_3, general school pupils (latest school year);
  pop, children: S3R167_M3010213, residents at the start of the year, all ages and aged 0-15 (latest year).
  meetings: the municipal council's YouTube channel (fetch/nyt.py, LT).
Then, after build_latam.py, run data-prep/simplify_borders.sh (a lighter copy of the map file for zoomed-out views).
Usage: python3 data-prep/prep_lithuania.py RAWDIR GEODIR WIKI_HTML (English Wikipedia, "Municipalities of Lithuania", action=render)
"""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "lithuania")
fold = lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def read(path):
    """SDMX-JSON -> (dims [(id, {code: name})], {codes tuple: value})."""
    d = json.load(open(path, encoding="utf-8"))
    dims = [(x["id"], [(v["id"], v["name"]) for v in x["values"]]) for x in d["structure"]["dimensions"]["observation"]]
    obs = {tuple(dims[i][1][j][0] for i, j in enumerate(map(int, k.split(":")))): v[0] for k, v in d["dataSets"][0]["observations"].items()}
    return [(i, dict(v)) for i, v in dims], obs


def latest(path, **fix):
    """{municipality code: value} for the latest period, other dimensions fixed by name=code."""
    dims, obs = read(path)
    ids = [i for i, _ in dims]
    per = max(dims[ids.index("LAIKOTARPIS")][1])
    out = {}
    for k, v in obs.items():
        k = dict(zip(ids, k))
        if k["LAIKOTARPIS"] == per and all(k.get(a) == b for a, b in fix.items()) and v is not None:
            out[k["savivaldybesRegdb"]] = v
    return per, out, dims[0][1]


def key(name):
    """('kaun', 'm') for "Kauno m. sav." and "Kaunas City Municipality"; kind r (district), m (city) or '' (plain)."""
    f = fold(name)
    kind = "m" if re.search(r"\bm\.|miesto|\bcity\b", f) else "r" if re.search(r"\br\.|rajono|district", f) else ""
    return fold(name.split()[0])[:4], kind


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def english(path):
    """{key: English name} from English Wikipedia's "Municipalities of Lithuania" table ("Akmenė District Municipality")."""
    import html as H
    cl = lambda c: re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>|\[\d+\]", "", c))).strip()
    s = open(path, encoding="utf-8").read()
    out = {}
    for t in re.findall(r"<table.*?</table>", s, re.S):
        for r in re.findall(r"<tr.*?</tr>", t, re.S):
            c = [cl(x) for x in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
            n = next((x for x in c if x.endswith("Municipality")), None)
            if n: out[key(n)] = n
    return out


def main(raw, geo, wiki=None):
    p = lambda f: os.path.join(raw, f)
    en = english(wiki) if wiki else {}
    py, pov, names = latest(p("lt_S3R453_M3080308.json"))
    sy, soc, _ = latest(p("lt_S3R0243_M3160702.json"), Lytis="0")
    my, meals, _ = latest(p("lt_S3R358_M3160909_1.json"))
    uy, pupils, _ = latest(p("lt_S3R057_M3110302_3.json"))
    ny, pop, _ = latest(p("lt_S3R167_M3010213.json"), Lytis="0", amziusREGM1040112="g000g999")
    _, kids, _ = latest(p("lt_S3R167_M3010213.json"), Lytis="0", amziusREGM1040112="g000g015")
    muni = {c: n for c, n in names.items() if n.endswith("sav.")}
    assert len(muni) == 60, len(muni)
    g = {key(f["properties"]["shapeName"]): f for f in json.load(open(os.path.join(geo, "geoBoundaries-LTU-ADM2_simplified.geojson"), encoding="utf-8"))["features"]}
    data, feats = {}, []
    for c, n in sorted(muni.items()):
        f = g.pop(key(n))
        data[c] = {"name": n, "en": en.get(key(n), ""), "poverty": pov.get(c), "social": soc.get(c), "meals": meals.get(c), "pupils": pupils.get(c),
                   "pop": pop.get(c), "children": kids.get(c)}
        feats.append({"type": "Feature", "properties": {"id": f"LTU-{c}", "NAME": n},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    assert not g, g.keys()
    data["_years"] = {"poverty": py, "social": sy, "meals": my, "pupils": uy, "pop": ny}
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "ltu_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "ltu_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(data["_years"], sum(x["pop"] or 0 for k, x in data.items() if k != "_years"), sum(x["pupils"] or 0 for k, x in data.items() if k != "_years"),
          [k for k, x in data.items() if k != "_years" and None in x.values()])


if __name__ == "__main__":
    main(*sys.argv[1:])
