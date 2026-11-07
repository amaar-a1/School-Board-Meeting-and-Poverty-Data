"""Adds a "Region" column (county, region, province or island) to the countries whose builds have none, for the
site's region menu. Run after the builds (build_nordic.py, build_iceland.py, build_switzerland.py, build_nz.py
call it), or on its own: python3 add_regions.py

- Norway: today's 15 counties (fylker). The municipality codes are from before the 2024 county split, so the
  municipalities of Viken, Vestfold og Telemark and Troms og Finnmark are placed by name.
- Sweden: the 21 counties (län), from the first two digits of the municipality code.
- Denmark: the 5 regions, from the municipality code.
- Finland: the 19 regions (maakunnat), from Statistics Finland's municipality-to-region table (2026).
- Netherlands: the 12 provinces, from the province borders (geoBoundaries ADM1).
- Iceland: the 8 regions (landshlutar), from the first digit of the municipality number.
- Switzerland: the 7 statistical regions (Grossregionen) the cantons belong to.
- New Zealand: North Island or South Island.
"""
import csv, json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs", "data")
IN = os.path.join(HERE, "inputs")

NO = {"03": "Oslo", "11": "Rogaland", "15": "Møre og Romsdal", "18": "Nordland", "34": "Innlandet", "42": "Agder", "46": "Vestland", "50": "Trøndelag"}
NO_SPLIT = {   # the 2020-2023 counties split in 2024, by municipality
    "Østfold": "Halden Moss Sarpsborg Fredrikstad Hvaler Aremark Marker Indre_Østfold Skiptvet Rakkestad Råde Våler",
    "Akershus": "Bærum Asker Lillestrøm Nordre_Follo Ullensaker Nesodden Frogn Vestby Ås Enebakk Lørenskog Rælingen Aurskog-Høland Nes Gjerdrum Nittedal Lunner Eidsvoll Nannestad Hurdal",
    "Buskerud": "Drammen Kongsberg Ringerike Hole Flå Nesbyen Gol Hemsedal Ål Hol Sigdal Krødsherad Modum Øvre_Eiker Lier Flesberg Rollag Nore_og_Uvdal Jevnaker",
    "Vestfold": "Horten Holmestrand Tønsberg Sandefjord Larvik Færder",
    "Telemark": "Porsgrunn Skien Notodden Siljan Bamble Kragerø Drangedal Nome Midt-Telemark Seljord Hjartdal Tinn Kviteseid Nissedal Fyresdal Tokke Vinje",
    "Finnmark": "Alta Hammerfest Vardø Vadsø Kautokeino Guovdageaidnu Loppa Hasvik Måsøy Nordkapp Porsanger Karasjok Lebesby Gamvik Berlevåg Tana Deatnu Nesseby Unjárga Båtsfjord Sør-Varanger",
    "Troms": "Tromsø Harstad Kvæfjord Tjeldsund Ibestad Gratangen Lavangen Bardu Salangen Målselv Sørreisa Dyrøy Senja Balsfjord Karlsøy Lyngen Storfjord Kåfjord Skjervøy Nordreisa Kvænangen",
}
SE = {"01": "Stockholm", "03": "Uppsala", "04": "Södermanland", "05": "Östergötland", "06": "Jönköping", "07": "Kronoberg", "08": "Kalmar",
      "09": "Gotland", "10": "Blekinge", "12": "Skåne", "13": "Halland", "14": "Västra Götaland", "17": "Värmland", "18": "Örebro",
      "19": "Västmanland", "20": "Dalarna", "21": "Gävleborg", "22": "Västernorrland", "23": "Jämtland", "24": "Västerbotten", "25": "Norrbotten"}
DK = {
    "Hovedstaden (Capital Region)": "101 147 151 153 155 157 159 161 163 165 167 169 173 175 183 185 187 190 201 210 217 219 223 230 240 250 260 270 400 411",
    "Sjælland (Zealand)": "253 259 265 269 306 316 320 326 329 330 336 340 350 360 370 376 390",
    "Syddanmark (Southern Denmark)": "410 420 430 440 450 461 479 480 482 492 510 530 540 550 561 563 573 575 580 607 621 630",
    "Midtjylland (Central Jutland)": "615 657 661 665 671 706 707 710 727 730 740 741 746 751 756 760 766 779 791",
    "Nordjylland (North Jutland)": "773 787 810 813 820 825 840 846 849 851 860",
}
DK = {c: k for k, v in DK.items() for c in v.split()}
IS = {"0": "Capital Region", "1": "Capital Region", "2": "Southern Peninsula", "3": "Western Region", "4": "Westfjords",
      "5": "Northwestern Region", "6": "Northeastern Region", "7": "Eastern Region", "8": "Southern Region"}
