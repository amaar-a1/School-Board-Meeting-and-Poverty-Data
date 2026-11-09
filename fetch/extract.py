# Temporary: INE census 2021 table 66627 (population 15+ in municipalities of 500+, by sex, birthplace and level of
# studies in progress), summed by municipality on the runner (the file is over GitHub's size limit): people studying at
# school levels (primary, lower and upper secondary, vocational), both sexes, all birthplaces, latest year.
import collections, csv, io, json, os, urllib.request
OUT = "fetch/out/es_enr3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
with urllib.request.urlopen(urllib.request.Request("https://www.ine.es/jaxiT3/files/t/csv_bd/66627.csv", headers=UA), timeout=1500) as r: t = r.read().decode("utf-8-sig", "ignore")
rd = csv.reader(io.StringIO(t), delimiter="\t"); h = next(rd); log.write(f"header {h}\n")
vals = collections.defaultdict(collections.Counter); rows = []
for row in rd:
    rows.append(row)
    for j, c in enumerate(row[:-1]):
        if len(vals[j]) < 40 or c in vals[j]: vals[j][c] += 1
log.write(json.dumps({h[j]: list(v)[:40] for j, v in vals.items()}, ensure_ascii=False) + "\n")
ix = {k: h.index(k) for k in h}
lvl = next(k for k in h if "estudios" in k.lower()); mun = next(k for k in h if "unicip" in k); per = next(k for k in h if "eriodo" in k)
others = [k for k in h if k not in (lvl, mun, per, h[-1])]
latest = max(r[ix[per]] for r in rows)
SCHOOL = ("Educación primaria e inferior", "Primera etapa de Educación Secundaria y similar", "Segunda etapa de educación secundaria, con orientación general",
          "Segunda etapa de Educación Secundaria, con orientación profesional (con y sin continuidad en la educación superior); Educación postsecundaria no superior")
out = collections.defaultdict(float)
for r in rows:
    if r[ix[per]] != latest or not r[ix[mun]].strip(): continue
    if any(r[ix[k]] not in ("Total", "") for k in others): continue
    if r[ix[lvl]] in SCHOOL:
        v = r[-1].replace(".", "").replace(",", ".").strip()
        if v and v not in ("..", "-"): out[r[ix[mun]].split(" ", 1)[0]] += float(v)
json.dump({"period": latest, "levels": SCHOOL, "by_municipality": {k: round(v) for k, v in sorted(out.items())}}, open(f"{OUT}/es_census_15plus_school.json", "w"), ensure_ascii=False)
log.write(f"latest {latest}; municipalities {len(out)}; total {sum(out.values())}; others {others}\n")
log.close()
