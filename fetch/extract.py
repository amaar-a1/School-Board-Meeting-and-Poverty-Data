# Temporary: Virgin Islands poverty by age by sex (vi000392020.dhc, field 186) for each island.
import csv, urllib.request, zipfile
B = "https://www2.census.gov/programs-surveys/decennial/2020/data/island-areas"
urllib.request.urlretrieve(f"{B}/us-virgin-islands/demographic-and-housing-characteristics-file/vi2020.dhc.zip", "/tmp/vi.zip")
z = zipfile.ZipFile("/tmp/vi.zip")
islands = {}
with z.open("vigeo2020.dhc") as f:
    for raw in f:
        g = raw.decode("latin-1").split("|")
        if g[2] == "050" and g[3] == "00" and g[4] == "00":
            islands[g[7]] = [x for x in g if x][-6] if False else g
with z.open("vi000392020.dhc") as f:
    seg = {}
    for raw in f:
        r = raw.decode("latin-1").rstrip("\r\n").split("|")
        if r[4] in islands or r[4] == "0000001":
            seg[r[4]] = r
with open("fetch/out/vi_islands.csv", "w", newline="") as out:
    w = csv.writer(out)
    w.writerow(["logrecno", "geo", "name", "total", "below", "kids_5_17", "kids_5_17_below"])
    for lr in ["0000001"] + sorted(islands):
        r = seg[lr]
        v = [0] + [int(x) for x in r[185:220]]
        below = v[5] + v[6] + v[7] + v[13] + v[14] + v[15]
        above = v[22] + v[23] + v[24] + v[30] + v[31] + v[32]
        g = islands.get(lr)
        w.writerow([lr, g[8] if g else "territory", "|".join(x for x in g[-12:] if x) if g else "", v[1], v[2], below + above, below])
