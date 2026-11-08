"""Poland's primary-school pupils by municipality (gmina), for build_latam.poland() (data-prep/inputs/poland/pl_pupils.json).

Raw file: the education ministry's school-by-school pupil counts from its education information system (SIO),
"Uczniowie szkół w roku 2025" on dane.gov.pl (resource 1254005), school year 2025/26, as of 30 September 2025.
Kept: primary schools (szkoła podstawowa), public and non-public, summed by the gmina the school is in (its 7-digit
TERYT code), with the public schools' total too. "Liczba uczniów ogółem" is the school's whole roll.
Statistics Poland's unit ids (12 digits) carry the TERYT code: voivodeship at [2:4], then county, gmina and kind at [7:12].
Usage: python3 data-prep/prep_poland_pupils.py RAW.xlsx
"""
import json, os, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "poland")


def main(f):
    ws = openpyxl.load_workbook(f, read_only=True).worksheets[0]
    it = ws.iter_rows(values_only=True); h = next(it)
    ix = {k: h.index(k) for k in ("Rok szkolny", "idTypPodmiotu", "idTerytGmina", "Liczba uczniów ogółem", "Publiczność")}
    tot, pub, year = {}, {}, ""
    # gminy created on 1 January 2025, counted with the gmina they were split from (the site's borders and figures are 2024's)
    NEW = {"1207132": "1207052",    # Szczawa, from Kamienica
           "2002162": "2002093"}    # Grabówka, from Supraśl
    for r in it:
        if r[ix["idTypPodmiotu"]] != 3: continue   # szkoła podstawowa
        g, n = str(r[ix["idTerytGmina"]]), int(r[ix["Liczba uczniów ogółem"]] or 0)
        g = NEW.get(g, g)
        tot[g] = tot.get(g, 0) + n
        if r[ix["Publiczność"]] == "publiczna": pub[g] = pub.get(g, 0) + n
        year = r[ix["Rok szkolny"]]
    names = json.load(open(os.path.join(IN, "pl_bdl_2024.json"), encoding="utf-8"))["names"]
    out, miss = {}, []
    for u in names:
        if u[-1] not in "123": continue
        t = u[2:4] + u[7:12]
        if t not in tot:   # gminy whose kind changed since 2024 (a village became a town: rural 2 -> urban-rural 3)
            alt = [k for k in tot if k[:6] == t[:6]]
            if len(alt) == 1: t = alt[0]
        if t in tot: out[u] = {"pupils": tot[t], "pupils_public": pub.get(t, 0), "year": year}
        else: miss.append((u, names[u]))
    json.dump(out, open(os.path.join(IN, "pl_pupils.json"), "w", encoding="utf-8"), ensure_ascii=False)
    used = {k for k in tot if any(k[:6] == (u[2:4] + u[7:11]) for u in out)}
    print(len(out), "gminy with pupils; without:", miss, "; school gminy not matched:", sorted(set(tot) - used))


if __name__ == "__main__":
    main(sys.argv[1])
