"""Municipal mergers since the population series start (2011), for data-prep/inputs/border_changes.json (borders.py).

  python3 data-prep/prep_border_changes.py france v_mvt_commune_2026.csv
  python3 data-prep/prep_border_changes.py italy  Variazioni_amministrative_territoriali_dal_01011991.xlsx
  python3 data-prep/prep_border_changes.py netherlands DIR_WITH_nl_YYYY.html
  python3 data-prep/prep_border_changes.py belgium -        (the 2019 list is written out below)
  python3 data-prep/prep_border_changes.py germany -        (likewise, from Eurostat's NUTS tables)

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
Each list is written in Eurostat's LAU codes (FR_xxxxx, ...), with the years from the first one after 2011.
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
            if F <= "2011": continue
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
        if not r[0] or str(r[0]) < "2011" or r[1] not in ("ES", "AP"): continue
        F = when(r)
        if F <= "2011": continue
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


# Belgium, 1 January 2019 (Statbel): seven Flemish mergers, and eleven Hainaut municipalities renumbered when the
# province's arrondissements were redrawn. Matched by name and population between Eurostat's 2018 and 2020 LAU files.
BE_2019 = [("12041", "Puurs-Sint-Amands", [("12030", "Puurs"), ("12034", "Sint-Amands")]),
           ("44083", "Deinze", [("44011", "Deinze"), ("44049", "Nevele")]),
           ("44084", "Aalter", [("44001", "Aalter"), ("44029", "Knesselare")]),
           ("44085", "Lievegem", [("44036", "Lovendegem"), ("44072", "Waarschoot"), ("44080", "Zomergem")]),
           ("45068", "Kruisem", [("45017", "Kruishoutem"), ("45057", "Zingem")]),
           ("72042", "Oudsbergen", [("72040", "Meeuwen-Gruitrode"), ("71047", "Opglabbeek")]),
           ("72043", "Pelt", [("72025", "Neerpelt"), ("72029", "Overpelt")])]
BE_2019_RENUMBERED = {"51067": "55010", "51068": "55039", "51069": "55023", "55085": "52063", "55086": "52043", "57096": "54007",
                      "57097": "54010", "58001": "55022", "58002": "56011", "58003": "56085", "58004": "56087"}


def belgium(_):
    out = [{"year": "2019", "into": "BE_" + new, "name": name, "from": ["BE_" + c for c, _ in parts], "names": [n for _, n in parts], "rename": False}
           for new, name, parts in BE_2019]
    out += [{"year": "2019", "into": "BE_" + new, "name": "", "from": ["BE_" + old], "names": [], "rename": True} for new, old in BE_2019_RENUMBERED.items()]
    return out


# Germany's districts (NUTS 3), from Eurostat's NUTS correspondence tables (fetch round 61: 2003-2006, 2006-2010,
# 2010-2013, 2013-2016), where a new district is wholly made of former ones ("DED2C = DED23 + DED24 + DED2B"), and
# code changes; and Thuringia's 2024 renumbering (with Eisenach joining Wartburgkreis in 2021), whose new codes
# Eurostat gives from 2014 and which match the old ones exactly. Districts redrawn from parts of others
# (most of Saxony-Anhalt's 2007 reform, Mecklenburg Lake District and Vorpommern-Greifswald) aren't added up.
DE = [("2007", "DEE07", "Börde", [("DEE33", "Bördekreis"), ("DEE36", "Ohrekreis")]),
      ("2007", "DEE08", "Burgenlandkreis", [("DEE22", "Burgenlandkreis"), ("DEE27", "Weißenfels")]),
      ("2007", "DEE0A", "Mansfeld-Südharz", [("DEE23", "Mansfelder Land"), ("DEE26", "Sangerhausen")]),
      ("2007", "DEE0B", "Saalekreis", [("DEE24", "Merseburg-Querfurt"), ("DEE25", "Saalkreis")]),
      ("2008", "DED2C", "Bautzen", [("DED23", "Hoyerswerda"), ("DED24", "Bautzen"), ("DED2B", "Kamenz")]),
      ("2008", "DED2D", "Görlitz", [("DED22", "Görlitz (city)"), ("DED26", "Niederschlesischer Oberlausitzkreis"), ("DED28", "Löbau-Zittau")]),
      ("2008", "DED2E", "Meißen", [("DED25", "Meißen"), ("DED27", "Riesa-Großenhain")]),
      ("2008", "DED2F", "Sächsische Schweiz-Osterzgebirge", [("DED29", "Sächsische Schweiz"), ("DED2A", "Weißeritzkreis")]),
      ("2008", "DED42", "Erzgebirgskreis", [("DED14", "Annaberg"), ("DED18", "Mittlerer Erzgebirgskreis"), ("DED1A", "Stollberg"), ("DED1B", "Aue-Schwarzenberg")]),
      ("2008", "DED43", "Mittelsachsen", [("DED16", "Freiberg"), ("DED19", "Mittweida"), ("DED33", "Döbeln")]),
      ("2008", "DED44", "Vogtlandkreis", [("DED12", "Plauen"), ("DED17", "Vogtlandkreis")]),
      ("2008", "DED45", "Zwickau", [("DED13", "Zwickau (city)"), ("DED15", "Chemnitzer Land"), ("DED1C", "Zwickauer Land")]),
      ("2008", "DED52", "Leipzig", [("DED34", "Leipziger Land"), ("DED35", "Muldentalkreis")]),
      ("2008", "DED53", "Nordsachsen", [("DED32", "Delitzsch"), ("DED36", "Torgau-Oschatz")]),
      ("2009", "DEA2D", "Städteregion Aachen", [("DEA21", "Aachen (city)"), ("DEA25", "Aachen (district)")]),
      ("2011", "DE80K", "Landkreis Rostock", [("DE807", "Bad Doberan"), ("DE809", "Güstrow")]),
      ("2011", "DE80L", "Vorpommern-Rügen", [("DE805", "Stralsund"), ("DE80D", "Nordvorpommern"), ("DE80H", "Rügen")]),
      ("2011", "DE80M", "Nordwestmecklenburg", [("DE806", "Wismar"), ("DE80E", "Nordwestmecklenburg")]),
      ("2011", "DE80O", "Ludwigslust-Parchim", [("DE80A", "Ludwigslust"), ("DE80G", "Parchim")]),
      ("2016", "DE91C", "Göttingen", [("DE915", "Göttingen"), ("DE919", "Osterode am Harz")]),
      ("2021", "DEG0R", "Wartburgkreis", [("DEG0N", "Eisenach"), ("DEG0P", "Wartburgkreis")])]
DE_RENUMBERED = [("2007", "DEE02", "DEE21"), ("2007", "DEE03", "DEE31"), ("2007", "DEE04", "DEE3B"), ("2007", "DEE0D", "DEE37"),
                 ("2008", "DED41", "DED11"), ("2008", "DED51", "DED31"), ("2016", "DEB1C", "DEB16"), ("2016", "DEB1D", "DEB19"),
                 ("2014", "DEG0Q", "DEG0B"), ("2014", "DEG0S", "DEG04"), ("2014", "DEG0T", "DEG0F"), ("2014", "DEG0U", "DEG0I"), ("2014", "DEG0V", "DEG0H")]


def germany(_):
    out = [{"year": y, "into": new, "name": name, "from": [c for c, _ in parts], "names": [n for _, n in parts], "rename": False} for y, new, name, parts in DE]
    out += [{"year": y, "into": new, "name": "", "from": [old], "names": [], "rename": True} for y, new, old in DE_RENUMBERED]
    return out


def main(country, path):
    d = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    d.setdefault(country, {})["mergers"] = {"france": france, "italy": italy, "netherlands": netherlands, "belgium": belgium, "germany": germany}[country](path)
    json.dump(d, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    m = d[country]["mergers"]
    print(country, len(m), "changes;", sum(1 for g in m if not g["rename"]), "mergers of", sum(len(g["from"]) for g in m if not g["rename"]), "places")


if __name__ == "__main__":
    main(*sys.argv[1:3])
