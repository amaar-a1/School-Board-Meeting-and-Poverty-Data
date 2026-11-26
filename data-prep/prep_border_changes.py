"""Municipal mergers since the population series start (2016), for data-prep/inputs/border_changes.json (borders.py).

  python3 data-prep/prep_border_changes.py france v_mvt_commune_2026.csv
  python3 data-prep/prep_border_changes.py italy  Variazioni_amministrative_territoriali_dal_01011991.xlsx
  python3 data-prep/prep_border_changes.py netherlands DIR_WITH_nl_YYYY.html

- France: INSEE, Code officiel géographique, "mouvements des communes" (fetch round 56): mergers (MOD 31-33: fusion
  simple, création de commune nouvelle, fusion-association), each former commune to the commune it joined; and code
  changes (MOD 41, 50), the same place under a new code; a merger later undone (MOD 21) is left out. A change takes effect in the population of the next
  1 January (Eurostat's LAU figures are for 1 January).
- Italy: ISTAT, "Variazioni amministrative e territoriali dal 1991" (fetch round 57): each suppressed municipality
  (ES) to the one it joined, a new one (CS) or an existing one that took it in (AQES, which is then a former place too);
  and code changes (AP: a move to another province), the same place under a new code. Smaller transfers of land
  between municipalities (AQ, CE) aren't followed.
- Netherlands: CBS, "Gemeentelijke indeling op 1 januari YYYY" (fetch round 59), the tables of municipalities
  abolished and the ones they formed or joined, 2012-2026. A municipality divided among several (Haaren, 2021) is
  only marked on the ones that took part of it: its parts can't be told apart.
Each list is written in Eurostat's LAU codes (FR_xxxxx, ...), with the years from the first one after 2016.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "border_changes.json")


def first_jan(date):
    y = int(date[:4])
    return str(y if date[5:] == "01-01" else y + 1)


def france(path):
    groups = {}
    for x in csv.DictReader(open(path, encoding="utf-8")):
        if x["MOD"] in ("31", "32", "33", "41", "50") and x["TYPECOM_AV"] == "COM" and x["TYPECOM_AP"] == "COM":
            F = first_jan(x["DATE_EFF"])
            if F <= "2016": continue
            g = groups.setdefault((F, x["COM_AP"]), {"year": F, "into": "FR_" + x["COM_AP"], "name": x["LIBELLE_AP"], "from": [], "names": [], "rename": x["MOD"] in ("41", "50")})
            if "FR_" + x["COM_AV"] not in g["from"]:
                g["from"].append("FR_" + x["COM_AV"]); g["names"].append(x["LIBELLE_AV"])
    # A merger later undone (MOD 21, rétablissement: a commune restored out of the one it had joined) is left out:
    # the places' borders went back, and the series cuts at the break instead.
    restored = {}
    for x in csv.DictReader(open(path, encoding="utf-8")):
        if x["MOD"] == "21":
            for c in (x["COM_AV"], x["COM_AP"]): restored[c] = max(restored.get(c, ""), first_jan(x["DATE_EFF"]))
    out = []
    for g in groups.values():
        if any(restored.get(c[3:], "") > g["year"] for c in g["from"] + [g["into"]]): continue
        # a code change alone (one place, new code) is no border change
        g["rename"] = g["rename"] and len(g["from"]) == 1
        out.append(g)
    return sorted(out, key=lambda g: (g["year"], g["into"]))


def italy(path):
    import openpyxl
    rows = list(openpyxl.load_workbook(path, read_only=True).worksheets[0].iter_rows(values_only=True))[1:]
    def when(r):   # "Data decorrenza" dd/mm/yyyy, or the year
        d = str(r[12] or "").strip()
        return first_jan(f"{d[6:10]}-{d[3:5]}-{d[0:2]}") if len(d) == 10 else str(int(r[0]) + 1)
    new = {(str(r[4]), when(r)) for r in rows if r[1] == "CS"}   # municipalities formed, and when
    groups = {}
    for r in rows:
        if not r[0] or str(r[0]) < "2016" or r[1] not in ("ES", "AP"): continue
        F = when(r)
        if F <= "2016": continue
        old, into = str(r[4]), str(r[8])
        g = groups.setdefault((F, into), {"year": F, "into": "IT_" + into, "name": str(r[9]).strip(), "from": [], "names": [], "rename": r[1] == "AP"})
        if r[1] == "ES" and (into, F) not in new and "IT_" + into not in g["from"]:   # absorbed into an existing municipality
            g["from"].append("IT_" + into); g["names"].append(str(r[9]).strip())
        g["from"].append("IT_" + old); g["names"].append(str(r[5]).strip())
    out = []
    for g in groups.values():
        g["rename"] = g["rename"] and len(g["from"]) == 1
        out.append(g)
    return sorted(out, key=lambda g: (g["year"], g["into"]))


def netherlands(folder):
    import glob, html, re
    groups, split = {}, {}
    for f in sorted(glob.glob(os.path.join(folder, "nl_20??.html"))):
        F = re.search(r"(20\d\d)", os.path.basename(f)).group(1)
        t = open(f, encoding="utf-8").read()
        for tab in re.findall(r"<table.*?</table>", t, re.S):
            for tr in re.findall(r"<tr.*?</tr>", tab, re.S):
                c = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
                if len(c) >= 4 and re.fullmatch(r"\d{4}", c[0]) and re.fullmatch(r"\d{4}", c[2]):
                    old, into = "NL_GM" + c[0], "NL_GM" + c[2]
                    clean = lambda n: re.sub(r"\s+\d\)?$", "", n).replace(" -", "-").strip()
                    split.setdefault((F, old), set()).add(into)
                    g = groups.setdefault((F, into), {"year": F, "into": into, "name": clean(c[3]), "from": [], "names": [], "rename": False})
                    if old not in g["from"]: g["from"].append(old); g["names"].append(clean(c[1]))
    out, seen = [], {}
    for g in sorted(groups.values(), key=lambda g: g["year"], reverse=True):
        if any(len(split[(g["year"], o)]) > 1 for o in g["from"]):   # divided among several: marked, not added up
            out.append({**g, "part": True, "rename": False}); continue
        if g["from"] == [g["into"]]: continue
        # the same merger listed on two years' pages (Weesp joined Amsterdam on 24 March 2022, which CBS counts
        # from 1 January 2023): the later one
        k = (g["into"], tuple(sorted(g["from"])))
        if k in seen: continue
        seen[k] = 1
        g["rename"] = len(g["from"]) == 1   # a new code (and name) for the same place
        out.append(g)
    return sorted(out, key=lambda g: (g["year"], g["into"]))


def main(country, path):
    d = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    d.setdefault(country, {})["mergers"] = {"france": france, "italy": italy, "netherlands": netherlands}[country](path)
    json.dump(d, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    m = d[country]["mergers"]
    print(country, len(m), "changes;", sum(1 for g in m if not g["rename"]), "mergers of", sum(len(g["from"]) for g in m if not g["rename"]), "places")


if __name__ == "__main__":
    main(*sys.argv[1:3])
