# Temporary: find the "poverty status in 2019 by age by sex" table in each territory's
# 2020 DHC summary file (territory-wide record, logical record 1) and save the counts.
import csv, os, urllib.request, zipfile
B = "https://www2.census.gov/programs-surveys/decennial/2020/data/island-areas"
T = {"gu": "guam", "mp": "commonwealth-of-the-northern-mariana-islands", "vi": "us-virgin-islands", "as": "american-samoa"}

def num(x):
    try: return int(x)
    except ValueError: return -1

def matches(vals):
    # Table layout: total; below poverty (male: 7 ages; female: 7 ages); at or above (same).
    for i in range(len(vals) - 34):
        v = [0] + vals[i:i + 35]     # 1-based
        if v[2] <= 0 or min(v[1:]) < 0: continue
        if (v[1] == v[2] + v[19] and v[2] == v[3] + v[11] and v[3] == sum(v[4:11]) and v[11] == sum(v[12:19])
                and v[19] == v[20] + v[28] and v[20] == sum(v[21:28]) and v[28] == sum(v[29:36])):
            yield i, v

rows = []
for ab, name in T.items():
    path = f"/tmp/{ab}.zip"
    if not os.path.exists(path):
        urllib.request.urlretrieve(f"{B}/{name}/demographic-and-housing-characteristics-file/{ab}2020.dhc.zip", path)
    z = zipfile.ZipFile(path)
    for info in z.infolist():
        if "geo" in info.filename: continue
        with z.open(info) as f:
            line = f.readline().decode("latin-1").rstrip("\r\n").split("|")
        if line[4] != "0000001": continue
        for i, v in matches([num(x) for x in line[5:]]):
            below = v[5] + v[6] + v[7] + v[13] + v[14] + v[15]
            above = v[22] + v[23] + v[24] + v[30] + v[31] + v[32]
            rows.append([ab, info.filename, i + 6, v[1], v[2], below + above, below] + v[1:])
os.makedirs("fetch/out", exist_ok=True)
with open("fetch/out/territory_poverty_candidates.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["territory", "file", "field", "total", "below", "kids_5_17", "kids_5_17_below"] + [f"v{k}" for k in range(1, 36)])
    w.writerows(rows)
print(len(rows), "candidate tables")
