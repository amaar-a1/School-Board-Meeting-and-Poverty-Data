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


def num(s):
    return int(str(s).replace(",", "").strip() or 0)


rows = list(csv.DictReader(open(os.path.join(HERE, "..", "docs", "data", "mexico.csv"), encoding="utf-8")))
by_state = {}
for r in rows:
    code = r["District ID"][3:]
    by_state.setdefault(code[:2], {})[norm(r["District"])] = code
data = json.load(open(os.path.join(D, "sep_basica_by_municipio_2025.json"), encoding="utf-8"))
out, unmatched = {}, []
for key, table in data["tables"].items():
    control, st = key.split("|")
    head = table[0]; ia = head.index("Alumnos")
    for row in table[1:]:
        name = row[0]
        if not name or norm(name).startswith("TOTAL"): continue
        n = num(row[ia]); k = norm(name)
        code = by_state.get(st, {}).get(k)
        if not code:
            others = [c[k] for s, c in by_state.items() if s != st and k in c]
            code = others[0] if len(others) == 1 else None
        if not code:
            unmatched.append((st, name, n)); continue
        x = out.setdefault(code, {"pupils": 0, "public": 0})
        x["pupils" if control == "0" else "public"] += n
json.dump({"cycle": data["cycle"], "by_municipality": dict(sorted(out.items()))}, open(os.path.join(D, "mx_pupils.json"), "w", encoding="utf-8"), indent=0)
print(len(out), "municipalities;", sum(x["pupils"] for x in out.values()), "pupils;", sum(x["public"] for x in out.values()), "public")
print("unmatched (control 0 and 1):", len(unmatched), unmatched[:30])
