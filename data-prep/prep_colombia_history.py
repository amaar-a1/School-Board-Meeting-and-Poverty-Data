"""Colombia's municipal enrollment for every year 2011 on, for change over time: data-prep/inputs/colombia/
men_enrollment_history.json, {municipality code: {year: pupils}}.

Ministry of Education, "Estadísticas en educación preescolar, básica y media por municipio" (datos.gov.co nudc-7mev),
every year (fetch round 53): as for the site's figure, the gross coverage rate times the population aged 5-16, which
gives back the ministry's enrollment count (transición to media) to within the rounding of the rate.
Usage: python3 data-prep/prep_colombia_history.py co_men_all_years.json
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(path):
    out = {}
    for r in json.load(open(path, encoding="utf-8")):
        f = lambda v: float(str(v or 0).replace(",", "")) if str(v or "").replace(",", "").replace(".", "", 1).isdigit() else 0
        pop, rate = f(r.get("poblaci_n_5_16")), f(r.get("cobertura_bruta"))
        if pop and rate: out.setdefault(r["c_digo_municipio"].zfill(5), {})[r["a_o"]] = round(pop * rate / 100)
    json.dump(out, open(os.path.join(HERE, "inputs", "colombia", "men_enrollment_history.json"), "w"), separators=(",", ":"), sort_keys=True)
    print(len(out), "municipalities")


if __name__ == "__main__":
    main(sys.argv[1])
