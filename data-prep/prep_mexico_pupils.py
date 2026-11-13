"""Pupils in basic education (preescolar, primaria, secundaria) by Mexican municipality, from SEP's school statistics.

Source: SEP, Dirección General de Planeación, Programación y Estadística Educativa, "Principales cifras"
(planeacion.sep.gob.mx/principalescifras), from the Formato 911 school census: ciclo escolar 2025-2026, modalidad
escolarizada, tipo educativo básica, each state with municipio "Todos", for all schools and for public schools
(control público). Fetched on GitHub's runner one state at a time: inputs/mexico/sep_basica_by_municipio_2025.json.

Each state's table lists the municipalities its schools are in, by name. A few rows are schools a state runs just over
its border (Aguascalientes lists Lagos de Moreno, Jalisco): those are added to the municipality of that name in the
neighbouring state when the name is found in exactly one other state, and otherwise left out.
Writes inputs/mexico/mx_pupils.json: {INEGI code: {"pupils", "public"}}.
Usage: python3 data-prep/prep_mexico_pupils.py
"""
import csv, json, os, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "inputs", "mexico")


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return " ".join(s.replace(".", " ").replace("-", " ").split())


# The map's 2012 names abbreviate ("Gral. Escobedo", "Dr. Arroyo") and often drop the honorific half of a name
# ("Silao" for Silao de la Victoria, "Tlaquepaque" for San Pedro Tlaquepaque).
ABBR = {"GRAL ": "GENERAL ", "DR ": "DOCTOR ", "STA ": "SANTA ", "STO ": "SANTO "}


def mapnorm(s):
    s = norm(s) + " "
    for a, b in ABBR.items(): s = s.replace(a, b) if s.startswith(a) else s
    return s.strip()


def variants(k):
    out = [k]
    for pre in ("HEROICA VILLA DE ", "HEROICA VILLA ", "HEROICA CIUDAD DE ", "HEROICO ", "HEROICA ", "EL ", "LA ", "LOS ", "LAS "):
        if k.startswith(pre): out.append(k[len(pre):])
    for v in list(out):
        if " DE " in v: out.append(v.split(" DE ")[0])
        if "," in v: out.append(v.split(",")[0])
    return out


def find(st_names, k):
    for v in variants(k):
        if v in st_names: return st_names[v]
    # the map's name is the end of SEP's ("TLAQUEPAQUE" in "SAN PEDRO TLAQUEPAQUE"): only if just one fits
    ends = [c for n, c in st_names.items() if len(n) > 4 and k.endswith(" " + n)]
    return ends[0] if len(ends) == 1 else None


# SEP names the map spells differently, and municipalities created after the map's 2012 borders, whose pupils go
# to the municipality they were split from: San Felipe (2021, from Mexicali), Dzitbalché (2021, from Calkiní),
# Las Vigas (2021, from San Marcos), San Nicolás (2021, from Cuajinicuilapa), Eldorado (2021, from Culiacán),
# Juan José Ríos (2021, from Guasave), Villa de Pozos (2024, from San Luis Potosí). Playa del Carmen is the
# municipality of Solidaridad, renamed. Left out, so those keep their census figure: Ñuu Savi and Santa Cruz del
# Rincón (Guerrero, 2021, each split from more than one municipality), and San Juan Mixtepec and San Pedro Mixtepec
# (Oaxaca), each two municipalities of the same name that SEP lists as one.
ALIAS = {("02", "SAN FELIPE"): "02002", ("04", "DZITBALCHE"): "04001", ("08", "DR BELISARIO DOMINGUEZ"): "08022",
         ("12", "LAS VIGAS"): "12053", ("12", "SAN NICOLAS"): "12023", ("20", "VILLA DE TUTUTEPEC"): "20334",
         ("20", "SAN MATEO YUCUTINDOO"): "20566", ("20", "VILLA HIDALGO YALALAG"): "20038", ("23", "PLAYA DEL CARMEN"): "23008",
         ("24", "AHUALULCO DEL SONIDO 13"): "24001", ("24", "VILLA DE POZOS"): "24028", ("25", "ELDORADO"): "25006",
         ("25", "JUAN JOSE RIOS"): "25011"}


def num(s):
    return int(str(s).replace(",", "").strip() or 0)


rows = list(csv.DictReader(open(os.path.join(HERE, "..", "docs", "data", "mexico.csv"), encoding="utf-8")))
by_state = {}
for r in rows:
    code = r["District ID"][3:]
    by_state.setdefault(code[:2], {})[mapnorm(r["District"])] = code
data = json.load(open(os.path.join(D, "sep_basica_by_municipio_2025.json"), encoding="utf-8"))
out, unmatched = {}, []
for key, table in data["tables"].items():
    control, st = key.split("|")
    head = table[0]; ia = head.index("Alumnos")
    for row in table[1:]:
        name = row[0]
        if len(row) <= ia or not name or norm(name).startswith("TOTAL"): continue   # totals and footnotes
        n = num(row[ia]); k = norm(name)
        code = ALIAS.get((st, k)) or find(by_state.get(st, {}), k)
        if not code:
            others = [c for c in (find(n, k) for s, n in by_state.items() if s != st) if c]
            code = others[0] if len(others) == 1 else None
        if not code:
            unmatched.append((st, name, n)); continue
        x = out.setdefault(code, {"pupils": 0, "public": 0})
        x["pupils" if control == "0" else "public"] += n
json.dump({"cycle": data["cycle"], "by_municipality": dict(sorted(out.items()))}, open(os.path.join(D, "mx_pupils.json"), "w", encoding="utf-8"), indent=0)
print(len(out), "municipalities;", sum(x["pupils"] for x in out.values()), "pupils;", sum(x["public"] for x in out.values()), "public")
print("unmatched (control 0 and 1):", len(unmatched), sum(n for *_, n in unmatched), "pupils:", [u for u in unmatched if u[0] != "x"])
