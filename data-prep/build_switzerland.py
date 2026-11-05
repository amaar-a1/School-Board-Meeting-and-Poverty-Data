"""Build docs/data/switzerland.csv and docs/data/map/switzerland.json: Switzerland's 26 cantons.

Swiss schooling is run by the cantons (each has its own education department and law); within a
canton, municipalities or school communities often have an elected school board (Schulpflege,
Schulkommission, commission scolaire), but there are about 2,000 of them and no figures below the
canton, so the site shows the cantons.
- Child poverty: Federal Statistical Office (BFS), social assistance statistics, table
  px-x-1304030000_121: the social assistance rate (Sozialhilfequote) for ages 0-17, 2025.
- Enrollment: BFS px-x-1502010100_101, pupils in compulsory school by school canton, 2024/25.
- Meetings (stand-in): sittings of the cantonal parliament (Kantonsrat, Grosser Rat, Landrat, Grand
  Conseil, Gran Consiglio), which passes the canton's school law and budget, on YouTube
  (data-prep/islands_youtube.py, "europe"; channels checked by hand in CHANNELS), one per day.
- Borders: Natural Earth 1:10m admin-1. Locale (estimated): children / 0.19 over area.
Usage: python3 data-prep/build_switzerland.py
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2
from build_islands import sittings

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "switzerland")
DOCS = os.path.join(HERE, "..", "docs", "data")
BFS = {"Zürich": "ZH", "Bern / Berne": "BE", "Luzern": "LU", "Uri": "UR", "Schwyz": "SZ", "Obwalden": "OW", "Nidwalden": "NW", "Glarus": "GL",
       "Zug": "ZG", "Fribourg / Freiburg": "FR", "Solothurn": "SO", "Basel-Stadt": "BS", "Basel-Landschaft": "BL", "Schaffhausen": "SH",
       "Appenzell Ausserrhoden": "AR", "Appenzell Innerrhoden": "AI", "St. Gallen": "SG", "Graubünden / Grigioni / Grischun": "GR",
       "Aargau": "AG", "Thurgau": "TG", "Ticino": "TI", "Vaud": "VD", "Valais / Wallis": "VS", "Neuchâtel": "NE", "Genève": "GE", "Jura": "JU"}
NAME = {"BE": "Bern", "FR": "Fribourg", "GR": "Graubünden", "VS": "Valais", "GE": "Geneva", "LU": "Lucerne"}
LANG = {"FR": "French", "VD": "French", "NE": "French", "GE": "French", "JU": "French", "VS": "French", "TI": "Italian"}
# Channels checked by hand: "all" is the parliament's own channel; "filter" a government channel or regional
# broadcaster, where only titles naming the parliament count. Cantons not listed: no recordings found on YouTube.
CHANNELS = {
    "SZ": ("https://www.youtube.com/channel/UC-jiMEbJjtTD4brzJutz5qg", "all", "Kantonsrat des Kantons Schwyz"),
    "AG": (None, "all", "Grosser Rat Kanton Aargau"),
    "VD": ("https://www.youtube.com/channel/UC62cOgKBko9NLJNZsW69n1A", "all", "Grand Conseil vaudois"),
    "GL": ("https://www.youtube.com/channel/UC0_fxWAMBk1D-Wcfb0rkWYA", "all", "Landrat des Kantons Glarus"),
    "LU": ("https://www.youtube.com/channel/UCbMJiK6gyIK1IaF61_Y2oBg", "filter", "Kanton Luzern"),
    "BS": (None, "filter", "Kanton Basel-Stadt"), "AR": (None, "filter", "Kanton Appenzell Ausserrhoden"),
    "SG": (None, "filter", "Kanton St.Gallen “St.Gallen”"), "TG": (None, "filter", "Kanton Thurgau"),
    "TI": (None, "filter", "Repubblica e Cantone Ticino"), "JU": (None, "filter", "République et Canton du Jura"),
    "BL": (None, "filter", "regioTvplus"), "SH": (None, "filter", "swissbroadcast"),
}
NAMEWORDS = {"BL": r"basel-landschaft|baselland", "SH": r"schaffhaus"}


def jsonstat(path):
    d = json.load(open(os.path.join(IN, path), encoding="utf-8"))
    ids, size = d["id"], d["size"]; cat = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
    lab = {k: d["dimension"][k]["category"]["label"] for k in ids}
    def v(**sel):
        full = {k: cat[k][0] for k in ids}; full.update(sel); i = 0
        for k, n in zip(ids, size): i = i * n + cat[k].index(full[k])
        return d["value"][i]
    return cat, lab, v


def main():
    import re
    cat, lab, v = jsonstat("bfs_social_assistance.json")
    age = next(k for k, t in lab["Altersklasse"].items() if t.startswith("0-17"))
    ab = list(lab["Absolut / relativ"]); year = cat["Jahr"][-1]
    sa = {}
    for k in cat["Kanton"]:
        t = lab["Kanton"][k]
        if t in BFS: sa[BFS[t]] = (v(Kanton=k, Altersklasse=age, **{"Absolut / relativ": ab[0], "Jahr": year}), v(Kanton=k, Altersklasse=age, **{"Absolut / relativ": ab[1], "Jahr": year}))
    pcat, plab, pv = jsonstat("bfs_pupils.json")
    pyear = pcat["Jahr"][-1]
    pupils = {BFS[plab["Schulkanton"][k]]: pv(Schulkanton=k, Jahr=pyear) for k in pcat["Schulkanton"] if plab["Schulkanton"][k] in BFS}
    chans = json.load(open(os.path.join(IN, "youtube", "channels.json"), encoding="utf-8"))
    titles = json.load(open(os.path.join(IN, "youtube", "titles.json"), encoding="utf-8"))
    url_of = {c["name"]: c["url"] for x in chans.values() for c in x.get("channels", [])}
    geo = json.load(open(os.path.join(IN, "ch_cantons.geojson"), encoding="utf-8"))
    rows, feats = [], []
    for f in sorted(geo["features"], key=lambda f: f["properties"]["iso_3166_2"]):
        code = f["properties"]["iso_3166_2"][3:]
        n_sa, rate = sa[code]
        kids = round(n_sa / rate * 100) if rate else ""
        dens = (kids / 0.19 / area_km2(f["geometry"])) if kids else 0
        url, mode, cname = CHANNELS.get(code, (None, None, None))
        url = url or (url_of.get(cname) if cname else None)
        n, note = 0, "No school board meets above the municipal level; no recorded sittings of the cantonal parliament were found on YouTube (most stream on their own websites)"
        if url and url in titles:
            vids = titles[url]
            if code in NAMEWORDS: vids = [t for t in vids if re.search(NAMEWORDS[code], t, re.I)]
            n = sittings(vids, mode)[0]
            if n: note = f"Stand-in: recorded sittings of the cantonal parliament on {cname}'s YouTube channel, one per day"
        rows.append({"District": NAME.get(code, f["properties"]["name"]), "Language": LANG.get(code, "German"),
                     "Locale": "Urban" if dens >= 2000 else "Suburban" if dens >= 500 else "Mixed" if dens >= 100 else "Rural",
                     "Available Board Meetings": n, "Meetings source": url if n else "", "Meetings note": note,
                     "Children": kids, "Children in Low Income": round(n_sa), "Percentage of Children in Low Income": f"{rate:.2f}%",
                     "Enrollment": round(pupils[code]), "Enrollment year": pyear, "People per km² (estimated)": round(dens), "District ID": f"CH-{code}"})
        rnd = lambda c: [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]
        feats.append({"type": "Feature", "properties": {"id": f"CH-{code}", "NAME": rows[-1]["District"]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    rows.sort(key=lambda r: r["District"])
    with open(os.path.join(DOCS, "switzerland.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", "switzerland.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for r in rows: print(f'{r["District"]:24} {r["Percentage of Children in Low Income"]:>7} {r["Enrollment"]:>7} {r["Locale"]:9} {r["Available Board Meetings"]}')


if __name__ == "__main__":
    main()
