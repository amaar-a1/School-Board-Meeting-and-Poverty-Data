"""Real pupil counts for the Spanish regions that publish them by municipality.

Catalonia: Departament d'Educació, "Alumnes matriculats per ensenyament i unitats dels centres docents"
  (Transparència Catalunya open data, dataset xvme-26kg), summed by the school's municipality for the latest
  school year: nursery (llar d'infants and parvulari), primary, compulsory secondary (ESO), batxillerat and
  special education. Language schools, arts and vocational courses are left out.
  Saved input: inputs/spain/regional/catalunya_matricules_2025_26_by_municipality.json (from the dataset's
  API: sum of "Matrícules. Total" grouped by "Codi municipi_5" and "Nom ensenyament").
Community of Madrid: "Alumnos no universitarios matriculados en centros escolares por tipo de centro y
  régimen. Municipios" (datos.comunidad.madrid), latest year, régimen general (nursery to batxillerato and
  vocational training; language, arts and adult schools left out), total and public.
Valencian Community: Conselleria d'Educació, "Resumen de escolarización 2025" (dadesobertes.gva.es, edu-alu-gen-2025),
  pupils by school summed by its municipality (infantil to bachillerato and special education, public and private;
  public = schools of public ownership): inputs/spain/regional/valencia_escolarizacion_2025_by_municipality.json.
Writes inputs/spain/es_regional_pupils.json: {INE code: {"pupils", "public"?, "year"}}.
Usage: python3 data-prep/prep_spain_regional_pupils.py
"""
import csv, json, os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "spain")
out = {}

cat = json.load(open(os.path.join(D, "regional", "catalunya_matricules_2025_26_by_municipality.json"), encoding="utf-8"))
KEEP = ("EDUCACIÓ INFANTIL", "LLAR D'INFANTS", "EDUCACIÓ PRIMÀRIA", "EDUCACIÓ SECUNDÀRIA OBLIGATÒRIA", "BATXILLERAT", "EDUCACIÓ ESPECIAL")
tot = {}
for r in cat["rows"]:
    if r["nom_ensenyament"].startswith(KEEP) and r.get("codi_municipi_5"):
        tot[r["codi_municipi_5"]] = tot.get(r["codi_municipi_5"], 0) + float(r.get("sum_matr_cules_total") or 0)
for code, v in tot.items():
    if v > 0:
        out[code] = {"pupils": round(v), "year": f"{cat['curs'].replace('/', '-')} (Catalonia's education department: pupils at the municipality's schools, nursery to batxillerat, public and private)"}
print("Catalonia", len(tot), "municipalities,", round(sum(tot.values())), "pupils")

rows = list(csv.DictReader(open(os.path.join(D, "regional", "madrid_alumnos_no_universitarios_municipios.csv"), encoding="utf-8-sig"), delimiter=";"))
yr = max(r["Año"] for r in rows)
m = {}
for r in rows:
    if r["Año"] == yr and r["Tipo territorio"] == "Municipios" and r["Régimen"] == "Régimen general" and r["Valor"]:
        m.setdefault("28" + r["Código territorio"][:3], {})[r["Tipo"]] = int(r["Valor"])
for code, x in m.items():
    if x.get("Total"):
        out[code] = {"pupils": x["Total"], "public": x.get("Público", ""),
                     "year": f"{yr}-{int(yr) % 100 + 1:02d} (Community of Madrid: pupils at the municipality's schools, nursery to bachillerato and vocational training, public and private)"}
print("Madrid", len(m), "municipalities,", sum(x.get("Total", 0) for x in m.values()), "pupils")
va = json.load(open(os.path.join(D, "regional", "valencia_escolarizacion_2025_by_municipality.json"), encoding="utf-8"))
for code, x in va["by_municipality"].items():
    if x["pupils"]:
        out[code] = {"pupils": x["pupils"], "public": x["public"],
                     "year": f"{va['curso']}-{int(va['curso']) % 100 + 1:02d} (Valencian education department: pupils at the municipality's schools, nursery to bachillerato, public and private)"}
print("Valencia", len(va["by_municipality"]), "municipalities,", sum(x["pupils"] for x in va["by_municipality"].values()), "pupils")
json.dump(dict(sorted(out.items())), open(os.path.join(D, "es_regional_pupils.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