CH = {"Lake Geneva Region": "Vaud Valais Geneva", "Espace Mittelland": "Bern Fribourg Solothurn Neuchâtel Jura",
      "Northwestern Switzerland": "Basel-Stadt Basel-Landschaft Aargau", "Zürich": "Zürich",
      "Eastern Switzerland": "Glarus Schaffhausen Appenzell_Ausserrhoden Appenzell_Innerrhoden Sankt_Gallen Graubünden Thurgau",
      "Central Switzerland": "Lucerne Uri Schwyz Obwalden Nidwalden Zug", "Ticino": "Ticino"}
CH = {n.replace("_", " "): k for k, v in CH.items() for n in v.split()}
FIXES = {"NL-GM0376": "Noord-Holland"}   # Blaricum: its centroid falls just inside the simplified Utrecht border
NZ_SOUTH = {"NZ-TNMW", "NZ-CAN", "NZ-OTA", "NZ-STL"}


def norm(s):
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s.replace("ø", "o").replace("Ø", "O").replace("æ", "ae").replace("å", "a")).encode("ascii", "ignore").decode().lower())


NO_BY_NAME = {norm(n.replace("_", " ")): k for k, v in NO_SPLIT.items() for n in v.split()}


def pip(pt, geom):
    x, y = pt
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    inside = False
    for poly in polys:
        ring = poly[0]
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]; xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: inside = not inside
            j = i
    return inside


def centroid(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    ring = max((p[0] for p in polys), key=len)
    return sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)


def by_borders(key, adm1_file, names=None):
    """{District ID: region} from the place's own border (its biggest polygon's centroid), else the nearest region."""
    adm1 = json.load(open(os.path.join(IN, "nordic", adm1_file), encoding="utf-8"))["features"]
    mp = json.load(open(os.path.join(DOCS, "map", f"{key}.json"), encoding="utf-8"))["features"]
    out = {}
    for f in mp:
        c = centroid(f["geometry"])
        hit = next((a for a in adm1 if pip(c, a["geometry"])), None)
        if not hit:   # a coastal or island centroid that falls just outside the simplified region
            hit = min(adm1, key=lambda a: (centroid(a["geometry"])[0] - c[0]) ** 2 + (centroid(a["geometry"])[1] - c[1]) ** 2)
        n = hit["properties"]["shapeName"]
        out[f["properties"]["id"]] = (names or {}).get(n, n)
    return out


def region(key, r, lookup):
    did = r["District ID"]; code = did.split("-", 1)[1]
    if key == "norway":
        if code[:2] in NO: return NO[code[:2]]
        name = re.sub(r"\s*\(.*?\)", "", r["District"])   # "Våler (Viken)"
        for part in re.split(r"\s*[/–-]\s*|\s+-\s+", name) + [name]:
            if norm(part) in NO_BY_NAME: return NO_BY_NAME[norm(part)]
        return ""
    if key == "sweden": return SE.get(code[:2], "")
    if key == "denmark": return DK.get(code, "")
    if key == "iceland": return IS.get(code[0], "")
    if key == "switzerland": return CH.get(r["District"], "")
    if key == "new-zealand": return "South Island" if did in NZ_SOUTH else "North Island"
    return FIXES.get(did) or lookup.get(did, "")


def add(key):
    path = os.path.join(DOCS, f"{key}.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    cols = list(rows[0].keys())
    lookup = {}
    if key == "finland":
        # Statistics Finland's municipality-to-region table (2026); the borders only for a municipality it lacks.
        lookup = by_borders(key, "gb_FIN_ADM1.geojson", {"Keski-Pohjanmaa": "Central Ostrobothnia", "Åland Islands": "Åland", "Southern Savonia": "South Savo", "Northern Savonia": "North Savo", "Northern Ostrobothnia": "North Ostrobothnia", "Finland Proper": "Southwest Finland", "Tavastia Proper": "Kanta-Häme"})
        fi = json.load(open(os.path.join(IN, "nordic", "fi_kunta_maakunta_2026.json"), encoding="utf-8"))
        lookup.update({f"FI-{c}": n for c, n in fi.items()})
    if key == "netherlands": lookup = by_borders(key, "gb_NLD_ADM1.geojson")
    for r in rows: r["Region"] = region(key, r, lookup)
    if "Region" not in cols: cols.insert(1, "Region")
    with open(path, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=cols); w.writeheader(); w.writerows(rows)
    miss = [r["District"] for r in rows if not r["Region"]]
    counts = {}
    for r in rows: counts[r["Region"]] = counts.get(r["Region"], 0) + 1
    print(key, len(rows), "rows;", len(counts), "regions;", "no region:", miss[:10])
    return counts


if __name__ == "__main__":
    for k in ("norway", "sweden", "denmark", "iceland", "switzerland", "new-zealand", "finland", "netherlands"):
        if k in ("finland", "netherlands") and not os.path.exists(os.path.join(IN, "nordic", f"gb_{'FIN' if k == 'finland' else 'NLD'}_ADM1.geojson")):
            print(k, "skipped: no region borders yet"); continue
        print(add(k))
