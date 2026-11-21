"""Turns the Argentina downloads (made on GitHub's runner, and geoBoundaries) into the small inputs build_latam.argentina()
reads (data-prep/inputs/argentina/).

- ar_prov.geojson: the 24 jurisdictions (23 provinces and the City of Buenos Aires), from geoBoundaries gbOpen ARG ADM1
  (simplified). That file draws Entre Ríos inside Buenos Aires province, so Entre Ríos is rebuilt from its 17 departments
  (geoBoundaries ARG ADM2) and taken out of Buenos Aires; "La Roja" is La Rioja.
- ar_data.json, per jurisdiction:
  poverty: INDEC, Encuesta Permanente de Hogares, "Incidencia de la pobreza y la indigencia en 31 aglomerados urbanos",
    first half of 2026 (cuadros, Cuadro 4.1 and "Poblaciones"): people below the poverty line in the province's surveyed
    urban areas (aglomerados), added up by people where a province has several; all ages. Rural areas aren't surveyed.
  pop: Census 2022 (INDEC, final results), people;
  meetings: the provincial legislature's recordings on YouTube (fetch/ar_yt2.py), see build_latam.argentina().
Usage: python3 data-prep/prep_argentina.py RAWDIR [RAWDIR ...] GEODIR
"""
import glob, json, os, re, sys, unicodedata
import xlrd
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "argentina")
key = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())
PROV = ["Buenos Aires", "Catamarca", "Chaco", "Chubut", "Ciudad Autónoma de Buenos Aires", "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy",
        "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
        "Santiago del Estero", "Tierra del Fuego", "Tucumán"]
# INDEC province codes (the first two digits of its geographic codes)
CODE = {"Ciudad Autónoma de Buenos Aires": "02", "Buenos Aires": "06", "Catamarca": "10", "Córdoba": "14", "Corrientes": "18", "Chaco": "22", "Chubut": "26",
        "Entre Ríos": "30", "Formosa": "34", "Jujuy": "38", "La Pampa": "42", "La Rioja": "46", "Mendoza": "50", "Misiones": "54", "Neuquén": "58",
        "Río Negro": "62", "Salta": "66", "San Juan": "70", "San Luis": "74", "Santa Cruz": "78", "Santa Fe": "82", "Santiago del Estero": "86",
        "Tucumán": "90", "Tierra del Fuego": "94"}
REGION = {"Ciudad Autónoma de Buenos Aires": "Gran Buenos Aires", "Buenos Aires": "Pampeana", "Córdoba": "Pampeana", "Entre Ríos": "Pampeana", "La Pampa": "Pampeana",
          "Santa Fe": "Pampeana", "Mendoza": "Cuyo", "San Juan": "Cuyo", "San Luis": "Cuyo", "Corrientes": "Noreste", "Chaco": "Noreste", "Formosa": "Noreste",
          "Misiones": "Noreste", "Catamarca": "Noroeste", "Jujuy": "Noroeste", "La Rioja": "Noroeste", "Salta": "Noroeste", "Santiago del Estero": "Noroeste",
          "Tucumán": "Noroeste", "Chubut": "Patagonia", "Neuquén": "Patagonia", "Río Negro": "Patagonia", "Santa Cruz": "Patagonia", "Tierra del Fuego": "Patagonia"}
# Each surveyed urban area (aglomerado) and its province. San Nicolás - Villa Constitución straddles Buenos Aires and Santa Fe,
# Viedma - Carmen de Patagones Río Negro and Buenos Aires: each goes to the province of its larger part.
AGLO = {"Ciudad Autónoma de Buenos Aires": "Ciudad Autónoma de Buenos Aires", "Partidos del GBA": "Buenos Aires", "Bahía Blanca - Cerri": "Buenos Aires",
        "Gran La Plata": "Buenos Aires", "Mar del Plata": "Buenos Aires", "San Nicolás - Villa Constitución": "Buenos Aires", "Gran Mendoza": "Mendoza",
        "Gran San Juan": "San Juan", "Gran San Luis": "San Luis", "Corrientes": "Corrientes", "Formosa": "Formosa", "Gran Resistencia": "Chaco",
        "Posadas": "Misiones", "Gran Catamarca": "Catamarca", "Gran Tucumán - Tafí Viejo": "Tucumán", "Jujuy - Palpalá": "Jujuy", "La Rioja": "La Rioja",
        "Salta": "Salta", "Santiago del Estero - La Banda": "Santiago del Estero", "Concordia": "Entre Ríos", "Gran Paraná": "Entre Ríos",
        "Gran Córdoba": "Córdoba", "Río Cuarto": "Córdoba", "Gran Rosario": "Santa Fe", "Gran Santa Fe": "Santa Fe", "Santa Rosa - Toay": "La Pampa",
        "Comodoro Rivadavia - Rada Tilly": "Chubut", "Rawson - Trelew": "Chubut", "Neuquén - Plottier": "Neuquén", "Río Gallegos": "Santa Cruz",
        "Ushuaia - Río Grande": "Tierra del Fuego", "Viedma - Carmen de Patagones": "Río Negro"}
