# Temporary: CBS population by age on 1 January 2026, Bonaire, Sint Eustatius and Saba (both sexes, all marital states).
import os, urllib.parse, urllib.request
OUT = "fetch/out/isl5"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
f = "Geslacht eq 'T001038' and BurgerlijkeStaat eq 'T001019' and Perioden eq '2026JJ00'"
u = "https://opendata.cbs.nl/ODataApi/odata/83698NED/TypedDataSet?$format=json&$filter=" + urllib.parse.quote(f)
with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r: open(f"{OUT}/83698NED_2026.json", "wb").write(r.read())
