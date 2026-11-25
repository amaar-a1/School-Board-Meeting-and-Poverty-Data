"""Chile's earlier comunal poverty estimates, for change over time: data-prep/inputs/chile/cl_poverty_history.json,
{comuna code (5 digits): {year: percent of people below the income poverty line}}.

Ministerio de Desarrollo Social y Familia, Observatorio Social, "Pobreza comunal": the income poverty rate of each
comuna, by small-area estimation (SAE) from the Casen survey, for 2011 (recalculated with the new methodology), 2013,
2015, 2017, 2020 (revised in 2022) and 2022 (observatorio.ministeriodesarrollosocial.gob.cl/pobreza-comunal-YYYY;
downloaded on GitHub's runner, fetch round 48). The 2009 and old-methodology 2011 tables aren't used: they measure
against a different poverty line. The site's 2024 figure is not added to the series: it uses the new poverty line of Casen 2024, about twice as high.
Also cl_population_history.json: the population each estimate is computed on (INE projections, column "Número de
personas según proyecciones de población"), in the 2020 and 2022 files and the site's 2024 file (inputs/chile).
Usage: python3 data-prep/prep_chile_history.py RAWDIR
"""
import glob, io, json, os, re, sys, zipfile
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))


def table(wb):
    """(year, {code: rate}) from the sheet with the income poverty percentage."""
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        for i, r in enumerate(rows[:10]):
            col = next((j for j, c in enumerate(r or []) if isinstance(c, str) and re.match(r"Porcentaje de personas en situación de pobreza por ingresos \d{4}", c.strip())), None)
            if col is None: continue
            year = re.search(r"(\d{4})", r[col]).group(1)
            out = {}
            for x in rows[i + 1:]:
                if x and isinstance(x[0], (int, float)) and isinstance(x[col], (int, float)):
                    out[str(int(x[0])).zfill(5)] = round(100 * x[col], 1)
            return year, out
    return None, {}


def main(raw):
    out = {}
    files = [f for f in glob.glob(os.path.join(raw, "cl_20*.xlsx")) if "Multidimensional_Comunas" not in f and "SAE_20092011" not in f]
    books = [openpyxl.load_workbook(f, read_only=True, data_only=True) for f in files]
    for z in glob.glob(os.path.join(raw, "cl_2011_*nueva*.zip")):
        zf = zipfile.ZipFile(z)
        books += [openpyxl.load_workbook(io.BytesIO(zf.read(n)), read_only=True, data_only=True) for n in zf.namelist() if n.endswith(".xlsx") and not n.startswith("__MACOSX")]
    for wb in books:
        y, t = table(wb)
        if not y: continue
        for code, v in t.items(): out.setdefault(code, {})[y] = v
        print(y, len(t), "comunas")
    json.dump(out, open(os.path.join(HERE, "inputs", "chile", "cl_poverty_history.json"), "w"), indent=0, sort_keys=True)
    pop = {}
    for f in [x for x in files if "Ingresos" in x] + [os.path.join(HERE, "inputs", "chile", "sae_ingresos_2024.xlsx")]:
        rows = list(openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True))
        for i, r in enumerate(rows[:10]):
            col = next((j for j, c in enumerate(r or []) if isinstance(c, str) and c.startswith("Número de personas según proyecciones")), None)
            if col is None: continue
            y = re.search(r"(20\d\d)", os.path.basename(f)).group(1)
            for x in rows[i + 1:]:
                if x and isinstance(x[0], (int, float)) and isinstance(x[col], (int, float)): pop.setdefault(str(int(x[0])).zfill(5), {})[y] = int(x[col])
            break
    json.dump(pop, open(os.path.join(HERE, "inputs", "chile", "cl_population_history.json"), "w"), indent=0, sort_keys=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