ER_DEPTS = ["Colón", "Concordia", "Diamante", "Federación", "Federal", "Feliciano", "Gualeguay", "Gualeguaychú", "Islas del Ibicuy", "La Paz", "Nogoyá",
            "Paraná", "San Salvador", "Tala", "Uruguay", "Victoria", "Villaguay"]


def find(dirs, name):
    return sorted(f for d in dirs for f in glob.glob(os.path.join(d, "**", name), recursive=True))[-1]


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 4), round(c[1], 4)]


def borders(geo):
    a1 = json.load(open(os.path.join(geo, "geoBoundaries-ARG-ADM1_simplified.geojson"), encoding="utf-8"))["features"]
    a2 = json.load(open(os.path.join(geo, "geoBoundaries-ARG-ADM2_simplified.geojson"), encoding="utf-8"))["features"]
    g1 = {("La Rioja" if f["properties"]["shapeName"] == "La Roja" else f["properties"]["shapeName"]): shape(f["geometry"]).buffer(0) for f in a1}
    ba = g1["Buenos Aires"]; want = {key(x) for x in ER_DEPTS}
    er = [shape(f["geometry"]).buffer(0) for f in a2 if key(f["properties"]["shapeName"]) in want
          and ba.contains(shape(f["geometry"]).buffer(0).representative_point()) and shape(f["geometry"]).representative_point().x > -60.9]
    assert len(er) == 17, len(er)
    g1["Entre Ríos"] = unary_union(er).buffer(0.003).buffer(-0.003)
    rest = ba.difference(g1["Entre Ríos"].buffer(0.01))
    parts = [p for p in getattr(rest, "geoms", [rest]) if p.area > 0.001]
    g1["Buenos Aires"] = unary_union(parts)
    assert set(g1) == set(PROV), set(PROV) ^ set(g1)
    feats = []
    for p in PROV:
        g = g1[p].simplify(0.005, preserve_topology=True)
        feats.append({"type": "Feature", "properties": {"id": "ARG-" + CODE[p], "NAME": p}, "geometry": {"type": g.geom_type, "coordinates": rnd(mapping(g)["coordinates"])}})
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "ar_prov.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)


def poverty(dirs):
    b = xlrd.open_workbook(find(dirs, "ar_cuadros_informe_pobreza_09_26.xls"))
    title = b.sheet_by_name("Cuadro 4.1").cell_value(0, 0)
    assert "Primer semestre de 2026" in title, title
    sh = b.sheet_by_name("Poblaciones (Ex cuadro 4.2)")
    agg, seen = {}, []
    for r in range(sh.nrows):
        n = str(sh.cell_value(r, 0)).strip()
        if n in AGLO and isinstance(sh.cell_value(r, 2), float):
            a = agg.setdefault(AGLO[n], [0, 0, []]); a[0] += sh.cell_value(r, 2); a[1] += sh.cell_value(r, 6); a[2].append(n); seen.append(n)
    assert len(seen) == len(AGLO), set(AGLO) - set(seen)
    return {p: {"poverty": round(100 * q / t, 1), "survey_pop_k": t, "aglos": ag} for p, (t, q, ag) in agg.items()}


if __name__ == "__main__":
    *dirs, geo = sys.argv[1:]
    os.makedirs(OUT, exist_ok=True)
    borders(geo)
    pov = poverty(dirs)
    old = json.load(open(os.path.join(OUT, "ar_data.json"), encoding="utf-8")) if os.path.exists(os.path.join(OUT, "ar_data.json")) else {}
    data = {p: {**old.get(p, {}), "code": CODE[p], "region": REGION[p], **pov[p]} for p in PROV}
    json.dump(data, open(os.path.join(OUT, "ar_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(data), "jurisdictions;", {p: d["poverty"] for p, d in data.items()})
